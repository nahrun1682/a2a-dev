from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class WorkflowState:
    """Shared session/context placeholder for generated workflows."""

    context: Dict[str, Any] = field(default_factory=dict)
    output: str = ""
    last_tool_result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context": self.context,
            "output": self.output,
            "last_tool_result": self.last_tool_result,
        }


StateDict = Dict[str, Any]
