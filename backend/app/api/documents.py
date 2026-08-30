"""Compatibility alias for app.modules.ragforge.api.documents."""

from app._compat import alias_module
from app.modules.ragforge.api import documents as _implementation


alias_module(globals(), _implementation)
