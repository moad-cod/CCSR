# CCSR repository context

CCSR is the platform. RAGForge is the current mature Retrieval-Augmented
Generation capability and is being separated from the platform incrementally.
The repository remains one deployable modular monolith.

## Current state

- The backend now has canonical platform authentication/organization and
  RAGForge ownership packages. Project and account deletion invoke registered
  capability lifecycle hooks instead of importing RAGForge cleanup directly.
- Project capability enablement is durable in `project_capabilities`, while
  RAG-owned project settings live in `rag_project_configs`. Existing projects
  are backfilled as RAGForge-enabled; legacy collection fields remain during
  the compatibility window.
- Authentication issues JWTs backed by durable, revocable sessions. Users have
  member/admin platform roles, organizations support expiring invitations, and
  shared default-deny policies govern organization and project access.
- The frontend is one Next.js application with shared UI primitives, but project
  navigation and data loading still assume RAG capabilities.
- PostgreSQL is authoritative for durable application state. Redis is
  best-effort cache/progress transport. MinIO stores ingestion artifacts and
  Qdrant stores RAG vectors.
- Airflow and Celery execute the same RAG ingestion stages through different
  adapters. A generic workflow/run gateway is not implemented yet.

## Intended dependency direction

```text
application composition root
  -> platform core
  -> registered capability modules
  -> infrastructure adapters

RAGForge module -> stable platform contracts
platform core -X-> RAGForge business logic
```

Do not introduce `project.type` branching. Projects enable capabilities
through associations, and infrastructure selection belongs to registered
workflow definitions rather than browser input.

## Authoritative navigation

- Current backend: [`backend/CONTEXT.md`](backend/CONTEXT.md)
- Current frontend: [`frontend/CONTEXT.md`](frontend/CONTEXT.md)
- Verified change impact: [`docs/map/CONTEXT.md`](docs/map/CONTEXT.md)
- Broad current maps: [`PROJECT_MAP.md`](PROJECT_MAP.md),
  [`backend/BACKEND_MAP.md`](backend/BACKEND_MAP.md), and
  [`frontend/FRONTEND_MAP.md`](frontend/FRONTEND_MAP.md)
- Proposed migration sequence: the approved architecture audit in the project
  work history; source and Alembic migrations remain authoritative over plans.

## Change rules

1. Use Graphify before repository exploration and verify graph results against
   source.
2. Enumerate import, route, Docker, test, and documentation referrers before a
   path move.
3. Preserve public URLs, API payloads, task names, Redis events, and environment
   variables through compatibility layers.
4. Use explicit Alembic expand/backfill/contract migrations for schema changes.
5. Do not store accounts, permissions, quotas, runs, or concurrency state in
   Markdown.
6. Update the nearest context and System Map cards when ownership changes.
