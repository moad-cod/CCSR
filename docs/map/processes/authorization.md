# Authorization

**Status:** Partially implemented with two different scopes.

**Authoritative sources:**
[`organizations.py`](../../../backend/app/api/organizations.py),
[`projects.py`](../../../backend/app/repositories/projects.py), and
[`core/auth.py`](../../../backend/app/core/auth.py).

**Current movement**

```text
Bearer token -> user identity
organization action -> membership and owner/admin check
project/RAG action -> Project.created_by check
```

**Hits**

- Organization visibility/mutations and creator-owned projects, documents,
  ingestion runs, and queries.

**Does not hit**

- Platform visitor/member/admin roles, project collaboration, quotas, workflow
  execution policy, or frontend navigation as a security boundary.
