# Quickstart: AI Knowledge Inbox

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package/venv manager), Node 18+
- An Anthropic API key with access to `claude-haiku-4-5`
- No embeddings API key needed — embeddings run locally via `sentence-transformers` (first run downloads the ~80MB `all-MiniLM-L6-v2` model)

## Setup

```bash
# backend
cd backend
uv sync
setx ANTHROPIC_API_KEY "sk-ant-..."               # or export on macOS/Linux, or put it in backend/.env
uv run uvicorn app.main:app --reload --port 8000

# frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Validation scenarios

Run these against a running backend (`http://localhost:8000`) to confirm the feature works end-to-end. Full request/response shapes: [contracts/api.md](./contracts/api.md).

### 1. Save a note (User Story 1)

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"source_type":"note","content":"Our refund policy allows returns within 30 days of purchase."}'
```

Expect `201` with a `chunk_count >= 1`.

### 2. Save a URL (User Story 1)

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"source_type":"url","content":"https://example.com"}'
```

Expect `201`. Try a dead URL (e.g. `https://this-domain-does-not-exist-xyz.test`) and expect `502` with an `error` message, not a crash.

### 3. List items (User Story 3)

```bash
curl http://localhost:8000/items
```

Expect both saved items, newest first, with correct `source_type`.

### 4. Ask a question answerable from saved content (User Story 2)

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"How long do I have to return something?"}'
```

Expect `200`, an `answer` mentioning 30 days, and `sources` citing the refund-policy note's `item_id`.

### 5. Ask an unrelated question (edge case)

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the capital of France?"}'
```

Expect `200` with an answer indicating no relevant saved content, and `sources: []` — not a fabricated answer.

### 6. Empty-inbox query (edge case)

Delete `backend/inbox.db`, restart the server, and repeat step 4's request against the empty inbox. Expect the same "nothing relevant" response without a provider call (check logs — no embedding/chat request should fire for zero stored chunks).

### 7. Frontend smoke test

Open the Vite dev URL (default `http://localhost:5173`): add a note via the form, confirm it appears in the list, ask a question, confirm the answer + source snippet render.
