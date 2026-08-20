# Tasks: AI Knowledge Inbox

**Input**: Design documents from `specs/001-ai-knowledge-inbox/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [data-model.md](./data-model.md), [contracts/api.md](./contracts/api.md), [research.md](./research.md)

**Tests**: Minimal — one focused test file per pipeline stage that has real branching logic (chunking, retrieval), plus a route smoke test. No per-endpoint TDD suite; this is a timeboxed exercise, not a library.

## Phase 1: Setup

- [ ] T001 Create `backend/` and `frontend/` directories per plan.md structure; add root `.gitignore` covering `backend/.venv/`, `backend/inbox.db`, `frontend/node_modules/`, `.env`
- [ ] T002 Create `backend/requirements.txt` (fastapi, uvicorn, anthropic, sentence-transformers, requests, beautifulsoup4, numpy, pytest, python-dotenv) and `backend/app/__init__.py`
- [ ] T003 [P] Scaffold `frontend/` with Vite React template (`package.json`, `index.html`, `src/main.jsx`)
- [ ] T004 [P] Add `backend/app/logging_config.py`: stdlib `logging` + JSON `Formatter`, one `configure_logging()` call used by `main.py`

## Phase 2: Foundational (blocking prerequisites)

**Purpose**: Storage schema, embedding/chunking primitives, and shared request/response models that every user story's endpoint depends on.

- [ ] T005 Implement `backend/app/storage.py`: SQLite connection helper + `init_db()` creating `items`/`chunks` tables and index per [data-model.md](./data-model.md)
- [ ] T006 [P] Implement `backend/app/schemas.py`: Pydantic models for `IngestRequest`, `IngestResponse`, `ItemSummary`, `ItemsResponse`, `QueryRequest`, `QueryResponse`, `SourceSnippet`, `ErrorResponse` per [contracts/api.md](./contracts/api.md)
- [ ] T007 [P] Implement `backend/app/chunking.py`: `chunk_text(text: str) -> list[str]` — fixed-size (~1500 char) windows with ~150-char overlap per [research.md](./research.md#chunking-strategy)
- [ ] T008 [P] Implement `backend/app/embeddings.py`: `embed_texts(texts: list[str]) -> list[list[float]]` wrapping a lazily-loaded local `sentence-transformers` `all-MiniLM-L6-v2` model (no network call, no `ProviderError` path here)
- [ ] T009 Implement `backend/app/main.py`: FastAPI app instance, `init_db()` on startup, global exception handler mapping `ValueError`→422 and `ProviderError`→502 to the `{error, detail}` shape, CORS enabled for the Vite dev origin
- [ ] T010 [P] Write `backend/tests/test_chunking.py`: assert overlap, boundary behavior on short text (single chunk), and long text (multiple chunks)

**Checkpoint**: Server boots, DB schema exists, chunking/embedding primitives are unit-testable in isolation.

---

## Phase 3: User Story 1 — Save content to the inbox (P1) 🎯 MVP

**Goal**: User can save a text note or a URL; content is fetched (if URL), chunked, embedded, and persisted.

**Independent Test**: `POST /ingest` a note and a URL; confirm `201` responses and that `GET /items` (built in US3 but trivially stubbable) reflects both. Per quickstart.md steps 1–2.

- [ ] T011 [US1] Implement `backend/app/ingestion.py`: `validate_and_extract(source_type, content) -> (raw_content, source_url, title)` — trims/validates note text, validates URL shape, fetches via `requests` (timeout) + `BeautifulSoup` text extraction, raises `ValueError` (422) or `ProviderError` (502) per [contracts/api.md](./contracts/api.md#post-ingest)
- [ ] T012 [US1] Implement item+chunk persistence in `backend/app/storage.py`: `insert_item(...) -> item_id`, `insert_chunks(item_id, chunks, embeddings)`
- [ ] T013 [US1] Implement `POST /ingest` handler in `backend/app/routes.py`: calls ingestion → chunking → embeddings → storage, returns `IngestResponse` with `chunk_count`; logs item id + chunk count
- [ ] T014 [P] [US1] Write `backend/tests/test_routes.py::test_ingest_note` and `::test_ingest_invalid_url`: assert 201 on valid note, 422 on empty content
- [ ] T015 [P] [US1] Implement `frontend/src/api.js`: `ingestItem({source_type, content})` fetch wrapper
- [ ] T016 [US1] Implement `frontend/src/components/AddItemForm.jsx`: note/URL toggle, textarea/input, submit calling `ingestItem`, surfaces error message on failure

**Checkpoint**: Notes and URLs can be saved end-to-end from the UI; invalid input and dead URLs show clear errors instead of crashing.

---

## Phase 4: User Story 2 — Ask a question over saved content (P1) 🎯 MVP

**Goal**: User asks a question and gets an answer with cited sources, grounded only in saved content.

**Independent Test**: With US1's items saved, `POST /query` a question answerable from them; confirm answer text + non-empty `sources`. Ask an unrelated question; confirm "no relevant content" response, not a fabrication. Per quickstart.md steps 4–6.

- [ ] T017 [US2] Implement `backend/app/retrieval.py`: `top_k_chunks(query_embedding, k=5) -> list[ChunkMatch]` — load all `(id, item_id, embedding)` from `storage.py`, compute cosine similarity via NumPy, return top-k above a minimum-similarity threshold (below threshold ⇒ empty list)
- [ ] T018 [US2] Implement `backend/app/answering.py`: `answer_question(question, matches) -> (answer, sources)` — if `matches` empty, return the fixed "no relevant content" answer without calling the LLM (per FR-010 and quickstart.md step 6); otherwise assemble a context prompt from matched chunks + question, call Anthropic `claude-haiku-4-5`, raising `ProviderError` (502) on failure, shape `sources` from the matched chunks/items
- [ ] T019 [US2] Implement `POST /query` handler in `backend/app/routes.py`: validates non-empty question (422), embeds question, calls `retrieval` → `answering`, returns `QueryResponse`; logs question length + retrieval hit count
- [ ] T020 [P] [US2] Write `backend/tests/test_retrieval.py`: assert top-k ordering by similarity and empty-result behavior on an empty chunk set
- [ ] T021 [P] [US2] Write `backend/tests/test_routes.py::test_query_no_relevant_content` and `::test_query_empty_question`
- [ ] T022 [P] [US2] Implement `frontend/src/api.js`: `askQuestion(question)` fetch wrapper
- [ ] T023 [US2] Implement `frontend/src/components/AskPanel.jsx`: question input, submit calling `askQuestion`, renders answer text + source snippet list (item title + snippet), loading/error states

**Checkpoint**: Full RAG loop works from the UI — save something, ask about it, get a grounded, cited answer; unrelated questions don't fabricate.

---

## Phase 5: User Story 3 — Browse saved items (P2)

**Goal**: User sees everything saved, newest-first, with type and timestamp.

**Independent Test**: Save several mixed items; `GET /items` returns all with correct type/timestamp ordering. Per quickstart.md step 3.

- [ ] T024 [US3] Implement `list_items()` in `backend/app/storage.py`: `SELECT` from `items` ordered by `created_at DESC`, mapped to `ItemSummary` (no raw content/embeddings in payload)
- [ ] T025 [US3] Implement `GET /items` handler in `backend/app/routes.py`: returns `ItemsResponse`; `200` with empty list when no items exist
- [ ] T026 [P] [US3] Write `backend/tests/test_routes.py::test_list_items_empty_and_populated`
- [ ] T027 [US3] Implement `frontend/src/components/ItemList.jsx`: renders items with type badge + relative/ISO timestamp, empty-state message
- [ ] T028 [US3] Wire `frontend/src/App.jsx`: compose `AddItemForm` + `ItemList` + `AskPanel`, refetch items after a successful ingest, share item list state via `useState`/props (no state library)

**Checkpoint**: Full app assembled — add, browse, ask — matches quickstart.md step 7 end-to-end.

---

## Phase 6: Polish & Cross-Cutting

- [ ] T029 [P] Add request logging middleware in `backend/app/main.py`: method, path, status, latency_ms per request (structured JSON via T004's logger)
- [ ] T030 [P] Write `backend/README.md` (or root `README.md`) covering setup (mirrors quickstart.md), plus the required **tradeoffs section**: chunking rationale, vector store choice, what breaks at scale, what changes for production — summarized from [research.md](./research.md)
- [ ] T031 Run through quickstart.md end-to-end (all 7 scenarios) manually; fix any gaps found
- [ ] T032 [P] Add `backend/.env.example` documenting `ANTHROPIC_API_KEY`

## Dependencies & Execution Order

- **Phase 1 (Setup)** → **Phase 2 (Foundational)**: no dependencies, must finish first — everything else needs the DB schema and chunking/embedding primitives.
- **Phase 3 (US1)** depends on Phase 2. Delivers a working save flow — this alone is a demoable slice (data goes in, is visible via direct DB/API inspection even before US3's list UI).
- **Phase 4 (US2)** depends on Phase 2 (retrieval/answering are independent of US1's route code, but need chunks to exist in the DB to be meaningfully tested — practically sequenced after US1).
- **Phase 5 (US3)** depends on Phase 2 only; independent of US1/US2 logic but most naturally built after US1 so there's something to list.
- **Phase 6 (Polish)** depends on all user stories being complete.

Suggested build order: Setup → Foundational → US1 → US2 → US3 → Polish (matches priorities: US1 and US2 are both P1/MVP-critical; US3 is P2).

## Parallel Execution Examples

Within Phase 2, T006/T007/T008/T010 touch different files and can run in parallel once T005 exists.

Within Phase 3, T014 (test) and T015 (frontend api.js) can run in parallel with each other after T013 lands.

Within Phase 4, T020/T021/T022 can run in parallel once T017–T019 land.

## Suggested MVP Scope

**Phase 1 + 2 + 3 + 4** (Setup, Foundational, US1, US2) is the minimum viable product: save content, ask questions, get cited answers. US3 (item browsing) and Phase 6 (polish/docs) round it out to match the full assignment brief but aren't required for the core RAG loop to be demoable.
