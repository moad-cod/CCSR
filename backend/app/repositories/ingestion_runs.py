"""Compatibility alias for app.modules.ragforge.repositories.ingestion_runs."""

from app._compat import alias_module
from app.modules.ragforge.repositories import ingestion_runs as _implementation


alias_module(globals(), _implementation)
