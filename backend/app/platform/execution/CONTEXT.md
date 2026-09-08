# Platform execution context

This package owns CCSR workflow definitions, generic runs, the execution
gateway, and infrastructure adapter contracts.

- `model.py` and `repository.py` make PostgreSQL authoritative for workflow
  versions, validated input snapshots, engine IDs, status, outputs, and errors.
- `registry.py` contains only server-approved definitions, adapters, and module
  handlers. Browser input must never select an engine or handler reference.
- `gateway.py` checks capability enablement, validates input with the registered
  Pydantic contract, creates a durable run, reserves quota, and dispatches it
  after commit.
- `adapters/` owns engine-specific mechanics. Airflow uses its REST API; Celery
  invokes only a server-registered module dispatcher.
- `api.py` exposes authorization-protected read endpoints for workflows and
  runs. It does not expose arbitrary execution submission.

Product-specific stage state stays in product modules. RAGForge links its
`IngestionRun` to a generic run and synchronizes broad statuses while retaining
the old `airflow_dag_run_id` response field during compatibility.

Generic terminal updates store only categorized safe errors and settle the
associated quota reservation. Detailed internal failures may remain in
module-owned operational state where existing compatibility requires them.
Generic runs may optionally reference a durable experiment after the gateway
verifies that the experiment belongs to the same project.
