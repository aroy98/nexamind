# Implementation Plan: AI Knowledge Inbox

**Branch**: `001-ai-knowledge-inbox` | **Date**: 2026-08-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-ai-knowledge-inbox/spec.md`

## Summary

A single-user web app for saving notes/URLs and asking questions over them via RAG. Backend is FastAPI over SQLite (items + chunk embeddings in one file, brute-force cosine similarity for retrieval — no separate vector DB needed at this scale). Content is chunked with fixed-size overlapping windows, embedded locally with `sentence-transformers` (`all-MiniLM-L6-v2`, no external API needed for embeddings), and answered with Anthropic's `claude-haiku-4-5` given the top-k retrieved chunks. Frontend is a small React app (input form, item list, ask-question panel) talking to three endpoints: `POST /ingest`, `GET /items`, `POST /query`. Everything runs synchronously in-process — no queues, no auth, no extra infra — matching the assignment's explicit anti-overengineering constraint and 6–12 hour timebox.

## Technical Context

**Language/Version**: Python 3.11 (backend), Node 18+ / React 18 (frontend)

**Primary Dependencies**: FastAPI, uvicorn, `anthropic` SDK (answers), `sentence-transformers` (local embeddings), `requests` + `beautifulsoup4` (URL fetch/extract), Python stdlib `sqlite3`, `logging` (JSON formatter); React (Vite), fetch API — no state library needed (component state + one context is enough at this scope)

**Storage**: SQLite, single file (`inbox.db`) — `items` table + `chunks` table (embedding stored as a serialized float BLOB)

**Testing**: pytest for backend (route + retrieval unit tests); no frontend test framework added — YAGNI at this scope, manual verification via quickstart.md

**Target Platform**: Local dev / single-process server (Linux/macOS/Windows), single deployable unit

**Project Type**: Web application (backend + frontend)

**Performance Goals**: Interactive use by one user; query end-to-end (retrieve + LLM call) under ~15s per SC-002. No concurrency/throughput target.

**Constraints**: No auth, no Kubernetes, no background job/queue infra, no external vector DB — per assignment's "Avoid" list. Ingestion embeds synchronously (acceptable since content sizes are small and single-user).

**Scale/Scope**: Tens to low hundreds of items (per spec Assumptions) — brute-force in-process cosine similarity over all chunks is fast enough and needs no index.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Re-checked against `.specify/memory/constitution.md` v1.0.0 (ratified 2026-08-20, after this plan's initial draft). All five principles PASS with no changes to the technical approach:

| Principle | Status | Evidence |
|---|---|---|
| I. Simplicity First | PASS | No auth, no queues, no external vector DB; SQLite + brute-force cosine search in-process |
| II. Tradeoff Transparency | PASS | research.md records decision/rationale/alternatives + scale limits for chunking, embeddings, and vector storage |
| III. Debuggable by Default | PASS | `logging_config.py` (structured JSON logs); contracts/api.md defines 422/502 status codes and a uniform `{error, detail}` error shape |
| IV. Separation of Concerns | PASS | Backend split by pipeline stage (routes/ingestion/chunking/embeddings/retrieval/answering/storage/schemas) — no god files |
| V. Contract-First API Design | PASS | contracts/api.md specifies validated request/response shapes for all 3 endpoints; `POST /query` responses always include `sources` |

No violations — Complexity Tracking table remains intentionally omitted.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-knowledge-inbox/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/            # Phase 1 output (OpenAPI-style endpoint contracts)
└── tasks.md              # Phase 2 output (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py            # FastAPI app, route wiring, exception handlers, logging setup
│   ├── routes.py           # POST /ingest, GET /items, POST /query — thin handlers only
│   ├── ingestion.py        # note/URL validation, URL fetch + text extraction
│   ├── chunking.py         # fixed-size overlapping chunk splitter
│   ├── embeddings.py        # local sentence-transformers embedding calls (single item + batch)
│   ├── retrieval.py         # cosine similarity search over stored chunk vectors
│   ├── answering.py         # prompt assembly + Anthropic chat call + source citation shaping
│   ├── storage.py           # sqlite3 access: items/chunks CRUD, schema init
│   ├── schemas.py           # Pydantic request/response models
│   └── logging_config.py    # structured (JSON) logging setup
├── tests/
│   ├── test_routes.py
│   ├── test_chunking.py
│   └── test_retrieval.py
├── requirements.txt
└── inbox.db                # created at runtime, gitignored

frontend/
├── src/
│   ├── api.js              # fetch wrappers for the 3 endpoints
│   ├── App.jsx              # layout: input form + item list + ask panel
│   ├── components/
│   │   ├── AddItemForm.jsx
│   │   ├── ItemList.jsx
│   │   └── AskPanel.jsx
│   └── main.jsx
├── index.html
└── package.json
```

**Structure Decision**: Web application split (Option 2) — `backend/` (FastAPI) and `frontend/` (React), each independently runnable. Backend is organized by pipeline stage (ingestion → chunking → embeddings → retrieval → answering) rather than by generic MVC layers, since that mirrors the actual RAG data flow and keeps each file single-purpose without introducing service/repository abstraction layers the assignment explicitly warns against.

## Complexity Tracking

*No constitution violations to justify — table intentionally omitted.*
