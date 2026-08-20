# Data Model: AI Knowledge Inbox

## Entities

### Item

Represents one saved note or URL.

| Field | Type | Notes |
|---|---|---|
| `id` | INTEGER PK, autoincrement | |
| `source_type` | TEXT, `'note'` \| `'url'` | validated on write |
| `raw_content` | TEXT | note body, or extracted page text for URLs |
| `source_url` | TEXT, nullable | set only when `source_type = 'url'` |
| `title` | TEXT, nullable | page `<title>` for URLs, or first ~60 chars of note text |
| `created_at` | TEXT (ISO-8601 UTC) | set server-side at insert |

Validation (FR-001, FR-002, FR-004):
- `note`: `raw_content` non-empty after trim, length ≤ 50,000 chars.
- `url`: must parse as a valid absolute HTTP(S) URL before fetch is attempted; fetch failure (timeout, non-2xx, non-HTML) → reject, no row written.

### Chunk

A retrievable slice of an Item's content, with its embedding.

| Field | Type | Notes |
|---|---|---|
| `id` | INTEGER PK, autoincrement | |
| `item_id` | INTEGER, FK → `items.id`, `ON DELETE CASCADE` | |
| `chunk_index` | INTEGER | 0-based position within the item |
| `chunk_text` | TEXT | the slice used for embedding + shown as the cited snippet |
| `embedding` | BLOB | float32 384-dim vector from local `all-MiniLM-L6-v2` (`sentence-transformers`), packed via `numpy.tobytes()` |

Relationship: one Item → many Chunks (1:N). Chunks are created at ingest time and never updated in place — re-ingesting isn't in scope (no edit/update endpoint).

### Query / Answer (not persisted)

Conceptual only — modeled as request/response shapes, not stored:

- **Query**: `{ question: str }`
- **Answer**: `{ answer: str, sources: [{ item_id, title, source_type, snippet }] }`

No persistence requirement in the spec (Assumptions: only cross-request survival within one running instance is required); query history storage is out of scope for v1.

## SQLite schema (`storage.py`)

```sql
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL CHECK (source_type IN ('note', 'url')),
    raw_content TEXT NOT NULL,
    source_url TEXT,
    title TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding BLOB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chunks_item_id ON chunks(item_id);
```

No separate vector index — `retrieval.py` loads all `(id, item_id, embedding)` rows, computes cosine similarity in Python/NumPy against the query embedding, and takes the top-k. See [research.md](./research.md) for why this is sufficient at target scale.
