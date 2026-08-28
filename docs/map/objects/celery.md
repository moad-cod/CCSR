# Celery

**Status:** Implemented RAG ingestion engine and optional Compose profile.

**Authoritative sources:**
[`celery_app.py`](../../../backend/app/workers/celery_app.py),
[`tasks.py`](../../../backend/app/workers/tasks.py), and
[`docker-compose.yml`](../../../docker-compose.yml).

**Hits**

- The shared RAG ingestion stage chain, retries, Redis broker/results, benchmark
  coverage, and focused integration tests.

**Does not hit**

- A generic short-workflow registry or a dedicated generic run model. Its
  workflow ID currently occupies the Airflow-named ingestion field.
