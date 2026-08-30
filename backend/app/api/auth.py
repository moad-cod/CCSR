"""Compatibility alias for app.platform.accounts.api."""

from app._compat import alias_module
from app.platform.accounts import api as _implementation


alias_module(globals(), _implementation)
