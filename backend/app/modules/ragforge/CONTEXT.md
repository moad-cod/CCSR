# RAGForge module ownership

This package owns pure RAGForge APIs, models, persistence, chunking, indexing,
retrieval, and query behavior. Compatibility aliases remain at the historical
app.api, app.models, app.repositories, and app.services paths.

The extraction is mechanical: public routes and payloads, SQL table names,
background task names, Redis keys, and environment variables are unchanged.
Mixed orchestration and shared infrastructure remain in their historical
locations until a later phase can separate them without changing behavior.

`capability.py` exposes the RAGForge capability definition and `lifecycle.py`
implements its project/account pre-delete cleanup hooks. `app/main.py` registers
that definition with the platform registry; platform routes do not import these
RAG-specific implementations.

`models/project_config.py` and `repositories/project_configs.py` are the
RAG-project boundary. Ingestion, document, query, internal-pipeline, indexing,
and lifecycle readers require both the durable `ragforge` association and a
`RAGProjectConfig`; they do not use the legacy project collection as their
configuration source. Project responses retain `collection` and
`qdrant_collection` while also exposing `capabilities` and `rag_config`.
