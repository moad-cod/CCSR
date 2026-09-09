# RAGForge frontend module

This slice owns capability-specific navigation gates and screens for sources,
ingestion pipelines, retrieval playgrounds, query history, and RAG
observability. Platform project, research, experiment, artifact, publication,
and permission behavior must not depend on this module.

Canonical screen entrypoints are `workspace-entry.tsx`,
`project-pipelines-page.tsx`, `ingestion-runs-page.tsx`,
`query-history-page.tsx`, and `observability-dashboard.tsx`. Their former
`components/` paths are compatibility exports.

Existing route URLs remain compatibility entry points. Route composition must
pass through `RAGForgeCapabilityGate` before mounting a project-scoped RAG
screen. Workspace-wide RAG reads use the bounded aggregate contract rather than
issuing one request per accessible project.
