"""Compatibility alias for app.modules.ragforge.models.document."""

from app._compat import alias_module
from app.modules.ragforge.models import document as _implementation


alias_module(globals(), _implementation)
