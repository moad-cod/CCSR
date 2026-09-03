"""Stable platform contracts for registered capability lifecycle behavior."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class ProjectLifecycleRecord(Protocol):
    """Project fields available to capability lifecycle hooks."""

    id: str
    created_by: str
    deleted_at: datetime | None


class AccountLifecycleRecord(Protocol):
    """Account fields available to capability lifecycle hooks."""

    id: str
    deleted_at: datetime | None


class ProjectProvisioningRecord(ProjectLifecycleRecord, Protocol):
    """Temporary legacy fields available while project creation dual-writes."""

    qdrant_collection: str


@dataclass(frozen=True)
class ProjectDeletionContext:
    db: AsyncSession
    project: ProjectLifecycleRecord


@dataclass(frozen=True)
class ProjectProvisioningContext:
    db: AsyncSession
    project: ProjectProvisioningRecord


@dataclass(frozen=True)
class AccountDeletionContext:
    db: AsyncSession
    account: AccountLifecycleRecord
    projects: Sequence[ProjectLifecycleRecord]


@dataclass(frozen=True)
class LifecycleResult:
    """Capability-neutral resource counts contributed by lifecycle hooks."""

    deleted_resources: Mapping[str, int] = field(default_factory=dict)

    def count(self, resource: str) -> int:
        return int(self.deleted_resources.get(resource, 0))


ProjectDeletionHook = Callable[
    [ProjectDeletionContext],
    Awaitable[LifecycleResult | None],
]
ProjectProvisioningHook = Callable[
    [ProjectProvisioningContext],
    Awaitable[None],
]
AccountDeletionHook = Callable[
    [AccountDeletionContext],
    Awaitable[LifecycleResult | None],
]


@dataclass(frozen=True)
class CapabilityLifecycle:
    after_project_create: ProjectProvisioningHook | None = None
    before_project_delete: ProjectDeletionHook | None = None
    before_account_delete: AccountDeletionHook | None = None


@dataclass(frozen=True)
class CapabilityDefinition:
    key: str
    enabled_by_default: bool = False
    lifecycle: CapabilityLifecycle = field(default_factory=CapabilityLifecycle)
