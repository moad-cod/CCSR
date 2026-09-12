"""Application composition and repeat-construction tests."""

import unittest

from app.composition import create_app, register_capabilities, register_execution
from app.platform.capabilities import CapabilityRegistry
from app.platform.execution.registry import ExecutionRegistry


class CompositionTests(unittest.IsolatedAsyncioTestCase):
    def test_repeated_registration_is_idempotent(self):
        capabilities = CapabilityRegistry()
        execution = ExecutionRegistry()

        register_capabilities(capabilities)
        register_capabilities(capabilities)
        register_execution(execution)
        register_execution(execution)

        self.assertEqual(
            [definition.key for definition in capabilities.definitions()],
            ["ragforge"],
        )
        self.assertEqual(len(execution.definitions()), 1)
        self.assertIsNotNone(execution.adapter_for("airflow"))
        self.assertIsNotNone(execution.adapter_for("celery"))
        self.assertIsNotNone(
            execution.handler_for("celery", "ragforge.ingestion.workflow")
        )

    def test_repeated_application_construction_preserves_routes(self):
        first = create_app()
        second = create_app()

        first_routes = sorted(
            route.path for route in first.routes if hasattr(route, "path")
        )
        second_routes = sorted(
            route.path for route in second.routes if hasattr(route, "path")
        )
        self.assertEqual(first_routes, second_routes)
        self.assertEqual(first_routes.count("/health"), 1)

    async def test_health_smoke(self):
        app = create_app()
        async with app.router.lifespan_context(app):
            health_route = next(
                route
                for route in app.routes
                if getattr(route, "path", None) == "/health"
            )
            self.assertEqual(health_route.endpoint(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
