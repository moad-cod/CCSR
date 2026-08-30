"""Compatibility alias for app.modules.ragforge.services.chunkers.fixed_size."""

from app._compat import alias_module
from app.modules.ragforge.services.chunkers import fixed_size as _implementation


alias_module(globals(), _implementation)
