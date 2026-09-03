# Capability

**Status:** Implemented for durable project enablement and lifecycle dispatch.

**Authoritative sources:** lifecycle contracts and registry in
[`capabilities/`](../../../backend/app/platform/capabilities), built-in
registration in [`main.py`](../../../backend/app/main.py), current project
schema in [`project.py`](../../../backend/app/models/project.py), and the product
direction in [`CONTEXT.md`](../../../CONTEXT.md).

**Hits**

- Future reusable behaviors such as RAG, evaluation, datasets, fine-tuning,
  classification, reproducibility, demonstrations, and publication.
- Capability-contributed backend workflows and frontend navigation.
- Project creation provisioning and project/account pre-delete cleanup
  contributed by RAGForge.
- Durable many-capability project enablement through `project_capabilities`.

**Does not hit**

- A one-to-one project type, capability-driven frontend navigation, or a
  requirement to create a source-code module per project.
