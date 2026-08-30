"""Compatibility alias for app.platform.organizations.repository."""

from app._compat import alias_module
from app.platform.organizations import repository as _implementation


alias_module(globals(), _implementation)
