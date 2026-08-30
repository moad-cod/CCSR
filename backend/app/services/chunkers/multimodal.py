"""Compatibility alias for app.modules.ragforge.services.chunkers.multimodal."""

from app._compat import alias_module
from app.modules.ragforge.services.chunkers import multimodal as _implementation


alias_module(globals(), _implementation)
