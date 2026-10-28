---
origin: curated
sources:
  - https://github.com/davidkimai/Context-Engineering (README, CITATIONS_v3.md — snapshot 2026-08-14)
confidence: high
cleaned: 2026-10-28
---
# Context Engineering — Papers and Further Reading

> The papers behind the chapters in [notes/](notes/). PDFs of the arXiv papers are in [sources/](sources/). Course index: [README](README.md).

---

## Core papers

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| ★ Mei et al., [*A Survey of Context Engineering for LLMs*](https://arxiv.org/abs/2507.13334) (Jul 2025) | A 1,400-paper taxonomy: retrieval/generation → processing → management → systems (RAG, memory, tools, multi-agent). The source of the `C = A(c₁…cₙ)` formalism | [2507.13334](sources/mei-2025-context-engineering-survey.pdf) | [context-engineering.md](context-engineering.md) · [02](notes/02-context-anatomy.md#the-formal-view) · [03](notes/03-budgeting-the-window.md) |
| ★ Chroma, [*Context Rot*](https://research.trychroma.com/context-rot) (2025) | Empirical: performance degrades with input length even on simple tasks, well before the window limit | web only | [01](notes/01-why-context-is-finite.md) · [12](notes/12-evaluating-context.md#long-context-behaviour) |
| Ebouky, Bartezzaghi & Rigotti (IBM Research Zurich), [*Eliciting Reasoning in LMs with Cognitive Tools*](https://arxiv.org/abs/2506.12115) (Jun 2025) | Modular cognitive-tool prompts (understand, recall, examine, backtrack) lift GPT-4.1 on AIME 2024 from 26.7% to 43.3% | [2506.12115](sources/ebouky-2025-cognitive-tools.pdf) | [08](notes/08-cognitive-tools.md) |
| Zhou et al. (Singapore-MIT), [*MEM1: Synergizing Memory and Reasoning for Long-Horizon Agents*](https://arxiv.org/abs/2506.15841) (Jun 2025) | RL-trained agents that consolidate memory into a constant-size internal state instead of appending history | [2506.15841](sources/zhou-2025-mem1.pdf) | [06](notes/06-memory.md#mem1-constant-size-memory) · [07](notes/07-structured-context.md) |
| [MemOS](https://github.com/MemTensor/MemOS) (MemTensor, 2025) | Memory as an OS-managed resource: scheduling, lifecycle and access control for agent memory | repo | [06](notes/06-memory.md#memos-style-management) |
| Yang et al. (Princeton), [*Emergent Symbolic Mechanisms Support Abstract Reasoning in LLMs*](https://arxiv.org/abs/2502.20332) (ICML 2025) | Mechanistic evidence for a three-stage abstraction → induction → retrieval circuit. Background on *why* structured context helps | [2502.20332](sources/yang-2025-emergent-symbolic-mechanisms.pdf) | [07](notes/07-structured-context.md#why-structure-helps) · [99](notes/99-speculative-field-track.md) |

## Speculative-track papers

The upstream "neural field / attractor / quantum semantics" framework cites these. The claims built on top of them are summarised, with caveats, in [99](notes/99-speculative-field-track.md).

| Paper | PDF |
|---|---|
| Wang et al., [*Unveiling Attractor Cycles in LLMs: A Dynamical Systems View of Successive Paraphrasing*](https://arxiv.org/abs/2502.15208) (2025) | [2502.15208](sources/wang-2025-attractor-cycles.pdf) |
| Agostino et al., [*A Quantum Semantic Framework for Natural Language Processing*](https://arxiv.org/abs/2506.10077) (2025) | [2506.10077](sources/agostino-2025-quantum-semantic-framework.pdf) |

## Talks and collections

- Andrej Karpathy, [*Software Is Changing (Again)*](https://www.youtube.com/watch?v=LCEmiRjPEtQ), YC AI Startup School 2025. The origin of *"the delicate art and science of filling the context window with just the right information for the next step."*
- [Awesome-Context-Engineering](https://github.com/Meirtz/Awesome-Context-Engineering): the maintained paper list that accompanies the survey.
- [NotebookLM notebook and podcast deep dive](https://notebooklm.google.com/notebook/0c6e4dc6-9c30-4f53-8e1a-05cc9ff3bc7e): audio overviews of the upstream repo.

## About the upstream course

The vendored `davidkimai/Context-Engineering` repo (snapshot 2026-08-14, about 600k words) was synthesized into chapters 03, 07, 08, 09, 12, 13 and 99, and into additions to 01, 02, 04, 05, 06 and 10. The raw files were then deleted on 2026-10-28. Each chapter's frontmatter `sources:` names the upstream files it draws on.

What was kept as files:

- [templates/](templates/): schema templates, prompt programs, control loops and prompt templates.
- [notebooks/](notebooks/): the `10_guides_zero_to_hero` Python labs.

To read the originals, use the upstream repo: https://github.com/davidkimai/Context-Engineering. The deleted files are also in this repo's git history: `git show a51061f:ai-engineering/02-context/<path>`.
