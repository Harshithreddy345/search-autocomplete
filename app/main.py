from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.trie import Trie
from app.seed import seed_trie
from app.routers import autocomplete, words, analytics

# Global Trie instance — shared across all requests
trie = Trie()

app = FastAPI(
    title="Search Autocomplete API",
    description="Real-time search autocomplete using Trie + Redis caching",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    """Preload Trie with seed data on startup."""
    seed_trie(trie)
    print(f"✓ Trie loaded with {trie.count_words()} words")


# Pass trie instance to routers via app state
app.state.trie = trie

app.include_router(autocomplete.router, tags=["Autocomplete"])
app.include_router(words.router,        prefix="/words",     tags=["Words"])
app.include_router(analytics.router,    prefix="/analytics", tags=["Analytics"])

app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
        "words_in_trie": trie.count_words(),
    }
