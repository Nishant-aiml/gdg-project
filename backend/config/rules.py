"""
Mode-specific rules and configurations for AICTE, NBA, NAAC, and NIRF
"""

from typing import Dict, List

# DEPRECATED: Document types removed
# System now uses 10 Information Blocks only
# See config/information_blocks.py for block definitions

# KPI definitions and formulas - OFFICIAL ACCREDITATION RULES
# Each mode has isolated formulas - NO cross-mode reuse
KPI_FORMULAS = {
    "aicte": {
        "fsr_score": {
            "name": "FSR Score",
            "formula": "calculate_fsr_score",
            "weight": 0.25,
            "official_formula": "FSR = Total Students / Total Faculty",
            "scoring_rule": "FSR ≤ 15 → 100, 15 < FSR ≤ 20 → linear (100→60), FSR > 20 → penalty"
        },
        "infrastructure_score": {
            "name": "Infrastructure Score",
            "formula": "calculate_infrastructure_score",
            "weight": 0.25,
            "official_formula": "0.40×Area + 0.25×Classrooms + 0.15×Library + 0.10×Digital + 0.10×Hostel"
        },
        "placement_index": {
            "name": "Placement Index",
            "formula": "calculate_placement_index",
            "weight": 0.25,
            "official_formula": "Placement % = (Placed / Eligible) × 100"
        },
        "lab_compliance_index": {
            "name": "Lab Compliance Index",
            "formula": "calculate_lab_compliance_index",
            "weight": 0.25,
            "official_formula": "Lab Compliance = (Available Labs / Required Labs) × 100"
        }
    },
    "nba": {
        "peos_psos": {
            "name": "PEOs & PSOs Criterion",
            "formula": "calculate_nba_peos_psos",
            "weight": 0.20
        },
        "faculty_quality": {
            "name": "Faculty Quality Criterion",
            "formula": "calculate_nba_faculty_quality",
            "weight": 0.20
        },
        "student_performance": {
            "name": "Student Performance Criterion",
            "formula": "calculate_nba_student_performance",
            "weight": 0.20
        },
        "continuous_improvement": {
            "name": "Continuous Improvement Criterion",
            "formula": "calculate_nba_continuous_improvement",
            "weight": 0.20
        },
        "co_po_mapping": {
            "name": "CO-PO Mapping Criterion",
            "formula": "calculate_nba_co_po_mapping",
            "weight": 0.20
        }
    },
    "naac": {
        "criterion_1": {
            "name": "NAAC Criterion 1 (Curricular Aspects)",
            "formula": "calculate_naac_criterion_1",
            "weight": 0.15
        },
        "criterion_2": {
            "name": "NAAC Criterion 2 (Teaching-Learning & Evaluation)",
            "formula": "calculate_naac_criterion_2",
            "weight": 0.15
        },
        "criterion_3": {
            "name": "NAAC Criterion 3 (Research, Innovations & Extension)",
            "formula": "calculate_naac_criterion_3",
            "weight": 0.15
        },
        "criterion_4": {
            "name": "NAAC Criterion 4 (Infrastructure & Learning Resources)",
            "formula": "calculate_naac_criterion_4",
            "weight": 0.15
        },
        "criterion_5": {
            "name": "NAAC Criterion 5 (Student Support & Progression)",
            "formula": "calculate_naac_criterion_5",
            "weight": 0.15
        },
        "criterion_6": {
            "name": "NAAC Criterion 6 (Governance, Leadership & Management)",
            "formula": "calculate_naac_criterion_6",
            "weight": 0.15
        },
        "criterion_7": {
            "name": "NAAC Criterion 7 (Institutional Values & Best Practices)",
            "formula": "calculate_naac_criterion_7",
            "weight": 0.10
        }
    },
    "nirf": {
        "tlr": {
            "name": "Teaching, Learning & Resources (TLR)",
            "formula": "calculate_nirf_tlr",
            "weight": 0.30
        },
        "rp": {
            "name": "Research & Professional Practice (RP)",
            "formula": "calculate_nirf_rp",
            "weight": 0.30
        },
        "go": {
            "name": "Graduation Outcomes (GO)",
            "formula": "calculate_nirf_go",
            "weight": 0.20
        },
        "oi": {
            "name": "Outreach & Inclusivity (OI)",
            "formula": "calculate_nirf_oi",
            "weight": 0.10
        },
        "pr": {
            "name": "Perception (PR)",
            "formula": "calculate_nirf_pr",
            "weight": 0.10
        }
    }
}

# Compliance rules
COMPLIANCE_RULES = {
    "aicte": [
        {
            "rule_id": "expired_fire_noc",
            "severity": "high",
            "check": "check_fire_noc_expiry"
        },
        {
            "rule_id": "missing_approvals",
            "severity": "high",
            "check": "check_missing_approvals"
        },
        {
            "rule_id": "low_fsr",
            "severity": "medium",
            "check": "check_fsr_ratio"
        },
        {
            "rule_id": "placement_issues",
            "severity": "medium",
            "check": "check_placement_data"
        }
    ]
}

# DEPRECATED: Document-based functions removed
# Use get_information_blocks() from config.information_blocks instead

def get_kpi_formulas(mode: str) -> Dict:
    """Get KPI formulas for mode"""
    return KPI_FORMULAS.get(mode.lower(), {})

def get_compliance_rules(mode: str) -> List[Dict]:
    """Get compliance rules for mode"""
    return COMPLIANCE_RULES.get(mode.lower(), [])

