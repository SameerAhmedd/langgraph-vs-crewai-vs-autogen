"""AutoGen workflow for the 7-day study-plan scenario."""

from __future__ import annotations

import asyncio
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


def run_autogen_workflow(task: dict[str, Any], settings: Settings) -> dict[str, Any]:
    """Run the study-plan task as a small AutoGen conversational workflow."""

    framework = "AutoGen"
    started_at, start_time = start_timer()
    observations = base_observations(framework, settings.use_fallback_mode)

    if settings.mock_mode:
        return generate_fallback_study_plan(framework, task, "MOCK_MODE enabled")
    if not settings.has_api_key:
        return generate_fallback_study_plan(framework, task, "OPENAI_API_KEY missing")

    try:
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.conditions import MaxMessageTermination
        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_ext.models.openai import OpenAIChatCompletionClient
    except ImportError as exc:
        observations["architecture_design"] = "AutoGen package could not be imported."
        return generate_fallback_study_plan(framework, task, f"AutoGen import failed: {exc}")

    conversation_log: list[str] = []
    try:
        plan, conversation_log = asyncio.run(
            _run_real_autogen(
                task,
                settings,
                AssistantAgent,
                MaxMessageTermination,
                RoundRobinGroupChat,
                OpenAIChatCompletionClient,
            )
        )
    except Exception as exc:
        return generate_fallback_study_plan(framework, task, f"AutoGen live API execution failed: {exc}")

    observations.update(
        {
            "architecture_design": "Implemented as a small conversational team with Planner and Reviewer agents.",
            "workflow_control": "Workflow control is conversation-oriented through a round-robin team and message limit.",
            "state_handling": "State is held mainly in conversation messages and the extracted final JSON response.",
            "agent_coordination": "Coordination is multi-agent conversational: planner drafts, reviewer checks, coordinator prompt starts the flow.",
            "transparency_and_debugging": "Conversation summaries and execution metadata are saved; full provider traces depend on AutoGen settings.",
            "ease_of_use": "Natural for conversational workflows, but async orchestration and output extraction add setup effort.",
            "development_complexity": "Moderate to high for a small task because model clients, teams, termination, and parsing are required.",
            "suitability_for_lightweight_automation": "Suitable when the lightweight task benefits from iterative agent discussion or review.",
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


async def _run_real_autogen(
    task: dict[str, Any],
    settings: Settings,
    AssistantAgent: Any,
    MaxMessageTermination: Any,
    RoundRobinGroupChat: Any,
    OpenAIChatCompletionClient: Any,
) -> tuple[dict[str, Any], list[str]]:
    """Execute the real AutoGen AgentChat workflow and parse the final response."""

    client_kwargs: dict[str, Any] = {
        "model": settings.openai_model,
        "timeout": settings.request_timeout_seconds,
        "max_retries": settings.max_retries,
    }
    if settings.openai_api_key:
        client_kwargs["api_key"] = settings.openai_api_key
    if settings.openai_base_url:
        client_kwargs["base_url"] = settings.openai_base_url

    model_client = OpenAIChatCompletionClient(**client_kwargs)
    try:
        planner = AssistantAgent(
            "planner_agent",
            model_client=model_client,
            system_message=(
                "Draft one concise 7-day beginner-friendly study plan as valid JSON only."
            ),
        )
        reviewer = AssistantAgent(
            "reviewer_agent",
            model_client=model_client,
            system_message=(
                "Check the JSON shape and return only corrected final JSON."
            ),
        )
        team = RoundRobinGroupChat(
            [planner, reviewer],
            termination_condition=MaxMessageTermination(max_messages=2),
        )
        result = await team.run(task=build_study_plan_prompt(task, "AutoGen"))
    finally:
        close = getattr(model_client, "close", None)
        if close is not None:
            maybe_awaitable = close()
            if asyncio.iscoroutine(maybe_awaitable):
                await maybe_awaitable

    messages = getattr(result, "messages", [])
    conversation_log = []
    final_text = ""
    for message in messages:
        source = getattr(message, "source", "unknown")
        content = str(getattr(message, "content", ""))
        conversation_log.append(f"{source}: {content[:300]}")
        if content.strip():
            final_text = content

    return extract_json_object(final_text), conversation_log
