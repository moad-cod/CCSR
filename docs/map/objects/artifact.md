# Artifact

**Status:** RAG pipeline artifacts exist; a shared artifact registry does not.

**Authoritative current sources:**
[`pipeline_artifacts.py`](../../../backend/app/services/pipeline_artifacts.py),
[`document_version.py`](../../../backend/app/models/document_version.py), and
[`docker-compose.yml`](../../../docker-compose.yml).

**Hits**

- Current version-scoped Bronze, Silver, and Gold object paths in MinIO.
- Future datasets, models, metrics, reports, figures, notebooks, and
  reproducibility packages after a generic registry is added.

**Does not hit**

- Large binary payload storage in PostgreSQL or Git.
