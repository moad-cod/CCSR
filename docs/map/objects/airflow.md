# Airflow

**Status:** Implemented RAG ingestion engine and optional Compose profile.

**Authoritative sources:** [`airflow.py`](../../../backend/app/services/airflow.py),
[`ragforge_ingestion.py`](../../../backend/airflow/dags/ragforge_ingestion.py),
and [`docker-compose.yml`](../../../docker-compose.yml).

**Hits**

- Long, ordered RAG ingestion stages, callbacks through the internal API,
  configured job commands, and Airflow-oriented E2E coverage.

**Does not hit**

- Browser-selected execution engines, generic workflow registration, or direct
  authoritative application state writes.
