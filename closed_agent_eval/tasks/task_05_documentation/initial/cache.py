from typing import Any, Optional
from datetime import datetime, timedelta
from threading import Lock


class TTLCache:
    def __init__(self, default_ttl: int = 300):
        self._cache = {}
        self._lock = Lock()
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                return None
            value, expiry = self._cache[key]
            if datetime.now() > expiry:
                del self._cache[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self._lock:
            expiry = datetime.now() + timedelta(seconds=ttl or self._default_ttl)
            self._cache[key] = (value, expiry)

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
