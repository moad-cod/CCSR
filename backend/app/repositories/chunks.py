"""Compatibility alias for app.modules.ragforge.repositories.chunks."""

from app._compat import alias_module
from app.modules.ragforge.repositories import chunks as _implementation


alias_module(globals(), _implementation)
