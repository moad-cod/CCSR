from __future__ import annotations

from types import SimpleNamespace
import unittest

from app.modules.ragforge.capability import register_ragforge_capability
from app.platform.capabilities import (
    AccountDeletionContext,
    CapabilityDefinition,
    CapabilityLifecycle,
    CapabilityRegistry,
    LifecycleResult,
    ProjectDeletionContext,
)


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

        result = await registry.before_project_delete(
            ProjectDeletionContext(db=SimpleNamespace(), project=SimpleNamespace())
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

        await registry.before_account_delete(
            AccountDeletionContext(
                db=SimpleNamespace(),
                account=account,
                projects=projects,
            )
        )

        self.assertIs(received[0].account, account)
        self.assertIs(received[0].projects, projects)

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
