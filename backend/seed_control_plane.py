"""Compatibility wrapper for ``python seed_control_plane.py``.

Prefer ``python -m scripts.seed_control_plane`` from the backend directory.
"""

from scripts import seed_control_plane


if __name__ == "__main__":
    raise SystemExit(seed_control_plane.main())
