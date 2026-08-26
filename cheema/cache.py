from __future__ import annotations

import inspect
import time
from typing import Any, Callable, Optional

_MISSING = object()


class MemoryCache:
    """In-process key-value cache with per-entry TTL. Default backend for ResponseCacheMiddleware, and usable directly by app code."""

    def __init__(self, *, max_entries: int = 1024):
        self.max_entries = int(max_entries)
        self._store: dict[str, tuple[Optional[float], Any]] = {}

    async def get(self, key: str, default: Any = None) -> Any:
        entry = self._store.get(key)
        if entry is None:
            return default
        expires_at, value = entry
        if expires_at is not None and expires_at <= time.time():
            self._store.pop(key, None)
            return default
        return value

    async def set(self, key: str, value: Any, *, ttl: Optional[float] = None) -> None:
        expires_at = (time.time() + ttl) if ttl is not None else None
        self._store[key] = (expires_at, value)
        self._prune()

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def clear(self) -> None:
        self._store.clear()

    async def get_or_set(self, key: str, factory: Callable[[], Any], *, ttl: Optional[float] = None) -> Any:
        value = await self.get(key, _MISSING)
        if value is not _MISSING:
            return value
        value = factory()
        if inspect.isawaitable(value):
            value = await value
        await self.set(key, value, ttl=ttl)
        return value

    def _prune(self):
        if len(self._store) <= self.max_entries:
            return
        finite = [(k, expires_at) for k, (expires_at, _v) in self._store.items() if expires_at is not None]
        oldest_key = min(finite, key=lambda x: x[1])[0] if finite else next(iter(self._store))
        self._store.pop(oldest_key, None)
