# 01 — LLM Fundamentals

> Depth layer. Summary: [interviewing/guides/2-llm-fundamentals](../../interviewing/guides/2-llm-fundamentals/00-overview.md)
> Position: first pillar — what LLMs are, how they're trained, how to prompt them.
> Everything in generative AI builds on this foundation.

---

## What it is

LLM fundamentals covers the architecture, training, and prompting of large language models.
This is the conceptual bedrock: before building RAG systems or agents, you need to understand
what the model is doing, why it behaves as it does, and how to instruct it reliably.

---

## Resource map

### Course material (hands-on)

- **[`langchain/`](langchain/)** — Learning LangChain book chapters (PDFs): LLM fundamentals,
  RAG, memory, agent architecture, deployment. Cross-pillar reference; the RAG and agent
  chapters overlap with 02 and 03.
- **[`llm from scratch/`](<llm from scratch/>)** — "Build a Large Language Model (From Scratch)"
  chapters (PDFs): attention mechanisms, GPT implementation, pretraining, fine-tuning for
  classification and instruction following.
- **[`llm handbook/`](<llm handbook/>)** — "LLM Engineer's Handbook" chapters (PDFs):
  LLM Twin concept, data engineering, RAG pipelines, supervised fine-tuning, preference
  alignment, evaluation, inference optimization, deployment.

### Readings

- **[`readings/`](readings/)** — prompting, RLHF, and generative-AI foundations reference
  papers and book chapters (PDFs). Includes constitutional AI, chain-of-thought, and
  prompt engineering for generative AI.

### Interviewing guides

- [2-llm-fundamentals](../../interviewing/guides/2-llm-fundamentals/00-overview.md) —
  compressed summary for interview prep: attention, RLHF, prompting, model behavior.

### Cleaned notes

- [rl.md](rl.md) — reinforcement learning and RLHF: how models are aligned post-pretraining.
- [prompt-engineering.md](../../ai-engineering/01-prompt/prompt-engineering.md) — core techniques:
  system prompts, zero-shot/few-shot, chain-of-thought, structured output, XML structuring,
  prompt templates, prompt chaining, long-context patterns, and the prompt/context boundary.

---

## Next pillar

→ [02-rag-retrieval/](../02-rag-retrieval/README.md) — RAG was the first killer app built
on top of LLMs. Presumes you can prompt a model reliably.
