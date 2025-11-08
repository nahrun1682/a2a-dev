from pathlib import Path

from flow_parser import parse_markdown


def test_sample_flow_parses_selector_and_loop():
    graph = parse_markdown(Path("docs/sample_flow.md"))

    selector_nodes = [node for node in graph.nodes if node.type == "selector"]
    assert selector_nodes, "Expected at least one selector node."
    assert selector_nodes[0].label == "天気の質問？"

    yes_edges = [
        edge for edge in graph.edges if edge.source == "B" and edge.target == "C"
    ]
    assert yes_edges and yes_edges[0].label.lower() == "yes"

    loop_nodes = [node for node in graph.nodes if node.loop]
    assert any(node.id == "E" for node in loop_nodes), "Refine node should be loop-enabled."

    loop_edges = [edge for edge in graph.edges if edge.edge_type == "loop"]
    assert loop_edges, "Loop edge metadata should be preserved."
