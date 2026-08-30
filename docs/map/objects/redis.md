# Redis

**Status:** Implemented as best-effort transport and cache.

**Authoritative sources:** [`event_stream.py`](../../../backend/app/services/event_stream.py),
[`query_cache.py`](../../../backend/app/modules/ragforge/services/query_cache.py), and
[`docker-compose.yml`](../../../docker-compose.yml).

**Hits**

- Replayable ingestion progress, query result caching, Celery broker/result
  transport, and future short-lived rate/concurrency controls.

**Does not hit**

- Authoritative runs, quota accounting, accounts, or publication state.
