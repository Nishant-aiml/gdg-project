"""
Government Document Parser
Extracts text from government letters, circulars, and schemes using Google Vision OCR
"""

import logging
from typing import Dict, Any, Optional
from services.google_ocr_service import GoogleOCRService
from services.docling_service import DoclingService
from services.ocr_service import OCRService
import os

logger = logging.getLogger(__name__)


class GovDocumentParser:
    """
    Parser for government documents (circulars, letters, schemes)
    Uses Google Vision OCR as primary, falls back to existing OCR services
    """
    
    def __init__(self):
        self.google_ocr = GoogleOCRService()
        self.docling = DoclingService()
        self.ocr_service = OCRService()
    
    def parse_document(
        self,
        file_path: str,
        file_name: str
    ) -> Dict[str, Any]:
        """
        Parse government document and extract text.
        
        Args:
            file_path: Path to document file
            file_name: Original file name
        
        Returns:
            Dict with:
                - extracted_text: Full text content
                - document_type: Detected type (circular, letter, scheme, etc.)
                - page_count: Number of pages
                - confidence: Extraction confidence
        """
        try:
            # Try Google Vision OCR first (primary for gov documents)
            if self.google_ocr.available:
                logger.info(f"Using Google Vision OCR for {file_name}")
                try:
                    result = self.google_ocr.ocr_pdf_pages(file_path)
                    # Handle both tuple and dict return types
                    if isinstance(result, tuple):
                        text, page_count = result
                    else:
                        text = result.get("text", "")
                        page_count = result.get("page_count", 1)
                    
                    if text and len(text.strip()) > 100:  # Minimum text threshold
                        document_type = self._detect_document_type(text, file_name)
                        return {
                            "extracted_text": text,
                            "document_type": document_type,
                            "page_count": page_count if isinstance(page_count, int) else 1,
                            "confidence": 0.9,  # Google Vision is high confidence
                            "method": "google_vision"
                        }
                    else:
                        logger.warning(f"Google Vision OCR returned insufficient text for {file_name}, trying fallback")
                except Exception as e:
                    logger.warning(f"Google Vision OCR failed: {e}, trying fallback")
            
            # Fallback 1: Docling (structured PDF parsing)
            if os.path.exists(file_path) and file_path.lower().endswith('.pdf'):
                logger.info(f"Using Docling parser for {file_name}")
                structured_text = self.docling.parse_pdf_to_structured_text(file_path)
                
                if structured_text and len(structured_text.strip()) > 100:
                    document_type = self._detect_document_type(structured_text, file_name)
                    return {
                        "extracted_text": structured_text,
                        "document_type": document_type,
                        "page_count": 1,  # Docling doesn't return page count easily
                        "confidence": 0.8,
                        "method": "docling"
                    }
            
            # Fallback 2: General OCR service (PaddleOCR)
            logger.info(f"Using general OCR service for {file_name}")
            text, page_count = self.ocr_service.ocr_pdf_pages(file_path)
            
            if text and len(text.strip()) > 50:
                document_type = self._detect_document_type(text, file_name)
                return {
                    "extracted_text": text,
                    "document_type": document_type,
                    "page_count": page_count,
                    "confidence": 0.7,
                    "method": "paddleocr"
                }
            
            # If all methods fail
            logger.error(f"All OCR methods failed for {file_name}")
            return {
                "extracted_text": "",
                "document_type": "unknown",
                "page_count": 0,
                "confidence": 0.0,
                "method": "none",
                "error": "Could not extract text from document"
            }
        
        except Exception as e:
            logger.error(f"Error parsing government document {file_name}: {e}", exc_info=True)
            return {
                "extracted_text": "",
                "document_type": "unknown",
                "page_count": 0,
                "confidence": 0.0,
                "method": "error",
                "error": str(e)
            }
    
    def _detect_document_type(self, text: str, file_name: str) -> str:
        """
        Detect document type from text and filename.
        
        Returns:
            Document type: "circular", "letter", "scheme", "notice", "order", etc.
        """
        text_lower = text.lower()[:500]  # Check first 500 chars
        file_lower = file_name.lower()
        
        # Check for keywords
        if any(keyword in text_lower for keyword in ["circular", "circular no", "circular number"]):
            return "circular"
        elif any(keyword in text_lower for keyword in ["scheme", "yojana", "programme"]):
            return "scheme"
        elif any(keyword in text_lower for keyword in ["order", "g.o", "government order"]):
            return "order"
        elif any(keyword in text_lower for keyword in ["notice", "notification"]):
            return "notice"
        elif any(keyword in text_lower for keyword in ["letter", "d.o", "dear"]):
            return "letter"
        elif any(keyword in text_lower for keyword in ["guideline", "guidelines"]):
            return "guideline"
        else:
            # Check filename
            if "circular" in file_lower:
                return "circular"
            elif "scheme" in file_lower or "yojana" in file_lower:
                return "scheme"
            elif "letter" in file_lower:
                return "letter"
            elif "notice" in file_lower:
                return "notice"
            else:
                return "document"  # Generic fallback

