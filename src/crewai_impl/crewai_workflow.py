"""CrewAI workflow for the 7-day study-plan scenario."""

from __future__ import annotations

import os
from typing import Any

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


def run_crewai_workflow(task: dict[str, Any], settings: Settings) -> dict[str, Any]:
    """Run the study-plan task as a small CrewAI role-based workflow."""

    framework = "CrewAI"
    started_at, start_time = start_timer()
    observations = base_observations(framework, settings.use_fallback_mode)

    os.environ["OTEL_SDK_DISABLED"] = "true"
    os.environ["CREWAI_TRACING_ENABLED"] = "false"
    os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

    if settings.mock_mode:
        return generate_fallback_study_plan(framework, task, "MOCK_MODE enabled")
    if not settings.has_api_key:
        return generate_fallback_study_plan(framework, task, "OPENAI_API_KEY missing")

    try:
        from crewai import Agent, Crew, LLM, Process, Task
    except ImportError as exc:
        observations["architecture_design"] = "CrewAI package could not be imported."
        return generate_fallback_study_plan(framework, task, f"CrewAI import failed: {exc}")

    step_log: list[str] = []
    try:
        plan = _run_real_crewai(task, settings, Agent, Crew, LLM, Process, Task)
        step_log.append("CrewAI kickoff completed and returned parseable JSON output.")
    except Exception as exc:
        return generate_fallback_study_plan(framework, task, f"CrewAI live API execution failed: {exc}")

    observations.update(
        {
            "architecture_design": "Implemented as role-based agents: Requirement Analyst, Study Planner, and Quality Reviewer.",
            "workflow_control": "CrewAI executes assigned tasks in a sequential process for this prototype.",
            "state_handling": "State is represented mostly through task context and the final crew result rather than a typed state object.",
            "agent_coordination": "Coordination is persona-based: each agent has a role, goal, backstory, and assigned task.",
            "transparency_and_debugging": "Verbose role/task definitions and saved metadata support inspection, though internal LLM reasoning is not exposed.",
            "ease_of_use": "Readable for academic role modelling, but setup involves several framework-specific abstractions.",
            "development_complexity": "Moderate to high for a small task because agents, tasks, crew, process, and parsing must be configured.",
            "suitability_for_lightweight_automation": "Useful when the task benefits from human-readable role separation and review steps.",
        }
    )

    return {
        "framework": framework,
        "task_id": task["task_id"],
        "status": "success",
        "final_answer_markdown": study_plan_to_markdown(plan),
        "final_answer_json": plan,
        "observations": observations,
        "execution_metadata": build_execution_metadata(started_at, start_time, []),
    }


def _run_real_crewai(
    task: dict[str, Any],
    settings: Settings,
    Agent: Any,
    Crew: Any,
    LLM: Any,
    Process: Any,
    Task: Any,
) -> dict[str, Any]:
    """Execute the real CrewAI workflow and parse its final JSON response."""

    llm_kwargs: dict[str, Any] = {
        "model": f"openai/{settings.openai_model}",
        "temperature": 0.1,
        "timeout": settings.request_timeout_seconds,
        "max_retries": settings.max_retries,
        "max_tokens": settings.max_output_tokens,
    }
    if settings.openai_base_url:
        llm_kwargs["base_url"] = settings.openai_base_url
    llm = LLM(**llm_kwargs)

    requirement_analyst = Agent(
        role="Requirement Analyst",
        goal="Extract the student's profile, learning goals, constraints, and expected output format.",
        backstory="An academic assistant who converts student requirements into clear planning constraints.",
        llm=llm,
        verbose=False,
        max_iter=1,
    )
    study_planner = Agent(
        role="Study Planner",
        goal="Create a beginner-friendly 7-day plan with practical daily activities.",
        backstory="An instructional planner experienced in short revision plans for computer science students.",
        llm=llm,
        verbose=False,
        max_iter=1,
    )
    quality_reviewer = Agent(
        role="Quality Reviewer",
        goal="Check that the plan is complete, structured, JSON-compatible, and aligned with the task.",
        backstory="A reviewer who verifies academic prototype outputs without inventing unsupported claims.",
        llm=llm,
        verbose=False,
        max_iter=1,
    )

    planning_task = Task(
        description=(
            "Create the final JSON directly. Use the student requirement and keep it concise. "
            + build_study_plan_prompt(task, "CrewAI")
        ),
        expected_output="Only valid JSON with exactly seven daily_plan entries.",
        agent=study_planner,
    )
    review_task = Task(
        description=(
            "Review the plan for completeness and return only the corrected final JSON. "
            "Do not include Markdown fences or explanatory text."
        ),
        expected_output="Only valid JSON with title, overview, daily_plan, and summary.",
        agent=quality_reviewer,
        context=[planning_task],
    )

    crew = Crew(
        agents=[requirement_analyst, study_planner, quality_reviewer],
        tasks=[planning_task, review_task],
        process=Process.sequential,
        verbose=False,
    )
    result = crew.kickoff()
    return extract_json_object(str(result))
