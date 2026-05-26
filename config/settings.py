"""Runtime settings for the agentic AI framework comparison prototype."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency may be absent before setup
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    base_dir: Path
    data_dir: Path
    outputs_dir: Path
    openai_api_key: str | None
    openai_model: str
    openai_base_url: str | None
    mock_mode: bool
    low_cost_mode: bool
    run_langgraph: bool
    run_crewai: bool
    run_autogen: bool
    max_output_tokens: int
    request_timeout_seconds: int
    max_retries: int
    use_fallback_mode: bool

    @property
    def has_api_key(self) -> bool:
        return bool(self.openai_api_key)


def load_settings() -> Settings:
    """Load settings from .env and process environment variables."""

    if load_dotenv is not None:
        load_dotenv(BASE_DIR / ".env")

    api_key = os.getenv("OPENAI_API_KEY") or None
    mock_mode = _env_bool("MOCK_MODE", True)
    legacy_fallback = _env_bool("USE_FALLBACK_MODE", False)
    low_cost_mode = _env_bool("LOW_COST_MODE", True)
    max_retries = _env_int("MAX_RETRIES", 1)

    os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
    os.environ.setdefault("OTEL_SDK_DISABLED", "true")
    os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")

    return Settings(
        base_dir=BASE_DIR,
        data_dir=BASE_DIR / "data",
        outputs_dir=BASE_DIR / "outputs",
        openai_api_key=api_key,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_base_url=os.getenv("OPENAI_BASE_URL") or None,
        mock_mode=mock_mode,
        low_cost_mode=low_cost_mode,
        run_langgraph=_env_bool("RUN_LANGGRAPH", True),
        run_crewai=_env_bool("RUN_CREWAI", True),
        run_autogen=_env_bool("RUN_AUTOGEN", True),
        max_output_tokens=_env_int("MAX_OUTPUT_TOKENS", 700),
        request_timeout_seconds=_env_int("REQUEST_TIMEOUT_SECONDS", 30),
        max_retries=max(0, max_retries),
        use_fallback_mode=mock_mode or legacy_fallback or not api_key,
    )


def _env_bool(name: str, default: bool) -> bool:
    """Read a boolean environment variable."""

    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _env_int(name: str, default: int) -> int:
    """Read an integer environment variable with a safe fallback."""

    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default
