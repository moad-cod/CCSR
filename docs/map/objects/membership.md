# Membership

**Status:** Implemented for organizations.

**Authoritative sources:**
[`organization_membership.py`](../../../backend/app/models/organization_membership.py),
[`organization_memberships.py`](../../../backend/app/repositories/organization_memberships.py),
and [`organizations.py`](../../../backend/app/api/organizations.py).

**Hits**

- Organization visibility and owner/admin organization mutations.
- Organization creation and a user's active organization selection.

**Does not hit**

- Platform-wide admin roles, invitations, membership-management APIs, project
  roles, or access to documents/runs owned by another member.
