"""LangGraph workflow for the 7-day study-plan scenario."""

from __future__ import annotations

import json
from typing import Any, TypedDict

from config.settings import Settings
from src.common.logging_utils import (
    base_observations,
    build_execution_metadata,
    build_failure_result,
    start_timer,
)
from src.common.study_plan import (
    build_study_plan_prompt,
    extract_json_object,
    generate_fallback_study_plan,
    study_plan_to_markdown,
)


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
        # The prompt is built from the graph state, so the analysis and goal-decomposition
        # nodes actually feed the generation node instead of being bypassed.
        plan = _generate_plan_with_langchain(build_langgraph_prompt(state), settings)
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
        "execution_metadata": {
            **build_execution_metadata(started_at, start_time, final_state.get("errors", [])),
            "step_log": final_state.get("step_log", []),
        },
    }


def _generate_plan_with_langchain(prompt: str, settings: Settings) -> dict[str, Any]:
    """Generate the plan with LangChain's OpenAI chat wrapper inside LangGraph."""

    from langchain_openai import ChatOpenAI

    llm_kwargs: dict[str, Any] = {
        "model": settings.openai_model,
        "api_key": settings.openai_api_key,
        "temperature": 0,
        "timeout": settings.request_timeout_seconds,
        "max_retries": settings.max_retries,
        "max_tokens": settings.max_output_tokens,
    }
    if settings.openai_base_url:
        llm_kwargs["base_url"] = settings.openai_base_url

    llm = ChatOpenAI(**llm_kwargs).bind(response_format={"type": "json_object"})
    response = llm.invoke(prompt)

    metadata = getattr(response, "response_metadata", None) or {}
    if metadata.get("finish_reason") == "length":
        raise ValueError(
            f"Model output was truncated at max_tokens={settings.max_output_tokens}; "
            "increase MAX_OUTPUT_TOKENS."
        )

    content = response.content if hasattr(response, "content") else str(response)
    return extract_json_object(str(content))


def build_langgraph_prompt(state: StudyPlanState) -> str:
    """Build the generation prompt from the graph state.

    Uses the same shared base prompt as the CrewAI and AutoGen implementations so the
    three frameworks are compared on an equivalent task, then appends what the earlier
    graph nodes produced (requirement analysis and decomposed study goals).
    """

    goal_lines = "\n".join(f"- {goal}" for goal in state.get("study_goals", []))
    return (
        build_study_plan_prompt(state["task"], "LangGraph")
        + "\n\nRequirement analysis from the previous graph node:\n"
        + json.dumps(state.get("requirement_analysis", {}), indent=2)
        + "\n\nStudy goals from the goal-decomposition node:\n"
        + goal_lines
        + "\n\nCover every study goal at least once across the seven days."
    )
