# Account

**Status:** Implemented, platform ownership not yet separated.

**Authoritative sources:** [`user.py`](../../../backend/app/models/user.py),
[`auth.py`](../../../backend/app/api/auth.py), and
[`core/auth.py`](../../../backend/app/core/auth.py).

**Hits**

- Authentication, current-user profile, active organization selection, owned
  projects, ingestion runs, and query logs.
- Account deletion currently triggers RAG/Qdrant project cleanup.

**Does not hit**

- Durable sessions, token revocation, platform admin roles, quotas, or public
  visitor state; those contracts do not exist yet.
