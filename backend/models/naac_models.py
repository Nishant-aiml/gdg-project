"""
NAAC Mode Database Models
Implementing 7 Criteria (C1-C7) as per NAAC Handbook

STRICT RULES:
- No dummy data
- Missing criterion → NULL overall
- Evidence required for every criterion
- No cross-mode data reuse
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any
import enum


# ============ ENUMS ============

class NAACCriterionID(enum.Enum):
    """NAAC 7 Criteria with Official Weights"""
    C1 = "Curricular Aspects"
    C2 = "Teaching-Learning and Evaluation"
    C3 = "Research, Innovations and Extension"
    C4 = "Infrastructure and Learning Resources"
    C5 = "Student Support and Progression"
    C6 = "Governance, Leadership and Management"
    C7 = "Institutional Values and Best Practices"


class NAACGrade(enum.Enum):
    """NAAC Accreditation Grades"""
    A_PLUS_PLUS = "A++"
    A_PLUS = "A+"
    A = "A"
    B_PLUS_PLUS = "B++"
    B_PLUS = "B+"
    B = "B"
    C = "C"
    D = "D"
    NOT_ACCREDITED = "Not Accredited"


# Official NAAC Criterion Weights (Total = 1000)
NAAC_CRITERION_WEIGHTS = {
    "C1": 150,  # Curricular Aspects
    "C2": 200,  # Teaching-Learning and Evaluation
    "C3": 250,  # Research, Innovations and Extension
    "C4": 100,  # Infrastructure and Learning Resources
    "C5": 100,  # Student Support and Progression
    "C6": 100,  # Governance, Leadership and Management
    "C7": 100,  # Institutional Values and Best Practices
}

NAAC_CRITERION_NAMES = {
    "C1": "Curricular Aspects",
    "C2": "Teaching-Learning and Evaluation",
    "C3": "Research, Innovations and Extension",
    "C4": "Infrastructure and Learning Resources",
    "C5": "Student Support and Progression",
    "C6": "Governance, Leadership and Management",
    "C7": "Institutional Values and Best Practices",
}


def create_naac_models(Base):
    """
    Factory function to create NAAC models with the given SQLAlchemy Base.
    """
    
    class NAACBatchMeta(Base):
        """
        NAAC-specific batch metadata
        Tracks criterion completion and validation state
        """
        __tablename__ = "naac_batch_meta"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), ForeignKey("batches.batch_id"), unique=True, nullable=False)
        
        # Institution info
        institution_type = Column(String(50))  # Autonomous/Affiliated/University
        cycle_number = Column(Integer)  # 1, 2, 3, 4...
        
        # Criterion completion tracking
        has_c1 = Column(Boolean, default=False)
        has_c2 = Column(Boolean, default=False)
        has_c3 = Column(Boolean, default=False)
        has_c4 = Column(Boolean, default=False)
        has_c5 = Column(Boolean, default=False)
        has_c6 = Column(Boolean, default=False)
        has_c7 = Column(Boolean, default=False)
        
        # SSR and IQAC
        has_ssr = Column(Boolean, default=False)
        has_iqac_report = Column(Boolean, default=False)
        
        # Validation state
        is_valid = Column(Boolean, default=True)
        invalid_reason = Column(Text)
        
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    
    class NAACCriterion(Base):
        """
        NAAC Criterion Score (C1-C7)
        Each criterion has a maximum score and weight
        """
        __tablename__ = "naac_criteria"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), ForeignKey("batches.batch_id"), nullable=False)
        criterion_id = Column(String(5), nullable=False)  # C1, C2, ..., C7
        criterion_name = Column(String(255))
        
        # Scoring
        score = Column(Float)  # Raw score (NULL if not computed)
        max_score = Column(Float, default=100.0)
        weight = Column(Integer)  # From NAAC_CRITERION_WEIGHTS
        weighted_score = Column(Float)  # score * (weight / total_weight)
        
        # Sub-components (JSON for flexibility)
        key_indicators = Column(JSON)  # Key Indicator scores
        qualitative_metrics = Column(JSON)  # QnM scores
        
        # Status
        status = Column(String(50))  # Computed / Partial / Not Computed
        
        # Evidence
        evidence_doc_ids = Column(Text)  # JSON list of document IDs
        evidence_pages = Column(Text)  # JSON list of page numbers
        
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, onupdate=datetime.utcnow)
        
        def __repr__(self):
            return f"<NAAC {self.criterion_id}: {self.score}/{self.max_score}>"
    
    
    class NAACKeyIndicator(Base):
        """
        NAAC Key Indicator within a Criterion
        Each criterion has multiple Key Indicators (KIs)
        """
        __tablename__ = "naac_key_indicators"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), nullable=False)
        criterion_id = Column(String(5), nullable=False)  # C1, C2, ..., C7
        ki_id = Column(String(10), nullable=False)  # 1.1, 1.2, 2.1, etc.
        ki_name = Column(String(255))
        
        # Scoring
        score = Column(Float)  # NULL if not computed
        max_score = Column(Float)
        weight = Column(Float)
        
        # Evidence
        evidence_doc_id = Column(String(36))
        evidence_page = Column(Integer)
        evidence_snippet = Column(Text)
        
        created_at = Column(DateTime, default=datetime.utcnow)
    
    
    class NAACQualitativeMetric(Base):
        """
        NAAC Qualitative Metrics (QnM)
        Additional metrics within each criterion
        """
        __tablename__ = "naac_qualitative_metrics"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), nullable=False)
        criterion_id = Column(String(5), nullable=False)
        metric_id = Column(String(20), nullable=False)
        metric_name = Column(String(255))
        
        # Data
        value = Column(Float)  # NULL if not available
        unit = Column(String(50))  # %, count, ratio, etc.
        description = Column(Text)
        
        # Evidence
        evidence_doc_id = Column(String(36))
        evidence_page = Column(Integer)
        
        created_at = Column(DateTime, default=datetime.utcnow)
    
    
    class NAACOverallScore(Base):
        """
        NAAC Overall Institutional Score
        Computed from weighted sum of all 7 criteria
        """
        __tablename__ = "naac_overall_scores"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), ForeignKey("batches.batch_id"), unique=True, nullable=False)
        
        # Overall score (4.0 scale)
        cgpa = Column(Float)  # NULL if any criterion missing
        
        # Grade based on CGPA
        grade = Column(String(10))  # A++, A+, A, B++, etc.
        
        # Criterion-wise breakdown
        c1_score = Column(Float)
        c2_score = Column(Float)
        c3_score = Column(Float)
        c4_score = Column(Float)
        c5_score = Column(Float)
        c6_score = Column(Float)
        c7_score = Column(Float)
        
        # Formula used
        formula_used = Column(Text)
        
        # Validity
        is_complete = Column(Boolean, default=False)
        missing_criteria = Column(Text)  # JSON list of missing criteria
        
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    
    return {
        'NAACBatchMeta': NAACBatchMeta,
        'NAACCriterion': NAACCriterion,
        'NAACKeyIndicator': NAACKeyIndicator,
        'NAACQualitativeMetric': NAACQualitativeMetric,
        'NAACOverallScore': NAACOverallScore,
    }


def get_naac_grade(cgpa: float) -> str:
    """
    Get NAAC grade from CGPA score.
    
    Grading (as per NAAC):
    - 3.51 - 4.00: A++ (Accredited)
    - 3.26 - 3.50: A+ (Accredited)
    - 3.01 - 3.25: A (Accredited)
    - 2.76 - 3.00: B++ (Accredited)
    - 2.51 - 2.75: B+ (Accredited)
    - 2.01 - 2.50: B (Accredited)
    - 1.51 - 2.00: C (Accredited)
    - <= 1.50: D (Not Accredited)
    """
    if cgpa is None:
        return "Not Computed"
    
    if cgpa >= 3.51:
        return "A++"
    elif cgpa >= 3.26:
        return "A+"
    elif cgpa >= 3.01:
        return "A"
    elif cgpa >= 2.76:
        return "B++"
    elif cgpa >= 2.51:
        return "B+"
    elif cgpa >= 2.01:
        return "B"
    elif cgpa >= 1.51:
        return "C"
    else:
        return "D"
