"""Tests for study-plan validation and Markdown rendering."""

import copy

import pytest

from src.common.study_plan import (
    build_fallback_study_plan,
    extract_json_object,
    normalize_activities,
    study_plan_to_markdown,
    validate_study_plan,
)

import json


def _plan() -> dict:
    return build_fallback_study_plan({"task_id": "t"}, "LangGraph")


def test_string_activity_is_normalised_to_list() -> None:
    plan = _plan()
    plan["daily_plan"][0]["study_activities"] = "Watch Python basics video."

    validate_study_plan(plan)

    assert plan["daily_plan"][0]["study_activities"] == ["Watch Python basics video."]


def test_markdown_does_not_split_strings_into_characters() -> None:
    plan = _plan()
    plan["daily_plan"][0]["study_activities"] = "Watch Python basics video."

    markdown = study_plan_to_markdown(plan)

    assert "- Watch Python basics video." in markdown
    assert "- W\n- a\n- t" not in markdown


def test_extract_json_object_accepts_string_activities() -> None:
    plan = _plan()
    plan["daily_plan"][2]["study_activities"] = "Read file handling guide."

    parsed = extract_json_object(json.dumps(plan))

    assert parsed["daily_plan"][2]["study_activities"] == ["Read file handling guide."]


def test_empty_or_wrong_type_activities_are_rejected() -> None:
    with pytest.raises(ValueError):
        normalize_activities([])
    with pytest.raises(ValueError):
        normalize_activities(42)


def test_plan_must_have_exactly_seven_days() -> None:
    plan = copy.deepcopy(_plan())
    plan["daily_plan"].pop()

    with pytest.raises(ValueError):
        validate_study_plan(plan)
