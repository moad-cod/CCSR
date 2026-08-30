"""Compatibility alias for app.modules.ragforge.services.chunkers.paragraph."""

from app._compat import alias_module
from app.modules.ragforge.services.chunkers import paragraph as _implementation


alias_module(globals(), _implementation)
