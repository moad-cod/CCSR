# Retrieval log

**Status:** Implemented; RAGForge trace.

**Authoritative sources:**
[`retrieval_log.py`](../../../backend/app/modules/ragforge/models/retrieval_log.py),
[`retrieval_logs.py`](../../../backend/app/modules/ragforge/repositories/retrieval_logs.py), and
[`query_observability.py`](../../../backend/app/modules/ragforge/services/query_observability.py).

**Hits**

- Ranked evidence, Qdrant/rerank scores, strategy, answer use, optional chunk
  lineage, citations, and query observability.

**Does not hit**

- Retrieval vector storage or generic experiment metrics.
