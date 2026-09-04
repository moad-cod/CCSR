# Authentication

**Status:** Implemented JWT authentication backed by durable revocable sessions.

**Authoritative sources:** [`accounts/api.py`](../../../backend/app/platform/accounts/api.py),
[`authentication.py`](../../../backend/app/platform/access/authentication.py), and frontend auth route
handlers under [`frontend/src/app/api/auth`](../../../frontend/src/app/api/auth/).

**Current movement**

```text
credentials -> FastAPI login -> durable session + signed access token
-> Next.js HttpOnly cookie -> same-origin proxy -> Bearer token validation
-> session/account/global-role validation
```

**Hits**

- Registration, login/logout, session listing/revocation, current-user routes,
  protected backend APIs, and frontend cookie/proxy behavior.

**Does not hit**

- Refresh tokens, OAuth, password recovery, and quotas.
