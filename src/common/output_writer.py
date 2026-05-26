"""Utilities for saving framework outputs and execution logs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FRAMEWORK_FILE_PREFIX = {
    "LangGraph": "langgraph",
    "CrewAI": "crewai",
    "AutoGen": "autogen",
}


def ensure_output_dir(output_dir: Path) -> None:
    """Create the output directory if it does not exist."""

    output_dir.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: Any) -> None:
    """Write JSON with stable formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")


def write_text(path: Path, content: str) -> None:
    """Write UTF-8 text content."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        file.write(content)


def framework_result_to_markdown(result: dict[str, Any], task: dict[str, Any]) -> str:
    """Create a readable Markdown report for one framework result."""

    metadata = result.get("execution_metadata", {})
    observations = result.get("observations", {})
    errors = metadata.get("errors", [])

    lines = [
        f"# {result.get('framework', 'Framework')} Output",
        "",
        "## Task Description",
        f"- Task ID: {task.get('task_id')}",
        f"- Task title: {task.get('task_title')}",
        f"- Student profile: {task.get('student_profile')}",
        f"- Goal: {task.get('goal')}",
        f"- Constraints: {json.dumps(task.get('constraints', {}), ensure_ascii=False)}",
        "",
        "## Execution Status",
        f"- Status: {result.get('status')}",
        f"- Started at: {metadata.get('started_at', '')}",
        f"- Completed at: {metadata.get('completed_at', '')}",
        f"- Duration seconds: {metadata.get('duration_seconds', 0)}",
        "",
        "## Final Generated Study Plan",
        result.get("final_answer_markdown") or "No final study plan was generated.",
        "",
        "## Observed Workflow Behavior",
    ]

    for key, value in observations.items():
        readable_key = key.replace("_", " ").title()
        lines.append(f"- **{readable_key}:** {value}")

    lines.extend(["", "## Notes for Thesis Discussion"])
    if result.get("status") == "success":
        lines.append(
            "This output can be inspected as an observed run of the prototype. "
            "Interpretation should consider fallback mode, model behavior, dependencies, and prompt design."
        )
    elif result.get("status") == "fallback":
        lines.append(
            "Fallback output was used. The framework structure was prepared, but live API execution "
            "was unavailable or disabled during this run."
        )
    else:
        lines.append(
            "This failed run is still relevant for the thesis discussion because dependency, API, "
            "or version limitations are part of practical framework evaluation."
        )

    lines.extend(["", "## Errors or Limitations"])
    if metadata.get("reason"):
        lines.append(f"- Reason: {metadata.get('reason')}")
    if errors:
        for error in errors:
            lines.append(f"- {error}")
    elif not metadata.get("reason"):
        lines.append("- No runtime errors were recorded.")

    return "\n".join(lines).strip() + "\n"


def write_framework_outputs(output_dir: Path, result: dict[str, Any], task: dict[str, Any]) -> None:
    """Write JSON and Markdown files for one framework."""

    ensure_output_dir(output_dir)
    framework = result.get("framework", "")
    prefix = FRAMEWORK_FILE_PREFIX.get(framework, framework.lower().replace(" ", "_"))

    write_json(output_dir / f"{prefix}_output.json", result)
    write_text(output_dir / f"{prefix}_output.md", framework_result_to_markdown(result, task))


def write_execution_log(output_dir: Path, results: list[dict[str, Any]]) -> None:
    """Write a compact execution log for all framework runs."""

    log_entries = []
    for result in results:
        metadata = result.get("execution_metadata", {})
        errors = metadata.get("errors", [])
        log_entries.append(
            {
                "framework": result.get("framework"),
                "status": result.get("status"),
                "reason": metadata.get("reason", ""),
                "error": "; ".join(errors),
                "duration_seconds": metadata.get("duration_seconds", 0),
            }
        )
    write_json(output_dir / "execution_log.json", log_entries)
