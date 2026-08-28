# RAG project configuration

**Status:** Embedded in `Project`; dedicated model planned.

**Authoritative current sources:** [`project.py`](../../../backend/app/models/project.py),
[`projects.py`](../../../backend/app/api/projects.py), and
[`config.py`](../../../backend/app/core/config.py).

**Hits**

- Current Qdrant collection identity and future RAG defaults such as embedding,
  sparse model, chunker, and retrieval configuration.

**Does not hit**

- Generic project identity, visibility, publication, or non-RAG capabilities.
