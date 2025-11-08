from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from models.node_model import Edge, FlowGraph, Node

MERMAID_BLOCK = re.compile(r"```mermaid\s*(.*?)```", re.DOTALL | re.IGNORECASE)
SQUARE_NODE = re.compile(r"(\w+)\[(.+?)\]")
CONDITION_NODE = re.compile(r"(\w+)\{(.+?)\}")
PIPE_EDGE = re.compile(r"^(\w+)\s*-->\|(.+?)\|\s*(\w+)$")
LABELED_EDGE = re.compile(r"^(\w+)\s*--\s*(.+?)\s*-->\s*(\w+)$")
PLAIN_EDGE = re.compile(r"^(\w+)\s*-->\s*(\w+)$")


def extract_mermaid_block(markdown: str) -> str:
    match = MERMAID_BLOCK.search(markdown)
    if not match:
        raise ValueError("Mermaid block not found in markdown.")
    return match.group(1).strip()


def _register_nodes(block: str) -> Dict[str, Node]:
    nodes: Dict[str, Node] = {}
    for pattern, node_type in ((SQUARE_NODE, "llm"), (CONDITION_NODE, "selector")):
        for match in pattern.finditer(block):
            node_id, label = match.groups()
            nodes[node_id] = Node(id=node_id, label=label.strip(), type=node_type)
    return nodes


def _sanitize_line(line: str) -> str:
    """Remove inline node definitions like A[Foo] for edge parsing."""

    line = re.sub(r"(\w+)\[.*?\]", r"\1", line)
    line = re.sub(r"(\w+)\{.*?\}", r"\1", line)
    return line.strip()


def _ensure_node(nodes: Dict[str, Node], node_id: str) -> None:
    if node_id not in nodes:
        nodes[node_id] = Node(id=node_id, label=node_id, type="llm")


def _parse_edges(block: str, nodes: Dict[str, Node]) -> List[Edge]:
    edges: List[Edge] = []
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.lower().startswith("flowchart") or line.startswith("%%"):
            continue

        if "-->" not in line:
            continue

        sanitized = _sanitize_line(line)
        edge_info: Tuple[str, str, str] | None = None

        for pattern in (PIPE_EDGE, LABELED_EDGE, PLAIN_EDGE):
            match = pattern.match(sanitized)
            if match:
                if pattern is PLAIN_EDGE:
                    edge_info = (match.group(1), "", match.group(2))
                else:
                    edge_info = (match.group(1), match.group(2).strip(), match.group(3))
                break

        if not edge_info:
            continue

        source, label, target = edge_info
        _ensure_node(nodes, source)
        _ensure_node(nodes, target)

        edge_type = "loop" if _is_loop_label(label) or source == target else "default"
        edges.append(Edge(source=source, target=target, label=label, edge_type=edge_type))
    return edges


def _is_loop_label(label: str) -> bool:
    return bool(label) and "loop" in label.lower()


def _mark_loop_nodes(nodes: Dict[str, Node], edges: Iterable[Edge]) -> None:
    reverse_lookup = {(edge.source, edge.target) for edge in edges}
    loop_nodes = set()

    for edge in edges:
        if edge.source == edge.target:
            loop_nodes.add(edge.source)
        if _is_loop_label(edge.label):
            loop_nodes.update({edge.source, edge.target})
        if (edge.target, edge.source) in reverse_lookup and edge.source != edge.target:
            loop_nodes.update({edge.source, edge.target})

    for node_id in loop_nodes:
        if node_id in nodes:
            nodes[node_id].loop = True
            nodes[node_id].metadata.setdefault("loop_reason", "edge_cycle")


def parse_markdown(path: Path) -> FlowGraph:
    markdown = path.read_text(encoding="utf-8")
    mermaid_block = extract_mermaid_block(markdown)
    nodes = _register_nodes(mermaid_block)
    edges = _parse_edges(mermaid_block, nodes)
    _mark_loop_nodes(nodes, edges)
    ordered_nodes = list(nodes.values())
    return FlowGraph(nodes=ordered_nodes, edges=edges)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Mermaid flowchart markdown into JSON.")
    parser.add_argument("markdown_path", help="Path to the markdown file containing the Mermaid diagram.")
    parser.add_argument(
        "-o",
        "--output",
        help="Optional path to save the generated JSON. Stdout is used when omitted.",
    )
    args = parser.parse_args()

    graph = parse_markdown(Path(args.markdown_path))
    payload = graph.to_dict()
    json_data = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json_data, encoding="utf-8")
    else:
        print(json_data)


if __name__ == "__main__":
    main()
