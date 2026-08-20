<!--
Sync Impact Report
- Version change: 1.0.0 → 1.1.0
- Modified principles: n/a
- Added sections: Governance / Commit conventions (no AI-attribution trailers in commit messages)
- Removed sections: none
- Templates requiring updates: none (commit conventions are enforced at commit time, not template-driven)
- Follow-up TODOs: none

Prior report (1.0.0, unratified template → 1.0.0):
- Added sections: Core Principles (5), Scope & Tech Constraints, Quality Gates, Governance
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ no change needed (Constitution Check gate is generic, reads from this file)
  - .specify/templates/spec-template.md ✅ no change needed (no principle-specific hardcoding)
  - .specify/templates/tasks-template.md ✅ no change needed (task categories already generic; polish phase covers logging/validation called out here)
  - specs/001-ai-knowledge-inbox/plan.md ✅ re-checked and updated
-->

# AI Knowledge Inbox Constitution

## Core Principles

### I. Simplicity First (NON-NEGOTIABLE)
Every dependency, abstraction, and infra choice MUST be justified by a concrete
requirement in front of us right now, not a hypothetical future one. Prefer the
stdlib, an already-installed package, or a single file over a new service,
framework, or layer. Auth systems, container orchestration, message queues,
and dedicated vector databases MUST NOT be introduced unless the single-user,
6-12 hour scope of this project actually demands them — it currently does not.
When a simpler option and a "more correct at scale" option both work today,
ship the simpler one and note the upgrade path in a comment.
**Rationale**: The assignment explicitly scores against bloat and infra
theater; every unnecessary moving part is a unit of review time and failure
surface that doesn't buy the single user anything.

### II. Tradeoff Transparency
Every architecturally significant decision (chunking strategy, embedding
model, vector storage, retrieval method) MUST have its rationale recorded
in-repo (plan.md, research.md, or code comments) — not just implemented
silently. The write-up MUST name what breaks first at scale and what the
production-grade replacement would be, even though that replacement is out
of scope now.
**Rationale**: The assignment is graded on tradeoff awareness as much as on
working code; undocumented "it just works" choices can't be evaluated and
don't transfer to a real production decision later.

### III. Debuggable by Default
Every request path MUST produce structured logs (not bare `print`), return a
sensible HTTP status code for its outcome (400 for bad input, 404 for missing
resource, 502/503 for upstream/LLM failures, etc.), and surface error
messages that name what went wrong and where — never a bare stack trace or a
silent empty response.
**Rationale**: A single-user prototype still gets debugged under time
pressure; logging and status codes are the cheapest possible investment
against that.

### IV. Separation of Concerns
Routes/controllers, business logic (chunking, embedding, retrieval, prompting),
and data access MUST live in distinct modules. No file MUST grow into a god
file mixing HTTP handling with RAG logic with DB queries. Repeated logic
(e.g., chunk formatting, source citation shaping) MUST be extracted once it
appears a second time, not copy-pasted.
**Rationale**: Explicitly required by the assignment's Code Quality section,
and it's what makes a 6-12 hour build reviewable in a single pass.

### V. Contract-First API Design
The three endpoints (`POST /ingest`, `GET /items`, `POST /query`) MUST have
explicit, validated request/response shapes with clear field naming. Invalid
input MUST be rejected with a 4xx response and a specific validation message,
never silently coerced or ignored. `POST /query` responses MUST include the
answer and the cited source chunks/items it was derived from — an answer
without citations is an incomplete response.
**Rationale**: The assignment scores API design directly (request/response
shape, error handling, validation, naming), and citations are the core
trust mechanism of a RAG feature — an uncited answer isn't verifiable.

## Scope & Tech Constraints

- Single-user, no authentication/authorization system of any kind.
- Backend: Node+Express or FastAPI; frontend: React (Tailwind/shadcn optional,
  clarity over visual polish).
- Storage: SQLite, in-memory, or another lightweight embedded store — no
  managed/hosted vector database.
- Embeddings/LLM: OpenAI, Anthropic, a local model, or an equivalent API —
  provider choice is free as long as Principle II's rationale is recorded.
- Ingestion covers plain-text notes and server-side URL fetch; stored content
  MUST retain raw content plus metadata (timestamp, source type).
- Target effort is 6-12 hours of real work with a 2-3 day calendar hard cap;
  scope decisions under time pressure MUST favor cutting features over
  cutting Principles III-V (logging, structure, and citations stay non-negotiable).

## Quality Gates

- A change MUST NOT be considered done if it introduces a new top-level
  dependency, service, or infra component without a Principle I justification
  recorded alongside it.
- A change touching `POST /ingest`, `GET /items`, or `POST /query` MUST keep
  request/response validation and error status codes intact per Principle V.
- Tests are not mandated wholesale (per YAGNI/Principle I) but any non-trivial
  branch in chunking, retrieval ranking, or prompt assembly MUST leave behind
  at least one runnable check (a unit test or an assert-based self-check).

## Governance

This constitution supersedes ad-hoc practice for this project. Amendments
require the change to be written here first (principle text + rationale)
before or alongside the code change it motivates — not after the fact.

**Versioning policy**: MAJOR for backward-incompatible principle removal or
redefinition, MINOR for a new principle or materially expanded guidance,
PATCH for wording/typo clarifications that don't change intent.

**Compliance review**: Every `/speckit-plan` run MUST re-check its Constitution
Check gate against the current version of this file; a plan that predates an
amendment MUST be re-validated before further implementation work continues
on it.

**Commit conventions**: Commit messages MUST NOT include AI-attribution
trailers (e.g. `Co-Authored-By: Claude`, `Generated with Claude Code`, or
similar). Authorship is the committing user's.

**Version**: 1.1.0 | **Ratified**: 2026-08-20 | **Last Amended**: 2026-08-20
