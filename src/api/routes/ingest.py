"""
Document ingestion endpoints
"""

import logging
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List, Dict, Any
from pymongo.database import Database

from src.api.dependencies import get_vector_manager, get_mongo_db, get_embedder
from src.core.vector_adapter import VectorDBManager
from src.core.ingestion.embedder import Embedder
from src.core.ingestion.text_chunker import TextChunker
from src.core.ingestion.pdf_processor import PDFProcessor
from src.core.ingestion.image_processor import ImageProcessor

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/document")
async def ingest_document(
    file: UploadFile = File(...),
    collection_name: str = "default",
    vector_manager: VectorDBManager = Depends(get_vector_manager),
    mongo_db: Database = Depends(get_mongo_db),
    embedder: Embedder = Depends(get_embedder)
) -> Dict[str, Any]:
    """
    Ingest a document (PDF, text, or image)
    
    Args:
        file: Uploaded file
        collection_name: Target collection
        vector_manager: Vector DB manager
        mongo_db: MongoDB database
        embedder: Embedding generator
    
    Returns:
        Ingestion result with document ID and chunks
    """
    try:
        # Determine file type
        file_ext = file.filename.split(".")[-1].lower()
        
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Process based on type
        text_content = ""
        metadata = {"filename": file.filename, "file_type": file_ext}
        
        if file_ext == "pdf":
            processor = PDFProcessor()
            result = processor.process(tmp_path)
            text_content = "\n".join([p["text"] for p in result["text_content"]])
            metadata.update({"page_count": result["page_count"]})
        
        elif file_ext in ["png", "jpg", "jpeg"]:
            processor = ImageProcessor()
            result = processor.process(tmp_path)
            text_content = result["text"]
            if result.get("caption"):
                text_content += f"\n{result['caption']}"
            metadata.update(result["metadata"])
        
        elif file_ext in ["txt", "md"]:
            text_content = content.decode("utf-8")
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
        
        # Chunk text
        chunker = TextChunker()
        chunks = chunker.chunk_text(text_content, metadata=metadata)
        
        # Generate embeddings
        chunk_texts = [c["text"] for c in chunks]
        embeddings = embedder.embed_texts(chunk_texts)
        
        # Store in vector DB
        import uuid
        doc_id = str(uuid.uuid4())
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_id = f"{doc_id}_{i}"
            vector_manager.index_vectors(
                collection_name=collection_name,
                vectors=[embedding],
                payloads=[{
                    "document_id": doc_id,
                    "chunk_id": i,
                    "text": chunk["text"],
                    **metadata
                }],
                ids=[vector_id]
            )
        
        # Store original in MongoDB
        mongo_db.documents.insert_one({
            "_id": doc_id,
            "filename": file.filename,
            "file_type": file_ext,
            "text_content": text_content,
            "chunk_count": len(chunks),
            "metadata": metadata
        })
        
        # Cleanup temp file
        import os
        os.unlink(tmp_path)
        
        return {
            "document_id": doc_id,
            "filename": file.filename,
            "chunks_created": len(chunks),
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{document_id}")
async def get_ingestion_status(
    document_id: str,
    mongo_db: Database = Depends(get_mongo_db)
) -> Dict[str, Any]:
    """Get ingestion status for a document"""
    doc = mongo_db.documents.find_one({"_id": document_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document_id": document_id,
        "filename": doc.get("filename"),
        "chunk_count": doc.get("chunk_count"),
        "metadata": doc.get("metadata")
    }
