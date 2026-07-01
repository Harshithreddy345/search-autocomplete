"""
Redis Cache Layer for Search Autocomplete.

Strategy:
- Cache top-k suggestions per prefix with TTL
- Invalidate cache when new words are inserted
- Graceful fallback to Trie if Redis unavailable
"""

import json
import os
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = 300  # 5 minutes

try:
    r = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    r.ping()
    REDIS_AVAILABLE = True
except Exception:
    r = None
    REDIS_AVAILABLE = False


def _cache_key(prefix: str, top_k: int) -> str:
    return f"autocomplete:{prefix.lower()}:{top_k}"


def get_cached_suggestions(prefix: str, top_k: int) -> list | None:
    """Return cached suggestions or None if not cached."""
    if not r:
        return None
    try:
        data = r.get(_cache_key(prefix, top_k))
        if data:
            return json.loads(data)
    except Exception:
        pass
    return None


def set_cached_suggestions(prefix: str, top_k: int, suggestions: list):
    """Cache suggestions for a prefix."""
    if not r:
        return
    try:
        r.setex(_cache_key(prefix, top_k), CACHE_TTL, json.dumps(suggestions))
    except Exception:
        pass


def invalidate_prefix_cache(word: str):
    """
    When a new word is inserted, invalidate all cached prefixes of that word.
    e.g. inserting 'apple' invalidates 'a', 'ap', 'app', 'appl', 'apple'
    """
    if not r:
        return
    try:
        for i in range(1, len(word) + 1):
            prefix = word[:i].lower()
            pattern = f"autocomplete:{prefix}:*"
            keys = r.keys(pattern)
            if keys:
                r.delete(*keys)
    except Exception:
        pass


def get_cache_stats() -> dict:
    """Return Redis cache statistics."""
    if not r:
        return {"redis_available": False}
    try:
        info = r.info("stats")
        keys = r.dbsize()
        return {
            "redis_available": True,
            "total_cached_keys": keys,
            "cache_hits": info.get("keyspace_hits", 0),
            "cache_misses": info.get("keyspace_misses", 0),
        }
    except Exception:
        return {"redis_available": False}


def flush_cache():
    """Clear all autocomplete cache entries."""
    if not r:
        return
    try:
        keys = r.keys("autocomplete:*")
        if keys:
            r.delete(*keys)
    except Exception:
        pass
