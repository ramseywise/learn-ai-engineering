# Python

A personal knowledge base of Python for data work — courses, notebooks, and code examples,
organized by domain. Each category below mixes finished/authored notebooks with reference material
from books and courses; sub-folder READMEs (where they exist) go into more detail.

> **Self-learner?** Start at [CURRICULUM.md](CURRICULUM.md) — subject map, prerequisites,
> and three learning paths (AI Engineering, Data Engineering, Full-Stack Data).
> **Interview prep?** Start at [interviewing/guides/00-start-here.md](interviewing/guides/00-start-here.md) —
> ten pillars (+ Pillar 0 programming), ordered so each builds on the last.

> **Interview prep (extended):** [interviewing KB](interviewing/README.md) — study guides,
> round-by-round prep, and the role × topic matrix. Hands-on AI-engineering evidence (RAG,
> agents, evals, MCP) lives in the working repos — see [`../PORTFOLIO.md`](../PORTFOLIO.md).
> System-design writeups of those systems and a contract-based code-review drill are compiled
> in the librarian wiki (`system-design-*.md`, `code-review-drill-sanyi.md`).

### Python for Data Analysis ([`data-analytics/`](data-analytics/README.md))
- [Python Basics](https://github.com/ramseywise/Python/tree/main/data-analytics/Python%20Basics)
    - Operations
    - Texts
    - Arrays
    - DataFrames
    - Plotting
    - Aggregation
    - Time Series

- [Text Analytics with Python](https://github.com/ramseywise/Python/tree/main/data-analytics/Text%20Analytics%20with%20Python)
    - NLP Basics
    - Processing and Understanding Text
    - Feature Engineering
    - Text Clssification
    - Text Summarization and Topic Modeling
    - Text Similarity and Clustering
    - Semantic Analysis
    - Sentiment Analysis

### Python for Data Engineering ([`data-engineering/`](data-engineering/README.md))
- [DataTalks Data Engineering](https://github.com/ramseywise/Python/tree/main/data-engineering/DataTalks%20Data%20Engineering)
    - Docker
    - Workflow
    - DWH
    - Batch
    - Streaming

- [DataTalks MLOps](https://github.com/ramseywise/Python/tree/main/data-engineering/DataTalks%20MLOps)
    - experiment tracking
    - orchestration
    - deployment
    - monitoring

### Python for Data Science ([`data-science/`](data-science/README.md))
- [Intro to Machine Learning in Python](https://github.com/ramseywise/Python/tree/main/data-science/Intro%20to%20Machine%20Learning%20in%20Python)
    - supervised learning
    - unsupervised learning
    - feature engineering
    - model evaluation
    - pipelines

- [Andrew Ng's Machine Learning Course](https://github.com/ramseywise/Python/tree/main/data-science/Ng's%20Machine%20Learning%20Nbks)
    - linear regression
    - logistic regression
    - multi-class classification
    - neural networks
    - bias and variance
    - SVMs
    - K-means and PCA
    - Anomaly detection and recommender systems

- [Andrew Ng's Deep Learning Course](https://github.com/ramseywise/Python/tree/main/data-science/Ng's%20Deep%20Learning%20Nbks)
    - CNNs
    - Hyperparameter tuning
    - Sequence models

- `Bayes/` (now in `data-analytics/`) and `Python for ML Models/` — pruned to just the
  authored/completed work; generic third-party clones with no personal modification were
  deleted (see [data-analytics/README.md](data-analytics/README.md) for what moved where).

### Python for Generative AI ([`generative-ai/`](generative-ai/README.md))

Seven pillars, ordered by dependency and temporal emergence. Pairs with
[`ai-engineering/`](ai-engineering/README.md) — gen-AI builds things with LLMs;
ai-engineering is the discipline that makes them reliable.

- **[01 — LLM Fundamentals](generative-ai/01-llm-fundamentals/README.md)** — what LLMs
  are, how they're trained, how to prompt them. Course material: `intro-to-nlp/` (NLTK,
  TensorFlow, transformers) and `nn-zero-to-hero/` (Karpathy: micrograd, makemore, nanogpt).
  TypeScript examples in `typescript/` (Anthropic SDK: API call, structured output, function calling, multi-turn).

- **[02 — RAG & Retrieval](generative-ai/02-rag-retrieval/README.md)** — the first killer
  app pattern. Course material: DeepLearning.AI RAG, Knowledge Graphs for RAG.

- **[03 — Agentic Foundations](generative-ai/03-agentic-foundations/README.md)** — framework
  learning: AutoGen, LangGraph, AgenticAIFrameworks, context engineering, agent memory.

- **[04 — Agentic Frameworks](generative-ai/04-agentic-frameworks/README.md)** — framework
  reference: LangGraph and ADK notes, selection guides. Course material: AI-Agents-in-LangGraph,
  Long-Term-Agentic-Memory-With-LangGraph.

- **[05 — RL & Alignment](generative-ai/05-RL/README.md)** — reinforcement learning, RLHF,
  and how models are aligned post-pretraining.

- **[06 — Observability](generative-ai/06-observability/README.md)** — LangFuse tracing,
  scoring, and evaluation pipelines for LLM applications.

- **[07 — Agentic Applications](generative-ai/07-agentic-applications/README.md)** — specific
  built projects: internet-search agent, deep-research bot. Active project:
  `07-agentic-applications/chatbot/deep-research-bot/`.

### AI Engineering ([`ai-engineering/`](ai-engineering/README.md))
- Six foundations — **prompt → context → harness → loop → graph → eval**. Depth companion
  to the [interviewing guides](interviewing/guides/00-start-here.md) (guides summarize;
  this goes deep). Each pillar cross-links its guide, cleaned notes, and coursera code.

### Readings (distributed by pillar)
- Reference papers and book chapters, no notes — pure reference, colocated with the pillar that uses them:
    - `data-analytics/readings/` — statistics and data-viz references (ISLP, *Statistics Done Wrong*)
    - `data-engineering/8-data-eng-data-mesh/` — data mesh and data-engineering handouts
    - `generative-ai/01-llm-fundamentals/readings/` — prompting, RLHF, and LLM foundations
    - `generative-ai/02-rag-retrieval/3-rag/` — retrieval-augmented generation papers
    - `ai-engineering/05-graph/3-rag-knowledge-graphs/` — knowledge graphs for RAG
    - `ai-engineering/readings/ai_engineering/` — AI design, AI engineering, and performance books
    - `ai-engineering/readings/general/` — foundational ML/NLP papers (word2vec, LIME, interpretability)

### Programming ([`programming/`](programming/README.md))
- Practice problems and cloud/infra reference — doesn't fit the data-domain categories above, kept
  as its own bucket
    - `HackerRank/` — Python and SQL practice problems
    - `Leet-Code/` — arrays/hashing, two pointers, sliding windows, linked lists, plus a
      competitive-programming reference book
