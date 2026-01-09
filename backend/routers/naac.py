"""
NAAC Mode API Router
Endpoints for NAAC accreditation evaluation (7 Criteria: C1-C7)

STRICT RULES:
- Missing criterion → NULL overall
- Evidence required for every criterion
- No estimated values
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Optional, List
from sqlalchemy.orm import Session
import json
import logging

from config.database import get_db
from services.naac_calculation_engine import NAACCalculationEngine, get_naac_criterion_info
from middleware.auth_middleware import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# NAAC Criteria Info
NAAC_CRITERIA = {
    "C1": {"name": "Curricular Aspects", "weight": 150},
    "C2": {"name": "Teaching-Learning and Evaluation", "weight": 200},
    "C3": {"name": "Research, Innovations and Extension", "weight": 250},
    "C4": {"name": "Infrastructure and Learning Resources", "weight": 100},
    "C5": {"name": "Student Support and Progression", "weight": 100},
    "C6": {"name": "Governance, Leadership and Management", "weight": 100},
    "C7": {"name": "Institutional Values and Best Practices", "weight": 100},
}


# ============ BATCH SETUP ============

@router.post("/{batch_id}/initialize")
async def initialize_naac_batch(
    batch_id: str,
    institution_type: str = "Affiliated",
    cycle_number: int = 1,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Initialize NAAC mode for a batch.
    """
    return {
        "batch_id": batch_id,
        "mode": "naac",
        "institution_type": institution_type,
        "cycle_number": cycle_number,
        "message": "NAAC mode initialized. Upload SSR and criterion data.",
        "criteria": get_naac_criterion_info()
    }


@router.get("/{batch_id}/status")
async def get_naac_batch_status(
    batch_id: str,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """Get NAAC batch validation status."""
    return {
        "batch_id": batch_id,
        "is_valid": True,
        "has_ssr": False,
        "has_iqac_report": False,
        "criteria_status": {c: False for c in NAAC_CRITERIA.keys()},
        "completeness_percent": 0
    }


# ============ DOCUMENT UPLOADS ============

@router.post("/{batch_id}/ssr")
async def upload_ssr(
    batch_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """Upload Self-Study Report (SSR)."""
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(400, "Only PDF or Word files accepted")
    
    return {
        "batch_id": batch_id,
        "message": "SSR uploaded successfully"
    }


@router.post("/{batch_id}/iqac-report")
async def upload_iqac_report(
    batch_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """Upload IQAC Annual Report."""
    return {
        "batch_id": batch_id,
        "message": "IQAC report uploaded successfully"
    }


@router.post("/{batch_id}/criterion/{criterion_id}")
async def upload_criterion_data(
    batch_id: str,
    criterion_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """Upload data for a specific criterion (C1-C7)."""
    if criterion_id not in NAAC_CRITERIA:
        raise HTTPException(400, f"Invalid criterion: {criterion_id}. Valid: C1-C7")
    
    return {
        "batch_id": batch_id,
        "criterion_id": criterion_id,
        "message": f"{NAAC_CRITERIA[criterion_id]['name']} data uploaded"
    }


# ============ DASHBOARD ============

@router.get("/{batch_id}/dashboard")
async def get_naac_dashboard(
    batch_id: str,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Get NAAC dashboard data.
    Shows 7 criteria scores and overall CGPA/Grade.
    """
    engine = NAACCalculationEngine(db)
    
    # Build criteria response
    criteria = []
    for c_id, c_info in NAAC_CRITERIA.items():
        criteria.append({
            "criterion_id": c_id,
            "name": c_info["name"],
            "weight": c_info["weight"],
            "score": None,  # NULL if not computed
            "weighted_score": None,
            "status": "Not Computed",
            "has_evidence": False
        })
    
    return {
        "batch_id": batch_id,
        "mode": "naac",
        "criteria": criteria,
        "cgpa": None,
        "grade": "Not Computed",
        "is_accredited": False,
        "missing_criteria": list(NAAC_CRITERIA.keys()),
        "formula_used": None
    }


@router.get("/{batch_id}/criterion/{criterion_id}")
async def get_criterion_details(
    batch_id: str,
    criterion_id: str,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """Drill-down view for a specific criterion."""
    if criterion_id not in NAAC_CRITERIA:
        raise HTTPException(400, f"Invalid criterion: {criterion_id}")
    
    return {
        "batch_id": batch_id,
        "criterion_id": criterion_id,
        "name": NAAC_CRITERIA[criterion_id]["name"],
        "weight": NAAC_CRITERIA[criterion_id]["weight"],
        "score": None,
        "key_indicators": [],
        "qualitative_metrics": [],
        "evidence_snippets": [],
        "formula_used": f"C{criterion_id[1]} = Σ(KI_Score × KI_Weight) / Σ(KI_Weight)"
    }


# ============ GRADING ============

@router.get("/grading-scale")
async def get_grading_scale():
    """Get NAAC grading scale."""
    return {
        "grades": [
            {"grade": "A++", "cgpa_range": "3.51 - 4.00", "status": "Accredited"},
            {"grade": "A+", "cgpa_range": "3.26 - 3.50", "status": "Accredited"},
            {"grade": "A", "cgpa_range": "3.01 - 3.25", "status": "Accredited"},
            {"grade": "B++", "cgpa_range": "2.76 - 3.00", "status": "Accredited"},
            {"grade": "B+", "cgpa_range": "2.51 - 2.75", "status": "Accredited"},
            {"grade": "B", "cgpa_range": "2.01 - 2.50", "status": "Accredited"},
            {"grade": "C", "cgpa_range": "1.51 - 2.00", "status": "Accredited"},
            {"grade": "D", "cgpa_range": "≤ 1.50", "status": "Not Accredited"},
        ]
    }
