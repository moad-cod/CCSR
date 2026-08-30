"""Compatibility alias for app.modules.ragforge.services.pipeline_artifacts."""

from app._compat import alias_module
from app.modules.ragforge.services import pipeline_artifacts as _implementation


alias_module(globals(), _implementation)
