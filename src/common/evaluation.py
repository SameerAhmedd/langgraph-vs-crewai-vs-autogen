"""Qualitative comparison matrix generation for thesis evaluation."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.common.output_writer import FRAMEWORK_FILE_PREFIX, write_text


CRITERIA_TO_OBSERVATION_KEYS = {
    "Architecture design": "architecture_design",
    "Workflow control": "workflow_control",
    "State handling": "state_handling",
    "Tool integration": "tool_integration",
    "Agent coordination": "agent_coordination",
    "Transparency and debugging": "transparency_and_debugging",
    "Ease of use": "ease_of_use",
    "Development complexity": "development_complexity",
    "Output structure": "output_structure",
    "Suitability for lightweight task automation": "suitability_for_lightweight_automation",
}


def load_framework_result(output_dir: Path, framework: str) -> dict[str, Any]:
    """Load one framework output JSON file."""

    prefix = FRAMEWORK_FILE_PREFIX[framework]
    path = output_dir / f"{prefix}_output.json"
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def create_comparison_rows(
    criteria: list[dict[str, Any]],
    results: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    """Create rows for the main qualitative comparison matrix."""

    rows: list[dict[str, str]] = []
    for criterion in criteria:
        criterion_name = criterion["criterion_name"]
        observation_key = CRITERIA_TO_OBSERVATION_KEYS.get(criterion_name, "")
        row = {
            "Criterion": criterion_name,
            "LangGraph Observation": _observation_for(results["LangGraph"], observation_key),
            "CrewAI Observation": _observation_for(results["CrewAI"], observation_key),
            "AutoGen Observation": _observation_for(results["AutoGen"], observation_key),
            "Notes for Thesis Interpretation": (
                "Fill with a careful interpretation after reading the generated outputs, "
                "execution logs, code, and any recorded errors. Do not assign scores for failed runs."
            ),
        }
        rows.append(row)
    return rows


def _observation_for(result: dict[str, Any], key: str) -> str:
    """Return a concise observation while respecting failed framework runs."""

    if result.get("status") == "fallback":
        return "Fallback output used; live framework execution unavailable in this run."

    if result.get("status") == "failed":
        errors = result.get("execution_metadata", {}).get("errors", [])
        return "Framework run failed; no qualitative score should be assigned automatically. " + (
            "; ".join(errors) or "No detailed error recorded."
        )

    if key == "output_structure":
        plan = result.get("final_answer_json", {})
        days = len(plan.get("daily_plan", []))
        return f"Generated normalized JSON and Markdown output with {days} daily plan entries."

    return result.get("observations", {}).get(key, "Observation not recorded.")


def create_summary_rows(results: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    """Create an optional summary table based on observed implementation behavior."""

    rows = []
    for framework, result in results.items():
        if result.get("status") == "fallback":
            rows.append(
                {
                    "Framework": framework,
                    "Main Strength": "Not assessed from fallback output.",
                    "Main Limitation": "Fallback output used; live framework execution unavailable in this run.",
                    "Best Suitable Use Case": "Requires live execution before thesis interpretation.",
                    "Implementation Complexity": "Not assessed automatically from fallback output.",
                }
            )
            continue

        if result.get("status") == "failed":
            rows.append(
                {
                    "Framework": framework,
                    "Main Strength": "Not assessed because execution failed.",
                    "Main Limitation": "; ".join(result.get("execution_metadata", {}).get("errors", [])),
                    "Best Suitable Use Case": "Requires successful setup before interpretation.",
                    "Implementation Complexity": "Not assessed automatically for failed run.",
                }
            )
            continue

        framework_notes = {
            "LangGraph": {
                "Main Strength": "Explicit graph nodes and state transitions make the workflow easy to inspect.",
                "Main Limitation": "Requires thinking in terms of state schemas and graph edges, which may be extra overhead for very small tasks.",
                "Best Suitable Use Case": "Small-to-medium workflows where state transitions and control flow should be transparent.",
                "Implementation Complexity": "Moderate: explicit state and graph setup add structure but also extra code.",
            },
            "CrewAI": {
                "Main Strength": "Role-based agents map clearly to human-readable responsibilities.",
                "Main Limitation": "The role/task abstraction can be more verbose than needed for a simple deterministic workflow.",
                "Best Suitable Use Case": "Tasks that benefit from role separation, review steps, and collaborative framing.",
                "Implementation Complexity": "Moderate to high: agent and task definitions add conceptual overhead.",
            },
            "AutoGen": {
                "Main Strength": "Conversational agent coordination is natural for multi-agent discussion and review.",
                "Main Limitation": "Conversation orchestration and message parsing can add complexity for simple structured output.",
                "Best Suitable Use Case": "Automation tasks where iterative discussion between agents is central to the design.",
                "Implementation Complexity": "Moderate to high: async execution and conversation extraction require care.",
            },
        }
        rows.append({"Framework": framework, **framework_notes[framework]})
    return rows


def write_comparison_csv(output_dir: Path, rows: list[dict[str, str]]) -> None:
    """Write the comparison matrix as CSV."""

    path = output_dir / "comparison_matrix.csv"
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def table_to_markdown(rows: list[dict[str, str]]) -> str:
    """Convert a list of dictionaries into a Markdown table."""

    if not rows:
        return ""
    headers = list(rows[0].keys())
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        values = [str(row.get(header, "")).replace("\n", " ").replace("|", "\\|") for header in headers]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def generate_comparison_matrix(
    output_dir: Path,
    criteria: list[dict[str, Any]],
    framework_results: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Generate CSV and Markdown comparison files."""

    if framework_results is None:
        results = {
            framework: load_framework_result(output_dir, framework)
            for framework in FRAMEWORK_FILE_PREFIX
        }
    else:
        results = {result["framework"]: result for result in framework_results}

    comparison_rows = create_comparison_rows(criteria, results)
    summary_rows = create_summary_rows(results)

    write_comparison_csv(output_dir, comparison_rows)
    markdown = "\n\n".join(
        [
            "# Qualitative Framework Comparison Matrix",
            (
                "This matrix should be interpreted as prototype execution evidence. "
                "Fallback outputs indicate that the framework structure was prepared, "
                "but live API execution was unavailable or disabled during this run."
            ),
            "It intentionally avoids automatic winner claims.",
            table_to_markdown(comparison_rows),
            "## Optional Interpretation Table",
            table_to_markdown(summary_rows),
        ]
    )
    write_text(output_dir / "comparison_matrix.md", markdown.strip() + "\n")
    return comparison_rows, summary_rows
