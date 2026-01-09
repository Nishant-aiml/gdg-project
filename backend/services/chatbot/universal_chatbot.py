"""
Universal Regulatory Assistant
ONE chatbot that handles all contexts: accreditation, GovEasy, navigation
"""

import logging
from typing import Dict, Any, Optional
from services.chatbot.context_router import ContextRouter, ChatbotContextMode
from services.chatbot.gov_easy_explainer import GovEasyExplainer
from services.chatbot_service import ChatbotService
from config.database import get_db, GovDocument, close_db

logger = logging.getLogger(__name__)


class UniversalRegulatoryAssistant:
    """
    Universal chatbot that dynamically switches behavior based on context.
    Replaces all fragmented chatbot implementations.
    """
    
    def __init__(self):
        self.context_router = ContextRouter()
        self.gov_easy_explainer = GovEasyExplainer()
        self.accreditation_chatbot = ChatbotService()  # Existing chatbot for accreditation
    
    def handle_query(
        self,
        query: str,
        batch_id: Optional[str] = None,
        gov_document_id: Optional[str] = None,
        current_page: Optional[str] = "dashboard",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Handle user query in appropriate context.
        
        Args:
            query: User query
            batch_id: Batch ID (for accreditation context)
            gov_document_id: Government document ID (for GovEasy context)
            current_page: Current page context
            **kwargs: Additional context (comparison_batch_ids, etc.)
        
        Returns:
            Dict with answer, citations, related_blocks, etc.
        """
        # Detect mode
        mode = self.context_router.detect_mode(
            batch_id=batch_id,
            gov_document_id=gov_document_id,
            query=query
        )
        
        logger.info(f"Universal chatbot operating in {mode.value} mode")
        
        # Route to appropriate handler
        if mode == ChatbotContextMode.GOV_EASY:
            return self._handle_gov_easy(query, gov_document_id)
        elif mode == ChatbotContextMode.ACCREDITATION:
            return self._handle_accreditation(query, batch_id, current_page, **kwargs)
        else:  # NAVIGATION
            return self._handle_navigation(query)
    
    def _handle_gov_easy(
        self,
        query: str,
        gov_document_id: str
    ) -> Dict[str, Any]:
        """Handle GovEasy queries (government document explanation)."""
        db = None
        try:
            db = get_db()
            
            # Get government document
            gov_doc = db.query(GovDocument).filter(GovDocument.id == gov_document_id).first()
            if not gov_doc:
                return {
                    "answer": "Government document not found. Please upload the document first.",
                    "citations": [],
                    "related_blocks": [],
                    "requires_context": False
                }
            
            if not gov_doc.extracted_text:
                return {
                    "answer": "This document has not been processed yet. Please wait for text extraction to complete.",
                    "citations": [],
                    "related_blocks": [],
                    "requires_context": False
                }
            
            # Explain document
            explanation = self.gov_easy_explainer.explain_document(
                extracted_text=gov_doc.extracted_text,
                document_type=gov_doc.document_type or "document",
                user_question=query
            )
            
            # Format response
            answer_parts = [explanation.get("explanation", "Could not generate explanation.")]
            
            if explanation.get("who_applies"):
                answer_parts.append(f"\n**Who this applies to:** {explanation['who_applies']}")
            
            if explanation.get("deadlines"):
                answer_parts.append(f"\n**Important Deadlines:**\n" + "\n".join(f"- {d}" for d in explanation["deadlines"]))
            
            if explanation.get("benefits"):
                answer_parts.append(f"\n**Benefits:**\n" + "\n".join(f"- {b}" for b in explanation["benefits"]))
            
            if explanation.get("required_documents"):
                answer_parts.append(f"\n**Required Documents:**\n" + "\n".join(f"- {d}" for d in explanation["required_documents"]))
            
            if explanation.get("consequences"):
                answer_parts.append(f"\n**Consequences of Missing Deadline:**\n" + "\n".join(f"- {c}" for c in explanation["consequences"]))
            
            if explanation.get("next_steps"):
                answer_parts.append(f"\n**Next Steps:**\n" + "\n".join(f"{i+1}. {step}" for i, step in enumerate(explanation["next_steps"])))
            
            return {
                "answer": "\n".join(answer_parts),
                "citations": explanation.get("citations", []),
                "related_blocks": [],
                "requires_context": False,
                "gov_easy_mode": True,
                "document_type": gov_doc.document_type
            }
        
        except Exception as e:
            logger.error(f"Error in GovEasy handler: {e}", exc_info=True)
            return {
                "answer": f"I encountered an error explaining this document: {str(e)[:200]}. Please try again.",
                "citations": [],
                "related_blocks": [],
                "requires_context": False
            }
        finally:
            if db:
                close_db(db)
    
    def _handle_accreditation(
        self,
        query: str,
        batch_id: str,
        current_page: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle accreditation queries (existing chatbot logic)."""
        # Import here to avoid circular dependency
        from routers.chatbot import (
            explain_score, is_explain_query, detect_kpi_name_from_query,
            is_policy_or_hypothetical_query, get_comparison_data, get_unified_report_data
        )
        from config.database import get_db, Batch, Block, close_db
        
        db = None
        try:
            db = get_db()
            
            # Get batch
            batch = db.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                return {
                    "answer": f"Batch {batch_id} not found.",
                    "citations": [],
                    "related_blocks": [],
                    "requires_context": False
                }
            
            # Get all blocks (limit to prevent huge context)
            blocks = db.query(Block).filter(Block.batch_id == batch_id).limit(50).all()
            
            # Get page-specific context
            comparison_data = None
            unified_report_data = None
            
            if current_page == "compare" and kwargs.get("comparison_batch_ids"):
                try:
                    comparison_data = get_comparison_data(kwargs["comparison_batch_ids"], db)
                except Exception as e:
                    logger.warning(f"Could not fetch comparison data: {e}")
            
            elif current_page == "unified-report":
                try:
                    unified_report_data = get_unified_report_data(batch_id, db)
                except Exception as e:
                    logger.warning(f"Could not fetch unified report data: {e}")
            
            # PRODUCTION HARDENING: Check if query should be refused
            if is_policy_or_hypothetical_query(query):
                return {
                    "answer": "I can only answer questions about your current batch data. I cannot provide policy advice, hypothetical scenarios, or general recommendations. Please ask about your uploaded documents, KPIs, or approval status.",
                    "citations": [],
                    "related_blocks": [],
                    "requires_context": False
                }
            
            # PRODUCTION HARDENING: Handle "Explain this score" queries
            mode = batch.mode or "aicte"
            if is_explain_query(query):
                kpi_name = detect_kpi_name_from_query(query, mode)
                if kpi_name:
                    try:
                        result = explain_score(
                            batch_id=batch_id,
                            kpi_type=kpi_name,
                            current_page=current_page
                        )
                        return result
                    except Exception as e:
                        logger.error(f"Error explaining score: {e}", exc_info=True)
                        return {
                            "answer": "Insufficient data to explain this score. The KPI details API encountered an error.",
                            "citations": [],
                            "related_blocks": [],
                            "requires_context": False
                        }
            
            # Build context
            try:
                context = self.accreditation_chatbot.build_context(
                    batch=batch,
                    blocks=blocks,
                    current_page=current_page or "dashboard",
                    comparison_data=comparison_data,
                    unified_report_data=unified_report_data
                )
            except Exception as e:
                logger.error(f"Error building context: {e}", exc_info=True)
                return {
                    "answer": f"Error building context: {str(e)[:200]}",
                    "citations": [],
                    "related_blocks": [],
                    "requires_context": False
                }
            
            # Generate response
            try:
                result = self.accreditation_chatbot.generate_response(
                    query=query,
                    context=context,
                    mode=mode,
                    batch_id=batch_id
                )
                return result
            except Exception as e:
                logger.error(f"Error generating chatbot response: {e}", exc_info=True)
                return {
                    "answer": f"I apologize, but I encountered an error processing your question: {str(e)[:200]}. Please try again or contact support.",
                    "citations": [],
                    "related_blocks": [],
                    "requires_context": False
                }
        
        except Exception as e:
            logger.error(f"Error in accreditation handler: {e}", exc_info=True)
            return {
                "answer": f"I encountered an error: {str(e)[:200]}. Please try again.",
                "citations": [],
                "related_blocks": [],
                "requires_context": False
            }
        finally:
            if db:
                close_db(db)
    
    def _handle_navigation(self, query: str) -> Dict[str, Any]:
        """Handle platform navigation queries."""
        # Static help map (NOT LLM-generated)
        help_map = {
            "upload": {
                "answer": "To upload documents:\n1. Select an accreditation mode (AICTE, NBA, NAAC, or NIRF)\n2. Click 'Start New Batch'\n3. Fill in institution/department details (optional)\n4. Drag and drop or browse for PDF, Excel, CSV, or Word files\n5. Click 'Upload & Process'\n\nDocuments will be automatically processed and analyzed.",
                "citations": []
            },
            "compare": {
                "answer": "To compare departments/institutions:\n1. Go to the Comparison page\n2. Select 2 or more batches from the list\n3. Choose a KPI to compare (FSR, Infrastructure, Placement, etc.)\n4. View side-by-side comparison with strengths and weaknesses\n\nNote: Only completed batches with valid data can be compared.",
                "citations": []
            },
            "trends": {
                "answer": "To view trends:\n1. Go to the Trends page\n2. Select a batch\n3. View KPI trends over multiple years\n4. See year-over-year changes and forecasts\n\nNote: Trends require at least 3 years of data for the same department.",
                "citations": []
            },
            "forecast": {
                "answer": "Forecasting is available on the Dashboard:\n1. View the trend chart for any KPI\n2. If you have 3+ years of data, forecasts are automatically generated\n3. Forecasts use linear regression based on historical data\n4. Confidence intervals are shown\n\nNote: Forecasts are estimates and should be used for planning purposes only.",
                "citations": []
            },
            "dashboard": {
                "answer": "The Dashboard shows:\n- Overall score and sufficiency percentage\n- KPI cards (FSR, Infrastructure, Placement, Lab Compliance)\n- Extracted data blocks\n- Trend charts (if multi-year data available)\n\nClick any KPI card to see detailed breakdown with formula, parameters, and evidence.",
                "citations": []
            },
            "kpi": {
                "answer": "KPIs (Key Performance Indicators) are calculated based on:\n- AICTE: FSR, Infrastructure, Placement, Lab Compliance\n- NBA: PEOs & PSOs, Faculty Quality, Student Performance, etc.\n- NAAC: 7 Criteria (C1-C7)\n- NIRF: TLR, RP, GO, OI, PR\n\nClick any KPI card to see the exact formula, input parameters, weights, and evidence sources.",
                "citations": []
            }
        }
        
        # Check if query matches any help topic
        query_lower = query.lower()
        for topic, help_data in help_map.items():
            if topic in query_lower:
                return {
                    "answer": help_data["answer"],
                    "citations": help_data.get("citations", []),
                    "related_blocks": [],
                    "requires_context": False,
                    "navigation_mode": True
                }
        
        # Generic navigation help
        return {
            "answer": """I can help you with:

**Platform Navigation:**
- How to upload documents
- How to compare departments
- How to view trends and forecasts
- Understanding the dashboard

**Accreditation Questions:**
- Explain any KPI score
- Why a score is low/high
- What documents are missing
- How to improve next year

**Government Documents (GovEasy):**
- Upload a government circular, letter, or scheme
- Ask "What does this mean?"
- Get simple explanations of eligibility, deadlines, and requirements

What would you like to know?""",
            "citations": [],
            "related_blocks": [],
            "requires_context": False,
            "navigation_mode": True
        }

