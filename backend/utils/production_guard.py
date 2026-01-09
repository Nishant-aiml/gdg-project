"""
ProductionGuard - Ensures NO dummy data in production
Enforces strict batch validation rules for regulatory compliance
"""

from typing import Dict, Any, Optional, List
from config.database import Batch
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class ProductionGuard:
    """
    Production-grade validation to ensure:
    - No dummy data anywhere
    - Invalid batches are properly marked
    - Only valid batches appear in compare/trends/forecast/reports
    """
    
    @staticmethod
    def mark_batch_invalid_if_needed(
        batch: Batch,
        kpi_results: Optional[Dict[str, Any]],
        sufficiency_result: Optional[Dict[str, Any]],
        db: Session
    ) -> bool:
        """
        Mark batch as invalid if it fails production criteria.
        Returns True if batch was marked invalid.
        
        Rules:
        - overall_score is None → invalid
        - sufficiency == 0 → invalid
        - no valid blocks → invalid
        """
        reasons = []
        
        # Check overall score
        if kpi_results:
            overall_score = kpi_results.get("overall_score")
            if overall_score is None:
                reasons.append("overall_score is null")
        else:
            reasons.append("no KPI results")
        
        # Check sufficiency
        if sufficiency_result:
            percentage = sufficiency_result.get("percentage", 0)
            present_count = sufficiency_result.get("present_count", 0)
            if percentage == 0 or present_count == 0:
                reasons.append(f"sufficiency is 0% ({present_count} blocks)")
        else:
            reasons.append("no sufficiency result")
        
        # Mark as invalid if any reason found
        if reasons:
            batch.is_invalid = 1
            logger.warning(f"Batch {batch.id} marked INVALID: {', '.join(reasons)}")
            db.commit()
            return True
        
        # Ensure valid batch is marked as valid
        if batch.is_invalid == 1:
            batch.is_invalid = 0
            db.commit()
        
        return False
    
    @staticmethod
    def validate_batch_for_operations(batch: Batch) -> Dict[str, Any]:
        """
        Validate batch before compare/trends/forecast/reports operations.
        Raises HTTPException if batch is invalid.
        
        Returns validation result dict for valid batches.
        """
        from fastapi import HTTPException
        
        if batch is None:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # Check if batch is marked invalid
        if batch.is_invalid == 1:
            raise HTTPException(
                status_code=400,
                detail=f"Batch {batch.id} is invalid and cannot be used for operations. "
                       "This batch has missing or incomplete data."
            )
        
        # Check if batch is still processing
        if batch.status not in ["completed"]:
            raise HTTPException(
                status_code=400,
                detail=f"Batch {batch.id} is not completed (status: {batch.status}). "
                       "Please wait for processing to finish."
            )
        
        # Verify KPI results exist
        if not batch.kpi_results:
            raise HTTPException(
                status_code=400,
                detail=f"Batch {batch.id} has no KPI results. Cannot proceed with operations."
            )
        
        return {
            "valid": True,
            "batch_id": batch.id,
            "status": batch.status,
            "has_kpis": bool(batch.kpi_results),
            "has_sufficiency": bool(batch.sufficiency_result)
        }
    
    @staticmethod
    def filter_valid_batches(batches: List[Batch]) -> List[Batch]:
        """
        Filter list to only include valid, completed batches.
        Used for compare/trends/forecast operations.
        """
        valid_batches = []
        for batch in batches:
            if batch.is_invalid == 0 and batch.status == "completed" and batch.kpi_results:
                valid_batches.append(batch)
        return valid_batches
    
    @staticmethod
    def validate_kpi_value(value: Any, field_name: str) -> Any:
        """
        Validate KPI value - return None if invalid, never dummy values.
        
        RULES:
        - No hardcoded values
        - No fallback values
        - No random values
        - If data is missing, return None
        """
        # None is acceptable - means missing data
        if value is None:
            return None
        
        # Empty string is treated as None
        if isinstance(value, str) and value.strip() == "":
            return None
        
        # NaN values are treated as None
        if isinstance(value, float):
            import math
            if math.isnan(value) or math.isinf(value):
                logger.warning(f"Invalid float value for {field_name}: {value}")
                return None
        
        # Validate numeric values are reasonable
        if isinstance(value, (int, float)):
            # Scores should be 0-100
            if "score" in field_name.lower():
                if value < 0 or value > 100:
                    logger.warning(f"Score {field_name} out of range: {value}")
                    return None
        
        return value
    
    @staticmethod
    def ensure_no_dummy_data(data: Dict[str, Any], context: str) -> Dict[str, Any]:
        """
        Scan data dict and remove any potential dummy/placeholder values.
        Returns cleaned data.
        """
        if data is None:
            return None
        
        cleaned = {}
        for key, value in data.items():
            # Skip obvious dummy values
            if value in ["N/A", "TBD", "TODO", "PLACEHOLDER", "DUMMY", "TEST"]:
                logger.warning(f"Removed dummy value for {key} in {context}")
                cleaned[key] = None
            else:
                cleaned[key] = ProductionGuard.validate_kpi_value(value, key)
        
        return cleaned
    
    # ============ NBA-SPECIFIC VALIDATION ============
    
    @staticmethod
    def validate_nba_batch_for_operations(
        batch: "Batch",
        nba_meta: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate NBA batch before analytics operations.
        
        NBA-specific rules:
        - Renewal batches MUST have ATR
        - Attainment targets MUST be defined with evidence
        - CO definitions MUST exist
        - Mappings MUST exist
        
        Returns validation result or raises HTTPException.
        """
        from fastapi import HTTPException
        
        reasons = []
        
        # Check if batch is invalid
        if batch.is_invalid == 1:
            raise HTTPException(
                status_code=400,
                detail="NBA batch is invalid and cannot be used for operations."
            )
        
        # Check renewal + ATR
        if nba_meta.get('is_renewal') and not nba_meta.get('has_atr'):
            reasons.append("ATR missing for renewal batch")
        
        # Check required data
        if not nba_meta.get('has_courses'):
            reasons.append("No courses defined")
        
        if not nba_meta.get('has_co_definitions'):
            reasons.append("No CO definitions uploaded")
        
        if not nba_meta.get('has_mappings'):
            reasons.append("CO-PO/PSO mappings not uploaded")
        
        if not nba_meta.get('has_student_data'):
            reasons.append("Student performance data not uploaded")
        
        if not nba_meta.get('has_targets'):
            reasons.append("Attainment targets not defined")
        
        if reasons:
            raise HTTPException(
                status_code=400,
                detail=f"NBA batch validation failed: {', '.join(reasons)}"
            )
        
        return {
            "valid": True,
            "batch_id": batch.id,
            "mode": "nba",
            "is_renewal": nba_meta.get('is_renewal', False)
        }
    
    @staticmethod
    def mark_nba_batch_invalid_if_needed(
        batch: "Batch",
        nba_meta: Dict[str, Any],
        db: "Session"
    ) -> bool:
        """
        Mark NBA batch as invalid if it fails requirements.
        
        Returns True if marked invalid.
        """
        reasons = []
        
        # Renewal without ATR
        if nba_meta.get('is_renewal') and not nba_meta.get('has_atr'):
            reasons.append("ATR missing for renewal")
        
        # Missing required uploads
        if not nba_meta.get('has_courses'):
            reasons.append("no courses")
        if not nba_meta.get('has_co_definitions'):
            reasons.append("no CO definitions")
        if not nba_meta.get('has_mappings'):
            reasons.append("no mappings")
        if not nba_meta.get('has_targets'):
            reasons.append("no attainment targets")
        
        if reasons:
            batch.is_invalid = 1
            logger.warning(f"NBA Batch {batch.id} marked INVALID: {', '.join(reasons)}")
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def validate_nba_evidence(
        evidence_doc_id: Optional[str],
        context: str
    ) -> bool:
        """
        Validate that evidence exists for an NBA calculation.
        
        STRICT: No evidence = No calculation
        Returns False if evidence is missing.
        """
        if not evidence_doc_id:
            logger.warning(f"NBA evidence check failed for {context}: No evidence document")
            return False
        return True
    
    @staticmethod
    def validate_nba_attainment_data(
        value: Any,
        field_name: str,
        evidence_doc_id: Optional[str] = None
    ) -> Optional[float]:
        """
        Validate NBA attainment value.
        
        RULES:
        - Must have evidence (if evidence_doc_id provided, it must not be None)
        - Must be a valid number
        - No dummy values
        - Returns None for missing/invalid data
        """
        # Check evidence if required
        if evidence_doc_id is None:
            logger.warning(f"NBA attainment {field_name}: No evidence, returning NULL")
            return None
        
        # None is acceptable
        if value is None:
            return None
        
        # Empty string
        if isinstance(value, str) and value.strip() == "":
            return None
        
        # Invalid float
        if isinstance(value, float):
            import math
            if math.isnan(value) or math.isinf(value):
                logger.warning(f"NBA invalid float for {field_name}: {value}")
                return None
        
        # Convert to float if possible
        try:
            float_val = float(value)
            # Attainment should be 0-100
            if float_val < 0 or float_val > 100:
                logger.warning(f"NBA attainment {field_name} out of range: {float_val}")
                return None
            return float_val
        except (TypeError, ValueError):
            logger.warning(f"NBA cannot convert {field_name} to float: {value}")
            return None


# Export singleton-style usage
production_guard = ProductionGuard()

