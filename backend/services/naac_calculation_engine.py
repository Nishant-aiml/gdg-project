"""
NAAC Calculation Engine
Implements 7 Criteria (C1-C7) as per NAAC Handbook

STRICT RULES:
- Missing criterion → NULL overall
- Evidence required for every criterion
- No estimated values
- No cross-mode data reuse
"""

from typing import Optional, Dict, List, Tuple, Any
from sqlalchemy.orm import Session
import json
import logging

logger = logging.getLogger(__name__)


# Official NAAC Criterion Weights (Total = 1000)
NAAC_WEIGHTS = {
    "C1": 150,  # Curricular Aspects
    "C2": 200,  # Teaching-Learning and Evaluation
    "C3": 250,  # Research, Innovations and Extension
    "C4": 100,  # Infrastructure and Learning Resources
    "C5": 100,  # Student Support and Progression
    "C6": 100,  # Governance, Leadership and Management
    "C7": 100,  # Institutional Values and Best Practices
}

TOTAL_WEIGHT = sum(NAAC_WEIGHTS.values())  # 1000


class NAACCalculationEngine:
    """
    NAAC Calculation Engine
    
    Implements:
    1. Criterion-wise scoring (C1-C7)
    2. Weighted CGPA calculation
    3. Grade assignment
    4. Evidence validation
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============ EVIDENCE VALIDATION ============
    
    def validate_evidence(self, evidence_doc_id: Optional[str], criterion_id: str) -> bool:
        """
        Validate evidence exists for a criterion.
        Returns False if no evidence → calculation blocked.
        """
        if not evidence_doc_id:
            logger.warning(f"NAAC {criterion_id}: No evidence document")
            return False
        return True
    
    # ============ CRITERION SCORING ============
    
    def calculate_criterion_score(
        self,
        criterion_id: str,
        key_indicators: List[Dict],
        evidence_doc_ids: List[str]
    ) -> Tuple[Optional[float], str]:
        """
        Calculate score for a single criterion.
        
        Args:
            criterion_id: C1, C2, ..., C7
            key_indicators: List of {ki_id, score, max_score, weight}
            evidence_doc_ids: List of document IDs as evidence
        
        Returns:
            (score, status)
            score is NULL if insufficient data
        """
        # Check evidence
        if not evidence_doc_ids:
            return None, "No evidence provided"
        
        # Check key indicators
        if not key_indicators:
            return None, "No key indicator data"
        
        # Filter valid KIs (with scores)
        valid_kis = [ki for ki in key_indicators if ki.get('score') is not None]
        
        if not valid_kis:
            return None, "No valid key indicator scores"
        
        # Calculate weighted score
        total_weight = sum(ki.get('weight', 1) for ki in valid_kis)
        weighted_sum = sum(
            ki['score'] * ki.get('weight', 1) 
            for ki in valid_kis
        )
        
        if total_weight == 0:
            return None, "Total weight is zero"
        
        score = (weighted_sum / total_weight) * 4.0  # Convert to 4-point scale
        
        # Cap at 4.0
        score = min(4.0, max(0.0, score))
        
        return round(score, 2), "Computed"
    
    # ============ OVERALL CGPA ============
    
    def calculate_cgpa(
        self,
        criterion_scores: Dict[str, Optional[float]]
    ) -> Tuple[Optional[float], str, List[str]]:
        """
        Calculate overall NAAC CGPA from criterion scores.
        
        Formula:
        CGPA = Σ(Criterion_Score × Weight) / Σ(Weight)
        
        Returns:
            (cgpa, formula_used, missing_criteria)
            CGPA is NULL if ANY criterion is missing.
        """
        missing = []
        
        # Check all 7 criteria present
        for c_id in ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]:
            if criterion_scores.get(c_id) is None:
                missing.append(c_id)
        
        # STRICT: ANY missing criterion = NULL overall
        if missing:
            logger.warning(f"NAAC CGPA blocked: Missing criteria {missing}")
            return None, f"Missing criteria: {', '.join(missing)}", missing
        
        # Calculate weighted CGPA
        weighted_sum = 0.0
        for c_id, score in criterion_scores.items():
            weight = NAAC_WEIGHTS.get(c_id, 0)
            weighted_sum += score * weight
        
        cgpa = weighted_sum / TOTAL_WEIGHT
        
        # Build formula string
        formula_parts = [
            f"({criterion_scores[c]}×{NAAC_WEIGHTS[c]})" 
            for c in sorted(criterion_scores.keys())
        ]
        formula = f"CGPA = ({' + '.join(formula_parts)}) / {TOTAL_WEIGHT} = {round(cgpa, 2)}"
        
        return round(cgpa, 2), formula, []
    
    # ============ GRADE ASSIGNMENT ============
    
    def get_grade(self, cgpa: Optional[float]) -> str:
        """
        Assign NAAC grade based on CGPA.
        
        Grading Scale (NAAC):
        - 3.51 - 4.00: A++
        - 3.26 - 3.50: A+
        - 3.01 - 3.25: A
        - 2.76 - 3.00: B++
        - 2.51 - 2.75: B+
        - 2.01 - 2.50: B
        - 1.51 - 2.00: C
        - <= 1.50: D (Not Accredited)
        """
        if cgpa is None:
            return "Not Computed"
        
        if cgpa >= 3.51:
            return "A++"
        elif cgpa >= 3.26:
            return "A+"
        elif cgpa >= 3.01:
            return "A"
        elif cgpa >= 2.76:
            return "B++"
        elif cgpa >= 2.51:
            return "B+"
        elif cgpa >= 2.01:
            return "B"
        elif cgpa >= 1.51:
            return "C"
        else:
            return "D"
    
    def is_accredited(self, cgpa: Optional[float]) -> bool:
        """Check if CGPA qualifies for accreditation (>= 1.51)"""
        if cgpa is None:
            return False
        return cgpa >= 1.51
    
    # ============ BATCH VALIDATION ============
    
    def validate_naac_batch(
        self,
        batch_id: str,
        naac_meta: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate NAAC batch for completeness.
        
        Returns:
            (is_valid, invalid_reason)
        """
        # Check IQAC report (mandatory)
        if not naac_meta.get('has_iqac_report'):
            return False, "IQAC report not uploaded"
        
        # Check SSR (mandatory)
        if not naac_meta.get('has_ssr'):
            return False, "Self-Study Report (SSR) not uploaded"
        
        # Check at least some criteria present
        criteria_present = sum([
            naac_meta.get('has_c1', False),
            naac_meta.get('has_c2', False),
            naac_meta.get('has_c3', False),
            naac_meta.get('has_c4', False),
            naac_meta.get('has_c5', False),
            naac_meta.get('has_c6', False),
            naac_meta.get('has_c7', False),
        ])
        
        if criteria_present == 0:
            return False, "No criterion data uploaded"
        
        return True, None
    
    # ============ FULL EVALUATION ============
    
    def evaluate_batch(
        self,
        batch_id: str,
        criterion_data: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        Perform full NAAC evaluation for a batch.
        
        Args:
            batch_id: Batch identifier
            criterion_data: Dict of {C1: {...}, C2: {...}, ...}
        
        Returns:
            Complete evaluation result
        """
        results = {
            'batch_id': batch_id,
            'criteria': {},
            'cgpa': None,
            'grade': None,
            'is_accredited': False,
            'formula_used': None,
            'missing_criteria': [],
        }
        
        criterion_scores = {}
        
        # Calculate each criterion
        for c_id in ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]:
            c_data = criterion_data.get(c_id, {})
            
            score, status = self.calculate_criterion_score(
                c_id,
                c_data.get('key_indicators', []),
                c_data.get('evidence_doc_ids', [])
            )
            
            criterion_scores[c_id] = score
            
            results['criteria'][c_id] = {
                'criterion_id': c_id,
                'name': self._get_criterion_name(c_id),
                'score': score,
                'weight': NAAC_WEIGHTS[c_id],
                'status': status,
            }
        
        # Calculate CGPA
        cgpa, formula, missing = self.calculate_cgpa(criterion_scores)
        
        results['cgpa'] = cgpa
        results['grade'] = self.get_grade(cgpa)
        results['is_accredited'] = self.is_accredited(cgpa)
        results['formula_used'] = formula
        results['missing_criteria'] = missing
        
        return results
    
    def _get_criterion_name(self, c_id: str) -> str:
        """Get full name of a criterion."""
        names = {
            "C1": "Curricular Aspects",
            "C2": "Teaching-Learning and Evaluation",
            "C3": "Research, Innovations and Extension",
            "C4": "Infrastructure and Learning Resources",
            "C5": "Student Support and Progression",
            "C6": "Governance, Leadership and Management",
            "C7": "Institutional Values and Best Practices",
        }
        return names.get(c_id, c_id)


# ============ UTILITY FUNCTIONS ============

def get_naac_criterion_info() -> List[Dict]:
    """Get list of NAAC criteria with weights."""
    return [
        {"id": "C1", "name": "Curricular Aspects", "weight": 150},
        {"id": "C2", "name": "Teaching-Learning and Evaluation", "weight": 200},
        {"id": "C3", "name": "Research, Innovations and Extension", "weight": 250},
        {"id": "C4", "name": "Infrastructure and Learning Resources", "weight": 100},
        {"id": "C5", "name": "Student Support and Progression", "weight": 100},
        {"id": "C6", "name": "Governance, Leadership and Management", "weight": 100},
        {"id": "C7", "name": "Institutional Values and Best Practices", "weight": 100},
    ]
