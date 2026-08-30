"""Compatibility alias for app.modules.ragforge.api.ingest."""

from app._compat import alias_module
from app.modules.ragforge.api import ingest as _implementation


alias_module(globals(), _implementation)
