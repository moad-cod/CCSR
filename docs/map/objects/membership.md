# Membership

**Status:** Implemented for organizations.

**Authoritative sources:**
[`organization_membership.py`](../../../backend/app/platform/organizations/membership.py),
[`organization_memberships.py`](../../../backend/app/platform/organizations/repository.py),
and [`organizations.py`](../../../backend/app/platform/organizations/api.py).

**Hits**

- Organization visibility, owner/admin organization mutations, and expiring
  invitations that activate or restore memberships.
- Organization creation and a user's active organization selection.

**Does not hit**

- Per-project custom roles and direct membership editing APIs.
