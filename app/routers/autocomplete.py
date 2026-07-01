from fastapi import APIRouter, Request, Query, HTTPException
from app import cache
import time

router = APIRouter()


@router.get("/autocomplete")
def autocomplete(
    request: Request,
    q: str = Query(..., min_length=1, max_length=100, description="Search prefix"),
    top_k: int = Query(5, ge=1, le=20, description="Number of suggestions to return"),
):
    """
    Get top-k autocomplete suggestions for a search prefix.

    - Checks Redis cache first (O(1))
    - Falls back to Trie search if cache miss (O(L + N))
    - Caches result for future requests
    - Increments search frequency for ranking
    """
    prefix = q.strip().lower()
    if not prefix:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    start_time = time.time()

    # 1. Check Redis cache
    cached = cache.get_cached_suggestions(prefix, top_k)
    if cached is not None:
        return {
            "prefix": prefix,
            "suggestions": cached,
            "source": "cache",
            "latency_ms": round((time.time() - start_time) * 1000, 2),
        }

    # 2. Cache miss — query Trie
    trie = request.app.state.trie
    suggestions = trie.get_suggestions(prefix, top_k)

    # 3. Store in Redis for next time
    cache.set_cached_suggestions(prefix, top_k, suggestions)

    return {
        "prefix": prefix,
        "suggestions": suggestions,
        "source": "trie",
        "latency_ms": round((time.time() - start_time) * 1000, 2),
    }


@router.post("/search")
def search(
    request: Request,
    q: str = Query(..., min_length=1, description="Exact search term"),
):
    """
    Record a search. Increments the word's frequency in the Trie
    so it ranks higher in future suggestions.
    """
    word = q.strip().lower()
    trie = request.app.state.trie
    trie.increment_frequency(word)
    cache.invalidate_prefix_cache(word)  # invalidate stale cache
    return {"message": f"Recorded search for '{word}'"}
