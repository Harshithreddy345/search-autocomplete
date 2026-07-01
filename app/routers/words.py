from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from app import cache

router = APIRouter()


class WordInsert(BaseModel):
    word: str
    frequency: int = 1


class WordDelete(BaseModel):
    word: str


@router.post("/", status_code=201)
def insert_word(payload: WordInsert, request: Request):
    """
    Insert a new word into the Trie with an optional frequency.
    Invalidates Redis cache for all prefixes of this word.
    """
    word = payload.word.strip().lower()
    if not word:
        raise HTTPException(status_code=400, detail="Word cannot be empty")

    trie = request.app.state.trie
    trie.insert(word, payload.frequency)
    cache.invalidate_prefix_cache(word)

    return {
        "message": f"'{word}' inserted successfully",
        "total_words": trie.count_words(),
    }


@router.post("/bulk", status_code=201)
def insert_bulk(payload: list[WordInsert], request: Request):
    """Insert multiple words at once."""
    trie = request.app.state.trie
    inserted = []
    for item in payload:
        word = item.word.strip().lower()
        if word:
            trie.insert(word, item.frequency)
            cache.invalidate_prefix_cache(word)
            inserted.append(word)

    return {
        "inserted": len(inserted),
        "words": inserted,
        "total_words": trie.count_words(),
    }


@router.delete("/")
def delete_word(payload: WordDelete, request: Request):
    """Delete a word from the Trie."""
    word = payload.word.strip().lower()
    trie = request.app.state.trie
    deleted = trie.delete(word)

    if not deleted:
        raise HTTPException(status_code=404, detail=f"'{word}' not found in Trie")

    cache.invalidate_prefix_cache(word)
    return {"message": f"'{word}' deleted successfully"}
