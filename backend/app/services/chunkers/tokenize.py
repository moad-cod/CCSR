"""Compatibility alias for app.modules.ragforge.services.chunkers.tokenize."""

from app._compat import alias_module
from app.modules.ragforge.services.chunkers import tokenize as _implementation


alias_module(globals(), _implementation)
