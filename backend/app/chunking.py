CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150


def chunk_text(text: str) -> list[str]:
    """Fixed-size overlapping character windows. See research.md#chunking-strategy."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= CHUNK_SIZE:
        return [text]

    chunks = []
    start = 0
    step = CHUNK_SIZE - CHUNK_OVERLAP
    while start < len(text):
        chunks.append(text[start : start + CHUNK_SIZE])
        start += step
    return chunks


if __name__ == "__main__":
    short = "hello world"
    assert chunk_text(short) == [short]
    assert chunk_text("") == []
    long_text = "x" * 4000
    result = chunk_text(long_text)
    assert len(result) > 1
    assert all(len(c) <= CHUNK_SIZE for c in result)
    # overlap: end of chunk N should reappear at the start of chunk N+1
    assert result[0][-CHUNK_OVERLAP:] == result[1][:CHUNK_OVERLAP]
    print("chunking self-check OK")
