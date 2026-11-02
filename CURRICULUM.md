# Learn AI Engineering: program curriculum

> A practical curriculum for understanding data, machine learning, large language models, and the systems that make them useful and reliable.

This is the program-level syllabus. It helps you choose a direction and connects the subject courses. Each subject curriculum is the authoritative workbook for its own learning objectives, chapters, decks, drills, labs, and sources.

## Program outcomes

By working through a path in this program, you will be able to:

1. Write reliable Python, SQL, and TypeScript for data and AI work.
2. Prepare data, quantify uncertainty, evaluate evidence, and make a defensible recommendation.
3. Train, assess, and explain predictive models while recognising their limits.
4. Build data pipelines whose outputs are reproducible, observable, governed, and useful downstream.
5. Explain how LLMs work and build retrieval, agentic, evaluation, and observability systems around them.
6. Engineer AI applications that are testable, secure, cost-aware, and suitable for production use.

## How to use this curriculum

Each subject is organised as a course workbook. A pillar is a unit; its notes are chapters, slides are lecture and recall material, and practice folders contain drills and labs. Work through a unit in this rhythm:

1. Read the chapters and reproduce their examples.
2. Review the deck and explain the ideas from memory.
3. Complete the `Try it` exercises and focused drills.
4. Complete a lab or applied task.
5. Keep the unit's mastery evidence—a working artifact plus assumptions, checks, and limitations—in a portfolio.

Librarian can present these same materials as lessons, decks, practice, and progress. This document deliberately describes learning outcomes rather than repository operations or build commands.

## Subject courses

| Course | What you learn | Recommended preparation | Curriculum |
|---|---|---|---|
| Programming | The Python, SQL, and TypeScript fluency needed to read, test, and build technical systems. | None | [Course curriculum](programming/CURRICULUM.md) |
| Data analytics | Turn messy data into statistically honest, decision-ready analysis. | Python foundations; SQL alongside it | [Course curriculum](data-analytics/CURRICULUM.md) |
| Data science | Fit, evaluate, explain, and apply classical, neural, NLP, time-series, and recommender models. | Python and data-analytics foundations | [Course curriculum](data-science/CURRICULUM.md) |
| Data engineering | Build the storage, ingestion, transformation, quality, serving, and governance systems that data products rely on. | Python, SQL, and data-analytics foundations | [Course curriculum](data-engineering/CURRICULUM.md) |
| Generative AI | Understand LLMs; build retrieval, agents, evaluation, observability, alignment, and applications. | Python helps; data and ML enrich the later units | [Course curriculum](generative-ai/CURRICULUM.md) |
| AI engineering | Build reliable AI products through prompt, context, harness, loop, graph, inference, multimodal, and safety engineering. | Generative-AI fundamentals | [Course curriculum](ai-engineering/CURRICULUM.md) |

## Learning paths

### Path A — Data analyst

**Goal:** answer business questions with trustworthy analysis and useful communication.

1. [Programming](programming/CURRICULUM.md): Python foundations and SQL.
2. [Data analytics](data-analytics/CURRICULUM.md): complete all six units and retain the applied-analysis portfolio.
3. Optional depth: [Data science](data-science/CURRICULUM.md) for predictive modelling, or [Data engineering](data-engineering/CURRICULUM.md) for durable pipelines.

### Path B — Data scientist

**Goal:** turn data into validated predictive models and model-driven decisions.

1. [Programming](programming/CURRICULUM.md): Python and SQL.
2. [Data analytics](data-analytics/CURRICULUM.md): Units 01–03 as the essential foundation; Unit 04 and Unit 06 provide valuable depth.
3. [Data science](data-science/CURRICULUM.md): work through the core model-building units, then choose NLP, time series, or recommenders to suit your work.
4. Optional depth: [Data engineering](data-engineering/CURRICULUM.md) for production data and ML platforms.

### Path C — Data engineer

**Goal:** make trustworthy data available for analytics, ML, and AI applications.

1. [Programming](programming/CURRICULUM.md): Python and SQL.
2. [Data analytics](data-analytics/CURRICULUM.md): Unit 01, then the statistical and experimentation foundations in Units 02–03.
3. [Data engineering](data-engineering/CURRICULUM.md): complete the pillars in order; revisit quality and governance during every project.
4. Optional depth: [Data science](data-science/CURRICULUM.md) for ML-platform users, or [Generative AI](generative-ai/CURRICULUM.md) for LLM-data systems.

### Path D — AI engineer

**Goal:** build reliable, evaluated LLM-powered applications.

1. [Programming](programming/CURRICULUM.md): Python; add TypeScript when it is your application language.
2. [Generative AI](generative-ai/CURRICULUM.md): LLM fundamentals, retrieval, agents, observability, and evaluation.
3. [AI engineering](ai-engineering/CURRICULUM.md): prompt, context, harness, loop, and graph engineering; then inference, multimodal, and safety.
4. [Data analytics](data-analytics/CURRICULUM.md): Units 02–03 strengthen experiment design and result interpretation.

### Path E — Full-stack data and AI

**Goal:** understand the entire journey from raw data to a production AI product.

1. [Programming](programming/CURRICULUM.md)
2. [Data analytics](data-analytics/CURRICULUM.md)
3. [Data science](data-science/CURRICULUM.md)
4. [Data engineering](data-engineering/CURRICULUM.md)
5. [Generative AI](generative-ai/CURRICULUM.md)
6. [AI engineering](ai-engineering/CURRICULUM.md)

This broad path is intentionally iterative: return to earlier courses as later projects reveal gaps.

## Portfolio standard

Completion is demonstrated by artifacts, not by reading alone. A well-rounded portfolio includes:

- a small tested Python or TypeScript program and a set of analytical SQL queries;
- a reproducible analysis with uncertainty, a decision memo, and an honest visualisation;
- a predictive-model or data-engineering project with validation and monitoring evidence;
- an LLM application with an evaluation set, traces or measurements, a safety boundary, and an explanation of trade-offs.

Choose artifacts that match your path; the subject curricula define the unit-level standard.

## Sources and depth

Each course maintains its own source map. Start with the course curriculum, then use the pillar's `references.md` to find books, papers, videos, courses, and primary documentation behind a specific chapter. Use the notes and labs as the primary learning surface; use references to deepen a question that practice has made concrete.

## Where to go next

This program has no single finish line. Choose the next subject based on the system you want to build: analytics for decisions, data science for models, data engineering for durable data systems, generative AI for LLM capabilities, and AI engineering for reliable AI products.
