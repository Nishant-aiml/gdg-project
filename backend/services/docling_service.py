"""
Fast Document Parsing Service
Uses PyMuPDF (fitz) + pdfplumber for fast, efficient extraction
Replaces heavy Docling dependency for Railway deployment
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import os
import json

logger = logging.getLogger(__name__)

# Try importing fast extraction libraries
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF not installed. pip install PyMuPDF")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber not installed. pip install pdfplumber")


class DoclingService:
    """Fast document parsing service using PyMuPDF + pdfplumber"""
    
    def __init__(self):
        self.docling_available = PYMUPDF_AVAILABLE  # For compatibility
        logger.info(f"DoclingService initialized (PyMuPDF: {PYMUPDF_AVAILABLE}, pdfplumber: {PDFPLUMBER_AVAILABLE})")
    
    def parse_pdf_to_structured_text(self, filepath: str) -> Dict[str, Any]:
        """
        Parse PDF to structured text using PyMuPDF (fast!) with pdfplumber for tables
        Returns: {
            full_text: str,
            section_chunks: List[Dict],
            tables_text: str,
            sections: List[Dict]
        }
        """
        if PYMUPDF_AVAILABLE:
            return self._pymupdf_extraction(filepath)
        else:
            return self._fallback_extraction(filepath)
    
    def _pymupdf_extraction(self, filepath: str) -> Dict[str, Any]:
        """Ultra-fast extraction using PyMuPDF"""
        try:
            doc = fitz.open(filepath)
            full_text_parts = []
            sections = []
            current_section = None
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text with layout preservation
                text = page.get_text("text")
                if text and text.strip():
                    full_text_parts.append(f"[Page {page_num + 1}]\n{text}")
                    
                    # Simple section detection based on font size/bold
                    blocks = page.get_text("dict")["blocks"]
                    for block in blocks:
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    # Detect headers by font size > 12 or bold
                                    if span["size"] > 12 or "bold" in span["font"].lower():
                                        section_title = span["text"].strip()
                                        if section_title and len(section_title) > 3:
                                            if current_section:
                                                sections.append(current_section)
                                            current_section = {
                                                "title": section_title,
                                                "level": 1 if span["size"] > 14 else 2,
                                                "page": page_num + 1,
                                                "content": []
                                            }
                                    elif current_section and span["text"].strip():
                                        current_section["content"].append(span["text"].strip())
            
            if current_section:
                sections.append(current_section)
            
            doc.close()
            
            # Extract tables using pdfplumber (more accurate for tables)
            tables_text = ""
            if PDFPLUMBER_AVAILABLE:
                tables_text = self._extract_tables_pdfplumber(filepath)
            
            full_text = "\n\n".join(full_text_parts)
            
            # Add tables to full text
            if tables_text:
                full_text += f"\n\n[TABLES]\n{tables_text}\n[/TABLES]"
            
            logger.info(f"PyMuPDF extraction: {len(full_text)} chars, {len(sections)} sections")
            
            # Create section chunks
            section_chunks = []
            for section in sections:
                section_text = " ".join(section.get("content", []))
                section_chunks.append({
                    "title": section["title"],
                    "level": section["level"],
                    "page": section.get("page", 1),
                    "text": section_text
                })
            
            return {
                "full_text": full_text,
                "section_chunks": section_chunks,
                "tables_text": tables_text,
                "sections": sections,
                "page_count": len(full_text_parts),
                "has_text": len(full_text.strip()) > 0
            }
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction error: {e}")
            return self._fallback_extraction(filepath)
    
    def _extract_tables_pdfplumber(self, filepath: str) -> str:
        """Extract tables using pdfplumber (more accurate than PyMuPDF for tables)"""
        try:
            tables_text_parts = []
            with pdfplumber.open(filepath) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if table:
                            table_text = f"[Table Page {page_num + 1}]\n"
                            for row in table:
                                row_text = " | ".join([str(cell or "") for cell in row])
                                table_text += row_text + "\n"
                            tables_text_parts.append(table_text)
            
            return "\n".join(tables_text_parts)
        except Exception as e:
            logger.warning(f"pdfplumber table extraction error: {e}")
            return ""
    
    def extract_tables(self, filepath: str) -> List[Dict[str, Any]]:
        """Extract tables from PDF"""
        tables = []
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(filepath) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        page_tables = page.extract_tables()
                        for table in page_tables:
                            if table:
                                tables.append({
                                    "rows": table,
                                    "row_count": len(table),
                                    "column_count": len(table[0]) if table else 0,
                                    "page": page_num + 1
                                })
            except Exception as e:
                logger.error(f"Table extraction error: {e}")
        return tables
    
    def extract_sections(self, filepath: str) -> List[Dict[str, Any]]:
        """Extract document sections with headers"""
        result = self.parse_pdf_to_structured_text(filepath)
        return result.get("sections", [])
    
    def _fallback_extraction(self, filepath: str) -> Dict[str, Any]:
        """Fallback extraction using pypdf when PyMuPDF is not available"""
        try:
            import pypdf
            
            full_text_parts = []
            with open(filepath, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        full_text_parts.append(f"[Page {page_num + 1}]\n{text}")
            
            full_text = "\n\n".join(full_text_parts)
            logger.info(f"Fallback extraction: {len(full_text)} chars")
            
            return {
                "full_text": full_text,
                "section_chunks": [],
                "tables_text": "",
                "sections": [],
                "page_count": num_pages if full_text_parts else 0,
                "has_text": len(full_text.strip()) > 0
            }
        except Exception as e:
            logger.error(f"Fallback extraction error: {e}")
            return {
                "full_text": "",
                "section_chunks": [],
                "tables_text": "",
                "sections": [],
                "page_count": 0,
                "has_text": False,
                "error": str(e)
            }
    
    def parse_document(self, filepath: str) -> Dict[str, Any]:
        """Alias for compatibility with existing code"""
        return self.parse_pdf_to_structured_text(filepath)
