# FastAPI application context

`app/main.py` is the composition root. Authentication and organizations now
live under `platform/`, while pure RAGForge code lives under
`modules/ragforge/`. Historical paths remain as compatibility aliases.

## Current ownership guide

- Platform-owned: `platform/access` (durable sessions and shared policies),
  `platform/accounts` (global roles), and `platform/organizations`
  (memberships and invitations).
- RAGForge-owned: `modules/ragforge` for documents, versions, chunks,
  embeddings, ingestion, retrieval, generation, query history, traces, and
  per-project RAG configuration.
- Infrastructure-oriented: PostgreSQL session setup, Redis connections, MinIO
  and Qdrant clients, provider clients, Airflow REST, and Celery configuration.
- Mixed seams requiring a split before movement: ingestion orchestration, event
  streaming, indexing, storage, and internal pipeline callbacks. Project/account
  project provisioning and cleanup cross the module boundary through
  capability lifecycle hooks. Durable enablement belongs to
  `platform/capabilities`.

Dependencies should point from RAGForge to platform contracts, never from
platform packages to RAGForge business logic. Preserve `app.models.tables` and
the legacy module aliases until callers migrate.

Use [`../../docs/map/CONTEXT.md`](../../docs/map/CONTEXT.md) to identify first-
order effects before changing a model or process.
