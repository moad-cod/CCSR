# FastAPI application context

`app/main.py` is the current composition root. The package is flat and mixes
future platform, RAGForge-module, and infrastructure responsibilities.

## Current ownership guide

- Platform-oriented: auth, organizations, users, memberships, and the generic
  portion of projects.
- RAGForge-oriented: documents, versions, chunks, embeddings, ingestion,
  retrieval, generation, query history, and traces.
- Infrastructure-oriented: PostgreSQL session setup, Redis connections, MinIO
  and Qdrant clients, provider clients, Airflow REST, and Celery configuration.
- Mixed seams requiring a split before movement: project/account deletion,
  ingestion orchestration, event streaming, indexing, storage, and internal
  pipeline callbacks.

Dependencies should eventually point from RAGForge to platform contracts, never
from platform packages to RAGForge business logic. Until packages are moved,
preserve `app.models.tables` and other compatibility imports.

Use [`../../docs/map/CONTEXT.md`](../../docs/map/CONTEXT.md) to identify first-
order effects before changing a model or process.
