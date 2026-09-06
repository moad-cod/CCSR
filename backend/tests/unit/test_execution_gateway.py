from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from pydantic import BaseModel

from app.platform.execution.adapters import CeleryExecutionAdapter
from app.platform.execution.contracts import RegisteredWorkflowDefinition
from app.platform.execution.gateway import ExecutionGateway
from app.platform.execution.registry import ExecutionRegistry


class _Input(BaseModel):
    resource_id: str


def _definition(engine="celery"):
    return RegisteredWorkflowDefinition(
        key="test.execute",
        version="1.0.0",
        capability_key="test",
        name="Test execution",
        description="Test workflow",
        engine=engine,
        input_model=_Input,
        output_schema={},
        handler_reference="test.handler",
        resource_requirements={},
    )


class ExecutionRegistryTests(unittest.TestCase):
    def test_registry_resolves_approved_version_and_engine_adapter(self):
        registry = ExecutionRegistry()
        adapter = CeleryExecutionAdapter()
        registry.register_workflow(_definition())
        registry.register_adapter(adapter)

        self.assertEqual(registry.get_workflow("test.execute").version, "1.0.0")
        self.assertIs(registry.adapter_for("celery"), adapter)

    def test_duplicate_workflow_version_is_rejected(self):
        registry = ExecutionRegistry()
        registry.register_workflow(_definition())

        with self.assertRaisesRegex(ValueError, "already registered"):
            registry.register_workflow(_definition())


class ExecutionGatewayTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_run_validates_capability_and_input_before_persisting(self):
        registry = ExecutionRegistry()
        definition = _definition()
        registry.register_workflow(definition)
        gateway = ExecutionGateway(registry)
        durable_definition = SimpleNamespace(id="definition-id")
        durable_run = SimpleNamespace(id="run-id")

        db = SimpleNamespace(
            get=AsyncMock(
                return_value=SimpleNamespace(
                    id="user-id",
                    global_role="member",
                    deleted_at=None,
                )
            )
        )
        with (
            patch(
                "app.platform.execution.gateway.capability_repository.list_project_capability_keys",
                AsyncMock(return_value=("test",)),
            ),
            patch(
                "app.platform.execution.gateway.repository.upsert_workflow_definition",
                AsyncMock(return_value=durable_definition),
            ) as upsert,
            patch(
                "app.platform.execution.gateway.repository.create_run",
                AsyncMock(return_value=durable_run),
            ) as create,
            patch(
                "app.platform.execution.gateway.reserve_run_quota",
                AsyncMock(),
            ) as reserve,
        ):
            result = await gateway.create_run(
                db,
                workflow_key="test.execute",
                project_id="project-id",
                requested_by="user-id",
                input_data={"resource_id": "resource-id"},
            )

        self.assertIs(result, durable_run)
        upsert.assert_awaited_once()
        self.assertEqual(create.await_args.kwargs["engine"], "celery")
        self.assertEqual(
            create.await_args.kwargs["input_snapshot"],
            {"resource_id": "resource-id"},
        )
        reserve.assert_awaited_once()

    async def test_create_run_denies_projects_without_required_capability(self):
        registry = ExecutionRegistry()
        registry.register_workflow(_definition())
        gateway = ExecutionGateway(registry)

        with patch(
            "app.platform.execution.gateway.capability_repository.list_project_capability_keys",
            AsyncMock(return_value=()),
        ):
            with self.assertRaisesRegex(ValueError, "not enabled"):
                await gateway.create_run(
                    SimpleNamespace(),
                    workflow_key="test.execute",
                    project_id="project-id",
                    requested_by="user-id",
                    input_data={"resource_id": "resource-id"},
                )


class CeleryAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_adapter_uses_only_the_registered_module_handler(self):
        handler = AsyncMock(return_value="external-id")

        receipt = await CeleryExecutionAdapter().dispatch(
            _definition(),
            {"resource_id": "resource-id"},
            handler,
        )

        self.assertEqual(receipt.external_execution_id, "external-id")
        handler.assert_awaited_once_with({"resource_id": "resource-id"})


if __name__ == "__main__":
    unittest.main()
