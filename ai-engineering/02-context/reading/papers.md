---
origin: curated
sources:
  - https://github.com/davidkimai/Context-Engineering (README, CITATIONS_v3.md — snapshot 2026-08-14)
confidence: high
cleaned: 2026-10-28
---
# Context Engineering — Papers and Further Reading

> Curated from the vendored `davidkimai/Context-Engineering` repo before it was removed. The kept course chapters and references are indexed in the [README](../README.md#course-material--context-engineering-davidkimai-snapshot-2026-08-14).

---

## Core papers

| Paper | Why read it | Maps to |
|---|---|---|
| Mei et al. — [A Survey of Context Engineering for LLMs](https://arxiv.org/abs/2507.13334) (Jul 2025) | 1,400-paper taxonomy: retrieval/generation → processing → management → systems (RAG, memory, tools, multi-agent). Source of the "context is the complete information payload" definition. | [context-engineering.md](../context-engineering.md) |
| Chroma — [Context Rot](https://research.trychroma.com/context-rot) (2025) | Empirical: performance degrades with input length even on simple tasks, well before the window limit. | [notes/01](../notes/01-why-context-is-finite.md) |
| Brown, Bartezzaghi & Rigotti (IBM Zurich) — [Eliciting Reasoning in LMs with Cognitive Tools](https://arxiv.org/abs/2506.12115) (Jun 2025) | Modular "cognitive tool" prompts (understand, recall, examine, backtrack) lift GPT-4.1 on AIME2024 from 26.7% → 43.3%. | [foundations/05](../notes/foundations/05_cognitive_tools.md) · [cognitive-tools](../cognitive-tools/README.md) |
| Zhou et al. (Singapore-MIT) — [MEM1: Synergizing Memory and Reasoning for Long-Horizon Agents](https://arxiv.org/abs/2506.15841) (Jun 2025) | RL-trained agents that consolidate memory into a constant-size internal state instead of appending history. | [notes/04](../notes/04-compression-compaction.md) · [notes/05](../notes/05-memory-as-context.md) |
| [MemOS](https://github.com/MemTensor/MemOS) (MemTensor, 2025) | Memory as an OS-managed resource — scheduling, lifecycle, and access control for agent memory. | [notes/05](../notes/05-memory-as-context.md) |
| Yang et al. (Princeton) — [Emergent Symbolic Mechanisms Support Abstract Reasoning in LLMs](https://openreview.net/forum?id=y1SnRPDWx4) (ICML 2025) | Mechanistic evidence for a three-stage abstraction → induction → retrieval circuit. Background on *why* structured context helps. | [notes/02](../notes/02-context-anatomy.md) |

## Talks and collections

- Andrej Karpathy — [Software Is Changing (Again)](https://www.youtube.com/watch?v=LCEmiRjPEtQ), YC AI Startup School 2025. Origin of *"the delicate art and science of filling the context window with just the right information for the next step."*
- [Awesome-Context-Engineering](https://github.com/Meirtz/Awesome-Context-Engineering) — maintained paper list that accompanies the survey.
- [NotebookLM notebook + podcast deep dive](https://notebooklm.google.com/notebook/0c6e4dc6-9c30-4f53-8e1a-05cc9ff3bc7e) — audio overviews of the repo (the vendored mp4s were removed).

## Deliberately not kept

The upstream repo also builds a "neural field / attractor / quantum semantics" framework on [Quantum Semantic Framework](https://arxiv.org/abs/2506.10077) and [Attractor Cycles in LLMs](https://arxiv.org/abs/2502.15208). Most of that track was dropped (`60_protocols/`, `context-schemas/`, the field-theory references and templates); foundations 08–14 and `00_COURSE/08_field_theory_integration` were kept. Retrieve the rest from upstream if needed:

- Repo: https://github.com/davidkimai/Context-Engineering (snapshot 2026-08-14)
