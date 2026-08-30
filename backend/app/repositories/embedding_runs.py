"""Compatibility alias for app.modules.ragforge.repositories.embedding_runs."""

from app._compat import alias_module
from app.modules.ragforge.repositories import embedding_runs as _implementation


alias_module(globals(), _implementation)
