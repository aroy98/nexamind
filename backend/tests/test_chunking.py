from app.chunking import CHUNK_OVERLAP, CHUNK_SIZE, chunk_text


def test_empty_text_yields_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_short_text_is_single_chunk():
    assert chunk_text("hello world") == ["hello world"]


def test_long_text_splits_with_overlap():
    long_text = "x" * 4000
    chunks = chunk_text(long_text)
    assert len(chunks) > 1
    assert all(len(c) <= CHUNK_SIZE for c in chunks)
    assert chunks[0][-CHUNK_OVERLAP:] == chunks[1][:CHUNK_OVERLAP]
