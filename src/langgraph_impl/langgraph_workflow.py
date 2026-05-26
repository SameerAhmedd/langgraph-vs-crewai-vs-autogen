"""LangGraph workflow for the 7-day study-plan scenario."""

from __future__ import annotations

from typing import Any, TypedDict

from config.settings import Settings
from src.common.logging_utils import (
    base_observations,
    build_execution_metadata,
    build_failure_result,
    start_timer,
)
from src.common.study_plan import extract_json_object, generate_fallback_study_plan, study_plan_to_markdown


class StudyPlanState(TypedDict, total=False):
    """Explicit state object passed between LangGraph nodes."""

    task: dict[str, Any]
    requirement_analysis: dict[str, Any]
    study_goals: list[str]
    final_answer_json: dict[str, Any]
    final_answer_markdown: str
    step_log: list[str]
    errors: list[str]


def run_langgraph_workflow(task: dict[str, Any], settings: Settings) -> dict[str, Any]:
    """Run the study-plan task through a small LangGraph state workflow."""

    framework = "LangGraph"
    started_at, start_time = start_timer()
    observations = base_observations(framework, settings.use_fallback_mode)

    if settings.mock_mode:
        return generate_fallback_study_plan(framework, task, "MOCK_MODE enabled")
    if not settings.run_langgraph:
        return generate_fallback_study_plan(framework, task, "Framework disabled for low-cost run")
    if not settings.has_api_key:
        return generate_fallback_study_plan(framework, task, "Missing OpenAI API key")

    try:
        from langgraph.graph import END, StateGraph
    except ImportError as exc:
        observations["architecture_design"] = "LangGraph package could not be imported."
        return generate_fallback_study_plan(framework, task, f"LangGraph import failed: {exc}")

    def analyze_requirement(state: StudyPlanState) -> StudyPlanState:
        current_task = state["task"]
        analysis = {
            "student_profile": current_task["student_profile"],
            "goal": current_task["goal"],
            "duration_days": current_task["constraints"]["duration_days"],
            "study_time_per_day": current_task["constraints"]["study_time_per_day"],
            "preferred_style": current_task["constraints"]["preferred_style"],
        }
        return {
            **state,
            "requirement_analysis": analysis,
            "step_log": [*state.get("step_log", []), "Analyzed requirement and extracted constraints."],
        }

    def decompose_goals(state: StudyPlanState) -> StudyPlanState:
        goals = [
            "Revise Python syntax and core data structures.",
            "Practice writing reusable functions.",
            "Use files for simple persistent input and output.",
            "Apply regular expressions to extract structured text.",
            "Analyze small datasets with beginner-friendly Python techniques.",
            "Combine the topics in a small integrated practice task.",
        ]
        return {
            **state,
            "study_goals": goals,
            "step_log": [*state.get("step_log", []), "Decomposed requirement into smaller study goals."],
        }

    def generate_plan(state: StudyPlanState) -> StudyPlanState:
        plan = _generate_plan_with_langchain(task, settings)
        log_entry = "Generated study plan using ChatOpenAI inside a LangGraph node."

        return {
            **state,
            "final_answer_json": plan,
            "step_log": [*state.get("step_log", []), log_entry],
        }

    def format_final_output(state: StudyPlanState) -> StudyPlanState:
        markdown = study_plan_to_markdown(state["final_answer_json"])
        return {
            **state,
            "final_answer_markdown": markdown,
            "step_log": [*state.get("step_log", []), "Formatted final output as Markdown and JSON."],
        }

    try:
        workflow = StateGraph(StudyPlanState)
        workflow.add_node("requirement_analysis", analyze_requirement)
        workflow.add_node("goal_decomposition", decompose_goals)
        workflow.add_node("plan_generation", generate_plan)
        workflow.add_node("final_formatting", format_final_output)

        workflow.set_entry_point("requirement_analysis")
        workflow.add_edge("requirement_analysis", "goal_decomposition")
        workflow.add_edge("goal_decomposition", "plan_generation")
        workflow.add_edge("plan_generation", "final_formatting")
        workflow.add_edge("final_formatting", END)

        compiled_workflow = workflow.compile()
        final_state = compiled_workflow.invoke({"task": task, "step_log": [], "errors": []})
    except Exception as exc:
        return generate_fallback_study_plan(framework, task, f"LangGraph live API execution failed: {exc}")

    observations.update(
        {
            "architecture_design": "Implemented as a StateGraph with four named nodes and an explicit StudyPlanState.",
            "workflow_control": "Workflow order is controlled by explicit graph edges from analysis to final formatting.",
            "state_handling": "Intermediate analysis, decomposed goals, final JSON, Markdown, and step logs are carried in state.",
            "agent_coordination": "Coordination is node-based rather than persona-based; each node performs one workflow responsibility.",
            "transparency_and_debugging": "Named nodes and the saved step log make state transitions inspectable.",
            "ease_of_use": "Clear for explicit workflows, but requires defining state schema, nodes, edges, and compilation.",
            "development_complexity": "Moderate for this small task because graph structure adds code while improving traceability.",
            "suitability_for_lightweight_automation": "Suitable when lightweight automation benefits from explicit workflow orchestration.",
        }
    )

    return {
        "framework": framework,
        "task_id": task["task_id"],
        "status": "success",
        "final_answer_markdown": final_state["final_answer_markdown"],
        "final_answer_json": final_state["final_answer_json"],
        "observations": observations,
        "execution_metadata": build_execution_metadata(started_at, start_time, final_state.get("errors", [])),
    }


def _generate_plan_with_langchain(task: dict[str, Any], settings: Settings) -> dict[str, Any]:
    """Generate the plan with LangChain's OpenAI chat wrapper inside LangGraph."""

    from langchain_openai import ChatOpenAI

    llm_kwargs: dict[str, Any] = {
        "model": settings.openai_model,
        "api_key": settings.openai_api_key,
        "temperature": 0,
        "timeout": settings.request_timeout_seconds,
        "max_retries": 0,
        "max_tokens": settings.max_output_tokens,
    }
    if settings.openai_base_url:
        llm_kwargs["base_url"] = settings.openai_base_url

    llm = ChatOpenAI(**llm_kwargs).bind(response_format={"type": "json_object"})
    response = llm.invoke(_build_compact_langgraph_prompt(task))
    content = response.content if hasattr(response, "content") else str(response)
    return extract_json_object(str(content))


def _build_compact_langgraph_prompt(task: dict[str, Any]) -> str:
    """Build a compact JSON-only prompt for the low-cost LangGraph run."""

    constraints = task["constraints"]
    return (
        "Return compact valid JSON only. Create a beginner-friendly 7-day study plan. "
        f"Student: {task['student_profile']}. Goal: {task['goal']} "
        f"Time: {constraints['study_time_per_day']} for {constraints['duration_days']} days. "
        "Keep total output under 450 tokens. Required JSON keys: title, overview, daily_plan, summary. "
        "daily_plan must have exactly 7 objects with keys: day, topic, learning_goal, "
        "study_activities, practice_task, expected_outcome. "
        "Use one short study_activities item per day. Keep every string under 6 words."
    )
