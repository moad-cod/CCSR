# Generic run

**Status:** Implemented; RAG ingestion is the first linked module-specific run.

**Authoritative sources:** [`model.py`](../../../backend/app/platform/execution/model.py),
[`repository.py`](../../../backend/app/platform/execution/repository.py), and
[`0008 migration`](../../../backend/alembic/versions/20260905_0008_add_generic_workflows_and_runs.py).

**Hits**

- Project/workflow/user identity, engine, external execution ID, general
  status, validated inputs, output summary, settled quota cost, and categorized
  safe errors.

**Does not hit**

- Detailed document version, Bronze/Silver/Gold, chunking, embedding, or indexing
  state; that remains in a linked RAG ingestion run.
