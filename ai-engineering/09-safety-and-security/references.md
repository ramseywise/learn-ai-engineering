---
origin: curated
sources: []
confidence: medium
cleaned: 2026-10-31
---
# Safety and Security — Papers and Further Reading

> The books and papers behind the notes in [notes/](notes/). PDFs are in [sources/](sources/). Course index: [README](README.md).

---

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| Wilson & Yen, *The Developer's Playbook for Large Language Model Security* (O'Reilly). Not yet in the repo. Wilson leads the OWASP Top 10 for LLM Applications project | whole book: threat model, injection, data leakage, supply chain, trust boundaries | not in repo | 02 · 06 · 07 |
| Huyen, *AI Engineering* (O'Reilly, 2025) | ch. 5 "Defensive prompt engineering"; ch. 10 guardrails | [ch05](../01-prompt-engineering/sources/huyen-ai-engineering/ch05-prompt-engineering.pdf) · [ch10](../06-eval/sources/huyen-ai-engineering/ch10-ai-engineering-architecture-user-feedback.pdf) (held by 01 and 06) | 01 · 04 |

## Frameworks and standards

| Resource | Why read it | Maps to |
|---|---|---|
| [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/) | The shared vocabulary (LLM01–LLM10). New in 2025: system prompt leakage, vector and embedding weaknesses | 02 · 06 |
| [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications/) (Dec 2025) | ASI01–ASI10: goal hijack, tool misuse, memory poisoning, inter-agent trust, rogue agents. Each entry maps back to the LLM list | 02 · 07 |
| [MITRE ATLAS](https://atlas.mitre.org/) | Adversary tactics and case studies for ML systems, in ATT&CK form | 02 |
| NIST, [AI 100-2: Adversarial Machine Learning taxonomy](https://csrc.nist.gov/pubs/ai/100/2/e2025/final) | Government taxonomy of attacks and mitigations, including GenAI. Already parked in the ledger | 02 · 05 |

## Tools and repos

| Resource | Why read it | Maps to |
|---|---|---|
| [NVIDIA garak](https://github.com/NVIDIA/garak) | Open-source LLM vulnerability scanner with probes for injection, leakage and jailbreaks (Apache-2.0) | 05 |
| [Microsoft PyRIT](https://github.com/Azure/PyRIT) | Red-teaming orchestration: targets, converters, scorers, multi-turn attacks | 05 |
| [promptfoo](https://github.com/promptfoo/promptfoo) | Red-teaming plus eval in CI, including RAG and agent attacks. Overlaps with [06/10](../06-eval/notes/10-evals-in-ci.md) | 05 |
| [AgentDojo](https://github.com/ethz-spylab/agentdojo) | Benchmark for injection attacks and defences on tool-using agents | 03 · 05 |
| [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails), [Guardrails AI](https://github.com/guardrails-ai/guardrails) | Programmable input/output rails, the two common open frameworks | 04 |
| Simon Willison, [prompt-injection tag](https://simonwillison.net/tags/prompt-injection/) | The running practitioner record: the dual LLM pattern, the lethal trifecta, new exploits as they land | 01 · 03 |

## Core papers

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| Greshake et al., [Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173) (2023) | Defined indirect injection through retrieved content | not yet downloaded | 01 |
| Beurer-Kellner et al., [Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837) (2025) | Six patterns that trade utility for provable limits on what injected text can do | not yet downloaded | 03 |
| Debenedetti et al., [Defeating Prompt Injections by Design (CaMeL)](https://arxiv.org/abs/2503.18813) (2025) | Separates control flow from data flow so retrieved text can't change the plan. Evaluated on AgentDojo | not yet downloaded | 03 |
| Inan et al., [Llama Guard](https://arxiv.org/abs/2312.06674) (2023) | The reference guard model. Already queued in the ledger under `harness` | not yet downloaded | 04 |

## AI Papers of the Week

Recent papers picked up by the weekly [DAIR](https://github.com/dair-ai/AI-Papers-of-the-Week) sync (`make papers`, then `/papers`).
83 safety papers are parked in the ledger under topic `safety`. Those in scope here include
ShieldGemma, Granite Guardian, *Mitigating LLM Jailbreaks with Few Examples*, *The Art of Refusal*,
*Poisoning Language Models During Instruction Tuning*, *Sleeper Agents*, *Red Teaming Visual
Language Models*, *Auditing Prompt Caching*, *Leaky Thoughts*, *Monitoring Reasoning Models for
Misbehavior*, SHADE-Arena and *Trustworthy LLMs*. Alignment-research papers (*Alignment Faking*,
*Weak-to-Strong Generalization*, anti-scheming) stay parked. They are routed here once `safety` is a
home in `scripts/papers/potw.py`.

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| Tamkin et al., [*Clio: Privacy-Preserving Insights into Real-World AI Use*](https://arxiv.org/abs/2412.13678) (Dec 2024) | Clusters millions of chats behind four privacy layers to find misuse (coordinated spam networks, classifier blind spots); private info falls from ~10% of raw chats to undetectable in cluster summaries. Vendor, self-validated | [clio-2024](sources/clio-2024.pdf) | 09 (planned), 06 (planned) |
| Eloundou et al., [*First-Person Fairness in Chatbots*](https://arxiv.org/abs/2410.19803) (Oct 2024) | Name-swap counterfactuals over real ChatGPT prompts, graded by GPT-4o: harmful gender stereotypes in <0.1% of chats overall, up to >2% on story writing for GPT-3.5; RL cut bias 3–12×. Vendor, same-family grader | [first-person-fairness](sources/first-person-fairness-chatbots-2024.pdf) | 08 (planned) |
| Carlini et al., [*Extracting Training Data from Diffusion Models*](https://arxiv.org/abs/2301.13188) (Jan 2023) | 109 near-copies of training images pulled from Stable Diffusion, mostly ones duplicated ≥100 times; diffusion models leak ~2× more than GANs; dedup helps, DP-SGD failed to train | [carlini-2023](sources/carlini-2023-extracting-training-data-diffusion-models.pdf) | 06 (planned) |
