# learn-ai-engineering

A self-paced curriculum for AI and data engineering: notes, notebooks, exercises and course
material, organized into six subjects. Each subject folder has its own README.

> **Where to start:** [CURRICULUM.md](CURRICULUM.md) has the subject map, prerequisites, three
> learning paths (AI Engineering, Data Engineering, Full-Stack Data), the definition of done, and
> [Sources](CURRICULUM.md#sources), which lists where each piece of vendored material came from.
>
> **Interview prep and coding drills** are in the private
> [sisyphus](https://github.com/ramseywise/sisyphus) repo:
> [interview guides](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md)
> and [language drills](https://github.com/ramseywise/sisyphus/blob/main/drills/README.md).
> Hands-on AI-engineering projects (RAG, agents, evals, MCP) are in the working repos listed in
> [`../PORTFOLIO.md`](../PORTFOLIO.md).

## Subjects

| Subject | What it covers |
|---|---|
| [Programming](programming/README.md) | [Python](programming/python/README.md) (foundations → informatics → engineering idioms → pandas), [SQL](programming/sql/README.md) (`SELECT` to query plans, SQL Murder Mystery capstone), [TypeScript](programming/typescript/README.md) (JS for Python developers → typed LLM apps) |
| [Data Analytics](data-analytics/README.md) | Six pillars: Python for data analysis (pandas and dataframes) → probability and statistics → experimentation and causality → Bayesian analysis → visualisation and storytelling → applied analyses (forecasting, credit, churn and more) |
| [Data Engineering](data-engineering/README.md) | Seven pillars built around *Designing Data-Intensive Applications*: storage and compute foundations → ingest and modelling → transform and orchestrate → warehouse, lakehouse and streaming → quality and observability → ML platform → architecture and governance |
| [Data Science](data-science/README.md) | Four pillars: classical ML → deep learning → NLP → time series and recommenders, practised in Intro to ML in Python, Andrew Ng's ML and Deep Learning courses and Text Analytics with Python |
| [Generative AI](generative-ai/README.md) | Nine pillars: LLM fundamentals → RAG → agentic foundations → agentic frameworks → RL and alignment → observability → agentic applications → evaluation → LLMs from scratch |
| [AI Engineering](ai-engineering/README.md) | Five foundations (prompt → context → harness → loop → graph), plus inference as the substrate and two cross-cuts: multimodal, safety and security. Labs in TypeScript and Python |

Generative AI builds things with LLMs; AI Engineering is the discipline that makes them reliable.

## Readings

Reference papers and book chapters sit in the `sources/` folder of the pillar that uses them, for
example [`generative-ai/01-llm-fundamentals/sources/`](generative-ai/01-llm-fundamentals/sources/).
New PDFs land in the inbox at [`scripts/papers/inbox/`](scripts/papers/inbox/), and the
`/readings` skill routes them to their home. External links (courses, books, papers, tools) are in
each pillar's `references.md`, the
[general resources](generative-ai/README.md#general-resources) list and
[ai-engineering/SOURCES.md](ai-engineering/SOURCES.md).
