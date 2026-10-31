# Generative AI

> **Depth domain.** This folder goes deep on the seven pillars of generative AI.
> The [interviewing guides](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md) are the compressed
> summary layer — read those for exam prep. Read here for synthesis and depth.

---

## The seven pillars

```
LLM fundamentals → RAG & retrieval → Agentic foundations → Agentic frameworks
                                    → RL & alignment
                                    → Observability
                                    → Agentic applications
```

The order encodes dependency and when each idea emerged:

- **LLM fundamentals** — what these models are, how they are trained and adapted, how to prompt and call them. Everything else builds on this.
- **RAG & retrieval** — the first killer-app pattern: give a model external knowledge at inference time. Presumes prompting.
- **Agentic foundations** — models that plan, use tools and operate in loops.
- **Agentic frameworks** — LangGraph, Google ADK and LangSmith: choosing and configuring the tooling.
- **RL & alignment** — how a pretrained model becomes an assistant (RLHF, DPO/GRPO, Constitutional AI) and how agents are post-trained.
- **Observability** — tracing, scoring and evaluation pipelines for LLM applications.
- **Agentic applications** — complete projects built with the frameworks.

Every pillar has the same shape: a `README.md` with reading order and rules of thumb, `notes/` numbered in reading order, `references.md` mapping every source to the notes that use it, `sources/` for local PDFs and figures, and `practice/` for runnable labs. See [ai-engineering/PILLAR-LAYOUT.md](../ai-engineering/PILLAR-LAYOUT.md).

External courses, books, papers and tools are collected in each pillar's `references.md`; cross-pillar links are under [General resources](#general-resources). Bojie Li's *AI Agents in Depth* (Apache-2.0) is synthesised into pillars [03](03-agentic-foundations/README.md), [05](05-RL/README.md) and [07](07-agentic-applications/README.md); each note links its labs upstream.

---

## Pillar → interviewing-guide crosswalk

| Pillar | Depth (here) | Summary (guide) |
|---|---|---|
| LLM fundamentals | [01-llm-fundamentals](01-llm-fundamentals/README.md) | [2-llm-fundamentals](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/2-llm-fundamentals/00-overview.md) |
| RAG & retrieval | [02-rag-retrieval](02-rag-retrieval/README.md) | [3-rag](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/3-rag/00-overview.md) |
| Agentic foundations | [03-agentic-foundations](03-agentic-foundations/README.md) | [4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md) |
| Agentic frameworks | [04-agentic-frameworks](04-agentic-frameworks/README.md) | [4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md) |
| RL & alignment | [05-RL](05-RL/README.md) | [2-llm-fundamentals](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/2-llm-fundamentals/00-overview.md) |
| Observability | [06-observability](06-observability/README.md) | [6-evals-observability](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/6-evals-observability/00-overview.md) |
| Agentic applications | [07-agentic-applications](07-agentic-applications/README.md) | [4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md) |

---

## Summary vs. depth split

**Interviewing guides** = compressed summaries for exam prep, one per topic, at the depth an interview loop needs.

**This folder** = depth for practitioners. Each pillar README says what the topic is, where it sits in the path, the order to read its notes in and the rules of thumb worth remembering, then links back to its guide.

Notes live inside each pillar's `notes/` folder with frontmatter (`origin`, `sources`, `confidence`, `cleaned`). There is no separate pointer layer for generative-ai content; `interviewing/guides/` (in sisyphus) is the only summary layer, and it links into both `ai-engineering/` and `generative-ai/` for depth.

---

## Relationship to ai-engineering

These two folders are complementary, not redundant:

- **generative-ai/** is the **application wave**: building things with LLMs. It maps the course material, foundational papers and practical patterns for using LLMs.
- **[ai-engineering/](../ai-engineering/README.md)** is the **discipline wave**: the engineering practices that make LLM applications reliable, observable and maintainable. It emerged after the application wave and presumes it.

Temporal order: learn the gen-AI pillars first; the ai-engineering foundations (prompt → context → harness → loop → graph → eval, with inference underneath) layer engineering discipline on top. No content is duplicated: where a topic is covered in both, the gen-AI note gives the application-level summary and links to the ai-engineering note for depth.

| gen-AI pillar | ai-engineering depth |
|---|---|
| 01 LLM fundamentals | [01-prompt-engineering](../ai-engineering/01-prompt-engineering/README.md) (prompting technique depth), [07-inference-engineering](../ai-engineering/07-inference-engineering/README.md) (serving) |
| 02 RAG & retrieval | [02-context-engineering](../ai-engineering/02-context-engineering/README.md) + [05-graph-engineering](../ai-engineering/05-graph-engineering/README.md) |
| 03–04 Agentic foundations + frameworks | [03-harness-engineering](../ai-engineering/03-harness-engineering/README.md) + [04-loop-engineering](../ai-engineering/04-loop-engineering/README.md) |
| 05 RL & alignment | [06-eval](../ai-engineering/06-eval/README.md) (environments and graders as training signal) |
| 06 Observability | [06-eval](../ai-engineering/06-eval/README.md) (evaluation and measurement) |

---

## TypeScript

Runnable Anthropic SDK examples (single call, streaming, structured output, tool loop, multi-turn) are in [01-llm-fundamentals/practice/](01-llm-fundamentals/practice/01-typescript-sdk/README.md).
Labs in the other pillars are Python unless their README says otherwise.

---

## General resources

Links that belong to no single pillar. They were kept from the retired `resources.md` (2026-10-31).
Each pillar's own courses, books and papers are in its `references.md`.

### Python and ML toolchain

These are the libraries the notebooks assume. Install per project with `uv`/`pip` from
each project's `pyproject.toml`. Don't install them all at once.

| Area | Libraries |
|---|---|
| Data | [NumPy](https://numpy.org/doc/), [pandas](https://pandas.pydata.org/docs/), [SciPy](https://docs.scipy.org/doc/scipy/), [Matplotlib](https://matplotlib.org/stable/), [seaborn](https://seaborn.pydata.org/) |
| Classical ML | [scikit-learn](https://scikit-learn.org/stable/), [XGBoost](https://xgboost.readthedocs.io/), [LightGBM](https://lightgbm.readthedocs.io/), [CatBoost](https://catboost.ai/docs/) |
| Deep learning | [PyTorch](https://pytorch.org/docs/), [TensorFlow](https://www.tensorflow.org/learn) / [Keras](https://keras.io/) |
| Vision | [OpenCV](https://docs.opencv.org/), [scikit-image](https://scikit-image.org/docs/stable/), [Pillow](https://pillow.readthedocs.io/) |

### Foundations (math, Python, classical ML)

- [MIT 18.06 Linear Algebra](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/) — Strang's lectures.
- [CS50's Introduction to Programming with Python](https://www.edx.org/learn/python/harvard-university-cs50-s-introduction-to-programming-with-python); practice on [HackerRank Python](https://www.hackerrank.com/domains/python) (see [`programming/`](https://github.com/ramseywise/sisyphus/blob/main/drills/README.md)).
- [Machine Learning Specialization (Andrew Ng)](https://www.coursera.org/specializations/machine-learning-introduction) — the course behind [`data-science/`](../data-science/README.md)'s Ng notebooks.
- [CS50's Introduction to AI](https://cs50.harvard.edu/ai/) and [AIMA](https://aima.cs.berkeley.edu/) — classical AI: search, reasoning, planning.
- [Designing Machine Learning Systems](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/) (Huyen) and [Made With ML](https://madewithml.com/) — production ML.

### Prompting → [ai-engineering/01-prompt](../ai-engineering/01-prompt-engineering/README.md)

- [Anthropic prompt engineering docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) · [OpenAI Cookbook](https://cookbook.openai.com/)

### Staying current

- Papers: the [AI Papers of the Week](../ai-engineering/02-context-engineering/references.md) flow (`/papers` skill) · [Distill](https://distill.pub/) (archive)
- Newsletters: [TLDR AI](https://tldr.tech/ai) · [The Rundown AI](https://www.therundown.ai/)

## Removed

Earlier versions of this README described `mcp-server-template/`, `mcp/`, `chatbot/berlin/`,
and `chatbot/BERT/`. None of these were ever committed to this repo, and none remain on disk —
they are not recoverable from git history. Recorded here because this README is the only
surviving description of them:

- `mcp-server-template/` — a generic FastMCP server template (env-var token auth → MCP tools),
  extracted from a personal integration against a SaaS API.
- `mcp/` — the original vendor-tied accounting-API integration that the template came from.
- `chatbot/BERT/` — appeared to be real production work (AWS Lambda deployment code) rather
  than course material.
- `chatbot/berlin/` — a reference chatbot clone.

`chatbot/deep_research_bench/` and `chatbot/deep-research-bot/` now live in [07-agentic-applications/practice/](07-agentic-applications/practice/).
