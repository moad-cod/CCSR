"""Compatibility alias for app.modules.ragforge.repositories.retrieval_logs."""

from app._compat import alias_module
from app.modules.ragforge.repositories import retrieval_logs as _implementation


alias_module(globals(), _implementation)
