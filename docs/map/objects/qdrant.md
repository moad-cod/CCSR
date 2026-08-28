# Qdrant

**Status:** Implemented for RAG capabilities.

**Authoritative sources:** [`indexer.py`](../../../backend/app/services/indexer.py),
[`chunk_indexing.py`](../../../backend/app/services/chunk_indexing.py),
[`retrieval/`](../../../backend/app/services/retrieval/), and
[`docker-compose.yml`](../../../docker-compose.yml).

**Hits**

- Dense/sparse vectors, RAG payload filters, deterministic point lineage,
  multimodal collections, and retrieval.

**Does not hit**

- Generic projects without RAG, durable run authority, account permissions, or
  artifact metadata.
