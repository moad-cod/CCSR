# Capability lifecycle

**Status:** Implemented for project provisioning and project/account pre-delete
cleanup, gated by durable capability associations.

**Authoritative current sources:** platform contracts and registry in
[`capabilities/`](../../../backend/app/platform/capabilities), RAGForge hooks in
[`lifecycle.py`](../../../backend/app/modules/ragforge/lifecycle.py), and
registration in [`composition.py`](../../../backend/app/composition.py).

**Current movement**

```text
project creation -> persist default-enabled capability association
-> registered provisioning hook -> capability-owned configuration -> commit

project/account deletion route -> platform capability registry
-> enabled capability lookup -> registered RAGForge pre-delete hook -> external cleanup
-> platform soft-delete fields -> PostgreSQL commit
```

**Hits**

- RAG configuration provisioning, project document/vector/image cleanup,
  account-owned Qdrant collection cleanup, lifecycle failure propagation, and
  compatibility response counts.

**Does not hit**

- Capability-driven frontend navigation, generic workflows/runs, capability
  removal hooks, or user-selectable project capabilities.
