"""Caching layer using diskcache."""

import hashlib
from typing import Any

import diskcache

from ms_lookup.config import CACHE_DIR, CACHE_TTL_DOCS, CACHE_TTL_DEEP


def _get_cache() -> diskcache.Cache:
    """Get or create cache instance."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return diskcache.Cache(str(CACHE_DIR))


def _make_key(command: str, *args: str, max_tokens: int | None = None) -> str:
    """Create cache key from command, args, and optionally max_tokens."""
    key_parts = [command] + list(args)
    if max_tokens is not None:
        key_parts.append(str(max_tokens))
    key_string = ":".join(key_parts)
    key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
    return f"{command}:{key_hash}"


def get_cached(command: str, *args: str, max_tokens: int | None = None) -> Any | None:
    """Get cached result if exists and not expired."""
    cache = _get_cache()
    key = _make_key(command, *args, max_tokens=max_tokens)
    return cache.get(key)


def set_cached(command: str, *args: str, max_tokens: int | None = None, value: Any) -> None:
    """Cache a result with appropriate TTL."""
    cache = _get_cache()
    key = _make_key(command, *args, max_tokens=max_tokens)

    # Select TTL based on command
    ttl = CACHE_TTL_DOCS if command == "docs" else CACHE_TTL_DEEP

    cache.set(key, value, expire=ttl)


def clear_cache() -> None:
    """Clear all cached entries."""
    cache = _get_cache()
    cache.clear()
