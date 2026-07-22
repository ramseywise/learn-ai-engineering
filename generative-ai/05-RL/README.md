# 05 — RL & Alignment

> Depth layer. Summary: [interviewing/guides/2-llm-fundamentals](../../interviewing/guides/2-llm-fundamentals/00-overview.md)
> Position: fifth pillar — reinforcement learning and post-training alignment.
> Presumes: [01-llm-fundamentals](../01-llm-fundamentals/README.md).

---

## What it is

Reinforcement learning underpins how modern LLMs are aligned to human preferences
(RLHF, constitutional AI, DPO) and increasingly how agentic systems are trained to
plan and self-correct. This pillar covers RL fundamentals, the RLHF training pipeline,
modern preference-optimization algorithms, and the connection between alignment and
agentic behavior.

---

## Curriculum — RL depth

Six topic areas, ordered from foundations through frontier techniques. Each lists what
exists in this repo, what's missing, and recommended resources to fill gaps.

### 1. RL Foundations

Core RL theory needed before understanding RLHF and alignment.

**Concepts:** Markov decision processes, policies, value functions, exploration vs.
exploitation, temporal-difference learning, Q-learning, policy gradients.

| Status | Resource | Location |
|--------|----------|----------|
| Exists | "Reinforcement Learning" book chapters 1-11 (PDFs) | [`2-llm-rlhf/`](2-llm-rlhf/) — chapters 1 (Why RL) through 11 (Conclusions) |
| Exists | Sutton & Barto textbook (RLbook2020.pdf) | [`2-llm-rlhf/RLbook2020.pdf`](2-llm-rlhf/RLbook2020.pdf) |
| Exists | rl.md — basics (MDP, agent/environment, policy, reward) | [`../01-llm-fundamentals/rl.md`](../01-llm-fundamentals/rl.md) |
| Missing | Cleaned note synthesizing RL foundations for LLM context | Recommend: distill chapters 1-5 into a foundations note focused on what's needed for RLHF |

**Assessment:** Strong reference coverage (full textbook + chapter PDFs). Gap is a
synthesized note that bridges classical RL to the LLM alignment use case.

---

### 2. RLHF — Reinforcement Learning from Human Feedback

The core technique that made ChatGPT possible. Three-stage pipeline:
supervised fine-tuning (SFT) -> reward model training -> RL optimization (PPO).

**Concepts:** Human preference collection, Bradley-Terry model, reward model
architecture, PPO for language models, KL penalty, reward hacking, overoptimization.

| Status | Resource | Location |
|--------|----------|----------|
| Exists | rl.md — RLHF overview (Step 1-3: preferences -> reward model -> PPO) | [`../01-llm-fundamentals/rl.md`](../01-llm-fundamentals/rl.md) (lines 262-266) |
| Exists | InstructGPT / GPT-4 papers | [`2-llm-rlhf/2303.08774v6.pdf`](2-llm-rlhf/2303.08774v6.pdf) (GPT-4), [`2-llm-rlhf/2203.02155v1.pdf`](2-llm-rlhf/2203.02155v1.pdf) |
| Exists | LLM Handbook — preference alignment chapter | [`../01-llm-fundamentals/llm handbook/`](../01-llm-fundamentals/llm%20handbook/) |
| Exists | LLM From Scratch — fine-tuning chapters | [`../01-llm-fundamentals/llm from scratch/`](../01-llm-fundamentals/llm%20from%20scratch/) |
| Missing | Cleaned note: RLHF pipeline walkthrough (SFT -> RM -> PPO) with diagrams | High priority — this is the core alignment technique |
| Missing | Hands-on notebook: RLHF with HuggingFace TRL | Recommend: [HuggingFace TRL docs](https://huggingface.co/docs/trl/), [Anthropic RLHF paper](https://arxiv.org/abs/2204.05862) |

**Assessment:** Papers exist but no structured walkthrough. This is the highest-priority
gap — a cleaned note walking through the three-stage pipeline would anchor the entire pillar.

---

### 3. PPO, DPO, and GRPO — Preference Optimization Algorithms

The algorithm family that implements alignment. PPO was first; DPO simplified the
pipeline; GRPO (DeepSeek) removes the critic network entirely.

**Concepts:**

- **PPO (Proximal Policy Optimization):** Clips policy update ratios for stability.
  The workhorse of RLHF — used by OpenAI, Anthropic, and others.
- **DPO (Direct Preference Optimization):** Eliminates the reward model entirely.
  Trains directly on preference pairs (prompt, chosen, rejected). Simpler, cheaper,
  increasingly standard.
- **GRPO (Group Relative Policy Optimization):** DeepSeek's approach — removes the
  critic, uses group-based advantage estimation. Powers DeepSeek-R1's reasoning.
- **KTO, IPO, ORPO:** Newer variants optimizing different trade-offs (single-signal
  feedback, bounded preferences, odds-ratio weighting).

| Status | Resource | Location |
|--------|----------|----------|
| Exists | rl.md — DPO section (no reward model, direct preference training) | [`../01-llm-fundamentals/rl.md`](../01-llm-fundamentals/rl.md) (lines 271-286) |
| Exists | rl.md — PPO overview (actor-critic, clipped ratios) | [`../01-llm-fundamentals/rl.md`](../01-llm-fundamentals/rl.md) (lines 122-124, 154) |
| Exists | PPO reference links (DigitalOcean, Toloka, MathWorks) | [`../01-llm-fundamentals/rl.md`](../01-llm-fundamentals/rl.md) |
| Exists | DPO paper (2305.18290v3.pdf) | [`2-llm-rlhf/2305.18290v3.pdf`](2-llm-rlhf/2305.18290v3.pdf) |
| Missing | GRPO — no coverage at all | Recommend: [DeepSeek-R1 paper](https://arxiv.org/abs/2501.12948), [GRPO explainer](https://arxiv.org/abs/2402.03300) |
| Missing | Cleaned note: PPO vs DPO vs GRPO comparison (when to use which) | High priority — practitioners need this decision framework |
| Missing | Algorithm evolution timeline (PPO -> DPO -> GRPO -> KTO/IPO/ORPO) | Would clarify the field's trajectory |

**Assessment:** DPO paper exists; PPO is covered in rl.md. GRPO is a complete gap.
A comparison note showing the algorithm evolution would be the most valuable addition.

---

### 4. Reward Modeling

The component that converts human preferences into a trainable signal. Central to
RLHF; bypassed by DPO but understanding it is essential for the full picture.

**Concepts:** Preference datasets, Bradley-Terry model, reward model architecture
(typically a modified LLM with a scalar head), reward hacking, overoptimization,
process vs. outcome reward models.

| Status | Resource | Location |
|--------|----------|----------|
| Exists | rl.md — reward function mentions (brief) | [`../01-llm-fundamentals/rl.md`](../01-llm-fundamentals/rl.md) |
| Exists | Reward hacking blog reference | [`../01-llm-fundamentals/rl.md`](../01-llm-fundamentals/rl.md) (line 51) |
| Exists | InstructGPT paper (describes reward model training) | [`2-llm-rlhf/`](2-llm-rlhf/) |
| Missing | Cleaned note: reward model architecture and training | Recommend: [Anthropic reward modeling](https://arxiv.org/abs/2204.05862), [OpenAI process reward models](https://openai.com/index/improving-mathematical-reasoning-with-process-reward-models/) |
| Missing | Process reward models vs outcome reward models | Key frontier topic — PRM drives chain-of-thought verification |

**Assessment:** Minimal coverage. Reward modeling is implicit in the RLHF papers but
never surfaced as its own topic. Understanding reward hacking, overoptimization, and
process vs. outcome reward models is critical for interview depth.

---

### 5. Constitutional AI / RLAIF

Anthropic's approach: replace human preference labeling with AI-generated feedback
guided by a constitution (a set of principles). Scales alignment without proportional
human labor.

**Concepts:** Constitutional principles, AI-generated critiques and revisions, RLAIF
(RL from AI Feedback), self-improvement loops, harmlessness training, red-teaming.

| Status | Resource | Location |
|--------|----------|----------|
| Exists | Constitutional AI paper | [`2-llm-rlhf/constitutional_ai.pdf`](2-llm-rlhf/constitutional_ai.pdf) |
| Exists | Constitutional AI paper (duplicate) | [`../01-llm-fundamentals/readings/constitutional_ai.pdf`](../01-llm-fundamentals/readings/constitutional_ai.pdf) |
| Exists | rl.md — brief mention | [`../01-llm-fundamentals/rl.md`](../01-llm-fundamentals/rl.md) |
| Missing | Cleaned note: constitutional AI pipeline (critique -> revision -> RLAIF) | Recommend: [Anthropic constitutional AI paper](https://arxiv.org/abs/2212.08073), [RLAIF paper](https://arxiv.org/abs/2309.00267) |
| Missing | Connection to safety/red-teaming literature | Would bridge to responsible AI topics |

**Assessment:** The paper exists in two locations (should deduplicate — canonical copy
should live here in `2-llm-rlhf/`, with a pointer from 01-llm-fundamentals). No
structured note explaining the technique or connecting it to the broader alignment story.

---

### 6. RL for Agentic Systems

RL applied to agent planning, tool use, and retrieval — where alignment meets agency.
Increasingly relevant as agents move from prompt-engineered to RL-trained.

**Concepts:** RL for tool use, RL for retrieval (Self-RAG, adaptive retrieval), MARL
(multi-agent RL), RL for reasoning (DeepSeek-R1, OpenAI o1), verifiable rewards.

| Status | Resource | Location |
|--------|----------|----------|
| Exists | rl.md — MARL section (CTDE, MADDPG, credit assignment) | [`../01-llm-fundamentals/rl.md`](../01-llm-fundamentals/rl.md) (lines 55-196) |
| Exists | rl.md — RL in RAG section (query rewriting, retrieval policy, tool use) | [`../01-llm-fundamentals/rl.md`](../01-llm-fundamentals/rl.md) (lines 197-259) |
| Exists | ReAct paper | [`2-llm-rlhf/reAct_syergizing_reasoning_ancd_acting_in_language_models.pdf`](2-llm-rlhf/reAct_syergizing_reasoning_ancd_acting_in_language_models.pdf) |
| Exists | Reflexion paper (language agents with RL) | [`2-llm-rlhf/reflexioin_language_agents_with_reinforcement_learning.pdf`](2-llm-rlhf/reflexioin_language_agents_with_reinforcement_learning.pdf) |
| Exists | Deep-research-bot RL notebook | [`../07-agentic-applications/chatbot/deep-research-bot/notebooks/03_rl_for_deep_research_agent.ipynb`](../07-agentic-applications/chatbot/deep-research-bot/notebooks/03_rl_for_deep_research_agent.ipynb) |
| Exists | WebGPT reference (RL for web browsing) | [`../01-llm-fundamentals/rl.md`](../01-llm-fundamentals/rl.md) (line 239) |
| Missing | RL for reasoning (DeepSeek-R1, OpenAI o1) — no coverage | Recommend: [DeepSeek-R1 paper](https://arxiv.org/abs/2501.12948) — this is the biggest recent development |
| Missing | Verifiable rewards for reasoning tasks | Key innovation: math/code tasks provide automatic reward signals |

**Assessment:** Best-covered area after foundations. The MARL and RL-in-RAG notes in
rl.md are rough (mixed zh/en Notion export) but contain real substance. The deep-research-bot
notebook is a hands-on application. Main gap is RL-for-reasoning (DeepSeek-R1, o1).

---

## Existing resource quality assessment

### `rl.md` (in 01-llm-fundamentals)

- **Status:** Low-confidence Notion export, mixed Chinese/English, many bare URLs
- **Strengths:** Covers MARL, RL-in-RAG, DPO/ILQL, reward hacking — real depth
- **Recommendation:** Split into topic-specific cleaned notes and migrate to this pillar.
  Keep a pointer in 01-llm-fundamentals for the pretraining->alignment pipeline story.
  Topics to extract: (1) RLHF pipeline, (2) PPO/DPO/GRPO comparison, (3) RL for RAG/agents

### `2-llm-rlhf/` readings

- **Status:** 39 PDFs, mix of RL textbook chapters and research papers
- **Strengths:** Comprehensive RL textbook (chapters 1-11), Sutton & Barto, key papers
- **Issues:** Some papers are duplicated across pillars (constitutional_ai.pdf). Several
  papers are not RL-specific (conversational-ai.pdf, rasa papers, batch-norm) — these may
  be misfiled from a Notion dump.
- **Recommendation:** Audit and reorganize. Move non-RL papers to appropriate pillars.
  Create a readings index mapping each paper to the curriculum topic it supports.

---

## Priority roadmap

Ordered by impact for interview depth and conceptual completeness:

1. **RLHF pipeline walkthrough** (Topic 2) — the single most important gap. A cleaned
   note walking SFT -> reward model -> PPO, with the "why" at each stage.
2. **PPO vs DPO vs GRPO comparison** (Topic 3) — practitioners need to know which
   algorithm to use when. Include GRPO and the DeepSeek-R1 story.
3. **rl.md cleanup and split** — extract the three topic notes from the Notion export.
   Translate Chinese sections. Remove bare URLs, add context.
4. **Constitutional AI / RLAIF note** (Topic 5) — the paper exists; a 1-page summary
   connecting it to RLHF and safety would close the gap.
5. **Reward modeling depth** (Topic 4) — process vs. outcome reward models, reward
   hacking patterns.
6. **RL for reasoning** (Topic 6) — DeepSeek-R1 and verifiable rewards. Newest and
   fastest-moving area.
7. **Readings audit** — deduplicate, move misfiled papers, create index.

---

## Cross-links

| Direction | Pillar | Connection |
|-----------|--------|------------|
| Upstream | [01-llm-fundamentals](../01-llm-fundamentals/README.md) | RL/RLHF is the post-pretraining alignment step. `rl.md` lives there as part of the training pipeline story. |
| Upstream | Fine-tuning (in `01-llm-fundamentals/llm from scratch/`, `llm handbook/`) | SFT is stage 1 of the RLHF pipeline. Preference alignment (DPO) is an alternative to stage 2+3. |
| Downstream | [03-agentic-foundations](../03-agentic-foundations/README.md) | RL-trained agents (ReAct, Reflexion, tool-use RL). MARL for multi-agent coordination. |
| Downstream | [07-agentic-applications](../07-agentic-applications/README.md) | Deep-research-bot has an RL notebook (`03_rl_for_deep_research_agent.ipynb`). |
| Lateral | [ai-engineering/06-eval](../../ai-engineering/06-eval/README.md) | Evaluation methodology for RL-trained agents: trajectory scoring, preference annotation, benchmarks. |
| Lateral | [interviewing/guides/2-llm-fundamentals](../../interviewing/guides/2-llm-fundamentals/00-overview.md) | Summary layer — RLHF, alignment, and prompting compressed for interview prep. |

---

## Next pillar

-> [06-observability/](../06-observability/README.md) — once agents are trained and deployed,
observability tooling (tracing, scoring, evaluation pipelines) closes the feedback loop.
