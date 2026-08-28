# Celery execution

**Status:** Implemented for RAG file ingestion.

**Authoritative sources:** [`tasks.py`](../../../backend/app/workers/tasks.py),
[`celery_app.py`](../../../backend/app/workers/celery_app.py), and
[`ingestion_workflow.py`](../../../backend/jobs/ingestion_workflow.py).

**Current movement**

```text
ingestion run -> Celery chain -> shared RAG ingestion stages
-> authenticated internal FastAPI callbacks -> durable state/progress
```

**Hits**

- Stage retries, Redis broker/results, Bronze/Silver/Gold processing, Qdrant
  indexing, and failure reporting.

**Does not hit**

- Direct PostgreSQL writes by workers or a generic short-workflow registry.
