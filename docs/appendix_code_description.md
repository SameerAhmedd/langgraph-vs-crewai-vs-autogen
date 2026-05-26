# Appendix Code Description

## Suggested Appendix Titles

- Appendix A: Prototype Source Code Overview
- Appendix B: Input Task Description
- Appendix C: Framework Output Samples
- Appendix D: Comparison Matrix

## File Descriptions

`main.py` runs the complete comparison workflow. It loads the task, executes LangGraph, CrewAI, and AutoGen implementations, writes outputs, and generates the comparison matrix.

`config/settings.py` loads environment variables and determines whether fallback mode is active.

`data/input_tasks.json` contains the synthetic student requirement used by all frameworks.

`data/evaluation_criteria.json` defines the qualitative criteria used for thesis interpretation.

`src/common/task_loader.py` loads JSON input and criteria files.

`src/common/study_plan.py` contains shared prompt construction, fallback output generation, Markdown formatting, and JSON validation helpers.

`src/common/output_writer.py` writes framework outputs, Markdown reports, and execution logs.

`src/common/evaluation.py` creates `comparison_matrix.csv` and `comparison_matrix.md`.

`src/common/logging_utils.py` provides execution metadata, failure result construction, and logging setup.

`src/langgraph_impl/langgraph_workflow.py` implements the explicit graph/state workflow.

`src/crewai_impl/crewai_workflow.py` implements the role-based multi-agent workflow.

`src/autogen_impl/autogen_workflow.py` implements the conversational multi-agent workflow.

`notebooks/thesis_prototype_colab.ipynb` provides a notebook version for academic demonstration or Google Colab execution.

`tests/` contains small tests for loading input, writing output files, and generating the comparison matrix.

## Referencing in the Thesis

Chapter 5 can reference the project structure, framework-specific implementation files, and common output format.

Chapter 6 can reference generated framework output samples, execution logs, and the comparison matrix.

The appendix can include selected code excerpts rather than every file in full. The full repository can be linked or submitted as supplementary material if allowed by the university guidelines.

