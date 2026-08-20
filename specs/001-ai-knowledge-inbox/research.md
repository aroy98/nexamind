# Phase 0 Research: AI Knowledge Inbox

## Chunking strategy

**Decision**: Fixed-size character windows (~1500 chars ≈ 350-400 tokens) with ~150-char overlap, split via plain string slicing on the raw extracted text.

**Rationale**: Content here is short notes and single web pages, not long structured documents — a semantic/sentence-aware splitter buys little at this scale and adds a dependency (e.g. `langchain`, `nltk`). Fixed-size windows are deterministic, fast, dependency-free, and "intentional" (documented, consistent) satisfies the assignment's bar ("simple is fine, but intentional"). Overlap avoids losing an answer that straddles a chunk boundary.

**Alternatives considered**:
- Sentence/paragraph-aware chunking (e.g. via `nltk`/`spacy`) — more semantically clean splits, but adds a heavyweight dependency for marginal benefit at this content scale.
- One chunk per item (no splitting) — simplest, but breaks retrieval precision for longer URLs (a 5,000-word article would dominate or dilute similarity scoring as a single vector).
- Token-aware chunking via `tiktoken` — more accurate token budgeting for the embedding/LLM context window, but character-count approximation is close enough at these content sizes and avoids a dependency just for counting.

## Embeddings & LLM provider

**Decision**: Local embeddings via `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dim) for chunks/queries; Anthropic `claude-haiku-4-5` for answer generation.

**Rationale**: The assignment allows "OpenAI or equivalent API" — Claude qualifies for the LLM step, but Anthropic has no embeddings endpoint, so embeddings need a separate source regardless of LLM choice. Rather than pulling in OpenAI just for embeddings, running a small local sentence-transformer keeps the project to a single external API dependency (Anthropic, for answers only) and removes any embedding-provider cost/rate-limit/network dependency from ingestion. `all-MiniLM-L6-v2` is small (~80MB), fast on CPU, and standard for exactly this kind of small-corpus semantic search demo.

**Alternatives considered**:
- OpenAI `text-embedding-3-small` — no local model download, marginally higher embedding quality; rejected here specifically to avoid depending on two LLM vendors at once.
- Larger local models (`all-mpnet-base-v2`, etc.) — better retrieval quality, slower CPU inference; MiniLM's quality is sufficient at this corpus size and priority is setup speed.
- `claude-opus-5`/`claude-sonnet-5` for answers — higher quality, higher cost/latency; unnecessary for grounded short-context Q&A over a small knowledge base.

**Tradeoff introduced**: local embeddings mean a first-run model download (~80MB) and CPU inference latency (small, but nonzero) that a pure-API approach wouldn't have. Acceptable for a single-user, low-volume tool; would reconsider (move to a hosted embeddings API or GPU-backed inference) if ingestion volume or corpus size grew significantly.

## Vector storage

**Decision**: Store chunk embeddings as serialized float32 BLOBs in a SQLite `chunks` table; retrieval does brute-force cosine similarity in Python over all rows.

**Rationale**: At tens-to-low-hundreds of items (per spec Assumptions), a linear scan over a few hundred to low-thousands of vectors is sub-millisecond-to-low-millisecond work — no index structure is needed. This avoids adding a vector DB dependency (Chroma, FAISS, pgvector, etc.) purely to satisfy "vector storage," which the assignment explicitly says can be "in-memory, sqlite, or lightweight DB." Using SQLite for both items and vectors also means one file, one connection, no second storage system to keep in sync.

**Alternatives considered**:
- FAISS in-process index — real ANN performance benefit, but that benefit doesn't materialize until the corpus is much larger; adds a native dependency for no measurable gain here.
- Chroma / a dedicated vector DB — convenient API, but another moving part (or another dependency) for a single-user, small-corpus tool; explicitly the kind of "overengineering infra" the assignment says to avoid.
- Pure in-memory (no persistence) — simplest, but items would vanish on restart, contradicting FR-003 (persist raw content + metadata).

## URL content extraction

**Decision**: `requests.get()` with a timeout, then `BeautifulSoup` to strip tags/scripts/styles and extract visible text.

**Rationale**: Both are common, lightweight, well-understood libraries; no headless browser needed since this is server-side static HTML fetch, not JS-rendered scraping (out of scope per assignment simplicity).

**Alternatives considered**:
- `trafilatura`/`readability-lxml` for higher-quality "main content" extraction — nicer output, but another dependency; BeautifulSoup's straightforward text extraction is good enough for a demo-scale RAG source.
- Headless browser (Playwright) — handles JS-rendered pages, but is heavy infrastructure explicitly out of scope for this exercise.

## Logging

**Decision**: Python stdlib `logging` with a small JSON `Formatter`, one logger per module, request-level log lines (route, status, latency) plus pipeline-stage lines (chunk count, retrieval hit count, provider errors).

**Rationale**: Stdlib covers "structured logging" without adding `structlog`/`loguru`. FastAPI already integrates cleanly with stdlib logging via middleware/exception handlers.

**Alternatives considered**: `structlog` — nicer ergonomics for structured fields, but unnecessary dependency for the log volume/complexity here.

## Frontend state management

**Decision**: Local component state (`useState`) in `App.jsx` for items/loading/error, lifted just far enough to be shared between the list and the ask panel; no Redux/Zustand/React Query.

**Rationale**: Three views, three endpoints, single user — a state library would be pure ceremony. `useState` + a couple of `fetch` calls in `api.js` is the whole "state management" surface.

**Alternatives considered**: React Query — nice caching/refetch semantics, but adds a dependency for a page that reloads its item list after each mutation anyway.

## Answer-provider failure isolation

**Decision**: Embedding generation (local, `sentence-transformers`) and answer generation (remote, Anthropic API) are separate stages with independent error handling in `embeddings.py` and `answering.py`.

**Rationale**: Since embeddings no longer depend on network access, ingestion can no longer fail on an embedding-provider outage — only on URL fetch issues. Only the `/query` answer step has an external-API failure mode now, narrowing where `ProviderError`/502s can originate.
