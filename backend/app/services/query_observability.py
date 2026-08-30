"""Compatibility alias for app.modules.ragforge.services.query_observability."""

from app._compat import alias_module
from app.modules.ragforge.services import query_observability as _implementation


alias_module(globals(), _implementation)
