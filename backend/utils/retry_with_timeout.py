"""
Retry utility with timeout support.
Max 2 retries for OCR/LLM calls.
"""

import time
import logging
from typing import Callable, Any, Optional, TypeVar
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_with_timeout(
    max_retries: int = 2,
    timeout_seconds: Optional[float] = None,
    delay_seconds: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying function calls with timeout.
    
    Args:
        max_retries: Maximum number of retries (default: 2)
        timeout_seconds: Maximum time to wait for function (None = no timeout)
        delay_seconds: Delay between retries (default: 1.0)
        exceptions: Tuple of exceptions to catch and retry on
    
    Usage:
        @retry_with_timeout(max_retries=2, timeout_seconds=15)
        def my_function():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):  # +1 for initial attempt
                try:
                    if timeout_seconds:
                        # Use threading timeout for blocking calls
                        import threading
                        import queue
                        
                        result_queue = queue.Queue()
                        exception_queue = queue.Queue()
                        
                        def target():
                            try:
                                result = func(*args, **kwargs)
                                result_queue.put(result)
                            except Exception as e:
                                exception_queue.put(e)
                        
                        thread = threading.Thread(target=target)
                        thread.daemon = True
                        thread.start()
                        thread.join(timeout=timeout_seconds)
                        
                        if thread.is_alive():
                            # Timeout occurred
                            raise TimeoutError(
                                f"Function {func.__name__} exceeded timeout of {timeout_seconds}s"
                            )
                        
                        if not exception_queue.empty():
                            raise exception_queue.get()
                        
                        if not result_queue.empty():
                            return result_queue.get()
                        
                        raise TimeoutError(f"Function {func.__name__} returned no result")
                    else:
                        # No timeout - direct call
                        return func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay_seconds}s..."
                        )
                        time.sleep(delay_seconds)
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {e}"
                        )
                except TimeoutError as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} timed out for {func.__name__}. "
                            f"Retrying in {delay_seconds}s..."
                        )
                        time.sleep(delay_seconds)
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts timed out for {func.__name__}"
                        )
            
            # All retries exhausted
            raise last_exception
        
        return wrapper
    return decorator

