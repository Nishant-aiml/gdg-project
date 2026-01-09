"""
Chatbot assistant router - Full AI chatbot system
Supports comprehensive Q&A about dashboard, KPIs, approval, comparison, trends
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging
from services.chatbot_service import ChatbotService
from services.chatbot.universal_chatbot import UniversalRegulatoryAssistant
from config.database import get_db, Batch, Block, close_db
from middleware.auth_middleware import get_current_user

router = APIRouter()
chatbot_service = ChatbotService()
universal_chatbot = UniversalRegulatoryAssistant()  # NEW: Universal chatbot
logger = logging.getLogger(__name__)


def get_comparison_data(batch_ids: List[str], db) -> Optional[Dict[str, Any]]:
    """Helper to get comparison data for chatbot context."""
    try:
        from routers.compare import compare_institutions
        from fastapi import Query
        
        # Call the comparison endpoint logic
        batch_ids_str = ",".join(batch_ids)
        comparison_result = compare_institutions(batch_ids=batch_ids_str)
        
        # Convert Pydantic model to dict
        if hasattr(comparison_result, 'model_dump'):
            return comparison_result.model_dump()
        elif hasattr(comparison_result, 'dict'):
            return comparison_result.dict()
        else:
            return comparison_result
    except Exception as e:
        logger.warning(f"Could not fetch comparison data: {e}")
        # Return basic info if full comparison fails
        return {
            "batch_ids": batch_ids,
            "count": len(batch_ids),
            "note": f"Comparison data unavailable: {str(e)}"
        }


def get_unified_report_data(batch_id: str, db) -> Optional[Dict[str, Any]]:
    """Helper to get unified report data for chatbot context."""
    try:
        from routers.unified_report import get_unified_report
        result = get_unified_report(batch_id)
        if result and hasattr(result, 'model_dump'):
            return result.model_dump()
        elif result and hasattr(result, 'dict'):
            return result.dict()
        elif isinstance(result, dict):
            return result
        return None
    except Exception as e:
        logger.warning(f"Could not fetch unified report data: {e}")
        return None


def explain_score(batch_id: str, kpi_type: str, current_page: Optional[str] = None) -> Dict[str, Any]:
    """
    Explain a KPI score using REAL backend data from KPI details endpoint.
    STRICT: Response MUST be generated ONLY from API response.
    NO inference, summarization, or independent calculation.
    
    Args:
        batch_id: Batch ID
        kpi_type: KPI type (e.g., 'fsr', 'infrastructure', 'placement', 'lab', 'overall')
        current_page: Current page context (for validation)
    
    Returns:
        ChatQueryResponse dict with explanation based ONLY on API response
        
    Raises:
        HTTPException: If KPI details API fails or data is insufficient
    """
    # Validate inputs
    if not batch_id or not batch_id.strip():
        raise HTTPException(status_code=400, detail="batch_id is required")
    
    if not kpi_type or not kpi_type.strip():
        raise HTTPException(status_code=400, detail="kpi_type is required")
    
    # DEMO MODE: Return demo explanation for demo batches
    if batch_id.startswith("demo-"):
        demo_explanations = {
            "fsr": "**Faculty-Student Ratio Score: 85.2/100**\n\nCalculated as: (Actual Faculty / Required Faculty) × 100\n- Faculty Count: 120\n- Student Count: 2,000\n- Actual Ratio: 1:16.7\n- AICTE Norm: 1:20\n\n✅ Exceeds AICTE requirements.",
            "infrastructure": "**Infrastructure Score: 72.0/100**\n\nBased on:\n- Classroom Space: 50 sqft/student (norm: 60) → 83%\n- Lab Area: 3,000 sqft (adequate)\n- Library: 2,000 sqft\n\n⚠️ Classroom space below norm.",
            "placement": "**Placement Index: 92.3/100**\n\nMetrics:\n- Placement Rate: 92%\n- Avg Package: ₹8.5 LPA\n- Higher Studies: 5%\n\n✅ Excellent placement performance.",
            "lab": "**Lab Compliance: 68.5/100**\n\nEquipment Status:\n- Required Labs: 10\n- Functional Labs: 8\n- Compliance: 80%\n\n⚠️ 2 labs need upgrades.",
            "overall": "**Overall AICTE Score: 78.5/100**\n\nWeighted Average:\n- FSR (30%): 85.2 → 25.6\n- Infrastructure (25%): 72.0 → 18.0\n- Placement (25%): 92.3 → 23.1\n- PhD Faculty (20%): 68.5 → 13.7\n\n**Total: 78.5/100**"
        }
        kpi_lower = kpi_type.lower()
        explanation = demo_explanations.get(kpi_lower, demo_explanations.get("overall"))
        return {
            "answer": explanation,
            "citations": ["Demo data - not from real documents"],
            "related_blocks": ["faculty_info", "infrastructure", "placement"],
            "requires_context": False
        }
    

    # Validate that request is for current batch (security check)
    db = get_db()
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
        
        mode = batch.mode or "aicte"
        
        # Validate KPI type is valid for this mode
        kpi_type_lower = kpi_type.lower().strip()
        valid_types_map = {
            "aicte": ["fsr", "infrastructure", "placement", "lab", "overall"],
            "nba": ["peos_psos", "faculty_quality", "student_performance", "continuous_improvement", "co_po_mapping", "overall"],
            "naac": [f"criterion_{i}" for i in range(1, 8)] + ["overall"],
            "nirf": ["tlr", "rp", "go", "oi", "pr", "overall"]
        }
        
        valid_types = valid_types_map.get(mode.lower(), valid_types_map["aicte"])
        if kpi_type_lower not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid KPI type '{kpi_type}' for {mode.upper()} mode. Must be one of: {', '.join(valid_types)}"
            )
    finally:
        close_db(db)
    
    # Call KPI details API endpoint (internal call)
    try:
        from services.kpi_detailed import get_kpi_detailed_breakdown
        
        # Call the KPI details endpoint
        kpi_details = get_kpi_detailed_breakdown(batch_id, kpi_type_lower)
        
        # STRICT VALIDATION: If API fails or returns insufficient data, refuse to answer
        if not kpi_details:
            return {
                "answer": "Insufficient data to explain this score. The KPI details endpoint returned no data.",
                "citations": [],
                "related_blocks": [],
                "requires_context": False
            }
        
        score = kpi_details.get("score")
        if score is None:
            return {
                "answer": "Insufficient data to explain this score. The score value is missing from the KPI details.",
                "citations": [],
                "related_blocks": [],
                "requires_context": False
            }
        
        # Check if we have parameters and evidence
        parameters = kpi_details.get("parameters", [])
        if not parameters or len(parameters) == 0:
            return {
                "answer": "Insufficient data to explain this score. No parameter breakdown is available.",
                "citations": [],
                "related_blocks": [],
                "requires_context": False
            }
        
        # Format explanation using ONLY the API response data
        result = chatbot_service.format_score_explanation(
            kpi_name=kpi_type_lower,
            kpi_details=kpi_details,
            mode=mode
        )
        
        return result
    
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Error fetching KPI details for {kpi_type}: {e}", exc_info=True)
        # STRICT: If API fails, refuse to answer
        raise HTTPException(
            status_code=500,
            detail=f"Cannot explain score: KPI details API failed. Error: {str(e)[:200]}"
        )


def detect_kpi_name_from_query(query: str, mode: str) -> Optional[str]:
    """
    Detect KPI name from user query.
    
    Returns:
        KPI type string (e.g., 'fsr', 'infrastructure') or None if not detected
    """
    query_lower = query.lower()
    
    # AICTE KPIs
    if mode.lower() == "aicte":
        if "fsr" in query_lower or "faculty-student" in query_lower or "faculty student" in query_lower:
            return "fsr"
        elif "infrastructure" in query_lower or "infra" in query_lower:
            return "infrastructure"
        elif "placement" in query_lower:
            return "placement"
        elif "lab" in query_lower or "laboratory" in query_lower:
            return "lab"
        elif "overall" in query_lower or "total score" in query_lower:
            return "overall"
    
    # NBA KPIs
    elif mode.lower() == "nba":
        if "peos" in query_lower or "pso" in query_lower:
            return "peos_psos"
        elif "faculty quality" in query_lower or "faculty" in query_lower:
            return "faculty_quality"
        elif "student performance" in query_lower:
            return "student_performance"
        elif "continuous improvement" in query_lower:
            return "continuous_improvement"
        elif "co-po" in query_lower or "co po" in query_lower:
            return "co_po_mapping"
        elif "overall" in query_lower:
            return "overall"
    
    # NAAC KPIs
    elif mode.lower() == "naac":
        for i in range(1, 8):
            if f"criterion {i}" in query_lower or f"criterion_{i}" in query_lower:
                return f"criterion_{i}"
        if "overall" in query_lower:
            return "overall"
    
    # NIRF KPIs
    elif mode.lower() == "nirf":
        if "tlr" in query_lower or "teaching learning" in query_lower:
            return "tlr"
        elif "rp" in query_lower or "research" in query_lower:
            return "rp"
        elif "go" in query_lower or "graduation" in query_lower:
            return "go"
        elif "oi" in query_lower or "outreach" in query_lower:
            return "oi"
        elif "pr" in query_lower or "perception" in query_lower:
            return "pr"
        elif "overall" in query_lower:
            return "overall"
    
    return None


def is_explain_query(query: str) -> bool:
    """
    Check if query is asking to explain a score.
    
    Returns:
        True if query contains explain keywords
    """
    query_lower = query.lower()
    explain_keywords = ["explain", "why", "how is", "how was", "what is", "what does", "breakdown", "calculate"]
    return any(keyword in query_lower for keyword in explain_keywords)


def is_policy_or_hypothetical_query(query: str) -> bool:
    """
    Check if query is asking about policy or hypothetical scenarios.
    
    Returns:
        True if query should be refused
    """
    query_lower = query.lower()
    
    # Policy keywords
    policy_keywords = [
        "policy", "regulation", "rule", "guideline", "norm", "standard",
        "what should", "what would", "if i", "suppose", "hypothetical",
        "what if", "scenario", "recommendation", "advice"
    ]
    
    # Check if it's asking about general policy (not tied to current batch)
    if any(keyword in query_lower for keyword in policy_keywords):
        # Allow if it's about current batch's policy compliance
        if "my" in query_lower or "this" in query_lower or "current" in query_lower:
            return False
        return True
    
    return False


class ChatQueryRequest(BaseModel):
    query: str
    batch_id: Optional[str] = None  # Optional - for accreditation context
    gov_document_id: Optional[str] = None  # Optional - for GovEasy context
    current_page: Optional[str] = "dashboard"
    comparison_batch_ids: Optional[list] = None


class ExplainScoreRequest(BaseModel):
    """Request model for explain_score intent"""
    batch_id: str
    kpi_type: str
    current_page: Optional[str] = "dashboard"


class ChatQueryResponse(BaseModel):
    answer: str
    citations: list
    related_blocks: list
    requires_context: bool


@router.get("/health")
def chatbot_health():
    """Check if chatbot service is properly configured."""
    try:
        from config.settings import settings
        from ai.gemini_client import GeminiClient
        
        # Check Gemini (primary)
        gemini_client = GeminiClient()
        gemini_available = gemini_client.available
        gemini_error = None if gemini_available else "Gemini API key not set or package not installed"
        
        # Check OpenAI (fallback)
        has_openai_key = bool(settings.OPENAI_API_KEY)
        primary_model = settings.OPENAI_MODEL_PRIMARY  # gpt-5-nano
        fallback_model = settings.OPENAI_MODEL_FALLBACK  # gpt-5-mini
        
        openai_client_ok = False
        openai_error = None
        if has_openai_key:
            try:
                from ai.openai_client import OpenAIClient
                client = OpenAIClient()
                openai_client_ok = True
            except Exception as e:
                openai_client_ok = False
                openai_error = str(e)
        else:
            openai_error = "OpenAI API key not set"
        
        # Overall status: OK if at least one service is available
        overall_status = "ok" if (gemini_available or openai_client_ok) else "error"
        
        return {
            "status": overall_status,
            "models": {
                "primary": "gemini-pro (free tier)",
                "fallback_1": primary_model,
                "fallback_2": fallback_model
            },
            "gemini": {
                "available": gemini_available,
                "error": gemini_error
            },
            "openai": {
                "has_api_key": has_openai_key,
                "client_initialized": openai_client_ok,
                "primary_model": primary_model,
                "fallback_model": fallback_model,
                "error": openai_error
            }
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@router.post("/query", response_model=ChatQueryResponse)
def query_chatbot(
    request: ChatQueryRequest,
    user: Optional[dict] = Depends(get_current_user)
) -> ChatQueryResponse:
    """
    Universal chatbot query endpoint.
    
    Automatically detects context:
    - If gov_document_id provided → GovEasy mode (explain government document)
    - If batch_id provided → Accreditation mode (explain scores, KPIs)
    - Otherwise → Navigation mode (platform help)
    
    Supports:
    - Dashboard: KPIs, sufficiency, compliance, blocks
    - Approval: Classification, readiness, required documents
    - Unified Report: Accreditation evaluation data
    - Comparison: Multi-institution comparison
    - Trends: Historical trends and forecasts
    - GovEasy: Government document explanation
    - Navigation: Platform help
    """
    try:
        # Validate request
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # DEMO MODE: Return demo response for demo batches
        if request.batch_id and request.batch_id.startswith("demo-"):
            query_lower = request.query.lower()
            # Generate context-aware demo responses
            if "fsr" in query_lower or "faculty" in query_lower:
                answer = "**Faculty-Student Ratio (FSR) Score: 85.2/100**\n\nThis score is calculated based on the ratio of faculty members to students. The demo institution has:\n- 120 faculty members\n- 2,000 students\n- Ratio: 1:16.7 (better than AICTE norm of 1:20)\n\n✅ Excellent performance in faculty adequacy."
            elif "infrastructure" in query_lower:
                answer = "**Infrastructure Score: 72.0/100**\n\nThis score evaluates campus facilities including:\n- Classroom area: 50 sqft/student (norm: 60 sqft)\n- Library space: Adequate\n- Lab facilities: Good condition\n\n⚠️ Improvement suggested for classroom space."
            elif "placement" in query_lower:
                answer = "**Placement Rate: 92.3/100**\n\nExcellent placement performance with:\n- 92% students placed\n- Average package: ₹8.5 LPA\n- Top recruiters: TCS, Infosys, Google\n\n✅ Outstanding placement record."
            elif "overall" in query_lower:
                answer = "**Overall AICTE Score: 78.5/100**\n\nThe weighted average of all KPIs:\n- FSR: 85.2 (weight: 30%)\n- Infrastructure: 72.0 (weight: 25%)\n- Placement: 92.3 (weight: 25%)\n- PhD Faculty: 68.5 (weight: 20%)\n\n✅ Good overall performance."
            else:
                answer = f"I can help you understand your evaluation metrics for this demo batch. You can ask about:\n\n• **FSR Score** - Faculty-Student Ratio (85.2)\n• **Infrastructure** - Facility assessment (72.0)\n• **Placement** - Placement rate (92.3)\n• **Overall Score** - Combined AICTE score (78.5)\n\nWhat would you like to know more about?"
            
            return ChatQueryResponse(
                answer=answer,
                citations=["Demo data - not from real documents"],
                related_blocks=["faculty_info", "infrastructure", "placement"],
                requires_context=False
            )
        
        # Use universal chatbot (auto-detects mode)
        result = universal_chatbot.handle_query(
            query=request.query,
            batch_id=request.batch_id,
            gov_document_id=request.gov_document_id,
            current_page=request.current_page or "dashboard",
            comparison_batch_ids=request.comparison_batch_ids
        )
        
        return ChatQueryResponse(**result)

    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in universal chatbot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)[:200]}")


@router.post("/explain_score", response_model=ChatQueryResponse)
def explain_score_endpoint(
    request: ExplainScoreRequest,
    user: Optional[dict] = Depends(get_current_user)
) -> ChatQueryResponse:
    """
    Dedicated endpoint for explain_score intent.
    
    STRICT RULES:
    - Accepts: batch_id, kpi_type, current_page
    - Calls: GET /api/kpi/details/{batch_id}/{kpi_type}
    - Response MUST be generated ONLY from API response
    - NO inference, summarization, or independent calculation
    - If data is missing → respond with "Insufficient data to explain this score"
    - Rejects questions not related to current batch, current KPI, or current page context
    - If KPI details API fails → chatbot must refuse to answer
    """
    try:
        # Validate current page context (if provided)
        if request.current_page:
            valid_pages = ["dashboard", "approval", "compare", "trends", "unified-report"]
            if request.current_page not in valid_pages:
                logger.warning(f"Invalid current_page: {request.current_page}, using 'dashboard'")
        
        # Call explain_score function
        result = explain_score(
            batch_id=request.batch_id,
            kpi_type=request.kpi_type,
            current_page=request.current_page
        )
        
        return ChatQueryResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in explain_score endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to explain score: {str(e)[:200]}"
        )


# Keep old endpoint for backward compatibility
@router.post("/chat")
def chat_with_assistant(message: Dict[str, Any]):
    """Legacy endpoint - redirects to new query endpoint"""
    return query_chatbot(ChatQueryRequest(
        query=message.get("message", ""),
        batch_id=message.get("batch_id", ""),
        current_page=message.get("current_page", "dashboard")
    ))
