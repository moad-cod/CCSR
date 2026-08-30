"""Compatibility alias for app.modules.ragforge.services.retrieval.dense."""

from app._compat import alias_module
from app.modules.ragforge.services.retrieval import dense as _implementation


alias_module(globals(), _implementation)
