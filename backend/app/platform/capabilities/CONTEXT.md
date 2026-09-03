# Platform capability context

This package owns capability contracts, the in-process definition registry,
and durable project enablement associations. It must not import capability
business logic.

- `model.py` stores enabled capability keys in `project_capabilities`.
- `repository.py` reads and writes those associations.
- `contracts.py` defines project provisioning and deletion lifecycle contexts.
- `registry.py` invokes hooks only for durable enabled associations. Definitions
  marked `enabled_by_default` are persisted during project creation before their
  provisioning hook runs.

Capability packages register definitions at the application composition root.
Do not add `project.type` branching or capability-specific configuration to
this platform package.
