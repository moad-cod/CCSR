# Capability lifecycle

**Status:** Implemented for project and account pre-delete cleanup.

**Authoritative current sources:** platform contracts and registry in
[`capabilities/`](../../../backend/app/platform/capabilities), RAGForge hooks in
[`lifecycle.py`](../../../backend/app/modules/ragforge/lifecycle.py), and
registration in [`main.py`](../../../backend/app/main.py).

**Current movement**

```text
project/account deletion route -> platform capability registry
-> registered RAGForge pre-delete hook -> external cleanup
-> platform soft-delete fields -> PostgreSQL commit
```

**Hits**

- Project document/vector/image cleanup, account-owned Qdrant collection
  cleanup, lifecycle failure propagation, and compatibility response counts.

**Does not hit**

- Durable project-capability associations, project creation, capability-driven
  frontend navigation, generic workflows/runs, or database schema.
