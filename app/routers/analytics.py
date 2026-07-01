from fastapi import APIRouter, Request
from app import cache

router = APIRouter()


@router.get("/stats")
def get_stats(request: Request):
    """Get Trie and cache statistics."""
    trie = request.app.state.trie
    cache_stats = cache.get_cache_stats()

    return {
        "trie": {
            "total_words": trie.count_words(),
        },
        "cache": cache_stats,
    }


@router.delete("/cache")
def flush_cache():
    """Flush all Redis autocomplete cache entries."""
    cache.flush_cache()
    return {"message": "Cache flushed successfully"}
