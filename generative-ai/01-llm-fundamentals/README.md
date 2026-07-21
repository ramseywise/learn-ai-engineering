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

- **[`../intro-to-nlp/`](../intro-to-nlp/README.md)** — NLTK, TensorFlow, transformers,
  word-cloud, word2vec. The NLP foundations that predate the transformer era; useful for
  understanding what transformers replaced and improved on.
- **[`../nn-zero-to-hero/`](../nn-zero-to-hero/README.md)** — Karpathy's course: micrograd
  (backprop from scratch), makemore (character-level LMs), nanogpt (GPT-2 from scratch).
  Best hands-on build-it-yourself path to understanding the transformer.

### Interviewing guides

- [2-llm-fundamentals](../../interviewing/guides/2-llm-fundamentals/00-overview.md) —
  compressed summary for interview prep: attention, RLHF, prompting, model behavior.

### Cleaned notes

- [prompt-engineering.md](../../interviewing/notes/prompt-engineering.md) — core techniques:
  system prompts, zero-shot/few-shot, chain-of-thought, structured output, XML structuring,
  prompt templates, prompt chaining, long-context patterns, and the prompt/context boundary.
- [rl.md](../../interviewing/notes/rl.md) — reinforcement learning and RLHF: how models are
  aligned post-pretraining.

### Readings

- [`readings/2-llm-fundamentals/`](../../readings/2-llm-fundamentals/) — prompting and
  generative-AI foundations reference papers.
- [`readings/2-llm-rlhf/`](../../readings/2-llm-rlhf/) — reinforcement learning and RLHF
  reference papers.

### TypeScript

TS examples coming — Google ADK and Vercel AI SDK will be added here as pointer targets
once the repos are linked. The Python fundamentals in this pillar remain canonical.

---

## Next pillar

→ [02-rag-retrieval/](../02-rag-retrieval/README.md) — RAG was the first killer app built
on top of LLMs. Presumes you can prompt a model reliably.
