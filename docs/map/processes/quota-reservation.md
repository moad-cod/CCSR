# Quota reservation

**Status:** Implemented for generic member runs.

**Authoritative sources:** [`service.py`](../../../backend/app/platform/quotas/service.py),
[`repository.py`](../../../backend/app/platform/quotas/repository.py), and
[`gateway.py`](../../../backend/app/platform/execution/gateway.py).

**Current movement**

```text
authorized workflow request -> validate policy and limits
-> lock account policy and atomically reserve durable usage -> dispatch
-> finalize started usage or release a pre-start failure
```

**Hits**

- Member limits, concurrency, generic run creation, usage history, and audited
  admin bypasses.

**Does not hit**

- Authorization itself or Redis as the durable usage ledger.
