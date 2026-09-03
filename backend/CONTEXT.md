# Backend context

The backend is a FastAPI modular monolith. Platform authentication and
organization ownership and the pure RAGForge implementation have been
separated mechanically; generic projects and several orchestration seams are
still in their historical packages.

## Route by task

- HTTP composition and routes: `app/main.py`; route implementations live with
  their owning platform or product package.
- Authentication and accounts: `app/platform/access/` and
  `app/platform/accounts/`; settings remain in `app/core/`.
- Organizations and memberships: `app/platform/organizations/`.
- RAGForge APIs, models, repositories, and services:
  `app/modules/ragforge/`.
- Generic project and shared/mixed adapters: historical `app/api/`,
  `app/models/`, `app/repositories/`, and `app/services/` paths.
- Durable migrations: `alembic/versions/`.
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
- `project_capabilities` is the durable enablement boundary and
  `rag_project_configs` owns Qdrant identity, embedding/sparse models, the
  default chunker, and retrieval settings. `Project.qdrant_collection` remains
  mandatory and dual-written temporarily for API/schema compatibility.
- `IngestionRun.airflow_dag_run_id` is also used for Celery workflow IDs.
- The application root registers RAGForge in the platform capability registry;
  project creation provisions its default association/configuration, and
  project/account deletion invokes hooks only for enabled projects without
  importing RAG code from platform routes.

Historical authentication, organization, and RAG imports are compatibility
aliases to the canonical ownership packages. Keep them until downstream code
and operational entry points have migrated; new code must use canonical paths.

Keep current table names, route prefixes, service-token behavior, task names,
and event payloads stable until explicit compatibility work is approved.
