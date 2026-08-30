"""Compatibility alias for app.modules.ragforge.repositories.document_versions."""

from app._compat import alias_module
from app.modules.ragforge.repositories import document_versions as _implementation


alias_module(globals(), _implementation)
