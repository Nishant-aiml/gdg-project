"""
NIRF (National Institutional Ranking Framework) Official Formulas
Institution-level ranking with 5 parameters
"""

from typing import Dict, Any, Optional, Tuple
from utils.parse_numeric import parse_numeric
import logging

logger = logging.getLogger(__name__)

# Import ProductionGuard for evidence validation
from services.production_guard import ProductionGuard


class NIRFFormulas:
    """
    NIRF ranking formulas - Institution level
    5 Parameters: TLR, RP, GO, OI, PR
    """
    
    @staticmethod
    def calculate_tlr(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NIRF Parameter: Teaching, Learning & Resources (TLR)
        
        Components:
        - Student Strength (30%)
        - Faculty-Student Ratio (30%)
        - Financial Resources (20%)
        - Library Resources (20%)
        """
        student_strength = parse_numeric(data.get("total_students")) or parse_numeric(data.get("student_count"))
        faculty_count = parse_numeric(data.get("faculty_count")) or parse_numeric(data.get("total_faculty"))
        financial_resources = parse_numeric(data.get("financial_resources")) or parse_numeric(data.get("budget"))
        library_resources = parse_numeric(data.get("library_books")) or parse_numeric(data.get("library_volumes"))
        
        # EVIDENCE ENFORCEMENT: Validate evidence for critical fields
        if student_strength is not None:
            student_evidence = evidence_map.get("total_students") or evidence_map.get("student_count") or {}
            has_evidence, error_msg = ProductionGuard.validate_evidence_required(
                student_strength, student_evidence, "student_strength"
            )
            if not has_evidence:
                logger.warning(f"NIRF TLR calculation: {error_msg}")
                student_strength = None
        
        if faculty_count is not None:
            faculty_evidence = evidence_map.get("faculty_count") or evidence_map.get("total_faculty") or {}
            has_evidence, error_msg = ProductionGuard.validate_evidence_required(
                faculty_count, faculty_evidence, "faculty_count"
            )
            if not has_evidence:
                logger.warning(f"NIRF TLR calculation: {error_msg}")
                faculty_count = None
        
        score_components = []
        evidence_info = {}
        
        # Component 1: Student Strength (30%)
        if student_strength and student_strength > 0:
            # Normalize: 2000 students = 100
            strength_score = min(100.0, (student_strength / 2000) * 100)
            score_components.append(("student_strength", strength_score, 0.30))
            evidence_info["student_strength"] = {
                "value": student_strength,
                "score": strength_score,
                "evidence": evidence_map.get("total_students") or {}
            }
        
        # Component 2: Faculty-Student Ratio (30%)
        if faculty_count and student_strength and faculty_count > 0:
            fsr = student_strength / faculty_count
            if fsr <= 15:
                fsr_score = 100.0
            elif fsr <= 20:
                fsr_score = 80.0
            elif fsr <= 25:
                fsr_score = 60.0
            else:
                fsr_score = max(0.0, 60.0 - (fsr - 25) * 2)
            
            score_components.append(("fsr", fsr_score, 0.30))
            evidence_info["fsr"] = {
                "value": round(fsr, 2),
                "score": fsr_score,
                "evidence": evidence_map.get("faculty_count") or {}
            }
        
        # Component 3: Financial Resources (20%)
        if financial_resources and financial_resources > 0:
            # 10 crores = 100
            fin_score = min(100.0, (financial_resources / 10) * 100)
            score_components.append(("financial_resources", fin_score, 0.20))
            evidence_info["financial_resources"] = {
                "value": financial_resources,
                "score": fin_score,
                "evidence": evidence_map.get("financial_resources") or {}
            }
        
        # Component 4: Library Resources (20%)
        if library_resources and library_resources > 0:
            # 50000 books = 100
            lib_score = min(100.0, (library_resources / 50000) * 100)
            score_components.append(("library_resources", lib_score, 0.20))
            evidence_info["library_resources"] = {
                "value": library_resources,
                "score": lib_score,
                "evidence": evidence_map.get("library_books") or {}
            }
        
        if len(score_components) == 0:
            return None, {
                "error": "TLR (Teaching, Learning & Resources) data missing",
                "formula": "TLR = 0.30×Student Strength + 0.30×FSR + 0.20×Financial + 0.20×Library",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "TLR = 0.30×Student Strength + 0.30×FSR + 0.20×Financial + 0.20×Library",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }
    
    @staticmethod
    def calculate_rp(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NIRF Parameter: Research & Professional Practice (RP)
        
        Components:
        - Publications (40%)
        - Citations (30%)
        - Patents (30%)
        """
        # NO FALLBACK VALUES - Missing data must return None
        publications = parse_numeric(data.get("research_publications")) or parse_numeric(data.get("publications"))
        citations = parse_numeric(data.get("citations")) or parse_numeric(data.get("citation_count"))
        patents = parse_numeric(data.get("patents")) or parse_numeric(data.get("patent_count"))
        
        score_components = []
        evidence_info = {}
        
        # Component 1: Publications (40%)
        if publications is not None and publications > 0:
            # 100 publications = 100
            pub_score = min(100.0, (publications / 100) * 100)
            score_components.append(("publications", pub_score, 0.40))
            evidence_info["publications"] = {
                "value": publications,
                "score": pub_score,
                "evidence": evidence_map.get("research_publications") or {}
            }
        
        # Component 2: Citations (30%)
        if citations is not None and citations > 0:
            # 500 citations = 100
            cit_score = min(100.0, (citations / 500) * 100)
            score_components.append(("citations", cit_score, 0.30))
            evidence_info["citations"] = {
                "value": citations,
                "score": cit_score,
                "evidence": evidence_map.get("citations") or {}
            }
        
        # Component 3: Patents (30%)
        if patents is not None and patents > 0:
            # 10 patents = 100
            pat_score = min(100.0, (patents / 10) * 100)
            score_components.append(("patents", pat_score, 0.30))
            evidence_info["patents"] = {
                "value": patents,
                "score": pat_score,
                "evidence": evidence_map.get("patents") or {}
            }
        
        if len(score_components) == 0:
            return None, {
                "error": "RP (Research & Professional Practice) data missing",
                "formula": "RP = 0.40×Publications + 0.30×Citations + 0.30×Patents",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "RP = 0.40×Publications + 0.30×Citations + 0.30×Patents",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }
    
    @staticmethod
    def calculate_go(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NIRF Parameter: Graduation Outcomes (GO)
        
        Components:
        - Placement Rate (40%)
        - Higher Studies (30%)
        - Graduation Rate (30%)
        """
        placement_rate = parse_numeric(data.get("placement_rate")) or parse_numeric(data.get("placement_percentage"))
        higher_studies = parse_numeric(data.get("higher_studies_count")) or parse_numeric(data.get("students_higher_studies"))
        graduation_rate = parse_numeric(data.get("graduation_rate")) or parse_numeric(data.get("pass_percentage"))
        
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
        
        # Component 2: Higher Studies (30%)
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
        
        # Component 3: Graduation Rate (30%)
        if graduation_rate is not None:
            grad_score = min(100.0, graduation_rate)
            score_components.append(("graduation_rate", grad_score, 0.30))
            evidence_info["graduation_rate"] = {
                "value": graduation_rate,
                "score": grad_score,
                "evidence": evidence_map.get("graduation_rate") or {}
            }
        
        if len(score_components) == 0:
            return None, {
                "error": "GO (Graduation Outcomes) data missing",
                "formula": "GO = 0.40×Placement + 0.30×Higher Studies + 0.30×Graduation Rate",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "GO = 0.40×Placement + 0.30×Higher Studies + 0.30×Graduation Rate",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }
    
    @staticmethod
    def calculate_oi(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NIRF Parameter: Outreach & Inclusivity (OI)
        
        Components:
        - Women Students % (40%)
        - Economically Disadvantaged % (30%)
        - Outreach Activities (30%)
        """
        women_students = parse_numeric(data.get("women_students")) or parse_numeric(data.get("female_students"))
        economically_disadvantaged = parse_numeric(data.get("economically_disadvantaged_students")) or parse_numeric(data.get("sc_st_students"))
        outreach_activities = parse_numeric(data.get("outreach_activities")) or parse_numeric(data.get("community_services"))
        
        score_components = []
        evidence_info = {}
        
        # Component 1: Women Students % (40%)
        if women_students is not None:
            total_students = parse_numeric(data.get("total_students")) or parse_numeric(data.get("student_count"))
            if total_students and total_students > 0:
                women_pct = (women_students / total_students) * 100
                # 40% women = 100
                women_score = min(100.0, (women_pct / 40) * 100)
                score_components.append(("women_students", women_score, 0.40))
                evidence_info["women_students"] = {
                    "value": women_students,
                    "percentage": round(women_pct, 2),
                    "score": women_score,
                    "evidence": evidence_map.get("women_students") or {}
                }
        
        # Component 2: Economically Disadvantaged % (30%)
        if economically_disadvantaged is not None:
            total_students = parse_numeric(data.get("total_students")) or parse_numeric(data.get("student_count"))
            if total_students and total_students > 0:
                disadvantaged_pct = (economically_disadvantaged / total_students) * 100
                # 20% disadvantaged = 100
                disadvantaged_score = min(100.0, (disadvantaged_pct / 20) * 100)
                score_components.append(("economically_disadvantaged", disadvantaged_score, 0.30))
                evidence_info["economically_disadvantaged"] = {
                    "value": economically_disadvantaged,
                    "percentage": round(disadvantaged_pct, 2),
                    "score": disadvantaged_score,
                    "evidence": evidence_map.get("economically_disadvantaged_students") or {}
                }
        
        # Component 3: Outreach Activities (30%)
        if outreach_activities and outreach_activities > 0:
            # 10 activities = 100
            outreach_score = min(100.0, (outreach_activities / 10) * 100)
            score_components.append(("outreach_activities", outreach_score, 0.30))
            evidence_info["outreach_activities"] = {
                "value": outreach_activities,
                "score": outreach_score,
                "evidence": evidence_map.get("outreach_activities") or {}
            }
        
        if len(score_components) == 0:
            return None, {
                "error": "OI (Outreach & Inclusivity) data missing",
                "formula": "OI = 0.40×Women Students + 0.30×Economically Disadvantaged + 0.30×Outreach",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "OI = 0.40×Women Students + 0.30×Economically Disadvantaged + 0.30×Outreach",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }
    
    @staticmethod
    def calculate_pr(
        data: Dict[str, Any],
        evidence_map: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        NIRF Parameter: Perception (PR)
        
        Components:
        - Peer Perception (50%)
        - Employer Perception (30%)
        - Public Perception (20%)
        """
        peer_perception = parse_numeric(data.get("peer_perception")) or parse_numeric(data.get("peer_ranking"))
        employer_perception = parse_numeric(data.get("employer_perception")) or parse_numeric(data.get("employer_rating"))
        public_perception = parse_numeric(data.get("public_perception")) or parse_numeric(data.get("public_ranking"))
        
        score_components = []
        evidence_info = {}
        
        # Component 1: Peer Perception (50%)
        if peer_perception is not None:
            peer_score = min(100.0, peer_perception)
            score_components.append(("peer_perception", peer_score, 0.50))
            evidence_info["peer_perception"] = {
                "value": peer_perception,
                "score": peer_score,
                "evidence": evidence_map.get("peer_perception") or {}
            }
        
        # Component 2: Employer Perception (30%)
        if employer_perception is not None:
            employer_score = min(100.0, employer_perception)
            score_components.append(("employer_perception", employer_score, 0.30))
            evidence_info["employer_perception"] = {
                "value": employer_perception,
                "score": employer_score,
                "evidence": evidence_map.get("employer_perception") or {}
            }
        
        # Component 3: Public Perception (20%)
        if public_perception is not None:
            public_score = min(100.0, public_perception)
            score_components.append(("public_perception", public_score, 0.20))
            evidence_info["public_perception"] = {
                "value": public_perception,
                "score": public_score,
                "evidence": evidence_map.get("public_perception") or {}
            }
        
        if len(score_components) == 0:
            return None, {
                "error": "PR (Perception) data missing",
                "formula": "PR = 0.50×Peer + 0.30×Employer + 0.20×Public",
                "evidence": {}
            }
        
        total_weight = sum(w for _, _, w in score_components)
        weighted_sum = sum(s * w for _, s, w in score_components)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(final_score, 2), {
            "formula": "PR = 0.50×Peer + 0.30×Employer + 0.20×Public",
            "components": {name: score for name, score, _ in score_components},
            "score": round(final_score, 2),
            "evidence": evidence_info
        }

