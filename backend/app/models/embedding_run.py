"""Compatibility alias for app.modules.ragforge.models.embedding_run."""

from app._compat import alias_module
from app.modules.ragforge.models import embedding_run as _implementation


alias_module(globals(), _implementation)
