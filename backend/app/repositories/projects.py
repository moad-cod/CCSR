from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Project


async def create_project(db: AsyncSession, **values) -> Project:
    project = Project(**values)
    db.add(project)
    await db.flush()
    return project


async def get_project(db: AsyncSession, project_id: str) -> Project | None:
    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.capabilities),
            selectinload(Project.rag_config),
        )
        .where(Project.id == project_id)
    )
    return result.scalar_one_or_none()


async def get_owned_project(db: AsyncSession, project_id: str, user_id: str) -> Project | None:
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.created_by == user_id,
            Project.deleted_at.is_(None),
        ).options(
            selectinload(Project.capabilities),
            selectinload(Project.rag_config),
        )
    )
    return result.scalar_one_or_none()


async def list_user_projects(db: AsyncSession, user_id: str) -> list[Project]:
    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.capabilities),
            selectinload(Project.rag_config),
        )
        .where(Project.created_by == user_id, Project.deleted_at.is_(None))
        .order_by(Project.created_at.desc())
    )
    return list(result.scalars().all())


async def list_accessible_projects(
    db: AsyncSession,
    *,
    user_id: str,
    global_role: str,
) -> list[Project]:
    query = (
        select(Project)
        .options(
            selectinload(Project.capabilities),
            selectinload(Project.rag_config),
        )
        .where(Project.deleted_at.is_(None))
        .order_by(Project.created_at.desc())
    )
    if global_role != "admin":
        from app.platform.organizations.membership import OrganizationMembership
        from app.platform.organizations.model import Organization

        query = (
            query.outerjoin(Organization, Organization.id == Project.organization_id)
            .outerjoin(
                OrganizationMembership,
                and_(
                    OrganizationMembership.organization_id == Project.organization_id,
                    OrganizationMembership.user_id == user_id,
                    OrganizationMembership.deleted_at.is_(None),
                ),
            )
            .where(
                or_(
                    Project.organization_id.is_(None),
                    Organization.deleted_at.is_(None),
                ),
                or_(
                    Project.created_by == user_id,
                    OrganizationMembership.id.is_not(None),
                )
            )
            .distinct()
        )
    result = await db.execute(query)
    return list(result.scalars().all())


async def rename_project(db: AsyncSession, project_id: str, user_id: str, name: str) -> Project | None:
    project = await get_owned_project(db, project_id, user_id)
    if project is not None:
        project.name = name
        await db.flush()
    return project
