"""Logging and result-shaping helpers."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

from src.common.study_plan import empty_plan


def configure_logging() -> None:
    """Configure concise console logging for local execution."""

    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def utc_now() -> str:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


def start_timer() -> tuple[str, float]:
    """Return an ISO timestamp and monotonic timer value."""

    return utc_now(), time.perf_counter()


def build_execution_metadata(
    started_at: str,
    start_time: float,
    errors: list[str] | None = None,
) -> dict[str, Any]:
    """Build normalized execution metadata."""

    completed_at = utc_now()
    return {
        "started_at": started_at,
        "completed_at": completed_at,
        "duration_seconds": round(time.perf_counter() - start_time, 3),
        "errors": errors or [],
    }


def build_failure_result(
    framework: str,
    task_id: str,
    started_at: str,
    start_time: float,
    error: str,
    observations: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Create a normalized failed result without stopping the main runner."""

    return {
        "framework": framework,
        "task_id": task_id,
        "status": "failed",
        "final_answer_markdown": "",
        "final_answer_json": empty_plan(),
        "observations": observations or {},
        "execution_metadata": build_execution_metadata(started_at, start_time, [error]),
    }


def base_observations(framework: str, fallback_mode: bool) -> dict[str, str]:
    """Create neutral observations that can be refined after execution."""

    mode_note = (
        "Fallback demonstration mode was used because no API key was available or fallback was forced."
        if fallback_mode
        else "Executed with configured LLM provider."
    )
    return {
        "architecture_design": f"{framework} implementation created for the same study-plan workflow. {mode_note}",
        "workflow_control": "Observed from code-level sequencing and execution metadata.",
        "state_handling": "Observed from intermediate data structures and final output files.",
        "tool_integration": "Uses shared Python helpers for prompt construction, JSON parsing, Markdown formatting, and file writing.",
        "agent_coordination": "Observed from the framework-specific coordination mechanism.",
        "transparency_and_debugging": "Execution metadata and errors are saved in outputs/execution_log.json.",
        "ease_of_use": "To be interpreted after comparing setup friction and code complexity.",
        "development_complexity": "To be interpreted from the implementation size and framework-specific abstractions.",
        "suitability_for_lightweight_automation": "To be interpreted from successful execution, clarity, and required setup effort.",
    }
