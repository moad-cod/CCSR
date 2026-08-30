"""Compatibility alias for app.modules.ragforge.services.storage."""

from app._compat import alias_module
from app.modules.ragforge.services import storage as _implementation


alias_module(globals(), _implementation)
