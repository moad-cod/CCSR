# Workflow submission

**Status:** Implemented for registered RAG ingestion; arbitrary submission is not exposed.

**Authoritative sources:** [`gateway.py`](../../../backend/app/platform/execution/gateway.py),
[`workflows.py`](../../../backend/app/modules/ragforge/workflows.py), and
[`ingestion_orchestrator.py`](../../../backend/app/services/ingestion_orchestrator.py).

**Current movement**

```text
authorized project upload -> validate and land Bronze
-> create generic run + linked RAG ingestion run
-> validate registered input/capability -> registered engine adapter
-> existing Airflow DAG or Celery chain
```

**Hits**

- File upload validation, MinIO landing, versioned definition/input snapshot,
  durable generic and RAG state, and registered engine enqueue.

**Does not hit**

- Quota reservation/finalization, arbitrary workflow inputs, or browser-selected
  engines and handlers.
