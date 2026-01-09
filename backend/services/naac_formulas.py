"""
NAAC (National Assessment and Accreditation Council) Official Formulas
Institution-level accreditation scoring with 7 criteria
"""

from typing import Dict, Any, Optional, Tuple
from utils.parse_numeric import parse_numeric
import logging

logger = logging.getLogger(__name__)


class NAACFormulas:
    """
    NAAC accreditation formulas - Institution level
    7 Criteria (C1-C7) with weighted scoring
    """
    
    @staticmethod
    def calculate_criterion_1(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NAAC Criterion 1: Curricular Aspects
        
        Components:
        - Curriculum Design (40%)
        - Curriculum Implementation (30%)
        - Academic Flexibility (30%)
        """
        # Simplified scoring - would need detailed NAAC rubric
        curriculum_design = data.get("curriculum_design") or data.get("curriculum_planning")
        curriculum_implementation = data.get("curriculum_implementation") or data.get("syllabus_implementation")
        academic_flexibility = data.get("academic_flexibility") or data.get("elective_courses")
        
        score_components = []
        evidence_info = {}
        
        # Component 1: Curriculum Design (40%)
        if curriculum_design:
            design_score = 100.0 if isinstance(curriculum_design, (dict, list)) and len(curriculum_design) > 0 else 50.0
            score_components.append(("curriculum_design", design_score, 0.40))
            evidence_info["curriculum_design"] = {
                "present": True,
                "score": design_score,
                "evidence": evidence_map.get("curriculum_design") or {}
            }
        
        # Component 2: Curriculum Implementation (30%)
        if curriculum_implementation:
            impl_score = 100.0 if isinstance(curriculum_implementation, (dict, list)) and len(curriculum_implementation) > 0 else 50.0
            score_components.append(("curriculum_implementation", impl_score, 0.30))
            evidence_info["curriculum_implementation"] = {
                "present": True,
                "score": impl_score,
                "evidence": evidence_map.get("curriculum_implementation") or {}
            }
        
        # Component 3: Academic Flexibility (30%)
        if academic_flexibility:
            flexibility_score = 100.0 if isinstance(academic_flexibility, (dict, list)) and len(academic_flexibility) > 0 else 50.0
            score_components.append(("academic_flexibility", flexibility_score, 0.30))
            evidence_info["academic_flexibility"] = {
                "present": True,
                "score": flexibility_score,
                "evidence": evidence_map.get("academic_flexibility") or {}
            }
        
        if len(score_components) == 0:
            return None, {
                "error": "Criterion 1 (Curricular Aspects) data missing",
                "formula": "C1 = 0.40×Curriculum Design + 0.30×Implementation + 0.30×Flexibility",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "C1 = 0.40×Curriculum Design + 0.30×Implementation + 0.30×Flexibility",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }
    
    @staticmethod
    def calculate_criterion_2(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NAAC Criterion 2: Teaching-Learning & Evaluation
        
        Components:
        - Student Enrolment (30%)
        - Teaching-Learning Process (40%)
        - Evaluation Process (30%)
        """
        student_enrolment = parse_numeric(data.get("student_enrolment")) or parse_numeric(data.get("total_students"))
        teaching_learning = data.get("teaching_learning_process") or data.get("pedagogy")
        evaluation_process = data.get("evaluation_process") or data.get("assessment_methods")
        
        score_components = []
        evidence_info = {}
        
        # Component 1: Student Enrolment (30%)
        if student_enrolment and student_enrolment > 0:
            # Normalize: 1000 students = 100
            enrolment_score = min(100.0, (student_enrolment / 1000) * 100)
            score_components.append(("student_enrolment", enrolment_score, 0.30))
            evidence_info["student_enrolment"] = {
                "value": student_enrolment,
                "score": enrolment_score,
                "evidence": evidence_map.get("student_enrolment") or {}
            }
        
        # Component 2: Teaching-Learning Process (40%)
        if teaching_learning:
            tl_score = 100.0 if isinstance(teaching_learning, (dict, list)) and len(teaching_learning) > 0 else 50.0
            score_components.append(("teaching_learning", tl_score, 0.40))
            evidence_info["teaching_learning"] = {
                "present": True,
                "score": tl_score,
                "evidence": evidence_map.get("teaching_learning_process") or {}
            }
        
        # Component 3: Evaluation Process (30%)
        if evaluation_process:
            eval_score = 100.0 if isinstance(evaluation_process, (dict, list)) and len(evaluation_process) > 0 else 50.0
            score_components.append(("evaluation_process", eval_score, 0.30))
            evidence_info["evaluation_process"] = {
                "present": True,
                "score": eval_score,
                "evidence": evidence_map.get("evaluation_process") or {}
            }
        
        if len(score_components) == 0:
            return None, {
                "error": "Criterion 2 (Teaching-Learning & Evaluation) data missing",
                "formula": "C2 = 0.30×Enrolment + 0.40×Teaching-Learning + 0.30×Evaluation",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "C2 = 0.30×Enrolment + 0.40×Teaching-Learning + 0.30×Evaluation",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }
    
    @staticmethod
    def calculate_criterion_3(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NAAC Criterion 3: Research, Innovations & Extension
        
        Components:
        - Research Publications (40%)
        - Research Projects (30%)
        - Extension Activities (30%)
        """
        # NO FALLBACK VALUES - Missing data must return None
        publications = parse_numeric(data.get("research_publications")) or parse_numeric(data.get("publications"))
        research_projects = parse_numeric(data.get("research_projects")) or parse_numeric(data.get("funded_projects"))
        extension_activities = parse_numeric(data.get("extension_activities")) or parse_numeric(data.get("community_services"))
        
        score_components = []
        evidence_info = {}
        
        # Component 1: Research Publications (40%)
        if publications is not None and publications > 0:
            # 50 publications = 100
            pub_score = min(100.0, (publications / 50) * 100)
            score_components.append(("publications", pub_score, 0.40))
            evidence_info["publications"] = {
                "value": publications,
                "score": pub_score,
                "evidence": evidence_map.get("research_publications") or {}
            }
        
        # Component 2: Research Projects (30%)
        if research_projects is not None and research_projects > 0:
            # 10 projects = 100
            proj_score = min(100.0, (research_projects / 10) * 100)
            score_components.append(("research_projects", proj_score, 0.30))
            evidence_info["research_projects"] = {
                "value": research_projects,
                "score": proj_score,
                "evidence": evidence_map.get("research_projects") or {}
            }
        
        # Component 3: Extension Activities (30%)
        if extension_activities is not None and extension_activities > 0:
            # 5 activities = 100
            ext_score = min(100.0, (extension_activities / 5) * 100)
            score_components.append(("extension_activities", ext_score, 0.30))
            evidence_info["extension_activities"] = {
                "value": extension_activities,
                "score": ext_score,
                "evidence": evidence_map.get("extension_activities") or {}
            }
        
        if len(score_components) == 0:
            return None, {
                "error": "Criterion 3 (Research, Innovations & Extension) data missing",
                "formula": "C3 = 0.40×Publications + 0.30×Projects + 0.30×Extension",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "C3 = 0.40×Publications + 0.30×Projects + 0.30×Extension",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }
    
    @staticmethod
    def calculate_criterion_4(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NAAC Criterion 4: Infrastructure & Learning Resources
        
        Components:
        - Physical Infrastructure (40%)
        - Library Resources (30%)
        - IT Infrastructure (30%)
        """
        built_up_area = parse_numeric(data.get("built_up_area")) or parse_numeric(data.get("total_area"))
        library_resources = parse_numeric(data.get("library_books")) or parse_numeric(data.get("library_volumes"))
        it_infrastructure = data.get("it_infrastructure") or data.get("computer_labs")
        
        score_components = []
        evidence_info = {}
        
        # Component 1: Physical Infrastructure (40%)
        if built_up_area and built_up_area > 0:
            # 10000 sqm = 100
            infra_score = min(100.0, (built_up_area / 10000) * 100)
            score_components.append(("physical_infrastructure", infra_score, 0.40))
            evidence_info["physical_infrastructure"] = {
                "value": built_up_area,
                "score": infra_score,
                "evidence": evidence_map.get("built_up_area") or {}
            }
        
        # Component 2: Library Resources (30%)
        if library_resources and library_resources > 0:
            # 50000 books = 100
            lib_score = min(100.0, (library_resources / 50000) * 100)
            score_components.append(("library_resources", lib_score, 0.30))
            evidence_info["library_resources"] = {
                "value": library_resources,
                "score": lib_score,
                "evidence": evidence_map.get("library_books") or {}
            }
        
        # Component 3: IT Infrastructure (30%)
        if it_infrastructure:
            it_score = 100.0 if isinstance(it_infrastructure, (dict, list)) and len(it_infrastructure) > 0 else 50.0
            score_components.append(("it_infrastructure", it_score, 0.30))
            evidence_info["it_infrastructure"] = {
                "present": True,
                "score": it_score,
                "evidence": evidence_map.get("it_infrastructure") or {}
            }
        
        if len(score_components) == 0:
            return None, {
                "error": "Criterion 4 (Infrastructure & Learning Resources) data missing",
                "formula": "C4 = 0.40×Physical Infrastructure + 0.30×Library + 0.30×IT",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "C4 = 0.40×Physical Infrastructure + 0.30×Library + 0.30×IT",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }
    
    @staticmethod
    def calculate_criterion_5(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NAAC Criterion 5: Student Support & Progression
        
        Components:
        - Student Support (40%)
        - Student Progression (30%)
        - Student Participation (30%)
        """
        student_support = data.get("student_support_services") or data.get("student_welfare")
        student_progression = parse_numeric(data.get("student_progression_rate")) or parse_numeric(data.get("graduation_rate"))
        student_participation = parse_numeric(data.get("student_participation")) or parse_numeric(data.get("co_curricular_activities"))
        
        score_components = []
        evidence_info = {}
        
        # Component 1: Student Support (40%)
        if student_support:
            support_score = 100.0 if isinstance(student_support, (dict, list)) and len(student_support) > 0 else 50.0
            score_components.append(("student_support", support_score, 0.40))
            evidence_info["student_support"] = {
                "present": True,
                "score": support_score,
                "evidence": evidence_map.get("student_support_services") or {}
            }
        
        # Component 2: Student Progression (30%)
        if student_progression is not None:
            progression_score = min(100.0, student_progression)
            score_components.append(("student_progression", progression_score, 0.30))
            evidence_info["student_progression"] = {
                "value": student_progression,
                "score": progression_score,
                "evidence": evidence_map.get("student_progression_rate") or {}
            }
        
        # Component 3: Student Participation (30%)
        if student_participation is not None:
            total_students = parse_numeric(data.get("total_students")) or parse_numeric(data.get("student_count"))
            if total_students and total_students > 0:
                participation_pct = (student_participation / total_students) * 100
                participation_score = min(100.0, participation_pct)
                score_components.append(("student_participation", participation_score, 0.30))
                evidence_info["student_participation"] = {
                    "value": student_participation,
                    "percentage": round(participation_pct, 2),
                    "score": participation_score,
                    "evidence": evidence_map.get("student_participation") or {}
                }
        
        if len(score_components) == 0:
            return None, {
                "error": "Criterion 5 (Student Support & Progression) data missing",
                "formula": "C5 = 0.40×Support + 0.30×Progression + 0.30×Participation",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "C5 = 0.40×Support + 0.30×Progression + 0.30×Participation",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }
    
    @staticmethod
    def calculate_criterion_6(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NAAC Criterion 6: Governance, Leadership & Management
        
        Components:
        - Governance Structure (40%)
        - Leadership (30%)
        - Management Practices (30%)
        """
        governance_structure = data.get("governance_structure") or data.get("administrative_structure")
        leadership = data.get("leadership") or data.get("leadership_team")
        management_practices = data.get("management_practices") or data.get("administrative_practices")
        
        score_components = []
        evidence_info = {}
        
        # Component 1: Governance Structure (40%)
        if governance_structure:
            gov_score = 100.0 if isinstance(governance_structure, (dict, list)) and len(governance_structure) > 0 else 50.0
            score_components.append(("governance_structure", gov_score, 0.40))
            evidence_info["governance_structure"] = {
                "present": True,
                "score": gov_score,
                "evidence": evidence_map.get("governance_structure") or {}
            }
        
        # Component 2: Leadership (30%)
        if leadership:
            lead_score = 100.0 if isinstance(leadership, (dict, list)) and len(leadership) > 0 else 50.0
            score_components.append(("leadership", lead_score, 0.30))
            evidence_info["leadership"] = {
                "present": True,
                "score": lead_score,
                "evidence": evidence_map.get("leadership") or {}
            }
        
        # Component 3: Management Practices (30%)
        if management_practices:
            mgmt_score = 100.0 if isinstance(management_practices, (dict, list)) and len(management_practices) > 0 else 50.0
            score_components.append(("management_practices", mgmt_score, 0.30))
            evidence_info["management_practices"] = {
                "present": True,
                "score": mgmt_score,
                "evidence": evidence_map.get("management_practices") or {}
            }
        
        if len(score_components) == 0:
            return None, {
                "error": "Criterion 6 (Governance, Leadership & Management) data missing",
                "formula": "C6 = 0.40×Governance + 0.30×Leadership + 0.30×Management",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "C6 = 0.40×Governance + 0.30×Leadership + 0.30×Management",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }
    
    @staticmethod
    def calculate_criterion_7(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NAAC Criterion 7: Institutional Values & Best Practices
        
        Components:
        - Institutional Values (50%)
        - Best Practices (50%)
        """
        institutional_values = data.get("institutional_values") or data.get("core_values")
        best_practices = data.get("best_practices") or data.get("innovative_practices")
        
        score_components = []
        evidence_info = {}
        
        # Component 1: Institutional Values (50%)
        if institutional_values:
            values_score = 100.0 if isinstance(institutional_values, (dict, list)) and len(institutional_values) > 0 else 50.0
            score_components.append(("institutional_values", values_score, 0.50))
            evidence_info["institutional_values"] = {
                "present": True,
                "score": values_score,
                "evidence": evidence_map.get("institutional_values") or {}
            }
        
        # Component 2: Best Practices (50%)
        if best_practices:
            practices_score = 100.0 if isinstance(best_practices, (dict, list)) and len(best_practices) > 0 else 50.0
            score_components.append(("best_practices", practices_score, 0.50))
            evidence_info["best_practices"] = {
                "present": True,
                "score": practices_score,
                "evidence": evidence_map.get("best_practices") or {}
            }
        
        if len(score_components) == 0:
            return None, {
                "error": "Criterion 7 (Institutional Values & Best Practices) data missing",
                "formula": "C7 = 0.50×Institutional Values + 0.50×Best Practices",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "C7 = 0.50×Institutional Values + 0.50×Best Practices",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }

