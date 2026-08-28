# Quota reservation

**Status:** Planned; no runtime implementation.

**Verification sources:** current models in
[`models/__init__.py`](../../../backend/app/models/__init__.py), settings in
[`config.py`](../../../backend/app/core/config.py), and limitations in
[`BACKEND_MAP.md`](../../../backend/BACKEND_MAP.md).

**Target movement**

```text
authorized workflow request -> validate policy and limits
-> atomically reserve durable usage -> dispatch
-> finalize actual usage or release reservation
```

**Hits**

- Future member limits, concurrency, generic run creation, usage history, and
  audited admin bypasses.

**Does not hit**

- Authorization itself or Redis as the durable usage ledger.
