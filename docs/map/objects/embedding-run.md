# Embedding run

**Status:** Implemented for durable RAG file ingestion.

**Authoritative sources:**
[`embedding_run.py`](../../../backend/app/models/embedding_run.py),
[`embedding_runs.py`](../../../backend/app/repositories/embedding_runs.py), and
[`internal_pipeline.py`](../../../backend/app/api/internal_pipeline.py).

**Hits**

- Document-version/model identity, embedding progress, model loading, retries,
  counts, timings, and ingestion observability.

**Does not hit**

- Generic model training/evaluation runs or synchronous URL/Drive/multimodal
  ingestion lineage.
