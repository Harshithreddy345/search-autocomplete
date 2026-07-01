import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.trie import Trie

client = TestClient(app)


# ── TRIE UNIT TESTS ──

def test_trie_insert_and_search():
    t = Trie()
    t.insert("apple", 10)
    t.insert("app", 5)
    results = t.get_suggestions("app")
    words = [r["word"] for r in results]
    assert "apple" in words
    assert "app" in words


def test_trie_frequency_ranking():
    t = Trie()
    t.insert("python", 100)
    t.insert("pytorch", 50)
    t.insert("pypy", 10)
    results = t.get_suggestions("py", top_k=3)
    assert results[0]["word"] == "python"  # highest frequency first


def test_trie_prefix_not_found():
    t = Trie()
    t.insert("apple")
    results = t.get_suggestions("xyz")
    assert results == []


def test_trie_delete():
    t = Trie()
    t.insert("apple")
    t.insert("app")
    deleted = t.delete("apple")
    assert deleted is True
    results = t.get_suggestions("app")
    words = [r["word"] for r in results]
    assert "apple" not in words
    assert "app" in words


def test_trie_case_insensitive():
    t = Trie()
    t.insert("Python")
    results = t.get_suggestions("PY")
    assert len(results) > 0
    assert results[0]["word"] == "python"


def test_trie_top_k():
    t = Trie()
    for i in range(10):
        t.insert(f"word{i}", i)
    results = t.get_suggestions("word", top_k=3)
    assert len(results) == 3


# ── API TESTS ──

def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_api_autocomplete():
    res = client.get("/autocomplete?q=py")
    assert res.status_code == 200
    data = res.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0


def test_api_autocomplete_no_results():
    res = client.get("/autocomplete?q=zzzzz")
    assert res.status_code == 200
    assert res.json()["suggestions"] == []


def test_api_insert_word():
    res = client.post("/words/", json={"word": "blockchain", "frequency": 500})
    assert res.status_code == 201
    # Now search for it
    res2 = client.get("/autocomplete?q=block")
    words = [s["word"] for s in res2.json()["suggestions"]]
    assert "blockchain" in words


def test_api_insert_bulk():
    res = client.post("/words/bulk", json=[
        {"word": "kubernetes", "frequency": 300},
        {"word": "kafka", "frequency": 200},
    ])
    assert res.status_code == 201
    assert res.json()["inserted"] == 2


def test_api_delete_word():
    client.post("/words/", json={"word": "deleteme", "frequency": 100})
    res = client.request("DELETE", "/words/", json={"word": "deleteme"})
    assert res.status_code == 200


def test_api_delete_nonexistent():
    res = client.request("DELETE", "/words/", json={"word": "doesnotexist123"})
    assert res.status_code == 404


def test_api_stats():
    res = client.get("/analytics/stats")
    assert res.status_code == 200
    assert "trie" in res.json()
