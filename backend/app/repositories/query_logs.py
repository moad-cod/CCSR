"""Compatibility alias for app.modules.ragforge.repositories.query_logs."""

from app._compat import alias_module
from app.modules.ragforge.repositories import query_logs as _implementation


alias_module(globals(), _implementation)
