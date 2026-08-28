# MinIO

**Status:** Implemented for RAG ingestion artifacts.

**Authoritative sources:**
[`bronze_storage.py`](../../../backend/app/services/bronze_storage.py),
[`pipeline_artifacts.py`](../../../backend/app/services/pipeline_artifacts.py),
and [`docker-compose.yml`](../../../docker-compose.yml).

**Hits**

- Raw Bronze uploads, chunked Silver Parquet, embedded Gold Parquet, retryable
  version-scoped object paths, and future shared large artifacts.

**Does not hit**

- Durable artifact metadata, access policy, run state, or vector search.
