# LLM Fundamentals — Study Guide

The breadth/theory round now front-loads transformer-era questions. Target: explain each
concept in 60 seconds with one level of depth in reserve (the follow-up is where the
signal is).

## 1. Architecture core

- **Tokenization** — BPE/SentencePiece subwords; why token ≠ word matters (cost, truncation,
  multilingual inflation, arithmetic weirdness). `nn-zero-to-hero/nanogpt` builds this from
  scratch — cite hands-on experience.
- **Attention** — `softmax(QKᵀ/√d)V`; self-attention = every token attends to every other
  (O(n²) — the reason long context is expensive and why "context rot" exists). Multi-head =
  parallel subspace views. Positional info via embeddings (learned, RoPE, ALiBi — ALiBi
  paper is in `readings/`).
- **Transformer block** — attention + MLP + residuals + layer norm; decoder-only for GPT-family
  (causal mask), encoder-only for BERT (bidirectional, classification/embedding), encoder-
  decoder for translation-style tasks. Papers: attention-is-all-you-need, BERT — both in
  `readings/general/`.
- **KV cache** — decode-time cache of past keys/values; the mechanism under prompt caching
  (see [context-engineering-cost guide](../5-context-cost/interview-guide.md) §3).
- **Sampling** — temperature, top-p/top-k, why temperature 0 still isn't fully deterministic
  in production (batching, floating point, MoE routing).

## 2. Training pipeline (tell it as a story)

1. **Pretraining** — next-token prediction at scale; scaling laws (params/data/compute
   trade-off — LLaMA's "train smaller longer" insight).
2. **SFT** — instruction-following on curated demonstrations.
3. **Preference alignment**:
   - **RLHF** — reward model from human preference pairs + PPO against it. Know the failure
     mode by name: **reward hacking**; and PPO's role: clipped policy updates for stability.
   - **DPO** — skips the reward model, optimizes preference pairs directly; more stable,
     cheaper, the common industry default now.
   - **Constitutional AI / RLAIF** — AI feedback guided by principles instead of (or before)
     human labels; critique-and-revise loop (paper in `readings/`).
4. **RL fundamentals behind it** (from the notes): MDP framing — agent/environment/state/
   action/reward/policy; exploration vs exploitation; value-based (DQN) vs policy-gradient
   (PPO) vs actor-critic. **MARL** exists (CTDE, QMIX, MADDPG) but say honestly: it's for
   multi-agent planning research, not something production LLM stacks train with.

## 3. Adaptation menu (the "RAG vs fine-tuning" ladder)

Prompting → few-shot → RAG → **PEFT/LoRA** (low-rank adapters; QLoRA = quantized base) →
full fine-tune. Decision axes: knowledge freshness (RAG), behavior/format/style (fine-tune),
data volume, budget, provenance requirements. They compose — a fine-tuned model inside a RAG
system is common. API-only models: no DPO/weights access — preference data goes into
prompts/evals instead.

## 4. Inference economics

Prefill (prompt, parallel, cheap/token) vs decode (output, sequential, expensive/token) —
why output-length discipline and streaming matter; quantization (8/4-bit) trades quality for
memory/latency; distillation for the 80% of traffic a small model can serve; speculative
decoding as a latency trick. Serving metrics: TTFT, tokens/sec, p95.

## 5. Failure modes (know mechanisms, not vibes)

- **Hallucination** — the objective rewards plausible continuation, not truth; models mimic
  human falsehoods in training data (TruthfulQA). Mitigations: grounding/RAG + citation
  checks, calibration, abstention ("I don't know" paths), verification loops.
- **Context limitations** — attention dilution in long contexts ("lost in the middle");
  mitigation = context engineering, not bigger windows.
- **Sycophancy, position bias, verbosity bias** — matter both for products and for
  LLM-as-judge design (see [evals guide](../6-evals-observability/interview-guide.md)).
- **Knowledge cutoff + drift** — why production systems pin model versions and re-eval on
  upgrades.

## 6. Question bank (answer sketches)

- *"Explain attention to a PM."* — weighted lookup: each word asks "which other words matter
  for my meaning here?" and blends them; the weights are learned.
- *"Why did RLHF-era models get so much better?"* — pretraining gives capability; alignment
  makes it *usable* — the gap between knowing and doing what's asked.
- *"LoRA vs full fine-tune?"* — LoRA: freeze weights, train low-rank deltas (~0.1–1% params);
  cheaper, swappable per-tenant adapters, less catastrophic forgetting; full FT for deep
  behavior shifts with big data.
- *"Why does the model hallucinate a citation?"* — citations are high-probability *patterns*;
  nothing in decoding checks existence — hence retrieval + grounding verification at the
  system level.
- *"DPO vs RLHF?"* — same preference data, no reward model or RL loop; directly raises the
  likelihood gap between chosen and rejected; trades some controllability for stability.

## Sources

- notes: [rl.md](../../notes/rl.md) (RL/RLHF/MARL — confidence: low, verify claims), [agents-self-training.md](../../notes/agents-self-training.md) (Agent-Lightning, training-agent disaggregation)
- readings: `general/` (attention, BERT, LLaMA, GPT-4, InstructGPT, Constitutional AI, CoT, ReAct, ToT, TruthfulQA), `2-llm-rlhf/` (DQN, PPO, RLHF preferences), `2-llm-fundamentals/` chapters
- repo: `generative-ai/nn-zero-to-hero/` (nanogpt from scratch), `generative-ai/intro-to-nlp/`
- librarian wiki: Direct Preference Optimization · Chain of Thought · Self-Learning Agents
