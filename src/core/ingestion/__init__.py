"""
Ingestion Package - Document processing components
"""

from .text_chunker import TextChunker
from .pdf_processor import PDFProcessor
from .image_processor import ImageProcessor

# Optional processors (require additional dependencies)
try:
    from src.core.ingestion.docx_processor import DOCXProcessor, is_docx_available
except ImportError:
    DOCXProcessor = None
    is_docx_available = lambda: False

try:
    from src.core.ingestion.xlsx_processor import XLSXProcessor, is_xlsx_available
except ImportError:
    XLSXProcessor = None
    is_xlsx_available = lambda: False

__all__ = [
    "TextChunker",
    "PDFProcessor",
    "ImageProcessor",
    "DOCXProcessor",
    "XLSXProcessor",
    "is_docx_available",
    "is_xlsx_available",
]
