from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from app.modules.ragforge.capability import register_ragforge_capability
from app.platform.capabilities import (
    AccountDeletionContext,
    CapabilityDefinition,
    CapabilityLifecycle,
    CapabilityRegistry,
    LifecycleResult,
    ProjectDeletionContext,
    ProjectProvisioningContext,
)
from app.platform.capabilities import registry as registry_module


class CapabilityRegistryTests(unittest.IsolatedAsyncioTestCase):
    async def test_lifecycle_hooks_run_in_registration_order_and_merge_counts(self):
        calls = []

        async def first_hook(_context):
            calls.append("first")
            return LifecycleResult(deleted_resources={"documents": 2})

        async def second_hook(_context):
            calls.append("second")
            return LifecycleResult(
                deleted_resources={"documents": 1, "artifacts": 4}
            )

        registry = CapabilityRegistry()
        registry.register(
            CapabilityDefinition(
                key="first",
                lifecycle=CapabilityLifecycle(before_project_delete=first_hook),
            )
        )
        registry.register(
            CapabilityDefinition(
                key="second",
                lifecycle=CapabilityLifecycle(before_project_delete=second_hook),
            )
        )

        with patch.object(
            registry_module.capability_repository,
            "list_project_capability_keys",
            AsyncMock(return_value=["first", "second"]),
        ):
            result = await registry.before_project_delete(
                ProjectDeletionContext(
                    db=SimpleNamespace(),
                    project=SimpleNamespace(id="project-id"),
                )
            )

        self.assertEqual(calls, ["first", "second"])
        self.assertEqual(result.count("documents"), 3)
        self.assertEqual(result.count("artifacts"), 4)

    async def test_account_hook_receives_account_and_owned_projects(self):
        received = []

        async def account_hook(context):
            received.append(context)
            return None

        registry = CapabilityRegistry()
        registry.register(
            CapabilityDefinition(
                key="account-aware",
                lifecycle=CapabilityLifecycle(before_account_delete=account_hook),
            )
        )
        account = SimpleNamespace(id="account-id")
        projects = [SimpleNamespace(id="project-id")]

        with patch.object(
            registry_module.capability_repository,
            "list_capability_project_ids",
            AsyncMock(return_value={"account-aware": {"project-id"}}),
        ):
            await registry.before_account_delete(
                AccountDeletionContext(
                    db=SimpleNamespace(),
                    account=account,
                    projects=projects,
                )
            )

        self.assertIs(received[0].account, account)
        self.assertEqual(received[0].projects, tuple(projects))

    async def test_default_capability_is_persisted_before_provisioning_hook(self):
        calls = []

        async def after_create(context):
            calls.append(("hook", context.project.id))

        registry = CapabilityRegistry()
        registry.register(
            CapabilityDefinition(
                key="enabled",
                enabled_by_default=True,
                lifecycle=CapabilityLifecycle(after_project_create=after_create),
            )
        )
        registry.register(CapabilityDefinition(key="opt-in"))

        async def enable(_db, *, project_id, capability_key):
            calls.append(("persist", project_id, capability_key))

        with patch.object(
            registry_module.capability_repository,
            "enable_project_capability",
            AsyncMock(side_effect=enable),
        ):
            enabled = await registry.provision_project(
                ProjectProvisioningContext(
                    db=SimpleNamespace(),
                    project=SimpleNamespace(id="project-id"),
                )
            )

        self.assertEqual(enabled, ("enabled",))
        self.assertEqual(
            calls,
            [
                ("persist", "project-id", "enabled"),
                ("hook", "project-id"),
            ],
        )

    def test_duplicate_capability_keys_are_rejected(self):
        registry = CapabilityRegistry()
        definition = CapabilityDefinition(key="duplicate")
        registry.register(definition)

        with self.assertRaisesRegex(ValueError, "already registered"):
            registry.register(definition)

    def test_ragforge_registration_is_idempotent_for_composition(self):
        registry = CapabilityRegistry()

        register_ragforge_capability(registry)
        register_ragforge_capability(registry)

        self.assertEqual(
            [definition.key for definition in registry.definitions()],
            ["ragforge"],
        )


if __name__ == "__main__":
    unittest.main()
