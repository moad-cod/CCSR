# Workflow submission

**Status:** Generic submission is planned; RAG ingestion submission exists.

**Authoritative current sources:** [`ingest.py`](../../../backend/app/modules/ragforge/api/ingest.py),
[`ingestion_orchestrator.py`](../../../backend/app/services/ingestion_orchestrator.py),
and [`ingestion_run.py`](../../../backend/app/modules/ragforge/models/ingestion_run.py).

**Current movement**

```text
owned project upload -> validate and land Bronze
-> create RAG ingestion run -> deployment-wide ORCHESTRATOR switch
-> Airflow or Celery
```

**Hits**

- File upload validation, MinIO landing, ingestion state, and engine enqueue.

**Does not hit**

- Versioned workflow definitions, generic runs, quotas, member execution policy,
  or arbitrary workflow inputs.
