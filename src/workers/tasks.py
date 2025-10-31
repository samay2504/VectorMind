"""
Celery tasks for background processing
Async document processing, embeddings, and maintenance
"""

import logging
from typing import List, Dict, Any
from celery import Task
from datetime import datetime, timedelta

from src.workers.celery_app import celery_app
from src.config import settings

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """Base task with callbacks"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        logger.error(f"Task {task_id} failed: {exc}")
        # Could send notification, update database, etc.
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        logger.info(f"Task {task_id} succeeded")


@celery_app.task(base=CallbackTask, bind=True, max_retries=3)
def process_document_async(self, file_path: str, collection_name: str, user_id: str) -> Dict[str, Any]:
    """
    Process document asynchronously
    
    Args:
        file_path: Path to uploaded file
        collection_name: Target collection
        user_id: User who uploaded
    
    Returns:
        Processing result
    """
    try:
        from src.core.ingestion.pdf_processor import PDFProcessor
        from src.core.ingestion.image_processor import ImageProcessor
        from src.core.ingestion.text_chunker import TextChunker
        from src.core.ingestion.embedder import Embedder
        from src.core.vector_adapter import VectorDBManager
        from pymongo import MongoClient
        import uuid
        
        logger.info(f"Processing document: {file_path}")
        
        # Determine file type
        file_ext = file_path.split(".")[-1].lower()
        
        # Process based on type
        if file_ext == "pdf":
            processor = PDFProcessor()
            result = processor.process(file_path)
            text_content = "\n".join([p["text"] for p in result["text_content"]])
        elif file_ext in ["png", "jpg", "jpeg"]:
            processor = ImageProcessor()
            result = processor.process(file_path)
            text_content = result["text"]
        else:
            with open(file_path, 'r') as f:
                text_content = f.read()
        
        # Chunk text
        chunker = TextChunker()
        chunks = chunker.chunk_text(text_content, metadata={"user_id": user_id})
        
        # Generate embeddings
        embedder = Embedder()
        chunk_texts = [c["text"] for c in chunks]
        embeddings = embedder.embed_texts(chunk_texts)
        
        # Store in vector DB
        vector_manager = VectorDBManager()
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
                    "user_id": user_id
                }],
                ids=[vector_id]
            )
        
        # Store in MongoDB
        mongo_client = MongoClient(settings.mongo_uri)
        db = mongo_client[settings.mongo_db_name]
        db.documents.insert_one({
            "_id": doc_id,
            "user_id": user_id,
            "file_path": file_path,
            "chunk_count": len(chunks),
            "processed_at": datetime.utcnow()
        })
        
        logger.info(f"Document processed: {doc_id}")
        
        return {
            "document_id": doc_id,
            "chunks": len(chunks),
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery_app.task(bind=True, max_retries=3)
def batch_embed_texts(self, texts: List[str]) -> List[List[float]]:
    """
    Batch embed multiple texts
    
    Args:
        texts: List of texts to embed
    
    Returns:
        List of embeddings
    """
    try:
        from src.core.ingestion.embedder import Embedder
        
        logger.info(f"Batch embedding {len(texts)} texts")
        
        embedder = Embedder()
        embeddings = embedder.embed_texts(texts)
        
        logger.info(f"Batch embedding complete: {len(embeddings)} embeddings")
        
        return embeddings
    
    except Exception as e:
        logger.error(f"Batch embedding failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery_app.task
def cleanup_old_data(days: int = 30) -> Dict[str, int]:
    """
    Cleanup old data (maintenance task)
    
    Args:
        days: Delete data older than this many days
    
    Returns:
        Cleanup statistics
    """
    try:
        from pymongo import MongoClient
        
        logger.info(f"Starting cleanup of data older than {days} days")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        mongo_client = MongoClient(settings.mongo_uri)
        db = mongo_client[settings.mongo_db_name]
        
        # Cleanup old documents
        doc_result = db.documents.delete_many({
            "processed_at": {"$lt": cutoff_date},
            "keep": {"$ne": True}  # Don't delete documents marked to keep
        })
        
        # Cleanup old audit logs (keep important ones)
        audit_result = db.audit_logs.delete_many({
            "timestamp": {"$lt": cutoff_date},
            "severity": {"$in": ["info"]}  # Only delete info-level logs
        })
        
        stats = {
            "documents_deleted": doc_result.deleted_count,
            "audit_logs_deleted": audit_result.deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
        logger.info(f"Cleanup complete: {stats}")
        
        return stats
    
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return {"error": str(e)}


@celery_app.task
def expire_old_consents() -> int:
    """
    Expire old consents (periodic task)
    
    Returns:
        Number of expired consents
    """
    try:
        from pymongo import MongoClient
        from src.core.security.consent_manager import ConsentManager
        
        logger.info("Expiring old consents")
        
        mongo_client = MongoClient(settings.mongo_uri)
        db = mongo_client[settings.mongo_db_name]
        
        consent_manager = ConsentManager(db)
        expired_count = consent_manager.expire_old_consents()
        
        logger.info(f"Expired {expired_count} consents")
        
        return expired_count
    
    except Exception as e:
        logger.error(f"Consent expiration failed: {e}")
        return 0


@celery_app.task(bind=True)
def analyze_document_for_pii(self, document_id: str) -> Dict[str, Any]:
    """
    Analyze document for PII (async)
    
    Args:
        document_id: Document to analyze
    
    Returns:
        PII analysis results
    """
    try:
        from pymongo import MongoClient
        from src.core.security.pii_detector import PIIDetector
        
        logger.info(f"Analyzing document for PII: {document_id}")
        
        mongo_client = MongoClient(settings.mongo_uri)
        db = mongo_client[settings.mongo_db_name]
        
        # Get document
        doc = db.documents.find_one({"_id": document_id})
        if not doc:
            return {"error": "Document not found"}
        
        # Analyze for PII
        pii_detector = PIIDetector()
        text = doc.get("text_content", "")
        analysis = pii_detector.analyze(text)
        
        # Store results
        db.documents.update_one(
            {"_id": document_id},
            {"$set": {
                "pii_analysis": analysis,
                "pii_analyzed_at": datetime.utcnow()
            }}
        )
        
        logger.info(f"PII analysis complete for {document_id}")
        
        return analysis
    
    except Exception as e:
        logger.error(f"PII analysis failed: {e}")
        return {"error": str(e)}


@celery_app.task
def generate_compliance_report(user_id: str) -> Dict[str, Any]:
    """
    Generate compliance report for user
    
    Args:
        user_id: User identifier
    
    Returns:
        Compliance report
    """
    try:
        from pymongo import MongoClient
        from src.core.security.consent_manager import ConsentManager
        from src.core.security.audit_log import AuditLogger
        
        logger.info(f"Generating compliance report for {user_id}")
        
        mongo_client = MongoClient(settings.mongo_uri)
        db = mongo_client[settings.mongo_db_name]
        
        # Get consent summary
        consent_manager = ConsentManager(db)
        consent_summary = consent_manager.get_consent_summary(user_id)
        
        # Get audit trail
        audit_logger = AuditLogger(db)
        audit_trail = audit_logger.get_user_audit_trail(user_id, limit=100)
        
        # Get documents
        documents = list(db.documents.find({"user_id": user_id}))
        
        report = {
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat(),
            "consent_summary": consent_summary,
            "total_documents": len(documents),
            "recent_activities": len(audit_trail),
            "compliance_status": "compliant"  # Could add more checks
        }
        
        logger.info(f"Compliance report generated for {user_id}")
        
        return report
    
    except Exception as e:
        logger.error(f"Compliance report generation failed: {e}")
        return {"error": str(e)}


@celery_app.task
def health_check_task() -> Dict[str, Any]:
    """
    Health check task for Celery workers
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "worker": "celery",
        "timestamp": datetime.utcnow().isoformat()
    }
