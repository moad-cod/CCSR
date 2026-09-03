from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.modules.ragforge.models.project_config import RAGProjectConfig
from app.platform.capabilities.model import ProjectCapability


RAGFORGE_CAPABILITY_KEY = "ragforge"


@dataclass(frozen=True)
class RAGProject:
    project: Project
    config: RAGProjectConfig

    @property
    def id(self) -> str:
        return self.project.id

    @property
    def organization_id(self) -> str | None:
        return self.project.organization_id

    @property
    def created_by(self) -> str:
        return self.project.created_by

    @property
    def collection(self) -> str:
        return self.config.qdrant_collection

    @property
    def qdrant_collection(self) -> str:
        return self.config.qdrant_collection

    def retrieval_option(self, key: str, default):
        configuration = self.config.retrieval_configuration or {}
        return configuration.get(key, default)

    @property
    def retrieval_strategy(self) -> str:
        value = self.retrieval_option("strategy", "hybrid")
        return value if value in {"dense", "hybrid"} else "hybrid"

    @property
    def retrieval_top_k(self) -> int:
        return _positive_int(self.retrieval_option("top_k", 5), default=5)

    @property
    def retrieval_fetch_k(self) -> int:
        return max(
            self.retrieval_top_k,
            _positive_int(self.retrieval_option("fetch_k", 30), default=30),
        )

    @property
    def use_rerank(self) -> bool:
        value = self.retrieval_option("use_rerank", True)
        return value if isinstance(value, bool) else True


def _positive_int(value, *, default: int) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


async def get_rag_project(
    db: AsyncSession,
    project_id: str,
    *,
    user_id: str | None = None,
    include_deleted: bool = False,
) -> RAGProject | None:
    query = (
        select(Project, RAGProjectConfig)
        .join(
            ProjectCapability,
            ProjectCapability.project_id == Project.id,
        )
        .join(
            RAGProjectConfig,
            RAGProjectConfig.project_id == Project.id,
        )
        .where(
            Project.id == project_id,
            ProjectCapability.capability_key == RAGFORGE_CAPABILITY_KEY,
        )
    )
    if user_id is not None:
        query = query.where(Project.created_by == user_id)
    if not include_deleted:
        query = query.where(Project.deleted_at.is_(None))

    row = (await db.execute(query)).one_or_none()
    if row is None:
        return None
    project, config = row
    return RAGProject(project=project, config=config)


async def get_rag_project_config(
    db: AsyncSession,
    project_id: str,
) -> RAGProjectConfig | None:
    return await db.get(RAGProjectConfig, project_id)


async def list_rag_project_configs(
    db: AsyncSession,
    project_ids: list[str],
) -> dict[str, RAGProjectConfig]:
    if not project_ids:
        return {}
    result = await db.execute(
        select(RAGProjectConfig).where(RAGProjectConfig.project_id.in_(project_ids))
    )
    return {config.project_id: config for config in result.scalars().all()}
