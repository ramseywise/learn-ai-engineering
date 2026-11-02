# Generative AI: course curriculum

> Learn what language models do, how to ground and evaluate them, and how to build agentic applications that are useful rather than merely impressive.

This syllabus turns the nine pillars into a coherent course. Each pillar README owns chapter sequencing, setup, decks, practice, and full citations.

## Course outcomes

By the end, you can explain the lifecycle and behaviour of LLMs; build and improve a retrieval system; design tool-using agents; compare frameworks; reason about RL and post-training; observe and evaluate systems; build applications; and implement key model mechanics from scratch.

## Before you begin

No formal prerequisite is required for Unit 01. [Programming: Python](../programming/python/README.md) makes labs substantially easier; [Data Analytics](../data-analytics/README.md) and [Data Science](../data-science/README.md) deepen evaluation and modelling topics.

**Learning model:** read chapters in order, review with the deck, complete the pillar lab where supplied, and save the stated evidence. API keys, GPUs, and optional external services are never assumed unless the relevant README explicitly says so.

## Course map

| Unit | Focus | Mastery evidence |
|---|---|---|
| [01 LLM fundamentals](01-llm-fundamentals/README.md) | Tokens, transformers, training, inference | Explain and call an LLM with controlled decoding |
| [02 RAG and retrieval](02-rag-retrieval/README.md) | Grounded generation | Measured retrieval pipeline |
| [03 Agentic foundations](03-agentic-foundations/README.md) | Tools, memory, autonomy | Bounded agent design |
| [04 Agentic frameworks](04-agentic-frameworks/README.md) | Framework trade-offs | Same workflow implemented and compared |
| [05 Reinforcement learning](05-RL/README.md) | Sequential decisions and alignment | Policy/value experiment and limitation analysis |
| [06 Observability](06-observability/README.md) | Traces, datasets, and improvement | Diagnosed trace and evaluation plan |
| [07 Agentic applications](07-agentic-applications/README.md) | End-to-end patterns | Working application with boundaries |
| [08 Evaluation](08-eval/README.md) | Reliable measurement | Reproducible evaluation report and gate |
| [09 LLMs from scratch](09-llms-from-scratch/README.md) | Model mechanics | Built/modified micrograd or nanoGPT exercise |

## Unit syllabus

### 01 — LLM fundamentals
**Objectives:** explain tokenisation, embeddings, attention, scale, decoding, pretraining, instruction tuning, preference optimisation, PEFT, prompting, and local/open-weight inference; call models from code and diagnose hallucination. **Learning:** [14 chapters, deck, and practice](01-llm-fundamentals/README.md). **Evidence:** a small model experiment with documented prompt, parameters, output behaviour, and limits. **Key sources:** [Attention Is All You Need](https://arxiv.org/abs/1706.03762), the pillar [references](01-llm-fundamentals/references.md).

### 02 — RAG and retrieval
**Objectives:** design ingestion, chunking, indexing, hybrid retrieval, reranking, generation, production, agentic, cached, and managed RAG choices; measure the bottleneck before tuning. **Learning:** [12 chapters, deck, and practice](02-rag-retrieval/README.md). **Evidence:** a retrieval system with a query set, retrieval/generation measurements, and a justified improvement. **Key sources:** [pillar references](02-rag-retrieval/references.md).

### 03 — Agentic foundations
**Objectives:** define an agent boundary; design tool use and ReAct loops; externalise memory; choose multi-agent patterns; set autonomy and guardrails. **Learning:** [seven chapters and deck](03-agentic-foundations/README.md). **Evidence:** a bounded agent design specifying goals, tools, state, verifier, stop conditions, and failure handling. **Key sources:** [pillar references](03-agentic-foundations/references.md).

### 04 — Agentic frameworks
**Objectives:** compare orchestration abstractions, state, tools, memory, tracing, and deployment trade-offs; avoid confusing framework choice with agent design. **Learning:** [chapters, deck, and practice](04-agentic-frameworks/README.md). **Evidence:** the same narrow workflow implemented or specified in two frameworks with a reasoned choice. **Key sources:** [pillar references](04-agentic-frameworks/references.md).

### 05 — Reinforcement learning
**Objectives:** reason about MDPs, value functions, policy optimisation, reward design, RLHF, constitutional approaches, and their failure modes. **Learning:** [chapters, deck, and practice](05-RL/README.md). **Evidence:** a policy/value exercise plus a description of reward, feedback loop, and likely reward-hacking failure. **Key sources:** Sutton and Barto, *Reinforcement Learning*; [pillar references](05-RL/references.md).

### 06 — Observability
**Objectives:** instrument traces; create datasets; score and compare runs; diagnose failures; manage latency and cost; turn observations into changes. **Learning:** [chapters, deck, and practice](06-observability/README.md). **Evidence:** a trace review with a named failure, measurement, intervention, and regression check. **Key sources:** [pillar references](06-observability/references.md).

### 07 — Agentic applications
**Objectives:** assemble retrieval, tools, memory, evaluation, and controls into scoped application patterns, including research and data-analysis agents. **Learning:** [chapters, deck, and practice](07-agentic-applications/README.md). **Evidence:** a working application with explicit permissions, data boundaries, success criteria, and human handoff. **Key sources:** [pillar references](07-agentic-applications/references.md).

### 08 — Evaluation
**Objectives:** design task datasets; choose metrics; use human and model judges cautiously; analyse uncertainty; test regressions; make evaluation a release gate. **Learning:** [chapters, deck, and practice](08-eval/README.md). **Evidence:** a versioned evaluation report with failure taxonomy, confidence/uncertainty, and a CI or release decision. **Key sources:** [pillar references](08-eval/references.md).

### 09 — LLMs from scratch
**Objectives:** implement automatic differentiation, train a character model, and understand the path from micrograd to a compact GPT. **Learning:** [three chapters, deck, and practice](09-llms-from-scratch/README.md). **Evidence:** a modified training run with hypothesis, metric, result, and explanation. **Key sources:** Karpathy's *nn-zero-to-hero* and [pillar references](09-llms-from-scratch/references.md).

## Completion standard and next steps

Complete a portfolio containing a measured RAG system, a bounded agent design or implementation, an observability/evaluation report, and one end-to-end application. Each must name its task, data boundary, success metric, failure modes, and release or stop decision.

Continue to [AI Engineering](../ai-engineering/README.md) for production engineering discipline, or revisit [Data Science](../data-science/README.md) for modelling depth.
