# PostgreSQL

**Status:** Implemented and authoritative for durable control-plane state.

**Authoritative sources:** [`db.py`](../../../backend/app/core/db.py),
[`models/`](../../../backend/app/models/), and
[`alembic/versions/`](../../../backend/alembic/versions/).

**Hits**

- Accounts, organizations, memberships, projects, research hierarchies,
  publication revisions, workflows, runs, quotas, artifact metadata, audit
  events, document lineage, ingestion status, chunks, embeddings, queries, and
  retrieval logs.

**Does not hit**

- Vector bodies, large artifacts, Redis replay/cache entries, or Airflow/Celery
  native state.
