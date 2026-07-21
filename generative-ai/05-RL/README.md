# 05 — RL & Alignment

> Depth layer. Summary: [interviewing/guides/2-llm-fundamentals](../../interviewing/guides/2-llm-fundamentals/00-overview.md)
> Position: fifth pillar — reinforcement learning and post-training alignment.
> Presumes: [01-llm-fundamentals](../01-llm-fundamentals/README.md).

---

## What it is

Reinforcement learning underpins how modern LLMs are aligned to human preferences
(RLHF, constitutional AI, DPO) and increasingly how agentic systems are trained to
plan and self-correct. This is a large field with deep theoretical roots; the material
here spans RL fundamentals through post-training alignment techniques.

This pillar is currently reference-heavy — course chapters and papers — with active
learning captured in the notes linked below.

---

## Resource map

### Course material (hands-on)

- **[`2-llm-rlhf/`](2-llm-rlhf/)** — "Reinforcement Learning" book chapters (PDFs):
  Markov decision processes, dynamic programming, Monte Carlo methods, temporal-difference
  learning, Q-learning, deep Q-networks, policy gradient methods, entropy methods, and
  practical RL. Also includes RLHF, constitutional AI, and agentic-RL reference papers.

### Cleaned notes

- [rl.md](../01-llm-fundamentals/rl.md) — RL and RLHF as applied to LLMs:
  reward modeling, PPO fine-tuning, constitutional AI, preference alignment.
  Lives in 01-llm-fundamentals because RL is part of the pretraining→alignment pipeline.

---

## Cross-links

- [01-llm-fundamentals/](../01-llm-fundamentals/README.md) — the RL notes (`rl.md`) live
  here as part of the training pipeline story.
- [ai-engineering/06-eval/](../../ai-engineering/06-eval/README.md) — evaluation
  methodology for RL-trained agents: trajectory scoring, preference annotation, benchmarks.

---

## Next pillar

→ [06-observability/](../06-observability/README.md) — once agents are trained and deployed,
observability tooling (tracing, scoring, evaluation pipelines) closes the feedback loop.
