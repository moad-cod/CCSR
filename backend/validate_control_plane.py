"""Compatibility wrapper for ``python validate_control_plane.py``.

Prefer ``python -m scripts.validate_control_plane`` from the backend directory.
"""

from scripts import validate_control_plane


if __name__ == "__main__":
    raise SystemExit(validate_control_plane.main())
