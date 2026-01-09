"""
KPI Details API Router.
Returns detailed parameter-level breakdown for each KPI.
NO dummy data - everything from real backend computation.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from services.kpi_detailed import get_kpi_detailed_breakdown
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/details/{batch_id}/{kpi_type}")
def get_kpi_details(batch_id: str, kpi_type: str) -> Dict[str, Any]:
    """
    Get detailed parameter breakdown for a specific KPI.
    
    Args:
        batch_id: Batch ID
        kpi_type: 
            - AICTE: 'fsr', 'infrastructure', 'placement', 'lab', 'overall'
            - NBA: 'peos_psos', 'faculty_quality', 'student_performance', 'continuous_improvement', 'co_po_mapping', 'overall'
            - NAAC: 'criterion_1' through 'criterion_7', 'overall'
            - NIRF: 'tlr', 'rp', 'go', 'oi', 'pr', 'overall'
    
    Returns:
        Detailed breakdown with parameters, evidence, calculation steps
    """
    from config.database import get_db, Batch, close_db
    
    db = get_db()
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
        
        mode = (batch.mode or "aicte").lower()
        kpi_type_lower = kpi_type.lower().strip()
        
        # Mode-specific valid types
        valid_types_map = {
            "aicte": ["fsr", "infrastructure", "placement", "lab", "overall"],
            "nba": ["peos_psos", "faculty_quality", "student_performance", "continuous_improvement", "co_po_mapping", "overall"],
            "naac": [f"criterion_{i}" for i in range(1, 8)] + ["overall"],
            "nirf": ["tlr", "rp", "go", "oi", "pr", "overall"]
        }
        
        valid_types = valid_types_map.get(mode, valid_types_map["aicte"])
        
        if kpi_type_lower not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid KPI type for {mode.upper()} mode. Must be one of: {', '.join(valid_types)}"
            )
    finally:
        close_db(db)
    
    try:
        result = get_kpi_detailed_breakdown(batch_id, kpi_type_lower)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(f"Error getting KPI details: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

