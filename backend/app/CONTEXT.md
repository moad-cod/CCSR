# FastAPI application context

`app/main.py` is the composition root. Authentication and organizations now
live under `platform/`, while pure RAGForge code lives under
`modules/ragforge/`. Historical paths remain as compatibility aliases.

## Current ownership guide

- Platform-owned: `platform/access`, `platform/accounts`, and
  `platform/organizations`.
- RAGForge-owned: `modules/ragforge` for documents, versions, chunks,
  embeddings, ingestion, retrieval, generation, query history, and traces.
- Infrastructure-oriented: PostgreSQL session setup, Redis connections, MinIO
  and Qdrant clients, provider clients, Airflow REST, and Celery configuration.
- Mixed seams requiring a split before movement: project/account deletion,
  ingestion orchestration, event streaming, indexing, storage, and internal
  pipeline callbacks.

Dependencies should point from RAGForge to platform contracts, never from
platform packages to RAGForge business logic. Account/project deletion is a
known temporary exception because it still performs RAG cleanup. Preserve
`app.models.tables` and the legacy module aliases until callers migrate.

Use [`../../docs/map/CONTEXT.md`](../../docs/map/CONTEXT.md) to identify first-
order effects before changing a model or process.
