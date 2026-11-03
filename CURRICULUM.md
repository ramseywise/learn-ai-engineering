# Learn AI Engineering: program curriculum

> A practical curriculum for understanding data, machine learning, large language models, and the systems that make them useful and reliable.

This is the program: outcomes, roles, paths, and the portfolio standard. It helps you choose a direction and connects the subject courses. Each subject README is the syllabus for its own objectives and evidence; each pillar README gives its reading order, decks, drills, and labs.

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
5. Keep the unit's mastery evidence, a working artifact plus assumptions, checks, and limitations, in a portfolio.

Librarian can present these same materials as lessons, decks, practice, and progress. This document deliberately describes learning outcomes rather than repository operations or build commands.

## Subject courses

| Course | What you learn | Recommended preparation | Syllabus |
|---|---|---|---|
| Programming | The Python, SQL, and TypeScript fluency needed to read, test, and build technical systems, the computer science behind them, the software design to keep them changeable, the backend and system design to keep them running under load, and the frontend and UX to make them usable. | None | [Syllabus](programming/README.md) |
| Data analytics | Turn messy data into statistically honest, decision-ready analysis. | Python foundations; SQL alongside it | [Syllabus](data-analytics/README.md) |
| Data science | Fit, evaluate, explain, and apply classical, neural, NLP, time-series, and recommender models. | Python and data-analytics foundations | [Syllabus](data-science/README.md) |
| Data engineering | Build the storage, ingestion, transformation, quality, serving, and governance systems that data products rely on. | Python and SQL; data analytics recommended, not required | [Syllabus](data-engineering/README.md) |
| Generative AI | Understand LLMs; build retrieval, agents, evaluation, observability, alignment, and applications. | Python helps; data and ML enrich the later units | [Syllabus](generative-ai/README.md) |
| AI engineering | Build reliable AI products through prompt, context, harness, loop, graph, inference, multimodal, and safety engineering. | Generative-AI fundamentals | [Syllabus](ai-engineering/README.md) |

## Role map

Choose by the job you want. *Core* is what the role does daily, and *awareness* is enough to work with the people who own it. The learning paths below are routes through the same material for the roles that have one.

| Role | Owns | Core | Awareness | Evidence to show |
|---|---|---|---|---|
| Backend engineer | APIs, data stores, reliability of a service | [Programming](programming/README.md): Python or TypeScript, SQL, [computer science foundations](programming/computer-science/README.md), [software design](programming/software-design/README.md), [backend and system design](programming/backend-and-system-design/README.md) | [Data engineering](data-engineering/README.md): storage foundations; [frontend and UX](programming/frontend-and-ux/README.md) | A tested service with a design you can defend under failure |
| Frontend engineer | The interface, its state and its accessibility | [Programming](programming/README.md): TypeScript, [frontend and UX](programming/frontend-and-ux/README.md), [software design](programming/software-design/README.md) | [backend and system design](programming/backend-and-system-design/README.md); AI interfaces if the product uses LLMs | A working, accessible interface with browser tests |
| Full-stack engineer | A feature from database to screen | [Programming](programming/README.md): TypeScript or Python, SQL, [software design](programming/software-design/README.md), [backend and system design](programming/backend-and-system-design/README.md), [frontend and UX](programming/frontend-and-ux/README.md) | [computer science foundations](programming/computer-science/README.md); [AI engineering](ai-engineering/README.md) | One small product built end to end |
| Data analyst | Trustworthy answers and decisions | [Programming](programming/README.md): Python, SQL; [Data analytics](data-analytics/README.md) | [Data science](data-science/README.md); [Data engineering](data-engineering/README.md) | A reproducible analysis and decision memo (Path A) |
| Data scientist | Validated models and model-driven decisions | [Programming](programming/README.md): Python, SQL; [Data analytics](data-analytics/README.md): Units 01 to 03; [Data science](data-science/README.md) | [Data engineering](data-engineering/README.md): ML platform; [Generative AI](generative-ai/README.md) | A validated model with an honest error analysis (Path B) |
| Data engineer | Pipelines, stores and data quality | [Programming](programming/README.md): Python, SQL; [Data engineering](data-engineering/README.md) | [Data analytics](data-analytics/README.md): Units 01 to 03; [backend and system design](programming/backend-and-system-design/README.md) | A reproducible pipeline with monitoring evidence (Path C) |
| ML engineer | Models in production | [Programming](programming/README.md): Python, [software design](programming/software-design/README.md); [Data science](data-science/README.md); [Data engineering](data-engineering/README.md): ML platform | [backend and system design](programming/backend-and-system-design/README.md); [Generative AI](generative-ai/README.md) | A served model with training, monitoring and rollback |
| AI engineer | Evaluated LLM applications | [Programming](programming/README.md): Python; [Generative AI](generative-ai/README.md); [AI engineering](ai-engineering/README.md) | [Data analytics](data-analytics/README.md): Units 02 and 03; [backend and system design](programming/backend-and-system-design/README.md); [frontend and UX](programming/frontend-and-ux/README.md) | An LLM application with an evaluation set and a safety boundary (Path D) |
| Platform engineer or SRE | Deployment, capacity and incident response | [Programming](programming/README.md): [computer science foundations](programming/computer-science/README.md), [backend and system design](programming/backend-and-system-design/README.md); [Data engineering](data-engineering/README.md): storage foundations and operations | [AI engineering](ai-engineering/README.md): inference | A deployed service with SLOs, a load test and a restore you've proved |
| Forward-deployed engineer | Shipping an AI system inside a customer's world | [Programming](programming/README.md): Python, SQL; [Generative AI](generative-ai/README.md); [AI engineering](ai-engineering/README.md); [backend and system design](programming/backend-and-system-design/README.md) | [frontend and UX](programming/frontend-and-ux/README.md); [Data engineering](data-engineering/README.md); AI product scoping in [Generative AI](generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product.md) | A scoped pilot with a metric, a cost estimate and a working demo |

## Learning paths

### Path A: Data analyst

**Goal:** answer business questions with trustworthy analysis and useful communication.

1. [Programming](programming/README.md): Python foundations and SQL.
2. [Data analytics](data-analytics/README.md): complete all six units and retain the applied-analysis portfolio.
3. Optional depth: [Data science](data-science/README.md) for predictive modelling, or [Data engineering](data-engineering/README.md) for durable pipelines.

### Path B: Data scientist

**Goal:** turn data into validated predictive models and model-driven decisions.

1. [Programming](programming/README.md): Python and SQL.
2. [Data analytics](data-analytics/README.md): Units 01 to 03 as the essential foundation; Unit 04 and Unit 06 provide valuable depth.
3. [Data science](data-science/README.md): work through the core model-building units, then choose NLP, time series, or recommenders to suit your work.
4. Optional depth: [Data engineering](data-engineering/README.md) for production data and ML platforms.

### Path C: Data engineer

**Goal:** make trustworthy data available for analytics, ML, and AI applications.

1. [Programming](programming/README.md): Python and SQL.
2. [Data analytics](data-analytics/README.md), recommended and not required: Unit 01, then the statistical and experimentation foundations in Units 02 and 03.
3. [Data engineering](data-engineering/README.md): complete the pillars in order; revisit quality and governance during every project.
4. Optional depth: [Data science](data-science/README.md) for ML-platform users, or [Generative AI](generative-ai/README.md) for LLM-data systems.

### Path D: AI engineer

**Goal:** build reliable, evaluated LLM-powered applications.

1. [Programming](programming/README.md): Python; add TypeScript when it is your application language.
2. [Generative AI](generative-ai/README.md): LLM fundamentals, retrieval, agents, observability, and evaluation.
3. [AI engineering](ai-engineering/README.md): prompt, context, harness, loop, and graph engineering; then inference, multimodal, and safety.
4. [Data analytics](data-analytics/README.md): Units 02 and 03 strengthen experiment design and result interpretation.

### Path E: Full-stack data and AI

**Goal:** understand the entire journey from raw data to a production AI product.

1. [Programming](programming/README.md)
2. [Data analytics](data-analytics/README.md)
3. [Data science](data-science/README.md)
4. [Data engineering](data-engineering/README.md)
5. [Generative AI](generative-ai/README.md)
6. [AI engineering](ai-engineering/README.md)

This broad path is intentionally iterative: return to earlier courses as later projects reveal gaps.

## Portfolio standard

Completion is demonstrated by artifacts, not by reading alone. A well-rounded portfolio includes:

- a small tested Python or TypeScript program and a set of analytical SQL queries;
- a reproducible analysis with uncertainty, a decision memo, and an honest visualisation;
- a predictive-model or data-engineering project with validation and monitoring evidence;
- an LLM application with an evaluation set, traces or measurements, a safety boundary, and an explanation of trade-offs.

Choose artifacts that match your path; the subject syllabi define the unit-level standard.

## Sources and depth

Each course maintains its own source map. Start with the subject README's Primary texts, then use the pillar's `references.md` to find books, papers, videos, courses, and primary documentation behind a specific chapter. Use the notes and labs as the primary learning surface; use references to deepen a question that practice has made concrete. Upstream material and its licences are in [THIRD_PARTY.md](THIRD_PARTY.md).

## Where to go next

This program has no single finish line. Choose the next subject based on the system you want to build: analytics for decisions, data science for models, data engineering for durable data systems, generative AI for LLM capabilities, and AI engineering for reliable AI products.
