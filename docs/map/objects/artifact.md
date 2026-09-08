# Artifact

**Status:** Shared metadata registry implemented; RAG objects remain in place.

**Authoritative sources:** [`model.py`](../../../backend/app/platform/artifacts/model.py),
[`repository.py`](../../../backend/app/platform/artifacts/repository.py), and
[`pipeline_artifacts.py`](../../../backend/app/modules/ragforge/services/pipeline_artifacts.py).

**Hits**

- Project/study/experiment/run/type/version/visibility/checksum/size/creator
  metadata.
- Existing version-scoped Bronze, Silver, and Gold objects plus Qdrant index
  lineage registered without moving their payloads.

**Does not hit**

- Large binary payload storage in PostgreSQL or Git; only metadata is durable
  in the registry.
