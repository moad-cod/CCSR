"""Helpers for preserving import compatibility during ownership extraction."""

from types import ModuleType
import sys
from typing import Any


def alias_module(namespace: dict[str, Any], implementation: ModuleType) -> None:
    """Expose the implementation through the legacy module being loaded."""

    legacy_name = namespace["__name__"]
    namespace.update(
        {
            name: value
            for name, value in vars(implementation).items()
            if not (name.startswith("__") and name.endswith("__"))
        }
    )
    namespace["__all__"] = [
        name for name in vars(implementation) if not name.startswith("_")
    ]
    sys.modules[legacy_name] = implementation
