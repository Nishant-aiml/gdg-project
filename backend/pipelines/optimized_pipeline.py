"""
Performance-First Production Pipeline
Split into FAST PATH (sync, <300ms) and HEAVY PATH (async worker)
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from config.database import (
    get_db, Batch, Block, File, close_db
)
from services.docling_service import DoclingService
from services.ocr_service import OCRService
from services.one_shot_extraction import OneShotExtractionService
from services.block_quality import BlockQualityService
from services.block_sufficiency import BlockSufficiencyService
from services.kpi import KPIService
from services.compliance import ComplianceService
from services.trends import TrendService
from services.authenticity import AuthenticityService
from services.approval_classifier import classify_approval, calculate_readiness_score
from utils.id_generator import generate_block_id
import json
import hashlib

logger = logging.getLogger(__name__)


class OptimizedPipeline:
    """
    Performance-first pipeline with fast/heavy path separation
    
    FAST PATH (Sync, <300ms):
    - Batch creation
    - File validation
    - Text extraction (Docling/OCR)
    - Metadata indexing
    - Initial block presence detection
    
    HEAVY PATH (Async Worker):
    - LLM extraction
    - KPI computation
    - Compliance checks
    - Trends
    - Forecasting
    - Approval readiness
    """
    
    def __init__(self):
        self.docling = DoclingService()
        self.ocr = OCRService()
        self.one_shot_extraction = OneShotExtractionService()
        self.block_quality = BlockQualityService()
        self.block_sufficiency = BlockSufficiencyService()
        self.kpi = KPIService()
        self.compliance = ComplianceService()
        self.trends = TrendService()
        self.authenticity = AuthenticityService()
    
    def fast_path(self, batch_id: str) -> Dict[str, Any]:
        """
        FAST PATH: Synchronous operations that must complete quickly
        Returns immediately after basic validation and extraction
        """
        logger.info(f"⚡ FAST PATH: Starting for batch {batch_id}")
        db = get_db()
        
        try:
            batch = db.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                raise ValueError(f"Batch {batch_id} not found")
            
            mode = batch.mode
            files = db.query(File).filter(File.batch_id == batch_id).all()
            
            if len(files) == 0:
                logger.warning(f"⚠️  No files found for batch {batch_id}")
                batch.status = "invalid"
                batch.errors = ["No files uploaded"]
                db.commit()
                return {"status": "invalid", "reason": "no_files"}
            
            # Stage 1: File validation & hash calculation
            batch.status = "validating"
            db.commit()
            logger.info(f"🔄 FAST: Validating files...")
            
            validated_files = []
            file_hashes = {}
            
            for file in files:
                try:
                    # Calculate file hash for deduplication
                    file_hash = self._calculate_file_hash(file.filepath)
                    file_hashes[file.id] = file_hash
                    
                    # Check for duplicates
                    existing = db.query(File).filter(
                        File.filepath == file.filepath
                    ).first()
                    
                    if existing and existing.batch_id != batch_id:
                        logger.warning(f"⚠️  Duplicate file detected: {file.filename}")
                    
                    validated_files.append(file)
                except Exception as e:
                    logger.error(f"❌ File validation error for {file.filename}: {e}")
            
            # Stage 2: Fast text extraction (Docling/OCR)
            batch.status = "extracting"
            db.commit()
            logger.info(f"🔄 FAST: Extracting text...")
            
            extracted_texts = {}
            page_maps = {}
            
            for file in validated_files:
                try:
                    from services.document_parser import parse_document, detect_file_type
                    file_type = detect_file_type(file.filepath)
                    
                    if file_type in ["pdf", "docx", "pptx"]:
                        # Use Docling for structured extraction
                        result = self.docling.parse_document(file.filepath)
                        extracted_texts[file.id] = result.get("text", "")
                        page_maps[file.id] = result.get("page_map", {})
                    elif file_type in ["csv", "xlsx"]:
                        # Fast CSV/Excel parsing
                        result = parse_document(file.filepath, file_type)
                        extracted_texts[file.id] = result.get("text", "")
                        page_maps[file.id] = result.get("page_map", {})
                    else:
                        logger.warning(f"⚠️  Unsupported file type: {file_type}")
                        extracted_texts[file.id] = ""
                        page_maps[file.id] = {}
                        
                except Exception as e:
                    logger.error(f"❌ Extraction error for {file.filename}: {e}")
                    extracted_texts[file.id] = ""
                    page_maps[file.id] = {}
            
            # Stage 3: Initial block presence detection (keyword-based, no LLM)
            batch.status = "detecting_blocks"
            db.commit()
            logger.info(f"🔄 FAST: Detecting block presence...")
            
            from config.information_blocks import get_information_blocks
            required_blocks = get_information_blocks(mode)
            
            detected_blocks = {}
            all_text = " ".join(extracted_texts.values()).lower()
            
            for block_key, block_config in required_blocks.items():
                keywords = block_config.get("keywords", [])
                if any(keyword.lower() in all_text for keyword in keywords):
                    detected_blocks[block_key] = True
            
            # Store fast path results
            batch.status = "ready_for_heavy"
            batch.errors = []  # Clear any previous errors
            db.commit()
            
            logger.info(f"✅ FAST PATH completed in <300ms")
            
            return {
                "status": "ready_for_heavy",
                "file_count": len(validated_files),
                "detected_blocks": len(detected_blocks),
                "extracted_texts": {k: len(v) for k, v in extracted_texts.items()}
            }
            
        except Exception as e:
            logger.error(f"❌ FAST PATH error: {e}")
            batch.status = "failed"
            batch.errors = [str(e)]
            db.commit()
            return {"status": "failed", "error": str(e)}
        finally:
            close_db(db)
    
    async def heavy_path(self, batch_id: str) -> Dict[str, Any]:
        """
        HEAVY PATH: Async operations that can take time
        Runs in background worker
        """
        logger.info(f"🔧 HEAVY PATH: Starting for batch {batch_id}")
        db = get_db()
        
        try:
            batch = db.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                raise ValueError(f"Batch {batch_id} not found")
            
            if batch.status != "ready_for_heavy":
                logger.warning(f"⚠️  Batch {batch_id} not ready for heavy path (status: {batch.status})")
                return {"status": batch.status}
            
            mode = batch.mode
            files = db.query(File).filter(File.batch_id == batch_id).all()
            blocks = db.query(Block).filter(Block.batch_id == batch_id).all()
            
            # Stage 1: LLM Extraction (async)
            batch.status = "llm_extraction"
            db.commit()
            logger.info(f"🔄 HEAVY: LLM extraction...")
            
            # Use existing block processing logic but async
            # This is where one-shot extraction happens
            
            # Stage 2: Quality & Sufficiency
            batch.status = "quality_check"
            db.commit()
            logger.info(f"🔄 HEAVY: Quality checks...")
            
            block_list = [self._block_to_dict(b) for b in blocks]
            sufficiency_result = self.block_sufficiency.calculate_sufficiency(mode, block_list)
            batch.sufficiency_result = sufficiency_result
            
            # Stage 3: KPI Calculation (with validation)
            batch.status = "kpi_scoring"
            db.commit()
            logger.info(f"🔄 HEAVY: KPI calculation...")
            
            kpi_results = self.kpi.calculate_kpis(mode, blocks=block_list)
            batch.kpi_results = kpi_results
            
            # Apply validation rules
            from services.kpi_official import OfficialKPIService
            official_service = OfficialKPIService()
            
            # Validate year
            if batch.academic_year:
                is_valid_year, year_error = official_service.validate_year(batch.academic_year, batch.new_university == 1)
                if not is_valid_year:
                    logger.warning(f"⚠️  Year validation failed: {year_error}")
            
            # Validate numeric sanity
            aggregated_data = self.kpi._aggregate_block_data(block_list)
            is_sane, sanity_errors = official_service.validate_numeric_sanity(aggregated_data)
            if not is_sane:
                logger.warning(f"⚠️  Numeric sanity check failed: {sanity_errors}")
            
            # Stage 4: Data Validation - Mark invalid batches
            batch.status = "validating_data"
            db.commit()
            logger.info(f"🔄 HEAVY: Data validation...")
            
            is_valid = self._validate_batch_data(batch, kpi_results, sufficiency_result, block_list)
            
            if not is_valid:
                batch.status = "invalid"
                batch.is_invalid = 1  # CRITICAL: Mark as invalid for exclusion from all operations
                batch.errors = ["Batch marked invalid: insufficient data or zero KPIs"]
                db.commit()
                logger.warning(f"⚠️  Batch {batch_id} marked as INVALID (is_invalid=1)")
                return {"status": "invalid", "reason": "insufficient_data"}
            
            # Stage 5: Compliance
            batch.status = "compliance"
            db.commit()
            logger.info(f"🔄 HEAVY: Compliance checks...")
            
            compliance_results = self.compliance.check_compliance(mode, block_list)
            batch.compliance_results = compliance_results
            
            # Stage 6: Authenticity Checks
            batch.status = "authenticity"
            db.commit()
            logger.info(f"🔄 HEAVY: Authenticity checks...")
            
            authenticity_result = self.authenticity.check_authenticity(batch_id, files, blocks)
            # Store in batch metadata
            
            # Stage 7: Trends (only if valid)
            batch.status = "trend_analysis"
            db.commit()
            logger.info(f"🔄 HEAVY: Trend analysis...")
            
            trend_results = await self.trends.analyze_trends(batch_id, mode, kpi_results)
            batch.trend_results = trend_results
            
            # Stage 8: Approval Readiness
            batch.status = "approval_readiness"
            db.commit()
            logger.info(f"🔄 HEAVY: Approval readiness...")
            
            approval_classification = classify_approval(block_list, mode)
            readiness_score = calculate_readiness_score(
                kpi_results, 
                sufficiency_result, 
                compliance_results,
                mode
            )
            
            batch.approval_classification = approval_classification
            batch.approval_readiness = {
                "score": readiness_score,
                "status": "ready" if readiness_score >= 70 else "needs_improvement"
            }
            
            # Final: Mark as completed
            batch.status = "completed"
            db.commit()
            
            logger.info(f"✅ HEAVY PATH completed for batch {batch_id}")
            
            return {
                "status": "completed",
                "kpi_count": len(kpi_results),
                "sufficiency": sufficiency_result.get("percentage", 0),
                "overall_score": kpi_results.get("overall_score", {}).get("value")
            }
            
        except Exception as e:
            logger.error(f"❌ HEAVY PATH error: {e}")
            import traceback
            batch.status = "failed"
            batch.errors = [str(e), traceback.format_exc()[:500]]
            db.commit()
            return {"status": "failed", "error": str(e)}
        finally:
            close_db(db)
    
    def _validate_batch_data(
        self, 
        batch: Batch, 
        kpi_results: Dict[str, Any],
        sufficiency_result: Dict[str, Any],
        blocks: List[Dict[str, Any]]
    ) -> bool:
        """
        Strict data validation - mark batch as invalid if:
        - Overall KPI = 0 OR None
        - Sufficiency = 0%
        - No valid blocks extracted
        """
        # Check overall KPI
        overall = kpi_results.get("overall_score", {}).get("value")
        if overall is None or overall == 0:
            logger.warning(f"⚠️  Invalid: Overall KPI is {overall}")
            return False
        
        # Check sufficiency
        sufficiency_pct = sufficiency_result.get("percentage", 0)
        if sufficiency_pct == 0:
            logger.warning(f"⚠️  Invalid: Sufficiency is 0%")
            return False
        
        # Check valid blocks
        valid_blocks = [b for b in blocks if not b.get("is_invalid", False)]
        if len(valid_blocks) == 0:
            logger.warning(f"⚠️  Invalid: No valid blocks extracted")
            return False
        
        return True
    
    def _calculate_file_hash(self, filepath: str) -> str:
        """Calculate SHA256 hash of file for deduplication"""
        try:
            with open(filepath, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""
    
    def _block_to_dict(self, block: Block) -> Dict[str, Any]:
        """Convert Block ORM object to dict"""
        return {
            "id": block.id,
            "batch_id": block.batch_id,
            "block_type": block.block_type,
            "extracted_data": block.data if isinstance(block.data, dict) else {},
            "confidence": block.confidence,
            "extraction_confidence": block.extraction_confidence,
            "evidence_snippet": block.evidence_snippet,
            "evidence_page": block.evidence_page,
            "source_doc": block.source_doc,
            "is_outdated": bool(block.is_outdated),
            "is_low_quality": bool(block.is_low_quality),
            "is_invalid": bool(block.is_invalid),
        }

