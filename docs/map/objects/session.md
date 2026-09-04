# Session

**Status:** Implemented as a durable authorization record.

**Authoritative sources:** [`session.py`](../../../backend/app/platform/access/session.py),
[`authentication.py`](../../../backend/app/platform/access/authentication.py), and
[`accounts API`](../../../backend/app/platform/accounts/api.py).

**Hits**

- Login, bearer-token validation, logout, session listing/revocation, password
  changes, and account deletion.

**Does not hit**

- Refresh-token rotation, OAuth providers, or anonymous visitor state.
