"""Compatibility alias for app.modules.ragforge.services.embedder."""

from app._compat import alias_module
from app.modules.ragforge.services import embedder as _implementation


alias_module(globals(), _implementation)
