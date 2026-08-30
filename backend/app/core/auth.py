"""Compatibility alias for app.platform.access.authentication."""

from app._compat import alias_module
from app.platform.access import authentication as _implementation


alias_module(globals(), _implementation)
