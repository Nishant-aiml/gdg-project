"""
NBA Calculation Engine
Implements official NBA OBE formulas with strict evidence validation

RULES:
- No dummy/fallback values
- Missing data → NULL (never 0)
- Every calculation MUST be evidence-backed
- Invalid batches excluded from analytics
"""

from typing import Optional, Dict, List, Tuple, Any
from sqlalchemy.orm import Session
import json
import logging

logger = logging.getLogger(__name__)


class NBACalculationEngine:
    """
    NBA OBE Calculation Engine
    
    Implements:
    1. CO Attainment (threshold-based, per course)
    2. PO/PSO Attainment (weighted from CO)
    3. Direct + Indirect combination (80/20)
    4. Qualitative status mapping
    5. Evidence validation
    """
    
    # Default thresholds for status (configurable)
    ATTAINMENT_THRESHOLDS = {
        'attained': 70.0,
        'partially_attained': 50.0,
    }
    
    # Default weights for direct/indirect combination
    DEFAULT_DIRECT_WEIGHT = 0.8
    DEFAULT_INDIRECT_WEIGHT = 0.2
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============ EVIDENCE VALIDATION ============
    
    def validate_evidence(self, evidence_doc_id: Optional[str]) -> bool:
        """
        Check if evidence exists for a calculation.
        Returns False if no evidence → prevents calculation.
        """
        if not evidence_doc_id:
            return False
        # Could add additional validation (check doc exists in DB)
        return True
    
    # ============ CO ATTAINMENT ============
    
    def calculate_co_attainment(
        self,
        total_students: Optional[int],
        students_above_threshold: Optional[int],
        evidence_doc_id: Optional[str] = None
    ) -> Optional[float]:
        """
        Calculate CO Attainment percentage.
        
        Formula: CO_Attainment = (students_above_threshold / total_students) × 100
        
        Returns NULL if:
        - total_students is None or 0
        - students_above_threshold is None
        - No evidence provided
        
        STRICT: Never returns 0 as fallback.
        """
        # Evidence check
        if not self.validate_evidence(evidence_doc_id):
            logger.warning("CO attainment calculation blocked: No evidence")
            return None
        
        # Data validation
        if total_students is None or total_students == 0:
            logger.warning("CO attainment calculation blocked: No student data")
            return None
        
        if students_above_threshold is None:
            logger.warning("CO attainment calculation blocked: No threshold data")
            return None
        
        # Calculate
        attainment = (students_above_threshold / total_students) * 100
        return round(attainment, 2)
    
    # ============ PO/PSO ATTAINMENT (DIRECT) ============
    
    def calculate_direct_po_attainment(
        self,
        co_attainments: List[Dict],
        mappings: List[Dict]
    ) -> Tuple[Optional[float], str, List[Dict]]:
        """
        Calculate PO/PSO Attainment from CO data (Direct Assessment).
        
        Formula:
        PO_Attainment = Σ(CO_Attainment × Mapping_Level) / Σ(Mapping_Level)
        
        Args:
            co_attainments: List of {co_id, attainment_percent, evidence_doc_id}
            mappings: List of {co_id, mapping_level (1,2,3)}
        
        Returns:
            (attainment_value, formula_used, contributing_cos)
            Returns (None, ..., ...) if insufficient data
        """
        # Build lookup for CO attainments
        co_lookup = {}
        for co in co_attainments:
            if co.get('attainment_percent') is not None:
                co_lookup[co['co_id']] = co
        
        # Filter mappings to only those with valid CO attainment
        valid_mappings = []
        for mapping in mappings:
            co_id = mapping['co_id']
            if co_id in co_lookup:
                valid_mappings.append({
                    'co_id': co_id,
                    'mapping_level': mapping['mapping_level'],
                    'attainment': co_lookup[co_id]['attainment_percent'],
                    'course_name': co_lookup[co_id].get('course_name', 'Unknown'),
                    'evidence_doc_id': co_lookup[co_id].get('evidence_doc_id'),
                })
        
        # Check if we have any valid data
        if not valid_mappings:
            logger.warning("PO attainment blocked: No valid CO mappings with attainment data")
            return None, "Insufficient data: No valid CO mappings", []
        
        # Calculate weighted sum
        numerator = 0.0
        denominator = 0.0
        contributing_cos = []
        
        for m in valid_mappings:
            weight = m['mapping_level']
            attainment = m['attainment']
            
            numerator += attainment * weight
            denominator += weight
            
            contributing_cos.append({
                'co_id': m['co_id'],
                'course_name': m['course_name'],
                'attainment': attainment,
                'mapping_level': weight,
                'weighted_contribution': round(attainment * weight, 2),
            })
        
        if denominator == 0:
            return None, "Insufficient data: Sum of mapping levels is 0", contributing_cos
        
        # Calculate final attainment
        po_attainment = numerator / denominator
        
        # Build formula string for transparency
        formula = f"Direct_PO = Σ(CO × Level) / Σ(Level) = {round(numerator, 2)} / {round(denominator, 2)} = {round(po_attainment, 2)}"
        
        return round(po_attainment, 2), formula, contributing_cos
    
    # ============ INDIRECT ASSESSMENT ============
    
    def calculate_indirect_po_attainment(
        self,
        indirect_data: List[Dict]
    ) -> Optional[float]:
        """
        Calculate PO attainment from indirect assessment data.
        
        Sources:
        - Alumni surveys
        - Employer feedback
        - Exit surveys
        
        Returns NULL if no indirect data available.
        """
        if not indirect_data:
            return None
        
        # Filter valid scores
        valid_scores = [d['score'] for d in indirect_data if d.get('score') is not None]
        
        if not valid_scores:
            return None
        
        # Average indirect scores
        avg_indirect = sum(valid_scores) / len(valid_scores)
        return round(avg_indirect, 2)
    
    # ============ FINAL PO ATTAINMENT (COMBINED) ============
    
    def calculate_final_po_attainment(
        self,
        direct_attainment: Optional[float],
        indirect_attainment: Optional[float],
        direct_weight: float = None,
        indirect_weight: float = None
    ) -> Tuple[Optional[float], str]:
        """
        Calculate final PO attainment by combining direct and indirect.
        
        Formula:
        Final_PO = (Direct × Direct_Weight) + (Indirect × Indirect_Weight)
        
        Default: 80% Direct + 20% Indirect
        
        Returns:
            (final_attainment, formula_used)
        """
        direct_weight = direct_weight or self.DEFAULT_DIRECT_WEIGHT
        indirect_weight = indirect_weight or self.DEFAULT_INDIRECT_WEIGHT
        
        # Handle missing data
        if direct_attainment is None and indirect_attainment is None:
            return None, "Insufficient Evidence: No direct or indirect data"
        
        # If only direct available
        if direct_attainment is not None and indirect_attainment is None:
            formula = f"Final = Direct only = {direct_attainment} (No indirect data)"
            return direct_attainment, formula
        
        # If only indirect available
        if direct_attainment is None and indirect_attainment is not None:
            formula = f"Final = Indirect only = {indirect_attainment} (No direct data)"
            return indirect_attainment, formula
        
        # Both available - weighted combination
        final = (direct_attainment * direct_weight) + (indirect_attainment * indirect_weight)
        formula = (
            f"Final = ({direct_attainment} × {direct_weight}) + "
            f"({indirect_attainment} × {indirect_weight}) = {round(final, 2)}"
        )
        
        return round(final, 2), formula
    
    # ============ ATTAINMENT STATUS ============
    
    def get_attainment_status(
        self,
        value: Optional[float],
        thresholds: Dict[str, float] = None
    ) -> str:
        """
        Get qualitative attainment status.
        
        Status levels:
        - "Attained" (≥ 70%)
        - "Partially Attained" (≥ 50%)
        - "Not Attained" (< 50%)
        - "Insufficient Evidence" (NULL)
        """
        if value is None:
            return "Insufficient Evidence"
        
        thresholds = thresholds or self.ATTAINMENT_THRESHOLDS
        
        if value >= thresholds['attained']:
            return "Attained"
        elif value >= thresholds['partially_attained']:
            return "Partially Attained"
        else:
            return "Not Attained"
    
    # ============ BATCH-LEVEL CALCULATIONS ============
    
    def calculate_all_po_attainments(
        self,
        batch_id: str,
        nba_meta: Dict
    ) -> Dict[str, Any]:
        """
        Calculate all PO attainments for a batch.
        
        Returns dict with PO1-PO12 results including:
        - direct_attainment
        - indirect_attainment
        - final_attainment
        - status
        - formula_used
        - contributing_cos
        """
        from models.nba_models import NBA_PROGRAM_OUTCOMES
        
        results = {}
        
        # Get weights from batch meta
        direct_weight = nba_meta.get('direct_weight', self.DEFAULT_DIRECT_WEIGHT)
        indirect_weight = nba_meta.get('indirect_weight', self.DEFAULT_INDIRECT_WEIGHT)
        
        for po_id, po_name in NBA_PROGRAM_OUTCOMES.items():
            # Get CO attainments mapped to this PO
            co_attainments = self._get_co_attainments_for_po(batch_id, po_id)
            mappings = self._get_mappings_for_po(batch_id, po_id)
            
            # Calculate direct
            direct, formula, contributing = self.calculate_direct_po_attainment(
                co_attainments, mappings
            )
            
            # Get indirect
            indirect_data = self._get_indirect_for_po(batch_id, po_id)
            indirect = self.calculate_indirect_po_attainment(indirect_data)
            
            # Calculate final
            final, final_formula = self.calculate_final_po_attainment(
                direct, indirect, direct_weight, indirect_weight
            )
            
            # Get status
            status = self.get_attainment_status(final)
            
            results[po_id] = {
                'po_id': po_id,
                'po_name': po_name,
                'direct_attainment': direct,
                'indirect_attainment': indirect,
                'final_attainment': final,
                'status': status,
                'formula_used': final_formula,
                'contributing_cos': contributing,
            }
        
        return results
    
    # ============ HELPER METHODS (DB QUERIES) ============
    
    def _get_co_attainments_for_po(self, batch_id: str, po_id: str) -> List[Dict]:
        """Get all CO attainments that map to a specific PO."""
        # This would query the database
        # Placeholder - implement based on actual DB models
        return []
    
    def _get_mappings_for_po(self, batch_id: str, po_id: str) -> List[Dict]:
        """Get all CO-PO mappings for a specific PO."""
        return []
    
    def _get_indirect_for_po(self, batch_id: str, po_id: str) -> List[Dict]:
        """Get indirect assessment data for a specific PO."""
        return []
    
    # ============ VALIDATION ============
    
    def validate_nba_batch(self, batch_id: str, nba_meta: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate NBA batch for completeness.
        
        Returns:
            (is_valid, invalid_reason)
            
        Invalid reasons:
        - "ATR missing for renewal"
        - "Targets not defined"
        - "No courses defined"
        - "No CO definitions"
        - "No mappings"
        - "No student data"
        """
        # Check renewal + ATR
        if nba_meta.get('is_renewal') and not nba_meta.get('has_atr'):
            return False, "ATR missing for renewal batch"
        
        # Check required data
        if not nba_meta.get('has_courses'):
            return False, "No courses defined"
        
        if not nba_meta.get('has_co_definitions'):
            return False, "No CO definitions uploaded"
        
        if not nba_meta.get('has_mappings'):
            return False, "CO-PO/PSO mappings not uploaded"
        
        if not nba_meta.get('has_student_data'):
            return False, "Student performance data not uploaded"
        
        if not nba_meta.get('has_targets'):
            return False, "Attainment targets not defined"
        
        return True, None


# ============ UTILITY FUNCTIONS ============

def get_required_nba_uploads() -> List[Dict]:
    """
    Get list of required NBA uploads with step order.
    Used for frontend wizard.
    """
    return [
        {
            'step': 1,
            'name': 'Course List',
            'key': 'course_list',
            'required': True,
            'description': 'List of courses with code, name, semester, credits',
        },
        {
            'step': 2,
            'name': 'CO Definitions',
            'key': 'co_definitions',
            'required': True,
            'description': 'Course Outcome statements for each course',
        },
        {
            'step': 3,
            'name': 'CO-PO/PSO Mapping Tables',
            'key': 'mapping_tables',
            'required': True,
            'description': 'Mapping of COs to POs (1-12) and PSOs with strength (1,2,3)',
        },
        {
            'step': 4,
            'name': 'Student Performance Data',
            'key': 'student_data',
            'required': True,
            'description': 'Student marks per CO for attainment calculation',
        },
        {
            'step': 5,
            'name': 'Attainment Targets',
            'key': 'targets',
            'required': True,
            'description': 'Approved attainment threshold percentage with evidence',
        },
        {
            'step': 6,
            'name': 'ATR & Improvement Actions',
            'key': 'atr',
            'required': False,  # Required for renewal only
            'required_for_renewal': True,
            'description': 'Action Taken Report with improvement actions',
        },
        {
            'step': 7,
            'name': 'Indirect Assessment',
            'key': 'indirect',
            'required': False,
            'description': 'Alumni surveys, employer feedback, exit surveys',
        },
    ]
