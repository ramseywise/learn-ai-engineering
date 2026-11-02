# Generative AI

> **Depth domain.** This folder goes deep on the eight pillars of generative AI.
> The [interviewing guides](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md) are the compressed
> summary layer — read those for exam prep. Read here for synthesis and depth.

---

## What this is

A course in building with large language models, from what a model is to a complete agent you can trust. Each pillar is a set of chapters with runnable code, a lecture deck, and a references file that maps every source to the chapter using it. Python is the course language, and blocks that need a paid key are marked `# illustrative`.

## Why this order

Each pillar exists because the previous one left a problem behind. A model on its own knows only its training data, so we give it retrieval. Retrieval answers questions but doesn't act, so we give it tools and a loop. A hand-written loop gets repetitive, so we compare the frameworks that own it. A base model doesn't behave like an assistant, and an agent doesn't get better by itself, so we look at how training shapes both. Once something runs, we have to see inside it and say whether it's any good, which is observability and eval, read together. With those in hand we can build the complete applications.

## The eight pillars

```text
01 LLM fundamentals → 02 RAG & retrieval → 03 Agentic foundations → 04 Agentic frameworks
                                                                           │
                                                                    05 RL & alignment
                                                                           │
                                     06 Observability  ⇄  08 Eval (read side by side)
                                                                           │
                                                               07 Agentic applications
```

The numbers are stable folder names, not a strict sequence. 08 is the Eval pillar, moved here from ai-engineering, and it belongs beside 06 and before 07 in your reading. 09 is LLMs from scratch, moved here from data science, and it reads straight after 01.

| Read | Pillar | The question it answers | Notes | Deck |
|---|---|---|---|---|
| 1 | [01 LLM fundamentals](01-llm-fundamentals/README.md) | What are these models, and how do you prompt, call and adapt them? | 14 | [pptx](01-llm-fundamentals/slides/llm-fundamentals.pptx) |
| 1b | [09 LLMs from scratch](09-llms-from-scratch/README.md) | What is inside a GPT, line by line? | 3 | [pptx](09-llms-from-scratch/slides/llms-from-scratch.pptx) |
| 2 | [02 RAG & retrieval](02-rag-retrieval/README.md) | How do you give a model knowledge at inference time? | 14 | in progress |
| 3 | [03 Agentic foundations](03-agentic-foundations/README.md) | How do models plan, use tools and work in loops? | 7 | [pptx](03-agentic-foundations/slides/agentic-foundations.pptx), [pdf](03-agentic-foundations/slides/agentic-foundations.pdf) |
| 4 | [04 Agentic frameworks](04-agentic-frameworks/README.md) | What do LangGraph, ADK and LangSmith do for one research agent, and which should you pick? | 7 | [pptx](04-agentic-frameworks/slides/agentic-frameworks.pptx), [pdf](04-agentic-frameworks/slides/agentic-frameworks.pdf) |
| 5 | [05 RL & alignment](05-RL/README.md) | How does a pretrained model become an assistant, and how are agents post-trained? | 14 | [pptx](05-RL/slides/rl-and-alignment.pptx), [pdf](05-RL/slides/rl-and-alignment.pdf) |
| 6 | [06 Observability](06-observability/README.md) | What happened inside a run, and what did it cost? | 6 | [pptx](06-observability/slides/observability.pptx), [pdf](06-observability/slides/observability.pdf) |
| 6 | [08 Eval](08-eval/README.md) | Was it any good, and is a difference real? | 13 | [pptx](08-eval/slides/eval-engineering.pptx), [pdf](08-eval/slides/eval-engineering.pdf) |
| 7 | [07 Agentic applications](07-agentic-applications/README.md) | What does it take to ship a search, research, voice, coding or data-analysis agent? | 6 | [pptx](07-agentic-applications/slides/agentic-applications.pptx), [pdf](07-agentic-applications/slides/agentic-applications.pdf) |

**Reading 06 and 08 together.** Observability is the tooling: traces, scores, judges over exports and dashboards, worked on one support agent's bad fortnight. Eval is the discipline: what correct means, which tasks represent real use, whether a grader can be trusted, and whether a difference is real. Read 06 chapters 1 and 2 first so you have data to reason about, then Eval's chapters on [graders](08-eval/notes/04-graders.md) and [reading results](08-eval/notes/09-reading-results.md), then return for the rest of 06.

Every pillar has the same shape: a `README.md` with reading order and rules of thumb, `notes/` numbered in reading order, `references.md` mapping every source to the notes that use it, `sources/` for local PDFs and figures, `practice/` for runnable labs, and `slides/` for the deck, rebuilt with `make slides PILLAR=generative-ai/<pillar> STRICT=1 PREVIEW=1`. See [ai-engineering/PILLAR-LAYOUT.md](../ai-engineering/PILLAR-LAYOUT.md).

External courses, books, papers and tools are collected in each pillar's `references.md`; cross-pillar links are under [General resources](#general-resources). Bojie Li's *AI Agents in Depth* (Apache-2.0) is synthesised into pillars [03](03-agentic-foundations/README.md), [05](05-RL/README.md) and [07](07-agentic-applications/README.md).

## Rules of thumb across the pillars

- Start with the simplest thing that can work: a prompt before retrieval, retrieval before a loop, a fixed graph before an open one.
- Write a loop by hand once before you judge a framework.
- Log what you'll need next month today, since the questions you can answer later are fixed by what you record now.
- Read results by category; an average can rise while a safety rule breaks.
- A coding agent's sentence is not a verdict and neither is a data agent's. Recompute, and keep some tests out of sight.
- Choose by the numbers your own task produces, not a leaderboard.

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
| Eval | [08-eval](08-eval/README.md) | [6-evals-observability](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/6-evals-observability/00-overview.md) |

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

Temporal order: learn the gen-AI pillars first; the ai-engineering foundations (prompt → context → harness → loop → graph, with inference underneath) layer engineering discipline on top. No content is duplicated: where a topic is covered in both, the gen-AI note gives the application-level summary and links to the ai-engineering note for depth.

| gen-AI pillar | Depth elsewhere |
|---|---|
| 01 LLM fundamentals | [01-prompt-engineering](../ai-engineering/01-prompt-engineering/README.md) (prompting technique depth), [07-inference-engineering](../ai-engineering/07-inference-engineering/README.md) (serving) |
| 02 RAG & retrieval | [02-context-engineering](../ai-engineering/02-context-engineering/README.md) + [05-graph-engineering](../ai-engineering/05-graph-engineering/README.md) |
| 03–04 Agentic foundations + frameworks | [03-harness-engineering](../ai-engineering/03-harness-engineering/README.md) + [04-loop-engineering](../ai-engineering/04-loop-engineering/README.md) |
| 05 RL & alignment | [08-eval](08-eval/README.md) in this folder (environments and graders as training signal) |
| 06 Observability | [08-eval](08-eval/README.md) in this folder (evaluation and measurement) |
| 07 Agentic applications | [08-multimodal-engineering](../ai-engineering/08-multimodal-engineering/README.md) (voice and vision), [09-safety-and-security](../ai-engineering/09-safety-and-security/README.md) (what an agent may do) |
| 08 Eval | Measures all of the above: the five ai-engineering foundations and the pillars here |

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
