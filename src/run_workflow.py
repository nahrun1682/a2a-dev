from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import List


def run_workflow(adk_bin: str, workflow_path: Path, extra_args: List[str]) -> int:
    command = [adk_bin, "run", str(workflow_path), *extra_args]
    completed = subprocess.run(command, check=False)
    return completed.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="Wrapper around `adk run` for the generated workflow.")
    parser.add_argument(
        "--workflow",
        default="src/generated/workflow.py",
        help="Path to the generated workflow file.",
    )
    parser.add_argument("--adk-bin", default="adk", help="ADK executable to use.")
    parser.add_argument(
        "extra",
        nargs=argparse.REMAINDER,
        help="Additional arguments forwarded to `adk run` (pass after `--`).",
    )
    args = parser.parse_args()
    workflow_path = Path(args.workflow).resolve()

    if not workflow_path.exists():
        raise SystemExit(f"Workflow file not found: {workflow_path}")

    exit_code = run_workflow(args.adk_bin, workflow_path, args.extra)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
