# Repository GUI Evaluation Report Prompt

## Mission

Interrogate the repository at `{{REPOSITORY_ROOT}}` and extract how it uses PyQt6, including architecture, styling, layout systems, widget inventories, interactions, dialogs, menus, graphics scenes, custom painting, model-view patterns, threading, packaging, and any distinctive implementation patterns.

The final response must preserve the technical essence of the repository while anonymizing product identity, domain vocabulary, code identifiers, and business-specific language.

## Mandatory Anonymization Rules

1. Keep real `PyQt6` API names, Qt class names, signal/slot concepts, layout patterns, stylesheet properties, and technical behavior.
2. Do not reveal real repository names, organization names, product names, file names, class names, function names, variable names, string literals, asset names, or domain-specific nouns.
3. Replace all identifying names with silly placeholder names. Examples:
   - Repository: `Project Marshmallow Observatory`
   - Package: `sparkle_pantry`
   - File: `pancake_control_room.py`
   - Class: `CaptainWidgetCastle`
   - Function: `deploy_snack_window()`
   - Variable: `wobble_counter`
   - Setting key: `ui.confetti_density`
4. Preserve structure and relationships even after renaming. If a class owns a dialog, keep that relationship, just anonymize both names.
5. Replace identifying textual copy with invented equivalents that preserve tone and function. Example: a real button label becomes something like `Launch Noodle Drawer`.
6. Keep visual values that matter technically, such as color hex values, spacing scales, border radii, font families, animation durations, widget dimensions, or palette roles, unless those values are clearly brand identifiers.
7. Do not emit a reversible real-to-fake mapping table.

## Investigation Scope

Inspect the repository for all of the following:

1. Imports from `PyQt6.QtWidgets`, `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtSvg`, `PyQt6.QtOpenGL`, `PyQt6.QtMultimedia`, and other PyQt6 modules.
2. Subclasses of major Qt surfaces such as `QApplication`, `QMainWindow`, `QWidget`, `QDialog`, `QDockWidget`, `QGraphicsView`, `QGraphicsScene`, `QAbstractItemModel`, `QStyledItemDelegate`, and custom `QObject` helpers.
3. Use of layouts, splitters, tab widgets, stacked widgets, toolboxes, scroll areas, dock systems, toolbars, menus, status bars, and custom chrome.
4. Styling systems including QSS, palettes, fonts, icons, effects, theme tokens, dynamic theme switching, and visual state changes.
5. Interaction systems including signals/slots, event filters, drag and drop, keyboard shortcuts, mouse gestures, context menus, flyouts, popovers, drawers, wizards, and dummy/demo interactions.
6. Graphics-heavy patterns such as `QGraphicsProxyWidget`, custom painting, `paintEvent`, custom `QGraphicsItem` subclasses, animation/effects, and scene composition.
7. Model-view patterns including table/tree/list models, delegates, proxy models, parameter editors, inspectors, property panes, and state synchronization.
8. Runtime architecture including document/state models, command flows, undo/redo, background threads, timers, workers, or state machines.
9. Packaging/runtime setup such as launch scripts, environment handling, system package assumptions, or desktop integration relevant to PyQt6 delivery.
10. Unique or exotic implementations that would teach another agent something non-obvious about how the repository exploits PyQt6.

## Interrogation Procedure

1. Identify the top-level shell and major windows.
2. Enumerate every meaningful PyQt6 surface and group them by role.
3. Trace where styling values come from and how they propagate.
4. Trace how user actions mutate application state.
5. Note any custom widgets, painters, proxy widgets, or scene items.
6. Note any overlays, dialogs, flyouts, drawers, wizards, inspectors, or nested workspaces.
7. Note any places where PyQt6 is being stretched in distinctive or unusual ways.
8. Summarize the transferable patterns another AI agent could reuse in a different codebase.

## Required Output Structure

### 1. Executive Summary

- Explain the overall PyQt6 application shape in 1-2 short paragraphs.
- Name the anonymized shell pattern and the main interaction style.

### 2. Anonymized Surface Inventory

Provide a table with these columns:

| Placeholder Surface | Real Qt Types | Purpose | Complexity | Notes |
| --- | --- | --- | --- | --- |

### 3. Styling and Theming Report

Describe:

- Palette, color, and contrast strategy.
- Typography strategy.
- Shape language such as radii, borders, shadows, separators, and chrome.
- QSS, palette, or token systems.
- Dynamic styling behaviors such as hover, focus, checked, disabled, loading, success, or error states.

### 4. Interaction and Layout Report

Describe:

- Main navigation patterns.
- Dialogs, flyouts, context menus, drawers, and transient surfaces.
- Forms, toggles, sliders, tables, trees, inspectors, and other control-heavy regions.
- Canvas/scene/graphics behavior if present.
- Selection, mutation, and synchronization flows.

### 5. PyQt6 Usage Breakdown

Provide grouped bullets for:

- Qt Widgets usage.
- Qt Core usage.
- Qt Gui usage.
- Graphics View / custom painting usage.
- Model/View usage.
- Threading / timers / workers.
- Packaging or runtime environment concerns.

### 6. Unique Implementations Worth Reusing

List the most distinctive implementation patterns. For each one include:

- Placeholder name.
- What it technically does.
- Why it is interesting.
- Which PyQt6 surfaces it relies on.
- What another repository could learn from it.

### 7. Transferable Design Language

Summarize the repository's reusable GUI style in neutral terms so another AI agent could recreate the feel without copying product identity.

### 8. Risks, Gaps, and Follow-Up Questions

List:

- Any incomplete areas in the repository.
- Any runtime assumptions that could trip up reproduction.
- Any follow-up questions needed to reproduce the same PyQt6 techniques elsewhere.

## Output Quality Bar

- Prefer specific technical observations over vague summaries.
- Preserve true PyQt6 mechanics.
- Anonymize anything product-identifying.
- Use silly placeholder names consistently enough to stay readable.
- Focus on reusable implementation patterns, not just widget counts.
