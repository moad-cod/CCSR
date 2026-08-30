"""Compatibility alias for app.platform.organizations.membership."""

from app._compat import alias_module
from app.platform.organizations import membership as _implementation


alias_module(globals(), _implementation)
