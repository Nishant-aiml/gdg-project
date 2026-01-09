"""
NBA Mode Pydantic Schemas
Request/Response models for NBA API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============ ENUMS ============

class AttainmentStatusEnum(str, Enum):
    ATTAINED = "Attained"
    PARTIALLY_ATTAINED = "Partially Attained"
    NOT_ATTAINED = "Not Attained"
    INSUFFICIENT_EVIDENCE = "Insufficient Evidence"


class NBADocTypeEnum(str, Enum):
    COURSE_LIST = "course_list"
    CO_DEFINITION = "co_definition"
    MAPPING_TABLE = "mapping_table"
    STUDENT_DATA = "student_data"
    ATTAINMENT_TARGET = "attainment_target"
    ATR = "atr"
    INDIRECT_ASSESSMENT = "indirect_assessment"


# ============ REQUEST SCHEMAS ============

class CourseCreate(BaseModel):
    """Create a new course"""
    course_code: str = Field(..., example="CS101")
    course_name: str = Field(..., example="Programming Fundamentals")
    semester: int = Field(..., ge=1, le=8)
    credits: int = Field(..., ge=1, le=6)
    department: Optional[str] = None
    academic_year: Optional[str] = Field(None, example="2024-25")


class CourseOutcomeCreate(BaseModel):
    """Create a Course Outcome"""
    course_id: int
    co_id: str = Field(..., example="CO1")
    statement: str = Field(..., min_length=10)
    bloom_level: Optional[str] = None
    evidence_doc_id: Optional[str] = None
    evidence_page: Optional[int] = None


class MappingCreate(BaseModel):
    """Create CO-PO or CO-PSO mapping"""
    co_id: int
    target_id: str = Field(..., example="PO1")  # PO1-PO12 or PSO1-PSO2
    mapping_level: int = Field(..., ge=1, le=3)
    evidence_doc_id: Optional[str] = None


class AttainmentTargetCreate(BaseModel):
    """Create attainment target"""
    target_percent: float = Field(..., ge=0, le=100, example=60.0)
    approved_by: Optional[str] = Field(None, example="Board of Studies")
    academic_year: str = Field(..., example="2024-25")
    evidence_doc_id: Optional[str] = None


class StudentDataUpload(BaseModel):
    """Student performance data for CO attainment"""
    co_id: int
    total_students: int = Field(..., ge=1)
    students_above_threshold: int = Field(..., ge=0)
    academic_year: Optional[str] = None
    evidence_doc_id: Optional[str] = None


class ImprovementActionCreate(BaseModel):
    """Create improvement action for a PO"""
    po_id: str = Field(..., example="PO3")
    issue_identified: str
    action_taken: str
    academic_year: str
    outcome_observed: Optional[str] = None
    evidence_doc_id: Optional[str] = None


class IndirectAssessmentCreate(BaseModel):
    """Create indirect assessment data"""
    assessment_type: str = Field(..., example="alumni_survey")
    po_id: str
    score: float = Field(..., ge=0, le=100)
    total_responses: Optional[int] = None
    evidence_doc_id: Optional[str] = None
    survey_year: Optional[str] = None


# ============ RESPONSE SCHEMAS ============

class CourseResponse(BaseModel):
    id: int
    batch_id: str
    course_code: str
    course_name: str
    semester: int
    credits: int
    department: Optional[str]
    academic_year: Optional[str]
    co_count: Optional[int] = 0

    class Config:
        from_attributes = True


class CourseOutcomeResponse(BaseModel):
    id: int
    course_id: int
    co_id: str
    statement: str
    bloom_level: Optional[str]
    has_evidence: bool = False
    attainment_percent: Optional[float] = None

    class Config:
        from_attributes = True


class ContributingCO(BaseModel):
    """CO contribution to a PO"""
    co_id: str
    course_name: str
    attainment: float
    mapping_level: int
    weighted_contribution: float


class POAttainmentResponse(BaseModel):
    """PO Attainment result"""
    po_id: str
    po_name: str
    direct_attainment: Optional[float] = None
    indirect_attainment: Optional[float] = None
    final_attainment: Optional[float] = None
    status: AttainmentStatusEnum
    formula_used: str
    contributing_cos: List[ContributingCO] = []
    has_evidence: bool = False


class PSOAttainmentResponse(BaseModel):
    """PSO Attainment result"""
    pso_id: str
    pso_name: str
    direct_attainment: Optional[float] = None
    indirect_attainment: Optional[float] = None
    final_attainment: Optional[float] = None
    status: AttainmentStatusEnum


class ImprovementActionResponse(BaseModel):
    """Improvement action for a PO"""
    id: int
    po_id: str
    issue_identified: str
    action_taken: str
    academic_year: str
    outcome_observed: Optional[str]
    has_evidence: bool = False


class GapAnalysisItem(BaseModel):
    """Gap analysis for a low-attainment PO"""
    po_id: str
    po_name: str
    current_attainment: Optional[float]
    target: float
    gap: Optional[float]
    root_cause_cos: List[str] = []
    improvement_action: Optional[ImprovementActionResponse] = None


class NBAUploadStep(BaseModel):
    """Upload wizard step"""
    step: int
    name: str
    key: str
    required: bool
    required_for_renewal: bool = False
    description: str
    completed: bool = False


class NBABatchStatusResponse(BaseModel):
    """NBA batch status and validation"""
    batch_id: str
    is_valid: bool
    invalid_reason: Optional[str] = None
    is_renewal: bool = False
    has_atr: bool = False
    direct_weight: float = 0.8
    indirect_weight: float = 0.2
    upload_progress: List[NBAUploadStep] = []
    completeness_percent: float = 0


class NBADashboardResponse(BaseModel):
    """NBA Dashboard data"""
    batch_id: str
    batch_status: NBABatchStatusResponse
    
    # Attainment tables
    po_attainments: List[POAttainmentResponse] = []
    pso_attainments: List[PSOAttainmentResponse] = []
    
    # Summary stats
    total_courses: int = 0
    total_cos: int = 0
    attained_pos: int = 0
    partially_attained_pos: int = 0
    not_attained_pos: int = 0
    
    # Target vs achieved
    attainment_target: Optional[float] = None
    average_po_attainment: Optional[float] = None
    
    # Gap analysis
    gap_analysis: List[GapAnalysisItem] = []
    
    # Improvement actions
    improvement_actions: List[ImprovementActionResponse] = []


class PODrilldownResponse(BaseModel):
    """Detailed PO drill-down view"""
    po_id: str
    po_name: str
    
    # Attainment details
    direct_attainment: Optional[float]
    indirect_attainment: Optional[float]
    final_attainment: Optional[float]
    status: AttainmentStatusEnum
    
    # Formula breakdown
    formula_used: str
    direct_weight: float
    indirect_weight: float
    
    # Contributing COs with course context
    contributing_cos: List[ContributingCO]
    
    # Evidence
    evidence_snippets: List[Dict[str, Any]] = []
    
    # Improvement action (if low attainment)
    improvement_action: Optional[ImprovementActionResponse] = None


# ============ CO-PO HEATMAP ============

class HeatmapCell(BaseModel):
    """Single cell in CO-PO heatmap"""
    co_id: str
    po_id: str
    mapping_level: Optional[int] = None  # 1, 2, 3, or None


class COPOHeatmapResponse(BaseModel):
    """CO-PO mapping heatmap data"""
    courses: List[str]
    cos: List[str]  # CO IDs
    pos: List[str]  # PO1-PO12
    cells: List[HeatmapCell]
