import importlib

from google.adk.agents import SequentialAgent


def test_generated_workflow_exports_root_agent():
    workflow_module = importlib.import_module("generated.workflow")

    assert hasattr(workflow_module, "root_agent")
    root_agent = workflow_module.root_agent
    assert isinstance(root_agent, SequentialAgent)
    assert root_agent.sub_agents, "SequentialAgent should include sub agents."

    assert hasattr(workflow_module, "node_registry")
    assert "B" in workflow_module.node_registry  # selector node present
