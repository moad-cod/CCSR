# Backend Refactor Plan — Phase 0 Discovery

Status: discovery complete; no application code has been changed.

Architectural authority: [`architecture/backend.md`](architecture/backend.md).
Compatibility authority: the currently working source, Alembic history, tests,
Docker/runtime commands, public URLs and payloads, task names, events, and
environment variables.

This plan records the repository as inspected on 2026-09-12. It is a migration
plan, not evidence that the target layout is already implemented. Moves are
deliberately incremental and must preserve a runnable modular monolith after
every phase.

## Current architecture

The backend is a FastAPI modular monolith rooted at `backend/app/main.py`.
`main.py` currently performs both application construction and composition: it
registers RAGForge capability/workflow definitions and directly mounts all
platform, project, research, publication, execution, and RAG routers. There is
no `app/composition.py` yet.

The repository is already partway through the target migration:

- Canonical accounts, access, organizations, capabilities, quotas, audit,
  artifacts, research/publication, and generic execution code is under
  `app/platform/`.
- Canonical RAGForge models, repositories, APIs, chunkers, retrieval, ingestion,
  indexing, generation, configuration, and lifecycle hooks are under
  `app/modules/ragforge/`.
- Generic project ownership remains in historical `app/api/projects.py`,
  `app/models/project.py`, and `app/repositories/projects.py`.
- `app/api/`, `app/models/`, `app/repositories/`, and much of `app/services/`
  contain compatibility re-exports alongside the remaining mixed seams.
- Generic workflow definitions and durable generic runs are implemented under
  `app/platform/execution/`, including Airflow and Celery adapters.
- Shared ingestion stages and executable commands are in `jobs/`; Airflow DAGs
  and callbacks are in `airflow/`; Celery entry points are in `app/workers/`
  plus the root `worker.py` wrapper.
- PostgreSQL is authoritative. The live migration history is in `alembic/` and
  currently runs from revision `20260711_0001` through `20260907_0010`.
- MinIO stores Bronze/Silver/Gold artifacts, Qdrant is a derived vector index,
  and Redis is best-effort cache/event/broker infrastructure.

Existing behavior already satisfies several important dependency goals:

- `app/platform/` has no imports of `app.modules.ragforge`.
- Platform deletion reaches RAGForge cleanup through registered lifecycle
  hooks rather than a platform-to-RAG import.
- RAG file ingestion dispatches through the generic execution gateway.
- Airflow and Celery preserve generic run identity through
  `external_execution_id`, while the legacy `airflow_dag_run_id` field remains
  a compatibility surface.

## Target architecture from backend.md

The target remains one deployable modular monolith with these top-level
application boundaries:

- `app/platform/`: accounts, organizations, access, projects, capability
  contracts/registry/lifecycle, audit, and quotas.
- `app/research/`: capability-neutral studies, experiments, runs, datasets,
  models, artifacts, metrics, findings, notes, and publications.
- `app/capabilities/ragforge/`: all RAG-specific domain and application logic.
- `app/execution/`: engine-neutral workflow/run/task contracts and gateway.
- `app/infrastructure/`: PostgreSQL, MinIO, Qdrant, Redis, event,
  orchestrator, and AI-provider adapters.
- `app/interfaces/`: HTTP, SSE, and internal transport concerns.
- `app/composition.py`: the sole assembly point for adapters, services,
  capabilities, workflows, and routers; `app/main.py` remains the FastAPI entry.
- `runtimes/airflow/` and `runtimes/celery/`: thin runtime packaging and entry
  points that execute shared capability stages.
- Alembic may remain under `alembic/`. Relocation to `migrations/` is optional
  and should occur only if a concrete operational or maintainability benefit is
  identified. Historical migrations must never be rewritten.

Mandatory dependency direction:

```text
composition/interfaces -> platform/research/execution/capabilities contracts
composition -> infrastructure implementations
ragforge -> stable platform/research/execution contracts
platform/research -X-> ragforge business logic
ragforge -X-> concrete Airflow/Celery implementations
```

The target names do not authorize schema changes. Module moves must not rename
tables, columns, IDs, public APIs, task names, event payloads, or environment
variables.

## Current → target file map

The entries below are proposed ownership outcomes. A directory entry covers its
contained files only after each file's callers and behavior have been verified.

### Application composition

CURRENT:
    app/main.py

TARGET:
    app/main.py + app/composition.py

ACTION:
    SPLIT

REASON:
    Keep FastAPI entry construction small and move adapter, registry, workflow,
    and router assembly to the target composition root.

DEPENDENCIES:
    Every mounted router; capability_registry; execution_registry; RAGForge
    capability/workflow registration; QuotaExceededError handler.

TESTS:
    API unit tests; ownership compatibility tests; FastAPI import/start smoke;
    e2e control-plane test.

RISK:
    high

### Platform projects

CURRENT:
    app/api/projects.py
    app/models/project.py
    app/repositories/projects.py

TARGET:
    app/platform/projects/router.py
    app/platform/projects/models.py
    app/platform/projects/repository.py
    app/platform/projects/schemas.py
    app/platform/projects/service.py (only if extracted behavior warrants it)

ACTION:
    MOVE / SPLIT

REASON:
    Projects and workspaces are generic platform concepts. The current router
    also mixes schemas, aggregate reads, lifecycle dispatch, and response
    shaping, which should be separated without changing payloads.

DEPENDENCIES:
    access policies; organizations; capability registry; generic runs;
    artifacts; research/publications; RAG config compatibility fields;
    `app.models.tables`; Alembic metadata imports; frontend project contracts.

TESTS:
    platform authorization; lifecycle deletion; capability navigation;
    project capability configuration; frontend control-plane API; e2e.

RISK:
    high

### Platform accounts, access, and organizations

CURRENT:
    app/platform/accounts/
    app/platform/access/
    app/platform/organizations/

TARGET:
    app/platform/accounts/
    app/platform/access/
    app/platform/organizations/

ACTION:
    KEEP / REORGANIZE INTERNALLY

REASON:
    Ownership is already correct. Later file naming can converge on
    models/schemas/repository/service/router where that reflects real behavior.

DEPENDENCIES:
    `app/api/auth.py`, `app/core/auth.py`, organization model/repository aliases,
    JWT/session configuration, project policies, frontend auth payloads.

TESTS:
    auth validation; organization authorization; platform authorization;
    ownership compatibility; e2e.

RISK:
    medium

### Platform capability, governance, and lifecycle services

CURRENT:
    app/platform/capabilities/
    app/platform/audit/
    app/platform/quotas/
    app/platform/artifacts/

TARGET:
    app/platform/capabilities/
    app/platform/lifecycle/
    app/platform/audit/
    app/platform/quotas/
    app/platform/artifacts/ or app/research/artifacts/ (ownership decision pending)

ACTION:
    KEEP / SPLIT

REASON:
    Capability registration, audit, and quota ownership is correct. Lifecycle
    contracts currently live with capabilities and can be split only when a
    concrete need appears. Artifact ownership is not decided by the target tree
    alone: inspect every consumer first and determine whether Artifact is a
    research-owned concept or a shared CCSR domain primitive. Its API and
    compatibility contracts must survive either outcome.

DEPENDENCIES:
    project/account deletion; generic execution quota reservation/finalization;
    RAGForge artifact registration; admin routes; migrations 0006 and 0009.

TESTS:
    capability registry; RAGForge lifecycle; quotas/artifacts/audit; project
    capability configuration; lifecycle deletion.

RISK:
    high

### Research core

CURRENT:
    app/platform/research/
    app/platform/publication/
    app/platform/artifacts/
    app/platform/execution/model.py (generic Run lineage)

TARGET:
    app/research/experiments/
    app/research/runs/
    app/research/datasets/
    app/research/models/
    app/research/artifacts/
    app/research/metrics/
    app/research/findings/
    app/research/notes/
    app/research/publications/

ACTION:
    SPLIT / MOVE

REASON:
    Current research models are capability-neutral but placed under platform and
    grouped into broad files. Target ownership is a separate research core.
    Generic execution Run behavior must remain in execution; only research
    lineage/application views belong in `research/runs`.

DEPENDENCIES:
    project overview aggregates; execution gateway study/experiment validation;
    artifact APIs; publication snapshots; migration 0010; frontend routes.

TESTS:
    research/publication; execution gateway; quotas/artifacts/audit; frontend
    control-plane API; authorization and e2e tests.

RISK:
    high

### Generic execution

CURRENT:
    app/platform/execution/

TARGET:
    app/execution/
    app/infrastructure/orchestrators/

ACTION:
    SPLIT / MOVE

REASON:
    Contracts, registry, gateway, workflow/run models, repository, and generic
    API belong to the top-level execution boundary. Concrete Airflow and Celery
    adapters belong to infrastructure and must be injected by composition.

DEPENDENCIES:
    capabilities repository; quotas; audit error safety; research lineage;
    RAGForge workflow definition; Airflow REST service; Celery handler registry;
    migrations 0008 and 0009.

TESTS:
    execution gateway; Airflow service; Celery orchestration; ingestion
    execution; e2e.

RISK:
    high

### RAGForge capability package

CURRENT:
    app/modules/ragforge/

TARGET:
    app/capabilities/ragforge/

ACTION:
    MOVE / REORGANIZE

REASON:
    Domain ownership is already correct, but the package name and technical
    sub-layout do not yet match the architectural authority. Move vertically by
    domain (documents, ingestion, parsing, chunking, embeddings, indexing,
    retrieval, generation, queries, evaluation) rather than merely renaming the
    folder.

DEPENDENCIES:
    historical `app/api`, `app/models`, `app/repositories`, and `app/services`
    aliases; main/composition registration; jobs; workers; tests; Alembic model
    registration; imports in seed/validation utilities.

TESTS:
    all chunking, embeddings, ingestion, Qdrant, observability, streaming,
    lifecycle, compatibility, API, and e2e coverage.

RISK:
    high

### Shared ingestion stages

CURRENT:
    jobs/ingestion_workflow.py
    jobs/ingestion_execution.py
    jobs/bronze_to_silver.py
    jobs/silver_to_gold.py
    jobs/upsert_qdrant.py
    app/modules/ragforge/services/pipeline_artifacts.py
    app/modules/ragforge/services/pipeline_status.py
    app/modules/ragforge/services/chunk_indexing.py

TARGET:
    app/capabilities/ragforge/ingestion/stages/
    runtimes/airflow/dags/
    runtimes/celery/tasks.py

ACTION:
    MERGE / SPLIT / MOVE

REASON:
    Shared business stages belong to RAGForge ingestion. Runtime commands and
    tasks should be thin wrappers over the same stage functions.

DEPENDENCIES:
    pipeline service-token API; MinIO paths; deterministic Qdrant/PostgreSQL
    lineage; status transitions; Redis events; Docker command templates; DAG
    task ordering and retries; Celery task names and retries.

TESTS:
    ingestion execution/planner/artifacts; Airflow control plane; Airflow
    integration; Celery integration; Qdrant lineage; streaming; e2e.

RISK:
    high

### RAGForge mixed services

CURRENT:
    app/services/ingestion_orchestrator.py
    app/services/event_stream.py
    app/services/airflow.py
    app/services/celery_ingestion.py
    app/services/control_plane_seed.py
    app/services/control_plane_validation.py

TARGET:
    app/capabilities/ragforge/ingestion/service.py
    app/interfaces/sse.py
    app/infrastructure/events/redis_streams.py
    app/infrastructure/orchestrators/airflow.py
    app/infrastructure/orchestrators/celery.py
    scripts/seed_control_plane.py
    scripts/validate_control_plane.py

ACTION:
    SPLIT / MOVE

REASON:
    These files cross domain, transport, infrastructure, and operational-tool
    concerns. They require seam extraction, not a folder rename.

DEPENDENCIES:
    RAG ingestion models/repositories; core settings/database; execution gateway;
    Redis; Airflow REST; Celery workers; script callers and tests.

TESTS:
    streaming; orchestrator integrations; reset/seed/validation workflows;
    execution gateway; e2e.

RISK:
    high

### Infrastructure clients

CURRENT:
    app/core/db.py
    app/modules/ragforge/services/storage.py
    app/modules/ragforge/services/indexer.py
    app/modules/ragforge/services/query_cache.py
    app/modules/ragforge/services/embedder.py
    provider construction embedded in RAG services

TARGET:
    app/infrastructure/postgres/session.py
    app/infrastructure/postgres/base.py
    app/infrastructure/postgres/metadata.py
    app/infrastructure/storage/minio.py
    app/infrastructure/vectors/qdrant.py
    app/infrastructure/cache/redis.py
    app/infrastructure/ai/

ACTION:
    SPLIT / MOVE

REASON:
    Technology clients belong in infrastructure, while RAG-specific indexing,
    embedding, cache policy, and storage naming stay in the capability behind
    explicit contracts.

DEPENDENCIES:
    nearly all ORM repositories; Alembic env; ingestion stages; query/retrieval;
    lifecycle cleanup; scripts; settings and tests that patch module symbols.

TESTS:
    database, Qdrant lineage, embedding backends, bronze storage, pipeline
    artifacts, query observability, lifecycle, e2e.

RISK:
    high

### Runtime packaging

CURRENT:
    airflow/
    app/workers/
    worker.py

TARGET:
    runtimes/airflow/
    runtimes/celery/

ACTION:
    MOVE / KEEP WRAPPERS

REASON:
    Runtime-specific packaging belongs outside application domain packages.
    Existing Docker mounts, image paths, worker app references, task/DAG names,
    callbacks, and environment variables require temporary compatibility paths.

DEPENDENCIES:
    docker-compose.yml; docker-compose.e2e.yml; backend/airflow/Dockerfile;
    `celery -A app.workers.celery_app:celery_app`; pipeline command variables;
    scripts/e2e_v2.sh; system-map documentation.

TESTS:
    Airflow/Celery unit and integration tests; Docker config validation; e2e.

RISK:
    high

### Alembic

CURRENT:
    alembic.ini
    alembic/env.py
    alembic/versions/

TARGET:
    alembic.ini
    alembic/env.py
    alembic/versions/
    (optionally migrations/ only if a concrete benefit is proven)

ACTION:
    KEEP / OPTIONAL INDEPENDENT MOVE WITH COMPATIBILITY

REASON:
    The current layout is valid and its name is cosmetic compared with
    preserving operational upgrade commands and historical revision IDs. Do
    not relocate Alembic without a concrete benefit. If separately approved,
    verify fresh and existing-schema upgrades and never rewrite history.

DEPENDENCIES:
    `alembic -c alembic.ini`; reset script; Docker/e2e commands; `app.models`
    metadata registration; documentation; revisions 0001–0010.

TESTS:
    Alembic import/current/heads; fresh upgrade to head; existing-schema upgrade;
    control-plane database/runtime; reset-dev-db tests.

RISK:
    high

### Benchmark/evaluation packages

CURRENT:
    evaluation/airflow_benchmark/
    evaluation/celery_benchmark/

TARGET:
    evaluation/ingestion/
    evaluation/ingestion/adapters/airflow.py
    evaluation/ingestion/adapters/celery.py

ACTION:
    MERGE / SPLIT

REASON:
    Both packages have parallel `cli`, `client`, `metrics`, `models`, `report`,
    `runner`, `validator`, and `workload` files. They are not byte-identical, so
    shared behavior must be compared and extracted while runtime differences
    remain in adapters.

DEPENDENCIES:
    benchmark READMEs/configs; benchmark tests; API event ordering; workload
    naming and report output formats.

TESTS:
    both benchmark test modules plus a cross-adapter contract test.

RISK:
    medium

### Test organization

CURRENT:
    tests/unit/{api,chunking,embeddings,ingestion,models,...}
    tests/integration/{airflow,celery,postgres,qdrant,streaming}
    tests/benchmarks/
    tests/e2e/

TARGET:
    tests/unit/platform/
    tests/unit/research/
    tests/unit/capabilities/ragforge/
    tests/unit/execution/
    tests/integration/{postgres,qdrant,minio,redis,airflow,celery}/
    tests/e2e/

ACTION:
    MOVE AFTER IMPLEMENTATION

REASON:
    Tests should follow stable ownership, but moving them before implementation
    would obscure regressions and increase import churn.

DEPENDENCIES:
    pytest discovery; patch target strings; fixture paths; Airflow plugin path;
    benchmark package names; CI commands.

TESTS:
    full backend suite before and after each batch; assertion counts preserved.

RISK:
    medium

## Module ownership

| Current area | Current responsibility | Target owner |
| --- | --- | --- |
| `app/core` | settings, SQLAlchemy setup, auth alias | core config plus PostgreSQL infrastructure |
| `app/platform/accounts`, `access`, `organizations` | identity, durable sessions, RBAC, membership | platform |
| historical project files | project CRUD, aggregate responses, lifecycle calls | platform/projects |
| `app/platform/capabilities` | durable enablement, registry, lifecycle contracts | platform/capabilities and optionally platform/lifecycle |
| `app/platform/quotas`, `audit` | durable governance | platform |
| `app/platform/artifacts` | shared artifact metadata/API | undecided: research-owned or shared CCSR primitive after consumer analysis |
| `app/platform/research`, `publication` | capability-neutral research/publication | research |
| `app/platform/execution` | generic workflow/run/gateway plus adapters | execution contracts/services; adapters to infrastructure |
| `app/modules/ragforge` | RAG capability | capabilities/ragforge |
| `jobs` | ingestion stages and CLI wrappers | RAG ingestion stages plus thin runtime/CLI adapters |
| `airflow`, `app/workers` | runtime integration | runtimes plus infrastructure orchestrator adapters |
| `app/services/event_stream.py` | SSE/event persistence bridge | interfaces plus infrastructure/events |
| `evaluation/*_benchmark` | duplicated ingestion benchmarks | evaluation/ingestion plus adapters |

## Dependency violations and risky dependencies

No direct `platform -> app.modules.ragforge` import was found. The following are
target-boundary violations or migration hazards, not necessarily current bugs:

1. `app/modules/ragforge/workflows.py` imports and instantiates concrete
   `AirflowExecutionAdapter` and `CeleryExecutionAdapter`, registers a Celery
   handler, and imports `app.workers.tasks` lazily. Capability business wiring
   therefore knows concrete engines. Move adapter/handler registration to
   composition; keep the capability responsible only for its generic workflow
   definition and handler contract.
2. `app/main.py` is the global composition root and imports concrete RAGForge
   modules directly. This is allowed at the application root, but construction
   should move to `composition.py` so import-time side effects are explicit and
   testable.
3. `app/platform/execution/` combines generic execution business logic with
   concrete Airflow/Celery adapters. Split implementations into infrastructure
   without changing engine values or database checks.
4. `app/services/ingestion_orchestrator.py` combines RAG ingestion state/event
   behavior, direct database session creation, and generic execution dispatch.
   Split the transaction/application boundary before moving it.
5. RAGForge models and API payloads retain `airflow_dag_run_id`. This is an
   intentional compatibility field and cannot be renamed merely to make the
   execution model generic; new generic state already uses
   `external_execution_id`.
6. `app/models/__init__.py` and `app/models/tables.py` aggregate models from all
   domains for metadata compatibility. Alembic depends on `import app.models`.
   Replace only after a dedicated metadata registry exists and migrations can
   import every model deterministically.
7. RAG repositories import the historical generic `app.models.project.Project`.
   This is directionally acceptable (RAG -> platform) only after Project moves
   to a stable platform path; retain the old import alias during migration.
8. `app/services/control_plane_seed.py` crosses platform, research, execution,
   and RAGForge domains. It is an operational composition utility, not a domain
   service; keep its cross-domain assembly in scripts/composition.
9. Concrete MinIO, Qdrant, Redis, embedding, reranker, and provider clients live
   inside RAG service modules. Separate client implementations from capability
   policies without inventing abstractions where no boundary is needed.
10. Airflow DAGs and Celery tasks do share stage-level behavior, but the Airflow
    DAG still executes configurable CLI commands while Celery calls Python stage
    functions. Preserve retry/idempotency and output parsing while converging on
    one business-stage implementation.

Canonical vector identity invariant:

```text
PostgreSQL owns durable Chunk identity.
Qdrant point IDs derive deterministically from PostgreSQL chunk lineage.
Qdrant is derived/rebuildable and must never become the identity authority.
```

Architecture tests should enforce at least:

- `app/platform` and `app/research` do not import RAGForge.
- RAGForge does not import Airflow, Celery, runtime packages, or concrete
  orchestrator adapters.
- generic execution does not contain RAG/EEG/ML-specific concepts.
- domain/application modules do not construct Redis/MinIO/Qdrant/orchestrator
  clients outside approved infrastructure/composition modules.

## Duplicate files

### Compatibility aliases (intentional duplicates)

The root script files `check_data.py`, `cleanup.py`, `create_tables.py`,
`reset_dev_db.py`, `seed_control_plane.py`, and `validate_control_plane.py` are
small compatibility wrappers. Their `scripts/` counterparts contain the
canonical implementations. They are behaviorally related but intentionally not
identical. Do not merge by overwriting either side.

Historical application aliases exist under:

- `app/api/{auth,organizations,documents,ingest,internal_pipeline,query,chunkers}.py`
- `app/models/` for moved account/organization/RAG models
- `app/repositories/` for moved organization/RAG repositories
- `app/services/` and `app/services/{chunkers,retrieval}/` for moved RAG services
- `app/core/auth.py` and `app/services/celery_app.py`

These aliases are covered by `test_ownership_compatibility.py` and must remain
until repository-wide and operational callers use canonical paths.

### Behavior duplicated across packages

`evaluation/airflow_benchmark/` and `evaluation/celery_benchmark/` each contain
the same nine conceptual modules. None of the compared Python files are
byte-identical. Phase 9 must classify differences as engine adapter behavior,
workload naming, or accidental drift before extracting common modules.

Airflow and Celery also contain parallel orchestration of detect, Bronze →
Silver, Silver → Gold, Qdrant upsert, and finalize. The stage intent is shared,
but invocation and retry mechanics differ; this is a merge/split candidate, not
a duplicate-file deletion candidate.

## Scripts to merge

Phase 1 should treat `backend/scripts/` as canonical and keep these root wrappers
temporarily:

| Root wrapper | Canonical implementation | Known compatibility purpose |
| --- | --- | --- |
| `check_data.py` | `scripts/check_data.py` | `python check_data.py` |
| `cleanup.py` | `scripts/cleanup.py` | `python cleanup.py` |
| `create_tables.py` | `scripts/create_tables.py` | legacy table-create workflow |
| `reset_dev_db.py` | `scripts/reset_dev_db.py` | documented/tested local reset command |
| `seed_control_plane.py` | `scripts/seed_control_plane.py` | documented seed workflow |
| `validate_control_plane.py` | `scripts/validate_control_plane.py` | documented schema validation workflow |

Phase 1 must:

1. inventory README, docs, CI, Docker, shell, and test references again;
2. make `python -m scripts.<name>` the documented canonical invocation;
3. verify every wrapper forwards arguments and exit codes correctly;
4. add deprecation text only if it does not break expected output consumers;
5. retain destructive confirmation and `--yes` behavior in reset;
6. retain wrappers until all external developer/operational workflows have had
   a compatibility window.

No evidence supports deleting any root wrapper in Phase 1.

## Files to preserve

- Every file under `alembic/versions/`, including revision IDs and
  `down_revision` links.
- `alembic.ini` and `alembic/env.py` at their current paths until migration
  command compatibility is proven.
- `app/models/__init__.py` and `app/models/tables.py` as metadata/import shims.
- All compatibility alias modules until old-path searches and tests prove them
  unused outside their intended window.
- Public route prefixes and request/response payloads, including
  `airflow_dag_run_id`.
- RAG document/version/run/chunk/query/retrieval IDs and deterministic Qdrant
  point lineage.
- MinIO Bronze/Silver/Gold object naming and recovery semantics.
- Airflow DAG/task names, Celery task names, retry behavior, callbacks, and
  service-token behavior.
- Redis event payloads, SSE replay/recovery behavior, and all environment
  variable names.
- Dockerfiles, compose service names/mounts/commands, e2e scripts, evaluation
  report formats, and the complete test suite during their migration windows.

## Files to move

Moves are conditional on the detailed map and phase gates above:

- Generic project files → `app/platform/projects/`.
- `app/platform/research` and `publication` → `app/research/` vertical domains.
- `app/platform/artifacts` → retain or move only after consumer inspection
  establishes whether Artifact is research-owned or a shared CCSR primitive.
- Generic portions of `app/platform/execution` → `app/execution/`.
- Concrete execution adapters → `app/infrastructure/orchestrators/`.
- `app/modules/ragforge` → vertical domains under
  `app/capabilities/ragforge/`.
- Shared ingestion business stages → RAGForge ingestion stages.
- Concrete PostgreSQL/MinIO/Qdrant/Redis/provider code → infrastructure while
  keeping domain policies in their owners.
- Airflow and Celery packaging → `runtimes/` only after Docker/runtime shims are
  ready.
- Tests → ownership-shaped paths after implementation paths stabilize.
- Alembic remains under `alembic/` by default. Relocation is optional, requires
  a concrete benefit and separate approval, and must never rewrite history.

## Compatibility wrappers needed

- Old → new Python import re-exports for every moved public module.
- Root maintenance-script wrappers forwarding argv and exit status.
- `app.models` metadata aggregation until Alembic has a stable new registry.
- Existing `app.workers.celery_app` and task import paths while Docker/worker
  commands migrate.
- Existing `airflow/` DAG/plugin paths or equivalent Docker mount shims while
  runtime packaging migrates.
- Existing `jobs.*` module CLI entry points while DAG command environment
  variables migrate.
- Existing execution imports under `app.platform.execution` while internal and
  downstream callers move to `app.execution`.
- Existing research/publication/artifact imports under `app.platform.*` while
  callers migrate to `app.research.*`.
- Existing `app.modules.ragforge` paths while callers migrate to
  `app.capabilities.ragforge`.
- API-field dual write/read for `IngestionRun.airflow_dag_run_id` and generic
  `Run.external_execution_id` until a separately approved API/schema contract
  phase.

Wrappers should issue no noisy runtime warnings in server, worker, migration, or
test imports unless output compatibility has been checked.

## Migration risks

### Data and schema

- Model import changes can silently omit tables from `Base.metadata`, affecting
  Alembic and reset/create utilities.
- Renaming Python packages does not justify renaming tables or columns.
- Migration 0006–0010 data establishes capability, authorization, execution,
  governance, and research state; moving code must preserve those mappings.
- PostgreSQL must own durable Chunk identity. Qdrant point IDs must derive
  deterministically from PostgreSQL chunk lineage; Qdrant is rebuildable and
  must never become the identity authority.

No fundamental conflict with the architecture source was found that currently
risks data loss. The apparent differences are migration-state differences:
research and execution are under `app/platform`, RAGForge is under
`app/modules`, migrations are under `alembic`, and runtime packaging is split.
These require compatibility migrations, not destructive correction.

### Runtime and behavior

- Import-time registry side effects can double-register or omit a workflow.
- Moving adapters can break patch targets and Celery serialization/import paths.
- Moving Airflow files can break volume mounts, command templates, plugin
  imports, DAG discovery, task IDs, or callback behavior.
- Splitting event streaming can break Redis replay ordering or PostgreSQL
  recovery even if endpoint tests still pass superficially.
- Verticalizing the project router can change Pydantic response fields or
  aggregate query counts.
- Consolidating benchmark code can accidentally normalize away meaningful
  engine differences or alter report schemas.
- Some dependencies are optional/heavy; import smoke tests must run in the same
  dependency profiles as FastAPI, Airflow, and Celery.

### Compatibility and operations

- Docker Compose references current backend paths and service/module names.
- Documentation and e2e scripts invoke Alembic from `backend/alembic.ini`.
- Frontend types and UI explicitly consume `airflow_dag_run_id`.
- Tests patch current module-qualified symbols; wrappers alone may not preserve
  monkeypatch behavior if symbol construction moves.
- Dirty, user-owned documentation changes already exist and must not be
  overwritten during later phases.

## Test coverage

The current suite includes 31 discovered `test_*.py` files:

- unit coverage for auth/models, platform/organization authorization,
  capability registry/configuration/lifecycle, execution gateway, quotas,
  artifacts/audit, research/publication, chunking, embeddings, ingestion,
  observability, frontend contracts, and ownership compatibility;
- integration coverage for PostgreSQL control-plane behavior, Qdrant lineage,
  Airflow, Celery, and streaming;
- separate Airflow and Celery benchmark tests;
- environment-driven end-to-end control-plane coverage.

Important gaps to add as the relevant phases begin:

- automated forbidden-import architecture tests;
- composition idempotency and adapter-registration tests;
- explicit MinIO and Redis integration directories/contracts;
- a local execution adapter contract if LocalRunner is introduced;
- fresh and existing-database Alembic upgrade gates before moving migrations;
- parity tests proving Airflow and Celery invoke the same stage contracts;
- compatibility-wrapper argv/exit-code and patch-target behavior;
- Docker Compose config/DAG discovery/worker import smoke checks.

Phase quality gates:

1. import `app.main` successfully;
2. start FastAPI and verify `/health` plus affected routes;
3. import Alembic metadata and verify one head;
4. run focused unit and integration tests for changed ownership;
5. run the full backend suite at major milestones;
6. search globally for the old path after every move;
7. inspect Docker, test, documentation, and script callers;
8. verify no circular imports and no migration-history loss.

No tests were run in Phase 0 because only a documentation plan was requested;
repository inspection was read-only apart from this file.

## Proposed phases

### Pre-Phase 2 known failure baseline

The full unit suite immediately before Phase 2 reported 138 passes and these
four pre-existing RAG observability errors. Phase 2 must not change their error
types or behavior and does not authorize fixing them:

| Test | Error type | Baseline behavior |
| --- | --- | --- |
| `RagObservabilityTests.test_cache_hit_is_logged_with_cached_retrieval_trace` | `fastapi.exceptions.HTTPException` | `403: Access denied` from `app.platform.access.policies._identity` |
| `RagObservabilityTests.test_empty_retrieval_still_logs_query` | `fastapi.exceptions.HTTPException` | `403: Access denied` from `app.platform.access.policies._identity` |
| `RagObservabilityTests.test_provider_failure_still_commits_query_and_retrieval_logs` | `AttributeError` | `insert_retrievals.await_args` is `None`, so accessing `.args` fails |
| `RagObservabilityTests.test_successful_query_logs_query_retrieval_scores_and_usage` | `fastapi.exceptions.HTTPException` | `403: Access denied` from `app.platform.access.policies._identity` |

### Phase 0 — Discovery (this document)

Complete. No application code or runtime configuration changed. Await approval.

### Phase 1 — Clean root and scripts

Canonicalize behavior under `backend/scripts/`; verify all six wrappers and
callers; preserve wrappers. Do not touch domain behavior.

Files affected by Phase 1 (expected):

- `backend/check_data.py`
- `backend/cleanup.py`
- `backend/create_tables.py`
- `backend/reset_dev_db.py`
- `backend/seed_control_plane.py`
- `backend/validate_control_plane.py`
- corresponding `backend/scripts/*.py` files only where forwarding/behavior
  gaps are proven
- `backend/tests/unit/test_reset_dev_db.py`
- new focused script-wrapper tests if needed
- current documentation/commands that still recommend root implementations

Phase 1 must not remove a root wrapper, modify schemas, or change cleanup/reset
targets without separate explicit approval.

### Phase 2 — Establish target package skeleton and composition seam

Create only necessary package roots and `composition.py`. Move registration
side effects behind idempotent composition functions while preserving
`app.main:app`.

### Phase 3 — Platform modules

Move generic projects first; normalize account/access/organization naming only
where useful; retain aliases. Keep capability registry, lifecycle, quotas, and
audit platform-owned.

### Phase 4 — RAGForge capability

Move canonical RAG code from `app/modules/ragforge` into vertical domains under
`app/capabilities/ragforge`, then absorb only clearly RAG-specific historical
aliases/services. Preserve old imports.

### Phase 5 — Shared ingestion business stages

Extract one tested RAGForge stage set. Convert jobs, DAG tasks, and Celery tasks
to thin adapters without changing task order, names, retries, idempotency,
commands, events, or artifact paths.

### Phase 6 — Generic execution contract

Move generic execution to `app/execution`; have composition register concrete
adapters/handlers. Add status/retry/cancel/events only to the extent supported
by existing behavior; do not pretend unsupported engine capabilities exist.

### Phase 7 — Infrastructure adapters

Extract concrete clients and adapter construction. Inject them at real module
boundaries, retaining small internal code where abstraction would add no value.

### Phase 8 — Research core

Move existing capability-neutral research, publication, and artifact behavior
into vertical `app/research` domains. Do not fabricate unimplemented models or
features merely to fill the target tree.

### Phase 9 — Evaluation cleanup

Diff every benchmark module semantically, extract shared behavior, and keep
Airflow/Celery-specific clients and submission/wait logic as adapters.

### Phase 10 — Test reorganization

Move tests to mirror stable ownership, updating patch targets carefully and
preserving all assertions. Add architecture-boundary tests.

### Phase 11 — Compatibility cleanup

Remove an alias or wrapper only after global old-path searches, Docker/CI/docs
inspection, focused tests, full backend tests, and an elapsed compatibility
window show it is safe.

### Phase 12 — Runtime packaging convergence (optional)

Move runtime packaging only if its benefit justifies the compatibility cost,
as its own isolated and tested change. Do not combine it with Alembic work.

### Phase 13 — Alembic relocation (optional and independent)

Keep `backend/alembic/` unless a concrete benefit is documented and the move is
separately approved. If performed, treat it as an independent change, preserve
every historical revision relationship, and verify fresh and existing-schema
upgrades. Never combine this work with runtime packaging.

### Phase 14 — Documentation convergence

Update `backend.md` only when implementation actually satisfies or
intentionally revises the architecture. Update the nearest `CONTEXT.md` and
verified System Map cards whenever ownership changes.

## Approval boundary

Phase 0 ends with this plan. No later phase is authorized by the creation of
this document. Phase 1 should begin only after explicit user approval.
