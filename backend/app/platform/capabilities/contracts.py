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
    collection: str
    deleted_at: datetime | None


class AccountLifecycleRecord(Protocol):
    """Account fields available to capability lifecycle hooks."""

    id: str
    deleted_at: datetime | None


@dataclass(frozen=True)
class ProjectDeletionContext:
    db: AsyncSession
    project: ProjectLifecycleRecord


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
AccountDeletionHook = Callable[
    [AccountDeletionContext],
    Awaitable[LifecycleResult | None],
]


@dataclass(frozen=True)
class CapabilityLifecycle:
    before_project_delete: ProjectDeletionHook | None = None
    before_account_delete: AccountDeletionHook | None = None


@dataclass(frozen=True)
class CapabilityDefinition:
    key: str
    lifecycle: CapabilityLifecycle = field(default_factory=CapabilityLifecycle)
