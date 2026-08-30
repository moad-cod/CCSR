"""Compatibility alias for app.platform.organizations.api."""

from app._compat import alias_module
from app.platform.organizations import api as _implementation


alias_module(globals(), _implementation)
