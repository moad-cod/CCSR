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
- Generic workflow definitions, runs, gateway, and engine adapters:
  `app/platform/execution/`.
- Quotas, shared artifact metadata, and administrative audit events:
  `app/platform/quotas/`, `app/platform/artifacts/`, and `app/platform/audit/`.
- Research hierarchy and public-safe publication snapshots:
  `app/platform/research/` and `app/platform/publication/`.
- Project responses expose server-resolved read/write/manage permissions.
  Platform and RAGForge overview endpoints provide bounded aggregate contracts
  for capability-aware frontend composition.
- Celery worker adapter: `app/workers/`
- Shared ingestion stages and commands: `jobs/`
- Airflow image, DAG, and callback plugin: `airflow/`
- Evaluation packages: `evaluation/`
- Verification: `tests/`

Read [`app/CONTEXT.md`](app/CONTEXT.md) before changing application packages.
Read `airflow/CONTEXT.md`, `jobs/CONTEXT.md`, or `evaluation/CONTEXT.md` before
changing those execution or research paths.

## Current boundaries

- Authentication requires a valid, unrevoked durable session and resolves a
  member/admin global role server-side.
- Organization list/read and mutations enforce membership and owner/admin roles;
  platform admins may administer every organization, and expiring invitations
  are the only way to join an existing organization.
- Personal projects remain creator-private. Active organization members may
  read organization projects; creators and organization owner/admin members may
  mutate them. Platform admins may administer every project. RAG routes use the
  same shared policy rather than creator-only checks.
- `project_capabilities` is the durable enablement boundary and
  `rag_project_configs` owns Qdrant identity, embedding/sparse models, the
  default chunker, and retrieval settings. `Project.qdrant_collection` remains
  mandatory and dual-written temporarily for API/schema compatibility.
- Generic runs own engine-neutral `engine` and `external_execution_id` fields.
  `IngestionRun.airflow_dag_run_id` remains dual-written for API compatibility
  and can still contain a Celery workflow ID during the transition.
- RAGForge registers `ragforge.ingest_document@1.0.0`; its generic run wraps
  the detailed ingestion run while the Airflow DAG and Celery chain keep their
  existing stage order, task names, callbacks, and event payloads.
- Member runs reserve durable daily/monthly/concurrency quota before dispatch;
  terminal updates finalize actual usage or release pre-start failures. Admin
  bypasses, quota changes, role changes, and manual artifact registrations are
  audited with redacted details.
- Projects may contain multiple research studies. Generic runs and artifacts
  can carry experiment/study lineage. Private and draft publications remain
  project-authorized; visitor routes read only the current immutable snapshot
  of a public publication.
- The application root registers RAGForge in the platform capability registry;
  project creation provisions its default association/configuration, and
  project/account deletion invokes hooks only for enabled projects without
  importing RAG code from platform routes.

Historical authentication, organization, and RAG imports are compatibility
aliases to the canonical ownership packages. Keep them until downstream code
and operational entry points have migrated; new code must use canonical paths.

Keep current table names, route prefixes, service-token behavior, task names,
and event payloads stable until explicit compatibility work is approved.
