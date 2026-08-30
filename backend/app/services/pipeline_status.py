"""Compatibility alias for app.modules.ragforge.services.pipeline_status."""

from app._compat import alias_module
from app.modules.ragforge.services import pipeline_status as _implementation


alias_module(globals(), _implementation)
