"""
KPI scoring engine for UGC and AICTE
Returns None instead of 0 when required fields are missing
"""

from typing import Dict, Any, List, Optional
from config.rules import get_kpi_formulas
from utils.parse_numeric import parse_numeric
import logging
import math

logger = logging.getLogger(__name__)

class KPIService:
    def calculate_kpis(
        self,
        mode: str,
        blocks: List[Dict[str, Any]] = None,
        aggregated_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calculate all KPIs for the mode from information blocks
        Uses official formulas with evidence tracking
        
        Returns normalized scores (0-100) or None if required fields missing
        
        Can work with either:
        - blocks: List of information blocks (new way)
        - aggregated_data: Pre-aggregated data from blocks (preferred)
        """
        from services.evidence_tracker import EvidenceTracker
        from services.kpi_official import OfficialKPIService
        
        formulas = get_kpi_formulas(mode)
        kpi_results = {}
        
        # Extract all data from blocks OR use provided aggregated data
        if aggregated_data:
            extracted_data = aggregated_data
        elif blocks:
            extracted_data = self._aggregate_block_data(blocks)
        else:
            extracted_data = {}
        
        # Build evidence map from blocks
        evidence_map = {}
        if blocks:
            # Evidence tracker now supports dicts directly
            evidence_map = EvidenceTracker.build_evidence_map(blocks)
        
        # Use official KPI service for AICTE, NBA, NAAC, NIRF
        official_service = OfficialKPIService()
        
        # Calculate each KPI using official formulas
        for kpi_id, kpi_config in formulas.items():
            if mode.lower() == "aicte":
                # AICTE mode - use official formulas
                if kpi_id == "fsr_score":
                    score, info = official_service.calculate_aicte_fsr(extracted_data, evidence_map)
                elif kpi_id == "infrastructure_score":
                    score, info = official_service.calculate_aicte_infrastructure(extracted_data, evidence_map)
                elif kpi_id == "placement_index":
                    score, info = official_service.calculate_aicte_placement(extracted_data, evidence_map)
                elif kpi_id == "lab_compliance_index":
                    score, info = official_service.calculate_aicte_lab_compliance(extracted_data, evidence_map)
                else:
                    # Fallback to legacy method
                    formula_func = getattr(self, kpi_config["formula"], None)
                    score = formula_func(extracted_data, mode) if formula_func else None
                    info = {}
            elif mode.lower() == "nba":
                # NBA mode - use official formulas
                if kpi_id == "peos_psos":
                    score, info = official_service.calculate_nba_peos_psos(extracted_data, evidence_map)
                elif kpi_id == "faculty_quality":
                    score, info = official_service.calculate_nba_faculty_quality(extracted_data, evidence_map)
                elif kpi_id == "student_performance":
                    score, info = official_service.calculate_nba_student_performance(extracted_data, evidence_map)
                elif kpi_id == "continuous_improvement":
                    score, info = official_service.calculate_nba_continuous_improvement(extracted_data, evidence_map)
                elif kpi_id == "co_po_mapping":
                    score, info = official_service.calculate_nba_co_po_mapping(extracted_data, evidence_map)
                else:
                    score = None
                    info = {}
            elif mode.lower() == "naac":
                # NAAC mode - use official formulas
                criterion_id = kpi_id  # e.g., "criterion_1"
                score, info = official_service.calculate_naac_criterion(criterion_id, extracted_data, evidence_map)
            elif mode.lower() == "nirf":
                # NIRF mode - use official formulas
                parameter_name = kpi_id  # e.g., "tlr"
                score, info = official_service.calculate_nirf_parameter(parameter_name, extracted_data, evidence_map)
            else:
                # UGC or other modes - use legacy methods
                formula_func = getattr(self, kpi_config["formula"], None)
                score = formula_func(extracted_data, mode) if formula_func else None
                info = {}
            
            kpi_results[kpi_id] = {
                "name": kpi_config["name"],
                "value": score if score is None else round(score, 2),
                "weight": kpi_config["weight"],
                "evidence_info": info.get("evidence", {}) if isinstance(info, dict) else {}
            }
        
        # Calculate overall score based on mode-specific formulas
        if mode.lower() == "aicte":
            # AICTE Overall - OFFICIAL FORMULA
            fsr = kpi_results.get("fsr_score", {}).get("value")
            infra = kpi_results.get("infrastructure_score", {}).get("value")
            placement = kpi_results.get("placement_index", {}).get("value")
            lab = kpi_results.get("lab_compliance_index", {}).get("value")

            kpi_scores = {
                "fsr_score": fsr,
                "infrastructure_score": infra,
                "placement_index": placement,
                "lab_compliance_index": lab
            }
            
            overall_score, overall_info = official_service.calculate_aicte_overall(kpi_scores)
            kpi_results["overall_score"] = {
                "name": "AICTE Overall Score",
                "value": overall_score,
                "weight": 1.0,
                "evidence_info": overall_info
            }
        elif mode.lower() == "nba":
            # NBA Overall - OFFICIAL FORMULA
            peos_psos = kpi_results.get("peos_psos", {}).get("value")
            faculty_quality = kpi_results.get("faculty_quality", {}).get("value")
            student_performance = kpi_results.get("student_performance", {}).get("value")
            continuous_improvement = kpi_results.get("continuous_improvement", {}).get("value")
            co_po_mapping = kpi_results.get("co_po_mapping", {}).get("value")
            
            criterion_scores = {
                "peos_psos": peos_psos,
                "faculty_quality": faculty_quality,
                "student_performance": student_performance,
                "continuous_improvement": continuous_improvement,
                "co_po_mapping": co_po_mapping
            }
            
            overall_score, overall_info = official_service.calculate_nba_overall(criterion_scores)
            kpi_results["overall_score"] = {
                "name": "NBA Overall Score",
                "value": overall_score,
                "weight": 1.0,
                "evidence_info": overall_info
            }
        elif mode.lower() == "naac":
            # NAAC Overall - OFFICIAL FORMULA
            criterion_1 = kpi_results.get("criterion_1", {}).get("value")
            criterion_2 = kpi_results.get("criterion_2", {}).get("value")
            criterion_3 = kpi_results.get("criterion_3", {}).get("value")
            criterion_4 = kpi_results.get("criterion_4", {}).get("value")
            criterion_5 = kpi_results.get("criterion_5", {}).get("value")
            criterion_6 = kpi_results.get("criterion_6", {}).get("value")
            criterion_7 = kpi_results.get("criterion_7", {}).get("value")
            
            criterion_scores = {
                "criterion_1": criterion_1,
                "criterion_2": criterion_2,
                "criterion_3": criterion_3,
                "criterion_4": criterion_4,
                "criterion_5": criterion_5,
                "criterion_6": criterion_6,
                "criterion_7": criterion_7
            }
            
            criterion_weights = {
                "criterion_1": 0.15,
                "criterion_2": 0.15,
                "criterion_3": 0.15,
                "criterion_4": 0.15,
                "criterion_5": 0.15,
                "criterion_6": 0.15,
                "criterion_7": 0.10
            }
            
            overall_score, overall_info = official_service.calculate_naac_overall(criterion_scores, criterion_weights)
            kpi_results["overall_score"] = {
                "name": "NAAC Overall Score",
                "value": overall_score,
                "weight": 1.0,
                "evidence_info": overall_info
            }
        elif mode.lower() == "nirf":
            # NIRF Overall - OFFICIAL FORMULA
            tlr = kpi_results.get("tlr", {}).get("value")
            rp = kpi_results.get("rp", {}).get("value")
            go = kpi_results.get("go", {}).get("value")
            oi = kpi_results.get("oi", {}).get("value")
            pr = kpi_results.get("pr", {}).get("value")
            
            parameter_scores = {
                "tlr": tlr,
                "rp": rp,
                "go": go,
                "oi": oi,
                "pr": pr
            }
            
            parameter_weights = {
                "tlr": 0.30,
                "rp": 0.30,
                "go": 0.20,
                "oi": 0.10,
                "pr": 0.10
            }
            
            overall_score, overall_info = official_service.calculate_nirf_overall(parameter_scores, parameter_weights)
            kpi_results["overall_score"] = {
                "name": "NIRF Overall Score",
                "value": overall_score,
                "weight": 1.0,
                "evidence_info": overall_info
            }
        else:
            # Fallback: calculate from available KPIs
            kpi_values = [kpi["value"] for kpi in kpi_results.values() if kpi["value"] is not None]
            if kpi_values:
                total_weight = sum(kpi["weight"] for kpi in kpi_results.values() if kpi["value"] is not None)
                overall_score = sum(
                    kpi["value"] * kpi["weight"] 
                    for kpi in kpi_results.values()
                    if kpi["value"] is not None
                ) / total_weight if total_weight > 0 else 0
                kpi_results["overall_score"] = {
                    "name": f"{mode.upper()} Overall Score",
                    "value": round(overall_score, 2),
                    "weight": 1.0
                }
            else:
                kpi_results["overall_score"] = {
                    "name": f"{mode.upper()} Overall Score",
                    "value": None,
                    "weight": 1.0
                }
        
        return kpi_results
    
    def _aggregate_block_data(self, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate extracted data from all information blocks, preferring _num fields"""
        aggregated = {}
        
        for block in blocks:
            # Skip invalid blocks
            if block.get("is_invalid", False):
                continue
                
            extracted_data = block.get("extracted_data", {})
            if extracted_data and isinstance(extracted_data, dict):
                # First pass: Add all _num fields directly (these are already normalized to correct units)
                for key, value in extracted_data.items():
                    if key.endswith("_num") and isinstance(value, (int, float)):
                        if key not in aggregated:
                            aggregated[key] = value
                        else:
                            # Take max if both exist (for numeric values)
                            if isinstance(aggregated[key], (int, float)):
                                aggregated[key] = max(aggregated[key], value)
                            else:
                                aggregated[key] = value
                        
                        # Special handling for area fields: ensure built_up_area_sqm_num exists
                        if key in ["built_up_area_num", "area_num", "total_area_num", "campus_area_num", "building_area_num"]:
                            # All area values from parse_numeric are already in sqm
                            if "built_up_area_sqm_num" not in aggregated:
                                aggregated["built_up_area_sqm_num"] = value
                            else:
                                aggregated["built_up_area_sqm_num"] = max(aggregated["built_up_area_sqm_num"], value)
                
                # Second pass: Add non-_num fields (for raw values and string fields)
                for key, value in extracted_data.items():
                    if key.endswith("_num"):
                        continue  # Already handled above
                    
                    if value is None or value == "" or value == "null" or value == "None":
                        continue
                    
                    # Map common alternate field names
                    target_key = key
                    if key == "total_faculty":
                        target_key = "faculty_count"
                    elif key in ("total_intake", "admitted_students"):
                        if "student_count" not in aggregated:
                            target_key = "student_count"
                    
                    # Check if _num variant exists (prefer parsed numeric)
                    num_key = f"{key}_num"
                    if num_key in extracted_data and extracted_data[num_key] is not None:
                        # Use parsed numeric value
                        if target_key not in aggregated or not isinstance(aggregated.get(target_key), (int, float)):
                            aggregated[target_key] = extracted_data[num_key]
                            aggregated[f"{target_key}_num"] = extracted_data[num_key]
                        else:
                            # Take max if both exist
                            current = aggregated[target_key]
                            new_val = extracted_data[num_key]
                            if isinstance(current, (int, float)) and isinstance(new_val, (int, float)):
                                aggregated[target_key] = max(current, new_val)
                                aggregated[f"{target_key}_num"] = max(current, new_val)
                    else:
                        # Use raw value and try to parse
                        if target_key in aggregated:
                            # If both are numbers, take the maximum
                            try:
                                current_val = parse_numeric(aggregated[target_key]) or 0
                                new_val = parse_numeric(value) or 0
                                if current_val > 0 or new_val > 0:
                                    max_val = max(current_val, new_val)
                                    aggregated[target_key] = max_val
                                    aggregated[f"{target_key}_num"] = max_val
                                else:
                                    aggregated[target_key] = value if value else aggregated[target_key]
                            except (ValueError, TypeError):
                                if value:
                                    aggregated[target_key] = value
                        else:
                            aggregated[target_key] = value
                            # Try to parse and add _num
                            parsed = parse_numeric(value)
                            if parsed is not None:
                                aggregated[f"{target_key}_num"] = parsed
        
        logger.debug(f"Aggregated data keys: {list(aggregated.keys())}")
        logger.debug(f"Sample values: faculty_count={aggregated.get('faculty_count')}, built_up_area_sqm_num={aggregated.get('built_up_area_sqm_num')}")
        
        return aggregated
    
    # UGC KPI Formulas
    def calculate_research_index(self, data: Dict[str, Any], mode: str) -> Optional[float]:
        """
        Calculate Research Index (0-100) or None if required fields missing
        Formula:
        - research_index = normalize(publications + citations + funded_projects)
        """
        publications = parse_numeric(data.get("publication_count")) or parse_numeric(data.get("publications")) or 0
        citations = parse_numeric(data.get("citation_count")) or parse_numeric(data.get("citations")) or 0
        funded_projects = parse_numeric(data.get("funded_projects")) or parse_numeric(data.get("projects")) or 0
        
        # Return None if all are missing
        if publications == 0 and citations == 0 and funded_projects == 0:
            return None
        
        # Normalize: publications (weight 0.5), citations (weight 0.3), funded_projects (weight 0.2)
        # Target values: 50 pubs = 100, 200 citations = 100, 10 projects = 100
        pub_score = min(publications / 50 * 100, 100) if publications > 0 else 0
        cit_score = min(citations / 200 * 100, 100) if citations > 0 else 0
        proj_score = min(funded_projects / 10 * 100, 100) if funded_projects > 0 else 0
        
        # Weighted average
        total_weight = 0.0
        weighted_sum = 0.0
        
        if publications > 0:
            total_weight += 0.5
            weighted_sum += pub_score * 0.5
        
        if citations > 0:
            total_weight += 0.3
            weighted_sum += cit_score * 0.3
        
        if funded_projects > 0:
            total_weight += 0.2
            weighted_sum += proj_score * 0.2
        
        if total_weight > 0:
            return weighted_sum / total_weight
        
        return None
    
    def calculate_governance_score(self, data: Dict[str, Any], mode: str) -> Optional[float]:
        """
        Calculate Governance Score (0-100) or None if required fields missing
        Formula:
        - governance_score = (present_committee_count / required_committee_count) * 100
        """
        present_committee_count = parse_numeric(data.get("committee_count")) or parse_numeric(data.get("present_committees"))
        
        # Return None if present_committee_count is missing
        if present_committee_count is None:
            return None
        
        required_committee_count = parse_numeric(data.get("required_committees"))
        
        # If required_committees not specified, use default (5 for UGC)
        if required_committee_count is None:
            required_committee_count = 5  # Default: BoG, AC, FC, IQAC, SC/ST
        
        if required_committee_count == 0:
            return None
        
        governance_score = (present_committee_count / required_committee_count) * 100
        
        # Cap at 100
        return min(governance_score, 100.0)
    
    def calculate_student_outcome_index(self, data: Dict[str, Any], mode: str) -> Optional[float]:
        """
        Calculate Student Outcome Index (0-100) or None if required fields missing
        Formula:
        - student_outcome = placement_rate
        """
        placement_rate = (parse_numeric(data.get("placement_percentage")) or 
                         parse_numeric(data.get("placement_rate")))
        
        # Return None if placement_rate is missing
        if placement_rate is None:
            return None
        
        # Cap at 100
        return min(placement_rate, 100.0)
    
    # AICTE KPI Formulas
    def calculate_fsr_score(self, data: Dict[str, Any], mode: str) -> Optional[float]:
        """
        Calculate FSR (Faculty Student Ratio) Score - OFFICIAL FORMULA
        
        Formula: FSR = Total Students / Total Faculty (NOT Faculty/Students)
        
        Scoring Rule:
        - FSR ≤ 15 → Score = 100
        - 15 < FSR ≤ 20 → Score = linear scale (100 → 60)
        - FSR > 20 → Score = proportional penalty
        
        STRICT: Only uses parsed numeric values (_num fields or parse_numeric results)
        Returns None if required fields missing (not 0)
        """
        # STRICT: Prefer _num fields (already parsed and validated)
        faculty_count = (
            data.get("faculty_count_num") or
            (parse_numeric(data.get("faculty_count")) if isinstance(data.get("faculty_count"), (str, int, float)) else None) or
            (parse_numeric(data.get("faculty")) if isinstance(data.get("faculty"), (str, int, float)) else None) or
            (parse_numeric(data.get("total_faculty")) if isinstance(data.get("total_faculty"), (str, int, float)) else None)
        )
        
        student_count = (
            data.get("student_count_num") or
            data.get("total_students_num") or
            data.get("total_intake_num") or
            (parse_numeric(data.get("total_students")) if isinstance(data.get("total_students"), (str, int, float)) else None) or
            (parse_numeric(data.get("student_count")) if isinstance(data.get("student_count"), (str, int, float)) else None) or
            (parse_numeric(data.get("students")) if isinstance(data.get("students"), (str, int, float)) else None) or
            (parse_numeric(data.get("total_intake")) if isinstance(data.get("total_intake"), (str, int, float)) else None) or
            (parse_numeric(data.get("admitted_students")) if isinstance(data.get("admitted_students"), (str, int, float)) else None)
        )
        
        # If student_count is not found, try to calculate from programs_approved
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
        
        # Return None if either is missing (required fields)
        if faculty_count is None or student_count is None:
            return None
        
        if student_count == 0 or faculty_count == 0:
            return None
        
        # OFFICIAL FORMULA: FSR = Students / Faculty (NOT Faculty/Students)
        fsr = student_count / faculty_count
        
        # Official scoring rule
        if fsr <= 15:
            return 100.0
        elif fsr <= 20:
            # Linear scale: 100 at FSR=15, 60 at FSR=20
            # slope = (60 - 100) / (20 - 15) = -8
            # score = 100 + (fsr - 15) * (-8)
            score = 100 + (fsr - 15) * (-8)
            return round(score, 2)
        else:
            # Proportional penalty: FSR > 20
            # Penalty = (fsr - 20) * 3 per unit over 20
            # Score = 60 - min(60, (fsr - 20) * 3)
            penalty = (fsr - 20) * 3
            score = max(0.0, 60.0 - penalty)
            return round(score, 2)
    
    def calculate_infrastructure_score(self, data: Dict[str, Any], mode: str) -> Optional[float]:
        """
        Calculate Infrastructure Score (0-100) using weighted scoring
        Formula: weighted combination of area, classrooms, library, digital resources, hostel
        """
        import math
        
        # Get student count
        student_count = (
            data.get("total_students_num")
            or data.get("student_count_num")
            or data.get("total_intake_num")
            or parse_numeric(data.get("total_students"))
            or parse_numeric(data.get("student_count"))
            or parse_numeric(data.get("total_intake"))
            or parse_numeric(data.get("admitted_students"))
        )
        
        # Return None if student count missing
        if student_count is None or student_count == 0:
            return None
        
        # 1. Area Score (40% weight) - Updated formula
        # Prefer _num fields (already normalized to sqm)
        built_up_area_sqm = (
            data.get("built_up_area_sqm_num")
            or data.get("built_up_area_num")
        )
        
        # If not found, try parsing raw values with unit conversion
        if built_up_area_sqm is None:
            raw_area = (
                data.get("built_up_area_raw")
                or data.get("built_up_area")
                or data.get("area")
                or data.get("total_area")
                or data.get("campus_area")
                or data.get("building_area")
            )
            if raw_area:
                # Use parse_numeric which handles unit conversion (sqft→sqm, acres→sqm, etc.)
                built_up_area_sqm = parse_numeric(raw_area)
                # If still None, try parse_numeric_with_metadata
                if built_up_area_sqm is None:
                    try:
                        from utils.parse_numeric_with_metadata import parse_numeric_with_metadata
                        meta = parse_numeric_with_metadata(raw_area)
                        built_up_area_sqm = meta.get("value")
                    except:
                        pass
        
        if built_up_area_sqm is None:
            area_score = 0.0
        else:
            required_area = student_count * 4  # AICTE norm: 4 sqm per student
            # Area scoring: min(100, (actual_area / required_area) * 100)
            area_score = min(100.0, (built_up_area_sqm / required_area) * 100) if required_area > 0 else 0.0
            # Normalize to 0-1 for weighted calculation
            area_score = area_score / 100.0
        
        # 2. Classroom Score (25% weight) - STRICT: Only parsed numeric values
        actual_classrooms = (
            data.get("classrooms_num") or
            data.get("total_classrooms_num") or
            data.get("number_of_classrooms_num") or
            (parse_numeric(data.get("total_classrooms")) if isinstance(data.get("total_classrooms"), (str, int, float)) else None) or
            (parse_numeric(data.get("classrooms")) if isinstance(data.get("classrooms"), (str, int, float)) else None) or
            (parse_numeric(data.get("number_of_classrooms")) if isinstance(data.get("number_of_classrooms"), (str, int, float)) else None) or
            0
        )
        required_classrooms = math.ceil(student_count / 40)  # AICTE norm: 40 students per classroom
        classroom_score = min(1.0, actual_classrooms / required_classrooms) if required_classrooms > 0 else 0.0
        
        # 3. Library Score (15% weight) - STRICT: Only parsed numeric values (already in sqm)
        library_area_sqm = (
            data.get("library_area_sqm_num") or
            data.get("library_area_num") or
            (parse_numeric(data.get("library_area_sqm")) if isinstance(data.get("library_area_sqm"), (str, int, float)) else None) or
            (parse_numeric(data.get("library_area")) if isinstance(data.get("library_area"), (str, int, float)) else None) or
            0
        )
        required_library = student_count * 0.5  # 0.5 sqm per student
        library_score = min(1.0, library_area_sqm / required_library) if required_library > 0 else 0.0
        
        # 4. Digital Library Score (10% weight) - STRICT: Only parsed numeric values
        digital_resources = (
            data.get("digital_library_resources_num") or
            data.get("digital_resources_num") or
            (parse_numeric(data.get("digital_library_resources")) if isinstance(data.get("digital_library_resources"), (str, int, float)) else None) or
            (parse_numeric(data.get("digital_resources")) if isinstance(data.get("digital_resources"), (str, int, float)) else None) or
            0
        )
        digital_library_score = min(1.0, digital_resources / 500)  # 500 resources = 100%
        
        # 5. Hostel Score (10% weight) - STRICT: Only parsed numeric values
        hostel_capacity = (
            data.get("hostel_capacity_num") or
            (parse_numeric(data.get("hostel_capacity")) if isinstance(data.get("hostel_capacity"), (str, int, float)) else None) or
            0
        )
        required_hostel = student_count * 0.4  # 40% of students need hostel
        hostel_score = min(1.0, hostel_capacity / required_hostel) if required_hostel > 0 else 0.0
        
        # Weighted infrastructure score with updated weights
        infra_score = 100 * (
            0.40 * area_score +
            0.25 * classroom_score +
            0.15 * library_score +
            0.10 * digital_library_score +
            0.10 * hostel_score
        )
        
        return round(infra_score, 2)
    
    def calculate_placement_index(self, data: Dict[str, Any], mode: str) -> Optional[float]:
        """
        Calculate Placement Index (0-100) or None if required fields missing
        Formula:
        - placement_index = (students_placed / students_eligible) * 100
        """
        # STRICT: Prefer normalized placement_rate_num if present
        placement_rate = (
            data.get("placement_rate_num") or
            (parse_numeric(data.get("placement_percentage")) if isinstance(data.get("placement_percentage"), (str, int, float)) else None) or
            (parse_numeric(data.get("placement_rate")) if isinstance(data.get("placement_rate"), (str, int, float)) else None)
        )
        
        # If placement_rate not available, calculate from students_placed / students_eligible
        # STRICT: Only use parsed numeric values
        if placement_rate is None:
            students_placed = (
                data.get("students_placed_num") or
                data.get("total_placements_num") or
                data.get("placed_students_num") or
                (parse_numeric(data.get("students_placed")) if isinstance(data.get("students_placed"), (str, int, float)) else None) or
                (parse_numeric(data.get("total_placements")) if isinstance(data.get("total_placements"), (str, int, float)) else None) or
                (parse_numeric(data.get("placement_count")) if isinstance(data.get("placement_count"), (str, int, float)) else None)
            )
            
            students_eligible = (
                data.get("students_eligible_num") or
                data.get("student_count_num") or
                data.get("total_students_num") or
                data.get("total_intake_num") or
                (parse_numeric(data.get("students_eligible")) if isinstance(data.get("students_eligible"), (str, int, float)) else None) or
                (parse_numeric(data.get("total_students")) if isinstance(data.get("total_students"), (str, int, float)) else None) or
                (parse_numeric(data.get("student_count")) if isinstance(data.get("student_count"), (str, int, float)) else None) or
                (parse_numeric(data.get("total_intake")) if isinstance(data.get("total_intake"), (str, int, float)) else None) or
                (parse_numeric(data.get("admitted_students")) if isinstance(data.get("admitted_students"), (str, int, float)) else None)
            )
            
            # Return None if required fields missing
            if students_placed is None or students_eligible is None:
                return None
            
            if students_eligible == 0:
                return None
            
            placement_rate = (students_placed / students_eligible) * 100
        
        # Cap at 100
        return min(placement_rate, 100.0)
    
    def calculate_lab_compliance_index(self, data: Dict[str, Any], mode: str) -> Optional[float]:
        """
        Calculate Lab Compliance Index (0-100) or None if required fields missing
        Formula:
        - lab_compliance = (available_labs / required_labs) * 100
        """
        # STRICT: Prefer _num field - check all possible field names including AICTE schema
        # Only use parsed numeric values, never raw strings
        available_labs = (
            data.get("total_labs_num") or  # AICTE schema (preferred)
            data.get("lab_count_num") or
            data.get("labs_num") or
            data.get("laboratories_num") or
            (parse_numeric(data.get("total_labs")) if isinstance(data.get("total_labs"), (str, int, float)) else None) or
            (parse_numeric(data.get("lab_count")) if isinstance(data.get("lab_count"), (str, int, float)) else None) or
            (parse_numeric(data.get("labs")) if isinstance(data.get("labs"), (str, int, float)) else None) or
            (parse_numeric(data.get("laboratories")) if isinstance(data.get("laboratories"), (str, int, float)) else None)
        )
        
        # Return None if available_labs is missing (required field)
        if available_labs is None:
            return None
        
        required_labs = (data.get("required_labs_num") or
                        parse_numeric(data.get("required_labs")))
        
        # If required_labs not specified, estimate based on student count
        if required_labs is None:
            student_count = (data.get("student_count_num") or
                           data.get("total_intake_num") or
                           parse_numeric(data.get("total_students")) or
                           parse_numeric(data.get("student_count")) or
                           parse_numeric(data.get("total_intake")) or
                           parse_numeric(data.get("admitted_students")))
            if student_count and student_count > 0:
                required_labs = max(5, student_count // 50)  # At least 1 lab per 50 students, minimum 5
            else:
                required_labs = 5  # Default minimum
        
        if required_labs == 0:
            return None
        
        lab_compliance = (available_labs / required_labs) * 100
        
        # Cap at 100
        return min(lab_compliance, 100.0)
