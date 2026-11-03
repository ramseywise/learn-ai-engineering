# Interviewing

Interview prep for AI, ML, data science, analytics, data engineering and forward-deployed roles. There is no
separate topic layer: the teaching and the recall both live in the pillar notes, and each note ends with an
`Interview checklist`. This folder holds what is only true in an interview, one folder per
[round](#interview-rounds).

**How to use.** Find your role in the map, work the core pillars' checklists, and read a note when you can't answer
a row. Then prep each round you're facing. [`../CROSSWALK.md`](../CROSSWALK.md) lists the rounds and drills that test
each curriculum unit.

## Role × pillar checklists

Roles: **AIE** (AI or agent engineer), **MLE** (ML engineer), **DS** (data scientist), **FDE** (forward-deployed or
applied AI engineer), **DA** (data analyst), **DE** (data engineer). ● core, ◐ secondary, ○ awareness.

| Topic: where the checklists are | AIE | MLE | DS | FDE | DA | DE |
|---|---|---|---|---|---|---|
| LLMs: [LLM fundamentals](../../generative-ai/01-llm-fundamentals/README.md), [RL](../../generative-ai/05-RL/README.md), [prompting](../../ai-engineering/01-prompt-engineering/README.md) | ● | ● | ◐ | ● | ○ | ○ |
| RAG: [RAG and retrieval](../../generative-ai/02-rag-retrieval/README.md) | ● | ◐ | ○ | ● | ○ | ○ |
| Agents: [foundations](../../generative-ai/03-agentic-foundations/README.md), [harness](../../ai-engineering/03-harness-engineering/README.md), [loops](../../ai-engineering/04-loop-engineering/README.md), [graphs](../../ai-engineering/05-graph-engineering/README.md) | ● | ◐ | ○ | ● | ○ | ○ |
| Evals: [eval](../../generative-ai/08-eval/README.md), [observability](../../generative-ai/06-observability/README.md) | ● | ● | ◐ | ● | ○ | ○ |
| Safety: [safety and security](../../ai-engineering/09-safety-and-security/README.md) | ● | ◐ | ○ | ● | ○ | ○ |
| Context and cost: [context](../../ai-engineering/02-context-engineering/README.md), [inference](../../ai-engineering/07-inference-engineering/README.md) | ● | ◐ | ○ | ◐ | ○ | ○ |
| ML: [classical ML](../../data-science/01-classical-ml/README.md), [deep learning](../../data-science/02-deep-learning/README.md) | ◐ | ● | ● | ○ | ○ | ○ |
| Data engineering and MLOps: [data engineering](../../data-engineering/README.md) | ◐ | ● | ◐ | ◐ | ◐ | ● |
| SQL: [SQL](../../programming/sql/README.md), [SQL for analytics](../../data-analytics/06-applied-analyses/notes/06-sql-for-analytics.md) | ◐ | ◐ | ● | ◐ | ● | ● |
| Stats and experiments: [probability and statistics](../../data-analytics/02-probability-and-statistics/README.md), [experimentation](../../data-analytics/03-experimentation-and-causality/README.md), [Bayesian analysis](../../data-analytics/04-bayesian-analysis/README.md) | ○ | ◐ | ● | ○ | ● | ○ |
| Product: [scoping an AI product](../../generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product.md), [metrics](../../data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design.md), [dashboards and storytelling](../../data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling.md) | ◐ | ○ | ● | ● | ● | ○ |
| System design: [backend and system design](../../programming/backend-and-system-design/README.md), [round method](rounds/system-design-round/study-guide.md) | ● | ● | ◐ | ● | ○ | ◐ |
| Coding: [Python](../../programming/python/README.md), [computer science](../../programming/computer-science/README.md), [drills](../../programming/drills/README.md) | ◐ | ◐ | ◐ | ◐ | ◐ | ● |

The DA and DE columns are a starting judgment. Titles blur between companies, so read the job description.

## Analysts and data engineers

Data jobs share some foundations and then split. The analyst explains the past and tests claims about it, the
scientist predicts on unseen data, and the engineer makes both possible.

| | Data analyst | Data scientist | Data engineer |
|---|---|---|---|
| The question | What happened, and is the difference real? | What will happen on rows nobody has seen, and can we trust it? | Does the right data arrive on time, correct, in a usable shape? |
| Prepare for | SQL, statistics, A/B tests, product sense | The analyst's list, plus ML and coding | SQL, coding, data modelling, pipeline design |
| After the shared start | [Experimentation](../../data-analytics/03-experimentation-and-causality/README.md), [storytelling](../../data-analytics/05-visualisation-and-storytelling/README.md), [applied analyses](../../data-analytics/06-applied-analyses/README.md) | [Classical ML](../../data-science/01-classical-ml/README.md), [structuring ML projects](../../data-science/02-deep-learning/notes/03-structuring-ml-projects.md), [Bayesian analysis](../../data-analytics/04-bayesian-analysis/README.md) | [Data engineering](../../data-engineering/README.md), from [data systems and data models](../../data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models.md) onward |

The shared start is [Python](../../programming/python/README.md) with
[Python for data analysis](../../data-analytics/01-python-for-data-analysis/README.md), then
[SQL for analytics](../../data-analytics/06-applied-analyses/notes/06-sql-for-analytics.md), then
[probability and statistics](../../data-analytics/02-probability-and-statistics/README.md).

## An order for starting from zero

Each line builds on the ones before it. Stats runs alongside ML, and comes first for analyst and data science roles.

1. Programming, then classical ML and stats.
2. LLMs, then RAG, then agents, then context and cost.
3. Evals and safety, once you have built something to test and attack.
4. Data engineering and MLOps, any time after classical ML.
5. System design and product, which draw on everything: revisit them repeatedly.

For the whole program, see [CURRICULUM.md](../../CURRICULUM.md).

## Interview rounds

| Round | Covers |
|---|---|
| [recruiter-screen](rounds/recruiter-screen/README.md) | Narrative, logistics, comp framing |
| [coding-challenge](rounds/coding-challenge/README.md) | Live coding, debugging rounds, pair programming (AI-assisted) |
| [technical-questions](rounds/technical-questions/README.md) | ML/LLM breadth and theory rapid-fire |
| [system-design-round](rounds/system-design-round/README.md) | ML/LLM/agent system design interviews, with a [decision tree](rounds/system-design-round/decision-tree.md) |
| [code-review-round](rounds/code-review-round/README.md) | Reviewing unfamiliar code under observation |
| [case-study](rounds/case-study/README.md) | Live and take-home cases, presentation and defense |
| [project-deep-dive](rounds/project-deep-dive/README.md) | Walking through your own systems |
| [behavioral](rounds/behavioral/README.md) | STAR stories, failure questions, collaboration |
| [customer-simulation](rounds/customer-simulation/README.md) | FDE stakeholder role-play, ambiguous-client scenarios |
| [leadership-rounds](rounds/leadership-rounds/README.md) | CTO and head-of-product conversations, reverse interview |

## Maintenance

**The split rule**: *"Is this true regardless of whether I'm being interviewed?"* Yes → a pillar note. No → `rounds/`.
"Separate read and write tools" is true at work, so it goes in a note. "Draw the architecture in under 3 minutes" is
only true in an interview, so it goes in a round. Nothing lands in a round folder just because it was useful for that
round.

- A topic question goes in the checklist of the note that answers it. If no note answers it, it's a gap for the
  curriculum, not a row. Authoring and wiring steps: the [`/practice` skill](../../.claude/skills/practice/SKILL.md).
- Round files carry `units:` frontmatter where the mapping to the curriculum is clear. `make crosswalk` turns those
  into [`../CROSSWALK.md`](../CROSSWALK.md).
- New files stay local until added to the allowlist in `practice/.gitignore`, after clearing the licence and checking
  for anything personal.
- Strip the preamble on ingest: content starts at the `#`. Anything the model said *about* the notes goes in `sources:`,
  and so does scraped page chrome.
- Librarian imports this folder as the `interviewing` course with `make import-courses`, so keep links relative and
  keep these files self-contained.
