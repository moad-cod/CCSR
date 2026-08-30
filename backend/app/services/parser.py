"""Compatibility alias for app.modules.ragforge.services.parser."""

from app._compat import alias_module
from app.modules.ragforge.services import parser as _implementation


alias_module(globals(), _implementation)
