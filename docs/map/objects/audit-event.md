# Audit event

**Status:** Implemented for platform-administrative actions and quota bypasses.

**Authoritative sources:** [`model.py`](../../../backend/app/platform/audit/model.py),
[`repository.py`](../../../backend/app/platform/audit/repository.py), and
[`api.py`](../../../backend/app/platform/audit/api.py).

**Hits**

- Admin quota changes, account role changes, manual artifact registration,
  admin execution bypasses, outcomes, target identity, and redacted details.

**Does not hit**

- Credentials, raw stack traces, artifact bodies, or mutable operational logs.
