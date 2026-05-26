"""Tests for synthetic task loading."""

from pathlib import Path

from src.common.task_loader import load_input_task


def test_input_task_loads_correctly() -> None:
    task = load_input_task(Path("data/input_tasks.json"))

    assert task["task_id"] == "study-plan-001"
    assert task["constraints"]["duration_days"] == 7
    assert "Python" in task["goal"]

