"""In-process registry for capability definitions and lifecycle hooks."""

from __future__ import annotations

from collections.abc import Iterable

from app.platform.capabilities.contracts import (
    AccountDeletionContext,
    CapabilityDefinition,
    LifecycleResult,
    ProjectDeletionContext,
    ProjectProvisioningContext,
)
from app.platform.capabilities import repository as capability_repository


class CapabilityRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, CapabilityDefinition] = {}

    def register(self, definition: CapabilityDefinition) -> None:
        key = definition.key.strip()
        if not key:
            raise ValueError("Capability key must not be empty")
        if key in self._definitions:
            raise ValueError(f"Capability {key!r} is already registered")
        self._definitions[key] = definition

    def get(self, key: str) -> CapabilityDefinition | None:
        return self._definitions.get(key)

    def definitions(self) -> tuple[CapabilityDefinition, ...]:
        return tuple(self._definitions.values())

    async def provision_project(
        self,
        context: ProjectProvisioningContext,
    ) -> tuple[str, ...]:
        enabled: list[str] = []
        for definition in self._definitions.values():
            if not definition.enabled_by_default:
                continue
            await capability_repository.enable_project_capability(
                context.db,
                project_id=context.project.id,
                capability_key=definition.key,
            )
            hook = definition.lifecycle.after_project_create
            if hook is not None:
                await hook(context)
            enabled.append(definition.key)
        return tuple(enabled)

    async def before_project_delete(
        self,
        context: ProjectDeletionContext,
    ) -> LifecycleResult:
        enabled = set(
            await capability_repository.list_project_capability_keys(
                context.db,
                context.project.id,
            )
        )
        contributions = []
        for key, definition in self._definitions.items():
            if key not in enabled:
                continue
            hook = definition.lifecycle.before_project_delete
            if hook is not None:
                contributions.append(await hook(context))
        return self._merge(contributions)

    async def before_account_delete(
        self,
        context: AccountDeletionContext,
    ) -> LifecycleResult:
        by_capability = await capability_repository.list_capability_project_ids(
            context.db,
            [project.id for project in context.projects],
        )
        contributions = []
        for key, definition in self._definitions.items():
            enabled_project_ids = by_capability.get(key, set())
            if not enabled_project_ids:
                continue
            hook = definition.lifecycle.before_account_delete
            if hook is not None:
                contributions.append(
                    await hook(
                        AccountDeletionContext(
                            db=context.db,
                            account=context.account,
                            projects=tuple(
                                project
                                for project in context.projects
                                if project.id in enabled_project_ids
                            ),
                        )
                    )
                )
        return self._merge(contributions)

    @staticmethod
    def _merge(contributions: Iterable[LifecycleResult | None]) -> LifecycleResult:
        totals: dict[str, int] = {}
        for contribution in contributions:
            if contribution is None:
                continue
            for resource, count in contribution.deleted_resources.items():
                if count < 0:
                    raise ValueError("Lifecycle resource counts must not be negative")
                totals[resource] = totals.get(resource, 0) + count
        return LifecycleResult(deleted_resources=totals)


capability_registry = CapabilityRegistry()
