# RAGForge module ownership

This package owns pure RAGForge APIs, models, persistence, chunking, indexing,
retrieval, and query behavior. Compatibility aliases remain at the historical
app.api, app.models, app.repositories, and app.services paths.

The extraction is mechanical: public routes and payloads, SQL table names,
background task names, Redis keys, and environment variables are unchanged.
Mixed orchestration and shared infrastructure remain in their historical
locations until a later phase can separate them without changing behavior.
