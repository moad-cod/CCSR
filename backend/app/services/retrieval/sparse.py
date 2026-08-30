"""Compatibility alias for app.modules.ragforge.services.retrieval.sparse."""

from app._compat import alias_module
from app.modules.ragforge.services.retrieval import sparse as _implementation


alias_module(globals(), _implementation)
