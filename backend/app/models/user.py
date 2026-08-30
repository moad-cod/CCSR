"""Compatibility alias for app.platform.accounts.model."""

from app._compat import alias_module
from app.platform.accounts import model as _implementation


alias_module(globals(), _implementation)
