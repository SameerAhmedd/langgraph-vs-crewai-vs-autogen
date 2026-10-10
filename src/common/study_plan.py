"""Shared study-plan helpers used by all framework implementations."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from typing import Any


DEFAULT_DAYS = [
    {
        "topic": "Python basics and revision setup",
        "learning_goal": "Refresh variables, data types, control flow, and the study workflow.",
        "study_activities": [
            "Review variables, strings, numbers, lists, dictionaries, and conditionals.",
            "Write small examples for loops, functions, and basic error messages."
        ],
        "practice_task": "Create a Python script that stores five study topics in a list and prints a numbered checklist.",
        "expected_outcome": "Student can explain and run basic Python syntax confidently."
    },
    {
        "topic": "Functions and modular thinking",
        "learning_goal": "Practice writing reusable functions with clear inputs and outputs.",
        "study_activities": [
            "Revise function definitions, parameters, return values, and simple docstrings.",
            "Break one larger problem into two or three smaller helper functions."
        ],
        "practice_task": "Write functions that calculate average study time and classify progress as low, medium, or high.",
        "expected_outcome": "Student can structure beginner-level Python code into readable functions."
    },
    {
        "topic": "File handling",
        "learning_goal": "Understand reading, writing, and safely closing text files.",
        "study_activities": [
            "Review open(), with-statements, read(), write(), and common file paths.",
            "Practice handling missing files with simple try/except blocks."
        ],
        "practice_task": "Create a script that writes daily study notes to a text file and reads them back.",
        "expected_outcome": "Student can use basic file input and output in a controlled script."
    },
    {
        "topic": "Regular expressions",
        "learning_goal": "Use regular expressions for simple pattern matching and text extraction.",
        "study_activities": [
            "Revise literals, character classes, quantifiers, groups, and re.findall().",
            "Test patterns on short strings before applying them to longer text."
        ],
        "practice_task": "Extract email-like strings and dates from a short block of sample text.",
        "expected_outcome": "Student can apply simple regex patterns and explain what they match."
    },
    {
        "topic": "Simple data analysis with lists and dictionaries",
        "learning_goal": "Analyze small datasets using core Python data structures.",
        "study_activities": [
            "Represent tabular information as lists of dictionaries.",
            "Calculate totals, averages, minimums, and maximums with loops."
        ],
        "practice_task": "Analyze a list of fictional quiz scores and print average score, highest score, and pass count.",
        "expected_outcome": "Student can perform small data analysis tasks without advanced libraries."
    },
    {
        "topic": "Introductory pandas-style data analysis",
        "learning_goal": "Understand how simple data analysis can be organized in tables.",
        "study_activities": [
            "Review the idea of rows, columns, filtering, and summary statistics.",
            "If pandas is available, create a small DataFrame and calculate summary values."
        ],
        "practice_task": "Build a small table of study sessions and summarize total hours per topic.",
        "expected_outcome": "Student can connect basic Python structures to tabular analysis concepts."
    },
    {
        "topic": "Integrated mini project and review",
        "learning_goal": "Combine Python basics, files, regex, and simple analysis in one small task.",
        "study_activities": [
            "Review notes from the previous six days and identify weak areas.",
            "Design a small script before coding it, then test it with sample input."
        ],
        "practice_task": "Create a script that reads sample notes, extracts keywords with regex, and summarizes topic frequency.",
        "expected_outcome": "Student completes a practical revision project and has a clear next-step study list."
    }
]


def build_fallback_study_plan(task: dict[str, Any], framework: str) -> dict[str, Any]:
    """Create deterministic fallback output without pretending to be LLM generated."""

    daily_plan = []
    for index, day in enumerate(DEFAULT_DAYS, start=1):
        daily_plan.append({"day": index, **day})

    return {
        "title": f"Fallback demonstration output: 7-day study plan generated through {framework}",
        "overview": (
            "This is fallback demonstration output generated because the live LLM/API call "
            "was unavailable or disabled. It verifies project structure and file generation, "
            "but it should not be treated as real LLM output."
        ),
        "daily_plan": daily_plan,
        "summary": (
            "The plan covers Python basics, file handling, regular expressions, and "
            "simple data analysis in seven two-hour study sessions."
        ),
    }


def generate_fallback_study_plan(framework_name: str, task: dict[str, Any], reason: str) -> dict[str, Any]:
    """Return a full framework result using deterministic fallback content."""

    started = datetime.now(timezone.utc)
    start_time = time.perf_counter()
    plan = build_fallback_study_plan(task, framework_name)
    markdown = (
        "This is fallback demonstration output generated because the live LLM/API call "
        "was unavailable or disabled.\n\n"
        f"Fallback reason: {reason}\n\n"
        f"{study_plan_to_markdown(plan)}"
    )
    completed = datetime.now(timezone.utc)

    return {
        "framework": framework_name,
        "task_id": task.get("task_id", ""),
        "status": "fallback",
        "final_answer_markdown": markdown,
        "final_answer_json": plan,
        "observations": {
            "architecture_design": (
                f"{framework_name} workflow structure is present, but live execution was skipped "
                "or unavailable in this run."
            ),
            "workflow_control": "Fallback output used; live framework execution unavailable in this run.",
            "state_handling": "Fallback output follows the same normalized JSON and Markdown structure.",
            "tool_integration": "Shared fallback generator, Markdown formatter, and output writer were used.",
            "agent_coordination": "Live agent coordination was not evaluated during fallback execution.",
            "transparency_and_debugging": f"Fallback reason recorded: {reason}",
            "ease_of_use": "Not scored from fallback output.",
            "development_complexity": "Not scored from fallback output.",
            "suitability_for_lightweight_automation": "Not scored from fallback output.",
        },
        "execution_metadata": {
            "started_at": started.isoformat(),
            "completed_at": completed.isoformat(),
            "duration_seconds": round(time.perf_counter() - start_time, 3),
            "reason": reason,
            "errors": [reason] if "failed" in reason.lower() or "error" in reason.lower() else [],
        },
    }


def study_plan_to_markdown(plan: dict[str, Any]) -> str:
    """Convert the normalized study-plan JSON object to Markdown."""

    lines = [f"# {plan.get('title', 'Study Plan')}", "", plan.get("overview", ""), ""]
    for item in plan.get("daily_plan", []):
        lines.extend(
            [
                f"## Day {item.get('day')}: {item.get('topic')}",
                f"**Learning goal:** {item.get('learning_goal')}",
                "",
                "**Study activities:**",
            ]
        )
        activities = item.get("study_activities", [])
        if isinstance(activities, str):  # defensive: never render a string character by character
            activities = [activities]
        for activity in activities:
            lines.append(f"- {activity}")
        lines.extend(
            [
                "",
                f"**Practice task:** {item.get('practice_task')}",
                f"**Expected outcome:** {item.get('expected_outcome')}",
                "",
            ]
        )
    lines.extend(["## Summary", plan.get("summary", "")])
    return "\n".join(lines).strip() + "\n"


def build_study_plan_prompt(task: dict[str, Any], framework: str) -> str:
    """Build a shared prompt so the task is equivalent across frameworks."""

    return f"""
You are generating an academic prototype output for a Bachelor thesis comparison of agentic AI frameworks.
Framework being executed: {framework}

Student profile: {task["student_profile"]}
Goal: {task["goal"]}
Constraints: {json.dumps(task["constraints"], indent=2)}

Produce only valid JSON with this structure:
{{
  "title": "string",
  "overview": "string",
  "daily_plan": [
    {{
      "day": 1,
      "topic": "string",
      "learning_goal": "string",
      "study_activities": ["string", "string"],
      "practice_task": "string",
      "expected_outcome": "string"
    }}
  ],
  "summary": "string"
}}

The daily_plan must contain exactly seven days. Each day should fit a 2-hour beginner-friendly study session.
""".strip()


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract and parse a JSON object from a model response."""

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise
        parsed = json.loads(match.group(0))

    if not isinstance(parsed, dict):
        raise ValueError("Model response did not contain a JSON object.")
    validate_study_plan(parsed)
    return parsed


def validate_study_plan(plan: dict[str, Any]) -> None:
    """Validate the common study-plan shape used for comparison."""

    required_fields = {"title", "overview", "daily_plan", "summary"}
    missing_fields = required_fields - set(plan)
    if missing_fields:
        raise ValueError(f"Study plan is missing fields: {sorted(missing_fields)}")

    daily_plan = plan.get("daily_plan")
    if not isinstance(daily_plan, list) or len(daily_plan) != 7:
        raise ValueError("Study plan must contain exactly seven daily_plan entries.")

    day_fields = {
        "day",
        "topic",
        "learning_goal",
        "study_activities",
        "practice_task",
        "expected_outcome",
    }
    for item in daily_plan:
        if not isinstance(item, dict):
            raise ValueError("Each daily_plan entry must be an object.")
        missing_day_fields = day_fields - set(item)
        if missing_day_fields:
            raise ValueError(f"Daily plan entry is missing fields: {sorted(missing_day_fields)}")
        # Models sometimes return a single string instead of a list when the prompt
        # asks for "one" item. Normalise it so downstream code never iterates a string.
        item["study_activities"] = normalize_activities(item["study_activities"])


def normalize_activities(value: Any) -> list[str]:
    """Return study activities as a list of non-empty strings."""

    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        raise ValueError("study_activities must be a string or a list of strings.")
    activities = [str(entry).strip() for entry in value if str(entry).strip()]
    if not activities:
        raise ValueError("study_activities must contain at least one activity.")
    return activities


def empty_plan() -> dict[str, Any]:
    """Return an empty JSON-compatible plan for failed framework runs."""

    return {"title": "", "overview": "", "daily_plan": [], "summary": ""}
