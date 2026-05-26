"""Tests for comparison matrix generation."""

from src.common.evaluation import generate_comparison_matrix
from src.common.logging_utils import base_observations
from src.common.study_plan import build_fallback_study_plan, study_plan_to_markdown


def _result(framework: str) -> dict:
    task = {"task_id": "test-task"}
    plan = build_fallback_study_plan(task, framework)
    return {
        "framework": framework,
        "task_id": "test-task",
        "status": "success",
        "final_answer_markdown": study_plan_to_markdown(plan),
        "final_answer_json": plan,
        "observations": base_observations(framework, True),
        "execution_metadata": {
            "started_at": "2026-01-01T00:00:00+00:00",
            "completed_at": "2026-01-01T00:00:01+00:00",
            "duration_seconds": 1,
            "errors": [],
        },
    }


def test_comparison_matrix_is_generated(tmp_path) -> None:
    criteria = [
        {
            "criterion_name": "Architecture design",
            "description": "",
            "observation_method": "",
            "rating_scale": "1 to 5",
            "notes_field": "",
        }
    ]
    framework_results = [_result("LangGraph"), _result("CrewAI"), _result("AutoGen")]

    rows, summary_rows = generate_comparison_matrix(tmp_path, criteria, framework_results)

    assert rows
    assert summary_rows
    assert (tmp_path / "comparison_matrix.csv").exists()
    assert (tmp_path / "comparison_matrix.md").exists()

