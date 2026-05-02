from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4

from ..models import ExperienceLevel


def make_stable_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


@dataclass(slots=True)
class ThemeToken:
    name: str
    value: Any
    category: str = "theme"

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ThemeToken":
        return cls(
            name=str(payload["name"]),
            value=payload["value"],
            category=str(payload.get("category", "theme")),
        )


@dataclass(slots=True)
class InteractionDefinition:
    trigger: str
    target_node_id: str
    action: str
    payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "InteractionDefinition":
        return cls(
            trigger=str(payload["trigger"]),
            target_node_id=str(payload["target_node_id"]),
            action=str(payload["action"]),
            payload=dict(payload.get("payload", {})),
        )


@dataclass(slots=True)
class StudioNode:
    node_id: str
    node_type: str
    label: str
    properties: dict[str, Any] = field(default_factory=dict)
    children: list["StudioNode"] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "properties": self.properties,
            "children": [child.to_dict() for child in self.children],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "StudioNode":
        return cls(
            node_id=str(payload["node_id"]),
            node_type=str(payload["node_type"]),
            label=str(payload["label"]),
            properties=dict(payload.get("properties", {})),
            children=[cls.from_dict(child) for child in payload.get("children", [])],
        )


@dataclass(slots=True)
class StudioDocument:
    title: str = "Untitled Studio"
    schema_version: int = 1
    experience_level: str = ExperienceLevel.BASIC.value
    nodes: list[StudioNode] = field(default_factory=list)
    theme_tokens: list[ThemeToken] = field(default_factory=list)
    interactions: list[InteractionDefinition] = field(default_factory=list)
    workspace_state: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)

    def iter_nodes(self) -> list[StudioNode]:
        nodes: list[StudioNode] = []
        for node in self.nodes:
            nodes.extend(self._iter_subtree(node))
        return nodes

    def find_node(self, node_id: str) -> StudioNode | None:
        for node in self.iter_nodes():
            if node.node_id == node_id:
                return node
        return None

    def replace_node(self, node_id: str, replacement: StudioNode) -> bool:
        for index, node in enumerate(self.nodes):
            if node.node_id == node_id:
                self.nodes[index] = replacement
                return True
            if self._replace_child_node(node.children, node_id, replacement):
                return True
        return False

    def remove_node(self, node_id: str) -> bool:
        for index, node in enumerate(self.nodes):
            if node.node_id == node_id:
                del self.nodes[index]
                return True
            if self._remove_child_node(node.children, node_id):
                return True
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "schema_version": self.schema_version,
            "experience_level": self.experience_level,
            "nodes": [node.to_dict() for node in self.nodes],
            "theme_tokens": [asdict(token) for token in self.theme_tokens],
            "interactions": [asdict(interaction) for interaction in self.interactions],
            "workspace_state": self.workspace_state,
            "meta": self.meta,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "StudioDocument":
        return cls(
            title=str(payload.get("title", "Untitled Studio")),
            schema_version=int(payload.get("schema_version", 1)),
            experience_level=ExperienceLevel.from_value(
                str(payload.get("experience_level", ExperienceLevel.BASIC.value))
            ).value,
            nodes=[StudioNode.from_dict(node) for node in payload.get("nodes", [])],
            theme_tokens=[ThemeToken.from_dict(token) for token in payload.get("theme_tokens", [])],
            interactions=[
                InteractionDefinition.from_dict(interaction)
                for interaction in payload.get("interactions", [])
            ],
            workspace_state=dict(payload.get("workspace_state", {})),
            meta=dict(payload.get("meta", {})),
        )

    @classmethod
    def from_json(cls, raw_json: str) -> "StudioDocument":
        return cls.from_dict(json.loads(raw_json))

    @classmethod
    def example(cls) -> "StudioDocument":
        drawn_node = StudioNode(
            node_id=make_stable_id("card"),
            node_type="scene-card",
            label="Mood Board Card",
            properties={
                "x": 60,
                "y": 60,
                "width": 260,
                "height": 180,
                "fill": "#f8f3e6",
            },
        )
        widget_node = StudioNode(
            node_id=make_stable_id("widget"),
            node_type="widget-preview",
            label="Embedded Prototype",
            properties={
                "x": 380,
                "y": 120,
                "kind": "button-card",
            },
        )

        return cls(
            title="Exploration 01",
            experience_level=ExperienceLevel.BASIC.value,
            nodes=[drawn_node, widget_node],
            theme_tokens=[
                ThemeToken(name="palette.surface", value="#f8f3e6", category="palette"),
                ThemeToken(name="radius.card", value=16, category="shape"),
            ],
            interactions=[
                InteractionDefinition(
                    trigger="hover",
                    target_node_id=widget_node.node_id,
                    action="opacity-pulse",
                    payload={"duration_ms": 180},
                )
            ],
            workspace_state={"active_panel": "inspector"},
            meta={"created_with": "phase-1-scaffold"},
        )

    def _remove_child_node(self, children: list[StudioNode], node_id: str) -> bool:
        for index, child in enumerate(children):
            if child.node_id == node_id:
                del children[index]
                return True
            if self._remove_child_node(child.children, node_id):
                return True
        return False

    @staticmethod
    def _iter_subtree(node: StudioNode) -> list[StudioNode]:
        nodes = [node]
        for child in node.children:
            nodes.extend(StudioDocument._iter_subtree(child))
        return nodes

    @staticmethod
    def _replace_child_node(
        children: list[StudioNode],
        node_id: str,
        replacement: StudioNode,
    ) -> bool:
        for index, child in enumerate(children):
            if child.node_id == node_id:
                children[index] = replacement
                return True
            if StudioDocument._replace_child_node(child.children, node_id, replacement):
                return True
        return False
