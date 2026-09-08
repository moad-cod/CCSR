from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from app.models import PublicationRevision
from app.platform.publication.service import (
    PublicationStateError,
    _public_snapshot,
    publish,
    unpublish,
)
from app.platform.research import repository as research_repository
from app.platform.research.slugs import normalize_slug


def publication_fixture(*, finding_visibility="public", artifact_visibility="public"):
    question = SimpleNamespace(question="Does retrieval improve accuracy?", rationale=None, ordinal=0)
    hypothesis = SimpleNamespace(
        statement="Retrieval improves grounded accuracy",
        rationale="Prior evidence",
        status="supported",
    )
    experiment = SimpleNamespace(
        id="experiment-id",
        slug="baseline",
        name="Baseline",
        objective="Measure grounded accuracy",
        status="completed",
        configuration={"provider_token": "must-not-be-public"},
    )
    study = SimpleNamespace(
        id="study-id",
        slug="retrieval-study",
        title="Retrieval Study",
        abstract="A public abstract",
        objective="Compare retrieval",
        methodology="Controlled evaluation",
        status="completed",
        questions=[question],
        hypotheses=[hypothesis],
        experiments=[experiment],
    )
    finding = SimpleNamespace(
        id="finding-id",
        experiment_id="experiment-id",
        title="Grounding improved",
        statement="The grounded configuration performed better.",
        evidence_summary="Measured on the evaluation set.",
        status="validated",
        visibility=finding_visibility,
    )
    artifact = SimpleNamespace(
        id="artifact-id",
        artifact_type="research-report",
        version="1",
        checksum="sha256:abc",
        size_bytes=42,
        visibility=artifact_visibility,
        storage_uri="minio://private/report.pdf",
        artifact_metadata={"format": "pdf"},
    )
    return SimpleNamespace(
        id="publication-id",
        project_id="project-id",
        research_study_id="study-id",
        slug="retrieval-results",
        title="Retrieval Results",
        summary="Public summary",
        state="draft",
        current_revision_number=None,
        published_at=None,
        project=SimpleNamespace(id="project-id", name="RAGForge"),
        research_study=study,
        findings=[finding],
        artifacts=[artifact],
    )


class ResearchHierarchyTests(unittest.IsolatedAsyncioTestCase):
    def test_normalize_slug_is_stable_and_url_safe(self):
        self.assertEqual(normalize_slug("  Selective QA: Study #1  "), "selective-qa-study-1")

    async def test_comparison_requires_at_least_two_experiments(self):
        db = SimpleNamespace()
        with self.assertRaisesRegex(ValueError, "at least two"):
            await research_repository.add_comparison(
                db,
                study=SimpleNamespace(id="study-id"),
                name="Incomplete comparison",
                experiment_ids=["one"],
                criteria={},
                result_summary={},
                conclusion=None,
            )

    async def test_dataset_must_use_artifact_from_same_project(self):
        db = SimpleNamespace(get=AsyncMock(return_value=SimpleNamespace(project_id="other")))
        with self.assertRaisesRegex(ValueError, "does not belong"):
            await research_repository.add_dataset(
                db,
                study=SimpleNamespace(id="study-id", project_id="project-id"),
                artifact_id="artifact-id",
                role="input",
                description=None,
            )


class PublicationSafetyTests(unittest.TestCase):
    def test_snapshot_exposes_only_public_projection(self):
        snapshot = _public_snapshot(publication_fixture())

        self.assertNotIn("configuration", snapshot["research_study"]["experiments"][0])
        self.assertNotIn("storage_uri", snapshot["artifacts"][0])
        self.assertNotIn("created_by", str(snapshot))
        self.assertNotIn("provider_token", str(snapshot))

    def test_snapshot_rejects_private_finding(self):
        with self.assertRaisesRegex(PublicationStateError, "validated public findings"):
            _public_snapshot(publication_fixture(finding_visibility="private"))

    def test_snapshot_rejects_private_artifact(self):
        with self.assertRaisesRegex(PublicationStateError, "public artifacts"):
            _public_snapshot(publication_fixture(artifact_visibility="private"))


class PublicationLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_publish_creates_immutable_revision_and_audit_event(self):
        publication = publication_fixture()
        db = SimpleNamespace(add=Mock(), flush=AsyncMock())
        actor = {"user_id": "admin-id", "global_role": "admin"}
        with (
            patch(
                "app.platform.publication.service.repository.get_publication",
                AsyncMock(return_value=publication),
            ),
            patch(
                "app.platform.publication.service.record_audit_event",
                AsyncMock(),
            ) as audit,
        ):
            result = await publish(
                db,
                project_id="project-id",
                publication_id="publication-id",
                actor=actor,
            )

        revision = db.add.call_args.args[0]
        self.assertIsInstance(revision, PublicationRevision)
        self.assertEqual(revision.revision_number, 1)
        self.assertEqual(result.state, "public")
        self.assertEqual(result.current_revision_number, 1)
        self.assertIsNotNone(result.published_at)
        self.assertEqual(audit.await_args.kwargs["action"], "publication.publish")

    async def test_publish_requires_draft_state(self):
        publication = publication_fixture()
        publication.state = "private"
        with patch(
            "app.platform.publication.service.repository.get_publication",
            AsyncMock(return_value=publication),
        ):
            with self.assertRaisesRegex(PublicationStateError, "Only a draft"):
                await publish(
                    SimpleNamespace(),
                    project_id="project-id",
                    publication_id="publication-id",
                    actor={"user_id": "user-id", "global_role": "member"},
                )

    async def test_unpublish_hides_snapshot_but_preserves_revision_number(self):
        publication = publication_fixture()
        publication.state = "public"
        publication.current_revision_number = 3
        db = SimpleNamespace(flush=AsyncMock())
        with patch(
            "app.platform.publication.service.record_audit_event", AsyncMock()
        ):
            await unpublish(
                db,
                publication=publication,
                actor={"user_id": "user-id", "global_role": "member"},
            )

        self.assertEqual(publication.state, "draft")
        self.assertEqual(publication.current_revision_number, 3)


if __name__ == "__main__":
    unittest.main()
