# CCSR Frontend Map

This document describes the frontend as it exists after the first CCSR
frontend migration. It documents implemented behavior only. Planned CCSR
research features are called out as backend blockers rather than presented as
working product surfaces.

## Product Model

CCSR, Canonical Computer Science Research, is presented in the frontend as a
local-first research engineering workspace.

The current mature workflow remains Retrieval/RAG:

```text
Project
  -> Sources
  -> Pipeline runs
  -> Playground query
  -> Evidence and retrieval trace
  -> Persisted history
```

The frontend preserves the existing implemented RAG control-plane behavior:

- Authentication through Next.js auth route handlers and an HttpOnly session
  cookie.
- Project CRUD.
- Source/document upload and management.
- URL and Google Drive ingestion.
- Durable file ingestion runs.
- Document versions and source metadata.
- Ingestion SSE recovery.
- Streamed `/rag/query/stream` answers.
- Gemini/Groq provider selection.
- Citations and retrieval traces.
- Playground history.
- Observability, organization, and profile settings.

The frontend does not implement first-class experiment records, dataset
registry, model registry, research notes, findings, reproducibility manifests,
or cross-domain NLP/CV experiment engines.

## Stack

| Area | Current implementation |
| --- | --- |
| Framework | Next.js App Router, React, TypeScript |
| Styling | Tailwind CSS v4 through `globals.css` with black, charcoal, and warm-cream CCSR tokens |
| Data fetching | TanStack Query |
| Forms | React Hook Form and Zod where forms need schema validation |
| Notifications | `sonner` toast system |
| Icons | `lucide-react` |
| Markdown | `react-markdown` with `remark-gfm` |
| Tests | Vitest, Testing Library, Playwright config |
| Auth | HttpOnly `ragforge_session` compatibility cookie set by Next.js route handlers |

The browser does not read or store the backend JWT directly.

```text
Browser UI
  -> /api/auth/login | /api/auth/register | /api/auth/logout
  -> HttpOnly ragforge_session cookie
  -> /api/backend/[...path] same-origin proxy
  -> FastAPI backend with Authorization: Bearer <token>
```

## Information Architecture

### Global Navigation

The global sidebar is workflow-oriented:

```text
Workspace
  Home
  Labs
  Projects

Research
  Experiments
  Comparisons

Monitor
  Runs
  Observability

Manage
  Organization
  Settings
```

`Experiments` and `Comparisons` route to planned-feature pages. They do not
show fake experiment records, fake metrics, or comparison results.

Global `Documents` and global `Query History` are not primary navigation
items. Source management and query history belong inside project workflows.

### Lab Navigation

Inside a project-backed Lab, the sidebar switches to Lab context:

```text
Back to all labs / projects

<Project Name>
  Overview
  Research
  Experiments
  Results
  Artifacts
  Test
  Reproduce
```

The common Lab shell also exposes the same sequence as a compact tab row inside
individual Lab pages. `Experiments`, `Results`, `Artifacts`, and `Reproduce`
use real source, ingestion-run, query-history, and collection evidence that
already exists in the backend. Unsupported baseline, evaluator, cost, and
generic experiment-record slots are labeled as unavailable or planned rather
than rendered as fake metrics.

## Routes

### Implemented Routes

| Route | Purpose |
| --- | --- |
| `/` | Redirects to `/projects` |
| `/login` | CCSR sign-in page |
| `/register` | CCSR registration page |
| `/home` | Cross-project home and next-work guidance |
| `/labs` | Premium lab discovery across implemented project workspaces, with domain filters and real readiness data |
| `/projects` | Project list, create, rename, delete |
| `/projects/[projectId]/overview` | Real project readiness, next action, recent runs, latest query |
| `/projects/[projectId]/research` | Lab research corpus and methodology evidence from real sources and runs |
| `/projects/[projectId]/experiments` | Evidence-backed experiment configurations, comparisons, readiness plots, and current findings |
| `/projects/[projectId]/results` | Real playground result evidence, comparison summary, metrics, plots, and findings |
| `/projects/[projectId]/artifacts` | Typed artifact registry for datasets, model references, configs, reports, plots, and code references backed by current endpoints |
| `/projects/[projectId]/test` | Interactive Test Lab with live readiness, variant comparison slots, and the implemented RAG playground |
| `/projects/[projectId]/reproduce` | Reproducibility checklist from current source, run, and query evidence |
| `/projects/[projectId]/sources` | Unified source manager and playground workspace entry |
| `/projects/[projectId]/playground` | Unified playground workspace entry |
| `/projects/[projectId]/pipelines` | Pipeline configuration notes and project run list |
| `/projects/[projectId]/settings` | Lab/project settings and destructive delete action |
| `/projects/[projectId]/runs/[runId]` | Run detail with durable ingestion status |
| `/projects/[projectId]/history/[queryId]` | Persisted query detail and retrieval evidence |
| `/runs` | Cross-project ingestion run index |
| `/observability` | Cross-project observability from real documents, runs, and queries |
| `/organization` | Organization list, create, rename, delete |
| `/settings/profile` | Current-user profile and organization context |

### Compatibility Routes

| Legacy route | Behavior |
| --- | --- |
| `/projects/[projectId]` | Redirects to `/projects/[projectId]/overview` |
| `/projects/[projectId]/chat` | Redirects to `/projects/[projectId]/playground` |
| `/projects/[projectId]/history` | Redirects to `/projects/[projectId]/playground?view=history` |
| `/projects/[projectId]/runs` | Redirects to `/projects/[projectId]/pipelines?view=runs` |
| `/projects/[projectId]/documents` | Supported as workspace compatibility for Sources |
| `/projects/[projectId]/evaluation` | Redirects to `/projects/[projectId]/results` |

## Main Frontend Directories

```text
frontend/
  src/
    app/
      (auth)/
      (dashboard)/
      api/
      globals.css
      layout.tsx
      page.tsx
    components/
      workspace/
      onboarding/
      ui/
    hooks/
    lib/
    test/
```

## Key Components

| Component | Role |
| --- | --- |
| `AppShell` | Authenticated shell, sidebar, top bar, project switcher, command palette |
| `LabShell` | Common Lab identity header and tabs: Overview, Research, Experiments, Results, Artifacts, Test, Reproduce |
| `LabResearchPage` | Project-backed research corpus and methodology evidence |
| `LabExperimentsPage` | Evidence-backed experiment configuration, comparison matrix, readiness plot, and experiment evidence |
| `LabResultsPage` | Real query-history result evidence, comparison summary, plots, and findings |
| `LabArtifactsPage` | Typed artifact registry for datasets, model references, configs, reports, plots, notebooks, and code references |
| `LabReproducePage` | Reproducibility readiness checklist |
| `LabTestPage` | Interactive Test Lab for current RAG execution, variant readiness, recent evidence, and persisted playground testing |
| `ProjectOverview` | Project readiness and next meaningful action using real data |
| `ProjectPipelinesPage` | Project pipeline information plus reusable run index |
| `IngestionRunsPage` | Global or project-scoped durable run list |
| `WorkspaceEntry` | Loads project state and mounts the unified workspace |
| `KnowledgeWorkspace` | Unified Sources/Playground layout with source panel and inspector |
| `DocumentPanel` | Source upload, URL/Drive ingestion, search, selection, retry, delete |
| `AssistantPanel` | Streamed playground query flow, execution trace, citations, history drawer |
| `SourceInspector` | Supported source tabs: Content, Versions, Retrieval Trace, Metadata |
| `QueryHistoryPage` | Durable playground history list |
| `QueryDetail` | Persisted answer and retrieval trace detail |
| `DocumentDetail` | Source metadata, versions, runs, and delete/version actions |
| `ConfirmDeleteDialog` | Shared typed destructive confirmation |
| `PlannedFeaturePage` | Truthful placeholder for backend-dependent research surfaces |

`ChatWorkspace`, `DocumentsWorkspace`, and `HistoryWorkspace` remain in the
codebase as legacy components. They are not primary navigation destinations.
They should be removed only after route and test coverage confirms they are no
longer needed.

## Current UX Surfaces

### Home

`/home` answers "what should I work on next?" It uses real project, document,
run, and query data. Empty states guide the user toward:

```text
Create project
  -> Add sources
  -> Process/index sources
  -> Test retrieval in Playground
  -> Inspect evidence
```

The page avoids fake analytics and does not show unsupported experiment
metrics.

### Projects

`/projects` shows projects as research workspaces. Cards link primarily to the
project overview. Rename and delete are kept in an overflow menu. Counts are
loaded from current document and ingestion endpoints.

### Labs

`/labs` is the premium discovery surface for project-backed research labs. It
groups existing project workspaces by frontend-inferred research domains such
as Retrieval/RAG, NLP, Computer Vision, Machine Learning, Multimodal, AI
Systems, and Mathematics. Lab cards use real project, source, and ingestion run
data; they do not invent unsupported experiment records or synthetic metrics.

### Sources

The Sources workflow reuses the existing document/source implementation and
preserves:

- file upload
- URL ingestion
- Google Drive ingestion
- chunker selection
- source search
- source status
- retry failed ingestion
- delete source
- document versions
- source metadata

The backend API still uses `documents` route names and document IDs. The UI
uses `Sources` for the product concept.

### Playground

The Playground preserves the implemented RAG query behavior:

- streamed SSE answers
- provider selection for Gemini/Groq
- one-source filter supported by the current backend
- retrieval settings
- stop generation
- Markdown answer rendering
- execution trace
- citations
- answer copy/regenerate actions
- query history drawer
- retrieval trace and source inspection

The Playground is not presented as an autonomous agent.

### Pipelines

Pipelines present durable ingestion execution without exposing Airflow as the
generic product concept. The UI uses:

```text
Pipeline
Run
Orchestrator
```

Airflow/Celery details remain implementation-specific and appear only where the
backend reports them.

### Observability

Observability is based on real documents, ingestion runs, and persisted query
history. Missing metrics are shown as unavailable rather than fabricated.

## Visual System

The active CCSR frontend identity uses:

- black page backgrounds
- charcoal panels and cards
- warm-cream primary actions and active navigation
- green only for semantic success/indexed/healthy states

Core tokens live in `frontend/src/app/globals.css`.

Approximate token intent:

```css
--background: #090909;
--sidebar: #0d0d0d;
--surface: #131313;
--surface-raised: #191919;
--surface-hover: #202020;
--border: #2b2926;
--border-strong: #403c36;
--ink: #f4efe7;
--ink-muted: #b7b0a7;
--ink-faint: #77716a;
--accent: #ebe0d1;
--accent-hover: #fff7ec;
```

Auth pages include a separate subtle atmospheric treatment in
`globals.css`. The main application shell remains calmer and denser.

## Auth Constraints

Do not move backend JWTs into client-readable storage. The frontend must keep:

```text
Next.js route handlers
  -> HttpOnly ragforge_session cookie
  -> same-origin backend proxy
```

The `ragforge_session` name remains for compatibility even though the product
branding is CCSR.

## Backend-Dependent Blockers

These are intentionally not implemented in this frontend milestone:

- first-class experiment records
- experiment run detail pages backed by persisted experiment APIs
- dataset registry and versioning
- model registry and versioning
- evaluation metrics dashboard
- comparison matrices
- cost/resource metrics
- research notes and findings
- reproducibility manifests
- knowledge graph or paper relationship browser
- project descriptions persisted by the backend

Planned pages must remain explicit that backend support is required.

## Validation Expectations

For frontend migration work, run from `frontend/`:

```bash
npm run lint
npm run test
npm run typecheck
npm run build
```

Run Playwright E2E where the local environment supports it:

```bash
npm run test:e2e
```
