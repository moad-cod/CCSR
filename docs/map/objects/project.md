# Project

**Status:** Implemented with durable capability associations; a legacy RAG
collection column remains temporarily.

**Authoritative sources:** [`project.py`](../../../backend/app/models/project.py),
[`projects.py`](../../../backend/app/api/projects.py), and
[`projects repository`](../../../backend/app/repositories/projects.py).

**Hits**

- Personal-project creator ownership, organization-member read access,
  creator/organization-admin write access, documents, ingestion,
  chunks, embeddings, query history, and lifecycle cleanup dispatched through
  the capability registry.
- Durable capability associations and optional one-to-one RAG configuration.
- Most project-scoped frontend routes and types.

**Does not hit**

- Per-project custom roles, description, visibility, publication state, or
  research studies. Generic workflows and runs reference projects without
  adding project-type branching.
