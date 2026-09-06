"""Redaction and stable public errors for durable control-plane records."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


SENSITIVE_KEY_PARTS = ("password", "secret", "token", "credential", "authorization", "api_key")


def sanitize_details(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): (
                "[redacted]"
                if any(part in str(key).lower() for part in SENSITIVE_KEY_PARTS)
                else sanitize_details(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [sanitize_details(item) for item in value]
    if isinstance(value, str):
        return value[:512]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)[:512]


def safe_execution_error(message: str | None) -> tuple[str, str]:
    normalized = (message or "").lower()
    if "timeout" in normalized or "timed out" in normalized:
        return "execution_timeout", "The workflow exceeded its allowed runtime."
    if "rate limit" in normalized or "quota" in normalized or "too many requests" in normalized:
        return "provider_unavailable", "A required provider is temporarily unavailable."
    if "no indexable" in normalized or "invalid input" in normalized:
        return "input_not_processable", "The workflow could not process the supplied input."
    if "orchestration" in normalized or "execution engine" in normalized or "broker" in normalized:
        return "dispatch_failed", "The execution engine could not start the workflow."
    return "workflow_failed", "The workflow could not be completed."
