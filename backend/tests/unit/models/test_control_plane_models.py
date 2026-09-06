import unittest

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import configure_mappers

from app.core.db import Base
from app.models import (
    Chunk,
    Document,
    EmbeddingRun,
    AuthSession,
    IngestionRun,
    GenericRun,
    OrganizationInvitation,
    OrganizationMembership,
    ProjectCapability,
    QueryLog,
    RAGProjectConfig,
    User,
    WorkflowDefinition,
    Artifact,
    AuditEvent,
    QuotaPolicy,
    QuotaReservation,
)


class ControlPlaneModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure_mappers()

    def test_tasks_4_through_9_tables_are_registered(self):
        self.assertTrue(
            {
                "ingestion_runs",
                "organization_memberships",
                "organization_invitations",
                "auth_sessions",
                "chunks",
                "embedding_runs",
                "query_logs",
                "retrieval_logs",
                "project_capabilities",
                "rag_project_configs",
                "workflow_definitions",
                "runs",
                "quota_policies",
                "quota_reservations",
                "artifacts",
                "audit_events",
            }.issubset(Base.metadata.tables)
        )

    def test_capability_and_rag_configuration_constraints_are_registered(self):
        capability_primary_key = tuple(
            ProjectCapability.__table__.primary_key.columns.keys()
        )
        self.assertEqual(
            capability_primary_key,
            ("project_id", "capability_key"),
        )

        config_unique_columns = {
            tuple(constraint.columns.keys())
            for constraint in RAGProjectConfig.__table__.constraints
            if isinstance(constraint, UniqueConstraint)
        }
        self.assertIn(("qdrant_collection",), config_unique_columns)
        config_foreign_key = next(
            iter(RAGProjectConfig.__table__.c.project_id.foreign_keys)
        )
        self.assertEqual(
            config_foreign_key.ondelete,
            "CASCADE",
        )

    def test_current_version_foreign_key_targets_document_versions(self):
        foreign_keys = list(Document.__table__.c.current_version_id.foreign_keys)
        self.assertEqual(len(foreign_keys), 1)
        self.assertEqual(foreign_keys[0].target_fullname, "document_versions.id")
        self.assertEqual(foreign_keys[0].ondelete, "SET NULL")

    def test_query_log_persists_streamed_final_answer(self):
        self.assertIn("answer", QueryLog.__table__.columns)
        self.assertTrue(QueryLog.__table__.c.answer.nullable)

    def test_invalid_lifecycle_statuses_are_rejected_by_models(self):
        cases = (
            (Document, "status", "not-a-document-status"),
            (IngestionRun, "status", "not-an-ingestion-status"),
            (EmbeddingRun, "status", "not-an-embedding-status"),
            (OrganizationMembership, "role", "not-an-organization-role"),
            (OrganizationInvitation, "role", "not-an-organization-role"),
            (User, "global_role", "not-a-global-role"),
            (WorkflowDefinition, "engine", "not-an-engine"),
            (GenericRun, "status", "not-a-run-status"),
            (Artifact, "visibility", "not-a-visibility"),
            (AuditEvent, "outcome", "not-an-outcome"),
            (QuotaReservation, "status", "not-a-reservation-status"),
        )
        for model, field_name, invalid_value in cases:
            with self.subTest(model=model.__name__):
                with self.assertRaises(ValueError):
                    model(**{field_name: invalid_value})

    def test_lifecycle_statuses_have_database_check_constraints(self):
        for model in (Document, IngestionRun, EmbeddingRun):
            with self.subTest(model=model.__name__):
                checks = [
                    constraint
                    for constraint in model.__table__.constraints
                    if isinstance(constraint, CheckConstraint)
                ]
                self.assertEqual(len(checks), 1)

    def test_organization_membership_uniqueness_constraints_are_present(self):
        unique_columns = {
            tuple(constraint.columns.keys())
            for constraint in OrganizationMembership.__table__.constraints
            if isinstance(constraint, UniqueConstraint)
        }
        self.assertIn(("organization_id", "user_id"), unique_columns)

    def test_platform_authorization_models_are_registered(self):
        self.assertEqual(AuthSession.__table__.c.token_hash.type.length, 64)
        self.assertFalse(AuthSession.__table__.c.expires_at.nullable)
        self.assertFalse(OrganizationInvitation.__table__.c.expires_at.nullable)

    def test_embedding_run_tracks_model_loading_and_retrying(self):
        self.assertEqual(EmbeddingRun(status="loading_model").status, "loading_model")
        self.assertEqual(EmbeddingRun(status="retrying").status, "retrying")

    def test_chunk_uniqueness_constraints_are_present(self):
        unique_columns = {
            tuple(constraint.columns.keys())
            for constraint in Chunk.__table__.constraints
            if isinstance(constraint, UniqueConstraint)
        }
        self.assertIn(("qdrant_point_id",), unique_columns)
        self.assertIn(("document_version_id", "chunk_index"), unique_columns)
        self.assertNotIn(("document_version_id", "content_hash"), unique_columns)

    def test_task_11_required_indexes_are_present(self):
        expected = {
            "documents": {
                ("project_id",),
                ("current_version_id",),
                ("status",),
                ("created_by",),
                ("created_at",),
            },
            "organization_memberships": {
                ("organization_id",),
                ("user_id",),
                ("role",),
                ("deleted_at",),
            },
            "document_versions": {
                ("document_id",),
                ("status",),
                ("content_hash",),
                ("created_at",),
            },
            "ingestion_runs": {
                ("project_id",),
                ("document_id",),
                ("document_version_id",),
                ("status",),
                ("created_at",),
            },
            "chunks": {
                ("project_id",),
                ("document_id",),
                ("document_version_id",),
                ("qdrant_point_id",),
                ("content_hash",),
                ("created_at",),
                ("project_id", "document_id"),
                ("document_version_id", "chunk_index"),
            },
            "query_logs": {
                ("project_id",),
                ("user_id",),
                ("normalized_question_hash",),
                ("created_at",),
                ("project_id", "created_at"),
            },
            "retrieval_logs": {
                ("query_log_id",),
                ("chunk_id",),
                ("rank",),
                ("query_log_id", "rank"),
            },
        }
        for table_name, required_columns in expected.items():
            with self.subTest(table=table_name):
                actual = {
                    tuple(index.columns.keys())
                    for index in Base.metadata.tables[table_name].indexes
                }
                self.assertTrue(required_columns.issubset(actual))


if __name__ == "__main__":
    unittest.main()
