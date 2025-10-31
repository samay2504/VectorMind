"""
Image processor with OCR and vision model support
"""

import logging
from typing import Dict, Any, Optional

from PIL import Image

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Process images with OCR and vision models"""
    
    def __init__(self, ocr_langs: str = "eng", ocr_config: str = "--oem 3 --psm 6", vision_model: Optional[Any] = None):
        self.ocr_langs = ocr_langs
        self.ocr_config = ocr_config
        self.vision_model = vision_model
    
    def process(self, image_path: str) -> Dict[str, Any]:
        """
        Process image with OCR and optional vision model
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary with OCR text and image metadata
        """
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
        """Run Tesseract OCR"""
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
        """Generate image caption using vision model"""
        try:
            if self.vision_model:
                return self.vision_model.generate_caption(image)
        except Exception as e:
            logger.warning(f"Caption generation failed: {e}")
        return None
