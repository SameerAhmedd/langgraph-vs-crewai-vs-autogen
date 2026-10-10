"""Tests for the LangGraph workflow that run without network access or an API key."""

from pathlib import Path
from types import SimpleNamespace

import pytest

pytest.importorskip("langgraph")

from config.settings import Settings
from src.common.study_plan import build_fallback_study_plan
from src.common.task_loader import load_input_task
from src.langgraph_impl import langgraph_workflow as lgw


def _settings(**overrides) -> Settings:
    values = dict(
        base_dir=Path("."),
        data_dir=Path("data"),
        outputs_dir=Path("outputs"),
        openai_api_key="test-key",
        openai_model="gpt-4o-mini",
        openai_base_url=None,
        mock_mode=False,
        low_cost_mode=True,
        run_langgraph=True,
        run_crewai=False,
        run_autogen=False,
        max_output_tokens=1500,
        request_timeout_seconds=30,
        max_retries=1,
        use_fallback_mode=False,
    )
    values.update(overrides)
    return Settings(**values)


def _task() -> dict:
    return load_input_task(Path("data/input_tasks.json"))


def test_graph_state_reaches_the_llm_prompt(monkeypatch) -> None:
    captured = {}

    def fake_generate(prompt, settings):
        captured["prompt"] = prompt
        return build_fallback_study_plan(_task(), "LangGraph")

    monkeypatch.setattr(lgw, "_generate_plan_with_langchain", fake_generate)

    result = lgw.run_langgraph_workflow(_task(), _settings())

    assert result["status"] == "success"
    # Output of the goal-decomposition node must be visible to the generation node.
    assert "Apply regular expressions to extract structured text." in captured["prompt"]
    # Output of the requirement-analysis node must be visible too.
    assert "study_time_per_day" in captured["prompt"]


def test_step_log_is_saved_in_execution_metadata(monkeypatch) -> None:
    monkeypatch.setattr(
        lgw,
        "_generate_plan_with_langchain",
        lambda prompt, settings: build_fallback_study_plan(_task(), "LangGraph"),
    )

    result = lgw.run_langgraph_workflow(_task(), _settings())

    assert len(result["execution_metadata"]["step_log"]) == 4


def test_truncated_model_output_raises_clear_error(monkeypatch) -> None:
    class FakeLLM:
        def __init__(self, **kwargs):
            pass

        def bind(self, **kwargs):
            return self

        def invoke(self, prompt):
            return SimpleNamespace(content='{"title": "cut off', response_metadata={"finish_reason": "length"})

    monkeypatch.setitem(__import__("sys").modules, "langchain_openai", SimpleNamespace(ChatOpenAI=FakeLLM))

    with pytest.raises(ValueError, match="truncated"):
        lgw._generate_plan_with_langchain("prompt", _settings(max_output_tokens=500))


def test_truncation_falls_back_instead_of_crashing(monkeypatch) -> None:
    def boom(prompt, settings):
        raise ValueError("Model output was truncated at max_tokens=500; increase MAX_OUTPUT_TOKENS.")

    monkeypatch.setattr(lgw, "_generate_plan_with_langchain", boom)

    result = lgw.run_langgraph_workflow(_task(), _settings(max_output_tokens=500))

    assert result["status"] == "fallback"
    assert "truncated" in result["execution_metadata"]["reason"]
