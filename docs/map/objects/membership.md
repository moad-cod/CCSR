# Membership

**Status:** Implemented for organizations.

**Authoritative sources:**
[`organization_membership.py`](../../../backend/app/platform/organizations/membership.py),
[`organization_memberships.py`](../../../backend/app/platform/organizations/repository.py),
and [`organizations.py`](../../../backend/app/platform/organizations/api.py).

**Hits**

- Organization visibility and owner/admin organization mutations.
- Organization creation and a user's active organization selection.

**Does not hit**

- Platform-wide admin roles, invitations, membership-management APIs, project
  roles, or access to documents/runs owned by another member.
