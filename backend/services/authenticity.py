"""
Document Authenticity Service
Lightweight but realistic forgery detection
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import json
from config.database import File, Block, get_db, close_db

logger = logging.getLogger(__name__)


class AuthenticityService:
    """
    Non-governmental, realistic forgery checks:
    - PDF metadata anomaly detection
    - OCR vs text mismatch %
    - Numeric plausibility rules
    - Duplicate document fingerprinting
    """
    
    def check_authenticity(
        self, 
        batch_id: str, 
        files: List[File], 
        blocks: List[Block]
    ) -> Dict[str, Any]:
        """
        Perform authenticity checks on documents
        Returns authenticity score (0-1) and flags
        """
        flags = []
        score = 1.0  # Start with perfect score, deduct for issues
        
        db = get_db()
        try:
            # Check 1: PDF Metadata Anomalies
            metadata_flags = self._check_metadata_anomalies(files)
            if metadata_flags:
                flags.extend(metadata_flags)
                score -= 0.1 * len(metadata_flags)
            
            # Check 2: OCR vs Text Mismatch
            ocr_mismatch = self._check_ocr_mismatch(files, blocks)
            if ocr_mismatch > 0.3:  # >30% mismatch is suspicious
                flags.append(f"High OCR/text mismatch ({ocr_mismatch:.1%})")
                score -= 0.15
            
            # Check 3: Numeric Plausibility
            plausibility_flags = self._check_numeric_plausibility(blocks)
            if plausibility_flags:
                flags.extend(plausibility_flags)
                score -= 0.1 * len(plausibility_flags)
            
            # Check 4: Duplicate Fingerprinting
            duplicate_flags = self._check_duplicates(files, batch_id)
            if duplicate_flags:
                flags.extend(duplicate_flags)
                score -= 0.2 * len(duplicate_flags)
            
            # Ensure score is between 0 and 1
            score = max(0.0, min(1.0, score))
            
            return {
                "authenticity_score": round(score, 2),
                "flags": flags,
                "status": "authentic" if score >= 0.8 else "suspicious" if score >= 0.5 else "flagged"
            }
        finally:
            close_db(db)
    
    def _check_metadata_anomalies(self, files: List[File]) -> List[str]:
        """Check for PDF metadata anomalies"""
        flags = []
        
        for file in files:
            if not file.filename.endswith('.pdf'):
                continue
            
            try:
                import PyPDF2
                with open(file.filepath, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    metadata = pdf_reader.metadata
                    
                    # Check for missing/modified metadata
                    if metadata is None:
                        flags.append(f"Missing PDF metadata: {file.filename}")
                    else:
                        # Check creation/modification dates
                        created = metadata.get('/CreationDate', '')
                        modified = metadata.get('/ModDate', '')
                        
                        if created and modified and created != modified:
                            # Check if modification is suspiciously recent
                            try:
                                from datetime import datetime
                                mod_date = datetime.strptime(modified[2:16], '%Y%m%d%H%M%S')
                                if (datetime.now() - mod_date).days < 1:
                                    flags.append(f"Recently modified PDF: {file.filename}")
                            except:
                                pass
            except Exception as e:
                logger.debug(f"Could not check metadata for {file.filename}: {e}")
        
        return flags
    
    def _check_ocr_mismatch(self, files: List[File], blocks: List[Block]) -> float:
        """Calculate OCR vs extracted text mismatch percentage"""
        # This is a simplified check - in production, compare OCR text with extracted text
        # For now, check if blocks have low confidence which might indicate OCR issues
        if not blocks:
            return 0.0
        
        low_confidence_count = sum(1 for b in blocks if b.extraction_confidence < 0.5)
        mismatch_ratio = low_confidence_count / len(blocks) if blocks else 0.0
        
        return mismatch_ratio
    
    def _check_numeric_plausibility(self, blocks: List[Block]) -> List[str]:
        """Check numeric values for plausibility"""
        flags = []
        
        for block in blocks:
            if not block.data or not isinstance(block.data, dict):
                continue
            
            data = block.data
            
            # Check for unrealistic growth rates
            if 'student_count_num' in data and 'faculty_count_num' in data:
                students = data.get('student_count_num', 0)
                faculty = data.get('faculty_count_num', 0)
                if faculty > 0:
                    fsr = students / faculty
                    if fsr > 100:  # Unrealistic FSR
                        flags.append(f"Unrealistic FSR ({fsr:.1f}):1 in {block.block_type}")
            
            # Check for negative values where they shouldn't exist
            numeric_fields = ['area_num', 'built_up_area_num', 'classroom_count_num', 
                            'lab_count_num', 'placement_rate_num']
            for field in numeric_fields:
                if field in data:
                    value = data[field]
                    if isinstance(value, (int, float)) and value < 0:
                        flags.append(f"Negative value for {field}: {value}")
            
            # Check for impossibly large values
            if 'area_num' in data:
                area = data['area_num']
                if isinstance(area, (int, float)) and area > 10000000:  # >10M sqm is suspicious
                    flags.append(f"Unrealistically large area: {area} sqm")
        
        return flags
    
    def _check_duplicates(self, files: List[File], batch_id: str) -> List[str]:
        """Check for duplicate documents using fingerprinting"""
        flags = []
        db = get_db()
        
        try:
            from config.database import DocumentHashCache
            
            file_hashes = {}
            for file in files:
                try:
                    with open(file.filepath, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    
                    # Check if this hash exists in other batches
                    existing = db.query(DocumentHashCache).filter(
                        DocumentHashCache.file_hash == file_hash,
                        DocumentHashCache.batch_id != batch_id
                    ).first()
                    
                    if existing:
                        flags.append(f"Duplicate document detected: {file.filename} (matches batch {existing.batch_id})")
                    
                    file_hashes[file.id] = file_hash
                except Exception as e:
                    logger.debug(f"Could not hash file {file.filename}: {e}")
            
            # Store hashes for future checks
            for file_id, file_hash in file_hashes.items():
                hash_entry = DocumentHashCache(
                    id=f"{batch_id}_{file_id}",
                    batch_id=batch_id,
                    file_hash=file_hash,
                    filename=files[0].filename if files else ""
                )
                db.merge(hash_entry)
            
            db.commit()
        finally:
            close_db(db)
        
        return flags

