"""Append-only administrative audit events."""

from app.platform.audit.repository import record_audit_event

__all__ = ["record_audit_event"]
