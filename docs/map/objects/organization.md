# Organization

**Status:** Implemented with membership-scoped access.

**Authoritative sources:**
[`organization.py`](../../../backend/app/platform/organizations/model.py),
[`organizations.py`](../../../backend/app/platform/organizations/api.py), and
[`organization_memberships.py`](../../../backend/app/platform/organizations/repository.py).

**Hits**

- Memberships, a user's active organization selection, optional project
  association, member-scoped visibility, and owner/admin mutations.

**Does not hit**

- Platform administration, invitation flows, project collaboration, or public
  portfolio visibility.
