# Ingestion run

**Status:** Implemented; RAGForge-specific run.

**Authoritative sources:**
[`ingestion_run.py`](../../../backend/app/models/ingestion_run.py),
[`ingestion_runs.py`](../../../backend/app/repositories/ingestion_runs.py), and
[`ingest.py`](../../../backend/app/api/ingest.py).

**Hits**

- One document-version ingestion attempt, durable status, retry, progress,
  chunks, and orchestrator traceability.
- The current `airflow_dag_run_id` field also stores Celery workflow IDs.

**Does not hit**

- Generic workflow inputs/outputs, quotas, or non-RAG executions.
