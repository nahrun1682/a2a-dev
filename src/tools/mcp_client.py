from __future__ import annotations

from typing import Any, Dict

from rich.console import Console

console = Console()


def call_mcp_tool(name: str, **kwargs: Any) -> Dict[str, Any]:
    """Mock MCP client to keep the interface swappable later."""

    console.log(f"[bold cyan]MCP mock[/] :: {name}({kwargs})")
    return {
        "tool": name,
        "status": "success",
        "input": kwargs,
        "output": f"{name} executed with inputs {kwargs}",
    }
