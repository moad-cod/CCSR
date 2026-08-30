"""Compatibility alias for app.modules.ragforge.models.document_version."""

from app._compat import alias_module
from app.modules.ragforge.models import document_version as _implementation


alias_module(globals(), _implementation)
