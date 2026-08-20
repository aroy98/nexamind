# Feature Specification: AI Knowledge Inbox

**Feature Branch**: `001-ai-knowledge-inbox`

**Created**: 2026-08-20

**Status**: Draft

**Input**: User description: "Build a minimal \"AI Knowledge Inbox\" — a single-user, no-auth web app for saving notes/URLs and asking questions over them via RAG. Content ingestion (text notes + URLs, server-side fetch), semantic search + RAG (chunking, embeddings, vector storage, retrieval, LLM answer with cited sources), React frontend, REST API (POST /ingest, GET /items, POST /query). Non-functional: structured logging, clear errors, sensible status codes, separation of concerns. Stack: FastAPI + OpenAI + SQLite + React. No auth, no k8s, no overengineering. Timeboxed 6-12 hour interview assignment."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Save content to the inbox (Priority: P1)

A user pastes a short text note or a URL into the app and saves it, so it becomes part of their searchable knowledge base.

**Why this priority**: Without saved content there is nothing to search or ask questions about — this is the foundation everything else builds on.

**Independent Test**: Submit a text note and a URL through the input form; confirm both appear in the saved items list with correct metadata (timestamp, source type).

**Acceptance Scenarios**:

1. **Given** the inbox is empty, **When** the user submits a plain-text note, **Then** the note is saved and appears in the items list with a timestamp and "note" source type.
2. **Given** the inbox is empty, **When** the user submits a valid URL, **Then** the server fetches the page content, saves it, and the item appears in the list with a timestamp and "url" source type.
3. **Given** the user submits a URL that cannot be fetched (dead link, timeout, non-HTML content), **When** the save is attempted, **Then** the user sees a clear error message and no partial/corrupt item is saved.

---

### User Story 2 - Ask a question over saved content (Priority: P1)

A user types a natural-language question and receives an answer synthesized from their saved notes/URLs, along with the source snippets the answer was drawn from.

**Why this priority**: This is the core value proposition of the product — turning saved content into answerable knowledge. Without it, the app is just a note list.

**Independent Test**: With at least one saved item containing known content, ask a question whose answer is contained in that content; verify the returned answer is correct and cites the source item.

**Acceptance Scenarios**:

1. **Given** saved items exist whose content answers the question, **When** the user submits the question, **Then** the app returns an answer plus the specific source snippets/items used.
2. **Given** no saved items relate to the question, **When** the user submits the question, **Then** the app responds indicating it has no relevant information, rather than fabricating an answer.
3. **Given** the inbox has zero saved items, **When** the user submits a question, **Then** the app returns a clear "nothing saved yet" response instead of calling the LLM.

---

### User Story 3 - Browse saved items (Priority: P2)

A user views a list of everything they've saved, to confirm what's in their knowledge base and when it was added.

**Why this priority**: Supports trust and orientation (users can see what the assistant "knows") but the app is still usable end-to-end without a polished list view.

**Independent Test**: Save several items of mixed type; load the list view and confirm all items appear with correct type and timestamp, newest-first.

**Acceptance Scenarios**:

1. **Given** multiple saved items, **When** the user opens the app, **Then** all items are listed with source type and timestamp, ordered newest-first.

---

### Edge Cases

- What happens when a note is submitted empty or whitespace-only? → Rejected with a validation error, nothing saved.
- What happens when a URL is malformed (not a valid URL)? → Rejected with a validation error before any fetch attempt.
- What happens when a question is submitted empty? → Rejected with a validation error.
- How does the system handle an item too large to embed in one chunk? → Content is split into multiple chunks per the chunking strategy; each chunk is independently searchable.
- What happens if the LLM or embedding provider call fails (rate limit, network error)? → The user sees a clear, non-crashing error message; no silent failure.
- What happens when two items contain near-duplicate content? → Both are stored and searchable independently; no dedup in scope for v1.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a user to save a plain-text note with no length-based rejection beyond a sane upper bound.
- **FR-002**: System MUST allow a user to save a URL; the server MUST fetch the page content server-side and extract readable text at save time.
- **FR-003**: System MUST persist, for every saved item: raw content, source type (note or url), original URL (if applicable), and a creation timestamp.
- **FR-004**: System MUST reject empty/whitespace-only note submissions and malformed URL submissions with a validation error, without persisting anything.
- **FR-005**: System MUST split saved content into chunks using a documented, consistent chunking strategy before generating embeddings.
- **FR-006**: System MUST generate a vector embedding for each chunk and store it alongside a reference to its source item.
- **FR-007**: System MUST, given a user question, retrieve the top-N most semantically relevant chunks across all saved items.
- **FR-008**: System MUST pass the retrieved chunks plus the user's question to an LLM and return a natural-language answer.
- **FR-009**: System MUST return, alongside the answer, the specific source snippets/items that were used to generate it.
- **FR-010**: System MUST respond gracefully (not with a fabricated answer) when no saved content is relevant to the question.
- **FR-011**: System MUST expose a way to list all saved items with their metadata, ordered newest-first.
- **FR-012**: System MUST return clear, actionable error messages and appropriate error responses when ingestion or querying fails (fetch failure, provider failure, validation failure).
- **FR-013**: System MUST NOT require user authentication; it operates as a single-user application.

### Key Entities

- **Item**: A saved piece of knowledge. Attributes: unique id, source type (note | url), raw text content, original URL (nullable), created-at timestamp.
- **Chunk**: A segment of an Item's content used for retrieval. Attributes: unique id, parent item id, chunk text, position/order within item, embedding vector.
- **Query**: A user's question. Attributes: question text, timestamp. Not necessarily persisted, but conceptually distinct from an Item.
- **Answer**: The result of a Query. Attributes: answer text, list of cited chunks/items used to produce it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can save a note or URL and see it reflected in the saved-items list in under 5 seconds (excluding slow external page fetches).
- **SC-002**: A user can ask a question and receive an answer with cited sources in under 15 seconds for a knowledge base of up to 100 saved items.
- **SC-003**: When the answer to a question is present in saved content, the returned answer correctly reflects that content and cites the item(s) it came from, in at least 9 of 10 manual test questions.
- **SC-004**: When no saved content is relevant to a question, the system avoids presenting a fabricated answer as fact in at least 9 of 10 manual test questions.
- **SC-005**: A new reviewer can read the returned answer and, using only the cited source snippets, independently verify the answer's accuracy without reading the full original item.

## Assumptions

- Single user, no authentication or multi-tenant data isolation is required (per assignment constraints).
- "URL" ingestion means fetching and extracting the main readable text of a public, non-authenticated web page at save time (not a live/re-crawled copy).
- Knowledge base scale for this exercise is small (tens to low hundreds of items) — this shapes chunking, storage, and retrieval choices, not a production-scale target.
- An LLM API (e.g. Anthropic, OpenAI, or equivalent) is available and reachable for answer generation; embeddings may be generated locally or via an API.
- "Cited sources" means returning enough of the source snippet and the parent item's identity that a user can trace the answer back to what they saved — not a formal citation format.
- Persistence only needs to survive across requests during a single running instance; multi-instance/concurrent-write scenarios are out of scope.
