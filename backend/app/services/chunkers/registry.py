"""Compatibility alias for app.modules.ragforge.services.chunkers.registry."""

from app._compat import alias_module
from app.modules.ragforge.services.chunkers import registry as _implementation


alias_module(globals(), _implementation)
