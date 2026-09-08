# Publication frontend ownership

This folder owns unauthenticated, read-only rendering of immutable publication
snapshots. It consumes only `/publications` visitor endpoints and must not infer
public content from authenticated project, run, source, or artifact APIs.

Draft editing remains in authenticated project screens when introduced. Keep
route files under `app/(public)/publications` thin.
