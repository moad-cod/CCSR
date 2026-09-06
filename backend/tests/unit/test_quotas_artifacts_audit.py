from decimal import Decimal
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from app.platform.artifacts.repository import register_artifact
from app.platform.audit.safety import safe_execution_error, sanitize_details
from app.modules.ragforge.repositories.ingestion_runs import _minio_storage_uri
from app.models import QuotaReservation
from app.platform.quotas.service import QuotaExceededError, finalize_run_quota, reserve_run_quota


class SafetyTests(unittest.TestCase):
    def test_audit_details_redact_nested_credentials(self):
        sanitized = sanitize_details(
            {"token": "secret", "nested": {"api_key": "key", "safe": "value"}}
        )

        self.assertEqual(sanitized["token"], "[redacted]")
        self.assertEqual(sanitized["nested"]["api_key"], "[redacted]")
        self.assertEqual(sanitized["nested"]["safe"], "value")

    def test_execution_errors_are_stable_and_do_not_echo_secrets(self):
        code, message = safe_execution_error("token=secret broker exploded")

        self.assertEqual(code, "dispatch_failed")
        self.assertNotIn("secret", message)


class QuotaServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_member_run_reserves_one_atomic_usage_unit(self):
        policy = SimpleNamespace(
            id="policy-id",
            enabled=True,
            max_input_bytes=1024,
            max_runtime_seconds=600,
            concurrent_run_limit=2,
            daily_run_limit=10,
            monthly_run_limit=20,
        )
        run = SimpleNamespace(
            id="run-id",
            project_id="project-id",
            requested_by="user-id",
            input_snapshot={"value": 1},
        )
        workflow = SimpleNamespace(
            key="test.execute",
            version="1.0.0",
            member_execution_allowed=True,
            runtime_limit_seconds=60,
        )
        db = SimpleNamespace(add=Mock(), flush=AsyncMock())
        with (
            patch("app.platform.quotas.service.repository.get_user_policy", AsyncMock(return_value=policy)),
            patch("app.platform.quotas.service.repository.active_reservation_count", AsyncMock(return_value=0)),
            patch("app.platform.quotas.service.repository.consumed_units", AsyncMock(return_value=Decimal("0"))),
        ):
            reservation = await reserve_run_quota(
                db,
                run=run,
                workflow=workflow,
                actor_global_role="member",
            )

        self.assertEqual(reservation.status, "reserved")
        self.assertEqual(reservation.reserved_units, Decimal("1"))
        db.add.assert_called_once_with(reservation)
        db.flush.assert_awaited_once()

    async def test_daily_limit_denies_without_creating_reservation(self):
        policy = SimpleNamespace(
            id="policy-id",
            enabled=True,
            max_input_bytes=None,
            max_runtime_seconds=None,
            concurrent_run_limit=2,
            daily_run_limit=1,
            monthly_run_limit=20,
        )
        run = SimpleNamespace(id="run-id", project_id="project-id", requested_by="user-id", input_snapshot={})
        workflow = SimpleNamespace(
            key="test.execute",
            version="1.0.0",
            member_execution_allowed=True,
            runtime_limit_seconds=None,
        )
        db = SimpleNamespace(add=Mock(), flush=AsyncMock())
        with (
            patch("app.platform.quotas.service.repository.get_user_policy", AsyncMock(return_value=policy)),
            patch("app.platform.quotas.service.repository.active_reservation_count", AsyncMock(return_value=0)),
            patch("app.platform.quotas.service.repository.consumed_units", AsyncMock(return_value=Decimal("1"))),
        ):
            with self.assertRaises(QuotaExceededError) as context:
                await reserve_run_quota(db, run=run, workflow=workflow, actor_global_role="member")

        self.assertEqual(context.exception.code, "daily_limit_exceeded")
        db.add.assert_not_called()

    async def test_admin_bypass_is_audited(self):
        run = SimpleNamespace(id="run-id", project_id="project-id", requested_by="admin-id")
        workflow = SimpleNamespace(key="test.execute", version="1.0.0")
        with patch("app.platform.quotas.service.record_audit_event", AsyncMock()) as audit:
            reservation = await reserve_run_quota(
                SimpleNamespace(),
                run=run,
                workflow=workflow,
                actor_global_role="admin",
            )

        self.assertIsNone(reservation)
        self.assertEqual(audit.await_args.kwargs["action"], "quota.bypass")

    async def test_prestart_failure_releases_reserved_usage(self):
        reservation = QuotaReservation(
            status="reserved",
            reserved_units=Decimal("1"),
        )
        run = SimpleNamespace(id="run-id", quota_cost=Decimal("0"))
        db = SimpleNamespace(flush=AsyncMock())
        with patch(
            "app.platform.quotas.service.repository.get_run_reservation",
            AsyncMock(return_value=reservation),
        ):
            await finalize_run_quota(db, run, consume=False)

        self.assertEqual(reservation.status, "released")
        self.assertEqual(reservation.actual_units, Decimal("0"))
        self.assertEqual(run.quota_cost, Decimal("0"))


class ArtifactRepositoryTests(unittest.IsolatedAsyncioTestCase):
    def test_minio_uri_does_not_repeat_bucket_prefix(self):
        self.assertEqual(
            _minio_storage_uri("bronze", "bronze/project/source.pdf"),
            "minio://bronze/project/source.pdf",
        )

    async def test_registration_is_idempotent_for_run_type_and_uri(self):
        existing = SimpleNamespace(id="artifact-id")
        result = SimpleNamespace(scalar_one_or_none=Mock(return_value=existing))
        db = SimpleNamespace(execute=AsyncMock(return_value=result), add=Mock(), flush=AsyncMock())

        artifact = await register_artifact(
            db,
            project_id="project-id",
            run_id="run-id",
            artifact_type="metrics",
            storage_provider="minio",
            storage_uri="minio://artifacts/metrics.json",
            created_by="user-id",
        )

        self.assertIs(artifact, existing)
        db.add.assert_not_called()


if __name__ == "__main__":
    unittest.main()
