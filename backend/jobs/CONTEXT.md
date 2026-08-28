# Ingestion jobs context

This folder contains orchestrator-neutral RAG ingestion stages and their CLI
wrappers. Airflow invokes the commands; Celery imports the shared stage
functions. The jobs communicate with FastAPI through the internal pipeline API
instead of writing PostgreSQL directly.

Preserve stage order, status transitions, artifact paths, command-line
arguments, environment variables, and idempotent Qdrant lineage when extracting
these jobs into a future workflow package.
