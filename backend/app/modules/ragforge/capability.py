"""RAGForge capability definition registered by the application root."""

from app.modules.ragforge.lifecycle import (
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
    lifecycle=CapabilityLifecycle(
        before_project_delete=before_project_delete,
        before_account_delete=before_account_delete,
    ),
)


def register_ragforge_capability(registry: CapabilityRegistry) -> None:
    if registry.get(RAGFORGE_CAPABILITY.key) is None:
        registry.register(RAGFORGE_CAPABILITY)
