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
- Server-resolved read/write/manage permissions in project API payloads and
  bounded platform overview counts.
- Capability- and permission-aware project navigation and project-scoped
  frontend routes.

**Does not hit**

- Per-project custom roles, description, or project-level visibility. Research
  and publication records remain separate platform objects. Generic workflows
  and runs reference projects without adding project-type branching.
