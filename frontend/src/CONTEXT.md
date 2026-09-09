# Frontend source context

The source tree separates platform navigation/project composition from the
RAGForge capability boundary. Historical component exports remain where routes
or extensions may still import them.

- Generic candidates include authentication, organization, project registry,
  profile, shared shell, and shared UI primitives.
- RAGForge candidates include sources, documents, ingestion, pipelines,
  playground, RAG history, retrieval traces, citations, and RAG evaluation.
- `platform/navigation/navigation.ts` is the shared capability- and
  permission-aware navigation policy.
- `platform/projects/` owns project shell and aggregate overview composition;
  former component paths are compatibility exports.
- `modules/ragforge/` owns the project capability gate. Current RAG screen
  components can migrate behind that boundary incrementally.
- `hooks/use-workspace-overview.ts` joins the platform and RAGForge aggregate
  contracts in two bounded requests rather than per-project requests.
- `lib/types.ts` is a compatibility barrel that should be split only when its
  consumers can migrate safely.
- `platform/publication/` is the first platform-owned frontend slice. It renders
  only immutable visitor snapshots; the backend proxy allowlist remains GET-only
  and publication-specific.

Future route files under `app/` should compose screens from `platform/` or
`modules/ragforge/`. Create those directories only when a real screen or
contract is ready to move.
