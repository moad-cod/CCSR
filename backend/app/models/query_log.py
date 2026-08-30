"""Compatibility alias for app.modules.ragforge.models.query_log."""

from app._compat import alias_module
from app.modules.ragforge.models import query_log as _implementation


alias_module(globals(), _implementation)
