"""
In-memory cache for performance optimization.
TTL: 5 minutes
NO Redis, NO external dependencies - pure Python dict with timestamps.
"""

import time
from typing import Dict, Any, Optional
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class InMemoryCache:
    """
    Simple in-memory cache with TTL.
    Thread-safe using locks.
    """
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.
        
        Returns:
            Cached value or None if expired/not found
        """
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            if time.time() - entry["timestamp"] > self.ttl:
                # Expired - remove it
                del self.cache[key]
                return None
            
            return entry["value"]
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache with current timestamp.
        """
        with self.lock:
            self.cache[key] = {
                "value": value,
                "timestamp": time.time()
            }
    
    def clear(self, pattern: Optional[str] = None) -> None:
        """
        Clear cache entries.
        
        Args:
            pattern: If provided, only clear keys matching pattern (simple substring match)
        """
        with self.lock:
            if pattern:
                keys_to_remove = [k for k in self.cache.keys() if pattern in k]
                for key in keys_to_remove:
                    del self.cache[key]
            else:
                self.cache.clear()
    
    def cleanup_expired(self) -> None:
        """
        Remove expired entries (call periodically).
        """
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self.cache.items()
                if current_time - entry["timestamp"] > self.ttl
            ]
            for key in expired_keys:
                del self.cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")


# Global cache instance (5 minute TTL)
cache = InMemoryCache(ttl_seconds=300)


def get_cache_key(prefix: str, *args) -> str:
    """
    Generate cache key from prefix and arguments.
    
    Example:
        get_cache_key("kpi", batch_id, mode) -> "kpi:batch_id:mode"
    """
    return f"{prefix}:" + ":".join(str(arg) for arg in args)

