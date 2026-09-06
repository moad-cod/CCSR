# Platform quota context

PostgreSQL is authoritative for per-account execution policies and usage.
Reservations are created in the same transaction as generic runs, serialized
by locking the account policy, and either finalized after execution starts or
released when dispatch fails before work begins. Platform-admin bypasses do not
consume quota and always create an audit event.

Authorization remains separate: passing quota checks never grants project or
workflow access. Redis must not become the usage ledger.
