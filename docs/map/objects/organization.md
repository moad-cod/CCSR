# Organization

**Status:** Implemented with membership-scoped access and platform administration.

**Authoritative sources:**
[`organization.py`](../../../backend/app/platform/organizations/model.py),
[`organizations.py`](../../../backend/app/platform/organizations/api.py), and
[`organization_memberships.py`](../../../backend/app/platform/organizations/repository.py).

**Hits**

- Memberships and invitations, a user's active organization selection,
  organization-project collaboration, member-scoped visibility, owner/admin
  mutations, and platform-admin access.

**Does not hit**

- Public portfolio visibility or direct membership editing.
