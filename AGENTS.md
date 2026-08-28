# Repository routing

Start with [`CONTEXT.md`](CONTEXT.md) for product identity, current boundaries,
and source-of-truth rules.

- Backend work: read [`backend/CONTEXT.md`](backend/CONTEXT.md).
- Frontend work: read [`frontend/CONTEXT.md`](frontend/CONTEXT.md).
- Architecture documentation: read [`docs/CONTEXT.md`](docs/CONTEXT.md).
- Change-impact questions: use the verified cards under [`docs/map/`](docs/map/).

Keep this file as a routing catalog. Put architecture detail in the nearest
`CONTEXT.md` and implementation facts in source code.

## Graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code or architecture documentation, run `graphify update .`
  to keep the graph current.
