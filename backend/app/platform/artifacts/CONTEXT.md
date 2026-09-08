# Platform artifact context

This package registers shared artifact metadata. Binary payloads remain in
MinIO (or another declared provider); PostgreSQL stores
project/study/experiment/run lineage, type, URI, version, visibility, checksum,
size, creator, and safe metadata.

RAGForge registers Bronze, Silver, Gold, and Qdrant index records through this
boundary without moving or renaming its existing objects.

Public visibility makes an artifact eligible for explicit publication
selection. It does not expose authenticated artifact APIs or storage locations.
