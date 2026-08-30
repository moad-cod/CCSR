"""Compatibility alias for app.modules.ragforge.api.internal_pipeline."""

from app._compat import alias_module
from app.modules.ragforge.api import internal_pipeline as _implementation


alias_module(globals(), _implementation)
