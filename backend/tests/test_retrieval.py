import numpy as np

from app import retrieval


def _row(item_id, vec, similarity_tag):
    return {
        "id": item_id,
        "item_id": item_id,
        "chunk_text": f"chunk-{similarity_tag}",
        "embedding": np.asarray(vec, dtype=np.float32),
        "title": f"item-{item_id}",
        "source_type": "note",
    }


def test_empty_chunk_set_returns_no_matches(monkeypatch):
    monkeypatch.setattr(retrieval, "get_all_chunks_with_items", lambda: [])
    assert retrieval.top_k_chunks([1.0, 0.0]) == []


def test_top_k_orders_by_similarity_and_applies_threshold(monkeypatch):
    rows = [
        _row(1, [1.0, 0.0], "high"),  # similarity 1.0 to query
        _row(2, [0.9, 0.1], "medium"),  # similarity ~0.9
        _row(3, [-1.0, 0.0], "irrelevant"),  # similarity -1.0, below threshold
    ]
    monkeypatch.setattr(retrieval, "get_all_chunks_with_items", lambda: rows)

    results = retrieval.top_k_chunks([1.0, 0.0], k=5)

    assert [r["item_id"] for r in results] == [1, 2]
    assert results[0]["similarity"] >= results[1]["similarity"]
