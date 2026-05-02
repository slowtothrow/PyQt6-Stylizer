# Public UI Research Reference

All gallery boards in PyQt6 Stylizer are original reinterpretations informed by the public
GitHub repositories listed here. No upstream code, assets, or layouts are reproduced
verbatim. Names and identifying details in the studio UI are intentionally generic.

---

## Source Repositories

| Repo | Why It Matters |
|------|---------------|
| `zhiyiYo/PyQt-Fluent-Widgets` ★7800+ | Gold-standard Fluent-design widget ecosystem. Navigation rails, settings cards, command bars, info bars. |
| `5yutan5/PyQtDarkTheme` ★740+ | Clean dark/light palette baseline for Fusion applications without heavy custom painting. |
| `pyapp-kit/superqt` ★280+ | Missing utility widgets: range sliders, colormap pickers, collapsible panels, enum combos. |
| `pyqtgraph/pyqtgraph` ★4300+ | High-performance scientific plotting, parameter trees, and live-data docking patterns. |
| `Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6` ★3000+ | Definitive dark app-shell reference. Custom chrome, side rail, stacked pages, slide drawers. |
| `zhiyiYo/PyQt-Frameless-Window` ★740+ | Cross-platform frameless window toolkit. Drag region, resize grip, OS-native shadow. |

---

## Gallery Board → Source Mapping

| Preset ID | Display Name | Primary Sources |
|-----------|--------------|----------------|
| `showcase-playground` | UI Showcase Playground | All 5 major repos |
| `theme-tuning-board` | Theme Tuning Board | PyQtDarkTheme |
| `fluent-navigation-gallery` | Navigation Gallery | PyQt-Fluent-Widgets |
| `micro-widget-lab` | Micro Widget Lab | superqt |
| `plot-control-workbench` | Plot Control Workbench | pyqtgraph |
| `dracula-app-shell` | Dark Shell Board | PyDracula |
| `command-bridge-lab` | Command Bridge Lab | PyQt-Fluent-Widgets, superqt |
| `frameless-operator-shell` | Frameless Operator Shell | PyQt-Frameless-Window, PyDracula |
| `notification-decision-deck` | Notification Decision Deck | PyQt-Fluent-Widgets |
| `auth-journey-studio` | Auth Journey Studio | PyQt-Fluent-Widgets, PyQt-Frameless-Window |
| `downloader-control-room` | Downloader Control Room | PyDracula |
| `creator-timeline-bay` | Creator Timeline Bay | superqt, pyqtgraph |
| `chat-ops-console` | Chat Ops Console | PyDracula, PyQt-Fluent-Widgets |
| `telemetry-mission-board` | Telemetry Mission Board | pyqtgraph |
| `data-entry-pattern-atlas` | Data Entry Pattern Atlas | PyQt-Fluent-Widgets |
| `dense-admin-shell` | Dense Admin Shell | PyDracula, pyqtgraph |
| `palette-motion-board` | Palette + Motion Board | PyQtDarkTheme, superqt |
| `media-review-studio` | Media Review Studio | pyqtgraph, PyQt-Fluent-Widgets |
| `inspector-workshop` | Inspector Workshop | superqt, pyqtgraph |
| `signal-flow-theater` | Signal Flow Theater | PyQt-Fluent-Widgets |
| `utility-grid-forge` | Utility Grid Forge | superqt, PyQtDarkTheme |
| `research-atlas-studio` | Research Atlas Studio | pyqtgraph, PyQt-Frameless-Window |

---

## Notes
- Preset names and canvas descriptions are original and do not reflect upstream project
  naming conventions.
- Source references are stored in `meta.source_references` on each `StudioDocument` and
  used only to acknowledge research provenance in tooltips and this document.
- The `--list-presets` CLI flag lists all boards with their summaries.
