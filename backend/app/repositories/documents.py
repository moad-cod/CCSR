"""Compatibility alias for app.modules.ragforge.repositories.documents."""

from app._compat import alias_module
from app.modules.ragforge.repositories import documents as _implementation


alias_module(globals(), _implementation)
