# Platform ownership

This package owns cross-product identity and tenancy capabilities.

- access/ owns authentication dependencies, durable sessions, token handling,
  and default-deny organization/project policies.
- accounts/ owns user accounts, global member/admin roles, session management,
  and their API.
- organizations/ owns organizations, memberships, invitations, roles, and their
  API.
- capabilities/ owns capability definitions, the in-process registry, and
  project/account lifecycle contracts. Product modules implement those hooks;
  the application composition root registers them.
- execution/ owns durable workflow definitions and generic runs plus the
  execution gateway and engine adapters. Module-owned workflow registrations
  supply schemas and handlers; the browser never selects infrastructure.
- quotas/ owns account policies, atomic reservations, and usage finalization.
- artifacts/ owns shared metadata while object bodies remain in MinIO.
- audit/ owns append-only, redacted administrative events.

Legacy imports under app.core, app.api, app.models, and app.repositories are
compatibility aliases. New platform code should import from app.platform.
Routes, payloads, database tables, and environment variables remain externally
stable during this extraction.
