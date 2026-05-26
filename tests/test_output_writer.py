"""Tests for framework output writing."""

from src.common.output_writer import write_framework_outputs
from src.common.study_plan import build_fallback_study_plan, study_plan_to_markdown


def test_output_files_can_be_written(tmp_path) -> None:
    task = {
        "task_id": "test-task",
        "task_title": "Test task",
        "student_profile": "Synthetic student",
        "goal": "Test goal",
        "constraints": {"duration_days": 7},
    }
    plan = build_fallback_study_plan(task, "LangGraph")
    result = {
        "framework": "LangGraph",
        "task_id": "test-task",
        "status": "success",
        "final_answer_markdown": study_plan_to_markdown(plan),
        "final_answer_json": plan,
        "observations": {},
        "execution_metadata": {
            "started_at": "2026-01-01T00:00:00+00:00",
            "completed_at": "2026-01-01T00:00:01+00:00",
            "duration_seconds": 1,
            "errors": [],
        },
    }

    write_framework_outputs(tmp_path, result, task)

    assert (tmp_path / "langgraph_output.json").exists()
    assert (tmp_path / "langgraph_output.md").exists()

