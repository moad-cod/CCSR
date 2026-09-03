"""RAGForge capability definition registered by the application root."""

from app.modules.ragforge.lifecycle import (
    after_project_create,
    before_account_delete,
    before_project_delete,
)
from app.platform.capabilities import (
    CapabilityDefinition,
    CapabilityLifecycle,
    CapabilityRegistry,
)


RAGFORGE_CAPABILITY = CapabilityDefinition(
    key="ragforge",
    enabled_by_default=True,
    lifecycle=CapabilityLifecycle(
        after_project_create=after_project_create,
        before_project_delete=before_project_delete,
        before_account_delete=before_account_delete,
    ),
)


def register_ragforge_capability(registry: CapabilityRegistry) -> None:
    if registry.get(RAGFORGE_CAPABILITY.key) is None:
        registry.register(RAGFORGE_CAPABILITY)
