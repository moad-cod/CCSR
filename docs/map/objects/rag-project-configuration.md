# RAG project configuration

**Status:** Implemented as a dedicated RAG-owned project configuration.

**Authoritative current sources:**
[`project_config.py`](../../../backend/app/modules/ragforge/models/project_config.py),
[`project_configs.py`](../../../backend/app/modules/ragforge/repositories/project_configs.py),
[`projects.py`](../../../backend/app/api/projects.py), and migration
[`20260902_0006`](../../../backend/alembic/versions/20260902_0006_add_project_capabilities_and_rag_configs.py).

**Hits**

- Qdrant collection identity, embedding and sparse models, default chunker,
  and retrieval configuration.
- RAG API authorization requires both this configuration and the durable
  `ragforge` capability association.

**Does not hit**

- Generic project identity, visibility, publication, or non-RAG capabilities.
- The temporary legacy `Project.qdrant_collection` compatibility column.
