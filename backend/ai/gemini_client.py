"""
Google Gemini API Client
Primary chatbot model (free tier)
"""

import logging
from typing import Dict, Any, Optional, List
import os
from config.settings import settings

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Install with: pip install google-generativeai")


class GeminiClient:
    """
    Google Gemini API client for chatbot
    Uses free tier with strict scope (platform-related questions only)
    """
    
    def __init__(self):
        # Try settings first, then environment variable
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or settings.UNSTRUCTURED_API_KEY  # Reuse if available
        self.model_name = settings.GEMINI_MODEL  # Use Gemini 2.5 Flash from settings
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set. Chatbot will fallback to OpenAI.")
            self.available = False
            return
        
        if not GEMINI_AVAILABLE:
            logger.warning("google-generativeai package not installed. Chatbot will fallback to OpenAI.")
            self.available = False
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
            self.available = True
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.available = False
    
    def generate_chat_response(
        self,
        query: str,
        context: Dict[str, Any],
        system_prompt: str
    ) -> Dict[str, Any]:
        """
        Generate chatbot response using Gemini
        
        Args:
            query: User question
            context: Platform context (KPIs, blocks, etc.)
            system_prompt: System instructions
        
        Returns:
            {
                "answer": str,
                "citations": List[str],
                "related_blocks": List[str]
            }
        """
        if not self.available:
            raise ValueError("Gemini client not available")
        
        try:
            # Build prompt with strict scope enforcement
            prompt = f"""{system_prompt}

CONTEXT (Platform Data Only):
{self._format_context(context)}

USER QUESTION: {query}

IMPORTANT RULES:
- Answer ONLY about the platform data provided above
- Explain scores, trends, missing documents based on real data
- NEVER hallucinate policy rules or make up data
- If data is missing, say "Not enough data" instead of fabricating
- Cite specific evidence when available

RESPONSE:"""
            
            # PERFORMANCE: Generate response with timeout (20s max)
            from utils.retry_with_timeout import retry_with_timeout
            import threading
            import queue
            
            @retry_with_timeout(max_retries=2, timeout_seconds=20, delay_seconds=1.0)
            def _generate_with_timeout():
                response = self.client.generate_content(prompt)
                return response.text if hasattr(response, 'text') else str(response)
            
            try:
                answer = _generate_with_timeout()
            except Exception as e:
                logger.error(f"Gemini API timeout/error after retries: {e}")
                raise
            
            # Extract citations from answer (simple pattern matching)
            citations = self._extract_citations(answer, context)
            related_blocks = self._extract_related_blocks(answer, context)
            
            return {
                "answer": answer,
                "citations": citations,
                "related_blocks": related_blocks,
                "requires_context": True
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for Gemini prompt"""
        parts = []
        
        # KPI Results
        if context.get("kpi_results"):
            parts.append("KPIs:")
            for kpi_id, kpi_data in context["kpi_results"].items():
                if isinstance(kpi_data, dict) and kpi_data.get("value") is not None:
                    parts.append(f"  - {kpi_data.get('name', kpi_id)}: {kpi_data.get('value')}")
        
        # Sufficiency
        if context.get("sufficiency_result"):
            sufficiency = context["sufficiency_result"]
            parts.append(f"Document Sufficiency: {sufficiency.get('percentage', 0)}%")
        
        # Compliance
        if context.get("compliance_results"):
            parts.append(f"Compliance Flags: {len(context['compliance_results'])} issues found")
        
        # Block summaries
        if context.get("block_summaries"):
            parts.append("Available Data Blocks:")
            for block_type, summary in context["block_summaries"].items():
                if summary.get("present"):
                    parts.append(f"  - {block_type}: {summary.get('fields_count', 0)} fields extracted")
        
        return "\n".join(parts) if parts else "No context data available"
    
    def _extract_citations(self, answer: str, context: Dict[str, Any]) -> List[str]:
        """Extract citation references from answer"""
        citations = []
        
        # Look for block references
        if context.get("block_summaries"):
            for block_type in context["block_summaries"].keys():
                if block_type.lower() in answer.lower():
                    citations.append(f"Data from {block_type} block")
        
        return citations
    
    def _extract_related_blocks(self, answer: str, context: Dict[str, Any]) -> List[str]:
        """Extract related block types mentioned in answer"""
        related = []
        
        if context.get("block_summaries"):
            for block_type in context["block_summaries"].keys():
                if block_type.lower() in answer.lower():
                    related.append(block_type)
        
        return related

