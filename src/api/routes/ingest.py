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
from src.core.ingestion.docx_processor import DOCXProcessor
from src.core.ingestion.xlsx_processor import XLSXProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

# Comprehensive list of supported file types
SUPPORTED_FILE_TYPES = {
    # Documents
    "pdf": "PDF Document",
    "docx": "Microsoft Word Document",
    "doc": "Microsoft Word Document (Legacy)",
    "txt": "Plain Text",
    "md": "Markdown",
    "rtf": "Rich Text Format",
    # Spreadsheets
    "xlsx": "Microsoft Excel Spreadsheet",
    "xls": "Microsoft Excel Spreadsheet (Legacy)",
    "csv": "Comma-Separated Values",
    # Images
    "png": "PNG Image",
    "jpg": "JPEG Image",
    "jpeg": "JPEG Image",
    "gif": "GIF Image",
    "bmp": "Bitmap Image",
    "tiff": "TIFF Image",
    "webp": "WebP Image",
    # Code and markup
    "py": "Python Code",
    "js": "JavaScript Code",
    "json": "JSON Data",
    "xml": "XML Data",
    "html": "HTML Document",
    "css": "CSS Stylesheet",
    "yaml": "YAML Data",
    "yml": "YAML Data",
}


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
        
        # Validate file type
        if file_ext not in SUPPORTED_FILE_TYPES:
            supported_list = ", ".join(sorted(SUPPORTED_FILE_TYPES.keys()))
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: '{file_ext}'. Supported types: {supported_list}"
            )
        
        logger.info(f"Processing {SUPPORTED_FILE_TYPES[file_ext]}: {file.filename}")
        
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Process based on type
        text_content = ""
        metadata = {"filename": file.filename, "file_type": file_ext}
        
        # PDF Documents
        if file_ext == "pdf":
            processor = PDFProcessor()
            result = processor.process(tmp_path)
            text_content = "\n".join([p["text"] for p in result["text_content"]])
            metadata.update({"page_count": result["page_count"]})
        
        # Word Documents
        elif file_ext in ["docx", "doc"]:
            try:
                processor = DOCXProcessor()
                result = processor.process(tmp_path)
                text_content = result["text"]
                metadata.update({
                    "paragraph_count": result.get("paragraph_count", 0),
                    "table_count": result.get("table_count", 0)
                })
            except ImportError:
                raise HTTPException(
                    status_code=500,
                    detail="DOCX processing not available. Please install python-docx: pip install python-docx"
                )
        
        # Excel Spreadsheets
        elif file_ext in ["xlsx", "xls"]:
            try:
                processor = XLSXProcessor()
                result = processor.process(tmp_path)
                text_content = result["text"]
                metadata.update({
                    "sheet_count": result.get("sheet_count", 0),
                    "row_count": result.get("row_count", 0)
                })
            except ImportError:
                raise HTTPException(
                    status_code=500,
                    detail="XLSX processing not available. Please install openpyxl: pip install openpyxl"
                )
        
        # CSV Files
        elif file_ext == "csv":
            import csv
            import io
            
            # Try different encodings
            try:
                text_content = content.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    text_content = content.decode("latin-1")
                except:
                    text_content = content.decode("utf-8", errors="ignore")
            
            # Parse CSV with error handling
            try:
                # Auto-detect delimiter
                dialect = csv.Sniffer().sniff(text_content[:1024])
                csv_reader = csv.reader(io.StringIO(text_content), dialect=dialect)
            except:
                # Fallback to comma delimiter
                csv_reader = csv.reader(io.StringIO(text_content))
            
            rows = []
            try:
                rows = list(csv_reader)
            except csv.Error as e:
                logger.warning(f"CSV parsing error: {e}, attempting with quoting=QUOTE_NONE")
                # Retry with different quoting
                csv_reader = csv.reader(io.StringIO(text_content), quoting=csv.QUOTE_NONE)
                rows = list(csv_reader)
            
            if rows:
                # Create readable format with headers emphasized
                formatted_rows = []
                
                # First row as headers (if it looks like headers)
                if len(rows) > 1 and all(isinstance(cell, str) for cell in rows[0]):
                    headers = rows[0]
                    formatted_rows.append("Headers: " + " | ".join(headers))
                    formatted_rows.append("-" * 80)
                    
                    # Data rows with column alignment
                    for row in rows[1:]:
                        formatted_rows.append(" | ".join(str(cell) for cell in row))
                else:
                    # No headers, just format rows
                    for row in rows:
                        formatted_rows.append(" | ".join(str(cell) for cell in row))
                
                text_content = "\n".join(formatted_rows)
                
                # Rich metadata
                metadata.update({
                    "row_count": len(rows),
                    "data_rows": len(rows) - 1 if len(rows) > 1 else len(rows),
                    "column_count": len(rows[0]) if rows else 0,
                    "has_headers": len(rows) > 1
                })
            else:
                raise HTTPException(status_code=400, detail="CSV file is empty or corrupted")
        
        # Images
        elif file_ext in ["png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp"]:
            processor = ImageProcessor()
            result = processor.process(tmp_path)
            text_content = result["text"]
            if result.get("caption"):
                text_content += f"\n{result['caption']}"
            metadata.update(result["metadata"])
        
        # Plain Text and Code Files
        elif file_ext in ["txt", "md", "py", "js", "json", "xml", "html", "css", "yaml", "yml", "rtf"]:
            try:
                # Try UTF-8 first
                text_content = content.decode("utf-8")
            except UnicodeDecodeError:
                # Fallback to latin-1
                text_content = content.decode("latin-1")
            
            # Add syntax highlighting hint for code files
            if file_ext in ["py", "js", "json", "xml", "html", "css", "yaml", "yml"]:
                metadata["content_type"] = "code"
                metadata["language"] = file_ext
        
        else:
            # This shouldn't happen due to earlier validation, but safety check
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
        
        # Validate we got some text content
        if not text_content or len(text_content.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"No text content extracted from {file.filename}. The file may be empty or corrupted."
            )
        
        logger.info(f"Extracted {len(text_content)} characters from {file.filename}")
        
        # Chunk text
        chunker = TextChunker()
        chunks = chunker.chunk_text(text_content, metadata=metadata)
        
        # Generate embeddings
        chunk_texts = [c["text"] for c in chunks]
        embeddings = embedder.embed_texts(chunk_texts)
        
        # Store in vector DB
        import uuid
        doc_id = str(uuid.uuid4())
        
        # Prepare vectors and payloads for batch indexing
        # Use pure UUIDs for Qdrant compatibility (no suffixes)
        vector_ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
        payloads = [
            {
                "document_id": doc_id,
                "chunk_id": i,
                "vector_id": vector_ids[i],
                "text": chunk["text"],
                **metadata
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Index all vectors in batch (VectorDBManager doesn't take collection_name)
        await vector_manager.index_vectors(
            vectors=embeddings,
            payloads=payloads,
            ids=vector_ids
        )
        
        # Store original in MongoDB
        mongo_db.documents.insert_one({
            "_id": doc_id,
            "document_id": doc_id,  # Add explicit document_id field for indexing
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


@router.get("/supported-formats")
async def get_supported_formats() -> Dict[str, Any]:
    """
    Get list of all supported file formats
    
    Returns:
        Dictionary with supported formats grouped by category
    """
    formats_by_category = {
        "documents": {
            ext: desc for ext, desc in SUPPORTED_FILE_TYPES.items()
            if ext in ["pdf", "docx", "doc", "txt", "md", "rtf"]
        },
        "spreadsheets": {
            ext: desc for ext, desc in SUPPORTED_FILE_TYPES.items()
            if ext in ["xlsx", "xls", "csv"]
        },
        "images": {
            ext: desc for ext, desc in SUPPORTED_FILE_TYPES.items()
            if ext in ["png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp"]
        },
        "code": {
            ext: desc for ext, desc in SUPPORTED_FILE_TYPES.items()
            if ext in ["py", "js", "json", "xml", "html", "css", "yaml", "yml"]
        }
    }
    
    return {
        "total_formats": len(SUPPORTED_FILE_TYPES),
        "formats": SUPPORTED_FILE_TYPES,
        "by_category": formats_by_category
    }
