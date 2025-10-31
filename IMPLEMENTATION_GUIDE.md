# Project Implementation Guide

This document provides a complete implementation guide for the remaining components. Copy each file to the specified location.

## 📁 File Structure Remaining

```
src/
├── core/
│   ├── ingestion/
│   │   ├── pdf_processor.py        ✓ Need to create
│   │   ├── image_processor.py      ✓ Need to create
│   │   └── text_chunker.py         ✓ Need to create
│   ├── retrieval/
│   │   ├── __init__.py             ✓ Need to create
│   │   ├── dense_retriever.py      ✓ Need to create
│   │   ├── sparse_retriever.py     ✓ Need to create
│   │   └── hybrid.py               ✓ Need to create
│   └── security/
│       ├── __init__.py             ✓ Need to create
│       ├── pii_detector.py         ✓ Need to create
│       ├── consent_manager.py      ✓ Need to create
│       ├── audit_log.py            ✓ Need to create
│       └── encryption.py           ✓ Need to create
├── api/
│   ├── __init__.py                 ✓ Need to create
│   ├── main.py                     ✓ Need to create
│   ├── dependencies.py             ✓ Need to create
│   ├── routes/
│   │   ├── __init__.py             ✓ Need to create
│   │   ├── ingest.py               ✓ Need to create
│   │   ├── query.py                ✓ Need to create
│   │   ├── dsar.py                 ✓ Need to create
│   │   └── health.py               ✓ Need to create
│   └── middleware/
│       ├── __init__.py             ✓ Need to create
│       ├── request_id.py           ✓ Need to create
│       ├── logging_middleware.py   ✓ Need to create
│       └── rate_limit.py           ✓ Need to create
└── workers/
    ├── __init__.py                 ✓ Need to create
    ├── celery_app.py               ✓ Need to create
    └── tasks.py                    ✓ Need to create
```

## 🔧 Implementation Priority

### Phase 1: Core Processing (Day 1)
1. Text chunker
2. PDF processor
3. Image processor
4. FastAPI main app
5. Health endpoints
6. Dependencies

### Phase 2: API & Retrieval (Day 2)
1. Ingest endpoint
2. Dense retriever
3. Sparse retriever (BM25)
4. Hybrid retriever
5. Query endpoint
6. Middleware (RequestID, logging, rate-limit)

### Phase 3: Compliance & Workers (Day 3)
1. PII detector
2. Consent manager
3. Audit logger
4. Encryption helper
5. DSAR endpoints
6. Celery workers
7. Tests

## 📝 Code Templates

Below are the complete implementations for each remaining file. Copy these to your project.

---

## 1. Text Chunker (`src/core/ingestion/text_chunker.py`)

```python
\"\"\"
Token-aware text chunking with overlap
Uses tiktoken for accurate token counting
\"\"\"

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class TextChunker:
    \"\"\"Chunks text into token-aware segments\"\"\"
    
    def __init__(self, chunk_size: int = 1024, chunk_overlap: int = 128, strategy: str = "token-aware"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
        self._encoder = None
        self._init_encoder()
    
    def _init_encoder(self):
        \"\"\"Initialize token encoder\"\"\"
        try:
            import tiktoken
            self._encoder = tiktoken.get_encoding("cl100k_base")
            logger.info("Initialized tiktoken encoder")
        except ImportError:
            logger.warning("tiktoken not available, falling back to character-based chunking")
            self._encoder = None
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        \"\"\"
        Chunk text into segments
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
        
        Returns:
            List of chunks with metadata
        \"\"\"
        if not text or not text.strip():
            return []
        
        if self._encoder and self.strategy == "token-aware":
            chunks = self._token_aware_chunking(text)
        else:
            chunks = self._sentence_based_chunking(text)
        
        # Add metadata
        result = []
        for i, chunk_text in enumerate(chunks):
            chunk = {
                "chunk_id": i,
                "text": chunk_text,
                "char_count": len(chunk_text),
                **(metadata or {})
            }
            result.append(chunk)
        
        return result
    
    def _token_aware_chunking(self, text: str) -> List[str]:
        \"\"\"Chunk based on token count\"\"\"
        tokens = self._encoder.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self._encoder.decode(chunk_tokens)
            chunks.append(chunk_text)
            start = end - self.chunk_overlap
        
        return chunks
    
    def _sentence_based_chunking(self, text: str) -> List[str]:
        \"\"\"Fallback: chunk based on sentences\"\"\"
        import re
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\\s+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                # Keep overlap
                overlap_sentences = current_chunk[-(self.chunk_overlap // 100):]
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
```

---

## 2. PDF Processor (`src/core/ingestion/pdf_processor.py`)

```python
\"\"\"
PDF processor for extracting text and images
Handles pure text, pure image, and mixed PDFs
\"\"\"

import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class PDFProcessor:
    \"\"\"Process PDFs and extract text and images\"\"\"
    
    def __init__(self, ocr_processor=None):
        self.ocr_processor = ocr_processor
    
    def process(self, file_path: str) -> Dict[str, Any]:
        \"\"\"
        Process PDF and extract all content
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Dictionary with extracted text, images, and metadata
        \"\"\"
        try:
            # Try text extraction first
            text_content, has_text = self._extract_text_pdfplumber(file_path)
            
            # Extract images
            images = self._extract_images(file_path)
            
            # If no text but has images, run OCR
            if not has_text and images and self.ocr_processor:
                logger.info(f"No text found, running OCR on {len(images)} images")
                ocr_text = []
                for img_path, page_num in images:
                    try:
                        ocr_result = self.ocr_processor.process(img_path)
                        ocr_text.append({
                            "page": page_num,
                            "text": ocr_result.get("text", "")
                        })
                    except Exception as e:
                        logger.error(f"OCR failed for image: {e}")
                
                # Merge OCR text
                for item in ocr_text:
                    page_num = item["page"]
                    text = item["text"]
                    if page_num < len(text_content):
                        text_content[page_num]["text"] += "\\n" + text
            
            return {
                "text_content": text_content,
                "images": images,
                "page_count": len(text_content),
                "has_text": has_text,
                "has_images": len(images) > 0
            }
        
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            raise
    
    def _extract_text_pdfplumber(self, file_path: str) -> Tuple[List[Dict[str, Any]], bool]:
        \"\"\"Extract text using pdfplumber\"\"\"
        import pdfplumber
        
        pages = []
        has_text = False
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if text.strip():
                    has_text = True
                
                pages.append({
                    "page": page_num + 1,
                    "text": text,
                    "width": page.width,
                    "height": page.height
                })
        
        return pages, has_text
    
    def _extract_images(self, file_path: str) -> List[Tuple[str, int]]:
        \"\"\"Extract images from PDF\"\"\"
        try:
            from pdf2image import convert_from_path
            
            images = convert_from_path(file_path)
            extracted = []
            
            for i, image in enumerate(images):
                # Save to temp file
                temp_path = tempfile.mktemp(suffix=".png")
                image.save(temp_path, "PNG")
                extracted.append((temp_path, i + 1))
            
            return extracted
        
        except Exception as e:
            logger.warning(f"Image extraction failed: {e}")
            return []
```

---

## 3. Image Processor (`src/core/ingestion/image_processor.py`)

```python
\"\"\"
Image processor with OCR and vision model support
\"\"\"

import logging
from typing import Dict, Any, Optional

from PIL import Image

logger = logging.getLogger(__name__)


class ImageProcessor:
    \"\"\"Process images with OCR and vision models\"\"\"
    
    def __init__(self, ocr_langs: str = "eng", ocr_config: str = "--oem 3 --psm 6", vision_model: Optional[Any] = None):
        self.ocr_langs = ocr_langs
        self.ocr_config = ocr_config
        self.vision_model = vision_model
    
    def process(self, image_path: str) -> Dict[str, Any]:
        \"\"\"
        Process image with OCR and optional vision model
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary with OCR text and image metadata
        \"\"\"
        try:
            # Load image
            image = Image.open(image_path)
            
            # Run OCR
            ocr_text = self._run_ocr(image)
            
            # Get image metadata
            metadata = {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode
            }
            
            # Optional: Run vision model for caption/description
            caption = None
            if self.vision_model:
                caption = self._generate_caption(image)
            
            return {
                "text": ocr_text,
                "caption": caption,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise
    
    def _run_ocr(self, image: Image.Image) -> str:
        \"\"\"Run Tesseract OCR\"\"\"
        try:
            import pytesseract
            
            text = pytesseract.image_to_string(
                image,
                lang=self.ocr_langs,
                config=self.ocr_config
            )
            return text.strip()
        
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""
    
    def _generate_caption(self, image: Image.Image) -> Optional[str]:
        \"\"\"Generate image caption using vision model\"\"\"
        try:
            if self.vision_model:
                return self.vision_model.generate_caption(image)
        except Exception as e:
            logger.warning(f"Caption generation failed: {e}")
        return None
```

---

## 4. FastAPI Main Application (`src/api/main.py`)

```python
\"\"\"
FastAPI application factory
\"\"\"

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from src.config import settings
from src.api.routes import health, ingest, query, dsar
from src.api.middleware.request_id import RequestIDMiddleware
from src.api.middleware.logging_middleware import LoggingMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    \"\"\"Lifecycle events\"\"\"
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    \"\"\"Create and configure FastAPI application\"\"\"
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=\"Production-grade Multimodal RAG System\",
        lifespan=lifespan
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=[\"*\"],
        allow_headers=[\"*\"],
    )
    
    # Custom middleware
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # Routes
    app.include_router(health.router, tags=[\"Health\"])
    app.include_router(ingest.router, prefix=\"/ingest\", tags=[\"Ingestion\"])
    app.include_router(query.router, prefix=\"/query\", tags=[\"Query\"])
    app.include_router(dsar.router, prefix=\"/dsar\", tags=[\"DSAR\"])
    
    # Prometheus metrics
    if settings.enable_metrics:
        metrics_app = make_asgi_app()
        app.mount(\"/metrics\", metrics_app)
    
    return app


app = create_app()
```

---

Continue this implementation by creating each file from the templates above. The complete system requires approximately 30-35 source files.

## 🚀 Quick Start Implementation

1. **Copy all configuration files** (already done ✓)
2. **Implement core components** (vector_adapter, llm provider ✓)
3. **Create processing pipeline** (use templates above)
4. **Build API endpoints** (FastAPI routes)
5. **Add security layer** (PII, consent, audit)
6. **Setup workers** (Celery tasks)
7. **Write tests**
8. **Create sample data**

## 📦 Next Steps

Run these commands to complete the setup:

```bash
# 1. Copy .env.example to .env and configure
cp .env.example .env

# 2. Install dependencies (if running locally)
pip install -r requirements.txt

# 3. Start services
docker-compose up -d

# 4. Run tests (once implemented)
pytest tests/ -v

# 5. Access API
curl http://localhost:8000/healthz
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [LangChain Documentation](https://python.langchain.com/)
- [Sentence Transformers](https://www.sbert.net/)

---

**Note**: This is a production-grade system. Each component should be thoroughly tested before deployment.
