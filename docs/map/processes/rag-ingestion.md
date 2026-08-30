# RAG ingestion

**Status:** Implemented, with one durable batch path and older synchronous paths.

**Authoritative sources:** [`ingest.py`](../../../backend/app/modules/ragforge/api/ingest.py),
[`ingestion_workflow.py`](../../../backend/jobs/ingestion_workflow.py),
[`pipeline_artifacts.py`](../../../backend/app/modules/ragforge/services/pipeline_artifacts.py),
and [`chunk_indexing.py`](../../../backend/app/modules/ragforge/services/chunk_indexing.py).

**Current movement**

```text
file upload -> MinIO Bronze + PostgreSQL document/version/run
-> Airflow or Celery -> Silver chunks -> Gold embeddings
-> Qdrant + PostgreSQL chunk lineage -> indexed status and SSE
```

**Hits**

- Parsing, chunker planning, embeddings, artifacts, deterministic indexing,
  retries, status transitions, and progress.

**Does not hit**

- Generic projects without RAG. URL, Drive, and multimodal paths do not have the
  same complete durable lineage today.
