"""Main runner for the agentic AI framework comparison prototype."""

from __future__ import annotations

from config.settings import load_settings
from src.autogen_impl.autogen_workflow import run_autogen_workflow
from src.common.evaluation import generate_comparison_matrix
from src.common.logging_utils import configure_logging
from src.common.output_writer import (
    ensure_output_dir,
    write_execution_log,
    write_framework_outputs,
)
from src.common.study_plan import generate_fallback_study_plan
from src.common.task_loader import load_evaluation_criteria, load_input_task
from src.crewai_impl.crewai_workflow import run_crewai_workflow
from src.langgraph_impl.langgraph_workflow import run_langgraph_workflow

def main() -> None:
    """Run all three framework implementations and create comparison outputs."""

    configure_logging()
    settings = load_settings()
    ensure_output_dir(settings.outputs_dir)

    task = load_input_task(settings.data_dir / "input_tasks.json")
    criteria = load_evaluation_criteria(settings.data_dir / "evaluation_criteria.json")

    runners = [
        ("LangGraph", settings.run_langgraph, run_langgraph_workflow),
        ("CrewAI", settings.run_crewai, run_crewai_workflow),
        ("AutoGen", settings.run_autogen, run_autogen_workflow),
    ]

    results = []
    for framework_name, enabled, runner in runners:
        if enabled:
            result = runner(task, settings)
        else:
            result = generate_fallback_study_plan(
                framework_name,
                task,
                "Framework disabled for low-cost run",
            )
        write_framework_outputs(settings.outputs_dir, result, task)
        results.append(result)

    write_execution_log(settings.outputs_dir, results)
    generate_comparison_matrix(settings.outputs_dir, criteria, results)

    print("Prototype run summary")
    for result in results:
        print(f"{result['framework']}: {result['status']}")
    print(f"Output folder: {settings.outputs_dir}")


if __name__ == "__main__":
    main()
