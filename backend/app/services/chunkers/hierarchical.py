"""Compatibility alias for app.modules.ragforge.services.chunkers.hierarchical."""

from app._compat import alias_module
from app.modules.ragforge.services.chunkers import hierarchical as _implementation


alias_module(globals(), _implementation)
