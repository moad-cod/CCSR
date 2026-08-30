"""Compatibility alias for app.modules.ragforge.services.chunkers.proposition."""

from app._compat import alias_module
from app.modules.ragforge.services.chunkers import proposition as _implementation


alias_module(globals(), _implementation)
