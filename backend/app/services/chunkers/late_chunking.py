"""Compatibility alias for app.modules.ragforge.services.chunkers.late_chunking."""

from app._compat import alias_module
from app.modules.ragforge.services.chunkers import late_chunking as _implementation


alias_module(globals(), _implementation)
