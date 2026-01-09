"""
Retry utility specifically for parsing operations.
Retries parsing failures once, but does NOT retry AI hallucinations or invalid data.
"""

import time
import logging
from typing import Callable, Any, TypeVar, Optional
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_parsing_with_timeout(
    timeout_seconds: float = 30.0,
    max_retries: int = 1,
    delay_seconds: float = 1.0
):
    """
    Decorator for retrying parsing operations with timeout.
    
    PERFORMANCE RULES:
    - Parsing steps: max 30s per document
    - Retry parsing failures once
    - Do NOT retry AI hallucinations or invalid data
    
    Args:
        timeout_seconds: Maximum time per attempt (default: 30s)
        max_retries: Maximum retries (default: 1 for parsing)
        delay_seconds: Delay between retries (default: 1.0)
    
    Usage:
        @retry_parsing_with_timeout(timeout_seconds=30, max_retries=1)
        def parse_document(file_path):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):  # +1 for initial attempt
                try:
                    # Use ThreadPoolExecutor for timeout
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(func, *args, **kwargs)
                        result = future.result(timeout=timeout_seconds)
                        return result
                
                except FuturesTimeoutError:
                    last_exception = TimeoutError(
                        f"Parsing exceeded timeout of {timeout_seconds}s"
                    )
                    if attempt < max_retries:
                        logger.warning(
                            f"Parsing attempt {attempt + 1}/{max_retries + 1} timed out. "
                            f"Retrying in {delay_seconds}s..."
                        )
                        time.sleep(delay_seconds)
                    else:
                        logger.error(
                            f"All {max_retries + 1} parsing attempts timed out"
                        )
                
                except Exception as e:
                    # Check if it's an AI hallucination or invalid data error
                    error_str = str(e).lower()
                    if any(keyword in error_str for keyword in [
                        "hallucination", "invalid data", "fabricated", 
                        "inferred", "estimated", "not found in document"
                    ]):
                        # Do NOT retry AI hallucinations or invalid data
                        logger.error(f"AI hallucination or invalid data detected. Not retrying: {e}")
                        raise e
                    
                    # It's a parsing failure - retry once
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Parsing attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {delay_seconds}s..."
                        )
                        time.sleep(delay_seconds)
                    else:
                        logger.error(
                            f"All {max_retries + 1} parsing attempts failed: {e}"
                        )
            
            # All retries exhausted
            raise last_exception
        
        return wrapper
    return decorator

