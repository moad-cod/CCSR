"""Reset local PostgreSQL and Qdrant development state safely."""

import argparse
import asyncio
from collections.abc import Callable, Sequence
from pathlib import Path
import sys

try:
    from scripts._bootstrap import ensure_backend_path
except ModuleNotFoundError:
    try:
        from backend.scripts._bootstrap import ensure_backend_path
    except ModuleNotFoundError:
        from _bootstrap import ensure_backend_path

ensure_backend_path()

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.core.db import engine, Base
import app.models  # noqa: F401 -- registers every model with Base.metadata
from app.core.config import settings
from qdrant_client import QdrantClient


def reset_qdrant(
    client_factory: Callable[..., QdrantClient] = QdrantClient,
) -> int:
    client = client_factory(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY or None,
        check_compatibility=False,
    )
    try:
        collections = client.get_collections().collections
        for collection in collections:
            client.delete_collection(collection_name=collection.name)
        return len(collections)
    finally:
        client.close()


async def drop_application_tables() -> None:
    async with engine.begin() as conn:
        # drop_all() cannot reset a legacy schema when an out-of-line foreign
        # key exists in current metadata but not in the database. Drop the
        # application tables together so PostgreSQL resolves either version of
        # the dependency graph; Alembic then recreates the current schema.
        preparer = conn.dialect.identifier_preparer
        names = [*sorted(Base.metadata.tables), "alembic_version"]
        table_names = ", ".join(preparer.quote(table_name) for table_name in names)
        await conn.execute(text(f"DROP TABLE IF EXISTS {table_names} CASCADE"))


def migrate_to_head() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "alembic"))
    command.upgrade(config, "head")


async def reset_database(*, reset_qdrant_state: bool = True) -> None:
    print("Resetting CCSR development state...")
    try:
        if reset_qdrant_state:
            deleted_collections = reset_qdrant()
            print(f"Deleted {deleted_collections} Qdrant collection(s)")
        else:
            print("Skipped Qdrant reset")

        await drop_application_tables()
        print("Dropped all application database tables")
    finally:
        await engine.dispose()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the interactive destructive-operation confirmation",
    )
    parser.add_argument(
        "--skip-qdrant",
        action="store_true",
        help="Reset PostgreSQL without contacting or deleting Qdrant collections",
    )
    return parser


def _confirm_reset(
    parser: argparse.ArgumentParser,
    *,
    assume_yes: bool,
    reset_qdrant_state: bool,
) -> bool:
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        parser.error("refusing a non-interactive reset without --yes")

    targets = "local application tables"
    if reset_qdrant_state:
        targets += " and Qdrant collections"
    response = input(f"This deletes {targets}. Type RESET to continue: ")
    return response == "RESET"


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not _confirm_reset(
        parser,
        assume_yes=args.yes,
        reset_qdrant_state=not args.skip_qdrant,
    ):
        print("Reset cancelled")
        return 1

    try:
        asyncio.run(reset_database(reset_qdrant_state=not args.skip_qdrant))
        migrate_to_head()
    except Exception as exc:
        print(f"Reset failed: {exc}", file=sys.stderr)
        if not args.skip_qdrant:
            print(
                "If Qdrant is intentionally unavailable, rerun with --skip-qdrant.",
                file=sys.stderr,
            )
        return 1

    print("Recreated the database at the latest Alembic revision")
    print("Fresh development reset complete. You can run test_chunkers.sh again.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
