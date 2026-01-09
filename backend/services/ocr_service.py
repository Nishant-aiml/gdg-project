"""
OCR Service with Google Cloud Vision API (free tier) and PaddleOCR fallback
Priority: Google Vision API (free tier: 1,000 images/month) → PaddleOCR
PERFORMANCE: 15s timeout, max 2 retries
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from utils.retry_with_timeout import retry_with_timeout

logger = logging.getLogger(__name__)

# Import Google OCR service
try:
    from services.google_ocr_service import GoogleOCRService
    GOOGLE_OCR_AVAILABLE = True
except ImportError:
    GOOGLE_OCR_AVAILABLE = False
    logger.debug("Google OCR service not available")

# Import PaddleOCR as fallback
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    logger.warning("PaddleOCR not installed. Install with: pip install paddleocr")

class OCRService:
    """
    OCR service with Google Cloud Vision API (primary, free tier) and PaddleOCR (fallback)
    Free tier: 1,000 images/month via Google Cloud Vision API
    """
    
    def __init__(self):
        # Initialize Google OCR (primary, free tier)
        self.google_ocr = None
        if GOOGLE_OCR_AVAILABLE:
            try:
                self.google_ocr = GoogleOCRService()
                if self.google_ocr.available:
                    logger.info("Google Cloud Vision API OCR initialized (free tier: 1,000 images/month)")
                else:
                    logger.info("Google Cloud Vision API not configured. Will use PaddleOCR fallback.")
            except Exception as e:
                logger.warning(f"Failed to initialize Google OCR: {e}. Will use PaddleOCR fallback.")
        
        # Initialize PaddleOCR (fallback)
        self.paddle_ocr = None
        if PADDLEOCR_AVAILABLE:
            try:
                # Initialize PaddleOCR (use_angle_cls=True for better accuracy)
                # Try without show_log first (newer versions don't support it)
                try:
                    self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
                except TypeError:
                    # Fallback for versions that don't support show_log
                    self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')
                logger.info("PaddleOCR initialized as fallback")
            except Exception as e:
                logger.warning(f"Failed to initialize PaddleOCR: {e}")
                self.paddle_ocr = None
    
    def ocr_page(self, image_path: str) -> str:
        """
        Run OCR on a single page image
        PERFORMANCE: 15s timeout, max 2 retries
        Priority: Google Cloud Vision API (free tier) → PaddleOCR
        
        Returns: Extracted text
        """
        # Try Google Cloud Vision API first (free tier)
        if self.google_ocr and self.google_ocr.available:
            try:
                text = self.google_ocr.ocr_image(image_path)
                if text:
                    logger.debug(f"Google OCR successful for {image_path}")
                    return text
                else:
                    logger.debug(f"Google OCR returned empty text for {image_path}, trying PaddleOCR")
            except Exception as e:
                logger.warning(f"Google OCR error for {image_path}: {e}, falling back to PaddleOCR")
        
        # Fallback to PaddleOCR
        if not self.paddle_ocr:
            logger.warning("No OCR service available (neither Google nor PaddleOCR)")
            return ""
        
        @retry_with_timeout(max_retries=2, timeout_seconds=15, delay_seconds=1.0)
        def _paddle_ocr_with_retry():
            result = self.paddle_ocr.ocr(image_path, cls=True)
            
            if not result or not result[0]:
                return ""
            
            # Extract text from OCR results
            text_lines = []
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0] if isinstance(line[1], (list, tuple)) else str(line[1])
                    if text:
                        text_lines.append(text)
            
            return "\n".join(text_lines)
        
        try:
            return _paddle_ocr_with_retry()
        except Exception as e:
            logger.error(f"PaddleOCR error for {image_path} after retries: {e}")
            return ""
    
    def ocr_pdf_pages(self, pdf_path: str, page_numbers: List[int]) -> Dict[int, str]:
        """
        Run OCR on specific pages of a PDF
        Priority: Google Cloud Vision API (free tier) → PaddleOCR
        
        Returns: Dict mapping page number to extracted text
        """
        # Try Google Cloud Vision API first (free tier)
        if self.google_ocr and self.google_ocr.available:
            try:
                results = self.google_ocr.ocr_pdf_pages(pdf_path, page_numbers)
                if results:
                    logger.debug(f"Google OCR successful for PDF {pdf_path}, pages {page_numbers}")
                    return results
                else:
                    logger.debug(f"Google OCR returned empty results, trying PaddleOCR")
            except Exception as e:
                logger.warning(f"Google OCR error for PDF {pdf_path}: {e}, falling back to PaddleOCR")
        
        # Fallback to PaddleOCR
        if not self.paddle_ocr:
            logger.warning("No OCR service available (neither Google nor PaddleOCR)")
            return {}
        
        try:
            # Convert PDF pages to images
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path, first_page=min(page_numbers), last_page=max(page_numbers))
            
            ocr_results = {}
            for idx, page_num in enumerate(page_numbers):
                if idx < len(images):
                    # Save temporary image
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        images[idx].save(tmp.name)
                        # Use PaddleOCR directly (Google already tried above)
                        try:
                            result = self.paddle_ocr.ocr(tmp.name, cls=True)
                            if result and result[0]:
                                text_lines = []
                                for line in result[0]:
                                    if line and len(line) >= 2:
                                        text = line[1][0] if isinstance(line[1], (list, tuple)) else str(line[1])
                                        if text:
                                            text_lines.append(text)
                                text = "\n".join(text_lines)
                                if text:
                                    ocr_results[page_num] = text
                        except Exception as e:
                            logger.warning(f"PaddleOCR error for page {page_num}: {e}")
                        # Clean up
                        Path(tmp.name).unlink()
            
            return ocr_results
            
        except ImportError:
            logger.warning("pdf2image not installed. Cannot convert PDF pages to images.")
            return {}
        except Exception as e:
            logger.error(f"PaddleOCR PDF error: {e}")
            return {}

