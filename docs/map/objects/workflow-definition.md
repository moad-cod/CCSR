# Workflow definition

**Status:** Planned; only a deployment-wide ingestion orchestrator switch exists.

**Verification sources:**
[`ingestion_orchestrator.py`](../../../backend/app/services/ingestion_orchestrator.py),
[`config.py`](../../../backend/app/core/config.py), and
[`models/__init__.py`](../../../backend/app/models/__init__.py).

**Hits**

- Future approved input/output schemas, workflow version, engine selection,
  runtime policy, module handler, and produced artifact types.

**Does not hit**

- The browser or arbitrary user-supplied commands. The current browser does not
  define Airflow DAGs or Celery tasks.
