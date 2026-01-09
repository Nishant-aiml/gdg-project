"""
NIRF Calculation Engine
Implements 5 Parameters (TLR, RP, GO, OI, PR) as per NIRF Framework

STRICT RULES:
- PR computed ONLY if perception survey uploaded
- Evidence required for every parameter
- No estimated values
- No cross-mode data reuse
"""

from typing import Optional, Dict, List, Tuple, Any
from sqlalchemy.orm import Session
import json
import logging

logger = logging.getLogger(__name__)


# Official NIRF Parameter Weights
NIRF_WEIGHTS = {
    "TLR": 100,  # Teaching, Learning and Resources
    "RP": 100,   # Research and Professional Practice
    "GO": 100,   # Graduation Outcomes
    "OI": 100,   # Outreach and Inclusivity
    "PR": 100,   # Perception
}

TOTAL_WEIGHT = 500  # Sum of all weights (excluding PR if not available)
TOTAL_WEIGHT_NO_PR = 400  # If PR not available


class NIRFCalculationEngine:
    """
    NIRF Calculation Engine
    
    Implements:
    1. Parameter-wise scoring (TLR, RP, GO, OI, PR)
    2. Sub-parameter calculations
    3. Overall score calculation
    4. Evidence validation
    
    CRITICAL: PR (Perception) is ONLY computed if perception survey uploaded.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============ EVIDENCE VALIDATION ============
    
    def validate_evidence(self, evidence_doc_id: Optional[str], param_id: str) -> bool:
        """
        Validate evidence exists for a parameter.
        Returns False if no evidence → calculation blocked.
        """
        if not evidence_doc_id:
            logger.warning(f"NIRF {param_id}: No evidence document")
            return False
        return True
    
    # ============ TLR CALCULATION ============
    
    def calculate_tlr(
        self,
        student_strength: Optional[int],
        faculty_count: Optional[int],
        phd_faculty: Optional[int],
        financial_resources: Optional[float],
        evidence_doc_ids: List[str]
    ) -> Tuple[Optional[float], Dict, str]:
        """
        Calculate TLR (Teaching, Learning and Resources) score.
        
        Sub-parameters:
        - SS: Student Strength (20%)
        - FSR: Faculty-Student Ratio (30%)
        - FQE: Faculty Qualification (20%)
        - FRU: Financial Resources (30%)
        
        Returns:
            (score, sub_scores, status)
        """
        if not evidence_doc_ids:
            return None, {}, "No evidence provided"
        
        sub_scores = {}
        
        # SS: Student Strength
        if student_strength is not None and student_strength > 0:
            # Normalized based on NIRF benchmarks
            ss_score = min(100, (student_strength / 3000) * 100)
            sub_scores['SS'] = round(ss_score, 2)
        
        # FSR: Faculty-Student Ratio
        if faculty_count and student_strength:
            ratio = faculty_count / student_strength
            # AICTE norm: 1:20 ideal
            fsr_score = min(100, (ratio / 0.05) * 100)
            sub_scores['FSR'] = round(fsr_score, 2)
        
        # FQE: Faculty Qualification
        if phd_faculty is not None and faculty_count:
            phd_ratio = phd_faculty / faculty_count
            fqe_score = min(100, phd_ratio * 100)
            sub_scores['FQE'] = round(fqe_score, 2)
        
        # FRU: Financial Resources (in Crores)
        if financial_resources is not None:
            fru_score = min(100, (financial_resources / 50) * 100)
            sub_scores['FRU'] = round(fru_score, 2)
        
        if not sub_scores:
            return None, {}, "Insufficient TLR data"
        
        # Weighted average (equal weights for simplicity)
        weights = {'SS': 20, 'FSR': 30, 'FQE': 20, 'FRU': 30}
        total = sum(sub_scores.get(k, 0) * weights[k] for k in weights)
        total_weight = sum(weights[k] for k in sub_scores.keys())
        
        if total_weight == 0:
            return None, sub_scores, "No valid sub-scores"
        
        score = total / total_weight
        return round(score, 2), sub_scores, "Computed"
    
    # ============ RP CALCULATION ============
    
    def calculate_rp(
        self,
        publications: Optional[int],
        citations: Optional[int],
        patents: Optional[int],
        funded_projects: Optional[float],
        evidence_doc_ids: List[str]
    ) -> Tuple[Optional[float], Dict, str]:
        """
        Calculate RP (Research and Professional Practice) score.
        
        Sub-parameters:
        - PU: Publications (35%)
        - QP: Quality of Publications (35%)
        - IPR: Patents & IPR (15%)
        - FPPP: Funded Projects (15%)
        """
        if not evidence_doc_ids:
            return None, {}, "No evidence provided"
        
        sub_scores = {}
        
        # PU: Publications
        if publications is not None:
            pu_score = min(100, (publications / 500) * 100)
            sub_scores['PU'] = round(pu_score, 2)
        
        # QP: Quality (citations per paper)
        if citations is not None and publications:
            cpp = citations / publications
            qp_score = min(100, (cpp / 10) * 100)
            sub_scores['QP'] = round(qp_score, 2)
        
        # IPR: Patents
        if patents is not None:
            ipr_score = min(100, (patents / 50) * 100)
            sub_scores['IPR'] = round(ipr_score, 2)
        
        # FPPP: Funded projects (in Crores)
        if funded_projects is not None:
            fppp_score = min(100, (funded_projects / 20) * 100)
            sub_scores['FPPP'] = round(fppp_score, 2)
        
        if not sub_scores:
            return None, {}, "Insufficient RP data"
        
        weights = {'PU': 35, 'QP': 35, 'IPR': 15, 'FPPP': 15}
        total = sum(sub_scores.get(k, 0) * weights[k] for k in weights)
        total_weight = sum(weights[k] for k in sub_scores.keys())
        
        if total_weight == 0:
            return None, sub_scores, "No valid sub-scores"
        
        score = total / total_weight
        return round(score, 2), sub_scores, "Computed"
    
    # ============ GO CALCULATION ============
    
    def calculate_go(
        self,
        placed_students: Optional[int],
        total_graduates: Optional[int],
        median_salary: Optional[float],
        higher_studies: Optional[int],
        evidence_doc_ids: List[str]
    ) -> Tuple[Optional[float], Dict, str]:
        """
        Calculate GO (Graduation Outcomes) score.
        
        Sub-parameters:
        - GPH: Higher Studies (40%)
        - MS: Median Salary (25%)
        - Placement Rate (35%)
        """
        if not evidence_doc_ids:
            return None, {}, "No evidence provided"
        
        sub_scores = {}
        
        # Placement Rate
        if placed_students is not None and total_graduates:
            placement_rate = (placed_students / total_graduates) * 100
            sub_scores['Placement'] = round(min(100, placement_rate), 2)
        
        # GPH: Higher Studies
        if higher_studies is not None and total_graduates:
            hs_rate = (higher_studies / total_graduates) * 100
            sub_scores['GPH'] = round(min(100, hs_rate * 2), 2)  # Normalized
        
        # MS: Median Salary (in LPA)
        if median_salary is not None:
            ms_score = min(100, (median_salary / 15) * 100)
            sub_scores['MS'] = round(ms_score, 2)
        
        if not sub_scores:
            return None, {}, "Insufficient GO data"
        
        weights = {'Placement': 35, 'GPH': 40, 'MS': 25}
        total = sum(sub_scores.get(k, 0) * weights.get(k, 0) for k in sub_scores)
        total_weight = sum(weights.get(k, 0) for k in sub_scores.keys())
        
        if total_weight == 0:
            return None, sub_scores, "No valid sub-scores"
        
        score = total / total_weight
        return round(score, 2), sub_scores, "Computed"
    
    # ============ OI CALCULATION ============
    
    def calculate_oi(
        self,
        women_students: Optional[int],
        total_students: Optional[int],
        economically_challenged: Optional[int],
        regional_diversity: Optional[float],
        evidence_doc_ids: List[str]
    ) -> Tuple[Optional[float], Dict, str]:
        """
        Calculate OI (Outreach and Inclusivity) score.
        
        Sub-parameters:
        - RD: Regional Diversity (30%)
        - WD: Women Diversity (30%)
        - ESCS: Economically/Socially Challenged (20%)
        - Facilities (20%)
        """
        if not evidence_doc_ids:
            return None, {}, "No evidence provided"
        
        sub_scores = {}
        
        # WD: Women Diversity
        if women_students is not None and total_students:
            wd_ratio = (women_students / total_students) * 100
            sub_scores['WD'] = round(min(100, wd_ratio * 2), 2)
        
        # ESCS: Economically/Socially Challenged
        if economically_challenged is not None and total_students:
            escs_ratio = (economically_challenged / total_students) * 100
            sub_scores['ESCS'] = round(min(100, escs_ratio * 2), 2)
        
        # RD: Regional Diversity
        if regional_diversity is not None:
            sub_scores['RD'] = round(min(100, regional_diversity), 2)
        
        if not sub_scores:
            return None, {}, "Insufficient OI data"
        
        weights = {'RD': 30, 'WD': 30, 'ESCS': 20}
        total = sum(sub_scores.get(k, 0) * weights.get(k, 0) for k in sub_scores)
        total_weight = sum(weights.get(k, 0) for k in sub_scores.keys())
        
        if total_weight == 0:
            return None, sub_scores, "No valid sub-scores"
        
        score = total / total_weight
        return round(score, 2), sub_scores, "Computed"
    
    # ============ PR CALCULATION (CRITICAL) ============
    
    def calculate_pr(
        self,
        has_perception_survey: bool,
        perception_data: Optional[Dict],
        evidence_doc_ids: List[str]
    ) -> Tuple[Optional[float], Dict, str]:
        """
        Calculate PR (Perception) score.
        
        CRITICAL RULE:
        PR is ONLY computed if perception survey is uploaded.
        Otherwise → NULL (never inferred from other data).
        """
        # STRICT: No survey = NULL
        if not has_perception_survey:
            logger.warning("NIRF PR: No perception survey uploaded → NULL")
            return None, {}, "Perception survey not uploaded"
        
        if not evidence_doc_ids:
            return None, {}, "No evidence provided"
        
        if not perception_data:
            return None, {}, "No perception data"
        
        sub_scores = {}
        
        # Extract perception survey scores
        peer_perception = perception_data.get('peer_perception')
        employer_perception = perception_data.get('employer_perception')
        academic_perception = perception_data.get('academic_perception')
        
        if peer_perception is not None:
            sub_scores['Peer'] = round(peer_perception, 2)
        if employer_perception is not None:
            sub_scores['Employer'] = round(employer_perception, 2)
        if academic_perception is not None:
            sub_scores['Academic'] = round(academic_perception, 2)
        
        if not sub_scores:
            return None, {}, "Insufficient perception data"
        
        # Average perception scores
        score = sum(sub_scores.values()) / len(sub_scores)
        return round(score, 2), sub_scores, "Computed"
    
    # ============ OVERALL SCORE ============
    
    def calculate_overall_score(
        self,
        param_scores: Dict[str, Optional[float]]
    ) -> Tuple[Optional[float], str, List[str]]:
        """
        Calculate overall NIRF ranking score.
        
        Formula:
        Score = (TLR + RP + GO + OI + PR) / 5
        
        If PR missing: Score = (TLR + RP + GO + OI) / 4
        
        Returns:
            (score, formula_used, missing_params)
        """
        missing = []
        available_params = {}
        
        # Check required params (TLR, RP, GO, OI)
        for p_id in ["TLR", "RP", "GO", "OI"]:
            if param_scores.get(p_id) is None:
                missing.append(p_id)
            else:
                available_params[p_id] = param_scores[p_id]
        
        # PR is optional (but noted if missing)
        if param_scores.get("PR") is None:
            missing.append("PR (Perception Survey)")
        else:
            available_params["PR"] = param_scores["PR"]
        
        # Need at least TLR, RP, GO, OI
        required_missing = [p for p in missing if p in ["TLR", "RP", "GO", "OI"]]
        if required_missing:
            logger.warning(f"NIRF overall blocked: Missing {required_missing}")
            return None, f"Missing required parameters: {', '.join(required_missing)}", missing
        
        # Calculate average
        total = sum(available_params.values())
        count = len(available_params)
        score = total / count
        
        # Build formula
        parts = [f"{p}={v}" for p, v in sorted(available_params.items())]
        formula = f"Score = ({' + '.join([str(v) for v in available_params.values()])}) / {count} = {round(score, 2)}"
        
        return round(score, 2), formula, missing
    
    # ============ BATCH VALIDATION ============
    
    def validate_nirf_batch(
        self,
        batch_id: str,
        nirf_meta: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate NIRF batch for minimum data requirements.
        """
        # Check at least TLR and GO (most important)
        if not nirf_meta.get('has_tlr_data'):
            return False, "TLR data not uploaded"
        
        if not nirf_meta.get('has_go_data'):
            return False, "Graduation Outcomes data not uploaded"
        
        return True, None


# ============ UTILITY FUNCTIONS ============

def get_nirf_parameter_info() -> List[Dict]:
    """Get list of NIRF parameters with weights."""
    return [
        {"id": "TLR", "name": "Teaching, Learning and Resources", "weight": 100},
        {"id": "RP", "name": "Research and Professional Practice", "weight": 100},
        {"id": "GO", "name": "Graduation Outcomes", "weight": 100},
        {"id": "OI", "name": "Outreach and Inclusivity", "weight": 100},
        {"id": "PR", "name": "Perception", "weight": 100, "note": "Requires perception survey"},
    ]
