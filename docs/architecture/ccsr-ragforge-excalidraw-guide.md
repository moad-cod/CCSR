# CCSR and RAGForge architecture drawing guide

This guide describes the architecture that is implemented in this repository
and translates it into boxes and arrows that can be drawn in Excalidraw.

It deliberately separates current behavior from future CCSR ideas. Use solid
shapes for implemented components, orange outlines for experimental components,
and dashed gray shapes for planned components.

## 1. Product boundary

**CCSR** (Canonical Computer Science Research) is the platform. It owns the
research workspace shell, identity, organizations, projects, authorization,
capability composition, and shared control-plane contracts.

**RAGForge** is the first mature capability inside CCSR. It owns documents,
document versions, ingestion, chunking, embeddings, vector indexing, retrieval,
grounded generation, citations, and RAG-specific observability.

The repository is currently one deployable modular monolith:

```text
CCSR application
  +-- Next.js presentation layer
  +-- FastAPI composition root
      +-- CCSR platform packages
      +-- RAGForge capability module
      +-- shared/mixed infrastructure adapters
```

The intended dependency direction is:

```text
application composition root
  -> CCSR platform contracts
  -> registered capability modules
  -> infrastructure adapters

RAGForge -> stable CCSR platform contracts
CCSR platform -X-> RAGForge business logic
```

The capability boundary is only partially generalized today. RAGForge is
registered in an in-process capability registry and contributes project/account
deletion hooks. Projects do not yet have durable capability-association records,
and the frontend still assumes that every project has RAG features.

## 2. Status legend for the drawing

| Visual style | Meaning | Examples |
| --- | --- | --- |
| Solid blue | Implemented CCSR platform | Authentication, organizations, projects, capability registry |
| Solid violet | Implemented RAGForge | Ingestion, chunking, retrieval, citations |
| Solid green | Runtime infrastructure | PostgreSQL, MinIO, Qdrant, Redis |
| Orange outline | Optional or experimental | Multimodal PDF path, R2, ColQwen2, cross-encoder reranker |
| Dashed gray | Planned, not implemented | Generic experiments, dataset/model registries, findings, publications |
| Red arrow | Destructive lifecycle operation | Project/account deletion cleanup |
| Dashed arrow | Best-effort or optional interaction | Redis events/cache, optional reranking, optional external orchestrator |

Recommended palette:

- Canvas: `#0B0F14`
- CCSR/platform: `#3B82F6`
- RAGForge: `#8B5CF6`
- Infrastructure: `#22C55E`
- Experimental: `#F59E0B`
- External providers: `#64748B`
- Destructive lifecycle: `#EF4444`
- Primary text: `#E5E7EB`

## 3. CCSR features

### 3.1 Identity and account management

- Register with email and password.
- Login with bcrypt password verification.
- Receive a seven-day HS256 JWT from FastAPI.
- Keep the JWT in a server-managed HttpOnly frontend cookie.
- Read and update the current profile, including name, email, password, and
  active organization.
- Soft-delete an account and its owned projects.

Not currently implemented: OAuth, refresh sessions, token revocation, password
recovery, or platform-wide administrator roles.

### 3.2 Organizations and membership

- Create, list, read, rename, and soft-delete organizations.
- Creating an organization also creates an owner membership.
- Active memberships control organization visibility.
- Owner and admin memberships can mutate an organization.
- A user can select an active organization.
- A project can optionally be associated with an organization.

Project/RAG access is still checked with `Project.created_by`. Organization
membership does not grant access to another member's projects.

Not currently implemented: invitations, membership-management APIs, project
roles, or organization-wide project collaboration.

### 3.3 Projects and Labs

- Create, list, read, rename, and soft-delete owner-scoped projects.
- Reserve a unique Qdrant collection name for every current project.
- Present projects as research Labs in the frontend.
- Show project overview, research evidence, results, artifacts, test workspace,
  reproduction readiness, sources, pipelines, and observability.
- Aggregate source, ingestion-run, query, latency, cache, and failure evidence.

Some Lab pages summarize real RAG evidence in a broader research vocabulary.
They are not backed by generic experiment, dataset, model, or finding records.

### 3.4 Capability composition and lifecycle

- The FastAPI composition root registers the `ragforge` capability.
- The platform registry stores capability definitions in deterministic order.
- Project deletion sends a `ProjectDeletionContext` to registered hooks.
- Account deletion sends an `AccountDeletionContext` to registered hooks.
- RAGForge contributes vector, document, and image cleanup without the platform
  deletion routes importing RAGForge business code.
- Hook results can contribute capability-neutral deleted-resource counts.

This is an in-process lifecycle seam. It is not yet a durable capability
enablement or plugin-installation system.

### 3.5 Frontend control-plane experience

- Next.js App Router application with a graphite, blue, and violet research UI.
- Same-origin backend proxy keeps bearer tokens out of browser JavaScript.
- Project/Lab discovery and management.
- Global and project-scoped sources, runs, history, and observability.
- Guided onboarding for selecting sources and chunking strategies.
- Streaming ingestion progress with polling recovery.
- Streaming RAG playground with provider selection, source filtering, Markdown
  answers, citations, retrieval traces, and persisted history.
- Organization management and profile settings.

The frontend uses real backend evidence. Generic experiment creation and
comparison routes are explicitly presented as planned rather than populated
with fake records.

## 4. RAGForge features

### 4.1 Source and version management

- Logical documents belong to a project.
- Re-uploading the same filename with different content creates a new immutable
  `DocumentVersion`.
- SHA-256 content hashes prevent duplicate content for the same logical
  document.
- Document detail includes current status, metadata, versions, linked runs, and
  deletion controls.
- Supported durable file formats: PDF, DOCX, XLSX, PPTX, CSV, HTML/HTM,
  Markdown, and plain text.
- Additional source paths: public URL and Google Drive.

### 4.2 Durable file-ingestion pipeline

The complete path begins at `POST /ingest/file`:

```text
validate project, file, size, and chunker
  -> upload raw bytes to MinIO Bronze
  -> create Document + DocumentVersion + IngestionRun in PostgreSQL
  -> enqueue Airflow or Celery
  -> parse and chunk into Silver Parquet
  -> embed into Gold Parquet
  -> idempotently index Qdrant and PostgreSQL Chunk lineage
  -> mark the version current and the run indexed
  -> stream progress to the frontend
```

PostgreSQL is the authoritative state machine. Airflow and Celery execute the
same five logical stages:

1. Detect the ingestion plan and mark the run running.
2. Transform Bronze source data into Silver chunks.
3. Embed Silver chunks into Gold artifacts.
4. Upsert deterministic dense and sparse points into Qdrant.
5. Finalize the run and current document version.

Failed runs retain durable state and can be retried. Deterministic chunk and
point identifiers make repeated indexing safe.

### 4.3 Synchronous ingestion paths

- URL ingestion fetches, parses, chunks, embeds, and indexes during the HTTP
  request.
- Google Drive ingestion does the same with a supplied access token.
- These paths create indexed document versions but do not create the complete
  Bronze/Silver/Gold artifact, ingestion-run, or PostgreSQL chunk lineage.

Draw these as a shorter violet path directly from FastAPI to Qdrant and
PostgreSQL, separate from the durable orchestrated pipeline.

### 4.4 Chunking strategies

The chunker registry exposes metadata without loading heavy implementations.

| Strategy | Main behavior | Status/runtime note |
| --- | --- | --- |
| Paragraph | Natural paragraph packing | Stable default |
| Fixed size | Predictable windows with overlap | Stable baseline |
| Sentence | Sentence-boundary units | Uses NLTK or fallback |
| Semantic | Embedding-aware topic boundaries | Beta |
| Hierarchical | Parent and child chunks | Beta; supports parent-context retrieval |
| Late chunking | Sentence groups with pooled vectors | Beta; reuses precomputed vectors |
| Proposition | LLM-extracted atomic propositions | Beta; Groq/network dependent |
| Multimodal | Visual PDF page embeddings | Optional heavy runtime |

### 4.5 Embedding and indexing

- Dense text embeddings use FastEmbed with `BAAI/bge-small-en-v1.5` by default.
- Sparse text embeddings use BM25 features.
- Qdrant collections contain named dense and sparse vectors plus payload
  filters for project, document, version, and chunk lineage.
- Durable file ingestion also writes `Chunk` rows to PostgreSQL.
- Qdrant is treated as rebuildable derived state; PostgreSQL and stored
  artifacts preserve the durable lineage.

### 4.6 Retrieval and grounded generation

```text
question
  -> authenticate and verify project/document ownership
  -> Redis cache lookup
  -> dense query embedding + sparse query embedding
  -> Qdrant dense/sparse prefetch
  -> reciprocal-rank fusion
  -> optional cross-encoder reranking
  -> optional parent-context replacement
  -> grounded prompt
  -> Gemini or Groq generation
  -> answer, citations, query log, and retrieval logs
```

- Hybrid search defaults to five returned hits after fetching larger dense and
  sparse candidate sets.
- Optional document filtering narrows retrieval to one source.
- Hierarchical retrieval can replace child text with deduplicated parent text.
- The generation prompt requires answers to be grounded in retrieved context.
- Gemini and Groq are called through OpenAI-compatible APIs.
- Cross-encoder reranking degrades gracefully when its optional dependency is
  unavailable.

### 4.7 Streaming and observability

- Query SSE emits received, embedding, retrieving, reranking, generating,
  token, completed, and failed events.
- Browser disconnection does not cancel the retained query task or durable
  query logging.
- Query events are not replayable.
- Ingestion SSE begins with a PostgreSQL snapshot, can replay Redis Stream
  events after `Last-Event-ID`, polls PostgreSQL for recovery, sends heartbeats,
  and stops at a terminal state.
- `QueryLog` stores the question, answer, provider/model, latency, route, and
  cache status.
- `RetrievalLog` stores rank, vector score, optional rerank score, retrieval
  strategy, evidence text, and links to document/chunk lineage when available.

### 4.8 Evaluation and benchmarking

- Airflow and Celery benchmark CLIs drive real ingestion APIs.
- Benchmarks write JSON and Markdown reports.
- Recorded measures include latency, queue time, processing time, throughput,
  success rate, recovery time, retry overhead, duplicate processing, and
  scaling efficiency.
- A BEIR/SciFact retrieval-evaluation configuration exists, but a complete
  verified runner is still in progress.

### 4.9 Experimental multimodal path

- Accept a PDF and render pages with PyMuPDF.
- Embed pages with a ColQwen2-style model.
- Store rendered page images in Cloudflare R2.
- Store multi-vector page embeddings in a separate
  `<project_collection>_multimodal` Qdrant collection.
- Retrieve page images and send them to Gemini vision for an answer.

The base Docker image does not contain the heavy PyTorch/ColPali dependencies.
Draw this entire path with orange outlines and an `optional` label.

## 5. Recommended Excalidraw canvas

Use a landscape canvas with six vertical zones from left to right.

### Zone A: people and source systems

| ID | Box label | Detail |
| --- | --- | --- |
| A1 | Researcher | Registers, creates Labs, uploads sources, runs queries |
| A2 | Browser | Holds the HttpOnly session cookie and renders SSE updates |
| A3 | Source systems | Local files, public URLs, Google Drive |

### Zone B: CCSR presentation

Place these inside a large solid-blue container named **CCSR Next.js UI**.

| ID | Box label | Detail |
| --- | --- | --- |
| B1 | Auth route handlers | Login, register, logout, HttpOnly cookie |
| B2 | Same-origin API proxy | Adds the backend bearer token and streams responses |
| B3 | Platform screens | Home, Labs/projects, organization, profile |
| B4 | RAG workspace screens | Sources, onboarding, runs, playground, history, observability |

### Zone C: FastAPI modular monolith

Draw one large graphite container named **FastAPI application**. Put two nested
containers inside it.

**CCSR platform container — solid blue**

| ID | Box label | Detail |
| --- | --- | --- |
| C1 | Accounts and authentication | JWT, profile, account lifecycle |
| C2 | Organizations and memberships | Member visibility; owner/admin mutations |
| C3 | Projects | Creator-owned project CRUD |
| C4 | Capability registry | Registers RAGForge lifecycle hooks |
| C5 | Shared control-plane adapters | Orchestrator selection, SSE/event support, service-token boundary |

**RAGForge capability container — solid violet**

| ID | Box label | Detail |
| --- | --- | --- |
| C6 | Source APIs | Documents, versions, file/URL/Drive/multimodal ingestion |
| C7 | Ingestion services | Parsing, planning, artifact transforms, retry/status logic |
| C8 | Chunker registry | Eight selectable strategies and lazy loading |
| C9 | Embedding and indexing | Dense/sparse vectors, deterministic lineage |
| C10 | Retrieval and generation | Hybrid RRF, optional rerank, Gemini/Groq |
| C11 | Query observability | Query history, retrieval traces, citations, cache |
| C12 | RAGForge lifecycle adapter | Project/account cleanup hooks |

Put a small composition-root diamond above both nested containers:

| ID | Diamond label | Detail |
| --- | --- | --- |
| C0 | Application composition root | Includes routers and registers `ragforge` |

### Zone D: execution plane

| ID | Box label | Style | Detail |
| --- | --- | --- | --- |
| D1 | Orchestrator selector | Blue/violet split | Chooses from `ORCHESTRATOR` |
| D2 | Airflow DAG | Violet | Optional Airflow profile |
| D3 | Celery worker chain | Violet | Optional Celery profile |
| D4 | Shared ingestion stages | Violet | Plan, Bronze->Silver, Silver->Gold, index, finalize |
| D5 | Benchmark CLIs | Gray | Drive APIs and produce benchmark reports |

Airflow and Celery are alternatives. Draw both pointing to the same `D4` box;
do not draw two different business pipelines.

### Zone E: data services

Use database cylinders.

| ID | Cylinder label | Stored responsibility |
| --- | --- | --- |
| E1 | PostgreSQL | Authoritative users, memberships, projects, documents, versions, runs, chunks, query/retrieval logs |
| E2 | MinIO | Bronze raw files, Silver chunk Parquet, Gold embedding Parquet |
| E3 | Qdrant | Rebuildable dense/sparse vectors and optional multimodal vectors |
| E4 | Redis | Best-effort query cache, ingestion event replay, Celery broker/results |
| E5 | Cloudflare R2 | Optional rendered PDF page images |
| E6 | Benchmark artifacts | Generated JSON and Markdown reports |

If the diagram shows the internal Airflow deployment, add a separate
`Airflow PostgreSQL` cylinder. It is Airflow metadata, not CCSR application
metadata.

### Zone F: external AI providers

| ID | Box label | Detail |
| --- | --- | --- |
| F1 | Gemini API | Text generation and optional multimodal vision |
| F2 | Groq API | Text generation and proposition extraction |
| F3 | Model cache | Local FastEmbed model files shared by API/workers |

## 6. Connectors to draw

Use these arrows for the main system diagram.

| From | To | Arrow label | Style |
| --- | --- | --- | --- |
| A1 | A2 | Uses | Solid |
| A2 | B1 | Login/register/logout | Solid |
| A2 | B3/B4 | Navigate and interact | Solid |
| B1 | C1 | Credentials/JWT | Solid |
| B2 | C0 | HTTPS + Bearer token | Solid |
| C0 | C1-C5 | Platform routes/contracts | Solid blue |
| C0 | C6-C12 | Registered RAG routes/module | Solid violet |
| C1/C2/C3 | E1 | Durable control-plane state | Solid |
| C4 | C12 | Lifecycle hook dispatch | Red for deletion flow |
| A3 | C6 | Files, URLs, Drive token | Solid |
| C6/C7 | E1 | Documents, versions, runs, statuses | Solid |
| C6/C7 | E2 | Bronze/Silver/Gold artifacts | Solid |
| C7 | D1 | Enqueue ingestion run | Solid |
| D1 | D2 | Airflow mode | Solid |
| D1 | D3 | Celery mode | Solid |
| D2/D3 | D4 | Execute common stages | Solid |
| D4 | C5/C7 | Service-token pipeline callbacks | Solid |
| C9/D4 | E3 | Dense/sparse vector upsert | Solid |
| C9/D4 | E1 | Chunk and embedding lineage | Solid |
| C10 | E3 | Filtered hybrid retrieval | Solid |
| C10 | F1/F2 | Grounded generation | Solid |
| C11 | E1 | Query and retrieval logs | Solid |
| C11 | E4 | Query cache | Dashed |
| C5 | E4 | Ingestion event publish/replay | Dashed |
| C5 | B2/B4 | SSE snapshots, stages, tokens | Solid |
| C12 | E3/E5 | Delete RAG resources | Red |
| D5 | C6/C5 | Benchmark real ingestion workflow | Solid |
| D5 | E6 | Write reports | Solid |
| C6/C9/C10 | E5 | Optional multimodal pages | Orange dashed |
| C10 | F1 | Optional vision question | Orange dashed |

## 7. Five sequence flows to draw separately

### Flow 1: authentication

```text
Researcher
  -> Next.js auth handler
  -> FastAPI accounts API
  -> PostgreSQL user lookup/create
  -> signed JWT
  -> HttpOnly cookie
  -> same-origin proxy adds Bearer token to later requests
```

### Flow 2: durable file ingestion

```text
Browser -> Next.js proxy -> FastAPI RAGForge ingestion API
  -> MinIO Bronze
  -> PostgreSQL DocumentVersion + IngestionRun
  -> orchestrator selector -> Airflow OR Celery
  -> shared stages -> Silver -> Gold
  -> FastAPI internal pipeline API
  -> Qdrant vectors + PostgreSQL chunks/status
  -> Redis event -> FastAPI SSE -> Browser progress
```

### Flow 3: streamed RAG query

```text
Browser -> Next.js streaming proxy -> FastAPI query API
  -> ownership check in PostgreSQL
  -> Redis cache lookup
  -> dense + sparse query embedding
  -> Qdrant hybrid retrieval and RRF
  -> optional reranking/parent context
  -> Gemini or Groq
  -> SSE stage/token events -> Browser
  -> PostgreSQL QueryLog + RetrievalLog
  -> best-effort Redis cache write
```

### Flow 4: project deletion through the capability seam

```text
Browser -> platform project route
  -> verify creator ownership
  -> capability registry
  -> RAGForge before-project-delete hook
      -> delete document vectors
      -> best-effort delete multimodal images
      -> delete text and multimodal collections
      -> mark documents deleted
  -> mark project deleted
  -> PostgreSQL commit
```

### Flow 5: observability and reproduction evidence

```text
Frontend Lab views
  -> projects + documents + versions
  -> ingestion runs and embedding progress
  -> query history and retrieval traces
  -> aggregate readiness, latency, cache, failure, citation, and artifact evidence
```

This flow derives views from existing RAG records. It does not create a generic
experiment or reproducibility-manifest entity.

## 8. Data-model relationships

Draw this as a separate entity diagram or a lower strip on the main canvas:

```text
Organization 1 ---- * OrganizationMembership * ---- 1 User
Organization 1 ---- * Project                  (optional grouping)
User         1 ---- * Project                  (creator ownership)
Project      1 ---- * Document
Document     1 ---- * DocumentVersion
Document     1 ---- 0..1 current DocumentVersion
Project      1 ---- * IngestionRun
DocumentVersion 1 -- * IngestionRun
DocumentVersion 1 -- * Chunk
DocumentVersion 1 -- * EmbeddingRun
Project      1 ---- * QueryLog
QueryLog     1 ---- * RetrievalLog
RetrievalLog * ---- 0..1 Chunk
```

Label `User -> Project` as the current security boundary. The organization link
groups records but does not replace creator ownership for project/RAG access.

## 9. Storage truth and failure boundaries

Add these notes beside the data-service cylinders:

- **PostgreSQL is authoritative.** Durable status, identity, ownership, lineage,
  and query evidence live here.
- **MinIO preserves ingestion artifacts.** It stores the rebuild inputs and
  intermediate outputs for durable file ingestion.
- **Qdrant is derived and rebuildable.** It is optimized retrieval state, not
  the metadata source of truth.
- **Redis is best-effort.** Cache or event loss must not erase durable run state.
- **Qdrant and PostgreSQL are not one transaction.** Deterministic IDs and retry
  repair temporary mismatches.
- **External orchestration is optional.** Without a configured Airflow or Celery
  adapter, a landed run remains durable but does not advance automatically.

## 10. What not to draw as implemented

If these concepts appear, use dashed gray boxes labelled `planned`:

- Generic experiment definitions and experiment runs.
- Dataset and model registries.
- Cross-domain NLP, Computer Vision, or fine-tuning workflows.
- Findings, research notes, publications, and mathematical concept graphs.
- Complete reproducibility manifests.
- Durable project-capability associations.
- Generic workflow definitions and generic run gateway.
- Project collaboration, project roles, invitations, quotas, and platform-wide
  administration.
- Local Ollama generation.

## 11. Minimal diagram version

For a presentation slide, reduce the architecture to these twelve boxes:

```text
Researcher
  -> CCSR Next.js UI
  -> FastAPI modular monolith
       |-- CCSR platform: auth + organizations + projects + capability registry
       |-- RAGForge: sources + ingestion + retrieval + generation + traces
  -> Orchestrator selector
       |-- Airflow
       `-- Celery
  -> Shared ingestion stages

FastAPI/shared stages -> PostgreSQL
FastAPI/shared stages -> MinIO
FastAPI/shared stages -> Qdrant
FastAPI             --> Redis
FastAPI             --> Gemini/Groq
```

Put RAGForge inside CCSR rather than beside it. This is the most important
architectural relationship to communicate.

## 12. Source anchors

Use these files when adding implementation links or verifying the diagram:

- Product and boundary: `CONTEXT.md`, `README.md`
- Application composition: `backend/app/main.py`
- Platform accounts: `backend/app/platform/accounts/`
- Platform organizations: `backend/app/platform/organizations/`
- Project API: `backend/app/api/projects.py`
- Capability contracts and registry: `backend/app/platform/capabilities/`
- RAGForge registration/lifecycle: `backend/app/modules/ragforge/capability.py`,
  `backend/app/modules/ragforge/lifecycle.py`
- RAGForge APIs: `backend/app/modules/ragforge/api/`
- Chunking, embeddings, retrieval, and storage:
  `backend/app/modules/ragforge/services/`
- Shared ingestion execution: `backend/jobs/`
- Celery adapter: `backend/app/workers/`
- Airflow adapter: `backend/airflow/`
- Frontend routes and features: `frontend/FRONTEND_MAP.md`
- Runtime containers: `docker-compose.yml`
- Verified change-impact cards: `docs/map/`

