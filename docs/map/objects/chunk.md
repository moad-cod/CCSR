# Chunk

**Status:** Implemented; RAGForge ownership.

**Authoritative sources:** [`chunk.py`](../../../backend/app/modules/ragforge/models/chunk.py),
[`chunk_indexing.py`](../../../backend/app/modules/ragforge/services/chunk_indexing.py), and
[`chunks.py`](../../../backend/app/modules/ragforge/repositories/chunks.py).

**Hits**

- Document/version/run lineage, deterministic Qdrant point identity, text
  metadata, retrieval logs, and retryable reindexing.

**Does not hit**

- Vector payload durability in PostgreSQL; vectors remain in Qdrant.
