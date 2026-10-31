# 09 — Safety and Security

> Depth layer. Summary: [7-security-safety](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/7-security-safety/) in the interviewing guides, from [00-start-here](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md).
> Position in the stack: *a cross-cut: every layer has an attack surface*.
> Jump to: [Scope](#scope) · [Planned notes](#planned-notes) · [References](#references)

---

## What it is

Safety and security engineering is keeping an LLM system from being turned against its users
or its owner, and from harming either by accident. The security half has an adversary:
prompt injection, data exfiltration through tool calls, poisoned retrieval, leaked system
prompts, supply-chain attacks on models and MCP servers. The safety half has none: harmful or
biased output, private data surfacing in an answer, an agent taking an irreversible action
it was never meant to take. Both come from the same root. The model can't reliably tell
instructions from data, so a system that mixes untrusted input, private data and the
ability to act outside itself (Willison's "lethal trifecta") will eventually be exploited.

**Inherits the weaknesses of:** every layer at once. A prompt can be overridden
([01](../01-prompt-engineering/README.md)), context can be poisoned
([02](../02-context-engineering/README.md)), a tool can be misused
([03](../03-harness-engineering/README.md)), a loop can amplify one bad step
([04](../04-loop-engineering/README.md)), and one compromised agent can mislead the others in a
graph ([05](../05-graph-engineering/README.md)). This pillar is where those threats are
modelled together and defended by design, not one prompt at a time.

**Why a pillar, not a note.** Added 2026-10-31 (see [CURRICULUM.md](../../CURRICULUM.md#definition-of-done)).
The readings ledger had parked 83 safety papers as a watch topic with no home. The
repo's security material was split across three notes:
[01/10 adversarial prompting](../01-prompt-engineering/notes/10-adversarial-prompting.md),
[03/04 execution boundaries](../03-harness-engineering/notes/04-execution-boundaries.md) and
[generative-ai/05/04 constitutional AI](../../generative-ai/05-RL/notes/04-constitutional-ai.md).
Threat modelling, guardrail models, red-teaming tools, privacy and the OWASP lists had no home.
Those notes stay where they are. This pillar links to them and covers what they leave out.

---

## Scope

| In | Out (lives elsewhere) |
|---|---|
| Threat modelling an LLM app or agent: trust zones, the lethal trifecta, OWASP LLM and Agentic Top 10 | Attack catalogue and prompt-level defences: [01/10](../01-prompt-engineering/notes/10-adversarial-prompting.md) |
| Design patterns that resist injection: dual LLM, plan-then-execute, CaMeL | Sandboxes, hooks, permission gates: [03/04](../03-harness-engineering/notes/04-execution-boundaries.md) |
| Guardrails: input/output filters, moderation APIs, guard models (Llama Guard, ShieldGemma, Granite Guardian) | Alignment training (RLHF, constitutional AI): [generative-ai/05](../../generative-ai/05-RL/README.md) |
| Red-teaming in practice: garak, PyRIT, promptfoo, AgentDojo | Grading safety as an eval metric: [06](../06-eval/README.md) |
| Data security and privacy: PII, training-data extraction, RAG access control, end-user IDs, logging | Alignment research (scheming, alignment faking, interpretability): parked in the ledger, not taught |
| Supply chain: model weights, MCP servers, poisoned datasets | Multimodal model internals: [08](../08-multimodal-engineering/README.md) |
| Harm and fairness in deployed output: bias audits, refusal tuning, know-your-customer limits | Bias in LLM judges: [06/05](../06-eval/notes/05-llm-as-judge.md) |

---

## Planned notes

Notes are written from the sources by `/papers` and `/chapter`. The outline below is the
target; rename or merge as the material dictates.

| # | Note | Main sources |
|---|---|---|
| 01 | Why LLM systems are hard to secure: instructions vs. data, the lethal trifecta | Willison; Greshake et al. 2023 |
| 02 | Threat modelling with the OWASP LLM and Agentic Top 10 and MITRE ATLAS | OWASP GenAI; Wilson & Yen ch. 1–3 |
| 03 | Design patterns that resist prompt injection | Beurer-Kellner et al. 2025; CaMeL |
| 04 | Guardrails: filters, moderation, guard models, and their cost | Llama Guard; ShieldGemma; Granite Guardian; Huyen ch. 10 |
| 05 | Red-teaming: manual, automated, and in CI | garak; PyRIT; promptfoo; AgentDojo; NIST AI 100-2 |
| 06 | Data security and privacy: PII, extraction, RAG access control | Wilson & Yen; OWASP LLM02, LLM08 |
| 07 | Agent and supply-chain security: tools, MCP servers, weights, poisoned data | OWASP Agentic Top 10; *Poisoning LMs During Instruction Tuning*; *Sleeper Agents* |
| 08 | Harm, bias and fairness in deployed output | *Trustworthy LLMs*; *The Art of Refusal* |
| 09 | Monitoring and incident response | *Monitoring Reasoning Models for Misbehavior*; SHADE-Arena |

---

## Layout

```
notes/                       topic notes (see Planned notes)
references.md                papers and books, mapped to notes
sources/<book-slug>/chNN-*.pdf   book chapters
sources/<author-year-slug>.pdf   papers
sources/images/              figures used in notes and slides
slides/                      lecture deck (deck.yaml → .pptx + .pdf)
```

## References

See [references.md](references.md).
