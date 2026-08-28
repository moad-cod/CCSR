# Airflow context

This folder contains the current RAG ingestion Airflow adapter: its image, DAG,
and control-plane callback plugin. Airflow is deployment infrastructure, while
the ordered ingestion stages are RAGForge workflow behavior.

Path and symbol names are referenced by `docker-compose.yml`, configured
`RAGFORGE_*_CMD` values, integration tests, and the Airflow image. Do not move or
rename them without preserving DAG discovery, command templates, callback
authentication, and the `ragforge_ingestion` DAG ID during migration.
