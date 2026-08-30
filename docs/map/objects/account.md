# Account

**Status:** Implemented with canonical platform ownership and legacy import aliases.

**Authoritative sources:** [`model.py`](../../../backend/app/platform/accounts/model.py),
[`api.py`](../../../backend/app/platform/accounts/api.py), and
[`authentication.py`](../../../backend/app/platform/access/authentication.py).

**Hits**

- Authentication, current-user profile, active organization selection, owned
  projects, ingestion runs, and query logs.
- Account deletion currently triggers RAG/Qdrant project cleanup.

**Does not hit**

- Durable sessions, token revocation, platform admin roles, quotas, or public
  visitor state; those contracts do not exist yet.
