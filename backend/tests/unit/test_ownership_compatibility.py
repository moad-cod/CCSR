"""Verify legacy ownership paths resolve to canonical module objects."""

import importlib
import unittest


MODULE_ALIASES = (
    ("app.core.auth", "app.platform.access.authentication"),
    ("app.api.auth", "app.platform.accounts.api"),
    ("app.models.user", "app.platform.accounts.model"),
    ("app.api.organizations", "app.platform.organizations.api"),
    ("app.models.organization", "app.platform.organizations.model"),
    (
        "app.models.organization_membership",
        "app.platform.organizations.membership",
    ),
    (
        "app.repositories.organization_memberships",
        "app.platform.organizations.repository",
    ),
    ("app.api.documents", "app.modules.ragforge.api.documents"),
    ("app.api.ingest", "app.modules.ragforge.api.ingest"),
    ("app.api.query", "app.modules.ragforge.api.query"),
    ("app.models.document", "app.modules.ragforge.models.document"),
    (
        "app.repositories.documents",
        "app.modules.ragforge.repositories.documents",
    ),
    ("app.services.indexer", "app.modules.ragforge.services.indexer"),
    (
        "app.services.query_cache",
        "app.modules.ragforge.services.query_cache",
    ),
    (
        "app.services.chunkers.fixed_size",
        "app.modules.ragforge.services.chunkers.fixed_size",
    ),
    (
        "app.services.retrieval.types",
        "app.modules.ragforge.services.retrieval.types",
    ),
)


class OwnershipCompatibilityTests(unittest.TestCase):
    def test_legacy_paths_alias_canonical_modules(self) -> None:
        for legacy_name, canonical_name in MODULE_ALIASES:
            with self.subTest(legacy=legacy_name):
                canonical = importlib.import_module(canonical_name)
                legacy = importlib.import_module(legacy_name)
                self.assertIs(legacy, canonical)


if __name__ == "__main__":
    unittest.main()
