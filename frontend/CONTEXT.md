# Frontend context

The frontend is one Next.js application serving authenticated CCSR screens. It
uses a same-origin backend proxy and HttpOnly authentication cookie. The current
project experience still assumes RAG data and routes. Login tokens are backed
by durable backend sessions, and the logout handler revokes the backend session
before clearing the compatibility cookie.

## Route by task

- App Router and route handlers: `src/app/`
- Current screen and shell components: `src/components/`
- Shared accessible primitives: `src/components/ui/`
- Client data hooks: `src/hooks/`
- API proxy/client, server auth, types, and SSE helpers: `src/lib/`
- Detailed current map: `FRONTEND_MAP.md`

Read [`src/CONTEXT.md`](src/CONTEXT.md) before moving screens or changing route
composition.

Preserve public route paths, authentication cookies, ingestion progress,
streaming answers, citations, query history, and the graphite/blue/violet visual
identity. Route files should remain thin as platform and RAGForge screen
ownership is introduced.
