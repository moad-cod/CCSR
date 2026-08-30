# Generic run

**Status:** Planned; the durable run currently implemented is RAG ingestion.

**Verification sources:** [`ingestion_run.py`](../../../backend/app/modules/ragforge/models/ingestion_run.py),
[`models/__init__.py`](../../../backend/app/models/__init__.py), and
[`ingestion_runs.py`](../../../backend/app/modules/ragforge/repositories/ingestion_runs.py).

**Hits**

- Future project/workflow/user identity, engine, external execution ID, general
  status, validated inputs, output summary, usage, and safe errors.

**Does not hit**

- Detailed document version, Bronze/Silver/Gold, chunking, embedding, or indexing
  state; that remains in a linked RAG ingestion run.
