"""Stable URL slug helpers for research and publication records."""

from __future__ import annotations

import re


_NON_SLUG = re.compile(r"[^a-z0-9]+")


def normalize_slug(value: str) -> str:
    slug = _NON_SLUG.sub("-", value.strip().lower()).strip("-")
    if not slug:
        raise ValueError("A slug must contain at least one letter or number")
    return slug[:120].rstrip("-")
