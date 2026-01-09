"""
Production Hardening Guards
Enforces strict data integrity rules:
- No dummy data
- Evidence required for all calculations
- Invalid batches excluded
- Department-wise governance
"""

from typing import Dict, Any, Optional, Tuple, List
from config.database import Batch
import logging

logger = logging.getLogger(__name__)


class ProductionGuard:
    """
    Production hardening guard service.
    Enforces strict rules before allowing operations.
    """
    
    @staticmethod
    def validate_batch_for_operations(batch: Batch) -> Tuple[bool, Optional[str]]:
        """
        Validate batch is suitable for operations (comparison, trends, forecast).
        
        Rules:
        - overall_score must not be 0 or None
        - sufficiency must not be 0
        - is_invalid must be 0 (valid)
        - Must have at least 1 document
        
        Returns: (is_valid, error_message)
        """
        if batch.is_invalid == 1:
            return False, "Batch is marked as invalid"
        
        # Check overall score
        if batch.overall_score is None or batch.overall_score == 0:
            return False, "Overall score is 0 or missing - batch marked invalid"
        
        # Check sufficiency
        if hasattr(batch, 'sufficiency') and batch.sufficiency is not None:
            if batch.sufficiency == 0:
                return False, "Sufficiency is 0% - batch marked invalid"
        
        # Check document count
        if hasattr(batch, 'total_documents') and batch.total_documents is not None:
            if batch.total_documents < 1:
                return False, "No documents uploaded"
        
        return True, None
    
    @staticmethod
    def validate_evidence_required(
        value: Any,
        evidence: Dict[str, Any],
        field_name: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that a value has evidence before using it in calculations.
        
        Args:
            value: The value to validate
            evidence: Evidence dict (from evidence_map)
            field_name: Name of the field for error messages
        
        Returns: (has_evidence, error_message)
        """
        # If value is None, no evidence needed
        if value is None:
            return True, None
        
        # If value exists, evidence must exist
        if not evidence:
            return False, f"Value for {field_name} exists but has no evidence"
        
        # Evidence must have at least snippet or source_doc
        if not evidence.get("snippet") and not evidence.get("source_doc"):
            return False, f"Evidence for {field_name} is incomplete (missing snippet and source)"
        
        return True, None
    
    @staticmethod
    def enforce_department_consistency(
        batch: Batch,
        required_department: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Enforce department-wise governance rules.
        
        Rules:
        - Batch must have exactly one department
        - If required_department provided, must match
        - Prevents cross-department operations
        
        Returns: (is_valid, error_message)
        """
        if not batch.department_name:
            return False, "Batch must have a department_name"
        
        if required_department and batch.department_name != required_department:
            return False, f"Department mismatch: batch has {batch.department_name}, required {required_department}"
        
        return True, None
    
    @staticmethod
    def validate_trends_data_contract(
        batches: List[Batch],
        institution_name: str,
        department_name: Optional[str] = None
    ) -> Tuple[bool, Optional[str], List[Batch]]:
        """
        Validate trends/forecast data contract.
        
        Rules:
        - Same institution
        - Same department (if provided)
        - Minimum 3 distinct academic years
        - Strict academic_year ordering
        
        Returns: (is_valid, error_message, valid_batches)
        """
        valid_batches = []
        years_seen = set()
        
        for batch in batches:
            # Skip invalid batches
            if batch.is_invalid == 1:
                continue
            
            # Check institution match
            if batch.institution_name != institution_name:
                continue
            
            # Check department match (if required)
            if department_name and batch.department_name != department_name:
                continue
            
            # Check overall score
            if batch.overall_score is None or batch.overall_score == 0:
                continue
            
            # Check academic year
            if not batch.academic_year:
                continue
            
            valid_batches.append(batch)
            years_seen.add(batch.academic_year)
        
        # Must have at least 3 distinct years
        if len(years_seen) < 3:
            return False, f"Insufficient data: need 3+ distinct years, found {len(years_seen)}", []
        
        # Sort by academic year
        valid_batches.sort(key=lambda b: b.academic_year or "")
        
        return True, None, valid_batches
    
    @staticmethod
    def mark_batch_invalid_if_needed(batch: Batch) -> bool:
        """
        Mark batch as invalid if it violates production rules.
        
        Rules:
        - overall_score == 0 or None → invalid
        - sufficiency == 0 → invalid
        - No valid blocks → invalid
        
        Returns: True if batch was marked invalid
        """
        was_invalid = batch.is_invalid == 1
        
        # Check overall score
        if batch.overall_score is None or batch.overall_score == 0:
            batch.is_invalid = 1
            logger.warning(f"Batch {batch.id} marked invalid: overall_score is {batch.overall_score}")
            return not was_invalid
        
        # Check sufficiency
        if hasattr(batch, 'sufficiency') and batch.sufficiency is not None:
            if batch.sufficiency == 0:
                batch.is_invalid = 1
                logger.warning(f"Batch {batch.id} marked invalid: sufficiency is 0%")
                return not was_invalid
        
        return False

