"""Compatibility alias for app.modules.ragforge.services.retrieval.hybrid."""

from app._compat import alias_module
from app.modules.ragforge.services.retrieval import hybrid as _implementation


alias_module(globals(), _implementation)
