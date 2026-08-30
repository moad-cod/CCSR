"""Compatibility alias for app.modules.ragforge.services.retrieval.types."""

from app._compat import alias_module
from app.modules.ragforge.services.retrieval import types as _implementation


alias_module(globals(), _implementation)
