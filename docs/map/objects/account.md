# Account

**Status:** Implemented with canonical platform ownership and legacy import aliases.

**Authoritative sources:** [`model.py`](../../../backend/app/platform/accounts/model.py),
[`api.py`](../../../backend/app/platform/accounts/api.py), and
[`authentication.py`](../../../backend/app/platform/access/authentication.py).

**Hits**

- Authentication, durable sessions, global member/admin role, current-user
  profile, active organization selection, accessible projects, ingestion runs,
  and query logs.
- Account deletion triggers registered capability hooks; RAGForge contributes
  the existing Qdrant project-collection cleanup.

**Does not hit**

- Quotas or public visitor state; those contracts do not exist yet.
