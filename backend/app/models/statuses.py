"""Compatibility alias for app.modules.ragforge.models.statuses."""

from app._compat import alias_module
from app.modules.ragforge.models import statuses as _implementation


alias_module(globals(), _implementation)
