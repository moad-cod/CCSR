# Organization invitation

**Status:** Implemented for authenticated organization onboarding.

**Authoritative sources:** [`invitation.py`](../../../backend/app/platform/organizations/invitation.py)
and [`organizations API`](../../../backend/app/platform/organizations/api.py).

**Hits**

- Organization owner/admin invitations, expiry, revocation, email-bound
  acceptance, and membership activation.

**Does not hit**

- Email delivery, unauthenticated account creation, or per-project invitations.
