# Publication ownership

This package owns publication drafts, public slugs, selected findings and
artifacts, and immutable revision snapshots. Private and draft records require
normal project authorization. Visitor routes read only a snapshot belonging to
a publication whose current state is `public`.

Publishing copies a deliberately limited, public-safe projection. It never
exposes run inputs, errors, source documents, credentials, creator identifiers,
or private findings and artifacts. Unpublishing hides the snapshot without
deleting its revision history.
