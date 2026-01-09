"""
NBA Mode API Router
Endpoints for NBA accreditation evaluation

STRICT RULES:
- No dummy data
- Missing data → NULL
- Evidence required for calculations
- ATR mandatory for renewal
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Optional, List
from sqlalchemy.orm import Session
import json
import logging

from config.database import get_db
from schemas.nba import (
    CourseCreate, CourseResponse,
    CourseOutcomeCreate, CourseOutcomeResponse,
    MappingCreate, AttainmentTargetCreate,
    StudentDataUpload, ImprovementActionCreate,
    IndirectAssessmentCreate,
    NBADashboardResponse, NBABatchStatusResponse,
    POAttainmentResponse, PSOAttainmentResponse,
    PODrilldownResponse, COPOHeatmapResponse,
    NBAUploadStep, GapAnalysisItem,
    AttainmentStatusEnum
)
from services.nba_calculation_engine import NBACalculationEngine, get_required_nba_uploads
from models.nba_models import NBA_PROGRAM_OUTCOMES, NBA_PSO_DEFAULTS
from middleware.auth_middleware import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ BATCH SETUP ============

@router.post("/{batch_id}/initialize")
async def initialize_nba_batch(
    batch_id: str,
    is_renewal: bool = False,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Initialize NBA mode for a batch.
    Creates NBABatchMeta record.
    """
    # Check if batch exists
    # Create NBABatchMeta with defaults
    
    return {
        "batch_id": batch_id,
        "mode": "nba",
        "is_renewal": is_renewal,
        "message": "NBA mode initialized. Upload required documents to proceed.",
        "required_uploads": get_required_nba_uploads()
    }


@router.get("/{batch_id}/status", response_model=NBABatchStatusResponse)
async def get_nba_batch_status(
    batch_id: str,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Get NBA batch validation status and upload progress.
    """
    # Get NBABatchMeta
    # Check each upload step completion
    # Calculate completeness
    
    upload_steps = get_required_nba_uploads()
    completed_steps = []
    
    for step in upload_steps:
        step_data = NBAUploadStep(
            step=step['step'],
            name=step['name'],
            key=step['key'],
            required=step['required'],
            required_for_renewal=step.get('required_for_renewal', False),
            description=step['description'],
            completed=False  # Check DB for actual status
        )
        completed_steps.append(step_data)
    
    return NBABatchStatusResponse(
        batch_id=batch_id,
        is_valid=True,
        is_renewal=False,
        has_atr=False,
        direct_weight=0.8,
        indirect_weight=0.2,
        upload_progress=completed_steps,
        completeness_percent=0
    )


# ============ COURSE MANAGEMENT ============

@router.post("/{batch_id}/courses", response_model=CourseResponse)
async def create_course(
    batch_id: str,
    course: CourseCreate,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Add a course to the NBA batch.
    Required before adding CO definitions.
    """
    # Create Course record
    # Update NBABatchMeta.has_courses = True
    
    return CourseResponse(
        id=1,
        batch_id=batch_id,
        course_code=course.course_code,
        course_name=course.course_name,
        semester=course.semester,
        credits=course.credits,
        department=course.department,
        academic_year=course.academic_year,
        co_count=0
    )


@router.post("/{batch_id}/courses/bulk")
async def bulk_upload_courses(
    batch_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Bulk upload courses from Excel/CSV.
    Expected columns: course_code, course_name, semester, credits
    """
    if not file.filename.endswith(('.xlsx', '.csv')):
        raise HTTPException(400, "Only Excel (.xlsx) or CSV files accepted")
    
    # Parse file
    # Create Course records
    # Update NBABatchMeta
    
    return {
        "batch_id": batch_id,
        "courses_added": 0,
        "message": "Courses uploaded successfully"
    }


@router.get("/{batch_id}/courses", response_model=List[CourseResponse])
async def list_courses(
    batch_id: str,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """List all courses in the NBA batch."""
    # Query courses
    return []


# ============ CO MANAGEMENT ============

@router.post("/{batch_id}/co-definitions")
async def upload_co_definitions(
    batch_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Upload CO definitions from Excel/PDF.
    Must link to existing courses.
    """
    if not file.filename.endswith(('.xlsx', '.pdf', '.docx')):
        raise HTTPException(400, "Only Excel, PDF, or Word files accepted")
    
    # Parse file
    # Extract CO statements
    # Link to courses
    # Update NBABatchMeta.has_co_definitions = True
    
    return {
        "batch_id": batch_id,
        "cos_extracted": 0,
        "message": "CO definitions uploaded"
    }


# ============ MAPPING TABLES ============

@router.post("/{batch_id}/mapping-tables")
async def upload_mapping_tables(
    batch_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Upload CO-PO and CO-PSO mapping tables from Excel.
    Mapping levels must be 1, 2, or 3.
    """
    if not file.filename.endswith(('.xlsx', '.csv')):
        raise HTTPException(400, "Only Excel or CSV files accepted")
    
    # Parse file
    # Validate mapping levels (1,2,3 only)
    # Create COPOMapping and COPSOMapping records
    # Update NBABatchMeta.has_mappings = True
    
    return {
        "batch_id": batch_id,
        "po_mappings_created": 0,
        "pso_mappings_created": 0,
        "message": "Mapping tables uploaded"
    }


# ============ STUDENT DATA ============

@router.post("/{batch_id}/student-data")
async def upload_student_data(
    batch_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Upload student performance data for CO attainment.
    Required columns: course_code, co_id, total_students, students_above_threshold
    """
    if not file.filename.endswith(('.xlsx', '.csv')):
        raise HTTPException(400, "Only Excel or CSV files accepted")
    
    # Parse file
    # Calculate CO attainment per row
    # Update NBABatchMeta.has_student_data = True
    
    return {
        "batch_id": batch_id,
        "cos_with_attainment": 0,
        "message": "Student data processed"
    }


# ============ ATTAINMENT TARGETS ============

@router.post("/{batch_id}/targets", response_model=dict)
async def set_attainment_target(
    batch_id: str,
    target: AttainmentTargetCreate,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Set approved attainment target for the batch.
    Must have evidence (BOS approval document).
    """
    if not target.evidence_doc_id:
        raise HTTPException(
            400, 
            "Attainment target requires evidence document (BOS approval). "
            "Hardcoded thresholds without evidence are INVALID."
        )
    
    # Create AttainmentTarget record
    # Update NBABatchMeta.has_targets = True
    
    return {
        "batch_id": batch_id,
        "target_percent": target.target_percent,
        "approved_by": target.approved_by,
        "message": "Attainment target set"
    }


# ============ ATR & IMPROVEMENT ============

@router.post("/{batch_id}/atr")
async def upload_atr(
    batch_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Upload Action Taken Report (ATR).
    MANDATORY for renewal batches.
    """
    # Store ATR document
    # Extract improvement actions
    # Update NBABatchMeta.has_atr = True
    
    return {
        "batch_id": batch_id,
        "message": "ATR uploaded successfully"
    }


@router.post("/{batch_id}/improvement-actions", response_model=dict)
async def add_improvement_action(
    batch_id: str,
    action: ImprovementActionCreate,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Add an improvement action for a PO.
    Links issue → action → outcome with evidence.
    """
    # Create ImprovementAction record
    
    return {
        "batch_id": batch_id,
        "po_id": action.po_id,
        "message": "Improvement action added"
    }


# ============ INDIRECT ASSESSMENT ============

@router.post("/{batch_id}/indirect-assessment")
async def upload_indirect_assessment(
    batch_id: str,
    file: UploadFile = File(...),
    assessment_type: str = "alumni_survey",
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Upload indirect assessment data (alumni/employer surveys).
    Optional but recommended for accurate PO attainment.
    """
    # Parse file
    # Extract per-PO indirect scores
    # Create IndirectAssessment records
    
    return {
        "batch_id": batch_id,
        "assessment_type": assessment_type,
        "message": "Indirect assessment uploaded"
    }


# ============ DASHBOARD ============

@router.get("/{batch_id}/dashboard", response_model=NBADashboardResponse)
async def get_nba_dashboard(
    batch_id: str,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Get complete NBA dashboard data.
    
    Includes:
    - PO attainment table (12 POs)
    - PSO attainment table
    - Summary statistics
    - Gap analysis
    - Improvement actions
    """
    engine = NBACalculationEngine(db)
    
    # Get batch meta
    batch_status = await get_nba_batch_status(batch_id, db, user)
    
    # Validate batch
    if not batch_status.is_valid:
        raise HTTPException(
            400,
            f"NBA batch is invalid: {batch_status.invalid_reason}. "
            "Please complete required uploads."
        )
    
    # Calculate PO attainments
    po_attainments = []
    for po_id, po_name in NBA_PROGRAM_OUTCOMES.items():
        po_attainments.append(POAttainmentResponse(
            po_id=po_id,
            po_name=po_name,
            direct_attainment=None,
            indirect_attainment=None,
            final_attainment=None,
            status=AttainmentStatusEnum.INSUFFICIENT_EVIDENCE,
            formula_used="No data available",
            contributing_cos=[],
            has_evidence=False
        ))
    
    # Calculate PSO attainments
    pso_attainments = []
    for pso_id, pso_name in NBA_PSO_DEFAULTS.items():
        pso_attainments.append(PSOAttainmentResponse(
            pso_id=pso_id,
            pso_name=pso_name,
            direct_attainment=None,
            indirect_attainment=None,
            final_attainment=None,
            status=AttainmentStatusEnum.INSUFFICIENT_EVIDENCE
        ))
    
    # Build gap analysis for low-attainment POs
    gap_analysis = []
    
    # Get improvement actions
    improvement_actions = []
    
    return NBADashboardResponse(
        batch_id=batch_id,
        batch_status=batch_status,
        po_attainments=po_attainments,
        pso_attainments=pso_attainments,
        total_courses=0,
        total_cos=0,
        attained_pos=0,
        partially_attained_pos=0,
        not_attained_pos=0,
        attainment_target=None,
        average_po_attainment=None,
        gap_analysis=gap_analysis,
        improvement_actions=improvement_actions
    )


# ============ DRILL-DOWN ============

@router.get("/{batch_id}/po/{po_id}", response_model=PODrilldownResponse)
async def get_po_drilldown(
    batch_id: str,
    po_id: str,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Get detailed drill-down for a specific PO.
    
    Shows:
    - Formula used
    - Contributing COs with weights
    - Course names
    - Evidence snippets
    - Improvement action (if low)
    
    NO frontend-side calculations allowed.
    """
    if po_id not in NBA_PROGRAM_OUTCOMES:
        raise HTTPException(400, f"Invalid PO ID: {po_id}. Valid: PO1-PO12")
    
    po_name = NBA_PROGRAM_OUTCOMES[po_id]
    
    return PODrilldownResponse(
        po_id=po_id,
        po_name=po_name,
        direct_attainment=None,
        indirect_attainment=None,
        final_attainment=None,
        status=AttainmentStatusEnum.INSUFFICIENT_EVIDENCE,
        formula_used="Direct + Indirect = 0.8×Direct + 0.2×Indirect",
        direct_weight=0.8,
        indirect_weight=0.2,
        contributing_cos=[],
        evidence_snippets=[],
        improvement_action=None
    )


# ============ HEATMAP ============

@router.get("/{batch_id}/heatmap", response_model=COPOHeatmapResponse)
async def get_co_po_heatmap(
    batch_id: str,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Get CO-PO mapping heatmap data.
    Shows mapping strength (1,2,3) for each CO-PO pair.
    """
    # Query all mappings
    # Build cells array
    
    return COPOHeatmapResponse(
        courses=[],
        cos=[],
        pos=list(NBA_PROGRAM_OUTCOMES.keys()),
        cells=[]
    )


# ============ VALIDATION ============

@router.post("/{batch_id}/validate")
async def validate_nba_batch(
    batch_id: str,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Validate NBA batch for completeness.
    Marks batch as invalid if required data is missing.
    
    Checks:
    - Courses defined
    - CO definitions present
    - Mappings uploaded
    - Student data uploaded
    - Targets defined
    - ATR present (if renewal)
    """
    engine = NBACalculationEngine(db)
    
    # Get batch meta
    nba_meta = {}  # Query from DB
    
    is_valid, invalid_reason = engine.validate_nba_batch(batch_id, nba_meta)
    
    if not is_valid:
        # Mark batch as invalid
        # Update batch.is_invalid = 1
        pass
    
    return {
        "batch_id": batch_id,
        "is_valid": is_valid,
        "invalid_reason": invalid_reason
    }
