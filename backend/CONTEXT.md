# Backend context

The backend is currently a FastAPI RAG control plane. It is the implementation
source of truth for authentication, organization membership, owner-scoped
projects, RAG ingestion/query behavior, and orchestration callbacks.

## Route by task

- HTTP composition and routes: `app/main.py`, then `app/api/`
- Authentication and settings: `app/core/`
- Durable schema: `app/models/` and `alembic/versions/`
- PostgreSQL operations: `app/repositories/`
- RAG behavior and integration clients: `app/services/`
- Celery worker adapter: `app/workers/`
- Shared ingestion stages and commands: `jobs/`
- Airflow image, DAG, and callback plugin: `airflow/`
- Evaluation packages: `evaluation/`
- Verification: `tests/`

Read [`app/CONTEXT.md`](app/CONTEXT.md) before changing application packages.
Read `airflow/CONTEXT.md`, `jobs/CONTEXT.md`, or `evaluation/CONTEXT.md` before
changing those execution or research paths.

## Current boundaries

- Organization list/read and mutations enforce membership and owner/admin roles.
- Project, document, ingestion, and query access remains creator-owned through
  `Project.created_by`.
- `Project.qdrant_collection` is mandatory, so the project model is not generic.
- `IngestionRun.airflow_dag_run_id` is also used for Celery workflow IDs.
- Platform account/project deletion directly imports RAG/Qdrant cleanup.

Keep current table names, route prefixes, service-token behavior, task names,
and event payloads stable until explicit compatibility work is approved.
