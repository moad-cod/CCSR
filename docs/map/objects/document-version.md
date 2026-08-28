# Document version

**Status:** Implemented; RAGForge ownership.

**Authoritative sources:**
[`document_version.py`](../../../backend/app/models/document_version.py),
[`document_versions.py`](../../../backend/app/repositories/document_versions.py),
and [`internal_pipeline.py`](../../../backend/app/api/internal_pipeline.py).

**Hits**

- Immutable source versions, content hashes, Bronze/Silver/Gold locations,
  ingestion attempts, chunks, and embedding runs.

**Does not hit**

- Generic artifact versioning or project publication snapshots.
