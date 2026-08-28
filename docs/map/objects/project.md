# Project

**Status:** Implemented, but currently RAG-specific.

**Authoritative sources:** [`project.py`](../../../backend/app/models/project.py),
[`projects.py`](../../../backend/app/api/projects.py), and
[`projects repository`](../../../backend/app/repositories/projects.py).

**Hits**

- Creator ownership, optional organization association, documents, ingestion,
  chunks, embeddings, query history, and Qdrant collection lifecycle.
- Most project-scoped frontend routes and types.

**Does not hit**

- Capabilities, description, visibility, publication state, research studies,
  generic workflows, or generic runs; these are not modeled yet.
