"""Capability registration and lifecycle contracts."""

from app.platform.capabilities.contracts import (
    AccountDeletionContext,
    CapabilityDefinition,
    CapabilityLifecycle,
    LifecycleResult,
    ProjectDeletionContext,
)
from app.platform.capabilities.registry import CapabilityRegistry, capability_registry


__all__ = [
    "AccountDeletionContext",
    "CapabilityDefinition",
    "CapabilityLifecycle",
    "CapabilityRegistry",
    "LifecycleResult",
    "ProjectDeletionContext",
    "capability_registry",
]
