# MinIO

**Status:** Implemented for RAG ingestion artifacts.

**Authoritative sources:**
[`bronze_storage.py`](../../../backend/app/modules/ragforge/services/bronze_storage.py),
[`pipeline_artifacts.py`](../../../backend/app/modules/ragforge/services/pipeline_artifacts.py),
and [`docker-compose.yml`](../../../docker-compose.yml).

**Hits**

- Raw Bronze uploads, chunked Silver Parquet, embedded Gold Parquet, retryable
  version-scoped object paths whose metadata is registered as shared artifacts.

**Does not hit**

- Durable artifact metadata, run state, or vector search.
