import numpy as np

from app.storage import get_all_chunks_with_items

# ponytail: naive fixed threshold tuned by eye for normalized MiniLM embeddings;
# revisit with real query/relevance data if false negatives/positives show up.
MIN_SIMILARITY = 0.25


def top_k_chunks(query_embedding: list[float], k: int = 5) -> list[dict]:
    rows = get_all_chunks_with_items()
    if not rows:
        return []

    query_vec = np.asarray(query_embedding, dtype=np.float32)
    scored = []
    for row in rows:
        similarity = float(np.dot(row["embedding"], query_vec))
        if similarity >= MIN_SIMILARITY:
            scored.append({**row, "similarity": similarity})

    scored.sort(key=lambda r: r["similarity"], reverse=True)
    return scored[:k]
