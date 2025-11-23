"""In-memory caching implementation."""

from typing import Optional, Any
import time

class MemoryCache:
    """In-memory caching implementation."""

    def __init__(self):
        self.cache: dict[str, dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache if not expired."""
        entry = self.cache.get(key)
        if not entry:
            return None

        if entry["expires_at"] < time.time():
            del self.cache[key]
            return None

        return entry["value"]

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set a value with TTL (seconds)."""
        expires_at = time.time() + ttl
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at,
        }