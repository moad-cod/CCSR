# Project publication

**Status:** Implemented through versioned publication snapshots.

**Authoritative sources:** [`service.py`](../../../backend/app/platform/publication/service.py),
[`repository.py`](../../../backend/app/platform/publication/repository.py), and
[`0010 migration`](../../../backend/alembic/versions/20260907_0010_add_research_and_publication.py).

**Current movement**

```text
authorized private/draft editing -> validate selected public findings/artifacts
-> immutable publication revision -> unauthenticated public read
-> unpublish back to draft without deleting revision history
```

**Hits**

- Published research, safe artifact metadata, public
  slugs, and audit records.

**Does not hit**

- Private project access or arbitrary publication of private runs and
  artifacts.
