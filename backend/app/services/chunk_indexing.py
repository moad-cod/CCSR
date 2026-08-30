"""Compatibility alias for app.modules.ragforge.services.chunk_indexing."""

from app._compat import alias_module
from app.modules.ragforge.services import chunk_indexing as _implementation


alias_module(globals(), _implementation)
