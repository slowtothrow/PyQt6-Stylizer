# Studio Document Schema

The first milestone keeps the canonical state in a pure-Python document model so the GUI is a projection of the document rather than the other way around.

## Top-level fields

- `schema_version`: integer for explicit migrations.
- `title`: document title shown in the shell.
- `experience_level`: `basic`, `intermediate`, or `advanced`.
- `nodes`: recursive scene/widget nodes with stable ids.
- `theme_tokens`: symbolic visual tokens such as palette, radius, or type scale values.
- `interactions`: serializable dummy interactions that can later drive `QStateMachine` runtimes.
- `workspace_state`: shell-specific state such as dock layout snapshots and recent selections.
- `meta`: forward-compatible metadata for exports and future tooling.

## Source of truth

`StudioDocument` is authoritative. The live `QGraphicsScene`, any embedded `QWidget` preview trees, and dock layout state are runtime projections that should be reconstructible from the document plus explicit workspace metadata.

## Immediate extension points

1. Add validated property descriptors to nodes so inspectors stop relying on placeholder group names.
2. Introduce command objects that mutate `StudioDocument` and later plug into `QUndoStack`.
3. Add export bundle writers that combine document JSON with preview images and an AI-facing handoff narrative.
