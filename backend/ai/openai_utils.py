"""
OpenAI API utility functions for safe API calls
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def safe_openai_call(client, model: str, messages: list, timeout: int = 60, **kwargs) -> Optional[Any]:
    """
    Safely call OpenAI API with multiple fallback strategies
    Handles temperature, response_format, and other parameter issues
    PERFORMANCE: Default timeout 60s for faster processing
    """

    # Strategy 1: Try with all provided parameters
    try:
        return client.chat.completions.create(
            model=model,
            messages=messages,
            timeout=timeout,
            **kwargs
        )
    except Exception as e1:
        logger.debug(f"Strategy 1 (full params) failed: {e1}")
        
    # Strategy 2: Try without temperature (some models don't support it with response_format)
    if "temperature" in kwargs:
        try:
            call_kwargs = {k: v for k, v in kwargs.items() if k != "temperature"}
            return client.chat.completions.create(
                model=model,
                messages=messages,
                timeout=timeout,
                **call_kwargs
            )
        except Exception as e2:
            logger.debug(f"Strategy 2 (no temperature) failed: {e2}")
    
    # Strategy 3: Try without response_format
    if "response_format" in kwargs:
        try:
            call_kwargs = {k: v for k, v in kwargs.items() if k != "response_format"}
            return client.chat.completions.create(
                model=model,
                messages=messages,
                timeout=timeout,
                **call_kwargs
            )
        except Exception as e3:
            logger.debug(f"Strategy 3 (no response_format) failed: {e3}")
    
    # Strategy 4: Minimal parameters - just model, messages, timeout
    try:
        return client.chat.completions.create(
            model=model,
            messages=messages,
            timeout=timeout
        )
    except Exception as e4:
        logger.error(f"All OpenAI call strategies failed: {e4}")
        raise e4


