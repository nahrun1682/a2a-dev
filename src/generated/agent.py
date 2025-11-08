from __future__ import annotations

from typing import Any, Dict, List

from google.adk.agents import Agent, LoopAgent, SequentialAgent

from models.state_model import WorkflowState
from tools.mcp_client import call_mcp_tool

DEFAULT_MODEL = "gemini-2.5-flash"
BASE_REACT_INSTRUCTION = """You operate inside a generated ReAct workflow. Follow this loop:
1. Reason step-by-step about the assigned node.
2. Decide whether to call `call_mcp_tool` (mocked MCP).
3. Observe the tool result and refine your plan.
4. Stop when your response contains 'OK'.

Persist helpful context inside session state via callbacks or tool outputs."""

GRAPH_DEFINITION: Dict[str, Any] = {
    "nodes": [{'id': 'A',
  'is_selector': False,
  'label': 'Input',
  'loop': False,
  'metadata': {},
  'type': 'llm',
  'var_name': 'a_agent'},
 {'id': 'C',
  'is_selector': False,
  'label': 'Weather',
  'loop': False,
  'metadata': {},
  'type': 'llm',
  'var_name': 'c_agent'},
 {'id': 'D',
  'is_selector': False,
  'label': 'General',
  'loop': False,
  'metadata': {},
  'type': 'llm',
  'var_name': 'd_agent'},
 {'id': 'E',
  'is_selector': False,
  'label': 'Refine',
  'loop': True,
  'metadata': {'loop_reason': 'edge_cycle'},
  'type': 'llm',
  'var_name': 'e_agent'},
 {'id': 'F',
  'is_selector': False,
  'label': 'Finalize',
  'loop': False,
  'metadata': {},
  'type': 'llm',
  'var_name': 'f_agent'},
 {'id': 'B',
  'is_selector': True,
  'label': '天気の質問？',
  'loop': False,
  'metadata': {},
  'type': 'selector',
  'var_name': 'b_agent'}],
    "edges": [{'from': 'A', 'label': '', 'to': 'B', 'type': 'default'},
 {'from': 'B', 'label': 'Yes', 'to': 'C', 'type': 'default'},
 {'from': 'B', 'label': 'No', 'to': 'D', 'type': 'default'},
 {'from': 'C', 'label': '', 'to': 'E', 'type': 'default'},
 {'from': 'D', 'label': '', 'to': 'E', 'type': 'default'},
 {'from': 'E', 'label': 'loop', 'to': 'E', 'type': 'loop'},
 {'from': 'E', 'label': '', 'to': 'F', 'type': 'default'}],
    "order": ['A', 'B', 'C', 'D', 'E', 'F'],
}

SELECTOR_ROUTES: Dict[str, List[Dict[str, str]]] = {
    "B": [{'label': 'Yes', 'normalized': 'yes', 'polarity': 'positive', 'target': 'C'},
 {'label': 'No', 'normalized': 'no', 'polarity': 'negative', 'target': 'D'}],
}


def build_instruction(label: str, node_id: str) -> str:
    return BASE_REACT_INSTRUCTION + f"\nCurrent node ({node_id}): {label}."


class SelectorAgent:
    """Documentation-first placeholder describing conditional routes.

    Real branching happens via shared session state and the surrounding
    SequentialAgent ordering, but keeping this structure makes it easy to
    replace with an ADK-native Router in the future.
    """

    def __init__(self, name: str, routes: List[Dict[str, str]]):
        self.name = name
        self.routes = routes

    def as_dict(self) -> Dict[str, List[Dict[str, str]]]:
        return {"name": self.name, "routes": self.routes}


workflow_state = WorkflowState().to_dict()

# === Auto-generated Agent Definitions ===
a_agent = Agent(
    name="a",
    model=DEFAULT_MODEL,
    description="Auto-generated step for Input",
    instruction=build_instruction("Input", "A"),
    tools=[call_mcp_tool],
)
c_agent = Agent(
    name="c",
    model=DEFAULT_MODEL,
    description="Auto-generated step for Weather",
    instruction=build_instruction("Weather", "C"),
    tools=[call_mcp_tool],
)
d_agent = Agent(
    name="d",
    model=DEFAULT_MODEL,
    description="Auto-generated step for General",
    instruction=build_instruction("General", "D"),
    tools=[call_mcp_tool],
)
e_agent = Agent(
    name="e",
    model=DEFAULT_MODEL,
    description="Auto-generated step for Refine",
    instruction=build_instruction("Refine", "E"),
    tools=[call_mcp_tool],
)
e_agent_loop = LoopAgent(
    name="e_loop",
    description="Loop wrapper for Refine",
    sub_agents=[e_agent],
    max_iterations=5,
)
f_agent = Agent(
    name="f",
    model=DEFAULT_MODEL,
    description="Auto-generated step for Finalize",
    instruction=build_instruction("Finalize", "F"),
    tools=[call_mcp_tool],
)
b_agent = Agent(
    name="b",
    model=DEFAULT_MODEL,
    description="Auto-generated step for 天気の質問？",
    instruction=build_instruction("天気の質問？", "B"),
    tools=[call_mcp_tool],
)

node_registry = {
    "A": a_agent,
    "C": c_agent,
    "D": d_agent,
    "E": e_agent_loop,
    "F": f_agent,
    "B": b_agent,
}

selector_registry = {
    "B": SelectorAgent(
        name="b_selector",
        routes=[{'label': 'Yes', 'normalized': 'yes', 'polarity': 'positive', 'target': 'C'},
 {'label': 'No', 'normalized': 'no', 'polarity': 'negative', 'target': 'D'}],
    ),
}

workflow_sequence = [
    node_registry["A"],
    node_registry["B"],
    node_registry["C"],
    node_registry["D"],
    node_registry["E"],
    node_registry["F"],
]

root_agent = SequentialAgent(
    name="generated_workflow",
    description="Workflow compiled from Mermaid flowchart.",
    sub_agents=workflow_sequence,
)