# Frontend source context

The source tree does not yet have platform/module ownership directories.

- Generic candidates include authentication, organization, project registry,
  profile, shared shell, and shared UI primitives.
- RAGForge candidates include sources, documents, ingestion, pipelines,
  playground, RAG history, retrieval traces, citations, and RAG evaluation.
- `components/app-shell.tsx` and `components/labs/lab-shell.tsx` currently
  hard-code project navigation.
- `hooks/use-workspace-overview.ts` requests RAG documents, ingestion runs, and
  query history per project and must not become the generic project contract.
- `lib/types.ts` is a compatibility barrel that should be split only when its
  consumers can migrate safely.

Future route files under `app/` should compose screens from `platform/` or
`modules/ragforge/`. Create those directories only when a real screen or
contract is ready to move.
