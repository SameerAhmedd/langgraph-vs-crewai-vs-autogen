# Framework Comparison Notes

## LangGraph Notes

LangGraph is represented through a `StateGraph` with named nodes:

- Requirement analysis
- Goal decomposition
- Plan generation
- Final formatting

The main observable advantage is explicit workflow orchestration. State is visible in the `StudyPlanState` object, and transitions are visible through graph edges.

Potential limitation: for a very small task, defining state, nodes, edges, and compilation may feel heavier than a direct script.

## CrewAI Notes

CrewAI is represented through role-based agents:

- Requirement Analyst
- Study Planner
- Quality Reviewer

This is useful for discussing agent roles, responsibility separation, and collaborative task framing. The agent definitions are readable for academic explanation.

Potential limitation: role and task definitions can become verbose for a small deterministic workflow.

## AutoGen Notes

AutoGen is represented through conversational coordination:

- Coordinator prompt
- Planner Agent
- Reviewer Agent

This makes sense for workflows where agents discuss or revise each other's outputs. The prototype uses a round-robin group chat and extracts the final JSON response.

Potential limitation: conversation management, async execution, and final-output parsing can add complexity for a simple structured task.

## Comparison Criteria

The comparison matrix should be interpreted through these criteria:

- Architecture design
- Workflow control
- State handling
- Tool integration
- Agent coordination
- Transparency and debugging
- Ease of use
- Development complexity
- Output structure
- Suitability for lightweight task automation

## Careful Interpretation

Do not claim that one framework is universally best. Interpret the outputs in relation to the specific task, code size, setup process, generated files, and any dependency or API errors.

If a framework fails, that failure is an observed practical result and should be discussed as a limitation.

