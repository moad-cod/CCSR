# Airflow execution

**Status:** Implemented for RAG file ingestion.

**Authoritative sources:** [`airflow.py`](../../../backend/app/services/airflow.py),
[`ragforge_ingestion.py`](../../../backend/airflow/dags/ragforge_ingestion.py),
[`ingestion_execution.py`](../../../backend/jobs/ingestion_execution.py), and
[`ragforge_control_plane.py`](../../../backend/airflow/plugins/ragforge_control_plane.py).

**Current movement**

```text
generic run -> Airflow adapter -> ragforge_ingestion DAG
-> configured Bronze/Silver/Gold/Qdrant jobs
-> authenticated internal FastAPI callbacks
```

**Hits**

- Long ingestion stages, external DAG ID, durable status callbacks, MinIO
  artifacts, Qdrant indexing, and progress events.

**Does not hit**

- Direct PostgreSQL writes by Airflow or changes to module-owned ingestion stages.
