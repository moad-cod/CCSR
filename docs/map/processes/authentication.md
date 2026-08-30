# Authentication

**Status:** Implemented JWT authentication; durable sessions are not implemented.

**Authoritative sources:** [`accounts/api.py`](../../../backend/app/platform/accounts/api.py),
[`authentication.py`](../../../backend/app/platform/access/authentication.py), and frontend auth route
handlers under [`frontend/src/app/api/auth`](../../../frontend/src/app/api/auth/).

**Current movement**

```text
credentials -> FastAPI login -> signed access token
-> Next.js HttpOnly cookie -> same-origin proxy -> Bearer token validation
```

**Hits**

- Registration, login, current-user routes, protected backend APIs, and frontend
  cookie/proxy behavior.

**Does not hit**

- Refresh sessions, revocation, OAuth, password recovery, quotas, or role policy.
