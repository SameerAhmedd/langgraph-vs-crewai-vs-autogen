# Comparative Analysis of Agentic AI Frameworks for Task Automation

Bachelor thesis prototype for IU International University of Applied Sciences.

Thesis title: **Comparative Analysis of Agentic AI Frameworks for Task Automation: Evaluating LangGraph, CrewAI, and AutoGen**

- Author: Sameer Ahmed
- Enrolment Number: 4235673

## Research Purpose

This project is a lightweight academic prototype that compares three agentic AI frameworks for the same task automation scenario:

- LangGraph
- CrewAI
- AutoGen

The purpose is to support Chapter 5, **Prototype Design and Implementation**, and Chapter 6, **Comparative Evaluation**. The prototype focuses on workflow architecture, agent coordination, state handling, tool integration, workflow control, transparency, ease of use, development complexity, and suitability for lightweight automation.

This is not a production benchmark and does not claim universal framework superiority.

## Scenario

The mandatory scenario is:

> Generate a structured 7-day study plan from a student requirement.

The synthetic input describes a Bachelor Computer Science student who wants to revise Python basics, file handling, regular expressions, and simple data analysis with two hours of study time per day.

Each framework attempts the same workflow:

1. Understand the requirement
2. Decompose it into study goals
3. Generate a 7-day plan
4. Add daily practice tasks
5. Produce JSON and Markdown output
6. Log execution metadata and errors

## Project Structure

```text
agentic-ai-framework-comparison/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── main.py
├── config/
├── data/
├── outputs/
├── src/
│   ├── common/
│   ├── langgraph_impl/
│   ├── crewai_impl/
│   └── autogen_impl/
├── notebooks/
├── docs/
└── tests/
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

Add your key if you want real LLM execution:

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
MOCK_MODE=false
LOW_COST_MODE=true
```

If no API key is present, the project runs in clearly labelled fallback demonstration mode. Fallback mode is useful for testing the code structure and file generation, but it must not be interpreted as real LLM output.

## Run

```bash
python main.py
```

## Low-Cost Safe Running Mode

Recommended first run:

```bash
MOCK_MODE=true python main.py
```

This mode makes no live OpenAI API calls. It generates clearly labelled fallback demonstration output so you can verify files, screenshots, and appendix material safely.

Real API run:

```bash
MOCK_MODE=false LOW_COST_MODE=true python main.py
```

Low-cost mode keeps requests conservative with short outputs, a request timeout, and limited retries.

Do not repeatedly run CrewAI or AutoGen with real API credentials if connection errors occur, because retries may consume credits.

Expected output files:

- `outputs/langgraph_output.json`
- `outputs/langgraph_output.md`
- `outputs/crewai_output.json`
- `outputs/crewai_output.md`
- `outputs/autogen_output.json`
- `outputs/autogen_output.md`
- `outputs/execution_log.json`
- `outputs/comparison_matrix.csv`
- `outputs/comparison_matrix.md`

The main runner does not crash the entire project if one framework fails. Instead, it records a structured failure result with error details.

## Colab Notebook

Open `notebooks/thesis_prototype_colab.ipynb` in Google Colab. The notebook explains the prototype, installs dependencies, loads environment variables, runs the same main workflow, and displays the comparison matrix.

For Colab, upload the full project folder or clone it into the notebook environment before running the cells.

## Evaluation Criteria

The qualitative criteria are stored in `data/evaluation_criteria.json`:

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

The generated comparison matrix uses observed outputs and implementation behavior. It intentionally avoids automatic winner claims.

## Academic Limitations

- This prototype is a lightweight academic comparison, not a large-scale benchmark.
- It does not evaluate enterprise deployment, security, latency, cost, production scalability, or long-running reliability.
- Outputs depend on model behavior, API availability, framework versions, prompt design, and local Python environment.
- Failed framework runs should be documented as practical limitations, not hidden or replaced with invented results.
- Fallback output is deterministic demonstration content and is clearly labelled as such.

## Ethical and Data Note

The input task is synthetic and non-sensitive. No personal student data is used.

## Troubleshooting

If a framework fails to import, run:

```bash
pip install -r requirements.txt
```

If AutoGen fails due to package changes, verify that both packages are installed:

```bash
pip install -U "autogen-agentchat" "autogen-ext[openai]"
```

If CrewAI fails because of dependency conflicts, try a fresh virtual environment with Python 3.10 or newer.

If real LLM execution fails, check:

- `.env` exists
- `OPENAI_API_KEY` is set
- `OPENAI_MODEL` is available for your account or provider
- `OPENAI_BASE_URL` is correct if using an OpenAI-compatible endpoint

## Dependency Note

The framework ecosystem changes quickly. Package names in `requirements.txt` were selected to match current public installation guidance:

- LangGraph: `langgraph`
- CrewAI: `crewai`
- AutoGen AgentChat: `autogen-agentchat` and `autogen-ext[openai]`

If future versions change APIs, keep the structured failure logs and document the limitation honestly in the thesis.
