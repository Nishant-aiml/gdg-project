"""
Google Cloud Vision API OCR Service
Free tier: 1,000 images per month
Falls back to PaddleOCR if unavailable or quota exceeded
PERFORMANCE: 15s timeout, max 2 retries
"""

import logging
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
from utils.retry_with_timeout import retry_with_timeout

logger = logging.getLogger(__name__)

try:
    from google.cloud import vision
    from google.oauth2 import service_account
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    logger.warning("google-cloud-vision not installed. Install with: pip install google-cloud-vision")


class GoogleOCRService:
    """
    Google Cloud Vision API OCR service
    Free tier: 1,000 images/month
    """
    
    def __init__(self):
        self.client = None
        self.available = False
        
        # Check for Google Cloud credentials
        google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if not GOOGLE_VISION_AVAILABLE:
            logger.warning("google-cloud-vision package not installed. Google OCR will not be available.")
            return
        
        try:
            if google_credentials_path and Path(google_credentials_path).exists():
                # Use service account credentials (recommended method)
                credentials = service_account.Credentials.from_service_account_file(
                    google_credentials_path
                )
                self.client = vision.ImageAnnotatorClient(credentials=credentials)
                self.available = True
                logger.info("Google Cloud Vision API initialized with service account credentials")
            else:
                # Try default credentials (if running on GCP or gcloud auth is set)
                try:
                    self.client = vision.ImageAnnotatorClient()
                    self.available = True
                    logger.info("Google Cloud Vision API initialized with default credentials")
                except Exception as default_err:
                    logger.info("Google Cloud Vision API credentials not found. Will use PaddleOCR fallback.")
                    logger.info("To enable Google OCR (free tier: 1,000 images/month):")
                    logger.info("  1. Set GOOGLE_APPLICATION_CREDENTIALS to path of service account JSON file")
                    logger.info("  2. Or run: gcloud auth application-default login")
                    self.available = False
        except Exception as e:
            logger.warning(f"Failed to initialize Google Cloud Vision API: {e}. Will use PaddleOCR fallback.")
            self.available = False
    
    def ocr_image(self, image_path: str) -> Optional[str]:
        """
        Run OCR on a single image using Google Cloud Vision API
        PERFORMANCE: 15s timeout, max 2 retries
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text or None if failed
        """
        if not self.available or not self.client:
            return None
        
        @retry_with_timeout(max_retries=2, timeout_seconds=15, delay_seconds=1.0)
        def _ocr_with_retry():
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = self.client.text_detection(image=image)
            
            if response.error.message:
                logger.error(f"Google Vision API error: {response.error.message}")
                return None
            
            texts = response.text_annotations
            if texts:
                # First annotation contains the entire detected text
                return texts[0].description
            
            return None
        
        try:
            return _ocr_with_retry()
        except Exception as e:
            logger.warning(f"Google OCR error for {image_path} after retries: {e}")
            return None
    
    def ocr_pdf_pages(self, pdf_path: str, page_numbers: List[int]) -> Dict[int, str]:
        """
        Run OCR on specific pages of a PDF using Google Cloud Vision API
        Note: Google Vision API works on images, so PDF pages must be converted first
        
        Args:
            pdf_path: Path to PDF file
            page_numbers: List of page numbers to OCR (1-indexed)
            
        Returns:
            Dict mapping page number to extracted text
        """
        if not self.available or not self.client:
            return {}
        
        try:
            # Convert PDF pages to images
            from pdf2image import convert_from_path
            images = convert_from_path(
                pdf_path, 
                first_page=min(page_numbers), 
                last_page=max(page_numbers)
            )
            
            ocr_results = {}
            for idx, page_num in enumerate(page_numbers):
                if idx < len(images):
                    # Save temporary image
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        images[idx].save(tmp.name)
                        text = self.ocr_image(tmp.name)
                        if text:
                            ocr_results[page_num] = text
                        # Clean up
                        Path(tmp.name).unlink()
            
            return ocr_results
            
        except ImportError:
            logger.warning("pdf2image not installed. Cannot convert PDF pages to images.")
            return {}
        except Exception as e:
            logger.warning(f"Google PDF OCR error: {e}")
            return {}

