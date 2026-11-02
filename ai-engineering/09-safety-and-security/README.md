# 09 — Safety and Security

> Depth layer. Summary: [7-security-safety](../../practice/interviewing/guides/7-security-safety) in the interviewing guides, from [00-start-here](../../practice/interviewing/guides/00-start-here.md).
> Position in the stack: *a cross-cut: every layer has an attack surface*.
> Jump to: [Scope](#scope) · [The story](#the-story) · [Reading order](#reading-order) · [Rules of thumb](#rules-of-thumb) · [Deck and practice](#deck-and-practice) · [References](#references)

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

**Why a pillar, not a note.** Added 2026-10-31 (see the [structure decisions](../../.claude/skills/pillar/references/pillar-layout.md#structure-decisions)).
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
| Red-teaming in practice: garak, PyRIT, promptfoo, AgentDojo | Grading safety as an eval metric: [the Eval pillar in generative-ai](../../generative-ai/08-eval/README.md) |
| Data security and privacy: PII, training-data extraction, RAG access control, end-user IDs, logging | Alignment research (scheming, alignment faking, interpretability): parked in the ledger, not taught |
| Supply chain: model weights, MCP servers, poisoned datasets | Multimodal model internals: [08](../08-multimodal-engineering/README.md) |
| Harm and fairness in deployed output: bias audits, refusal tuning, know-your-customer limits | Bias in LLM judges: [Eval, LLM as judge](../../generative-ai/08-eval/notes/05-llm-as-judge.md) |

---

## The story

Harbour is a support agent for an online shop. It reads help articles, looks up orders, files tickets, sends email, issues refunds and can run small scripts. We start by drawing its trust boundaries and finding the dangerous combination, then watch that combination get exploited by text the model merely read, and learn why no filter fully closes the hole. So we add guard models, knowing what they cost in false refusals, and then put the hard limits outside the model, in a policy engine and a sandbox that hold whatever the model decides. We test all of it with tools that make attacks cheap to repeat, and each finding becomes a permanent test. Then, because something will still get through, we prepare to notice it, switch off one capability, find everyone affected, and turn the failure into the next test.

## Reading order

| # | Chapter | Question it answers |
|---|---|---|
| 1 | [Threat model](notes/01-threat-model.md) | What can go wrong, by which path, and which paths matter first? Includes privacy, data security and supply chain |
| 2 | [Prompt injection and jailbreaks](notes/02-prompt-injection-and-jailbreaks.md) | Why can't the model tell instructions from data, and which designs limit the damage? |
| 3 | [Guardrail models](notes/03-guardrail-models.md) | What do filters and guard models catch, and what do they cost? Includes harm, refusal and fairness |
| 4 | [Tool and execution sandboxing](notes/04-tool-and-execution-sandboxing.md) | How do you enforce limits that don't depend on the model behaving? |
| 5 | [Red-teaming tools](notes/05-red-teaming-tools.md) | How do you find failures, and how much does a clean run prove? |
| 6 | [Incident response](notes/06-incident-response.md) | What do you do when one gets through? |

Read in order. Each chapter assumes the Harbour system and the paths from chapter 1. If you need only the practical minimum, read chapters 1 and 4.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [DA 02/02 Probability foundations](../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md) | Base rates and false alarms |
| [DA 03/02 Metrics and KPI design](../../data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design.md) | Guardrail metrics, a different sense of the word |
| [DS 01/04 Model evaluation](../../data-science/01-classical-ml/notes/04-model-evaluation.md) | The guard's confusion matrix |
| [GA 05/04 Constitutional AI](../../generative-ai/05-RL/notes/04-constitutional-ai.md) | Alignment training |
| [GA 08/05 LLM as judge](../../generative-ai/08-eval/notes/05-llm-as-judge.md) | Judges in safety evals |

**Feeds into**

| Chapter | Why |
|---|---|
| None in other subjects | AI engineering is the last subject in the path |

## Rules of thumb

- **Any input the model reads is an instruction to it.** Retrieved documents, tool results and emails all count.
- **Break the trifecta first.** Private data, untrusted content and a way out: remove one leg from any path that has all three.
- **Put hard limits outside the model.** A prompt asks, and a policy engine enforces.
- **Guards reduce risk, and they don't remove it.** Measure false refusals beside catch rate, since a guard that blocks everything scores perfectly on safety.
- **A clean run is weak evidence.** Zero successes in twenty tries still allows a true rate around 16%. Report the bound.
- **A passing security test needs proof it exercised the control.** Harm in the baseline, a recorded denial in the guarded run, otherwise inconclusive.
- **Test the application, not the bare model.** The serious paths run through your tools and data.
- **Build narrow switches before you need them.** Per-tool kill, read-only mode, source quarantine and rollback, each one drilled.
- **Deleting the seed isn't eradication.** Memories, caches, indexes and agent-written skills keep what they absorbed.
- **Every incident leaves a regression case, a threat-model update and a detection rule.**

## Deck and practice

The lecture deck is [slides/safety-and-security.pptx](slides/safety-and-security.pptx), with a [PDF](slides/safety-and-security.pdf). Its spec is [slides/deck.yaml](slides/deck.yaml). Rebuild it with `make slides PILLAR=ai-engineering/09-safety-and-security`.

This pillar has no practice folder yet. Each chapter has runnable code on synthetic data and a Try it section. To run a block, copy it to a file and use `uv run python file.py`; apart from the commands marked `# illustrative`, which need credentials, the blocks use only the standard library or numpy (add `--with numpy`).

---

## Layout

```
notes/                       chapters (see Reading order)
references.md                papers and books, mapped to notes
sources/<book-slug>/chNN-*.pdf   book chapters
sources/<author-year-slug>.pdf   papers
sources/images/              figures used in notes and slides
slides/                      lecture deck (deck.yaml → .pptx + .pdf)
```

## Primary texts

- Huyen, *AI Engineering*, ch. 10
- Wilson and Yen, *The Developer's Playbook for Large Language Model Security*: recommended; not in the repo, and the notes do not rely on it
- Debenedetti et al., *Defeating Prompt Injections by Design*

Everything else: [references.md](references.md).

## References

See [references.md](references.md).
