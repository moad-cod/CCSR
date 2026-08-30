# Document version

**Status:** Implemented; RAGForge ownership.

**Authoritative sources:**
[`document_version.py`](../../../backend/app/modules/ragforge/models/document_version.py),
[`document_versions.py`](../../../backend/app/modules/ragforge/repositories/document_versions.py),
and [`internal_pipeline.py`](../../../backend/app/modules/ragforge/api/internal_pipeline.py).

**Hits**

- Immutable source versions, content hashes, Bronze/Silver/Gold locations,
  ingestion attempts, chunks, and embedding runs.

**Does not hit**

- Generic artifact versioning or project publication snapshots.
