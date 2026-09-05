# Workflow definition

**Status:** Implemented; RAG document ingestion is the first registered version.

**Authoritative sources:**
[`model.py`](../../../backend/app/platform/execution/model.py),
[`registry.py`](../../../backend/app/platform/execution/registry.py), and
[`workflows.py`](../../../backend/app/modules/ragforge/workflows.py).

**Hits**

- Approved input/output schemas, workflow version, engine selection,
  runtime policy, module handler, and produced artifact types.

**Does not hit**

- The browser or arbitrary user-supplied commands. Engine selection and handler
  references come only from server-registered definitions.
