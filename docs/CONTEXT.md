# Documentation context

Documentation explains current behavior or an explicitly labelled target; it
does not define runtime state.

- `architecture/` describes implemented RAG control-plane and lifecycle design.
- `research/` contains the current RAG evaluation framework.
- `plans/` is historical/planning material and is not authoritative over code.
- `reports/` contains point-in-time reviews.
- `map/` is the concise, source-linked System Map for change impact.

When implementation and prose disagree, source code and Alembic migrations win.
Correct the map rather than copying implementation detail into multiple files.
