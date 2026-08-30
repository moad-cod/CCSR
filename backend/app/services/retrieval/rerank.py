"""Compatibility alias for app.modules.ragforge.services.retrieval.rerank."""

from app._compat import alias_module
from app.modules.ragforge.services.retrieval import rerank as _implementation


alias_module(globals(), _implementation)
