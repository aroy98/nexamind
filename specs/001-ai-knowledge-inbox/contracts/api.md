# API Contracts: AI Knowledge Inbox

Base URL: `http://localhost:8000` (dev). JSON in, JSON out. No auth headers.

---

## POST /ingest

Save a note or URL. Server fetches+extracts content synchronously for URLs, chunks it, embeds the chunks, and persists everything before responding.

**Request**

```json
{
  "source_type": "note",
  "content": "Free text note..."
}
```

or

```json
{
  "source_type": "url",
  "content": "https://example.com/article"
}
```

`content` is the note text when `source_type = "note"`, or the URL string when `source_type = "url"`.

**Response — 201 Created**

```json
{
  "id": 12,
  "source_type": "url",
  "title": "Example Article",
  "source_url": "https://example.com/article",
  "created_at": "2026-08-20T10:15:00Z",
  "chunk_count": 4
}
```

**Errors**

| Status | Condition |
|---|---|
| 422 | `source_type` missing/invalid, or `content` empty/whitespace-only, or `content` is not a valid absolute URL when `source_type = "url"` |
| 502 | URL fetch failed (timeout, connection error, non-2xx, non-HTML content type) |

Note: embedding generation is local (no network call), so it is not a source of 502s here — only URL fetch can fail.

Error body shape (all error responses):

```json
{ "error": "human-readable message", "detail": "optional extra context" }
```

---

## GET /items

List all saved items, newest first. No embeddings/chunks in the payload — metadata only.

**Response — 200 OK**

```json
{
  "items": [
    {
      "id": 12,
      "source_type": "url",
      "title": "Example Article",
      "source_url": "https://example.com/article",
      "created_at": "2026-08-20T10:15:00Z"
    },
    {
      "id": 11,
      "source_type": "note",
      "title": "Meeting notes...",
      "source_url": null,
      "created_at": "2026-08-20T09:40:00Z"
    }
  ]
}
```

Empty inbox → `200 OK` with `{ "items": [] }` (not a 404).

---

## POST /query

Ask a question over saved content.

**Request**

```json
{ "question": "What did the article say about pricing?" }
```

**Response — 200 OK**

```json
{
  "answer": "The article states pricing starts at $10/month...",
  "sources": [
    {
      "item_id": 12,
      "title": "Example Article",
      "source_type": "url",
      "snippet": "...pricing starts at $10/month for the basic tier..."
    }
  ]
}
```

When no saved content is relevant (FR-010) or the inbox is empty:

```json
{
  "answer": "I don't have any saved content relevant to that question.",
  "sources": []
}
```

This is still `200 OK` — it's a valid, non-error outcome, not a failure.

**Errors**

| Status | Condition |
|---|---|
| 422 | `question` missing or empty/whitespace-only |
| 502 | Anthropic chat completion call failed (embedding is local, not a failure source) |

---

## Cross-cutting

- All 4xx/5xx responses use the `{ "error", "detail" }` shape above.
- All responses are `application/json`.
- Every request is logged (structured JSON) with: method, path, status, latency_ms, and — for `/ingest`/`/query` — item/chunk counts or retrieval hit counts as applicable.
