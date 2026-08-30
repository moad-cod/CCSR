"""Compatibility alias for app.modules.ragforge.services.bronze_storage."""

from app._compat import alias_module
from app.modules.ragforge.services import bronze_storage as _implementation


alias_module(globals(), _implementation)
