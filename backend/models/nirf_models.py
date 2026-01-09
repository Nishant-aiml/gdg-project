"""
NIRF Mode Database Models
Implementing 5 Parameters (TLR, RP, GO, OI, PR) as per NIRF Framework

STRICT RULES:
- No dummy data
- PR computed ONLY if perception survey uploaded
- Evidence required for every parameter
- No cross-mode data reuse
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime, JSON
from datetime import datetime
from typing import Optional, Dict, Any
import enum


# ============ ENUMS ============

class NIRFParameterID(enum.Enum):
    """NIRF 5 Parameters"""
    TLR = "Teaching, Learning and Resources"
    RP = "Research and Professional Practice"
    GO = "Graduation Outcomes"
    OI = "Outreach and Inclusivity"
    PR = "Perception"


# Official NIRF Parameter Weights (Engineering Ranking)
NIRF_PARAMETER_WEIGHTS = {
    "TLR": 100,  # Teaching, Learning and Resources
    "RP": 100,   # Research and Professional Practice
    "GO": 100,   # Graduation Outcomes
    "OI": 100,   # Outreach and Inclusivity
    "PR": 100,   # Perception
}

NIRF_PARAMETER_NAMES = {
    "TLR": "Teaching, Learning and Resources",
    "RP": "Research and Professional Practice",
    "GO": "Graduation Outcomes",
    "OI": "Outreach and Inclusivity",
    "PR": "Perception",
}

# TLR Sub-parameters
TLR_SUB_PARAMS = {
    "SS": {"name": "Student Strength", "weight": 20},
    "FSR": {"name": "Faculty-Student Ratio", "weight": 30},
    "FQE": {"name": "Faculty Qualification & Experience", "weight": 20},
    "FRU": {"name": "Financial Resources & Utilization", "weight": 30},
}

# RP Sub-parameters
RP_SUB_PARAMS = {
    "PU": {"name": "Publications", "weight": 35},
    "QP": {"name": "Quality of Publications", "weight": 35},
    "IPR": {"name": "IPR and Patents", "weight": 15},
    "FPPP": {"name": "Footprint of Projects & Practice", "weight": 15},
}

# GO Sub-parameters
GO_SUB_PARAMS = {
    "GPH": {"name": "Graduation Performance (Higher Studies)", "weight": 40},
    "GUE": {"name": "University Examinations", "weight": 15},
    "MS": {"name": "Median Salary", "weight": 25},
    "GPHD": {"name": "Graduating Students in PhD", "weight": 20},
}

# OI Sub-parameters
OI_SUB_PARAMS = {
    "RD": {"name": "Regional Diversity", "weight": 30},
    "WD": {"name": "Women Diversity", "weight": 30},
    "ESCS": {"name": "Economically & Socially Challenged Students", "weight": 20},
    "PCS": {"name": "Perception Survey", "weight": 20},
}


def create_nirf_models(Base):
    """
    Factory function to create NIRF models with the given SQLAlchemy Base.
    """
    
    class NIRFBatchMeta(Base):
        """
        NIRF-specific batch metadata
        Tracks parameter completion and validation state
        """
        __tablename__ = "nirf_batch_meta"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), ForeignKey("batches.batch_id"), unique=True, nullable=False)
        
        # Institution info
        institution_type = Column(String(50))  # Engineering/Management/University/etc.
        ranking_year = Column(Integer)
        
        # Parameter completion tracking
        has_tlr_data = Column(Boolean, default=False)
        has_rp_data = Column(Boolean, default=False)
        has_go_data = Column(Boolean, default=False)
        has_oi_data = Column(Boolean, default=False)
        has_pr_survey = Column(Boolean, default=False)  # CRITICAL: PR needs survey
        
        # Validation state
        is_valid = Column(Boolean, default=True)
        invalid_reason = Column(Text)
        
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    
    class NIRFParameter(Base):
        """
        NIRF Parameter Score (TLR, RP, GO, OI, PR)
        """
        __tablename__ = "nirf_parameters"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), ForeignKey("batches.batch_id"), nullable=False)
        param_id = Column(String(5), nullable=False)  # TLR, RP, GO, OI, PR
        param_name = Column(String(255))
        
        # Scoring (out of 100)
        score = Column(Float)  # NULL if not computed
        weight = Column(Integer, default=100)
        weighted_score = Column(Float)
        
        # Sub-parameter scores (JSON)
        sub_scores = Column(JSON)  # {SS: 15, FSR: 25, ...}
        
        # Status
        status = Column(String(50))  # Computed / Partial / Not Computed
        
        # Evidence
        evidence_doc_ids = Column(Text)  # JSON list of document IDs
        
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, onupdate=datetime.utcnow)
        
        def __repr__(self):
            return f"<NIRF {self.param_id}: {self.score}/100>"
    
    
    class NIRFSubParameter(Base):
        """
        NIRF Sub-parameter data
        Detailed breakdown within each parameter
        """
        __tablename__ = "nirf_sub_parameters"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), nullable=False)
        param_id = Column(String(5), nullable=False)  # Parent: TLR, RP, etc.
        sub_param_id = Column(String(10), nullable=False)  # SS, FSR, FQE, etc.
        sub_param_name = Column(String(255))
        
        # Raw data
        raw_value = Column(Float)
        unit = Column(String(50))  # count, ratio, %, LPA, etc.
        
        # Normalized score (0-100)
        normalized_score = Column(Float)
        weight = Column(Float)
        weighted_score = Column(Float)
        
        # Evidence
        evidence_doc_id = Column(String(36))
        evidence_page = Column(Integer)
        
        created_at = Column(DateTime, default=datetime.utcnow)
    
    
    class NIRFOverallScore(Base):
        """
        NIRF Overall Ranking Score
        Computed from weighted sum of all 5 parameters
        """
        __tablename__ = "nirf_overall_scores"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        batch_id = Column(String(36), ForeignKey("batches.batch_id"), unique=True, nullable=False)
        
        # Overall score (out of 100)
        total_score = Column(Float)  # NULL if any critical param missing
        
        # Parameter-wise breakdown
        tlr_score = Column(Float)
        rp_score = Column(Float)
        go_score = Column(Float)
        oi_score = Column(Float)
        pr_score = Column(Float)  # NULL if no perception survey
        
        # Formula used
        formula_used = Column(Text)
        
        # Validity
        is_complete = Column(Boolean, default=False)
        missing_params = Column(Text)  # JSON list of missing parameters
        
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    
    return {
        'NIRFBatchMeta': NIRFBatchMeta,
        'NIRFParameter': NIRFParameter,
        'NIRFSubParameter': NIRFSubParameter,
        'NIRFOverallScore': NIRFOverallScore,
    }
