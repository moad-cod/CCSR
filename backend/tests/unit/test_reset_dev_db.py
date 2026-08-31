import asyncio
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from scripts import reset_dev_db


class ResetDevDatabaseTests(unittest.TestCase):
    def test_help_has_no_reset_side_effects(self):
        with (
            patch.object(reset_dev_db, "reset_database", new=AsyncMock()) as reset,
            redirect_stdout(StringIO()),
            self.assertRaises(SystemExit) as context,
        ):
            reset_dev_db.main(["--help"])

        self.assertEqual(context.exception.code, 0)
        reset.assert_not_awaited()

    def test_non_interactive_reset_requires_yes(self):
        with (
            patch.object(reset_dev_db.sys.stdin, "isatty", return_value=False),
            patch.object(reset_dev_db, "reset_database", new=AsyncMock()) as reset,
            redirect_stderr(StringIO()),
            self.assertRaises(SystemExit) as context,
        ):
            reset_dev_db.main([])

        self.assertEqual(context.exception.code, 2)
        reset.assert_not_awaited()

    def test_yes_and_skip_qdrant_run_database_reset_and_migration(self):
        reset = AsyncMock()
        with (
            patch.object(reset_dev_db, "reset_database", new=reset),
            patch.object(reset_dev_db, "migrate_to_head") as migrate,
            redirect_stdout(StringIO()),
        ):
            result = reset_dev_db.main(["--yes", "--skip-qdrant"])

        self.assertEqual(result, 0)
        reset.assert_awaited_once_with(reset_qdrant_state=False)
        migrate.assert_called_once_with()

    def test_qdrant_client_is_closed_after_collection_deletion(self):
        client = Mock()
        client.get_collections.return_value = SimpleNamespace(
            collections=[SimpleNamespace(name="one"), SimpleNamespace(name="two")]
        )
        factory = Mock(return_value=client)

        deleted = reset_dev_db.reset_qdrant(factory)

        self.assertEqual(deleted, 2)
        self.assertEqual(client.delete_collection.call_count, 2)
        client.close.assert_called_once_with()

    def test_database_engine_is_disposed_when_reset_fails(self):
        dispose = AsyncMock()
        with (
            patch.object(
                reset_dev_db,
                "drop_application_tables",
                new=AsyncMock(side_effect=RuntimeError("database unavailable")),
            ),
            patch.object(
                reset_dev_db,
                "engine",
                SimpleNamespace(dispose=dispose),
            ),
            redirect_stdout(StringIO()),
            self.assertRaisesRegex(RuntimeError, "database unavailable"),
        ):
            asyncio.run(reset_dev_db.reset_database(reset_qdrant_state=False))

        dispose.assert_awaited_once_with()


if __name__ == "__main__":
    unittest.main()
