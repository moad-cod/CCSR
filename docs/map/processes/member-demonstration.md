# Member demonstration

**Status:** Planned; no safe generic member execution gateway exists.

**Verification sources:** current route registration in
[`main.py`](../../../backend/app/main.py), current models in
[`models/__init__.py`](../../../backend/app/models/__init__.py), and backend-
dependent frontend blockers in [`FRONTEND_MAP.md`](../../../frontend/FRONTEND_MAP.md).

**Target movement**

```text
member selects approved demonstration
-> server authorization -> quota reservation -> schema validation
-> registered workflow version -> generic run -> bounded result/artifacts
```

**Hits**

- Future approved models/datasets/parameters, quota and concurrency policy,
  generic run history, safe outputs, and auditing.

**Does not hit**

- Arbitrary shell commands, images, environment variables, DAG definitions,
  executable code, or infrastructure credentials supplied by members.
