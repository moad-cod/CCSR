# Authorization

**Status:** Implemented for current platform, organization, and project actions.

**Authoritative sources:**
[`policies.py`](../../../backend/app/platform/access/policies.py),
[`organizations.py`](../../../backend/app/platform/organizations/api.py), and
[`authentication.py`](../../../backend/app/platform/access/authentication.py).

**Current movement**

```text
Bearer token -> durable session -> user identity + global role
organization action -> global-admin or membership-role policy
project/RAG action -> personal ownership or organization project policy
```

**Hits**

- Organization visibility/mutations, invitations, personal projects, shared
  organization projects, documents, ingestion runs, and queries.

**Does not hit**

- Public visitor authorization, per-project custom roles, quotas, workflow
  execution policy, or frontend navigation as a security boundary.
