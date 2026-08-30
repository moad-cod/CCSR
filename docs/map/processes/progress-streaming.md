# Progress streaming

**Status:** Implemented for ingestion and query streaming.

**Authoritative sources:** [`event_stream.py`](../../../backend/app/services/event_stream.py),
[`ingest.py`](../../../backend/app/modules/ragforge/api/ingest.py),
[`query.py`](../../../backend/app/modules/ragforge/api/query.py), and frontend
[`use-ingestion-stream.ts`](../../../frontend/src/hooks/use-ingestion-stream.ts).

**Current movement**

```text
durable PostgreSQL status + best-effort Redis event log
-> FastAPI SSE snapshot/replay/heartbeat -> frontend state
```

Query generation separately emits stage/token SSE events and persists the final
query trace.

**Hits**

- Ingestion recovery/replay, status snapshots, query tokens, frontend progress,
  and terminal events.

**Does not hit**

- Redis as authoritative run state or permission checks performed only in the
  browser.
