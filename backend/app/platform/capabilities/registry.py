"""In-process registry for capability definitions and lifecycle hooks."""

from __future__ import annotations

from collections.abc import Iterable

from app.platform.capabilities.contracts import (
    AccountDeletionContext,
    CapabilityDefinition,
    LifecycleResult,
    ProjectDeletionContext,
)


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

    async def before_project_delete(
        self,
        context: ProjectDeletionContext,
    ) -> LifecycleResult:
        contributions = []
        for definition in self._definitions.values():
            hook = definition.lifecycle.before_project_delete
            if hook is not None:
                contributions.append(await hook(context))
        return self._merge(contributions)

    async def before_account_delete(
        self,
        context: AccountDeletionContext,
    ) -> LifecycleResult:
        contributions = []
        for definition in self._definitions.values():
            hook = definition.lifecycle.before_account_delete
            if hook is not None:
                contributions.append(await hook(context))
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
