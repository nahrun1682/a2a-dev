import json
from pathlib import Path

from compiler import render_workflow


def build_dummy_graph(tmp_path: Path) -> Path:
    data = {
        "nodes": [
            {"id": "A", "label": "Start", "type": "llm", "loop": False},
            {"id": "B", "label": "Decide", "type": "selector", "loop": False},
            {"id": "C", "label": "Finish", "type": "llm", "loop": True},
        ],
        "edges": [
            {"from": "A", "to": "B", "label": ""},
            {"from": "B", "to": "C", "label": "Yes"},
            {"from": "C", "to": "C", "label": "loop", "type": "loop"},
        ],
    }
    path = tmp_path / "graph.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_compiler_renders_jinja_template(tmp_path):
    graph_path = build_dummy_graph(tmp_path)
    template_dir = Path("src/templates")
    output_path = tmp_path / "workflow.py"

    render_workflow(graph_path, template_dir, output_path, model="gemini-2.5-flash")

    generated = output_path.read_text(encoding="utf-8")
    assert "SequentialAgent" in generated
    assert "LoopAgent" in generated
    assert "SelectorAgent" in generated
