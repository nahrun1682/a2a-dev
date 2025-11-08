from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Node:
    """Light-weight representation of a flow node."""

    id: str
    label: str
    type: str  # e.g. "llm", "selector"
    loop: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "id": self.id,
            "label": self.label,
            "type": self.type,
            "loop": self.loop,
        }
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload


@dataclass
class Edge:
    """Directed edge between nodes."""

    source: str
    target: str
    label: str = ""
    edge_type: str = "default"

    def to_dict(self) -> Dict[str, str]:
        payload = {
            "from": self.source,
            "to": self.target,
            "label": self.label,
        }
        if self.edge_type != "default":
            payload["type"] = self.edge_type
        return payload


@dataclass
class FlowGraph:
    nodes: List[Node]
    edges: List[Edge]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }
