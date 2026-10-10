# LangGraph vs CrewAI vs AutoGen: one task, three agent frameworks

[![CI](https://github.com/SameerAhmedd/Agentic-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/SameerAhmedd/Agentic-AI/actions/workflows/ci.yml)

The same task, a structured 7-day study plan, implemented in three agentic AI frameworks and compared on workflow control, state handling, transparency and development complexity. Each run produces normalised JSON and Markdown output plus an execution log, so the frameworks can be compared on equal terms.

Originally built for my B.Sc. Computer Science thesis at IU International University of Applied Sciences (2026). The exact state described in the thesis is tagged [`thesis-submission`](https://github.com/SameerAhmedd/Agentic-AI/tree/thesis-submission); this branch contains later fixes and extensions (see [Status](#status-and-roadmap)).

## What I found

| Framework | Design | Strongest when | Cost of using it |
|---|---|---|---|
| **LangGraph** | Explicit graph: nodes, edges, a typed state object | You need an inspectable, repeatable pipeline | More code than a direct prompt for a small task |
| **AutoGen** | Planner and Reviewer agents talking to each other | The task benefits from a draft-and-review loop | Async orchestration, termination rules and JSON extraction from chat messages |
| **CrewAI** | Role-based agents, tasks and a crew | The work splits naturally into roles | Not run live in the thesis run (see below) |

- **No framework wins everywhere.** The right choice depends on the shape of the task and how much control and traceability you need.
- **LangGraph was the easiest to debug**: named nodes, an explicit state object and a saved step log show where a run went wrong.
- **AutoGen was the most flexible**, but state lives in the conversation history, so you inspect messages to see how the final answer came about.
- **CrewAI was implemented but not executed live** in the final thesis run, so it is assessed from its structure and documentation, not from observed output.

Caveat: this is one task, run once per framework, with a qualitative comparison. It is not a benchmark. A repeated-run evaluation is planned (see roadmap).

## The task

> Generate a structured 7-day study plan from a student requirement.

The synthetic input is a Bachelor Computer Science student who wants to revise Python basics, file handling, regular expressions and simple data analysis in two hours per day. No real personal data is used.

Each framework runs the same workflow:

1. Understand the requirement
2. Decompose it into study goals
3. Generate a 7-day plan with daily practice tasks
4. Produce JSON and Markdown output
5. Log execution metadata and errors

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
```

Run without any API key (clearly labelled fallback output, useful to verify the pipeline):

```bash
MOCK_MODE=true python main.py
```

Run live (needs `OPENAI_API_KEY` in `.env`):

```bash
MOCK_MODE=false python main.py
```

Run the tests (no API key or network needed):

```bash
pytest
```

Outputs are written to `outputs/`: one JSON and one Markdown file per framework, `execution_log.json`, and `comparison_matrix.csv` / `.md`. The files committed in `outputs/` are from the original thesis run.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | none | Enables live runs; without it the project uses labelled fallback output |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model used by all frameworks |
| `MOCK_MODE` | `true` | Skip all API calls |
| `RUN_LANGGRAPH` / `RUN_CREWAI` / `RUN_AUTOGEN` | `true` | Enable or disable a framework |
| `MAX_OUTPUT_TOKENS` | `1500` | Output cap; around 500 truncates the JSON (see below) |
| `MAX_RETRIES` | `1` | Retries per request |
| `OPENAI_BASE_URL` | none | Point at an OpenAI-compatible endpoint |

Fallback output is deterministic demonstration content, always labelled as such, and is never reported as a live result. A failing framework does not stop the others; it records a structured failure.

## Project structure

```
.
├── main.py                  # runs all three frameworks and writes outputs
├── config/settings.py       # environment-based settings
├── data/                    # input task and evaluation criteria
├── src/
│   ├── common/              # shared prompt, validation, output writing, evaluation
│   ├── langgraph_impl/      # StateGraph with four named nodes
│   ├── crewai_impl/         # Requirement Analyst, Study Planner, Quality Reviewer
│   └── autogen_impl/        # Planner and Reviewer conversation
├── tests/                   # unit tests (run offline)
├── outputs/                 # results of the thesis run
├── notebooks/               # Colab notebook that runs the same pipeline
└── docs/                    # notes written during the thesis
```

## Evaluation criteria

Architecture design, workflow control, state handling, tool integration, agent coordination, transparency and debugging, ease of use, development complexity, output structure, and suitability for lightweight task automation. The criteria live in `data/evaluation_criteria.json`, and the generated matrix reports observations without declaring a winner.

## Known limitations

- **One task, one run.** Results depend on the model, prompts, framework versions and configuration. Treat them as observations, not rankings.
- **Truncation.** A 7-day plan needs roughly 900 to 1,200 output tokens. With a cap near 500 the JSON is cut off, parsing fails and the run falls back. This happened in one of my runs, which is why the default is now 1500 and truncation raises an explicit error.
- **Configuration differs between frameworks.** LangGraph runs at temperature 0, CrewAI at 0.1, and AutoGen uses the client default with no explicit token cap. A fair comparison needs these aligned, which is part of the planned evaluation.
- **CrewAI has not been run live since the Requirement Analyst was given a task** (it previously had none). That change is covered by syntax checks only.
- No latency, cost, security or scalability measurements.

## Status and roadmap

Done since the thesis submission:

- Fixed character-by-character bullets in the Markdown output (the model returned a string where a list was expected)
- LangGraph now passes its graph state into the model call and uses the same base prompt as the other frameworks
- Step logs and conversation logs are saved in the outputs
- CrewAI's Requirement Analyst now actually runs
- Offline tests and CI

Planned:

- [ ] Repeated live runs (10 per framework) with automated output checks: valid JSON, seven days, within the two-hour limit, all topics covered
- [ ] Pass rate, latency and token cost per framework, with CrewAI run live
- [ ] Aligned model settings across frameworks

## Troubleshooting

- Import errors: `pip install -r requirements.txt`
- AutoGen API changes: `pip install -U "autogen-agentchat" "autogen-ext[openai]"`
- CrewAI dependency conflicts: use a fresh virtual environment with Python 3.10 or newer
- Live run fails: check that `.env` exists, `OPENAI_API_KEY` is set and the model is available to your account
