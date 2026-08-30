"""Compatibility alias for app.modules.ragforge.api.query."""

from app._compat import alias_module
from app.modules.ragforge.api import query as _implementation


alias_module(globals(), _implementation)
