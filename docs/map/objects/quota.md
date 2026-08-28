# Quota

**Status:** Planned; no durable quota or usage model.

**Verification sources:** the current model registry in
[`models/__init__.py`](../../../backend/app/models/__init__.py) and current
backend limitations in [`BACKEND_MAP.md`](../../../backend/BACKEND_MAP.md).

**Hits**

- Future member run allowance, concurrency, runtime/input limits, reservation,
  finalization, and usage ledger.

**Does not hit**

- Authorization decisions. A permitted action can still exceed quota, and an
  action within quota can still be unauthorized.
