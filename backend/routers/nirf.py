"""
NIRF Mode API Router
Endpoints for NIRF ranking evaluation (5 Parameters: TLR, RP, GO, OI, PR)

STRICT RULES:
- PR computed ONLY if perception survey uploaded
- Evidence required for every parameter
- No estimated values
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Optional, List
from sqlalchemy.orm import Session
import json
import logging

from config.database import get_db
from services.nirf_calculation_engine import NIRFCalculationEngine, get_nirf_parameter_info
from middleware.auth_middleware import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# NIRF Parameters Info
NIRF_PARAMS = {
    "TLR": {"name": "Teaching, Learning and Resources", "weight": 100},
    "RP": {"name": "Research and Professional Practice", "weight": 100},
    "GO": {"name": "Graduation Outcomes", "weight": 100},
    "OI": {"name": "Outreach and Inclusivity", "weight": 100},
    "PR": {"name": "Perception", "weight": 100, "requires_survey": True},
}


# ============ BATCH SETUP ============

@router.post("/{batch_id}/initialize")
async def initialize_nirf_batch(
    batch_id: str,
    institution_type: str = "Engineering",
    ranking_year: int = 2024,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Initialize NIRF mode for a batch.
    """
    return {
        "batch_id": batch_id,
        "mode": "nirf",
        "institution_type": institution_type,
        "ranking_year": ranking_year,
        "message": "NIRF mode initialized. Upload parameter data.",
        "parameters": get_nirf_parameter_info()
    }


@router.get("/{batch_id}/status")
async def get_nirf_batch_status(
    batch_id: str,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """Get NIRF batch validation status."""
    return {
        "batch_id": batch_id,
        "is_valid": True,
        "has_tlr_data": False,
        "has_rp_data": False,
        "has_go_data": False,
        "has_oi_data": False,
        "has_pr_survey": False,
        "completeness_percent": 0
    }


# ============ PARAMETER UPLOADS ============

@router.post("/{batch_id}/tlr")
async def upload_tlr_data(
    batch_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """Upload TLR (Teaching, Learning and Resources) data."""
    return {
        "batch_id": batch_id,
        "parameter": "TLR",
        "message": "TLR data uploaded successfully"
    }


@router.post("/{batch_id}/rp")
async def upload_rp_data(
    batch_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """Upload RP (Research and Professional Practice) data."""
    return {
        "batch_id": batch_id,
        "parameter": "RP",
        "message": "RP data uploaded successfully"
    }


@router.post("/{batch_id}/go")
async def upload_go_data(
    batch_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """Upload GO (Graduation Outcomes) data."""
    return {
        "batch_id": batch_id,
        "parameter": "GO",
        "message": "GO data uploaded successfully"
    }


@router.post("/{batch_id}/oi")
async def upload_oi_data(
    batch_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """Upload OI (Outreach and Inclusivity) data."""
    return {
        "batch_id": batch_id,
        "parameter": "OI",
        "message": "OI data uploaded successfully"
    }


@router.post("/{batch_id}/perception-survey")
async def upload_perception_survey(
    batch_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Upload Perception Survey data.
    CRITICAL: PR score is ONLY computed if this is provided.
    """
    if not file.filename.endswith(('.xlsx', '.csv', '.pdf')):
        raise HTTPException(400, "Only Excel, CSV, or PDF files accepted")
    
    return {
        "batch_id": batch_id,
        "parameter": "PR",
        "message": "Perception survey uploaded. PR score will be computed."
    }


# ============ DASHBOARD ============

@router.get("/{batch_id}/dashboard")
async def get_nirf_dashboard(
    batch_id: str,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Get NIRF dashboard data.
    Shows 5 parameter scores and overall ranking score.
    """
    engine = NIRFCalculationEngine(db)
    
    # Build parameters response
    parameters = []
    for p_id, p_info in NIRF_PARAMS.items():
        param_data = {
            "param_id": p_id,
            "name": p_info["name"],
            "weight": p_info["weight"],
            "score": None,  # NULL if not computed
            "sub_scores": {},
            "status": "Not Computed",
            "has_evidence": False
        }
        
        # Special note for PR
        if p_id == "PR":
            param_data["note"] = "Requires perception survey upload"
        
        parameters.append(param_data)
    
    return {
        "batch_id": batch_id,
        "mode": "nirf",
        "parameters": parameters,
        "overall_score": None,
        "missing_params": list(NIRF_PARAMS.keys()),
        "formula_used": None,
        "has_perception_survey": False
    }


@router.get("/{batch_id}/parameter/{param_id}")
async def get_parameter_details(
    batch_id: str,
    param_id: str,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """Drill-down view for a specific parameter."""
    if param_id not in NIRF_PARAMS:
        raise HTTPException(400, f"Invalid parameter: {param_id}. Valid: TLR, RP, GO, OI, PR")
    
    # Sub-parameter definitions
    sub_params = {
        "TLR": ["SS (Student Strength)", "FSR (Faculty-Student Ratio)", "FQE (Faculty Qualification)", "FRU (Financial Resources)"],
        "RP": ["PU (Publications)", "QP (Quality of Publications)", "IPR (Patents)", "FPPP (Funded Projects)"],
        "GO": ["GPH (Higher Studies)", "Placement Rate", "MS (Median Salary)"],
        "OI": ["RD (Regional Diversity)", "WD (Women Diversity)", "ESCS (Economically Challenged)"],
        "PR": ["Peer Perception", "Employer Perception", "Academic Perception"],
    }
    
    response = {
        "batch_id": batch_id,
        "param_id": param_id,
        "name": NIRF_PARAMS[param_id]["name"],
        "weight": NIRF_PARAMS[param_id]["weight"],
        "score": None,
        "sub_parameters": sub_params.get(param_id, []),
        "sub_scores": {},
        "evidence_snippets": [],
        "formula_used": f"{param_id} = Weighted average of sub-parameters"
    }
    
    if param_id == "PR":
        response["note"] = "PR requires perception survey. If not uploaded, PR = NULL."
    
    return response


# ============ RANKING INFO ============

@router.get("/parameters-info")
async def get_parameters_info():
    """Get NIRF parameters info with sub-parameters."""
    return {
        "parameters": get_nirf_parameter_info(),
        "total_marks": 500,
        "note": "PR (Perception) is only computed if perception survey is uploaded"
    }
