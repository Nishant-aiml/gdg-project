"""
NBA (National Board of Accreditation) Official Formulas
Department-level accreditation scoring with 5 criteria
"""

from typing import Dict, Any, Optional, Tuple
from utils.parse_numeric import parse_numeric
import logging

logger = logging.getLogger(__name__)

# Import ProductionGuard for evidence validation
from services.production_guard import ProductionGuard


class NBAFormulas:
    """
    NBA accreditation formulas - Department level
    5 Criteria: PEOs & PSOs, Faculty Quality, Student Performance, Continuous Improvement, CO-PO Mapping
    """
    
    @staticmethod
    def calculate_peos_psos(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NBA PEOs & PSOs Criterion
        
        Components:
        - PEOs Definition (50%)
        - PSOs Definition (50%)
        
        Missing PEO/PSO → mark criterion invalid
        """
        peos = data.get("peos") or data.get("program_educational_objectives")
        psos = data.get("psos") or data.get("program_specific_outcomes")
        
        score_components = []
        evidence_info = {}
        
        # Component 1: PEOs Definition (50%)
        if peos:
            # Check if PEOs are well-defined
            if isinstance(peos, list) and len(peos) >= 3:
                peos_score = 100.0
            elif isinstance(peos, str) and len(peos) > 100:
                peos_score = 100.0
            elif isinstance(peos, dict) and len(peos) > 0:
                peos_score = 100.0
            else:
                peos_score = 50.0  # Partial credit
            
            score_components.append(("peos", peos_score, 0.50))
            evidence_info["peos"] = {
                "present": True,
                "score": peos_score,
                "evidence": evidence_map.get("peos") or {}
            }
        
        # Component 2: PSOs Definition (50%)
        if psos:
            # Check if PSOs are well-defined
            if isinstance(psos, list) and len(psos) >= 3:
                psos_score = 100.0
            elif isinstance(psos, str) and len(psos) > 100:
                psos_score = 100.0
            elif isinstance(psos, dict) and len(psos) > 0:
                psos_score = 100.0
            else:
                psos_score = 50.0  # Partial credit
            
            score_components.append(("psos", psos_score, 0.50))
            evidence_info["psos"] = {
                "present": True,
                "score": psos_score,
                "evidence": evidence_map.get("psos") or {}
            }
        
        if len(score_components) == 0:
            return None, {
                "error": "PEOs and PSOs missing",
                "formula": "PEOs & PSOs = 0.50×PEOs + 0.50×PSOs",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "PEOs & PSOs = 0.50×PEOs + 0.50×PSOs",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }
    
    @staticmethod
    def calculate_faculty_quality(
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
        faculty_count = parse_numeric(data.get("faculty_count")) or parse_numeric(data.get("total_faculty"))
        student_count = parse_numeric(data.get("student_count")) or parse_numeric(data.get("total_students"))
        phd_faculty = parse_numeric(data.get("phd_faculty")) or parse_numeric(data.get("phd_faculty_count"))
        faculty_development = parse_numeric(data.get("faculty_development_activities")) or parse_numeric(data.get("fdp_count"))
        
        score_components = []
        evidence_info = {}
        
        # Component 1: FSR (40%)
        if faculty_count and student_count and faculty_count > 0:
            fsr = student_count / faculty_count
            if fsr <= 15:
                fsr_score = 100.0
            elif fsr <= 20:
                fsr_score = 80.0
            elif fsr <= 25:
                fsr_score = 60.0
            else:
                fsr_score = max(0.0, 60.0 - (fsr - 25) * 2)
            
            score_components.append(("fsr", fsr_score, 0.40))
            evidence_info["fsr"] = {
                "value": round(fsr, 2),
                "score": fsr_score,
                "evidence": evidence_map.get("faculty_count") or {}
            }
        
        # Component 2: PhD % (30%)
        if phd_faculty is not None and faculty_count and faculty_count > 0:
            phd_percentage = (phd_faculty / faculty_count) * 100
            # 60% PhD = 100
            phd_score = min(100.0, (phd_percentage / 60) * 100)
            score_components.append(("phd_percentage", phd_score, 0.30))
            evidence_info["phd_percentage"] = {
                "value": round(phd_percentage, 2),
                "score": phd_score,
                "evidence": evidence_map.get("phd_faculty") or {}
            }
        
        # Component 3: Faculty Development (30%)
        if faculty_development is not None:
            # 10 activities = 100
            dev_score = min(100.0, (faculty_development / 10) * 100)
            score_components.append(("faculty_development", dev_score, 0.30))
            evidence_info["faculty_development"] = {
                "value": faculty_development,
                "score": dev_score,
                "evidence": evidence_map.get("faculty_development_activities") or {}
            }
        
        if len(score_components) == 0:
            return None, {
                "error": "Faculty Quality data missing",
                "formula": "Faculty Quality = 0.40×FSR + 0.30×PhD% + 0.30×Faculty Development",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "Faculty Quality = 0.40×FSR + 0.30×PhD% + 0.30×Faculty Development",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }
    
    @staticmethod
    def calculate_student_performance(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NBA Student Performance Criterion
        
        Components:
        - Placement Rate (40%)
        - Pass Percentage (30%)
        - Higher Studies (30%)
        """
        placement_rate = parse_numeric(data.get("placement_rate")) or parse_numeric(data.get("placement_percentage"))
        pass_percentage = parse_numeric(data.get("pass_percentage")) or parse_numeric(data.get("pass_rate"))
        higher_studies = parse_numeric(data.get("higher_studies_count")) or parse_numeric(data.get("students_higher_studies"))
        
        score_components = []
        evidence_info = {}
        
        # Component 1: Placement Rate (40%)
        if placement_rate is not None:
            placement_score = min(100.0, placement_rate)
            score_components.append(("placement_rate", placement_score, 0.40))
            evidence_info["placement_rate"] = {
                "value": placement_rate,
                "score": placement_score,
                "evidence": evidence_map.get("placement_rate") or {}
            }
        
        # Component 2: Pass Percentage (30%)
        if pass_percentage is not None:
            pass_score = min(100.0, pass_percentage)
            score_components.append(("pass_percentage", pass_score, 0.30))
            evidence_info["pass_percentage"] = {
                "value": pass_percentage,
                "score": pass_score,
                "evidence": evidence_map.get("pass_percentage") or {}
            }
        
        # Component 3: Higher Studies (30%)
        if higher_studies is not None:
            total_students = parse_numeric(data.get("total_students")) or parse_numeric(data.get("student_count"))
            if total_students and total_students > 0:
                higher_studies_pct = (higher_studies / total_students) * 100
                higher_studies_score = min(100.0, higher_studies_pct)
                score_components.append(("higher_studies", higher_studies_score, 0.30))
                evidence_info["higher_studies"] = {
                    "value": higher_studies,
                    "percentage": round(higher_studies_pct, 2),
                    "score": higher_studies_score,
                    "evidence": evidence_map.get("higher_studies_count") or {}
                }
        
        if len(score_components) == 0:
            return None, {
                "error": "Student Performance data missing",
                "formula": "Student Performance = 0.40×Placement + 0.30×Pass% + 0.30×Higher Studies",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "Student Performance = 0.40×Placement + 0.30×Pass% + 0.30×Higher Studies",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }
    
    @staticmethod
    def calculate_continuous_improvement(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NBA Continuous Improvement Criterion
        
        Components:
        - Action Plan (50%)
        - Feedback Implementation (50%)
        """
        action_plan = data.get("action_plan") or data.get("quality_action_plan")
        feedback_implementation = data.get("feedback_implementation") or data.get("feedback_action_taken")
        
        score_components = []
        evidence_info = {}
        
        # Component 1: Action Plan (50%)
        if action_plan:
            if isinstance(action_plan, (dict, list)) and len(action_plan) > 0:
                action_score = 100.0
            elif isinstance(action_plan, str) and len(action_plan) > 100:
                action_score = 100.0
            else:
                action_score = 50.0
            
            score_components.append(("action_plan", action_score, 0.50))
            evidence_info["action_plan"] = {
                "present": True,
                "score": action_score,
                "evidence": evidence_map.get("action_plan") or {}
            }
        
        # Component 2: Feedback Implementation (50%)
        if feedback_implementation:
            if isinstance(feedback_implementation, (dict, list)) and len(feedback_implementation) > 0:
                feedback_score = 100.0
            elif isinstance(feedback_implementation, str) and len(feedback_implementation) > 100:
                feedback_score = 100.0
            else:
                feedback_score = 50.0
            
            score_components.append(("feedback_implementation", feedback_score, 0.50))
            evidence_info["feedback_implementation"] = {
                "present": True,
                "score": feedback_score,
                "evidence": evidence_map.get("feedback_implementation") or {}
            }
        
        if len(score_components) == 0:
            return None, {
                "error": "Continuous Improvement data missing",
                "formula": "Continuous Improvement = 0.50×Action Plan + 0.50×Feedback Implementation",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "Continuous Improvement = 0.50×Action Plan + 0.50×Feedback Implementation",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }
    
    @staticmethod
    def calculate_co_po_mapping(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NBA CO-PO Mapping Criterion
        
        Critical for NBA - missing CO-PO mapping → major penalty
        """
        co_po_mapping = data.get("co_po_mapping") or data.get("course_outcome_program_outcome_mapping")
        
        if not co_po_mapping:
            return None, {
                "error": "CO-PO mapping missing - major penalty",
                "formula": "CO-PO Mapping = Assessment of mapping quality",
                "evidence": {}
            }
        
        # Check if mapping is well-defined
        if isinstance(co_po_mapping, dict) and len(co_po_mapping) > 0:
            score = 100.0
        elif isinstance(co_po_mapping, str) and len(co_po_mapping) > 100:
            score = 100.0
        elif isinstance(co_po_mapping, list) and len(co_po_mapping) > 0:
            score = 100.0
        else:
            score = 50.0  # Partial credit
        
        return round(score, 2), {
            "formula": "CO-PO Mapping = Assessment of mapping quality",
            "score": round(score, 2),
            "evidence": {
                "co_po_mapping": {
                    "present": True,
                    "evidence": evidence_map.get("co_po_mapping") or {}
                }
            }
        }
