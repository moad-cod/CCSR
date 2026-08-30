"""Compatibility alias for app.modules.ragforge.services.indexer."""

from app._compat import alias_module
from app.modules.ragforge.services import indexer as _implementation


alias_module(globals(), _implementation)
