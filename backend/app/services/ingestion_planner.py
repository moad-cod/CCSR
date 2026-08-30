"""Compatibility alias for app.modules.ragforge.services.ingestion_planner."""

from app._compat import alias_module
from app.modules.ragforge.services import ingestion_planner as _implementation


alias_module(globals(), _implementation)
