"""Compatibility alias for app.platform.organizations.model."""

from app._compat import alias_module
from app.platform.organizations import model as _implementation


alias_module(globals(), _implementation)
