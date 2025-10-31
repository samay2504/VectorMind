"""
Initialize MongoDB with proper structure for Multimodal RAG System
Creates collections, indexes, and sample data structure
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import CollectionInvalid, OperationFailure
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_database_structure(mongo_uri: str, db_name: str):
    """
    Create MongoDB database structure with collections and indexes
    """
    try:
        # Connect to MongoDB
        logger.info(f"Connecting to MongoDB: {mongo_uri}")
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # Test connection
        client.admin.command('ping')
        logger.info(f"✅ Successfully connected to MongoDB!")
        logger.info(f"📊 Database: {db_name}")
        
        # 1. Documents Collection (Main storage for all documents)
        logger.info("\n📄 Creating 'documents' collection...")
        try:
            documents_collection = db.create_collection('documents')
            logger.info("✅ 'documents' collection created")
        except CollectionInvalid:
            documents_collection = db['documents']
            logger.info("ℹ️  'documents' collection already exists")
        
        # Create indexes for documents
        documents_collection.create_index([("document_id", ASCENDING)], unique=True)
        documents_collection.create_index([("user_id", ASCENDING)])
        documents_collection.create_index([("file_type", ASCENDING)])
        documents_collection.create_index([("created_at", DESCENDING)])
        documents_collection.create_index([("metadata.tags", ASCENDING)])
        documents_collection.create_index([("$**", TEXT)])  # Full-text search
        logger.info("✅ Indexes created for 'documents'")
        
        # Insert sample document structure
        sample_doc = {
            "document_id": "sample_text_001",
            "user_id": "user_demo",
            "file_name": "sample_document.txt",
            "file_type": "text",
            "file_path": "/uploads/text/sample_document.txt",
            "file_size": 1024,
            "content": {
                "raw_text": "This is a sample text document for the multimodal RAG system.",
                "processed_text": "This is a sample text document for the multimodal RAG system.",
                "chunks": [
                    {
                        "chunk_id": 0,
                        "text": "This is a sample text document for the multimodal RAG system.",
                        "start_idx": 0,
                        "end_idx": 62
                    }
                ],
                "summary": "Sample text document",
                "key_entities": ["multimodal", "RAG", "system"]
            },
            "metadata": {
                "language": "en",
                "tags": ["sample", "demo", "text"],
                "author": "System",
                "description": "Sample document for testing",
                "word_count": 11,
                "char_count": 62
            },
            "vector_ids": ["sample_text_001_0"],
            "status": "processed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "processed_at": datetime.utcnow()
        }
        
        if documents_collection.count_documents({"document_id": "sample_text_001"}) == 0:
            documents_collection.insert_one(sample_doc)
            logger.info("✅ Sample text document inserted")
        
        # 2. Images Collection (Specialized for image documents)
        logger.info("\n🖼️  Creating 'images' collection...")
        try:
            images_collection = db.create_collection('images')
            logger.info("✅ 'images' collection created")
        except CollectionInvalid:
            images_collection = db['images']
            logger.info("ℹ️  'images' collection already exists")
        
        # Create indexes for images
        images_collection.create_index([("image_id", ASCENDING)], unique=True)
        images_collection.create_index([("document_id", ASCENDING)])
        images_collection.create_index([("user_id", ASCENDING)])
        images_collection.create_index([("created_at", DESCENDING)])
        images_collection.create_index([("metadata.tags", ASCENDING)])
        logger.info("✅ Indexes created for 'images'")
        
        # Insert sample image structure
        sample_image = {
            "image_id": "sample_img_001",
            "document_id": "sample_text_001",  # Link to parent document
            "user_id": "user_demo",
            "file_name": "sample_image.jpg",
            "file_path": "/uploads/images/sample_image.jpg",
            "file_size": 524288,
            "image_data": {
                "width": 1920,
                "height": 1080,
                "format": "JPEG",
                "color_mode": "RGB",
                "thumbnail_path": "/uploads/images/thumbnails/sample_image_thumb.jpg"
            },
            "extracted_content": {
                "ocr_text": "Sample text extracted from image via OCR",
                "caption": "A sample image for testing",
                "objects_detected": ["text", "document"],
                "scene_description": "Document with text content"
            },
            "embeddings": {
                "visual_embedding_id": "sample_img_001_visual",
                "text_embedding_id": "sample_img_001_text"
            },
            "metadata": {
                "tags": ["sample", "demo", "image"],
                "exif": {},
                "created_date": None,
                "camera_model": None
            },
            "status": "processed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "processed_at": datetime.utcnow()
        }
        
        if images_collection.count_documents({"image_id": "sample_img_001"}) == 0:
            images_collection.insert_one(sample_image)
            logger.info("✅ Sample image document inserted")
        
        # 3. PDFs Collection (Specialized for PDF documents)
        logger.info("\n📕 Creating 'pdfs' collection...")
        try:
            pdfs_collection = db.create_collection('pdfs')
            logger.info("✅ 'pdfs' collection created")
        except CollectionInvalid:
            pdfs_collection = db['pdfs']
            logger.info("ℹ️  'pdfs' collection already exists")
        
        # Create indexes for PDFs
        pdfs_collection.create_index([("pdf_id", ASCENDING)], unique=True)
        pdfs_collection.create_index([("document_id", ASCENDING)])
        pdfs_collection.create_index([("user_id", ASCENDING)])
        pdfs_collection.create_index([("created_at", DESCENDING)])
        pdfs_collection.create_index([("metadata.tags", ASCENDING)])
        pdfs_collection.create_index([("$**", TEXT)])  # Full-text search
        logger.info("✅ Indexes created for 'pdfs'")
        
        # Insert sample PDF structure
        sample_pdf = {
            "pdf_id": "sample_pdf_001",
            "document_id": "sample_pdf_doc_001",
            "user_id": "user_demo",
            "file_name": "sample_document.pdf",
            "file_path": "/uploads/pdfs/sample_document.pdf",
            "file_size": 2097152,
            "pdf_metadata": {
                "num_pages": 10,
                "author": "Sample Author",
                "title": "Sample PDF Document",
                "subject": "Testing multimodal RAG",
                "creator": "Sample Creator",
                "producer": "PDF Producer",
                "creation_date": datetime.utcnow(),
                "modification_date": datetime.utcnow()
            },
            "pages": [
                {
                    "page_number": 1,
                    "text_content": "This is page 1 content from the PDF document.",
                    "has_images": True,
                    "has_tables": False,
                    "images": ["sample_pdf_001_page1_img1"],
                    "tables": [],
                    "chunk_ids": ["sample_pdf_001_page1_chunk0"]
                }
            ],
            "extracted_content": {
                "full_text": "This is page 1 content from the PDF document.",
                "chunks": [
                    {
                        "chunk_id": 0,
                        "page_number": 1,
                        "text": "This is page 1 content from the PDF document.",
                        "start_idx": 0,
                        "end_idx": 46
                    }
                ],
                "images_extracted": 1,
                "tables_extracted": 0,
                "summary": "Sample PDF document with single page"
            },
            "vector_ids": ["sample_pdf_001_page1_chunk0"],
            "metadata": {
                "tags": ["sample", "demo", "pdf"],
                "category": "documentation",
                "language": "en",
                "is_scanned": False,
                "ocr_applied": False
            },
            "status": "processed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "processed_at": datetime.utcnow()
        }
        
        if pdfs_collection.count_documents({"pdf_id": "sample_pdf_001"}) == 0:
            pdfs_collection.insert_one(sample_pdf)
            logger.info("✅ Sample PDF document inserted")
        
        # 4. Consents Collection (GDPR/Privacy compliance)
        logger.info("\n🔒 Creating 'consents' collection...")
        try:
            consents_collection = db.create_collection('consents')
            logger.info("✅ 'consents' collection created")
        except CollectionInvalid:
            consents_collection = db['consents']
            logger.info("ℹ️  'consents' collection already exists")
        
        consents_collection.create_index([("user_id", ASCENDING)])
        consents_collection.create_index([("consent_type", ASCENDING)])
        consents_collection.create_index([("created_at", DESCENDING)])
        logger.info("✅ Indexes created for 'consents'")
        
        # 5. Audit Logs Collection (Security & compliance)
        logger.info("\n📋 Creating 'audit_logs' collection...")
        try:
            audit_collection = db.create_collection('audit_logs')
            logger.info("✅ 'audit_logs' collection created")
        except CollectionInvalid:
            audit_collection = db['audit_logs']
            logger.info("ℹ️  'audit_logs' collection already exists")
        
        audit_collection.create_index([("user_id", ASCENDING)])
        audit_collection.create_index([("action", ASCENDING)])
        audit_collection.create_index([("timestamp", DESCENDING)])
        audit_collection.create_index([("resource_type", ASCENDING)])
        logger.info("✅ Indexes created for 'audit_logs'")
        
        # 6. Conversations Collection (Chat history)
        logger.info("\n💬 Creating 'conversations' collection...")
        try:
            conversations_collection = db.create_collection('conversations')
            logger.info("✅ 'conversations' collection created")
        except CollectionInvalid:
            conversations_collection = db['conversations']
            logger.info("ℹ️  'conversations' collection already exists")
        
        conversations_collection.create_index([("conversation_id", ASCENDING)], unique=True)
        conversations_collection.create_index([("user_id", ASCENDING)])
        conversations_collection.create_index([("created_at", DESCENDING)])
        conversations_collection.create_index([("ttl_expires_at", ASCENDING)], expireAfterSeconds=0)
        logger.info("✅ Indexes created for 'conversations'")
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("✅ MongoDB Database Initialization Complete!")
        logger.info("="*60)
        logger.info(f"\n📊 Database: {db_name}")
        logger.info(f"📍 Collections created:")
        
        collections = db.list_collection_names()
        for idx, coll_name in enumerate(collections, 1):
            coll = db[coll_name]
            count = coll.count_documents({})
            indexes = len(list(coll.list_indexes()))
            logger.info(f"   {idx}. {coll_name:<20} - {count} documents, {indexes} indexes")
        
        logger.info("\n✨ Ready to use!")
        logger.info("="*60)
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing MongoDB: {e}")
        return False


if __name__ == "__main__":
    # Load from .env or use default
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    mongo_uri = os.getenv("MONGO_URI", "mongodb://samay2504:250403@localhost:27017/modality_rag?authSource=modality_rag")
    db_name = os.getenv("MONGO_DB", "modality_rag")
    
    logger.info("🚀 Starting MongoDB Initialization...")
    logger.info(f"📍 URI: {mongo_uri.replace(mongo_uri.split('@')[0].split('//')[1], '***:***')}")
    logger.info(f"📊 Database: {db_name}\n")
    
    success = create_database_structure(mongo_uri, db_name)
    
    if success:
        logger.info("\n✅ All done! Your MongoDB is ready for the Multimodal RAG System.")
    else:
        logger.error("\n❌ Failed to initialize MongoDB. Please check the logs above.")
        sys.exit(1)
