"""
GovEasy Explainer
Explains government documents in simple language using Gemini API
"""

import logging
from typing import Dict, Any, Optional
from ai.gemini_client import GeminiClient
from ai.openai_utils import safe_openai_call

logger = logging.getLogger(__name__)


class GovEasyExplainer:
    """
    Explains government documents (circulars, letters, schemes) in simple language.
    Uses Gemini API as primary, GPT-5 Nano as fallback.
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    def explain_document(
        self,
        extracted_text: str,
        document_type: str,
        user_question: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Explain government document in simple language.
        
        Args:
            extracted_text: Full OCR text from document
            document_type: Type of document (circular, letter, scheme, etc.)
            user_question: Optional specific question from user
        
        Returns:
            Dict with:
                - explanation: Simple explanation in plain English
                - who_applies: Who this document applies to
                - deadlines: Important deadlines mentioned
                - benefits: Benefits/features mentioned
                - required_documents: Documents required
                - consequences: Consequences of missing deadline
                - next_steps: Action items checklist
                - citations: Page numbers or sections referenced
        """
        if not extracted_text or len(extracted_text.strip()) < 50:
            return {
                "explanation": "I could not extract sufficient text from this document. Please ensure the document is clear and readable.",
                "who_applies": None,
                "deadlines": [],
                "benefits": [],
                "required_documents": [],
                "consequences": [],
                "next_steps": [],
                "citations": [],
                "error": "Insufficient text extracted"
            }
        
        # Build prompt for Gemini
        prompt = self._build_explanation_prompt(extracted_text, document_type, user_question)
        
        # Try Gemini first (primary)
        try:
            if self.gemini_client.available:
                logger.info("Using Gemini API for GovEasy explanation")
                response = self.gemini_client.generate_chat_response(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3  # Lower temperature for factual explanations
                )
                
                if response:
                    # Parse structured response
                    result = self._parse_explanation_response(response, extracted_text)
                    result["model_used"] = "gemini-pro"
                    return result
        except Exception as e:
            logger.warning(f"Gemini API failed for GovEasy: {e}, trying fallback")
        
        # Fallback to GPT-5 Nano
        try:
            logger.info("Using GPT-5 Nano as fallback for GovEasy explanation")
            from config.settings import settings
            
            response = safe_openai_call(
                model=settings.OPENAI_MODEL_PRIMARY,  # gpt-5-nano
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            if response:
                result = self._parse_explanation_response(response, extracted_text)
                result["model_used"] = "gpt-5-nano"
                result["fallback_used"] = True
                return result
        except Exception as e:
            logger.error(f"GPT-5 Nano fallback also failed: {e}")
        
        # If both fail, return error
        return {
            "explanation": "I apologize, but I encountered an error while explaining this document. Please try again or contact support.",
            "who_applies": None,
            "deadlines": [],
            "benefits": [],
            "required_documents": [],
            "consequences": [],
            "next_steps": [],
            "citations": [],
            "error": "Both Gemini and GPT-5 Nano failed"
        }
    
    def _build_explanation_prompt(
        self,
        extracted_text: str,
        document_type: str,
        user_question: Optional[str]
    ) -> str:
        """Build prompt for document explanation."""
        base_prompt = f"""You are a helpful assistant that explains government documents in simple, clear language.

Document Type: {document_type.upper()}

Document Text:
{extracted_text[:8000]}  # Limit to 8000 chars to avoid token limits

"""
        
        if user_question:
            base_prompt += f"""
User Question: {user_question}

"""
        
        base_prompt += """
Please provide a structured explanation in JSON format with the following fields:

{
  "explanation": "Simple, clear explanation of what this document means in plain English (2-3 paragraphs)",
  "who_applies": "Who this document applies to (e.g., 'All engineering colleges', 'New universities only', etc.)",
  "deadlines": ["List of important deadlines mentioned in the document"],
  "benefits": ["List of benefits, features, or advantages mentioned"],
  "required_documents": ["List of documents or information required"],
  "consequences": ["What happens if deadlines are missed or requirements not met"],
  "next_steps": ["Action items checklist for the user"],
  "citations": ["Page numbers or section references where key information was found"]
}

IMPORTANT RULES:
1. ONLY use information from the document text provided above
2. Do NOT add information not present in the document
3. If information is missing, say "Not mentioned in document"
4. Use simple, clear language - avoid legal jargon
5. Be specific about dates, deadlines, and requirements
6. If user asked a specific question, focus your explanation on answering that question

Return ONLY valid JSON, no additional text.
"""
        return base_prompt
    
    def _parse_explanation_response(
        self,
        response: str,
        extracted_text: str
    ) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        import json
        import re
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                
                # Validate and clean
                result = {
                    "explanation": parsed.get("explanation", "Could not generate explanation."),
                    "who_applies": parsed.get("who_applies"),
                    "deadlines": parsed.get("deadlines", []),
                    "benefits": parsed.get("benefits", []),
                    "required_documents": parsed.get("required_documents", []),
                    "consequences": parsed.get("consequences", []),
                    "next_steps": parsed.get("next_steps", []),
                    "citations": parsed.get("citations", [])
                }
                
                # Ensure all are lists where expected
                for key in ["deadlines", "benefits", "required_documents", "consequences", "next_steps", "citations"]:
                    if not isinstance(result[key], list):
                        result[key] = [result[key]] if result[key] else []
                
                return result
        except Exception as e:
            logger.warning(f"Failed to parse JSON response: {e}, using fallback")
        
        # Fallback: return response as explanation
        return {
            "explanation": response[:1000],  # Limit length
            "who_applies": None,
            "deadlines": [],
            "benefits": [],
            "required_documents": [],
            "consequences": [],
            "next_steps": [],
            "citations": []
        }

