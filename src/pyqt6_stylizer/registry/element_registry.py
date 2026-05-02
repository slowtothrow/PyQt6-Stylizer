from __future__ import annotations

from dataclasses import dataclass

from ..document.schema import StudioNode, make_stable_id


@dataclass(frozen=True, slots=True)
class ElementDefinition:
    element_type: str
    display_name: str
    node_type: str
    description: str
    default_properties: dict[str, object]

    def instantiate(
        self,
        insertion_index: int,
        *,
        position: tuple[float, float] | None = None,
    ) -> StudioNode:
        properties = dict(self.default_properties)
        if position is not None:
            properties["x"] = float(position[0])
            properties["y"] = float(position[1])
        else:
            if "x" in properties:
                properties["x"] = float(properties["x"]) + 28.0 * insertion_index
            if "y" in properties:
                properties["y"] = float(properties["y"]) + 20.0 * insertion_index

        properties.setdefault("description", self.description)

        return StudioNode(
            node_id=make_stable_id(self.element_type),
            node_type=self.node_type,
            label=self.display_name,
            properties=properties,
        )


class ElementRegistry:
    def __init__(self, definitions: list[ElementDefinition]) -> None:
        self._definitions = definitions
        self._by_type = {definition.element_type: definition for definition in definitions}

    def definitions(self) -> list[ElementDefinition]:
        return list(self._definitions)

    def definition_for(self, element_type: str) -> ElementDefinition | None:
        return self._by_type.get(element_type)

    def instantiate(
        self,
        element_type: str,
        insertion_index: int,
        *,
        position: tuple[float, float] | None = None,
    ) -> StudioNode | None:
        definition = self.definition_for(element_type)
        if definition is None:
            return None
        return definition.instantiate(insertion_index, position=position)

    @classmethod
    def default(cls) -> "ElementRegistry":
        return cls(
            [
                ElementDefinition(
                    element_type="scene-card",
                    display_name="Scene Card",
                    node_type="scene-card",
                    description="A drawn card for mood-board style layout and surface experiments.",
                    default_properties={
                        "x": 60.0,
                        "y": 60.0,
                        "width": 260.0,
                        "height": 180.0,
                        "fill": "#f8f3e6",
                    },
                ),
                ElementDefinition(
                    element_type="widget-preview",
                    display_name="Embedded Widget Card",
                    node_type="widget-preview",
                    description="A real QWidget preview hosted in the scene through QGraphicsProxyWidget.",
                    default_properties={
                        "x": 380.0,
                        "y": 120.0,
                        "width": 360.0,
                        "height": 260.0,
                        "kind": "simple-controls",
                        "cta_label": "Trigger Dummy State",
                    },
                ),
                ElementDefinition(
                    element_type="palette-swatch",
                    display_name="Palette Swatch",
                    node_type="scene-card",
                    description="A compact scene item for testing palette, accent, and contrast decisions.",
                    default_properties={
                        "x": 120.0,
                        "y": 320.0,
                        "width": 180.0,
                        "height": 120.0,
                        "fill": "#d8e4f2",
                    },
                ),
                ElementDefinition(
                    element_type="state-badge",
                    display_name="State Badge",
                    node_type="scene-card",
                    description="A small drawn component for experimenting with empty, loading, success, and error states.",
                    default_properties={
                        "x": 340.0,
                        "y": 320.0,
                        "width": 160.0,
                        "height": 110.0,
                        "fill": "#efe4d4",
                    },
                ),
                ElementDefinition(
                    element_type="effect-stack",
                    display_name="Effect Stack",
                    node_type="widget-preview",
                    description="A widget host reserved for future blur, shadow, and opacity-chain experimentation.",
                    default_properties={
                        "x": 560.0,
                        "y": 280.0,
                        "width": 360.0,
                        "height": 260.0,
                        "kind": "effects-lab",
                        "cta_label": "Preview Effect",
                    },
                ),
                ElementDefinition(
                    element_type="copy-deck",
                    display_name="Copy Deck",
                    node_type="scene-card",
                    description="A text-heavy board for headlines, body copy, helper text, and tone comparisons.",
                    default_properties={
                        "x": 160.0,
                        "y": 460.0,
                        "width": 260.0,
                        "height": 160.0,
                        "fill": "#f3ece1",
                    },
                ),
                ElementDefinition(
                    element_type="metric-panel",
                    display_name="Metric Panel",
                    node_type="widget-preview",
                    description="A compact widget host for KPI cards, counters, and status summaries.",
                    default_properties={
                        "x": 720.0,
                        "y": 120.0,
                        "width": 420.0,
                        "height": 300.0,
                        "kind": "data-table-console",
                        "cta_label": "Refresh Metric",
                    },
                ),
                ElementDefinition(
                    element_type="navigation-rail",
                    display_name="Navigation Rail",
                    node_type="widget-preview",
                    description="A shell-focused widget host for route groups, icons, and persistent settings affordances.",
                    default_properties={
                        "x": 880.0,
                        "y": 120.0,
                        "width": 520.0,
                        "height": 360.0,
                        "kind": "navigation-workspace",
                        "cta_label": "Switch Route",
                    },
                ),
                ElementDefinition(
                    element_type="command-surface",
                    display_name="Command Surface",
                    node_type="scene-card",
                    description="A structured area for menus, command bars, search shortcuts, and grouped actions.",
                    default_properties={
                        "x": 640.0,
                        "y": 460.0,
                        "width": 280.0,
                        "height": 160.0,
                        "fill": "#e8eff6",
                    },
                ),
                ElementDefinition(
                    element_type="inspector-host",
                    display_name="Inspector Host",
                    node_type="widget-preview",
                    description="A denser utility host for tree controls, property editors, and advanced runtime toggles.",
                    default_properties={
                        "x": 1000.0,
                        "y": 300.0,
                        "width": 520.0,
                        "height": 360.0,
                        "kind": "inspector-tree",
                        "cta_label": "Reveal Controls",
                    },
                ),
            ]
        )
