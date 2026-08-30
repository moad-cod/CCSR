"""Compatibility alias for app.modules.ragforge.services.retriever."""

from app._compat import alias_module
from app.modules.ragforge.services import retriever as _implementation


alias_module(globals(), _implementation)
