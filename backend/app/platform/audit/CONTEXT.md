# Platform audit context

Audit events are append-only PostgreSQL records for administrative actions and
quota bypasses. Details pass through the shared redactor before persistence.
Only platform admins may read the audit stream.

Never store credentials, bearer tokens, raw exception traces, or artifact
contents in audit details.
