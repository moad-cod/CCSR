# Query log

**Status:** Implemented; RAGForge trace.

**Authoritative sources:** [`query_log.py`](../../../backend/app/models/query_log.py),
[`query.py`](../../../backend/app/api/query.py), and
[`query_logs.py`](../../../backend/app/repositories/query_logs.py).

**Hits**

- Question, answer, provider/model, cache state, latency, evaluation scores,
  user/project ownership, and retrieval trace records.

**Does not hit**

- A generic CCSR run, quota reservation, or non-RAG prediction result.
