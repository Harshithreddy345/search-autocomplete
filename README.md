# 🔍 Search Autocomplete System

A real-time search autocomplete engine built with a **Trie data structure** and **Redis caching**, served via a **FastAPI REST API**. Inspired by how Google and Amazon implement search suggestions.

## 🧠 How It Works

```
User types "py" →
  1. Check Redis cache → HIT → return instantly (O(1))
  2. Cache MISS → traverse Trie from "py" node → collect all words → sort by frequency
  3. Cache result in Redis (TTL: 5 min)
  4. Return top-k suggestions ranked by search frequency
```

## ⚡ Time Complexities

| Operation | Time Complexity |
|---|---|
| Insert word | O(L) — L = word length |
| Prefix search | O(L + N) — N = nodes in subtree |
| Cache lookup | O(1) |
| Delete word | O(L) |

## 🏗️ Architecture

```
Client → FastAPI → Redis Cache (hit) → Return
                 → Trie (miss)  → Cache → Return
```

## 🚀 Quick Start

```bash
# Run with Docker (Redis included)
docker-compose up --build

# Or run locally
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/autocomplete?q=py&top_k=5` | Get top-k suggestions for prefix |
| POST | `/search?q=python` | Record a search (boosts frequency) |
| POST | `/words/` | Insert a word with frequency |
| POST | `/words/bulk` | Bulk insert words |
| DELETE | `/words/` | Delete a word |
| GET | `/analytics/stats` | Trie size + cache stats |
| DELETE | `/analytics/cache` | Flush Redis cache |

## 💡 Example

```bash
GET /autocomplete?q=py&top_k=3
```

```json
{
  "prefix": "py",
  "suggestions": [
    {"word": "python", "frequency": 9500},
    {"word": "python tutorial", "frequency": 8200},
    {"word": "pytorch", "frequency": 5000}
  ],
  "source": "trie",
  "latency_ms": 1.2
}
```

Second call for same prefix:
```json
{
  "source": "cache",
  "latency_ms": 0.3
}
```

## 🧪 Run Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## 📈 Resume Bullet Points

- *Built a search autocomplete system using a custom Trie implementation with O(L) insert/search complexity, serving top-k frequency-ranked suggestions via FastAPI*
- *Integrated Redis caching layer reducing repeated prefix query latency by ~75% with automatic cache invalidation on word insertion*
- *Preloaded Trie with 60+ real-world search terms with frequency weights; supports dynamic insertion, deletion, and bulk loading*
- *Wrote 15 unit and integration tests covering Trie operations, frequency ranking, cache behavior, and all API endpoints*
