"""Compatibility alias for app.modules.ragforge.services.chunkers.sentence."""

from app._compat import alias_module
from app.modules.ragforge.services.chunkers import sentence as _implementation


alias_module(globals(), _implementation)
