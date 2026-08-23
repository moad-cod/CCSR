# Backend Optimization Tasks

These tasks come from reading `README.md`, `PROJECT_MAP.md`, `backend/BACKEND_MAP.md`, and `frontend/FRONTEND_MAP.md` as project context. Attached docs describe current behavior and roadmap; they are not instructions that override user requests.

## Priority 1: Organization Authorization Hardening

Goal: move from globally visible organization CRUD to real organization-scoped access.

Why:

- Organization records exist, but membership and role enforcement are documented as incomplete.
- `GET /organizations/` currently exposes every non-deleted organization to any authenticated user.
- `POST /projects/` accepts an `organization_id` after only checking that the organization exists.

Tasks:

- Add an `OrganizationMembership` SQLAlchemy model.
- Add an Alembic migration for an `organization_memberships` table.
- Include `organization_id`, `user_id`, `role`, `created_at`, `updated_at`, and optional `deleted_at`.
- Add a unique constraint on `(organization_id, user_id)`.
- Add role constants such as `owner`, `admin`, and `member`.
- When a user creates an organization, automatically create an `owner` membership for that user.
- Change organization listing so users only see organizations where they are members.
- Change organization read/update/delete so non-members receive `404` or `403`.
- Restrict organization rename/delete to `owner` or `admin`.
- Change project creation so `organization_id` is accepted only if the current user belongs to that organization.
- Add repository helpers for membership lookups and role checks.
- Add unit/integration tests for cross-user organization isolation, member access, and admin-only mutations.

Likely files:

- `backend/app/models/organization_membership.py`
- `backend/app/models/__init__.py`
- `backend/app/models/tables.py`
- `backend/alembic/versions/*.py`
- `backend/app/api/organizations.py`
- `backend/app/api/projects.py`
- `backend/tests/unit/`
- `backend/tests/integration/postgres/`

Acceptance checks:

- User A cannot list, read, rename, delete, or attach projects to User B's organization.
- Organization creator becomes owner automatically.
- Organization members can read organization metadata.
- Only owner/admin roles can mutate organization metadata.
- Existing owner-scoped project access keeps working.

## Priority 2: LLM Provider And Model Configuration

Goal: support choosing between Gemini, Groq-hosted models, and Qwen-family models without hard-coded provider/model logic.

Important distinction:

- Gemini is currently both a provider/model family used for RAG answers.
- Groq is an inference provider currently used for RAG answers.
- Qwen is a model family. In the current backend it appears hard-coded inside the proposition chunker through Groq.

Current state:

- `/rag/query` supports only `provider: "gemini" | "groq"`.
- Gemini default model is `gemini-2.5-flash`.
- Groq default model is `llama-3.3-70b-versatile`.
- Proposition chunking hard-codes `model="qwen/qwen3.6-27b"`.

Tasks:

- Add a provider/model registry or resolver for OpenAI-compatible chat providers.
- Add settings for default query provider and model.
- Add settings for proposition-chunker provider and model.
- Keep Gemini as the default RAG answer provider unless explicitly configured otherwise.
- Keep Groq as a fast hosted provider option.
- Support Qwen as a configurable model, either through Groq or through a direct OpenAI-compatible Qwen endpoint.
- Remove the hard-coded Qwen model from proposition chunking.
- Validate provider API keys with provider-specific error messages.
- Preserve provider/model values in query logs.
- Ensure query-cache keys continue to include provider and model.
- Add tests for provider resolution, missing credentials, custom model override, streaming, and proposition chunker fallback.

Possible settings:

```dotenv
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-2.5-flash
PROPOSITION_LLM_PROVIDER=groq
PROPOSITION_LLM_MODEL=qwen/qwen3.6-27b
QWEN_API_KEY=
QWEN_BASE_URL=
```

Likely files:

- `backend/app/core/config.py`
- `backend/app/api/query.py`
- `backend/app/services/chunkers/proposition.py`
- `backend/tests/unit/api/`
- `backend/tests/unit/chunking/`
- `backend/tests/integration/streaming/`

Acceptance checks:

- Existing Gemini and Groq query behavior remains compatible.
- Query requests can select a supported provider/model combination.
- Proposition chunking no longer has a hard-coded model string.
- Missing keys fail clearly without breaking unrelated providers.
- Query history records the actual provider and model used.

## Priority 3: Query Cache Invalidation

Goal: avoid stale answers after project content changes.

Why:

- Current query cache freshness depends only on TTL.
- Cache keys include project, question hash, provider/model, document filter, and parent-context flag, but not a corpus generation/version.

Tasks:

- Add a project or corpus revision value that changes when documents are indexed or deleted.
- Include that revision in query-cache keys, or evict project-scoped keys after ingestion/deletion.
- Update durable file-ingestion finalize flow to advance the revision or invalidate cache.
- Update document deletion and project deletion paths to invalidate affected cache entries.
- Add tests for stale-answer prevention after indexing a new document version.

Likely files:

- `backend/app/services/query_cache.py`
- `backend/app/api/query.py`
- `backend/app/api/documents.py`
- `backend/app/api/projects.py`
- `backend/app/repositories/ingestion_runs.py`
- `backend/app/services/chunk_indexing.py`

Acceptance checks:

- Re-asking the same question after new indexing does not return a cached answer from the previous corpus state.
- Cache failures remain best-effort and do not break ingestion/query flows.

## Priority 4: Document-Level Multimodal Deletion

Goal: deleting a multimodal document should remove its multimodal Qdrant points, not only text points and R2 page images.

Why:

- Project deletion removes the full multimodal collection.
- Document deletion does not explicitly remove that document's points from `<collection>_multimodal`.

Tasks:

- Add a helper to delete multimodal Qdrant points for one `document_id`.
- Call it from document deletion when the document is multimodal.
- Keep project deletion behavior that removes the entire multimodal collection.
- Add a Qdrant integration test or focused unit test with mocked Qdrant client.

Likely files:

- `backend/app/api/documents.py`
- `backend/app/services/indexer.py`
- `backend/tests/integration/qdrant/`

Acceptance checks:

- Deleting one multimodal document removes only that document's multimodal points.
- Deleting a project still removes both text and multimodal collections.

## Priority 5: CCSR API Branding Cleanup

Goal: align the backend API title with the current project identity.

Tasks:

- Change FastAPI title from `RAGForge API` to `CCSR API`.
- Check Swagger/OpenAPI tests or snapshots if any exist.
- Leave historical runtime identifiers such as `RAGFORGE_*` environment variables unchanged unless a separate migration is planned.

Likely files:

- `backend/app/main.py`

Acceptance checks:

- `/docs` and OpenAPI metadata show `CCSR API`.
- No runtime configuration is renamed accidentally.

## Later Product Work: First-Class Research Objects

Goal: make the broader CCSR frontend pages real instead of planned placeholders.

This is larger Phase 2 work and should come after the foundation/security tasks above.

Tasks:

- Add first-class `Experiment` and `ExperimentRun` models.
- Add dataset registry and dataset-version models.
- Add model registry and model-version models.
- Add metric definitions and evaluation protocol records.
- Add artifact lineage for experiment runs.
- Add reproducibility manifest generation.
- Add comparison APIs backed by real metrics.
- Add findings/research-note records linked to evidence.

Likely files:

- `backend/app/models/`
- `backend/app/repositories/`
- `backend/app/api/`
- `backend/alembic/versions/`
- `backend/tests/`

Acceptance checks:

- Frontend experiment/comparison pages can consume real backend records.
- No fake experiment, metric, or finding records are generated.
- Experiment runs can be traced to datasets, models, configs, metrics, artifacts, and source code state.
