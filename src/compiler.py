from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape

from models.node_model import Edge, Node

DEFAULT_MODEL = "gemini-2.5-flash"


def _load_nodes(node_payload: List[dict]) -> Dict[str, Node]:
    nodes: Dict[str, Node] = {}
    for raw in node_payload:
        node = Node(
            id=raw["id"],
            label=raw.get("label", raw["id"]),
            type=raw.get("type", "llm"),
            loop=raw.get("loop", False),
            metadata=raw.get("metadata") or {},
        )
        nodes[node.id] = node
    return nodes


def _load_edges(edge_payload: List[dict]) -> List[Edge]:
    edges: List[Edge] = []
    for raw in edge_payload:
        edges.append(
            Edge(
                source=raw["from"],
                target=raw["to"],
                label=raw.get("label", ""),
                edge_type=raw.get("type", "default"),
            )
        )
    return edges


def _var_name(node_id: str) -> str:
    safe = re.sub(r"[^0-9a-zA-Z_]", "_", node_id)
    return f"{safe.lower()}_agent"


def _topological_order(nodes: Dict[str, Node], edges: List[Edge]) -> List[str]:
    indegree = {node_id: 0 for node_id in nodes}
    adjacency: Dict[str, List[str]] = {node_id: [] for node_id in nodes}

    for edge in edges:
        if edge.source == edge.target:
            continue
        adjacency.setdefault(edge.source, []).append(edge.target)
        indegree[edge.target] = indegree.get(edge.target, 0) + 1

    queue = [node_id for node_id, degree in indegree.items() if degree == 0]
    ordered: List[str] = []

    while queue:
        current = queue.pop(0)
        ordered.append(current)

        for neighbor in adjacency.get(current, []):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(ordered) != len(nodes):
        # Fall back to the declared order for any nodes left inside cycles.
        remaining = [node_id for node_id in nodes if node_id not in ordered]
        ordered.extend(remaining)

    return ordered


def _selector_routes(node_id: str, edges: List[Edge]) -> List[dict]:
    routes = []
    for edge in edges:
        if edge.source != node_id:
            continue
        label = edge.label or ""
        normalized = label.strip().lower()
        polarity = "neutral"
        if normalized in {"yes", "true"}:
            polarity = "positive"
        elif normalized in {"no", "false"}:
            polarity = "negative"
        elif "loop" in normalized:
            polarity = "loop"
        routes.append(
            {
                "label": label,
                "normalized": normalized,
                "polarity": polarity,
                "target": edge.target,
            }
        )
    return routes


def _build_template_payload(nodes: Dict[str, Node], edges: List[Edge], model: str) -> dict:
    ordered_ids = _topological_order(nodes, edges)
    selector_map = {
        node_id: _selector_routes(node_id, edges)
        for node_id, node in nodes.items()
        if node.type == "selector"
    }

    rendered_nodes = []
    for node_id, node in nodes.items():
        rendered_nodes.append(
            {
                "id": node_id,
                "label": node.label,
                "type": node.type,
                "loop": node.loop,
                "metadata": node.metadata,
                "var_name": _var_name(node_id),
                "is_selector": node.type == "selector",
            }
        )

    payload = {
        "model": model or DEFAULT_MODEL,
        "nodes": rendered_nodes,
        "edges": [
            {"from": edge.source, "to": edge.target, "label": edge.label, "type": edge.edge_type}
            for edge in edges
        ],
        "ordered_node_ids": ordered_ids,
        "selector_routes": selector_map,
        "loop_nodes": [node_id for node_id, node in nodes.items() if node.loop],
        "has_selector": bool(selector_map),
    }
    return payload


def render_workflow(graph_json: Path, template_dir: Path, output_path: Path, model: str) -> None:
    payload = json.loads(graph_json.read_text(encoding="utf-8"))
    nodes = _load_nodes(payload.get("nodes", []))
    edges = _load_edges(payload.get("edges", []))
    context = _build_template_payload(nodes, edges, model)

    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(default_for_string=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("adk_flow.jinja2")
    rendered = template.render(**context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    print(f"Generated workflow at {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile Mermaid graph JSON into an ADK workflow.")
    parser.add_argument("graph_json", help="Path to the JSON produced by flow_parser.py")
    parser.add_argument("template_dir", help="Directory containing adk_flow.jinja2")
    parser.add_argument("output_path", help="Path for the generated workflow.py file")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Gemini model to use for generated agents",
    )
    args = parser.parse_args()

    render_workflow(
        graph_json=Path(args.graph_json),
        template_dir=Path(args.template_dir),
        output_path=Path(args.output_path),
        model=args.model,
    )


if __name__ == "__main__":
    main()
