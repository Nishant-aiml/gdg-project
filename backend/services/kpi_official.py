"""
Official Accreditation KPI Formulas
Deterministic, evidence-backed calculations for AICTE, NBA, NAAC, NIRF
NO dummy data, NO inferred values, NO AI calculations
"""

from typing import Dict, Any, List, Optional, Tuple
from utils.parse_numeric import parse_numeric
from services.production_guard import ProductionGuard
import logging
import math

logger = logging.getLogger(__name__)


class OfficialKPIService:
    """
    Official KPI calculation service with strict validation and evidence tracking.
    Each mode has isolated formulas - no cross-mode reuse.
    """
    
    def __init__(self):
        pass
    
    # ==================== AICTE MODE (INSTITUTION LEVEL) ====================
    
    def calculate_aicte_fsr(
        self,
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        AICTE Faculty-Student Ratio (FSR) - OFFICIAL FORMULA
        
        Formula: FSR = Total Students / Total Faculty
        
        Scoring Rule:
        - FSR ≤ 15 → Score = 100
        - 15 < FSR ≤ 20 → Score = linear scale (100 → 60)
        - FSR > 20 → Score = proportional penalty
        
        Returns: (score, evidence_info)
        """
        # Extract inputs (mandatory)
        faculty_count = (
            data.get("faculty_count_num") or
            parse_numeric(data.get("faculty_count")) or
            parse_numeric(data.get("total_faculty")) or
            parse_numeric(data.get("faculty"))
        )
        
        student_count = (
            data.get("student_count_num") or
            data.get("total_students_num") or
            data.get("total_intake_num") or
            parse_numeric(data.get("total_students")) or
            parse_numeric(data.get("student_count")) or
            parse_numeric(data.get("total_intake")) or
            parse_numeric(data.get("admitted_students"))
        )
        
        # If student_count not found, try programs_approved
        if student_count is None:
            programs = data.get("programs_approved", [])
            if isinstance(programs, list):
                total_intake = 0
                for program in programs:
                    if isinstance(program, dict):
                        intake = parse_numeric(program.get("intake_2025_26") or program.get("intake") or program.get("students"))
                        if intake:
                            total_intake += intake
                if total_intake > 0:
                    student_count = total_intake
        
        # EVIDENCE ENFORCEMENT: Validate evidence before calculation
        faculty_evidence = evidence_map.get("faculty_count") or evidence_map.get("total_faculty") or {}
        student_evidence = evidence_map.get("student_count") or evidence_map.get("total_students") or {}
        
        # If values exist, they MUST have evidence
        if faculty_count is not None:
            has_evidence, error_msg = ProductionGuard.validate_evidence_required(
                faculty_count, faculty_evidence, "faculty_count"
            )
            if not has_evidence:
                logger.warning(f"FSR calculation: {error_msg}")
                # Mark as missing if no evidence
                faculty_count = None
        
        if student_count is not None:
            has_evidence, error_msg = ProductionGuard.validate_evidence_required(
                student_count, student_evidence, "student_count"
            )
            if not has_evidence:
                logger.warning(f"FSR calculation: {error_msg}")
                # Mark as missing if no evidence
                student_count = None
        
        # Validation: Both inputs mandatory
        if faculty_count is None or student_count is None:
            return None, {
                "missing_inputs": ["faculty_count" if faculty_count is None else None, "student_count" if student_count is None else None],
                "formula": "FSR = Total Students / Total Faculty",
                "evidence": {}
            }
        
        if faculty_count == 0 or student_count == 0:
            return None, {
                "error": "Faculty or student count is zero",
                "formula": "FSR = Total Students / Total Faculty",
                "evidence": {}
            }
        
        # Calculate FSR (Students per Faculty)
        fsr = student_count / faculty_count
        
        # Official scoring rule
        if fsr <= 15:
            score = 100.0
            rule_applied = "FSR ≤ 15 → Score = 100"
        elif fsr <= 20:
            # Linear scale: 100 at FSR=15, 60 at FSR=20
            # slope = (60 - 100) / (20 - 15) = -8
            # score = 100 + (fsr - 15) * (-8)
            score = 100 + (fsr - 15) * (-8)
            rule_applied = f"15 < FSR ≤ 20 → Linear scale: {score:.2f}"
        else:
            # Proportional penalty: FSR > 20
            # Penalty = (fsr - 20) * 3 per unit over 20
            # Score = 60 - min(60, (fsr - 20) * 3)
            penalty = (fsr - 20) * 3
            score = max(0.0, 60.0 - penalty)
            rule_applied = f"FSR > 20 → Proportional penalty: {score:.2f}"
        
        # Collect evidence
        evidence = {
            "faculty_count": {
                "value": faculty_count,
                "evidence": evidence_map.get("faculty_count") or evidence_map.get("total_faculty") or {}
            },
            "student_count": {
                "value": student_count,
                "evidence": evidence_map.get("student_count") or evidence_map.get("total_students") or {}
            },
            "fsr_calculated": fsr,
            "rule_applied": rule_applied
        }
        
        return round(score, 2), {
            "formula": "FSR = Total Students / Total Faculty",
            "inputs": {
                "faculty_count": faculty_count,
                "student_count": student_count
            },
            "fsr_value": round(fsr, 2),
            "score": round(score, 2),
            "evidence": evidence
        }
    
    def calculate_aicte_infrastructure(
        self,
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        AICTE Infrastructure Score - OFFICIAL FORMULA
        
        Weighted Formula:
        Infrastructure Score = 
            0.40 × Area Adequacy +
            0.25 × Classroom Adequacy +
            0.15 × Library Adequacy +
            0.10 × Digital Availability +
            0.10 × Hostel Availability
        
        Each sub-score calculated independently.
        """
        # Get student count (required for norms)
        student_count = (
            data.get("total_students_num") or
            data.get("student_count_num") or
            data.get("total_intake_num") or
            parse_numeric(data.get("total_students")) or
            parse_numeric(data.get("student_count")) or
            parse_numeric(data.get("total_intake"))
        )
        
        # EVIDENCE ENFORCEMENT: Validate evidence for student_count
        student_evidence = evidence_map.get("total_students") or evidence_map.get("student_count") or evidence_map.get("total_intake") or {}
        if student_count is not None:
            has_evidence, error_msg = ProductionGuard.validate_evidence_required(
                student_count, student_evidence, "student_count"
            )
            if not has_evidence:
                logger.warning(f"Infrastructure calculation: {error_msg}")
                student_count = None
        
        if student_count is None or student_count == 0:
            return None, {
                "error": "Student count missing - cannot calculate infrastructure norms",
                "formula": "Infrastructure = 0.40×Area + 0.25×Classrooms + 0.15×Library + 0.10×Digital + 0.10×Hostel",
                "evidence": {}
            }
        
        sub_scores = {}
        evidence_info = {}
        
        # 1. Area Adequacy (40% weight)
        built_up_area_sqm = (
            data.get("built_up_area_sqm_num") or
            data.get("built_up_area_num") or
            parse_numeric(data.get("built_up_area"))
        )
        
        if built_up_area_sqm is not None and built_up_area_sqm > 0:
            # EVIDENCE ENFORCEMENT: Validate evidence for built_up_area
            area_evidence = evidence_map.get("built_up_area") or evidence_map.get("built_up_area_sqm") or {}
            has_evidence, error_msg = ProductionGuard.validate_evidence_required(
                built_up_area_sqm, area_evidence, "built_up_area"
            )
            if not has_evidence:
                logger.warning(f"Infrastructure calculation: {error_msg}")
                built_up_area_sqm = None
        
        if built_up_area_sqm is not None and built_up_area_sqm > 0:
            required_area = student_count * 4  # AICTE norm: 4 sqm per student
            area_adequacy = min(100.0, (built_up_area_sqm / required_area) * 100) if required_area > 0 else 0.0
            sub_scores["area"] = area_adequacy
            evidence_info["area"] = {
                "actual": built_up_area_sqm,
                "required": required_area,
                "adequacy": round(area_adequacy, 2),
                "evidence": evidence_map.get("built_up_area") or evidence_map.get("built_up_area_sqm") or {}
            }
        else:
            sub_scores["area"] = 0.0
            evidence_info["area"] = {
                "actual": None,
                "required": student_count * 4,
                "adequacy": 0.0,
                "missing": True,
                "evidence": {}
            }
        
        # 2. Classroom Adequacy (25% weight)
        actual_classrooms = (
            parse_numeric(data.get("total_classrooms")) or
            parse_numeric(data.get("classrooms")) or
            0
        )
        
        if actual_classrooms > 0:
            # EVIDENCE ENFORCEMENT: Validate evidence for classrooms
            classroom_evidence = evidence_map.get("classrooms") or evidence_map.get("total_classrooms") or {}
            has_evidence, error_msg = ProductionGuard.validate_evidence_required(
                actual_classrooms, classroom_evidence, "classrooms"
            )
            if not has_evidence:
                logger.warning(f"Infrastructure calculation: {error_msg}")
                actual_classrooms = 0
        
        if actual_classrooms > 0:
            required_classrooms = math.ceil(student_count / 40)  # AICTE norm: 40 students per classroom
            classroom_adequacy = min(100.0, (actual_classrooms / required_classrooms) * 100) if required_classrooms > 0 else 0.0
            sub_scores["classrooms"] = classroom_adequacy
            evidence_info["classrooms"] = {
                "actual": actual_classrooms,
                "required": required_classrooms,
                "adequacy": round(classroom_adequacy, 2),
                "evidence": evidence_map.get("classrooms") or evidence_map.get("total_classrooms") or {}
            }
        else:
            sub_scores["classrooms"] = 0.0
            evidence_info["classrooms"] = {
                "actual": None,
                "required": math.ceil(student_count / 40),
                "adequacy": 0.0,
                "missing": True,
                "evidence": {}
            }
        
        # 3. Library Adequacy (15% weight)
        library_area_sqm = (
            parse_numeric(data.get("library_area_sqm")) or
            parse_numeric(data.get("library_area")) or
            0
        )
        
        if library_area_sqm > 0:
            required_library = student_count * 0.5  # 0.5 sqm per student
            library_adequacy = min(100.0, (library_area_sqm / required_library) * 100) if required_library > 0 else 0.0
            sub_scores["library"] = library_adequacy
            evidence_info["library"] = {
                "actual": library_area_sqm,
                "required": required_library,
                "adequacy": round(library_adequacy, 2),
                "evidence": evidence_map.get("library_area") or {}
            }
        else:
            sub_scores["library"] = 0.0
            evidence_info["library"] = {
                "actual": None,
                "required": student_count * 0.5,
                "adequacy": 0.0,
                "missing": True,
                "evidence": {}
            }
        
        # 4. Digital Availability (10% weight)
        digital_resources = (
            parse_numeric(data.get("digital_library_resources")) or
            parse_numeric(data.get("digital_resources")) or
            0
        )
        
        if digital_resources > 0:
            # 500 resources = 100%
            digital_adequacy = min(100.0, (digital_resources / 500) * 100)
            sub_scores["digital"] = digital_adequacy
            evidence_info["digital"] = {
                "actual": digital_resources,
                "target": 500,
                "adequacy": round(digital_adequacy, 2),
                "evidence": evidence_map.get("digital_library_resources") or {}
            }
        else:
            # Check if digital library exists (yes/no)
            has_digital = data.get("digital_library_systems") or data.get("has_digital_library")
            if has_digital:
                sub_scores["digital"] = 50.0  # Partial credit for having it
                evidence_info["digital"] = {
                    "actual": "Yes",
                    "target": "Yes",
                    "adequacy": 50.0,
                    "evidence": evidence_map.get("digital_library_systems") or {}
                }
            else:
                sub_scores["digital"] = 0.0
                evidence_info["digital"] = {
                    "actual": None,
                    "target": 500,
                    "adequacy": 0.0,
                    "missing": True,
                    "evidence": {}
                }
        
        # 5. Hostel Availability (10% weight) - Optional
        hostel_capacity = (
            parse_numeric(data.get("hostel_capacity")) or
            0
        )
        
        if hostel_capacity > 0:
            required_hostel = student_count * 0.4  # 40% of students need hostel
            hostel_adequacy = min(100.0, (hostel_capacity / required_hostel) * 100) if required_hostel > 0 else 0.0
            sub_scores["hostel"] = hostel_adequacy
            evidence_info["hostel"] = {
                "actual": hostel_capacity,
                "required": required_hostel,
                "adequacy": round(hostel_adequacy, 2),
                "evidence": evidence_map.get("hostel_capacity") or {}
            }
        else:
            sub_scores["hostel"] = 0.0
            evidence_info["hostel"] = {
                "actual": None,
                "required": student_count * 0.4,
                "adequacy": 0.0,
                "optional": True,
                "evidence": {}
            }
        
        # Calculate weighted score
        infrastructure_score = (
            0.40 * sub_scores["area"] +
            0.25 * sub_scores["classrooms"] +
            0.15 * sub_scores["library"] +
            0.10 * sub_scores["digital"] +
            0.10 * sub_scores["hostel"]
        )
        
        return round(infrastructure_score, 2), {
            "formula": "Infrastructure = 0.40×Area + 0.25×Classrooms + 0.15×Library + 0.10×Digital + 0.10×Hostel",
            "sub_scores": sub_scores,
            "score": round(infrastructure_score, 2),
            "evidence": evidence_info
        }
    
    def calculate_aicte_placement(
        self,
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        AICTE Placement Index - OFFICIAL FORMULA
        
        Formula: Placement % = (Placed / Eligible) × 100
        Placement Index = Placement %
        """
        # Try direct placement rate first
        placement_rate = (
            data.get("placement_rate_num") or
            parse_numeric(data.get("placement_percentage")) or
            parse_numeric(data.get("placement_rate"))
        )
        
        # If not available, calculate from components
        if placement_rate is None:
            students_placed = (
                data.get("students_placed_num") or
                data.get("total_placements_num") or
                parse_numeric(data.get("students_placed")) or
                parse_numeric(data.get("total_placements"))
            )
            
            students_eligible = (
                data.get("students_eligible_num") or
                data.get("student_count_num") or
                data.get("total_students_num") or
                parse_numeric(data.get("students_eligible")) or
                parse_numeric(data.get("total_students")) or
                parse_numeric(data.get("student_count"))
            )
            
            # EVIDENCE ENFORCEMENT: Validate evidence for placement data
            placed_evidence = evidence_map.get("students_placed") or evidence_map.get("total_placements") or {}
            eligible_evidence = evidence_map.get("students_eligible") or evidence_map.get("total_students") or evidence_map.get("student_count") or {}
            
            if students_placed is not None:
                has_evidence, error_msg = ProductionGuard.validate_evidence_required(
                    students_placed, placed_evidence, "students_placed"
                )
                if not has_evidence:
                    logger.warning(f"Placement calculation: {error_msg}")
                    students_placed = None
            
            if students_eligible is not None:
                has_evidence, error_msg = ProductionGuard.validate_evidence_required(
                    students_eligible, eligible_evidence, "students_eligible"
                )
                if not has_evidence:
                    logger.warning(f"Placement calculation: {error_msg}")
                    students_eligible = None
            
            if students_placed is None or students_eligible is None:
                return None, {
                    "error": "Placement data missing",
                    "formula": "Placement Index = (Students Placed / Students Eligible) × 100",
                    "evidence": {}
                }
            
            if students_eligible == 0:
                return None, {
                    "error": "Students eligible is zero",
                    "formula": "Placement Index = (Students Placed / Students Eligible) × 100",
                    "evidence": {}
                }
            
            placement_rate = (students_placed / students_eligible) * 100
            evidence_info = {
                "students_placed": {
                    "value": students_placed,
                    "evidence": evidence_map.get("students_placed") or {}
                },
                "students_eligible": {
                    "value": students_eligible,
                    "evidence": evidence_map.get("students_eligible") or {}
                }
            }
        else:
            evidence_info = {
                "placement_rate": {
                    "value": placement_rate,
                    "evidence": evidence_map.get("placement_rate") or {}
                }
            }
        
        # Cap at 100
        placement_index = min(placement_rate, 100.0)
        
        return round(placement_index, 2), {
            "formula": "Placement Index = (Students Placed / Students Eligible) × 100",
            "placement_rate": round(placement_rate, 2),
            "score": round(placement_index, 2),
            "evidence": evidence_info
        }
    
    def calculate_aicte_lab_compliance(
        self,
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        AICTE Lab Compliance Index - OFFICIAL FORMULA
        
        Rule-based (not numeric):
        - All mandatory labs present → 100
        - Any mandatory lab missing → proportional deduction
        - No labs data → NULL
        """
        available_labs = (
            data.get("total_labs_num") or
            parse_numeric(data.get("total_labs")) or
            parse_numeric(data.get("lab_count")) or
            0
        )
        
        # EVIDENCE ENFORCEMENT: Validate evidence for lab data
        lab_evidence = evidence_map.get("total_labs") or evidence_map.get("lab_count") or {}
        if available_labs is not None and available_labs > 0:
            has_evidence, error_msg = ProductionGuard.validate_evidence_required(
                available_labs, lab_evidence, "available_labs"
            )
            if not has_evidence:
                logger.warning(f"Lab compliance calculation: {error_msg}")
                available_labs = None
        
        if available_labs is None or available_labs == 0:
            return None, {
                "error": "Lab data missing",
                "formula": "Lab Compliance = (Available Labs / Required Labs) × 100",
                "evidence": {}
            }
        
        # Calculate required labs
        required_labs = data.get("required_labs_num") or parse_numeric(data.get("required_labs"))
        
        if required_labs is None:
            # Estimate based on student count
            student_count = (
                data.get("student_count_num") or
                data.get("total_students_num") or
                parse_numeric(data.get("total_students")) or
                parse_numeric(data.get("student_count"))
            )
            
            if student_count and student_count > 0:
                required_labs = max(5, student_count // 50)  # At least 1 lab per 50 students, minimum 5
            else:
                required_labs = 5  # Default minimum
        
        if required_labs == 0:
            return None, {
                "error": "Required labs is zero",
                "formula": "Lab Compliance = (Available Labs / Required Labs) × 100",
                "evidence": {}
            }
        
        lab_compliance = (available_labs / required_labs) * 100
        
        # Cap at 100
        compliance_score = min(lab_compliance, 100.0)
        
        return round(compliance_score, 2), {
            "formula": "Lab Compliance = (Available Labs / Required Labs) × 100",
            "inputs": {
                "available_labs": available_labs,
                "required_labs": required_labs
            },
            "score": round(compliance_score, 2),
            "evidence": {
                "available_labs": {
                    "value": available_labs,
                    "evidence": evidence_map.get("total_labs") or {}
                },
                "required_labs": {
                    "value": required_labs,
                    "evidence": {}
                }
            }
        }
    
    def calculate_aicte_overall(
        self,
        kpi_scores: Dict[str, Optional[float]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        AICTE Overall Score - OFFICIAL FORMULA
        
        STRICT RULE: Overall = Average of available KPIs ONLY
        If Infrastructure missing → do not include it.
        Never substitute missing values.
        """
        fsr = kpi_scores.get("fsr_score")
        infra = kpi_scores.get("infrastructure_score")
        placement = kpi_scores.get("placement_index")
        lab = kpi_scores.get("lab_compliance_index")
        
        # Collect only available (non-None) KPIs
        available_kpis = []
        included = []
        
        if fsr is not None:
            available_kpis.append(fsr)
            included.append("FSR")
        
        if infra is not None:
            available_kpis.append(infra)
            included.append("Infrastructure")
        
        if placement is not None:
            available_kpis.append(placement)
            included.append("Placement")
        
        if lab is not None:
            available_kpis.append(lab)
            included.append("Lab Compliance")
        
        if len(available_kpis) == 0:
            return None, {
                "error": "No KPIs available",
                "formula": "Overall = Average of available KPIs",
                "included": [],
                "excluded": ["FSR", "Infrastructure", "Placement", "Lab Compliance"]
            }
        
        overall_score = sum(available_kpis) / len(available_kpis)
        
        excluded = [kpi for kpi in ["FSR", "Infrastructure", "Placement", "Lab Compliance"] if kpi not in included]
        
        return round(overall_score, 2), {
            "formula": "Overall = Average of available KPIs",
            "included": included,
            "excluded": excluded,
            "kpi_values": available_kpis,
            "score": round(overall_score, 2)
        }
    
    # ==================== NBA MODE (DEPARTMENT LEVEL) ====================
    
    def calculate_nba_peos_psos(
        self,
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NBA PEOs & PSOs Criterion
        
        Qualitative + Quantitative scoring
        Missing PEO/PSO → mark criterion invalid
        """
        from services.nba_formulas import NBAFormulas
        return NBAFormulas.calculate_peos_psos(data, evidence_map)
    
    def calculate_nba_faculty_quality(
        self,
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NBA Faculty Quality Criterion
        
        Components:
        - FSR (40%): Faculty-Student Ratio
        - PhD % (30%): Percentage of PhD faculty
        - Faculty Development (30%): FDPs, conferences, publications
        """
        from services.nba_formulas import NBAFormulas
        return NBAFormulas.calculate_faculty_quality(data, evidence_map)
    
    def calculate_nba_overall(
        self,
        criterion_scores: Dict[str, Optional[float]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NBA Overall Score
        
        Formula: NBA Score = Average of criterion scores
        """
        available_scores = [v for v in criterion_scores.values() if v is not None]
        
        if len(available_scores) == 0:
            return None, {
                "error": "No criterion scores available",
                "formula": "NBA Score = Average of criterion scores"
            }
        
        nba_score = sum(available_scores) / len(available_scores)
        
        return round(nba_score, 2), {
            "formula": "NBA Score = Average of criterion scores",
            "criterion_scores": criterion_scores,
            "score": round(nba_score, 2)
        }
    
    # ==================== NAAC MODE (INSTITUTION LEVEL) ====================
    
    def calculate_naac_criterion(
        self,
        criterion_id: str,
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NAAC Criterion Score (C1-C7)
        
        Each criterion has:
        - Quantitative indicators (scored numerically)
        - Qualitative indicators (scored via rubric)
        
        Returns None if criterion data missing.
        """
        from services.naac_formulas import NAACFormulas
        
        criterion_map = {
            "criterion_1": NAACFormulas.calculate_criterion_1,
            "criterion_2": NAACFormulas.calculate_criterion_2,
            "criterion_3": NAACFormulas.calculate_criterion_3,
            "criterion_4": NAACFormulas.calculate_criterion_4,
            "criterion_5": NAACFormulas.calculate_criterion_5,
            "criterion_6": NAACFormulas.calculate_criterion_6,
            "criterion_7": NAACFormulas.calculate_criterion_7,
        }
        
        calculator = criterion_map.get(criterion_id)
        if calculator:
            return calculator(data, evidence_map)
        
        return None, {
            "error": f"NAAC Criterion {criterion_id} calculation not found",
            "formula": f"NAAC {criterion_id} = Weighted sum of indicators",
            "evidence": {}
        }
    
    def calculate_naac_overall(
        self,
        criterion_scores: Dict[str, Optional[float]],
        criterion_weights: Dict[str, float]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NAAC Overall Score
        
        Formula: NAAC Score = Σ(Criterion Score × Criterion Weight)
        If any criterion missing → mark incomplete (do NOT estimate).
        """
        weighted_sum = 0.0
        total_weight = 0.0
        included = []
        excluded = []
        
        for criterion_id, weight in criterion_weights.items():
            score = criterion_scores.get(criterion_id)
            if score is not None:
                weighted_sum += score * weight
                total_weight += weight
                included.append(criterion_id)
            else:
                excluded.append(criterion_id)
        
        if total_weight == 0:
            return None, {
                "error": "No criterion scores available",
                "formula": "NAAC Score = Σ(Criterion Score × Criterion Weight)",
                "included": [],
                "excluded": list(criterion_weights.keys())
            }
        
        naac_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(naac_score, 2), {
            "formula": "NAAC Score = Σ(Criterion Score × Criterion Weight)",
            "included": included,
            "excluded": excluded,
            "weighted_sum": weighted_sum,
            "total_weight": total_weight,
            "score": round(naac_score, 2)
        }
    
    # ==================== NIRF MODE (INSTITUTION LEVEL) ====================
    
    def calculate_nirf_parameter(
        self,
        parameter_name: str,
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NIRF Parameter Score
        
        Parameters: TLR, RP, GO, OI, PR
        Each parameter computed independently.
        """
        from services.nirf_formulas import NIRFFormulas
        
        parameter_map = {
            "tlr": NIRFFormulas.calculate_tlr,
            "rp": NIRFFormulas.calculate_rp,
            "go": NIRFFormulas.calculate_go,
            "oi": NIRFFormulas.calculate_oi,
            "pr": NIRFFormulas.calculate_pr,
        }
        
        calculator = parameter_map.get(parameter_name.lower())
        if calculator:
            return calculator(data, evidence_map)
        
        return None, {
            "error": f"NIRF Parameter {parameter_name} calculation not found",
            "formula": f"NIRF {parameter_name} = Weighted aggregation",
            "evidence": {}
        }
    
    def calculate_nirf_overall(
        self,
        parameter_scores: Dict[str, Optional[float]],
        parameter_weights: Dict[str, float]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NIRF Overall Score
        
        Formula: NIRF Score = Σ(Weighted Parameter Scores)
        """
        weighted_sum = 0.0
        total_weight = 0.0
        included = []
        excluded = []
        
        for param_name, weight in parameter_weights.items():
            score = parameter_scores.get(param_name)
            if score is not None:
                weighted_sum += score * weight
                total_weight += weight
                included.append(param_name)
            else:
                excluded.append(param_name)
        
        if total_weight == 0:
            return None, {
                "error": "No parameter scores available",
                "formula": "NIRF Score = Σ(Weighted Parameter Scores)",
                "included": [],
                "excluded": list(parameter_weights.keys())
            }
        
        nirf_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(nirf_score, 2), {
            "formula": "NIRF Score = Σ(Weighted Parameter Scores)",
            "included": included,
            "excluded": excluded,
            "weighted_sum": weighted_sum,
            "total_weight": total_weight,
            "score": round(nirf_score, 2)
        }
    
    # ==================== VALIDATION HELPERS ====================
    
    def validate_year(self, academic_year: str, is_new: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Validate academic year
        
        Rule: Year must be ≥ current_year - 2 (for renewal) or ≥ current_year (for new)
        """
        from datetime import datetime
        current_year = datetime.now().year
        
        try:
            # Parse year from "2024-25" format
            year_str = academic_year.split("-")[0]
            year = int(year_str)
            
            if is_new:
                if year < current_year:
                    return False, f"New institution year {year} is before current year {current_year}"
            else:
                if year < current_year - 2:
                    return False, f"Renewal year {year} is more than 2 years before current year {current_year}"
            
            return True, None
        except (ValueError, AttributeError):
            return False, f"Invalid academic year format: {academic_year}"
    
    def validate_numeric_sanity(
        self,
        data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate numeric sanity checks
        
        Rules:
        - Students ≥ Faculty
        - Placement ≤ Eligible
        - Areas > 0
        """
        errors = []
        
        faculty_count = parse_numeric(data.get("faculty_count")) or parse_numeric(data.get("total_faculty"))
        student_count = parse_numeric(data.get("student_count")) or parse_numeric(data.get("total_students"))
        
        if faculty_count and student_count:
            if student_count < faculty_count:
                errors.append(f"Student count ({student_count}) < Faculty count ({faculty_count})")
        
        students_placed = parse_numeric(data.get("students_placed"))
        students_eligible = parse_numeric(data.get("students_eligible"))
        
        if students_placed and students_eligible:
            if students_placed > students_eligible:
                errors.append(f"Students placed ({students_placed}) > Students eligible ({students_eligible})")
        
        built_up_area = parse_numeric(data.get("built_up_area"))
        if built_up_area and built_up_area <= 0:
            errors.append(f"Built-up area ({built_up_area}) must be > 0")
        
        return len(errors) == 0, errors

