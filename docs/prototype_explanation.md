# Prototype Design Explanation

## Academic Context

This prototype supports a Bachelor thesis comparing LangGraph, CrewAI, and AutoGen for lightweight task automation. The implementation is intentionally small so the comparison remains understandable and suitable for thesis discussion.

## Scenario Selection

The study-plan scenario was selected because it is simple enough to run locally but rich enough to show meaningful workflow behavior. It requires requirement analysis, decomposition, generation, review or formatting, and structured output.

The task uses only synthetic, non-sensitive input:

- A Bachelor Computer Science student profile
- A goal to revise beginner Python topics
- A seven-day time constraint
- A preferred beginner-friendly style

## Equivalent Workflow Across Frameworks

Each framework implementation follows the same conceptual workflow:

1. Analyze the requirement
2. Decompose the requirement into smaller study goals
3. Generate a seven-day study plan
4. Add practice tasks and expected outcomes
5. Return a normalized JSON object and Markdown report
6. Save execution metadata and errors

The implementations differ only in coordination style:

- LangGraph uses explicit graph nodes and a typed state object.
- CrewAI uses role-based agents and sequential task assignments.
- AutoGen uses a conversational multi-agent team.

## Support for Research Questions

The code supports qualitative comparison by making framework behavior observable in source code and output files. The generated files can be used to discuss:

- How each framework structures the workflow
- How coordination is represented
- How state or intermediate outputs are handled
- How transparent the workflow is during execution
- How much implementation complexity is required for a small automation scenario

## Fallback Mode

Fallback mode exists so the project can run without spending API credits. It creates deterministic demonstration output and clearly labels it as fallback content. It should be used for testing structure and file generation only.

Fallback output must not be described as real LLM output in the thesis.

## Limitations

This prototype does not measure enterprise readiness, cost, latency, security, scalability, or production reliability. It is designed for qualitative academic interpretation, not quantitative benchmarking.

Framework versions and APIs may change. If a dependency fails, the project records the failure so the limitation can be discussed honestly.

