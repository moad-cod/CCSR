"""Compatibility alias for app.modules.ragforge.api.chunkers."""

from app._compat import alias_module
from app.modules.ragforge.api import chunkers as _implementation


alias_module(globals(), _implementation)
