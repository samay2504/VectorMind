"""
PDF processor for extracting text and images
Handles pure text, pure image, and mixed PDFs

═══════════════════════════════════════════════════════════════════════════
Copyright © 2025 Samay Mehar. All Rights Reserved.
PROPRIETARY SOFTWARE - PATENT PENDING
Author: Samay Mehar | Created: October 31 - November 1, 2025
Unauthorized use is strictly prohibited and may result in legal action.
═══════════════════════════════════════════════════════════════════════════
"""

import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process PDFs and extract text and images"""
    
    def __init__(self, ocr_processor=None):
        self.ocr_processor = ocr_processor
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Process PDF and extract all content
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Dictionary with extracted text, images, and metadata
        """
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
                        text_content[page_num]["text"] += "\n" + text
            
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
        """Extract text using pdfplumber"""
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
        """Extract images from PDF"""
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
