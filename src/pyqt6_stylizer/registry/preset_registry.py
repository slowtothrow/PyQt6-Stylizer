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
            lines.append(
                f"Anonymized public-research remix built from {len(self.source_references)} GitHub source repo"
                f"{'s' if len(self.source_references) != 1 else ''}."
            )
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
                    summary="A broad survey board spanning controls, shells, flyouts, dialogs, tables, effects, and teaching surfaces.",
                    document_factory=_showcase_playground_document,
                    source_references=(
                        "zhiyiYo/PyQt-Fluent-Widgets",
                        "pyqtgraph/pyqtgraph",
                        "pyapp-kit/superqt",
                        "5yutan5/PyQtDarkTheme",
                        "Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6",
                    ),
                ),
                PresetDefinition(
                    preset_id="starter-board",
                    display_name="Starter Mood Board",
                    summary="A light baseline for copy, accent, and embedded-widget experiments.",
                    document_factory=_starter_board_document,
                ),
                PresetDefinition(
                    preset_id="theme-tuning-board",
                    display_name="Theme Tuning Board",
                    summary="A compact palette, icon, and shape comparison surface for quick style decisions.",
                    document_factory=_theme_tuning_document,
                    source_references=("5yutan5/PyQtDarkTheme",),
                ),
                PresetDefinition(
                    preset_id="fluent-navigation-gallery",
                    display_name="Navigation Gallery",
                    summary="A navigation-first shell remix with grouped destinations, search, and settings cards.",
                    document_factory=_fluent_navigation_document,
                    source_references=("zhiyiYo/PyQt-Fluent-Widgets",),
                ),
                PresetDefinition(
                    preset_id="micro-widget-lab",
                    display_name="Micro Widget Lab",
                    summary="Smaller controls for slider, picker, and utility-density exploration.",
                    document_factory=_micro_widget_lab_document,
                    source_references=("pyapp-kit/superqt",),
                ),
                PresetDefinition(
                    preset_id="plot-control-workbench",
                    display_name="Plot Control Workbench",
                    summary="A data-tool board focused on plotting surfaces, parameter trees, and dockable thinking.",
                    document_factory=_plot_control_document,
                    source_references=("pyqtgraph/pyqtgraph",),
                ),
                PresetDefinition(
                    preset_id="dracula-app-shell",
                    display_name="Dark Shell Board",
                    summary="A high-contrast shell with left rail, content stack, and auxiliary settings drawer.",
                    document_factory=_dracula_shell_document,
                    source_references=("Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6",),
                ),
                PresetDefinition(
                    preset_id="command-bridge-lab",
                    display_name="Command Bridge Lab",
                    summary="A mission-control board for command palette, alerts, and quick action flows.",
                    document_factory=_command_bridge_document,
                    source_references=("zhiyiYo/PyQt-Fluent-Widgets", "pyapp-kit/superqt"),
                ),
                PresetDefinition(
                    preset_id="frameless-operator-shell",
                    display_name="Frameless Operator Shell",
                    summary="Custom-chrome shell studies for titlebar controls, side drawers, and route stacks.",
                    document_factory=_frameless_operator_document,
                    source_references=(
                        "zhiyiYo/PyQt-Frameless-Window",
                        "Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6",
                    ),
                ),
                PresetDefinition(
                    preset_id="notification-decision-deck",
                    display_name="Notification Decision Deck",
                    summary="Toast, banner, and confirmation patterns staged beside a compact review shell.",
                    document_factory=_notification_decision_document,
                    source_references=("zhiyiYo/PyQt-Fluent-Widgets",),
                ),
                PresetDefinition(
                    preset_id="auth-journey-studio",
                    display_name="Auth Journey Studio",
                    summary="Login, register, recovery, and trust-state surfaces arranged as a single flow board.",
                    document_factory=_auth_journey_document,
                    source_references=(
                        "zhiyiYo/PyQt-Fluent-Widgets",
                        "zhiyiYo/PyQt-Frameless-Window",
                    ),
                ),
                PresetDefinition(
                    preset_id="downloader-control-room",
                    display_name="Downloader Control Room",
                    summary="Queue, progress, destination, and detail panels tuned for file-transfer style applications.",
                    document_factory=_downloader_control_document,
                    source_references=("Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6",),
                ),
                PresetDefinition(
                    preset_id="creator-timeline-bay",
                    display_name="Creator Timeline Bay",
                    summary="Timeline, preview, caption, and card gallery patterns for media-adjacent workflows.",
                    document_factory=_creator_timeline_document,
                    source_references=("pyapp-kit/superqt", "pyqtgraph/pyqtgraph"),
                ),
                PresetDefinition(
                    preset_id="chat-ops-console",
                    display_name="Chat Ops Console",
                    summary="A conversation-first shell with activity stream, command actions, and operator notes.",
                    document_factory=_chat_ops_document,
                    source_references=(
                        "Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6",
                        "zhiyiYo/PyQt-Fluent-Widgets",
                    ),
                ),
                PresetDefinition(
                    preset_id="telemetry-mission-board",
                    display_name="Telemetry Mission Board",
                    summary="Signals, metrics, alarms, and dense inspectors staged for live-operating dashboards.",
                    document_factory=_telemetry_mission_document,
                    source_references=("pyqtgraph/pyqtgraph",),
                ),
                PresetDefinition(
                    preset_id="data-entry-pattern-atlas",
                    display_name="Data Entry Pattern Atlas",
                    summary="Forms, helper text, tables, and review summaries organized for CRUD-heavy tools.",
                    document_factory=_data_entry_pattern_document,
                    source_references=("zhiyiYo/PyQt-Fluent-Widgets",),
                ),
                PresetDefinition(
                    preset_id="dense-admin-shell",
                    display_name="Dense Admin Shell",
                    summary="A deliberately busy shell for testing how much structure a Qt app can carry before it breaks down.",
                    document_factory=_dense_admin_document,
                    source_references=(
                        "Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6",
                        "pyqtgraph/pyqtgraph",
                    ),
                ),
                PresetDefinition(
                    preset_id="palette-motion-board",
                    display_name="Palette + Motion Board",
                    summary="Accent, motion, effects, and theme variation studies kept on one comparison surface.",
                    document_factory=_palette_motion_document,
                    source_references=("5yutan5/PyQtDarkTheme", "pyapp-kit/superqt"),
                ),
                PresetDefinition(
                    preset_id="media-review-studio",
                    display_name="Media Review Studio",
                    summary="Preview, metadata, timeline, and issue-tracking panels for review-oriented tooling.",
                    document_factory=_media_review_document,
                    source_references=("pyqtgraph/pyqtgraph", "zhiyiYo/PyQt-Fluent-Widgets"),
                ),
                PresetDefinition(
                    preset_id="inspector-workshop",
                    display_name="Inspector Workshop",
                    summary="A property-heavy laboratory for nested trees, advanced settings, and block editing.",
                    document_factory=_inspector_workshop_document,
                    source_references=("pyapp-kit/superqt", "pyqtgraph/pyqtgraph"),
                ),
                PresetDefinition(
                    preset_id="signal-flow-theater",
                    display_name="Signal Flow Theater",
                    summary="A teaching-first board that puts signal chains, state updates, and action responses on stage.",
                    document_factory=_signal_flow_document,
                    source_references=("zhiyiYo/PyQt-Fluent-Widgets",),
                ),
                PresetDefinition(
                    preset_id="utility-grid-forge",
                    display_name="Utility Grid Forge",
                    summary="A compact playground for repeated cards, batch actions, and dense tool surfaces.",
                    document_factory=_utility_grid_document,
                    source_references=("pyapp-kit/superqt", "5yutan5/PyQtDarkTheme"),
                ),
                PresetDefinition(
                    preset_id="research-atlas-studio",
                    display_name="Research Atlas Studio",
                    summary="A mixed board for notes, findings, evidence panes, and drill-down review controls.",
                    document_factory=_research_atlas_document,
                    source_references=("pyqtgraph/pyqtgraph", "zhiyiYo/PyQt-Frameless-Window"),
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


def _command_bridge_document() -> StudioDocument:
    command_palette = _widget_preview(
        "Command Palette",
        x=60.0,
        y=70.0,
        description="A searchable command launcher wired to a result list and keyboard-driven selection.",
        cta_label="Open Command",
        kind="command-palette-lab",
    )
    alert_stack = _widget_preview(
        "Alert + Status Strip",
        x=480.0,
        y=70.0,
        description="Toast, banner, and inline-alert patterns side by side so urgency levels can be compared at a glance.",
        cta_label="Fire Alert",
        kind="flyout-lab",
    )
    quick_actions = _widget_preview(
        "Quick Action Bar",
        x=900.0,
        y=70.0,
        description="A compact row of primary actions with icon-only mode, overflow menu, and keyboard access.",
        cta_label="Run Action",
        kind="simple-controls",
    )
    routing_notes = _scene_card(
        "Routing Architecture",
        x=60.0,
        y=360.0,
        width=360.0,
        height=180.0,
        fill="#e8f0fb",
        description="Sketch the routing model here — which commands need confirmation, which are silent, and which hand off to a sub-panel.",
        kind="routing-notes",
    )
    shortcut_map = _scene_card(
        "Shortcut Surface Map",
        x=470.0,
        y=360.0,
        width=360.0,
        height=180.0,
        fill="#eef6ee",
        description="Document which shortcut slots are occupied, which are free, and how conflicts should resolve across modes.",
        kind="shortcut-map",
    )
    return StudioDocument(
        title="Command Bridge Lab",
        experience_level=ExperienceLevel.INTERMEDIATE.value,
        nodes=[command_palette, alert_stack, quick_actions, routing_notes, shortcut_map],
        theme_tokens=_theme_tokens(
            ("palette.accent", "#2f80ed", "palette"),
            ("palette.alert.warn", "#e6a817", "palette"),
            ("palette.alert.error", "#c0392b", "palette"),
            ("spacing.action-bar", 10, "layout"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="submit",
                target_node_id=command_palette.node_id,
                action="dispatch-command",
                payload={"mode": "keyboard-first"},
            ),
            InteractionDefinition(
                trigger="click",
                target_node_id=alert_stack.node_id,
                action="cycle-alert-level",
                payload={"levels": ["info", "warning", "error"]},
            ),
        ],
        workspace_state={"active_panel": "interactions", "recommended_zoom": 0.86},
        meta=_preset_meta(
            "command-bridge-lab",
            ("zhiyiYo/PyQt-Fluent-Widgets", "pyapp-kit/superqt"),
            ("commands", "alerts", "keyboard", "intermediate"),
        ),
    )


def _frameless_operator_document() -> StudioDocument:
    frameless_shell = _widget_preview(
        "Frameless Window Chrome",
        x=60.0,
        y=70.0,
        description="Custom titlebar controls, drag region, and system-button replacements so non-native chrome feels polished.",
        cta_label="Toggle Chrome",
        kind="frameless-shell",
    )
    side_drawer = _widget_preview(
        "Slide-In Settings Drawer",
        x=500.0,
        y=70.0,
        description="A right-side drawer that overlays the content area without pushing the main layout.",
        cta_label="Open Drawer",
        kind="settings-drawer",
    )
    route_stack = _widget_preview(
        "Route Stack Preview",
        x=900.0,
        y=70.0,
        description="A stacked page surface showing how push/pop navigation transitions feel in a desktop shell.",
        cta_label="Navigate",
        kind="content-stack",
    )
    chrome_notes = _scene_card(
        "Chrome Constraint Notes",
        x=60.0,
        y=380.0,
        width=380.0,
        height=190.0,
        fill="#1e2633",
        description="Note platform-specific limits here: hit-test regions, resize grips, shadow layers, and OS-level snap behavior.",
        kind="chrome-notes",
    )
    motion_notes = _scene_card(
        "Transition Motion Notes",
        x=490.0,
        y=380.0,
        width=340.0,
        height=190.0,
        fill="#2a2f3e",
        description="Document which page transitions use opacity fade, which use slide, and which are instant for accessibility.",
        kind="motion-notes",
    )
    return StudioDocument(
        title="Frameless Operator Shell",
        experience_level=ExperienceLevel.ADVANCED.value,
        nodes=[frameless_shell, side_drawer, route_stack, chrome_notes, motion_notes],
        theme_tokens=_theme_tokens(
            ("chrome.mode", "frameless", "runtime"),
            ("palette.surface", "#1a1f2b", "palette"),
            ("palette.accent", "#4f9cf9", "palette"),
            ("motion.page-transition", "slide", "animation"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="click",
                target_node_id=frameless_shell.node_id,
                action="toggle-frameless-mode",
                payload={"source": "zhiyiYo/PyQt-Frameless-Window"},
            ),
            InteractionDefinition(
                trigger="click",
                target_node_id=side_drawer.node_id,
                action="animate-drawer",
                payload={"direction": "right", "duration_ms": 220},
            ),
        ],
        workspace_state={"active_panel": "tokens", "recommended_zoom": 0.84},
        meta=_preset_meta(
            "frameless-operator-shell",
            ("zhiyiYo/PyQt-Frameless-Window", "Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6"),
            ("shell", "frameless", "motion", "advanced"),
        ),
    )


def _notification_decision_document() -> StudioDocument:
    toast_surface = _widget_preview(
        "Toast Notification Surface",
        x=60.0,
        y=70.0,
        description="Stacked non-blocking toasts with auto-dismiss, action links, and severity levels.",
        cta_label="Fire Toast",
        kind="flyout-lab",
    )
    confirmation_dialog = _widget_preview(
        "Confirmation Flow",
        x=490.0,
        y=70.0,
        description="Blocking and non-blocking confirmation dialogs staged for primary, secondary, and destructive decisions.",
        cta_label="Open Confirm",
        kind="dialog-lab",
    )
    banner_ribbon = _widget_preview(
        "Banner Ribbon",
        x=920.0,
        y=70.0,
        description="Persistent top-of-panel banners for deprecation warnings, maintenance notices, and feature announcements.",
        cta_label="Dismiss Banner",
        kind="simple-controls",
    )
    decision_tree = _scene_card(
        "Decision Routing Card",
        x=60.0,
        y=370.0,
        width=360.0,
        height=190.0,
        fill="#fff8e1",
        description="Map which user actions require confirmation, which are silent, and which offer undo as the safety net.",
        kind="decision-routing",
    )
    ux_writing = _scene_card(
        "UX Writing Guide",
        x=470.0,
        y=370.0,
        width=340.0,
        height=190.0,
        fill="#e8f4e8",
        description="Keep action-button copy, title phrasing, and body-text tone visible while iterating on dialog and toast patterns.",
        kind="ux-writing",
    )
    return StudioDocument(
        title="Notification Decision Deck",
        experience_level=ExperienceLevel.INTERMEDIATE.value,
        nodes=[toast_surface, confirmation_dialog, banner_ribbon, decision_tree, ux_writing],
        theme_tokens=_theme_tokens(
            ("notification.info", "#2f80ed", "palette"),
            ("notification.warn", "#e6a817", "palette"),
            ("notification.danger", "#c0392b", "palette"),
            ("notification.success", "#27ae60", "palette"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="click",
                target_node_id=toast_surface.node_id,
                action="queue-toast",
                payload={"levels": ["info", "success", "warn", "error"]},
            ),
            InteractionDefinition(
                trigger="click",
                target_node_id=confirmation_dialog.node_id,
                action="open-confirmation",
                payload={"style": "destructive"},
            ),
        ],
        workspace_state={"active_panel": "interactions", "recommended_zoom": 0.88},
        meta=_preset_meta(
            "notification-decision-deck",
            ("zhiyiYo/PyQt-Fluent-Widgets",),
            ("notifications", "dialogs", "ux", "intermediate"),
        ),
    )


def _auth_journey_document() -> StudioDocument:
    login_card = _widget_preview(
        "Login Surface",
        x=60.0,
        y=70.0,
        description="Email, password, remember-me, and primary CTA arranged for minimal friction and clear hierarchy.",
        cta_label="Sign In",
        kind="auth-shell",
    )
    register_card = _widget_preview(
        "Register Surface",
        x=480.0,
        y=70.0,
        description="Multi-field registration with inline validation, password strength, and terms acknowledgement.",
        cta_label="Create Account",
        kind="choice-matrix",
    )
    recovery_card = _widget_preview(
        "Recovery Flow",
        x=900.0,
        y=70.0,
        description="Email-code entry, new-password confirmation, and success state in a stepped single-panel flow.",
        cta_label="Send Reset",
        kind="simple-controls",
    )
    trust_notes = _scene_card(
        "Trust Signal Notes",
        x=60.0,
        y=380.0,
        width=360.0,
        height=180.0,
        fill="#edf5ff",
        description="Document where security badges, captcha, and provider logos should appear without breaking the visual rhythm.",
        kind="trust-notes",
    )
    error_states = _scene_card(
        "Error State Atlas",
        x=470.0,
        y=380.0,
        width=360.0,
        height=180.0,
        fill="#fff0f0",
        description="Map out every error condition — wrong credentials, locked account, network failure — and their field-level messages.",
        kind="error-states",
    )
    return StudioDocument(
        title="Auth Journey Studio",
        experience_level=ExperienceLevel.INTERMEDIATE.value,
        nodes=[login_card, register_card, recovery_card, trust_notes, error_states],
        theme_tokens=_theme_tokens(
            ("auth.surface", "#ffffff", "palette"),
            ("auth.accent", "#2f80ed", "palette"),
            ("auth.error", "#c0392b", "palette"),
            ("auth.radius", 16, "shape"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="submit",
                target_node_id=login_card.node_id,
                action="validate-credentials",
                payload={"modes": ["success", "error", "locked"]},
            ),
            InteractionDefinition(
                trigger="change",
                target_node_id=register_card.node_id,
                action="validate-password-strength",
                payload={"levels": ["weak", "fair", "strong"]},
            ),
        ],
        workspace_state={"active_panel": "inspector", "recommended_zoom": 0.88},
        meta=_preset_meta(
            "auth-journey-studio",
            ("zhiyiYo/PyQt-Fluent-Widgets", "zhiyiYo/PyQt-Frameless-Window"),
            ("auth", "forms", "validation", "intermediate"),
        ),
    )


def _downloader_control_document() -> StudioDocument:
    queue_panel = _widget_preview(
        "Download Queue Panel",
        x=60.0,
        y=70.0,
        description="A scrollable queue with per-row progress bars, status chips, and pause/cancel actions.",
        cta_label="Add Item",
        kind="scroll-gallery",
    )
    progress_detail = _widget_preview(
        "Progress Detail Card",
        x=540.0,
        y=70.0,
        description="Speed, ETA, destination path, and completion graph for the currently active transfer.",
        cta_label="Inspect",
        kind="slider-lab",
    )
    destination_picker = _widget_preview(
        "Destination Picker",
        x=960.0,
        y=70.0,
        description="A tree-based folder picker with recent locations, create-folder action, and path breadcrumb.",
        cta_label="Choose Folder",
        kind="inspector-tree",
    )
    ops_notes = _scene_card(
        "Concurrency + Throttle Notes",
        x=60.0,
        y=380.0,
        width=380.0,
        height=180.0,
        fill="#e8f0fb",
        description="Sketch the maximum concurrent connections, retry strategy, and bandwidth cap UI affordances.",
        kind="ops-notes",
    )
    completion_notes = _scene_card(
        "Completion State Notes",
        x=490.0,
        y=380.0,
        width=340.0,
        height=180.0,
        fill="#e8f6ee",
        description="Map the success, partial-failure, and all-failed terminal states and what actions should be available in each.",
        kind="completion-notes",
    )
    return StudioDocument(
        title="Downloader Control Room",
        experience_level=ExperienceLevel.INTERMEDIATE.value,
        nodes=[queue_panel, progress_detail, destination_picker, ops_notes, completion_notes],
        theme_tokens=_theme_tokens(
            ("transfer.active", "#2f80ed", "palette"),
            ("transfer.success", "#27ae60", "palette"),
            ("transfer.error", "#c0392b", "palette"),
            ("transfer.paused", "#8e9db5", "palette"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="change",
                target_node_id=progress_detail.node_id,
                action="update-speed-graph",
                payload={"interval_ms": 500},
            ),
            InteractionDefinition(
                trigger="select",
                target_node_id=destination_picker.node_id,
                action="validate-write-access",
                payload={"check": "permissions"},
            ),
        ],
        workspace_state={"active_panel": "inspector", "recommended_zoom": 0.86},
        meta=_preset_meta(
            "downloader-control-room",
            ("Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6",),
            ("transfer", "queue", "progress", "intermediate"),
        ),
    )


def _creator_timeline_document() -> StudioDocument:
    timeline_strip = _widget_preview(
        "Timeline Strip",
        x=60.0,
        y=70.0,
        description="A horizontal scrubber with clip markers, playhead, zoom level, and in/out point handles.",
        cta_label="Scrub",
        kind="timeline-review",
    )
    preview_pane = _widget_preview(
        "Preview Pane",
        x=500.0,
        y=70.0,
        description="A fixed-ratio preview area with frame counter, playback controls, and metadata overlay.",
        cta_label="Play",
        kind="effects-lab",
    )
    card_gallery = _widget_preview(
        "Asset Card Gallery",
        x=940.0,
        y=70.0,
        description="A grid-scroll library of thumbnail cards with tag chips, duration labels, and select-all affordance.",
        cta_label="Select",
        kind="card-gallery",
    )
    caption_notes = _scene_card(
        "Caption + Subtitle Notes",
        x=60.0,
        y=380.0,
        width=380.0,
        height=180.0,
        fill="#f0f4ff",
        description="Document caption rendering, font size overrides, background opacity, and multi-language display needs.",
        kind="caption-notes",
    )
    export_notes = _scene_card(
        "Export Preset Notes",
        x=490.0,
        y=380.0,
        width=340.0,
        height=180.0,
        fill="#f0fff4",
        description="Sketch the format selector, quality dial, destination summary, and estimated-size label for the export panel.",
        kind="export-notes",
    )
    return StudioDocument(
        title="Creator Timeline Bay",
        experience_level=ExperienceLevel.ADVANCED.value,
        nodes=[timeline_strip, preview_pane, card_gallery, caption_notes, export_notes],
        theme_tokens=_theme_tokens(
            ("timeline.playhead", "#e74c3c", "palette"),
            ("timeline.clip", "#2f80ed", "palette"),
            ("timeline.marker", "#f39c12", "palette"),
            ("preview.background", "#111820", "palette"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="drag",
                target_node_id=timeline_strip.node_id,
                action="scrub-playhead",
                payload={"snap": "frame"},
            ),
            InteractionDefinition(
                trigger="select",
                target_node_id=card_gallery.node_id,
                action="load-clip-preview",
                payload={"target": preview_pane.node_id},
            ),
        ],
        workspace_state={"active_panel": "inspector", "recommended_zoom": 0.82},
        meta=_preset_meta(
            "creator-timeline-bay",
            ("pyapp-kit/superqt", "pyqtgraph/pyqtgraph"),
            ("media", "timeline", "preview", "advanced"),
        ),
    )


def _chat_ops_document() -> StudioDocument:
    chat_shell = _widget_preview(
        "Chat Ops Shell",
        x=60.0,
        y=70.0,
        description="A full conversation shell with message stream, composer, user list, and channel switcher.",
        cta_label="Send",
        kind="chat-ops-shell",
    )
    ops_console = _widget_preview(
        "Operator Console",
        x=740.0,
        y=70.0,
        description="A parallel operator panel for commands, system events, active sessions, and alert escalation.",
        cta_label="Execute",
        kind="ops-console",
    )
    activity_notes = _scene_card(
        "Activity Stream Notes",
        x=60.0,
        y=390.0,
        width=360.0,
        height=180.0,
        fill="#1a2233",
        description="Map what event types appear in the stream, how they are grouped, and which require inline action.",
        kind="activity-notes",
    )
    routing_notes = _scene_card(
        "Message Routing Notes",
        x=470.0,
        y=390.0,
        width=340.0,
        height=180.0,
        fill="#1e2f1e",
        description="Document how messages route to channels, how threads branch, and how the composer state is preserved across switches.",
        kind="routing-notes",
    )
    return StudioDocument(
        title="Chat Ops Console",
        experience_level=ExperienceLevel.ADVANCED.value,
        nodes=[chat_shell, ops_console, activity_notes, routing_notes],
        theme_tokens=_theme_tokens(
            ("palette.surface", "#13181f", "palette"),
            ("palette.accent", "#4f9cf9", "palette"),
            ("chat.mention", "#9b59b6", "palette"),
            ("chat.timestamp", "#5d7086", "palette"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="submit",
                target_node_id=chat_shell.node_id,
                action="send-message",
                payload={"mode": "markdown"},
            ),
            InteractionDefinition(
                trigger="click",
                target_node_id=ops_console.node_id,
                action="escalate-event",
                payload={"levels": ["info", "critical"]},
            ),
        ],
        workspace_state={"active_panel": "interactions", "recommended_zoom": 0.8},
        meta=_preset_meta(
            "chat-ops-console",
            ("Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6", "zhiyiYo/PyQt-Fluent-Widgets"),
            ("chat", "ops", "dark", "advanced"),
        ),
    )


def _telemetry_mission_document() -> StudioDocument:
    signal_plot = _widget_preview(
        "Live Signal Plot",
        x=60.0,
        y=70.0,
        description="A high-frequency rolling plot with configurable axes, grid lines, and threshold overlays.",
        cta_label="Inject Signal",
        kind="plot-pane",
    )
    metric_row = _widget_preview(
        "KPI Metric Row",
        x=690.0,
        y=70.0,
        description="A horizontal strip of KPI cards showing live values, delta arrows, and sparklines.",
        cta_label="Refresh",
        kind="data-table-console",
    )
    alarm_panel = _widget_preview(
        "Alarm + Threshold Panel",
        x=60.0,
        y=390.0,
        description="Threshold sliders, active-alarm list, and acknowledge/escalate actions in one compact surface.",
        cta_label="Acknowledge",
        kind="slider-lab",
    )
    dense_inspector = _widget_preview(
        "Dense Parameter Inspector",
        x=500.0,
        y=390.0,
        description="A packed tree of runtime parameters with live read-back values and edit-in-place controls.",
        cta_label="Edit Param",
        kind="dense-inspector",
    )
    layout_notes = _scene_card(
        "Dashboard Layout Notes",
        x=960.0,
        y=70.0,
        width=320.0,
        height=190.0,
        fill="#0d1b2a",
        description="Sketch the tile grid, resize handles, and saved-layout system for a configurable mission dashboard.",
        kind="dashboard-layout",
    )
    return StudioDocument(
        title="Telemetry Mission Board",
        experience_level=ExperienceLevel.ADVANCED.value,
        nodes=[signal_plot, metric_row, alarm_panel, dense_inspector, layout_notes],
        theme_tokens=_theme_tokens(
            ("plot.background", "#0b1420", "palette"),
            ("plot.signal.primary", "#00d4ff", "palette"),
            ("plot.signal.secondary", "#ff6b35", "palette"),
            ("alarm.critical", "#ff2d55", "palette"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="change",
                target_node_id=alarm_panel.node_id,
                action="update-threshold-overlay",
                payload={"target": signal_plot.node_id},
            ),
            InteractionDefinition(
                trigger="select",
                target_node_id=dense_inspector.node_id,
                action="live-edit-parameter",
                payload={"source": "pyqtgraph/pyqtgraph"},
            ),
        ],
        workspace_state={"active_panel": "tokens", "recommended_zoom": 0.78},
        meta=_preset_meta(
            "telemetry-mission-board",
            ("pyqtgraph/pyqtgraph",),
            ("telemetry", "realtime", "dashboard", "advanced"),
        ),
    )


def _data_entry_pattern_document() -> StudioDocument:
    form_surface = _widget_preview(
        "Multi-Section Form",
        x=60.0,
        y=70.0,
        description="A grouped form with field-level validation, helper text, required markers, and section dividers.",
        cta_label="Submit",
        kind="choice-matrix",
    )
    table_crud = _widget_preview(
        "Editable Table + Toolbar",
        x=520.0,
        y=70.0,
        description="An inline-edit table with add/delete toolbar, row selection, and undo for bulk operations.",
        cta_label="Add Row",
        kind="data-table-console",
    )
    review_summary = _widget_preview(
        "Review Summary Panel",
        x=980.0,
        y=70.0,
        description="A read-only confirmation surface that echoes entered values before committing the operation.",
        cta_label="Confirm",
        kind="inspector-tree",
    )
    validation_notes = _scene_card(
        "Validation Rule Map",
        x=60.0,
        y=390.0,
        width=380.0,
        height=180.0,
        fill="#fff8e6",
        description="List every field-level rule, their error messages, and whether they validate on blur, on change, or on submit.",
        kind="validation-notes",
    )
    state_flow = _scene_card(
        "Form State Flow",
        x=490.0,
        y=390.0,
        width=340.0,
        height=180.0,
        fill="#e8fbe8",
        description="Map the idle, dirty, validating, submitting, success, and error states and what the UI should show in each.",
        kind="form-state-flow",
    )
    return StudioDocument(
        title="Data Entry Pattern Atlas",
        experience_level=ExperienceLevel.INTERMEDIATE.value,
        nodes=[form_surface, table_crud, review_summary, validation_notes, state_flow],
        theme_tokens=_theme_tokens(
            ("form.required", "#c0392b", "palette"),
            ("form.helper", "#526273", "palette"),
            ("form.success", "#27ae60", "palette"),
            ("form.radius", 10, "shape"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="change",
                target_node_id=form_surface.node_id,
                action="validate-field",
                payload={"timing": "on-blur"},
            ),
            InteractionDefinition(
                trigger="submit",
                target_node_id=form_surface.node_id,
                action="populate-review",
                payload={"target": review_summary.node_id},
            ),
        ],
        workspace_state={"active_panel": "inspector", "recommended_zoom": 0.86},
        meta=_preset_meta(
            "data-entry-pattern-atlas",
            ("zhiyiYo/PyQt-Fluent-Widgets",),
            ("forms", "tables", "validation", "intermediate"),
        ),
    )


def _dense_admin_document() -> StudioDocument:
    left_nav = _widget_preview(
        "Persistent Left Navigation",
        x=60.0,
        y=70.0,
        description="A full-height navigation with grouped routes, badge counters, and collapse-to-icon mode.",
        cta_label="Switch Route",
        kind="navigation-workspace",
    )
    data_grid = _widget_preview(
        "Dense Data Grid",
        x=500.0,
        y=70.0,
        description="A column-sortable, filterable table with bulk-select toolbar, pagination, and export action.",
        cta_label="Filter",
        kind="data-table-console",
    )
    detail_panel = _widget_preview(
        "Detail Side Panel",
        x=980.0,
        y=70.0,
        description="A contextual right panel that shows selected-row detail, action buttons, and audit history.",
        cta_label="Open Detail",
        kind="inspector-tree",
    )
    signal_strip = _widget_preview(
        "Health Signal Strip",
        x=60.0,
        y=390.0,
        description="A condensed metric bar showing system health, queue depth, error rate, and latency at a glance.",
        cta_label="Drill Down",
        kind="slider-lab",
    )
    breadcrumb_notes = _scene_card(
        "Breadcrumb + Header Notes",
        x=500.0,
        y=390.0,
        width=380.0,
        height=180.0,
        fill="#eef3fb",
        description="Document how the page header communicates depth, provides quick actions, and handles overflow at narrow widths.",
        kind="breadcrumb-notes",
    )
    return StudioDocument(
        title="Dense Admin Shell",
        experience_level=ExperienceLevel.ADVANCED.value,
        nodes=[left_nav, data_grid, detail_panel, signal_strip, breadcrumb_notes],
        theme_tokens=_theme_tokens(
            ("palette.surface", "#f3f6fb", "palette"),
            ("palette.accent", "#2f80ed", "palette"),
            ("density", "compact", "layout"),
            ("sidebar.width", 240, "layout"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="select",
                target_node_id=data_grid.node_id,
                action="populate-detail-panel",
                payload={"target": detail_panel.node_id},
            ),
            InteractionDefinition(
                trigger="click",
                target_node_id=left_nav.node_id,
                action="navigate-route",
                payload={"update_breadcrumb": True},
            ),
        ],
        workspace_state={"active_panel": "outliner", "recommended_zoom": 0.78},
        meta=_preset_meta(
            "dense-admin-shell",
            ("Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6", "pyqtgraph/pyqtgraph"),
            ("admin", "dense", "data-grid", "advanced"),
        ),
    )


def _palette_motion_document() -> StudioDocument:
    dark_surface = _widget_preview(
        "Dark Palette Study",
        x=60.0,
        y=70.0,
        description="A full dark-mode widget set showing how accent, muted text, and elevated surfaces interact at low luminance.",
        cta_label="Tune Dark",
        kind="effects-lab",
    )
    light_surface = _widget_preview(
        "Light Palette Study",
        x=510.0,
        y=70.0,
        description="The same widget set in a cool neutral light palette so dark/light decisions can be made in direct comparison.",
        cta_label="Tune Light",
        kind="font-color-lab",
    )
    motion_bench = _widget_preview(
        "Motion Timing Bench",
        x=960.0,
        y=70.0,
        description="Easing curves, duration sliders, and before/after previews for opacity, geometry, and color transitions.",
        cta_label="Preview Motion",
        kind="slider-lab",
    )
    token_board = _scene_card(
        "Design Token Board",
        x=60.0,
        y=390.0,
        width=440.0,
        height=200.0,
        fill="#f0f4ff",
        description="A living reference for surface, accent, text, border, and shadow tokens across both modes.",
        kind="token-board",
    )
    contrast_notes = _scene_card(
        "Contrast + Accessibility Notes",
        x=550.0,
        y=390.0,
        width=340.0,
        height=200.0,
        fill="#fff9e6",
        description="Record WCAG contrast ratios for key color pairings and flag any combinations that fall below AA threshold.",
        kind="contrast-notes",
    )
    return StudioDocument(
        title="Palette + Motion Board",
        experience_level=ExperienceLevel.INTERMEDIATE.value,
        nodes=[dark_surface, light_surface, motion_bench, token_board, contrast_notes],
        theme_tokens=_theme_tokens(
            ("motion.duration.fast", 120, "animation"),
            ("motion.duration.standard", 220, "animation"),
            ("motion.easing", "ease-out", "animation"),
            ("contrast.min-ratio", 4.5, "accessibility"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="change",
                target_node_id=motion_bench.node_id,
                action="preview-easing",
                payload={"source": "pyapp-kit/superqt"},
            ),
            InteractionDefinition(
                trigger="click",
                target_node_id=dark_surface.node_id,
                action="toggle-theme-mode",
                payload={"source": "5yutan5/PyQtDarkTheme"},
            ),
        ],
        workspace_state={"active_panel": "tokens", "recommended_zoom": 0.86},
        meta=_preset_meta(
            "palette-motion-board",
            ("5yutan5/PyQtDarkTheme", "pyapp-kit/superqt"),
            ("palette", "motion", "accessibility", "intermediate"),
        ),
    )


def _media_review_document() -> StudioDocument:
    preview_surface = _widget_preview(
        "Media Preview Surface",
        x=60.0,
        y=70.0,
        description="A fixed-ratio preview region with zoom controls, annotation overlay, and playback transport.",
        cta_label="Play",
        kind="effects-studio",
    )
    metadata_inspector = _widget_preview(
        "Metadata Inspector",
        x=620.0,
        y=70.0,
        description="A structured panel for file metadata, edit history, attached notes, and per-frame annotations.",
        cta_label="Add Note",
        kind="dense-inspector",
    )
    issue_tracker = _widget_preview(
        "Issue + Flag Tracker",
        x=60.0,
        y=410.0,
        description="A list of flagged frames, reviewer comments, and resolution states for collaborative review flows.",
        cta_label="Resolve",
        kind="data-table-console",
    )
    timeline_notes = _scene_card(
        "Review Timeline Notes",
        x=500.0,
        y=410.0,
        width=380.0,
        height=190.0,
        fill="#f0f4ff",
        description="Map how frame markers, in/out regions, and reviewer threads attach to the timeline without cluttering the scrub area.",
        kind="review-timeline-notes",
    )
    return StudioDocument(
        title="Media Review Studio",
        experience_level=ExperienceLevel.ADVANCED.value,
        nodes=[preview_surface, metadata_inspector, issue_tracker, timeline_notes],
        theme_tokens=_theme_tokens(
            ("review.annotation", "#f39c12", "palette"),
            ("review.flag", "#e74c3c", "palette"),
            ("review.resolved", "#27ae60", "palette"),
            ("preview.background", "#0d1117", "palette"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="select",
                target_node_id=issue_tracker.node_id,
                action="jump-to-frame",
                payload={"target": preview_surface.node_id},
            ),
            InteractionDefinition(
                trigger="click",
                target_node_id=preview_surface.node_id,
                action="add-frame-annotation",
                payload={"target": metadata_inspector.node_id},
            ),
        ],
        workspace_state={"active_panel": "inspector", "recommended_zoom": 0.82},
        meta=_preset_meta(
            "media-review-studio",
            ("pyqtgraph/pyqtgraph", "zhiyiYo/PyQt-Fluent-Widgets"),
            ("media", "review", "annotations", "advanced"),
        ),
    )


def _inspector_workshop_document() -> StudioDocument:
    deep_tree = _widget_preview(
        "Deep Property Tree",
        x=60.0,
        y=70.0,
        description="A nested multi-level tree showing how grouped, collapsed, and searchable properties feel at high density.",
        cta_label="Expand All",
        kind="parameter-tree",
    )
    block_editor = _widget_preview(
        "JSON Block Editor",
        x=510.0,
        y=70.0,
        description="A side-by-side block preview and raw-JSON edit surface with syntax hints and validation feedback.",
        cta_label="Apply Block",
        kind="data-table-console",
    )
    advanced_settings = _widget_preview(
        "Advanced Settings Stack",
        x=960.0,
        y=70.0,
        description="A tiered settings surface showing basic, intermediate, and expert options with progressive disclosure toggles.",
        cta_label="Expand Expert",
        kind="settings-stack",
    )
    schema_notes = _scene_card(
        "Schema + Type Notes",
        x=60.0,
        y=390.0,
        width=380.0,
        height=190.0,
        fill="#eef3fb",
        description="Document property types, acceptable ranges, default values, and any constraints that the inspector should enforce.",
        kind="schema-notes",
    )
    undo_notes = _scene_card(
        "Undo + History Notes",
        x=490.0,
        y=390.0,
        width=340.0,
        height=190.0,
        fill="#f0fff4",
        description="Map which edits are undoable, how history is scoped, and whether per-property or per-object granularity serves the workflow better.",
        kind="undo-notes",
    )
    return StudioDocument(
        title="Inspector Workshop",
        experience_level=ExperienceLevel.ADVANCED.value,
        nodes=[deep_tree, block_editor, advanced_settings, schema_notes, undo_notes],
        theme_tokens=_theme_tokens(
            ("inspector.density", "compact", "layout"),
            ("inspector.accent", "#2f80ed", "palette"),
            ("inspector.expert-tint", "#f3e8ff", "palette"),
            ("inspector.error", "#c0392b", "palette"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="change",
                target_node_id=block_editor.node_id,
                action="validate-schema",
                payload={"source": "pyapp-kit/superqt"},
            ),
            InteractionDefinition(
                trigger="select",
                target_node_id=deep_tree.node_id,
                action="populate-block-editor",
                payload={"target": block_editor.node_id},
            ),
        ],
        workspace_state={"active_panel": "inspector", "recommended_zoom": 0.84},
        meta=_preset_meta(
            "inspector-workshop",
            ("pyapp-kit/superqt", "pyqtgraph/pyqtgraph"),
            ("inspector", "properties", "advanced"),
        ),
    )


def _signal_flow_document() -> StudioDocument:
    emitter_card = _widget_preview(
        "Signal Emitter Surface",
        x=60.0,
        y=70.0,
        description="A set of controls wired to emit different signal types: clicked, valueChanged, textChanged, and custom pyqtSignal.",
        cta_label="Emit Signal",
        kind="simple-controls",
    )
    slot_viewer = _widget_preview(
        "Slot Response Viewer",
        x=500.0,
        y=70.0,
        description="A live log showing which slots fired, with what arguments, and in which order — making the connect() pattern visible.",
        cta_label="Connect",
        kind="data-table-console",
    )
    chain_diagram = _widget_preview(
        "Signal Chain Diagram",
        x=940.0,
        y=70.0,
        description="A wired tree showing how one signal triggers a chain of updates across multiple widgets and models.",
        cta_label="Trigger Chain",
        kind="inspector-tree",
    )
    pattern_notes = _scene_card(
        "Signal Pattern Notes",
        x=60.0,
        y=390.0,
        width=380.0,
        height=190.0,
        fill="#eef8ff",
        description="Document the key patterns here: one-to-one, one-to-many, lambda slots, blocking signals, and thread-safe emit.",
        kind="signal-pattern-notes",
    )
    pitfall_notes = _scene_card(
        "Common Pitfall Notes",
        x=490.0,
        y=390.0,
        width=340.0,
        height=190.0,
        fill="#fff5f5",
        description="Keep gotchas visible: reference cycles through lambdas, double-connection bugs, disconnecting in destructors.",
        kind="pitfall-notes",
    )
    return StudioDocument(
        title="Signal Flow Theater",
        experience_level=ExperienceLevel.BASIC.value,
        nodes=[emitter_card, slot_viewer, chain_diagram, pattern_notes, pitfall_notes],
        theme_tokens=_theme_tokens(
            ("signal.emit-color", "#2f80ed", "palette"),
            ("signal.slot-color", "#27ae60", "palette"),
            ("signal.chain-color", "#9b59b6", "palette"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="click",
                target_node_id=emitter_card.node_id,
                action="emit-and-log",
                payload={"target": slot_viewer.node_id},
            ),
            InteractionDefinition(
                trigger="connect",
                target_node_id=slot_viewer.node_id,
                action="update-chain-diagram",
                payload={"target": chain_diagram.node_id},
            ),
        ],
        workspace_state={"active_panel": "interactions", "recommended_zoom": 0.88},
        meta=_preset_meta(
            "signal-flow-theater",
            ("zhiyiYo/PyQt-Fluent-Widgets",),
            ("signals", "slots", "teaching", "basic"),
        ),
    )


def _utility_grid_document() -> StudioDocument:
    card_grid = _widget_preview(
        "Repeating Card Grid",
        x=60.0,
        y=70.0,
        description="A grid of uniform cards for catalog, dashboard-tile, or gallery layouts with hover states and batch selection.",
        cta_label="Select All",
        kind="card-gallery",
    )
    batch_action_bar = _widget_preview(
        "Batch Action Bar",
        x=540.0,
        y=70.0,
        description="A contextual toolbar that appears when multiple items are selected, offering bulk operations and a count summary.",
        cta_label="Apply Batch",
        kind="flyout-lab",
    )
    filter_sidebar = _widget_preview(
        "Filter Sidebar",
        x=980.0,
        y=70.0,
        description="A collapsible facet sidebar with checkbox groups, range sliders, and an active-filters summary chip row.",
        cta_label="Apply Filter",
        kind="choice-matrix",
    )
    density_notes = _scene_card(
        "Density + Spacing Notes",
        x=60.0,
        y=390.0,
        width=360.0,
        height=180.0,
        fill="#f0f4ff",
        description="Track which grid density levels feel comfortable for different data types and screen sizes.",
        kind="density-notes",
    )
    empty_state = _scene_card(
        "Empty + Zero State",
        x=470.0,
        y=390.0,
        width=360.0,
        height=180.0,
        fill="#f5fff5",
        description="Design the zero-results, first-run, and all-filtered-out states so the grid never feels broken.",
        kind="empty-state",
    )
    return StudioDocument(
        title="Utility Grid Forge",
        experience_level=ExperienceLevel.INTERMEDIATE.value,
        nodes=[card_grid, batch_action_bar, filter_sidebar, density_notes, empty_state],
        theme_tokens=_theme_tokens(
            ("grid.columns", 4, "layout"),
            ("grid.gap", 16, "layout"),
            ("grid.card-radius", 14, "shape"),
            ("grid.hover-elevation", 4, "effect"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="select",
                target_node_id=card_grid.node_id,
                action="reveal-batch-bar",
                payload={"target": batch_action_bar.node_id},
            ),
            InteractionDefinition(
                trigger="change",
                target_node_id=filter_sidebar.node_id,
                action="filter-grid-results",
                payload={"target": card_grid.node_id},
            ),
        ],
        workspace_state={"active_panel": "inspector", "recommended_zoom": 0.86},
        meta=_preset_meta(
            "utility-grid-forge",
            ("pyapp-kit/superqt", "5yutan5/PyQtDarkTheme"),
            ("grid", "batch", "filter", "intermediate"),
        ),
    )


def _research_atlas_document() -> StudioDocument:
    evidence_pane = _widget_preview(
        "Evidence Pane",
        x=60.0,
        y=70.0,
        description="A scrollable annotated document viewer with highlight regions, margin notes, and source citations.",
        cta_label="Annotate",
        kind="scroll-gallery",
    )
    findings_board = _widget_preview(
        "Findings Board",
        x=540.0,
        y=70.0,
        description="A structured tree of observations, themes, and sub-findings with confidence ratings and linked evidence.",
        cta_label="Add Finding",
        kind="inspector-tree",
    )
    drill_down = _widget_preview(
        "Drill-Down Review Panel",
        x=980.0,
        y=70.0,
        description="A detail surface that expands a selected finding into full context, supporting evidence, and related items.",
        cta_label="Drill Down",
        kind="dialog-lab",
    )
    synthesis_notes = _scene_card(
        "Synthesis Notes",
        x=60.0,
        y=390.0,
        width=400.0,
        height=190.0,
        fill="#f4f0ff",
        description="Keep emerging themes, cross-cutting concerns, and open questions visible while building the findings tree.",
        kind="synthesis-notes",
    )
    export_notes = _scene_card(
        "Export + Report Notes",
        x=510.0,
        y=390.0,
        width=360.0,
        height=190.0,
        fill="#f0fff8",
        description="Map the report sections, citation formats, and export targets that the studio should eventually generate.",
        kind="export-report-notes",
    )
    return StudioDocument(
        title="Research Atlas Studio",
        experience_level=ExperienceLevel.ADVANCED.value,
        nodes=[evidence_pane, findings_board, drill_down, synthesis_notes, export_notes],
        theme_tokens=_theme_tokens(
            ("research.highlight", "#f6e05e", "palette"),
            ("research.citation", "#4a90d9", "palette"),
            ("research.confidence.high", "#27ae60", "palette"),
            ("research.confidence.low", "#e67e22", "palette"),
        ),
        interactions=[
            InteractionDefinition(
                trigger="select",
                target_node_id=findings_board.node_id,
                action="populate-drill-down",
                payload={"target": drill_down.node_id},
            ),
            InteractionDefinition(
                trigger="click",
                target_node_id=evidence_pane.node_id,
                action="link-to-finding",
                payload={"target": findings_board.node_id},
            ),
        ],
        workspace_state={"active_panel": "inspector", "recommended_zoom": 0.82},
        meta=_preset_meta(
            "research-atlas-studio",
            ("pyqtgraph/pyqtgraph", "zhiyiYo/PyQt-Frameless-Window"),
            ("research", "annotations", "findings", "advanced"),
        ),
    )