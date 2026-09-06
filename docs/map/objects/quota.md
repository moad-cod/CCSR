# Quota

**Status:** Implemented for per-account workflow execution.

**Authoritative sources:** [`model.py`](../../../backend/app/platform/quotas/model.py),
[`service.py`](../../../backend/app/platform/quotas/service.py), and
[`0009 migration`](../../../backend/alembic/versions/20260906_0009_add_quotas_artifacts_and_audit.py).

**Hits**

- Member run allowance, concurrency, runtime/input limits, reservation,
  finalization, and usage ledger.

**Does not hit**

- Authorization decisions. A permitted action can still exceed quota, and an
  action within quota can still be unauthorized.
