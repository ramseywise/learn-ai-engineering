# Generative AI

> Learn what language models do, how to ground and evaluate them, and how to build agentic applications that are useful rather than merely impressive.

## What this is

A course in building with large language models, from what a model is to a complete agent you can trust. Each pillar is a set of chapters with runnable code, a lecture deck, and a references file that maps every source to the chapter using it. Python is the course language, and blocks that need a paid key are marked `# illustrative`.

## Why this order

Each pillar exists because the previous one left a problem behind. A model on its own knows only its training data, so we give it retrieval. Retrieval answers questions but doesn't act, so we give it tools and a loop. A hand-written loop gets repetitive, so we compare the frameworks that own it. A base model doesn't behave like an assistant, and an agent doesn't get better by itself, so we look at how training shapes both. Once something runs, we have to see inside it and say whether it's any good, which is observability and eval, read together. With those in hand we can build the complete applications.
## Course outcomes

By the end, you can explain the lifecycle and behaviour of LLMs; build and improve a retrieval system; design tool-using agents; compare frameworks; reason about RL and post-training; observe and evaluate systems; build applications; and implement key model mechanics from scratch.

## Before you begin

No formal prerequisite is required for Unit 01. [Programming: Python](../programming/python/README.md) makes labs substantially easier; [Data Analytics](../data-analytics/README.md) and [Data Science](../data-science/README.md) deepen evaluation and modelling topics.

**Learning model:** read chapters in order, review with the deck, complete the pillar lab where supplied, and save the stated evidence. API keys, GPUs, and optional external services are never assumed unless the relevant README explicitly says so.

## The nine pillars

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

| Read | Pillar | The question it answers | Mastery evidence | Deck |
|---|---|---|---|---|
| 1 | [01 LLM fundamentals](01-llm-fundamentals/README.md) | What are these models, and how do you prompt, call and adapt them? | Explain and call an LLM with controlled decoding | [pptx](01-llm-fundamentals/slides/llm-fundamentals.pptx) |
| 1b | [09 LLMs from scratch](09-llms-from-scratch/README.md) | What is inside a GPT, line by line? | Built/modified micrograd or nanoGPT exercise | [pptx](09-llms-from-scratch/slides/llms-from-scratch.pptx) |
| 2 | [02 RAG & retrieval](02-rag-retrieval/README.md) | How do you give a model knowledge at inference time? | Measured retrieval pipeline | in progress |
| 3 | [03 Agentic foundations](03-agentic-foundations/README.md) | How do models plan, use tools and work in loops? | Bounded agent design | [pptx](03-agentic-foundations/slides/agentic-foundations.pptx), [pdf](03-agentic-foundations/slides/agentic-foundations.pdf) |
| 4 | [04 Agentic frameworks](04-agentic-frameworks/README.md) | What do LangGraph, ADK and LangSmith do for one research agent, and which should you pick? | Same workflow implemented and compared | [pptx](04-agentic-frameworks/slides/agentic-frameworks.pptx), [pdf](04-agentic-frameworks/slides/agentic-frameworks.pdf) |
| 5 | [05 RL & alignment](05-RL/README.md) | How does a pretrained model become an assistant, and how are agents post-trained? | Policy/value experiment and limitation analysis | [pptx](05-RL/slides/rl-and-alignment.pptx), [pdf](05-RL/slides/rl-and-alignment.pdf) |
| 6 | [06 Observability](06-observability/README.md) | What happened inside a run, and what did it cost? | Diagnosed trace and evaluation plan | [pptx](06-observability/slides/observability.pptx), [pdf](06-observability/slides/observability.pdf) |
| 6 | [08 Eval](08-eval/README.md) | Was it any good, and is a difference real? | Reproducible evaluation report and gate | [pptx](08-eval/slides/eval-engineering.pptx), [pdf](08-eval/slides/eval-engineering.pdf) |
| 7 | [07 Agentic applications](07-agentic-applications/README.md) | What does it take to ship a search, research, voice, coding or data-analysis agent? | Working application with boundaries | [pptx](07-agentic-applications/slides/agentic-applications.pptx), [pdf](07-agentic-applications/slides/agentic-applications.pdf) |

**Reading 06 and 08 together.** Observability is the tooling: traces, scores, judges over exports and dashboards, worked on one support agent's bad fortnight. Eval is the discipline: what correct means, which tasks represent real use, whether a grader can be trusted, and whether a difference is real. Read 06 chapters 1 and 2 first so you have data to reason about, then Eval's chapters on [graders](08-eval/notes/04-graders.md) and [reading results](08-eval/notes/09-reading-results.md), then return for the rest of 06.

Every pillar has the same shape: a `README.md` with reading order and rules of thumb, `notes/` numbered in reading order, `references.md` mapping every source to the notes that use it, `sources/` for local PDFs and figures, `practice/` for runnable labs, and `slides/` for the deck, rebuilt with `make slides PILLAR=generative-ai/<pillar> STRICT=1 PREVIEW=1`. See the [pillar layout](https://github.com/ramseywise/librarian/blob/main/.claude/skills/pillar/references/pillar-layout.md).

Bojie Li's *AI Agents in Depth* (Apache-2.0) is synthesised into pillars [03](03-agentic-foundations/README.md), [05](05-RL/README.md) and [07](07-agentic-applications/README.md). `deep_research_bench` and `deep-research-bot` are in [07's practice](07-agentic-applications/practice/).

## Units

### [01 LLM fundamentals](01-llm-fundamentals/README.md)

**Objectives:** explain tokenisation, embeddings, attention ([Vaswani et al.](https://arxiv.org/abs/1706.03762)), scale, decoding, pretraining, instruction tuning, preference optimisation, PEFT, prompting, and local/open-weight inference ([Alammar and Grootendorst](https://www.llm-book.com/)); call models from code and diagnose hallucination.

**Learning:** [chapters, deck, and practice](01-llm-fundamentals/README.md). **Evidence:** a small model experiment with documented prompt, parameters, output behaviour, and limits.

### [02 RAG and retrieval](02-rag-retrieval/README.md)

**Objectives:** design ingestion, chunking, indexing, hybrid retrieval, reranking, generation, production, agentic, cached, and managed RAG choices ([Lewis et al. 2020](https://arxiv.org/abs/2005.11401); Huyen, ch. 6); measure the bottleneck before tuning.

**Learning:** [chapters and practice](02-rag-retrieval/README.md). **Evidence:** a retrieval system with a query set, retrieval/generation measurements, and a justified improvement. The deck is in progress.

### [03 Agentic foundations](03-agentic-foundations/README.md)

**Objectives:** define an agent boundary ([Li, ch. 1](https://github.com/bojieli/ai-agent-book)); design tool use and ReAct loops ([Yao et al. 2022](https://arxiv.org/abs/2210.03629)); externalise memory; choose multi-agent patterns; set autonomy and guardrails.

**Learning:** [chapters and deck](03-agentic-foundations/README.md). **Evidence:** a bounded agent design specifying goals, tools, state, verifier, stop conditions, and failure handling.

### [04 Agentic frameworks](04-agentic-frameworks/README.md)

**Objectives:** compare orchestration abstractions, state, tools, memory, tracing, and deployment trade-offs ([LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview); [ADK docs](https://adk.dev/)); avoid confusing framework choice with agent design.

**Learning:** [chapters, deck, and practice](04-agentic-frameworks/README.md). **Evidence:** the same narrow workflow implemented or specified in two frameworks with a reasoned choice.

### [05 RL and alignment](05-RL/README.md)

**Objectives:** reason about MDPs, value functions, policy optimisation ([Sutton and Barto](http://incompleteideas.net/book/the-book-2nd.html)), reward design, RLHF, constitutional approaches, and their failure modes ([Li, ch. 8](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter8.md)).

**Learning:** [chapters, deck, and practice](05-RL/README.md). **Evidence:** a policy/value exercise plus a description of reward, feedback loop, and likely reward-hacking failure.

### [06 Observability](06-observability/README.md)

**Objectives:** instrument traces ([Dong et al.](https://arxiv.org/abs/2411.05285)); create datasets; score and compare runs; diagnose failures ([Beyer et al., ch. 6](https://sre.google/sre-book/monitoring-distributed-systems/)); manage latency and cost; turn observations into changes.

**Learning:** [chapters, deck, and practice](06-observability/README.md). **Evidence:** a trace review with a named failure, measurement, intervention, and regression check.

### [07 Agentic applications](07-agentic-applications/README.md)

**Objectives:** assemble retrieval, tools, memory, evaluation, and controls into scoped application patterns, including research ([Du et al.](https://arxiv.org/abs/2506.11763); [Li, ch. 6](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter6.md)) and data-analysis agents.

**Learning:** [chapters, deck, and practice](07-agentic-applications/README.md). **Evidence:** a working application with explicit permissions, data boundaries, success criteria, and human handoff.

### [08 Eval](08-eval/README.md)

**Objectives:** design task datasets ([Anthropic, *Demystifying evals*](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)); choose metrics; use human and model judges cautiously ([Husain and Shankar](https://hamel.dev/blog/posts/field-guide/)); analyse uncertainty; test regressions; make evaluation a release gate.

**Learning:** [chapters, deck, and practice](08-eval/README.md). **Evidence:** a versioned evaluation report with failure taxonomy, confidence/uncertainty, and a CI or release decision.

### [09 LLMs from scratch](09-llms-from-scratch/README.md)

**Objectives:** implement automatic differentiation, train a character model, and understand the path from micrograd to a compact GPT ([Karpathy](https://karpathy.ai/zero-to-hero.html); [Raschka](https://www.manning.com/books/build-a-large-language-model-from-scratch)).

**Learning:** [chapters, deck, and practice](09-llms-from-scratch/README.md). **Evidence:** a modified training run with hypothesis, metric, result, and explanation.

## Rules of thumb across the pillars

- Start with the simplest thing that can work: a prompt before retrieval, retrieval before a loop, a fixed graph before an open one.
- Write a loop by hand once before you judge a framework.
- Log what you'll need next month today, since the questions you can answer later are fixed by what you record now.
- Read results by category; an average can rise while a safety rule breaks.
- A coding agent's sentence is not a verdict and neither is a data agent's. Recompute, and keep some tests out of sight.
- Choose by the numbers your own task produces, not a leaderboard.

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

## TypeScript

Runnable Anthropic SDK examples (single call, streaming, structured output, tool loop, multi-turn) are in [01-llm-fundamentals/practice/](01-llm-fundamentals/practice/01-typescript-sdk/README.md).
Labs in the other pillars are Python unless their README says otherwise.

## Completion standard and next steps

Complete a portfolio containing a measured RAG system, a bounded agent design or implementation, an observability/evaluation report, and one end-to-end application. Each must name its task, data boundary, success metric, failure modes, and release or stop decision.

Continue to [AI Engineering](../ai-engineering/README.md) for production engineering discipline, or revisit [Data Science](../data-science/README.md) for modelling depth.

## Primary texts

- Alammar and Grootendorst, *Hands-On Large Language Models*: Unit 01
- Raschka, *Build a Large Language Model (From Scratch)*: Units 01 and 09
- Huyen, *AI Engineering*: across Units 01, 02, 05 and 08
- Li, *AI Agents in Depth*: Units 03, 05 and 07
- Lakshmanan and Hapke, *Generative AI Design Patterns*: Unit 03
- Sutton and Barto, *Reinforcement Learning: An Introduction*: Unit 05
- Phoenix and Taylor, *Prompt Engineering for Generative AI*: Unit 04

Links that belong to no single pillar: [references.md](references.md). Everything else: each pillar's own `references.md`.
