from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from ..document.schema import InteractionDefinition, StudioDocument, StudioNode, ThemeToken, make_stable_id
from ..models import ExperienceLevel


def _scene_card(
    label: str,
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    fill: str,
    description: str,
    kind: str = "scene-card",
) -> StudioNode:
    return StudioNode(
        node_id=make_stable_id("card"),
        node_type="scene-card",
        label=label,
        properties={
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "fill": fill,
            "description": description,
            "kind": kind,
        },
    )


def _widget_preview(
    label: str,
    *,
    x: float,
    y: float,
    description: str,
    cta_label: str,
    kind: str,
    width: float = 360.0,
    height: float = 260.0,
) -> StudioNode:
    return StudioNode(
        node_id=make_stable_id("widget"),
        node_type="widget-preview",
        label=label,
        properties={
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "description": description,
            "cta_label": cta_label,
            "kind": kind,
        },
    )


def _theme_tokens(*tokens: tuple[str, object, str]) -> list[ThemeToken]:
    return [ThemeToken(name=name, value=value, category=category) for name, value, category in tokens]


def _preset_meta(preset_id: str, source_references: tuple[str, ...], tags: tuple[str, ...]) -> dict[str, object]:
    return {
        "preset_id": preset_id,
        "source_references": list(source_references),
        "tags": list(tags),
        "provenance": "original reinterpretation informed by public repository research",
    }


@dataclass(frozen=True, slots=True)
class PresetDefinition:
    preset_id: str
    display_name: str
    summary: str
    document_factory: Callable[[], StudioDocument] = field(repr=False)
    source_references: tuple[str, ...] = ()

    def build_document(self) -> StudioDocument:
        document = self.document_factory()
        document.meta.setdefault("preset_id", self.preset_id)
        return document

    def tooltip(self) -> str:
        lines = [self.summary, "Double-click to load this example, then drag or tweak elements in the workspace."]
        if self.source_references:
            lines.append("Inspired by: " + ", ".join(self.source_references))
        return "\n".join(lines)


class PresetRegistry:
    def __init__(self, definitions: list[PresetDefinition], default_preset_id: str) -> None:
        self._definitions = definitions
        self._by_id = {definition.preset_id: definition for definition in definitions}
        self.default_preset_id = default_preset_id

    def definitions(self) -> list[PresetDefinition]:
        return list(self._definitions)

    def definition_for(self, preset_id: str | None) -> PresetDefinition | None:
        if preset_id is None:
            return None
        return self._by_id.get(preset_id)

    def instantiate(self, preset_id: str) -> StudioDocument | None:
        definition = self.definition_for(preset_id)
        if definition is None:
            return None
        return definition.build_document()

    @classmethod
    def default(cls) -> "PresetRegistry":
        return cls(
            definitions=[
                PresetDefinition(
                    preset_id="blank-canvas",
                    display_name="Blank Canvas",
                    summary="An empty canvas to start from scratch. Drag elements from 'Add to Canvas', style them in Properties, then export to Python code.",
                    document_factory=_blank_canvas_document,
                ),
                PresetDefinition(
                    preset_id="showcase-playground",
                    display_name="UI Showcase Playground",
                    summary="One giant canvas packed with simple controls, dense nested shells, flyouts, dialogs, tables, effects, and styling studies.",
                    document_factory=_showcase_playground_document,
                    source_references=(
                        "zhiyiYo/PyQt-Fluent-Widgets",
                        "pyqtgraph/pyqtgraph",
                        "pyapp-kit/superqt",
                        "5yutan5/PyQtDarkTheme",
                        "Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6",
                    ),
                ),
            ],
            default_preset_id="blank-canvas",
        )


def _blank_canvas_document() -> StudioDocument:
    """A completely empty canvas — ideal starting point for beginners."""
    return StudioDocument(
        title="Blank Canvas",
        experience_level=ExperienceLevel.BASIC.value,
        nodes=[],
        theme_tokens=[
            ThemeToken(name="palette.surface", value="#f8f3e6", category="palette"),
            ThemeToken(name="palette.accent", value="#4a90d9", category="palette"),
            ThemeToken(name="radius.card", value=8, category="shape"),
        ],
        interactions=[],
        workspace_state={"active_panel": "library"},
        meta={
            "preset_id": "blank-canvas",
            "hint": "Drag any element from 'Add to Canvas', then select it and edit in Properties.",
        },
    )


def _showcase_playground_document() -> StudioDocument:
    overview = _scene_card(
        "Showcase Map",
        x=40.0,
        y=40.0,
        width=340.0,
        height=165.0,
        fill="#f8f3e6",
        description="This canvas is the starting point now: simple controls, nested admin shells, menus, dialogs, scroll regions, and effects all live together for direct comparison.",
        kind="showcase-map",
    )
    elegant = _scene_card(
        "Simple + Elegant Patterns",
        x=40.0,
        y=235.0,
        width=340.0,
        height=185.0,
        fill="#e2efe6",
        description="Keep the restrained solutions visible too: tight copy hierarchy, one or two strong actions, and minimal chrome that still reads clearly.",
        kind="elegant-patterns",
    )
    dense = _scene_card(
        "Dense + Nested Patterns",
        x=40.0,
        y=455.0,
        width=340.0,
        height=205.0,
        fill="#e7edf7",
        description="Use these alongside the heavy widget cards to compare when splitters, tabs, trees, and toolboxes feel powerful versus overwhelming.",
        kind="dense-patterns",
    )
    remix = _scene_card(
        "Duplicate + Remix",
        x=40.0,
        y=695.0,
        width=340.0,
        height=165.0,
        fill="#f1e5ef",
        description="Select any example, duplicate it, then edit values in Properties or the JSON block pane to fork new directions without losing the baseline.",
        kind="duplicate-remix",
    )

    simple_controls = _widget_preview(
        "Simple Controls",
        x=430.0,
        y=40.0,
        width=420.0,
        height=340.0,
        description="A compact baseline card with buttons, one toggle, and one visible accent choice for the cleanest interaction model.",
        cta_label="Apply Accent",
        kind="simple-controls",
    )
    font_color = _widget_preview(
        "Typography + Color Lab",
        x=890.0,
        y=40.0,
        width=430.0,
        height=360.0,
        description="Live font, size, text-tone, and surface controls so typography and palette decisions stay inspectable instead of abstract.",
        cta_label="Apply Type",
        kind="font-color-lab",
    )
    effects = _widget_preview(
        "Effects Lab",
        x=1360.0,
        y=40.0,
        width=430.0,
        height=360.0,
        description="Blur, opacity, and accent comparisons for subtle polish decisions that are hard to judge in isolation.",
        cta_label="Tune Effects",
        kind="effects-lab",
    )
    choices = _widget_preview(
        "Choice Matrix",
        x=430.0,
        y=430.0,
        width=420.0,
        height=380.0,
        description="A checkbox and radio-button cluster for settings-heavy applications where grouped decisions need to remain legible.",
        cta_label="Lock In",
        kind="choice-matrix",
    )
    sliders = _widget_preview(
        "Slider + Dial Bench",
        x=890.0,
        y=430.0,
        width=420.0,
        height=360.0,
        description="Sliders, scrollbars, dials, and progress indicators wired together so motion density can be judged side by side.",
        cta_label="Sync Controls",
        kind="slider-lab",
    )
    flyouts = _widget_preview(
        "Flyout + Menu Lab",
        x=1350.0,
        y=430.0,
        width=500.0,
        height=340.0,
        description="Instant popups, nested menus, and split-button behavior for command-dense surfaces that still need to feel obvious.",
        cta_label="Open Flyout",
        kind="flyout-lab",
    )
    dialogs = _widget_preview(
        "Dialog Launcher",
        x=1890.0,
        y=430.0,
        width=480.0,
        height=340.0,
        description="A launch surface for testing modeless dialog stacks, tabbed forms, confirmation buttons, and message language.",
        cta_label="Open Dialog",
        kind="dialog-lab",
    )
    scrolling = _widget_preview(
        "Scrollable Utility Stack",
        x=430.0,
        y=840.0,
        width=430.0,
        height=440.0,
        description="A scroll area full of mini cards so nested utility panels, overflow behavior, and scrollbar treatment can be judged directly.",
        cta_label="Inspect Stack",
        kind="scroll-gallery",
    )
    navigation = _widget_preview(
        "Navigation Workspace",
        x=900.0,
        y=840.0,
        width=600.0,
        height=440.0,
        description="A persistent rail plus stacked pages, including nested tabs inside settings, for shell-level interaction exploration.",
        cta_label="Switch Page",
        kind="navigation-workspace",
    )
    inspector = _widget_preview(
        "Inspector Tree",
        x=1540.0,
        y=840.0,
        width=600.0,
        height=440.0,
        description="A splitter-based tree inspector with tabs and notes to simulate property-heavy tools and layered metadata views.",
        cta_label="Inspect Node",
        kind="inspector-tree",
    )
    data_console = _widget_preview(
        "Data Table + Console",
        x=430.0,
        y=1330.0,
        width=600.0,
        height=440.0,
        description="Toolbar actions, dense tables, and a running log for complex GUI-heavy applications that mix operations with live results.",
        cta_label="Run Query",
        kind="data-table-console",
    )
    workspace_shell = _widget_preview(
        "Nested Workspace Shell",
        x=1070.0,
        y=1330.0,
        width=1040.0,
        height=680.0,
        description="The heaviest example on the canvas: tabs, splitters, trees, tables, console output, and a toolbox monitor so nested complexity is easy to inspect and clone.",
        cta_label="Open Shell",
        kind="workspace-shell",
    )

    return StudioDocument(
        title="UI Showcase Playground",
        experience_level=ExperienceLevel.ADVANCED.value,
        nodes=[
            overview,
            elegant,
            dense,
            remix,
            simple_controls,
            font_color,
            effects,
            choices,
            sliders,
            flyouts,
            dialogs,
            scrolling,
            navigation,
            inspector,
            data_console,
            workspace_shell,
        ],
        theme_tokens=_theme_tokens(
            ("palette.surface", "#fffdf8", "palette"),
            ("palette.accent.primary", "#223647", "palette"),
            ("palette.accent.secondary", "#7a375f", "palette"),
            ("type.scale.display", 20, "type"),
            ("radius.card", 16, "shape"),
            ("effect.shadow.blur", 24, "effect"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="click",
                target_node_id=flyouts.node_id,
                action="show-command-flyout",
                payload={"patterns": ["toolbar", "context-menu", "split-button"]},
            ),
            InteractionDefinition(
                trigger="click",
                target_node_id=dialogs.node_id,
                action="open-review-dialog",
                payload={"modalities": ["modeless", "tabbed-form"]},
            ),
            InteractionDefinition(
                trigger="change",
                target_node_id=effects.node_id,
                action="tune-effects",
                payload={"targets": ["shadow", "opacity", "accent"]},
            ),
            InteractionDefinition(
                trigger="select",
                target_node_id=workspace_shell.node_id,
                action="swap-nested-pane",
                payload={"zones": ["author", "monitor"]},
            ),
        ],
        workspace_state={"active_panel": "inspector", "recommended_zoom": 0.54},
        meta=_preset_meta(
            "showcase-playground",
            (
                "zhiyiYo/PyQt-Fluent-Widgets",
                "pyqtgraph/pyqtgraph",
                "pyapp-kit/superqt",
                "5yutan5/PyQtDarkTheme",
                "Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6",
            ),
            ("showcase", "nested", "dialogs", "menus", "controls"),
        ),
    )


def _starter_board_document() -> StudioDocument:
    mood_card = _scene_card(
        "Mood Board Card",
        x=60.0,
        y=60.0,
        width=280.0,
        height=180.0,
        fill="#f8f3e6",
        description="Use this as the loose visual anchor for copy tone, material hints, and composition notes.",
    )
    prototype = _widget_preview(
        "Embedded Prototype",
        x=380.0,
        y=90.0,
        description="A real QWidget host for immediate button, label, and spacing experiments inside the graphics scene.",
        cta_label="Trigger Dummy State",
        kind="button-card",
    )
    swatch = _scene_card(
        "Accent Swatch",
        x=80.0,
        y=300.0,
        width=220.0,
        height=130.0,
        fill="#d8e4f2",
        description="Keep alternate accent, border, and surface pairings visible while iterating on the main composition.",
        kind="palette-swatch",
    )
    copy_tester = _widget_preview(
        "Copy Tone Tester",
        x=380.0,
        y=330.0,
        description="A second widget card dedicated to microcopy, call-to-action wording, and state copy experiments.",
        cta_label="Swap Tone",
        kind="copy-tester",
    )

    return StudioDocument(
        title="Starter Mood Board",
        experience_level=ExperienceLevel.BASIC.value,
        nodes=[mood_card, prototype, swatch, copy_tester],
        theme_tokens=_theme_tokens(
            ("palette.surface", "#f8f3e6", "palette"),
            ("palette.accent", "#31485e", "palette"),
            ("radius.card", 16, "shape"),
            ("type.scale.headline", 20, "type"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="hover",
                target_node_id=prototype.node_id,
                action="opacity-pulse",
                payload={"duration_ms": 180},
            ),
            InteractionDefinition(
                trigger="click",
                target_node_id=copy_tester.node_id,
                action="cycle-copy-tone",
                payload={"states": ["playful", "neutral", "urgent"]},
            ),
        ],
        workspace_state={"active_panel": "inspector", "recommended_zoom": 0.92},
        meta=_preset_meta("starter-board", (), ("baseline", "mixed-surface", "basic")),
    )


def _theme_tuning_document() -> StudioDocument:
    theme_switcher = _widget_preview(
        "Theme Switcher",
        x=60.0,
        y=80.0,
        description="Compare dark, light, and auto-theme framing while keeping the same structural shell in view.",
        cta_label="Toggle Theme",
        kind="theme-switcher",
    )
    accent_pairs = _scene_card(
        "Accent Pairings",
        x=430.0,
        y=80.0,
        width=300.0,
        height=150.0,
        fill="#2b313a",
        description="Track how primary accents behave across surface, icon, and border roles before committing to a palette family.",
        kind="theme-pairing",
    )
    corners = _scene_card(
        "Sharp vs Rounded",
        x=770.0,
        y=80.0,
        width=260.0,
        height=150.0,
        fill="#edf1f6",
        description="Use this card to compare rounded and sharp treatments, especially for toolbars, side panels, and cards.",
        kind="shape-study",
    )
    palette_probe = _widget_preview(
        "Palette Probe",
        x=60.0,
        y=320.0,
        description="A dedicated host for testing palette-driven controls against both stylesheet and QPalette variations.",
        cta_label="Sample Palette",
        kind="palette-probe",
    )
    standard_icons = _widget_preview(
        "Standard Icon Surface",
        x=500.0,
        y=320.0,
        description="Measure how iconography changes under theme swaps, overridden standard icons, and accent shifts.",
        cta_label="Rotate Accent",
        kind="icon-surface",
    )

    return StudioDocument(
        title="Theme Tuning Board",
        experience_level=ExperienceLevel.BASIC.value,
        nodes=[theme_switcher, accent_pairs, corners, palette_probe, standard_icons],
        theme_tokens=_theme_tokens(
            ("theme.mode", "auto", "theme"),
            ("theme.primary", "#4f8fba", "palette"),
            ("shape.corner", "rounded", "shape"),
            ("icon.style", "standard-overridden", "icon"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="change",
                target_node_id=theme_switcher.node_id,
                action="swap-theme",
                payload={"modes": ["dark", "light", "auto"]},
            ),
            InteractionDefinition(
                trigger="click",
                target_node_id=standard_icons.node_id,
                action="rotate-primary-accent",
                payload={"source": "5yutan5/PyQtDarkTheme"},
            ),
        ],
        workspace_state={"active_panel": "tokens", "recommended_zoom": 0.9},
        meta=_preset_meta(
            "theme-tuning-board",
            ("5yutan5/PyQtDarkTheme",),
            ("theme", "palette", "basic"),
        ),
    )


def _fluent_navigation_document() -> StudioDocument:
    nav_rail = _widget_preview(
        "Primary Navigation Rail",
        x=60.0,
        y=70.0,
        description="A left-side navigation surface inspired by Fluent-style grouped destinations and settings anchors.",
        cta_label="Switch Section",
        kind="navigation-rail",
    )
    search_strip = _widget_preview(
        "Search + Action Strip",
        x=360.0,
        y=70.0,
        description="Blend a search entry with quick actions so command density can rise without collapsing the overall shell.",
        cta_label="Run Command",
        kind="search-strip",
    )
    settings_stack = _widget_preview(
        "Settings Card Stack",
        x=360.0,
        y=290.0,
        description="Use grouped cards to test copy density, row spacing, and mixed control weights inside a settings view.",
        cta_label="Flip Setting",
        kind="settings-stack",
    )
    status_ribbon = _scene_card(
        "Status Ribbon",
        x=930.0,
        y=80.0,
        width=300.0,
        height=140.0,
        fill="#e9f1fb",
        description="Keep alert, progress, and info-bar treatments visible while navigation changes elsewhere on the canvas.",
        kind="status-ribbon",
    )
    command_surface = _scene_card(
        "Command Surface",
        x=930.0,
        y=280.0,
        width=300.0,
        height=180.0,
        fill="#eff5ef",
        description="Reserve this zone for menus, flyouts, segmented controls, and other structured action clusters.",
        kind="command-surface",
    )

    return StudioDocument(
        title="Fluent Navigation Gallery",
        experience_level=ExperienceLevel.INTERMEDIATE.value,
        nodes=[nav_rail, search_strip, settings_stack, status_ribbon, command_surface],
        theme_tokens=_theme_tokens(
            ("palette.surface", "#f7f9fc", "palette"),
            ("palette.accent", "#0067c0", "palette"),
            ("radius.card", 18, "shape"),
            ("spacing.group", 14, "layout"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="click",
                target_node_id=nav_rail.node_id,
                action="switch-route",
                payload={"routes": ["home", "view", "settings"]},
            ),
            InteractionDefinition(
                trigger="submit",
                target_node_id=search_strip.node_id,
                action="show-command-flyout",
                payload={"source": "zhiyiYo/PyQt-Fluent-Widgets"},
            ),
        ],
        workspace_state={"active_panel": "interactions", "recommended_zoom": 0.84},
        meta=_preset_meta(
            "fluent-navigation-gallery",
            ("zhiyiYo/PyQt-Fluent-Widgets",),
            ("navigation", "settings", "intermediate"),
        ),
    )


def _micro_widget_lab_document() -> StudioDocument:
    slider_lab = _widget_preview(
        "Range Slider Lab",
        x=60.0,
        y=80.0,
        description="Experiment with single, double, and multi-handle slider patterns without leaving the main canvas.",
        cta_label="Shift Handles",
        kind="range-slider-lab",
    )
    search_inputs = _widget_preview(
        "Searchable Inputs",
        x=430.0,
        y=80.0,
        description="Compare searchable combo boxes, filtered lists, and compact picker layouts inside one utility card.",
        cta_label="Filter Items",
        kind="search-inputs",
    )
    colormap_bench = _widget_preview(
        "Colormap Bench",
        x=800.0,
        y=80.0,
        description="Use swatches, catalog pickers, and visible labels to decide how scientific controls should surface color intent.",
        cta_label="Swap Cmap",
        kind="colormap-bench",
    )
    collapsible_notes = _scene_card(
        "Collapsible Notes",
        x=90.0,
        y=340.0,
        width=280.0,
        height=170.0,
        fill="#eef0f7",
        description="Document what should stay collapsed by default and which utility surfaces should open up when users ask for more control.",
        kind="collapsible-notes",
    )
    quantity_probe = _scene_card(
        "Quantity + Unit Probe",
        x=430.0,
        y=340.0,
        width=300.0,
        height=170.0,
        fill="#edf5ee",
        description="Use this area to sketch how large numbers, unit pickers, and scale hints should co-exist without crowding.",
        kind="quantity-probe",
    )

    return StudioDocument(
        title="Micro Widget Lab",
        experience_level=ExperienceLevel.INTERMEDIATE.value,
        nodes=[slider_lab, search_inputs, colormap_bench, collapsible_notes, quantity_probe],
        theme_tokens=_theme_tokens(
            ("slider.bar", "#3b88fd", "palette"),
            ("slider.tick", "#8f8f8f", "palette"),
            ("picker.colormap", "viridis", "theme"),
            ("spacing.utility", 12, "layout"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="drag",
                target_node_id=slider_lab.node_id,
                action="update-range-labels",
                payload={"source": "pyapp-kit/superqt"},
            ),
            InteractionDefinition(
                trigger="select",
                target_node_id=colormap_bench.node_id,
                action="preview-colormap",
                payload={"catalog": ["viridis", "plasma", "magma"]},
            ),
        ],
        workspace_state={"active_panel": "inspector", "recommended_zoom": 0.88},
        meta=_preset_meta(
            "micro-widget-lab",
            ("pyapp-kit/superqt",),
            ("widgets", "controls", "intermediate"),
        ),
    )


def _plot_control_document() -> StudioDocument:
    plot_pane = _widget_preview(
        "Live Plot Pane",
        x=60.0,
        y=70.0,
        description="Treat this as the primary data view while tuning axes, contrast, update cadence, and annotation density.",
        cta_label="Inject Sample",
        kind="plot-pane",
    )
    parameter_tree = _widget_preview(
        "Parameter Tree",
        x=850.0,
        y=70.0,
        description="A control surface inspired by nested parameter trees, save/restore state flows, and incremental adjustments.",
        cta_label="Expand Groups",
        kind="parameter-tree",
    )
    dock_zones = _scene_card(
        "Dock Layout Zones",
        x=60.0,
        y=360.0,
        width=420.0,
        height=190.0,
        fill="#e9eef6",
        description="Sketch where docked consoles, plots, tables, and floating panels should land before committing to a real docking system.",
        kind="dock-zones",
    )
    gradient_notes = _scene_card(
        "Gradient + ROI Notes",
        x=520.0,
        y=360.0,
        width=280.0,
        height=190.0,
        fill="#f4efe5",
        description="Use this card to capture gradient, image-analysis, and region-of-interest affordances you may want later.",
        kind="gradient-notes",
    )
    interaction_matrix = _widget_preview(
        "Interaction Matrix",
        x=850.0,
        y=360.0,
        description="Reserve a second dense control card for run-on-change experiments, throttled updates, and parameter-linked actions.",
        cta_label="Run Update",
        kind="interaction-matrix",
    )

    return StudioDocument(
        title="Plot Control Workbench",
        experience_level=ExperienceLevel.ADVANCED.value,
        nodes=[plot_pane, parameter_tree, dock_zones, gradient_notes, interaction_matrix],
        theme_tokens=_theme_tokens(
            ("plot.background", "#10161d", "palette"),
            ("plot.curve.primary", "#08f7fe", "palette"),
            ("plot.curve.secondary", "#fe53bb", "palette"),
            ("parameter.compact", True, "layout"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="change",
                target_node_id=parameter_tree.node_id,
                action="reconfigure-plot",
                payload={"source": "pyqtgraph/pyqtgraph"},
            ),
            InteractionDefinition(
                trigger="action",
                target_node_id=interaction_matrix.node_id,
                action="save-restore-state",
                payload={"targets": [plot_pane.node_id, parameter_tree.node_id]},
            ),
        ],
        workspace_state={"active_panel": "outliner", "recommended_zoom": 0.82},
        meta=_preset_meta(
            "plot-control-workbench",
            ("pyqtgraph/pyqtgraph",),
            ("plotting", "analysis", "advanced"),
        ),
    )


def _dracula_shell_document() -> StudioDocument:
    left_rail = _widget_preview(
        "Collapsed Left Rail",
        x=60.0,
        y=60.0,
        description="A narrow branded rail for testing icon-only navigation, selection highlights, and progressive expansion.",
        cta_label="Expand Rail",
        kind="left-rail",
    )
    content_stack = _widget_preview(
        "Center Content Stack",
        x=320.0,
        y=60.0,
        description="A stacked central pane for home, widgets, and secondary pages with visible toolbar and card treatments.",
        cta_label="Switch Page",
        kind="content-stack",
    )
    settings_drawer = _widget_preview(
        "Auxiliary Settings Drawer",
        x=980.0,
        y=60.0,
        description="Use a side drawer to test extra controls, help text, and theme tuning without losing the main page context.",
        cta_label="Open Drawer",
        kind="settings-drawer",
    )
    table_treatment = _scene_card(
        "Table + Toolbar Treatment",
        x=360.0,
        y=360.0,
        width=420.0,
        height=180.0,
        fill="#2b2f38",
        description="Keep the grid, input, scrollbar, and button treatment visible together to test cohesive high-density theming.",
        kind="table-treatment",
    )
    titlebar_notes = _scene_card(
        "Titlebar Controls",
        x=840.0,
        y=360.0,
        width=300.0,
        height=180.0,
        fill="#394150",
        description="A note zone for custom window chrome, utility buttons, and top-right action affordances.",
        kind="titlebar-notes",
    )

    return StudioDocument(
        title="Dracula App Shell",
        experience_level=ExperienceLevel.ADVANCED.value,
        nodes=[left_rail, content_stack, settings_drawer, table_treatment, titlebar_notes],
        theme_tokens=_theme_tokens(
            ("palette.surface", "#282c34", "palette"),
            ("palette.accent.primary", "#bd93f9", "palette"),
            ("palette.accent.secondary", "#ff79c6", "palette"),
            ("chrome.custom_titlebar", True, "runtime"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="click",
                target_node_id=left_rail.node_id,
                action="toggle-menu-width",
                payload={"source": "Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6"},
            ),
            InteractionDefinition(
                trigger="click",
                target_node_id=settings_drawer.node_id,
                action="toggle-side-drawer",
                payload={"side": "right"},
            ),
        ],
        workspace_state={"active_panel": "history", "recommended_zoom": 0.8},
        meta=_preset_meta(
            "dracula-app-shell",
            ("Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6",),
            ("shell", "theme", "advanced"),
        ),
    )