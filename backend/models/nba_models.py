"""
NBA Mode Database Models
Following official NBA OBE methodology with course-level granularity

STRICT RULES:
- No dummy/fallback values
- Missing data → NULL
- Every score MUST link to evidence
- ATR mandatory for renewal batches
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


# ============ ENUMS ============

class POType(enum.Enum):
    """Standard 12 Program Outcomes as per NBA"""
    PO1 = "Engineering Knowledge"
    PO2 = "Problem Analysis"
    PO3 = "Design/Development of Solutions"
    PO4 = "Conduct Investigations of Complex Problems"
    PO5 = "Modern Tool Usage"
    PO6 = "The Engineer and Society"
    PO7 = "Environment and Sustainability"
    PO8 = "Ethics"
    PO9 = "Individual and Team Work"
    PO10 = "Communication"
    PO11 = "Project Management and Finance"
    PO12 = "Life-long Learning"


class AttainmentStatus(enum.Enum):
    """NBA Attainment Status Levels"""
    ATTAINED = "Attained"
    PARTIALLY_ATTAINED = "Partially Attained"
    NOT_ATTAINED = "Not Attained"
    INSUFFICIENT_EVIDENCE = "Insufficient Evidence"


class NBADocumentType(enum.Enum):
    """NBA-specific document types"""
    COURSE_LIST = "course_list"
    CO_DEFINITION = "co_definition"
    CO_PO_MAPPING = "co_po_mapping"
    CO_PSO_MAPPING = "co_pso_mapping"
    STUDENT_DATA = "student_data"
    ATTAINMENT_TARGET = "attainment_target"
    ATR = "atr"  # Action Taken Report
    IMPROVEMENT_ACTION = "improvement_action"
    ALUMNI_SURVEY = "alumni_survey"
    EMPLOYER_FEEDBACK = "employer_feedback"
    PLACEMENT_DATA = "placement_data"


# ============ NBA MODELS ============
# These will be added to the main database module

def create_nba_models(Base):
    """
    Factory function to create NBA models with the given SQLAlchemy Base.
    This allows integration with the existing database setup.
    """
    
    class Course(Base):
        """
        Course Model (CRITICAL for NBA)
        NBA evaluates course-wise, not just program-wise.
        """
        __tablename__ = "nba_courses"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), ForeignKey("batches.batch_id"), nullable=False)
        course_code = Column(String(20), nullable=False)
        course_name = Column(String(255), nullable=False)
        semester = Column(Integer, nullable=False)
        credits = Column(Integer, nullable=False)
        department = Column(String(100))
        academic_year = Column(String(20))
        created_at = Column(DateTime, default=datetime.utcnow)
        
        # Relationships
        course_outcomes = relationship("CourseOutcome", back_populates="course")
        
        def __repr__(self):
            return f"<Course {self.course_code}: {self.course_name}>"
    
    
    class CourseOutcome(Base):
        """
        Course Outcome (CO) Definition
        MANDATORY: Must be linked to a Course
        """
        __tablename__ = "nba_course_outcomes"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        course_id = Column(Integer, ForeignKey("nba_courses.id"), nullable=False)  # MANDATORY
        batch_id = Column(String(36), nullable=False)
        co_id = Column(String(10), nullable=False)  # CO1, CO2, etc.
        statement = Column(Text, nullable=False)  # CO statement text
        bloom_level = Column(String(50))  # Bloom's taxonomy level
        evidence_doc_id = Column(String(36))  # Link to evidence document
        evidence_page = Column(Integer)  # Page number in evidence
        created_at = Column(DateTime, default=datetime.utcnow)
        
        # Relationships
        course = relationship("Course", back_populates="course_outcomes")
        po_mappings = relationship("COPOMapping", back_populates="course_outcome")
        pso_mappings = relationship("COPSOMapping", back_populates="course_outcome")
        attainment_data = relationship("COAttainmentData", back_populates="course_outcome")
        
        def __repr__(self):
            return f"<CO {self.co_id}: {self.statement[:50]}...>"
    
    
    class AttainmentTarget(Base):
        """
        Attainment Target (MANDATORY)
        NBA requires defined attainment targets with evidence.
        Hardcoded thresholds without evidence → INVALID
        """
        __tablename__ = "nba_attainment_targets"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), ForeignKey("batches.batch_id"), nullable=False)
        target_percent = Column(Float, nullable=False)  # e.g., 60.0
        approved_by = Column(String(255))  # BOS/Academic Council
        academic_year = Column(String(20), nullable=False)
        evidence_doc_id = Column(String(36))  # MANDATORY for valid target
        evidence_page = Column(Integer)
        created_at = Column(DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f"<AttainmentTarget {self.target_percent}% for {self.academic_year}>"
    
    
    class COPOMapping(Base):
        """
        CO to PO Mapping
        Mapping strength: 1 (Low), 2 (Medium), 3 (High)
        Blank = no mapping
        """
        __tablename__ = "nba_co_po_mappings"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        co_id = Column(Integer, ForeignKey("nba_course_outcomes.id"), nullable=False)
        po_id = Column(String(5), nullable=False)  # PO1, PO2, ..., PO12
        mapping_level = Column(Integer, nullable=False)  # 1, 2, or 3 ONLY
        evidence_doc_id = Column(String(36))
        created_at = Column(DateTime, default=datetime.utcnow)
        
        # Relationships
        course_outcome = relationship("CourseOutcome", back_populates="po_mappings")
        
        def __repr__(self):
            return f"<Mapping CO{self.co_id} → {self.po_id} (Level {self.mapping_level})>"
    
    
    class COPSOMapping(Base):
        """
        CO to PSO Mapping
        Mapping strength: 1, 2, or 3
        """
        __tablename__ = "nba_co_pso_mappings"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        co_id = Column(Integer, ForeignKey("nba_course_outcomes.id"), nullable=False)
        pso_id = Column(String(5), nullable=False)  # PSO1, PSO2
        mapping_level = Column(Integer, nullable=False)  # 1, 2, or 3 ONLY
        evidence_doc_id = Column(String(36))
        created_at = Column(DateTime, default=datetime.utcnow)
        
        # Relationships
        course_outcome = relationship("CourseOutcome", back_populates="pso_mappings")
    
    
    class COAttainmentData(Base):
        """
        CO Attainment from Student Performance (Direct Assessment)
        CO_Attainment = % students ≥ approved_target
        NULL if no student data
        """
        __tablename__ = "nba_co_attainment"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        co_id = Column(Integer, ForeignKey("nba_course_outcomes.id"), nullable=False)
        batch_id = Column(String(36), nullable=False)
        total_students = Column(Integer)  # NULL if missing
        students_above_threshold = Column(Integer)  # NULL if missing
        threshold_percent = Column(Float)  # From AttainmentTarget
        attainment_percent = Column(Float)  # Calculated, NULL if cannot compute
        evidence_doc_id = Column(String(36))  # MANDATORY for valid attainment
        evidence_page = Column(Integer)
        academic_year = Column(String(20))
        created_at = Column(DateTime, default=datetime.utcnow)
        
        # Relationships
        course_outcome = relationship("CourseOutcome", back_populates="attainment_data")
        
        def calculate_attainment(self) -> float:
            """
            Calculate CO attainment percentage.
            Returns NULL if required data is missing.
            """
            if self.total_students is None or self.total_students == 0:
                return None
            if self.students_above_threshold is None:
                return None
            return (self.students_above_threshold / self.total_students) * 100
    
    
    class POAttainment(Base):
        """
        PO Attainment Result
        Combines Direct (from CO) and Indirect (from surveys) assessment.
        Final = 0.8 × Direct + 0.2 × Indirect (configurable weights)
        """
        __tablename__ = "nba_po_attainment"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), ForeignKey("batches.batch_id"), nullable=False)
        po_id = Column(String(5), nullable=False)  # PO1 - PO12
        po_name = Column(String(255))  # Full name from POType enum
        
        # Direct assessment (from CO attainment)
        direct_attainment = Column(Float)  # NULL if cannot compute
        direct_weight = Column(Float, default=0.8)  # 80% default
        
        # Indirect assessment (from surveys)
        indirect_attainment = Column(Float)  # NULL if no indirect data
        indirect_weight = Column(Float, default=0.2)  # 20% default
        
        # Final combined attainment
        final_attainment = Column(Float)  # NULL if insufficient data
        status = Column(String(50))  # Attained/Partially/Not/Insufficient
        
        # Evidence
        formula_used = Column(Text)
        evidence_doc_ids = Column(Text)  # JSON list of doc IDs
        contributing_cos = Column(Text)  # JSON list of contributing COs
        
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    
    class PSOAttainment(Base):
        """
        PSO (Program Specific Outcome) Attainment
        Similar structure to POAttainment
        """
        __tablename__ = "nba_pso_attainment"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), ForeignKey("batches.batch_id"), nullable=False)
        pso_id = Column(String(5), nullable=False)  # PSO1, PSO2
        pso_name = Column(String(255))
        
        direct_attainment = Column(Float)
        indirect_attainment = Column(Float)
        final_attainment = Column(Float)
        status = Column(String(50))
        
        formula_used = Column(Text)
        evidence_doc_ids = Column(Text)
        contributing_cos = Column(Text)
        
        created_at = Column(DateTime, default=datetime.utcnow)
    
    
    class PEOAttainment(Base):
        """
        PEO (Program Educational Objective) Attainment
        Computed using INDIRECT assessment only:
        - Alumni feedback
        - Employer feedback
        - Placement indicators
        """
        __tablename__ = "nba_peo_attainment"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), ForeignKey("batches.batch_id"), nullable=False)
        peo_id = Column(String(5), nullable=False)  # PEO1, PEO2, PEO3
        peo_statement = Column(Text)
        
        source_type = Column(String(50))  # alumni/employer/placement
        attainment_value = Column(Float)  # NULL if no indirect data
        status = Column(String(50))
        
        evidence_doc_id = Column(String(36))
        evidence_summary = Column(Text)
        
        created_at = Column(DateTime, default=datetime.utcnow)
    
    
    class ImprovementAction(Base):
        """
        Continuous Improvement Tracking (MANDATORY for NBA)
        Links low PO → improvement action with evidence
        """
        __tablename__ = "nba_improvement_actions"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), ForeignKey("batches.batch_id"), nullable=False)
        po_id = Column(String(5), nullable=False)  # Which PO this addresses
        
        issue_identified = Column(Text, nullable=False)
        action_taken = Column(Text, nullable=False)
        academic_year = Column(String(20), nullable=False)
        outcome_observed = Column(Text)  # Result of the action
        
        evidence_doc_id = Column(String(36))  # ATR document
        evidence_page = Column(Integer)
        
        created_at = Column(DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f"<Improvement {self.po_id}: {self.issue_identified[:50]}...>"
    
    
    class IndirectAssessment(Base):
        """
        Indirect Assessment Data
        - Alumni surveys
        - Employer feedback
        - Exit surveys
        """
        __tablename__ = "nba_indirect_assessments"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), ForeignKey("batches.batch_id"), nullable=False)
        assessment_type = Column(String(50), nullable=False)  # alumni/employer/exit
        
        # Per-PO indirect scores
        po_id = Column(String(5))
        score = Column(Float)  # NULL if not surveyed
        total_responses = Column(Integer)
        
        evidence_doc_id = Column(String(36))
        survey_year = Column(String(20))
        
        created_at = Column(DateTime, default=datetime.utcnow)
    
    
    class NBABatchMeta(Base):
        """
        NBA-specific batch metadata
        Tracks renewal status, ATR presence, validation state
        """
        __tablename__ = "nba_batch_meta"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), ForeignKey("batches.batch_id"), unique=True, nullable=False)
        
        # Renewal tracking
        is_renewal = Column(Boolean, default=False)
        previous_batch_id = Column(String(36))  # Link to previous accreditation
        
        # ATR status (MANDATORY for renewal)
        has_atr = Column(Boolean, default=False)
        atr_doc_id = Column(String(36))
        
        # Attainment weights (configurable)
        direct_weight = Column(Float, default=0.8)
        indirect_weight = Column(Float, default=0.2)
        
        # Validation state
        has_courses = Column(Boolean, default=False)
        has_co_definitions = Column(Boolean, default=False)
        has_mappings = Column(Boolean, default=False)
        has_student_data = Column(Boolean, default=False)
        has_targets = Column(Boolean, default=False)
        
        # Invalid reason (if applicable)
        is_valid = Column(Boolean, default=True)
        invalid_reason = Column(Text)
        
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    
    # Return all models as a dictionary
    return {
        'Course': Course,
        'CourseOutcome': CourseOutcome,
        'AttainmentTarget': AttainmentTarget,
        'COPOMapping': COPOMapping,
        'COPSOMapping': COPSOMapping,
        'COAttainmentData': COAttainmentData,
        'POAttainment': POAttainment,
        'PSOAttainment': PSOAttainment,
        'PEOAttainment': PEOAttainment,
        'ImprovementAction': ImprovementAction,
        'IndirectAssessment': IndirectAssessment,
        'NBABatchMeta': NBABatchMeta,
    }


# Standard PO definitions for reference
NBA_PROGRAM_OUTCOMES = {
    "PO1": "Engineering Knowledge",
    "PO2": "Problem Analysis",
    "PO3": "Design/Development of Solutions",
    "PO4": "Conduct Investigations of Complex Problems",
    "PO5": "Modern Tool Usage",
    "PO6": "The Engineer and Society",
    "PO7": "Environment and Sustainability",
    "PO8": "Ethics",
    "PO9": "Individual and Team Work",
    "PO10": "Communication",
    "PO11": "Project Management and Finance",
    "PO12": "Life-long Learning",
}

NBA_PSO_DEFAULTS = {
    "PSO1": "Mathematical and Algorithmic Foundations",
    "PSO2": "Open-Source Tool Proficiency",
}
