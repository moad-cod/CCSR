# CCSR Frontend Map

This document maps the current frontend implementation for CCSR, Canonical
Computer Science Research. It describes implemented behavior only, including
which backend APIs each feature uses. Planned research-system concepts are
called out as backend blockers rather than presented as working product
surfaces.

## Product Model

CCSR is a local-first research engineering system for computer science and AI
experimentation. The frontend currently presents a broader research Lab model,
while the strongest implemented workflow remains Retrieval-Augmented
Generation:

```text
Project/Lab
  -> Sources
  -> Ingestion runs
  -> Indexed corpus
  -> Interactive RAG test
  -> Retrieval traces and citations
  -> Persisted query history
  -> Results, artifacts, and reproducibility evidence
```

The UI is intentionally honest about unsupported functionality. It does not
fabricate experiment records, evaluation scores, model registries, dataset
registries, cost metrics, or research findings when no backend contract exists.

## Stack

| Area | Current implementation |
| --- | --- |
| Framework | Next.js App Router, React, TypeScript |
| Styling | Tailwind CSS v4 through `frontend/src/app/globals.css` |
| Design identity | Dark graphite research UI with restrained CCSR blue and research violet accents |
| Data fetching | TanStack Query |
| Forms | React Hook Form and Zod where schema validation is needed |
| Notifications | `sonner` toast system |
| Icons | `lucide-react` |
| Markdown | `react-markdown` with `remark-gfm` |
| Tests | Vitest, Testing Library, Playwright config |
| Auth | HttpOnly `ragforge_session` compatibility cookie set by Next.js route handlers |

## Auth And API Flow

The browser never reads or stores the backend JWT directly.

```text
Browser UI
  -> /api/auth/login | /api/auth/register | /api/auth/logout
  -> HttpOnly ragforge_session cookie
  -> /api/backend/[...path] same-origin proxy
  -> FastAPI backend with Authorization: Bearer <token>
```

### Frontend Route Handlers

| Frontend handler | Backend connection | Behavior |
| --- | --- | --- |
| `/api/auth/login` | `POST /auth/login` | Sends form-encoded credentials to the backend and stores `access_token` in the HttpOnly `ragforge_session` cookie. |
| `/api/auth/register` | `POST /auth/register` | Proxies registration JSON to the backend. |
| `/api/auth/logout` | `POST /auth/logout` | Best-effort revokes the durable backend session, then clears the `ragforge_session` cookie. |
| `/api/backend/[...path]` | Any authenticated backend path | Adds `Authorization: Bearer <cookie token>`, forwards request body and selected headers, and streams backend responses back to the UI. |

`BACKEND_URL` controls the backend origin. If unset, the frontend uses
`http://localhost:8000`.

## Current Folder Structure

```text
frontend/
  FRONTEND_MAP.md
  components.json
  eslint.config.mjs
  next.config.ts
  package.json
  playwright.config.ts
  postcss.config.mjs
  tsconfig.json
  src/
    app/
      (auth)/
        layout.tsx
        login/page.tsx
        register/page.tsx
      (dashboard)/
        layout.tsx
        home/page.tsx
        labs/page.tsx
        projects/page.tsx
        runs/page.tsx
        observability/page.tsx
        organization/page.tsx
        experiments/page.tsx
        comparisons/page.tsx
        documents/page.tsx
        history/page.tsx
        settings/profile/page.tsx
        projects/[projectId]/
          page.tsx
          overview/page.tsx
          research/page.tsx
          experiments/page.tsx
          results/page.tsx
          artifacts/page.tsx
          test/page.tsx
          reproduce/page.tsx
          sources/page.tsx
          playground/page.tsx
          pipelines/page.tsx
          settings/page.tsx
          onboarding/page.tsx
          observability/page.tsx
          chat/page.tsx
          documents/page.tsx
          evaluation/page.tsx
          history/page.tsx
          runs/page.tsx
          runs/[runId]/
          history/[queryId]/
          documents/[documentId]/
          experiments/new/page.tsx
          experiments/[experimentId]/page.tsx
      api/
        auth/
        backend/[...path]/
      globals.css
      layout.tsx
      page.tsx
    components/
      labs/
      onboarding/
      ui/
      workspace/
      app-shell.tsx
      document-detail.tsx
      ingestion-run-detail.tsx
      ingestion-runs-page.tsx
      project-overview.tsx
      project-pipelines-page.tsx
      query-detail.tsx
      query-history-page.tsx
    hooks/
      use-ingestion-stream.ts
      use-workspace-overview.ts
    lib/
      api.ts
      server-auth.ts
      sse.ts
      types.ts
      utils.ts
    test/
      setup.ts
```

## Route Map

### Implemented Primary Routes

| Route | Feature | Characteristics | Backend APIs |
| --- | --- | --- | --- |
| `/` | Root redirect | Redirects authenticated users into project workspace flow. | none |
| `/login` | Login | CCSR sign-in, validation, password visibility, toast errors, auth ambience. | `POST /api/auth/login` -> backend `POST /auth/login` |
| `/register` | Registration | Account creation, password confirmation, auto-login after successful registration. | `POST /api/auth/register` -> backend `POST /auth/register`; then `POST /api/auth/login` |
| `/publications` | Public research index | Unauthenticated cards built only from immutable public publication revisions. | `GET /publications` through the GET-only public proxy allowlist |
| `/publications/[slug]` | Public research detail | Public-safe study, question, hypothesis, experiment, finding, and artifact projections without run inputs or storage locations. | `GET /publications/{slug}` through the GET-only public proxy allowlist |
| `/home` | Workspace home | Cross-project project/research and enabled RAGForge summaries without request fan-out. | `GET /projects/overview`; `GET /rag/workspace/overview?include=documents,runs,history`; optional create APIs |
| `/labs` | Lab discovery | Project-backed Lab discovery with aggregate readiness and permission-aware actions. | `GET /projects/overview`; `GET /rag/workspace/overview`; project mutation APIs |
| `/projects` | Project index | Capability-aware project browser with aggregate stats and permission-aware actions. | `GET /projects/overview`; `GET /rag/workspace/overview`; project mutation APIs |
| `/documents` | Global RAG source browser | Cross-project source list for RAGForge-enabled projects. | `GET /projects/overview`; `GET /rag/workspace/overview?include=documents`; `DELETE /documents/{document_id}` |
| `/history` | Global RAG query history | Cross-project persisted query history for RAGForge-enabled projects. | `GET /projects/overview`; `GET /rag/workspace/overview?include=history` |
| `/runs` | Global RAG ingestion runs | Cross-project ingestion run list without per-project requests. | `GET /projects/overview`; `GET /rag/workspace/overview?include=documents,runs` |
| `/observability` | Global RAG observability | Aggregated source, ingestion, query, latency, cache, and failure evidence. | `GET /projects/overview`; `GET /rag/workspace/overview?include=documents,runs,history` |
| `/organization` | Organization management | Organization list, create, rename, delete, active organization indication. | `GET /organizations/`; `POST /organizations/`; `PATCH /organizations/{organization_id}`; `DELETE /organizations/{organization_id}`; `GET /auth/me` |
| `/settings/profile` | Profile settings | Current-user profile, organization selection, optional password update. | `GET /auth/me`; `PATCH /auth/me`; `GET /organizations/` |

### Project Lab Routes

| Route | Feature | Characteristics | Backend APIs |
| --- | --- | --- | --- |
| `/projects/[projectId]/overview` | Project overview | Platform research/run/artifact/publication counts plus a separate enabled RAGForge summary. | `GET /projects/{project_id}/overview`; conditional `GET /rag/projects/{project_id}/overview` |
| `/projects/[projectId]/research` | Lab research/paper | Durable study/question/hypothesis/methodology content with existing RAG source and run evidence as a compatibility fallback. | `GET /projects/{project_id}`; `GET /projects/{project_id}/research/studies`; `GET /projects/{project_id}/research/studies/{study_id}`; source/run/version APIs |
| `/projects/[projectId]/experiments` | Experiment evidence | Durable experiment records plus existing A/B/C/D readiness and operational evidence. | `GET /projects/{project_id}`; `GET /projects/{project_id}/research/experiments`; document, ingestion, and query-history APIs |
| `/projects/[projectId]/results` | Results | Real persisted query results, latency/cache summaries, comparison summary, findings from available evidence. | `GET /projects/{project_id}`; `GET /rag/projects/{project_id}/history?limit=100`; `GET /ingest/runs?project_id=...&limit=100` |
| `/projects/[projectId]/artifacts` | Artifacts | Typed registry for source objects, model references, configs, reports, plots, notebooks placeholder, and code references. | `GET /projects/{project_id}`; `GET /documents/?project_id=...`; `GET /ingest/runs?project_id=...&limit=100`; `GET /rag/projects/{project_id}/history?limit=100`; `GET /documents/{document_id}/versions` |
| `/projects/[projectId]/test` | Interactive Test Lab | Variant selector for baseline/retrieval/adaptation/final, readiness metrics, latest evidence, embedded executable RAG workspace. | `GET /projects/{project_id}`; `GET /documents/?project_id=...`; `GET /ingest/runs?project_id=...&limit=100`; `GET /rag/projects/{project_id}/history?limit=100`; workspace APIs listed under Sources and Playground |
| `/projects/[projectId]/reproduce` | Reproducibility | Checklist for corpus, pipeline, query evidence, traceability, and reproduction readiness. | `GET /projects/{project_id}`; `GET /documents/?project_id=...`; `GET /ingest/runs?project_id=...&limit=100`; `GET /rag/projects/{project_id}/history?limit=100` |
| `/projects/[projectId]/sources` | Sources workspace | Unified source manager and source inspector; uploads, URL/Drive ingestion, search, retry, delete, versions, traces. | `GET /documents/?project_id=...`; `GET /ingest/runs?project_id=...&limit=30`; `GET /chunkers`; `POST /ingest/file`; `POST /ingest/url`; `POST /ingest/gdrive`; `POST /ingest/runs/{run_id}/retry`; `DELETE /documents/{document_id}`; `GET /documents/{document_id}/versions`; `GET /rag/queries/{query_log_id}` when inspecting traces |
| `/projects/[projectId]/playground` | RAG playground | Streamed answers, provider selection, one-source filter, retrieval options, stop generation, Markdown, citations, history drawer. | `GET /documents/?project_id=...`; `POST /rag/query/stream` through `/api/backend/rag/query/stream`; `GET /rag/queries/{query_log_id}`; `GET /rag/projects/{project_id}/history?limit=100` |
| `/projects/[projectId]/pipelines` | Pipeline info | Pipeline configuration notes, chunker options, and project-scoped run list. | `GET /projects/{project_id}`; `GET /chunkers`; run list APIs from `IngestionRunsPage` |
| `/projects/[projectId]/settings` | Project settings | Rename project, source count warning, delete project. | `GET /projects/{project_id}`; `PATCH /projects/{project_id}`; `DELETE /projects/{project_id}`; `GET /documents/?project_id=...` |
| `/projects/[projectId]/onboarding` | Project onboarding | Guided source selection, chunker selection, ingestion submission, processing status, retry failed stage. | `GET /projects/{project_id}`; `GET /documents/?project_id=...`; `GET /ingest/runs?project_id=...&limit=30`; `GET /chunkers`; `POST /ingest/file`; `POST /ingest/url`; `POST /ingest/gdrive`; `GET /ingest/runs/{run_id}`; `POST /ingest/runs/{run_id}/retry` |
| `/projects/[projectId]/runs/[runId]` | Run detail | Durable ingestion status, stage progress, diagnostics, retry, linked source. | `GET /ingest/runs/{run_id}`; `GET /documents/{document_id}` when linked from detail; `POST /ingest/runs/{run_id}/retry` |
| `/projects/[projectId]/history/[queryId]` | Query detail | Persisted question, answer, provider/model metadata, latency, retrieval trace, citations. | `GET /rag/queries/{query_log_id}`; `GET /projects/{project_id}` |
| `/projects/[projectId]/documents/[documentId]` | Source detail | Document overview, status, versions, linked runs, metadata, upload new version, delete. | `GET /documents/{document_id}`; `GET /projects/{project_id}`; `GET /documents/{document_id}/versions`; `GET /ingest/runs?project_id=...&limit=100`; `POST /ingest/file`; `DELETE /documents/{document_id}` |
| `/projects/[projectId]/observability` | Project observability | Project-scoped observability using the shared observability component. | `GET /projects/{project_id}`; `GET /documents/?project_id=...`; `GET /ingest/runs?project_id=...&limit=100`; `GET /rag/projects/{project_id}/history?limit=100` |
| `/projects/[projectId]/experiments/new` | Planned experiment creation | Project-scoped planned page for future persisted experiment creation. | `GET /projects/{project_id}` through `ProjectPlannedFeaturePage` |
| `/projects/[projectId]/experiments/[experimentId]` | Planned experiment detail | Project-scoped planned page for future experiment detail records. | `GET /projects/{project_id}` through `ProjectPlannedFeaturePage` |

### Planned Or Compatibility Routes

| Route | Behavior | Backend APIs |
| --- | --- | --- |
| `/experiments` | Planned global experiment records page; no fake records. | none |
| `/comparisons` | Planned global comparison page; no fake matrices. | none |
| `/projects/[projectId]` | Redirects to `/projects/[projectId]/overview`. | none |
| `/projects/[projectId]/chat` | Redirects to `/projects/[projectId]/playground`. | none |
| `/projects/[projectId]/history` | Redirects to `/projects/[projectId]/playground?view=history`. | none |
| `/projects/[projectId]/runs` | Redirects to `/projects/[projectId]/pipelines?view=runs`. | none |
| `/projects/[projectId]/documents` | Supported compatibility entry for Sources. | Source workspace APIs |
| `/projects/[projectId]/evaluation` | Redirects to `/projects/[projectId]/results`. | none |

## Feature Matrix

| Feature area | Primary components | Characteristics | Backend/API connections |
| --- | --- | --- | --- |
| Application shell | `AppShell`, `platform/navigation` | Capability- and permission-aware platform/RAGForge navigation, breadcrumbs, switchers, search, and responsive shell. | `GET /auth/me`; `GET /projects/`; `GET /organizations/` |
| Authentication | `(auth)/layout.tsx`, `login/page.tsx`, `register/page.tsx` | Branded auth layout, validated forms, HttpOnly-cookie auth, no client JWT storage. | `POST /api/auth/login`; `POST /api/auth/register`; backend `POST /auth/login`; backend `POST /auth/register` |
| Project/Lab creation | `ProjectForm`, `ProjectsPage`, `LabsDiscoveryPage`, Home create flow | Create named research workspace, choose organization, choose chunker preference in local storage for onboarding. | `POST /projects/`; `GET /organizations/`; `GET /chunkers` |
| Project/Lab management | `ProjectCard`, `LabCard`, `ConfirmDeleteDialog`, settings page | Search, sort, grid/list, rename, delete, destructive confirmation. | `GET /projects/`; `PATCH /projects/{project_id}`; `DELETE /projects/{project_id}` |
| Project shell | `platform/projects/ProjectShell` | Separates platform research links from enabled RAGForge links and hides settings without write permission. | `GET /projects/{project_id}/overview` |
| Overview | `platform/projects/ProjectOverview` | Platform aggregate summary composed with a conditional RAGForge aggregate panel. | `GET /projects/{project_id}/overview`; conditional `GET /rag/projects/{project_id}/overview` |
| Research paper view | `LabResearchPage` | Durable study/question/hypothesis/methodology content plus paper/source evidence. | Research study APIs plus existing project, document, ingestion, and version APIs |
| Experiment evidence | `LabExperimentsPage` | Durable experiments, baseline/retrieval/pipeline/final comparison slots, readiness bars, run/query evidence. | `GET /projects/{project_id}/research/experiments` plus existing evidence APIs |
| Public publications | `PublicationsPage`, `PublicationDetailPage` | Unauthenticated rendering of immutable public-safe revision snapshots. | `GET /publications`; `GET /publications/{slug}` |
| Results | `LabResultsPage` | Persisted query counts, latency, cache hits, indexed runs, result plots, findings, evidence links. | `GET /projects/{project_id}`; `GET /rag/projects/{project_id}/history?limit=100`; `GET /ingest/runs?project_id=...&limit=100` |
| Artifacts | `LabArtifactsPage` | Datasets from documents, model/config references from versions and query history, report links, plot summary, code references. | `GET /projects/{project_id}`; `GET /documents/?project_id=...`; `GET /documents/{document_id}/versions`; `GET /ingest/runs?project_id=...&limit=100`; `GET /rag/projects/{project_id}/history?limit=100` |
| Test Lab | `LabTestPage`, `WorkspaceEntry`, `KnowledgeWorkspace` | Interactive testing of current RAG system, variant readiness selector, latest evidence, embedded workspace. | Lab evidence APIs plus workspace APIs: documents, runs, chunkers, ingestion, streamed RAG query, query trace/history |
| Reproduce | `LabReproducePage` | Reproducibility checklist from real corpus, run, query, trace, and artifact evidence. | `GET /projects/{project_id}`; `GET /documents/?project_id=...`; `GET /ingest/runs?project_id=...&limit=100`; `GET /rag/projects/{project_id}/history?limit=100` |
| Sources | `KnowledgeWorkspace`, `DocumentPanel`, `SourceInspector`, `DocumentDetail` | File/URL/Drive ingestion, source list, status filters, retry, delete, versions, metadata, source-specific trace inspection. | `GET /documents/?project_id=...`; `GET /documents/{document_id}`; `GET /documents/{document_id}/versions`; `DELETE /documents/{document_id}`; `GET /chunkers`; `POST /ingest/file`; `POST /ingest/url`; `POST /ingest/gdrive`; `GET /ingest/runs?project_id=...`; `POST /ingest/runs/{run_id}/retry` |
| Pipelines and runs | `ProjectPipelinesPage`, `IngestionRunsPage`, `IngestionRunDetail`, `IngestionPipeline`, `useIngestionStream` | Run list, filters, stage progress, embedding progress, diagnostics, retry, SSE recovery/poll fallback. | `GET /chunkers`; `GET /ingest/runs?project_id=...`; `GET /ingest/runs/{run_id}`; `GET /ingest/runs/{run_id}/events` through `EventSource`; `POST /ingest/runs/{run_id}/retry`; `GET /documents/?project_id=...` |
| Playground | `AssistantPanel`, `HistoryDrawer`, `RetrievalTrace`, `QueryHistoryPage`, `QueryDetail` | Provider selection, streamed answer generation, stop, markdown answer, execution activity, citations, trace restore, history search/filter. | `POST /rag/query/stream`; `GET /rag/queries/{query_log_id}`; `GET /rag/projects/{project_id}/history?limit=100`; `GET /documents/?project_id=...` |
| Observability | `ObservabilityDashboard` | Cross-project or project-scoped health, failures, query/runs windows, cache and latency evidence. | `GET /projects/`; `GET /projects/{project_id}`; `GET /documents/?project_id=...`; `GET /ingest/runs?project_id=...&limit=100`; `GET /rag/projects/{project_id}/history?limit=100` |
| Organization | `organization/page.tsx` | Organization CRUD and active organization context display. | `GET /organizations/`; `POST /organizations/`; `PATCH /organizations/{organization_id}`; `DELETE /organizations/{organization_id}`; `GET /auth/me` |
| Profile | `settings/profile/page.tsx` | User profile, email/full-name edits, organization assignment, optional password update. | `GET /auth/me`; `PATCH /auth/me`; `GET /organizations/` |
| Shared states and polish | `LoadingState`, `EmptyState`, `ErrorState`, `globals.css` | Accessible loading skeletons, empty/error panels, reduced-motion support, skip navigation, consistent focus styles. | none |

## API Endpoint Reference

All browser calls to backend business APIs go through the same-origin proxy:

```text
apiFetch("/projects/")
  -> /api/backend/projects/
  -> BACKEND_URL/projects/
```

### Auth

| API | Used by | Notes |
| --- | --- | --- |
| `POST /auth/login` | `/api/auth/login` route handler | Backend returns access token; frontend stores it as HttpOnly cookie. |
| `POST /auth/register` | `/api/auth/register` route handler | Registration proxy. |
| `GET /auth/me` | App shell, organization, profile | Current user and active organization. |
| `PATCH /auth/me` | App shell, profile | Organization switch, profile edits, optional password update. |

### Projects And Organizations

| API | Used by | Notes |
| --- | --- | --- |
| `GET /projects/` | Home, Labs, Projects, Observability, AppShell, overview hooks | Project list. |
| `GET /projects/overview` | Home, Labs, Projects, global RAG pages | Accessible projects, resolved permissions, and platform aggregate counts in constant query count. |
| `GET /projects/{project_id}/overview` | Project shell and overview | Authorized project, permissions, and platform-owned counts. |
| `POST /projects/` | Home, Labs, Projects | Create project/Lab. |
| `GET /projects/{project_id}` | Lab shell, overview, research, settings, pipelines, query detail, observability | Project detail. |
| `PATCH /projects/{project_id}` | Labs, Projects, settings | Rename/update project. |
| `DELETE /projects/{project_id}` | Labs, Projects, settings | Delete project. |
| `GET /organizations/` | AppShell, create dialogs, organization, profile | Organization list. |
| `POST /organizations/` | Organization page | Create organization. |
| `PATCH /organizations/{organization_id}` | Organization page | Rename organization. |
| `DELETE /organizations/{organization_id}` | Organization page | Delete organization. |

### Research And Publication

| API | Used by | Notes |
| --- | --- | --- |
| `GET /projects/{project_id}/research/studies` | `LabResearchPage` | Authorized project study index. |
| `GET /projects/{project_id}/research/studies/{study_id}` | `LabResearchPage` | Full durable hierarchy for the selected study. |
| `GET /projects/{project_id}/research/experiments` | `LabExperimentsPage` | Authorized durable experiment index. |
| `GET /rag/workspace/overview` | Global RAGForge pages | Bounded documents, run summaries, history, and per-project readiness for all accessible enabled projects. |
| `GET /rag/projects/{project_id}/overview` | Project overview | Bounded RAGForge readiness, recent runs, primary source, and latest query. |
| `GET /publications` | `PublicationsPage` | Unauthenticated current public revisions only. |
| `GET /publications/{slug}` | `PublicationDetailPage` | Unauthenticated immutable public-safe snapshot. |

### Sources, Versions, And Ingestion

| API | Used by | Notes |
| --- | --- | --- |
| `GET /documents/?project_id={project_id}` | Most Lab pages, workspace, projects/labs stats, observability, runs | Project source list. |
| `GET /documents/{document_id}` | Document detail, run detail links | Source detail. |
| `GET /documents/{document_id}/versions` | Research page, artifacts page, source inspector, document detail | Immutable document versions and parser/chunker/embedding metadata. |
| `DELETE /documents/{document_id}` | Workspace source panel, document detail | Delete logical source. |
| `GET /chunkers` | Create dialogs, onboarding, documents workspace, pipelines | Available chunking configurations. |
| `POST /ingest/file` | Onboarding, sources workspace, document version upload | Multipart file upload and ingestion run creation. |
| `POST /ingest/url` | Onboarding, sources workspace | URL ingestion. |
| `POST /ingest/gdrive` | Onboarding, sources workspace | Google Drive ingestion with file ID and token. |
| `GET /ingest/runs?project_id={project_id}&limit={n}` | Lab pages, source workspace, projects/labs stats, runs, observability | Project-scoped ingestion runs. |
| `GET /ingest/runs/{run_id}` | Run detail, onboarding status, ingestion stream recovery | Durable run detail. |
| `GET /ingest/runs/{run_id}/events` | `useIngestionStream` | Server-sent run status events via same-origin backend proxy. |
| `POST /ingest/runs/{run_id}/retry` | Source workspace, onboarding, run detail, pipeline component | Retry failed run from durable artifacts. |

### RAG And Retrieval Evidence

| API | Used by | Notes |
| --- | --- | --- |
| `POST /rag/query/stream` | `AssistantPanel`, legacy `ChatWorkspace` | SSE answer generation. Request includes `question`, `project_id`, `provider`, optional `document_id`, `use_parent_context`, and `include_context`. |
| `GET /rag/projects/{project_id}/history?limit=100` | Lab pages, history drawer, query history, observability | Persisted query records for a project. |
| `GET /rag/queries/{query_log_id}` | Query detail, history restore, assistant trace load, source inspector traces | Persisted answer plus retrieval trace/citations. |

## Key Component Responsibilities

| Component | Responsibility |
| --- | --- |
| `AppShell` | Authenticated application chrome, responsive sidebar, top navigation, organization/project switchers, command palette, skip navigation. |
| `LabShell` | Common project Lab header and tabs. |
| `LabsDiscoveryPage` | Project-backed Lab discovery and domain filtering. |
| `LabResearchPage` | Research question, methodology, paper/source viewer, document metadata. |
| `LabExperimentsPage` | Evidence-backed configuration comparison and experiment readiness. |
| `LabResultsPage` | Query-history result evidence, plots, findings, comparison summary. |
| `LabArtifactsPage` | Artifact registry assembled from current source/version/run/query evidence. |
| `LabTestPage` | Interactive Test Lab wrapper and variant readiness layer. |
| `LabReproducePage` | Reproducibility checklist and run/query/source readiness. |
| `ProjectOverview` | Project readiness and next action. |
| `ProjectPipelinesPage` | Pipeline description and chunker configuration context. |
| `IngestionRunsPage` | Global or project-scoped ingestion run index. |
| `IngestionRunDetail` | Durable run detail and retry path. |
| `WorkspaceEntry` | Loads source state before mounting the unified workspace. |
| `KnowledgeWorkspace` | Unified Sources/Playground layout, selection state, upload/delete/retry mutations. |
| `DocumentPanel` | Source list, filters, upload actions, status cards. |
| `AssistantPanel` | Streaming RAG interaction, activity trace, citations, history restore. |
| `SourceInspector` | Source content, versions, retrieval trace, metadata. |
| `QueryHistoryPage` | Query history search and outcome filtering. |
| `QueryDetail` | Persisted answer and retrieval trace detail. |
| `DocumentDetail` | Source metadata, versions, runs, upload new version, delete. |
| `LoadingState` | Accessible skeleton loading region. |
| `EmptyState` | Consistent empty-state panel. |
| `ErrorState` | Consistent error-state panel with retry affordance. |
| `ConfirmDeleteDialog` | Typed destructive confirmation. |
| `PlannedFeaturePage` | Truthful placeholder for backend-dependent surfaces. |

Legacy components still present:

```text
ChatWorkspace
DocumentsWorkspace
HistoryWorkspace
IngestionCard
DocumentList
ProjectPlannedFeaturePage
```

They are retained for compatibility and tests. Remove them only after route and
test coverage confirms they are no longer referenced.

## Shared Data Hooks And Utilities

| File | Purpose | API behavior |
| --- | --- | --- |
| `lib/api.ts` | `apiFetch` and `authFetch` wrappers | `apiFetch` prefixes `/api/backend`; `authFetch` prefixes `/api/auth`; both normalize backend error payloads. |
| `lib/server-auth.ts` | Server-side auth constants | Defines `AUTH_COOKIE = "ragforge_session"` and `backendUrl()`. |
| `lib/sse.ts` | SSE parsing helpers | Consumes streamed backend events for RAG answers. |
| `hooks/use-workspace-overview.ts` | Cross-project overview composition | Joins platform and RAGForge aggregates in two bounded requests. |
| `hooks/use-ingestion-stream.ts` | Run status streaming | Uses `EventSource` to `/api/backend/ingest/runs/{run_id}/events`, then recovers with `GET /ingest/runs/{run_id}`. |

## Visual System

Core tokens live in `frontend/src/app/globals.css`.

Current identity:

- dark graphite background: `--background: #090B10`
- dark sidebar: `--sidebar: #0C0F15`
- primary panels: `--surface-1: #11151D`
- raised panels: `--surface-2: #161B25`
- hover panels: `--surface-hover: #1A202B`
- primary text: `--text-primary: #F3F5F7`
- secondary text: `--text-secondary: #A6AFBD`
- muted text: `--text-muted: #717B89`
- CCSR blue: `--accent: #6C8CFF`
- research violet: `--research-violet: #A78BFA`
- semantic success/warning/danger/info tokens for status only

Design characteristics:

- restrained dark research UI
- dense but readable operational layouts
- cards with small radii, not nested decorative cards
- icons from `lucide-react`
- color plus text/icon status communication
- accessible skip navigation and focus states
- reduced-motion cleanup for users who prefer less animation
- loading, empty, and error states are centralized in shared primitives

## Backend-Dependent Blockers

The frontend intentionally labels these as planned or unavailable until backend
contracts exist:

- persisted experiment run detail APIs
- model-only baseline execution endpoint
- fine-tuned/QLoRA adapter execution endpoint
- dataset registry and versioning
- model registry and versioning
- notebook registry
- evaluation metrics dashboard
- evaluator score contracts
- formal comparison matrices
- cost/resource metrics
- authenticated publication authoring UI
- reproducibility manifest export/import
- knowledge graph or paper relationship browser
- persisted project descriptions

## Current Modularity Boundary

The App Router files remain thin. `src/platform/navigation/` owns shared
capability and permission filtering, while `src/platform/projects/` owns the
project shell and platform/RAG aggregate overview composition. Historical
`LabShell` and `ProjectOverview` imports remain compatibility exports.

`src/modules/ragforge/` owns the project capability gate. Existing source,
playground, pipeline, test, and observability URLs remain stable and mount only
for RAGForge-enabled projects. Workspace-wide RAG screens use one bounded
module aggregate alongside one platform aggregate rather than N+1 requests.

## Validation Expectations

For frontend changes, run from `frontend/`:

```bash
npm run lint
npm run typecheck
npm run test
npm run build
```

Run Playwright E2E where the local environment supports it:

```bash
npm run test:e2e
```
