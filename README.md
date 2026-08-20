# AI Knowledge Inbox

Save notes/URLs, ask questions over them, get cited answers via a minimal RAG pipeline.
See [specs/001-ai-knowledge-inbox](specs/001-ai-knowledge-inbox/) for the full spec, plan, and API contract.

## Setup

```bash
# backend
cd backend
python -m venv .venv && .venv/Scripts/activate   # or source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000

# frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. See [quickstart.md](specs/001-ai-knowledge-inbox/quickstart.md) for curl-based validation scenarios.

## Running tests

```bash
cd backend
pytest
```

## Tradeoffs

**Chunking**: Fixed-size character windows (~1500 chars, ~150-char overlap), plain string
slicing. Content here is short notes and single web pages, not long structured documents, so a
semantic/sentence-aware splitter (nltk/spacy) would add a dependency for marginal benefit.
Overlap avoids losing an answer that straddles a chunk boundary.

**Vector store**: Chunk embeddings live as float32 BLOBs in a SQLite `chunks` table; retrieval
is a brute-force cosine-similarity scan over all rows in Python/NumPy. At tens-to-low-hundreds
of items this is sub-millisecond work — no index structure (FAISS, Chroma, pgvector) is needed,
and it keeps everything in one file with one connection.

**Embeddings/LLM split**: Embeddings run locally via `sentence-transformers`
(`all-MiniLM-L6-v2`) so ingestion has no external-API dependency or cost; only `/query`'s answer
step calls Anthropic (`claude-haiku-4-5`), narrowing where a provider outage can bite.

**What breaks at scale**: Brute-force cosine similarity is O(n) per query — past roughly
10k-100k chunks the linear scan and float BLOB I/O would start dominating latency. Single SQLite
file also serializes writes; concurrent multi-user ingestion would contend on the same file.

**Production changes**: Swap the brute-force scan for an ANN index (FAISS, pgvector, or a
managed vector DB) once corpus size or query volume justifies it; move SQLite to Postgres for
concurrent writes and durability; add auth/multi-tenancy (out of scope here per the assignment);
move synchronous ingestion (URL fetch + embed) to a background queue so large/slow URL fetches
don't block the request.
