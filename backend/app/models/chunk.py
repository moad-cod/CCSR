"""Compatibility alias for app.modules.ragforge.models.chunk."""

from app._compat import alias_module
from app.modules.ragforge.models import chunk as _implementation


alias_module(globals(), _implementation)
