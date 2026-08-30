"""Compatibility alias for app.modules.ragforge.services.query_cache."""

from app._compat import alias_module
from app.modules.ragforge.services import query_cache as _implementation


alias_module(globals(), _implementation)
