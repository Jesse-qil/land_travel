"""LRU 内存缓存封装"""
import time
from collections import OrderedDict
from threading import Lock
from typing import Any


class CacheRepository:
    def __init__(self, max_size: int = 500):
        self._store: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = Lock()
        self._max_size = max_size

    async def get(self, key: str) -> Any | None:
        with self._lock:
            if key not in self._store:
                return None
            value, expire_at = self._store[key]
            if expire_at and time.time() > expire_at:
                del self._store[key]
                return None
            self._store.move_to_end(key)
            return value

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        with self._lock:
            expire_at = time.time() + ttl if ttl > 0 else 0
            self._store[key] = (value, expire_at)
            self._store.move_to_end(key)
            while len(self._store) > self._max_size:
                self._store.popitem(last=False)

    async def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    async def clear_prefix(self, prefix: str) -> None:
        with self._lock:
            keys = [k for k in self._store if k.startswith(prefix)]
            for k in keys:
                del self._store[k]


cache_repo = CacheRepository()
