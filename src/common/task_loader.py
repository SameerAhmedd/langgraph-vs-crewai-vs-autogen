"""Helpers for loading synthetic task and evaluation data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json_file(path: Path) -> dict[str, Any] | list[dict[str, Any]]:
    """Load a JSON file and return its parsed content."""

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_input_task(path: Path) -> dict[str, Any]:
    """Load the synthetic study-plan task description."""

    data = load_json_file(path)
    if not isinstance(data, dict):
        raise ValueError("Input task JSON must contain one task object.")

    required_fields = {"task_id", "task_title", "student_profile", "goal", "constraints"}
    missing_fields = required_fields - set(data)
    if missing_fields:
        raise ValueError(f"Input task is missing required fields: {sorted(missing_fields)}")

    return data


def load_evaluation_criteria(path: Path) -> list[dict[str, Any]]:
    """Load qualitative evaluation criteria."""

    data = load_json_file(path)
    if not isinstance(data, list):
        raise ValueError("Evaluation criteria JSON must contain a list of criteria.")
    return data

