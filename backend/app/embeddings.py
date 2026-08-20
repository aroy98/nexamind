_model = None


def _get_model():
    # ponytail: first call per process pays a ~10-15s HuggingFace Hub metadata
    # check even when the model is already cached locally; acceptable for a
    # single dev process, revisit (HF_HUB_OFFLINE=1 post-cache) if cold-start
    # latency on repeated restarts becomes a real problem.
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    vectors = _get_model().encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return vectors.tolist()
