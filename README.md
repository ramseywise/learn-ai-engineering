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
| [Data Analytics](data-analytics/README.md) | Statistical analysis, Bayesian A/B testing, Michigan/Wesleyan statistics coursework |
| [Data Engineering](data-engineering/README.md) | DataTalks Data Engineering (Docker, workflow, DWH, batch, streaming) and MLOps (tracking, orchestration, deployment, monitoring), data mesh |
| [Data Science](data-science/README.md) | Intro to ML in Python, Andrew Ng's ML and Deep Learning courses, Text Analytics with Python, intro to NLP, Karpathy's *nn-zero-to-hero* |
| [Generative AI](generative-ai/README.md) | Seven pillars: LLM fundamentals → RAG → agentic foundations → agentic frameworks → RL & alignment → observability → agentic applications |
| [AI Engineering](ai-engineering/README.md) | Six foundations: prompt → context → harness → loop → graph → eval |

Generative AI builds things with LLMs; AI Engineering is the discipline that makes them reliable.

## Readings

Reference papers and book chapters sit next to the pillar that uses them, in `readings/` or
`sources/` folders, for example
[`ai-engineering/readings/`](ai-engineering/readings/) and
[`generative-ai/01-llm-fundamentals/readings/`](generative-ai/01-llm-fundamentals/readings/).
External links (courses, books, papers, tools) are in
[generative-ai/resources.md](generative-ai/resources.md) and
[ai-engineering/SOURCES.md](ai-engineering/SOURCES.md).
