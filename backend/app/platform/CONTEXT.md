# Platform ownership

This package owns cross-product identity and tenancy capabilities.

- access/ owns authentication dependencies and token handling.
- accounts/ owns user accounts and their API.
- organizations/ owns organizations, memberships, roles, and their API.
- capabilities/ owns capability definitions, the in-process registry, and
  project/account lifecycle contracts. Product modules implement those hooks;
  the application composition root registers them.

Legacy imports under app.core, app.api, app.models, and app.repositories are
compatibility aliases. New platform code should import from app.platform.
Routes, payloads, database tables, and environment variables remain externally
stable during this extraction.
