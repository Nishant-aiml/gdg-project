"""
Context Router for Universal Chatbot
Automatically detects which mode the chatbot should operate in
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ChatbotContextMode(Enum):
    """Chatbot context modes"""
    ACCREDITATION = "accreditation"  # Platform/accreditation context
    GOV_EASY = "gov_easy"  # Government document explanation
    NAVIGATION = "navigation"  # Platform navigation help


class ContextRouter:
    """
    Routes chatbot queries to appropriate context handler.
    Auto-detects mode based on available context.
    """
    
    def detect_mode(
        self,
        batch_id: Optional[str] = None,
        gov_document_id: Optional[str] = None,
        query: Optional[str] = None
    ) -> ChatbotContextMode:
        """
        Detect which mode the chatbot should operate in.
        
        Args:
            batch_id: Batch ID (if available)
            gov_document_id: Government document ID (if available)
            query: User query (for navigation detection)
        
        Returns:
            ChatbotContextMode enum
        """
        # Priority 1: GovEasy mode (if gov document exists)
        if gov_document_id:
            logger.info(f"Detected GovEasy mode for document {gov_document_id}")
            return ChatbotContextMode.GOV_EASY
        
        # Priority 2: Accreditation mode (if batch exists)
        if batch_id:
            logger.info(f"Detected Accreditation mode for batch {batch_id}")
            return ChatbotContextMode.ACCREDITATION
        
        # Priority 3: Navigation mode (if query suggests navigation help)
        if query and self._is_navigation_query(query):
            logger.info("Detected Navigation mode from query")
            return ChatbotContextMode.NAVIGATION
        
        # Default: Navigation mode (platform help)
        logger.info("Defaulting to Navigation mode")
        return ChatbotContextMode.NAVIGATION
    
    def _is_navigation_query(self, query: str) -> bool:
        """Check if query is about platform navigation."""
        query_lower = query.lower()
        navigation_keywords = [
            "how do i", "how to", "where can i", "where is",
            "how does", "what is", "explain how", "show me",
            "upload", "compare", "trends", "forecast", "dashboard",
            "navigation", "help", "guide", "tutorial"
        ]
        return any(keyword in query_lower for keyword in navigation_keywords)

