# System Design Round (ML/LLM/agent)

## What's tested
The highest-weight technical round in 2026 AIE/MLE loops (research F4): structured
ambiguity handling — clarify → requirements → design → shortcomings → iterate — with
trade-off narration as the actual graded skill. Interviewers score the *process*
(strategic questions, adapting to curveballs, growth mindset) as much as the design.

## Format & trends
45–60 min whiteboard/virtual-whiteboard. The prompt is deliberately vague ("design a
support chatbot"). 2026 versions are LLM-flavored by default: RAG pipelines, agent
systems, eval/monitoring, cost/latency budgets. Curveballs mid-round are deliberate
adaptability tests; the best interviews meander through options before converging.

**The method lives in the [system-design study guide](../guides/system-design.md)** —
process (§1), trade-off narration formula (§2), reference architecture (§3),
bottleneck/failure tables (§4), the measurement close (§5). This file is round-day
logistics only.

## Prep checklist
- [ ] Rehearse the §1 five-step process until the clarifying questions are automatic
  (the two openers: priorities question + data-sensitivity question).
- [ ] Draw the §3 reference architecture from memory in under 3 minutes.
- [ ] Dry-run the four classic prompts in §6 against a timer (8 min/step).
- [ ] Rehearse the three librarian drill systems as full spoken answers — designs you've
  actually built beat memorized generic ones.
- [ ] Prepare the closing move: success metrics with numbers + a future-improvements list.
- [ ] Practice the recovery move: interviewer challenges a trade-off → adapt visibly,
  don't defend.

## Question bank
See [system-design guide](../guides/system-design.md) §7. Round-day variants:
- "Design X for 1K users. … Now 1M." — the scale curveball; separate what changes
  (caching, sharding, async) from what doesn't.
- "You have half the budget." — degrade deliberately: smaller model tiers, caching,
  batch instead of realtime; state what quality you're trading.
- "What breaks first?" — pick from the bottleneck table and name the mitigation.
- "How do you know it works?" — evals + monitoring, stated unprompted
  ([evals guide](../guides/evals-observability.md)).

## Per-role weighting
| AIE | MLE | DS | FDE |
|---|---|---|---|
| ● | ● | ◐ | ● |

Highest-weight round for AIE/MLE. For FDE the [case study](case-study.md) and
[customer simulation](customer-simulation.md) outweigh it (research F4) — but the same
design method underpins the case. DS gets a lighter "design the analytics/ML pipeline"
variant.

## Links
- Study guides: [system-design](../guides/system-design.md) (the method), [rag](../guides/rag.md), [agents](../guides/agents.md), [context-engineering-cost](../guides/context-engineering-cost.md) (domain content)
- Research: F4 in `.claude/docs/plans/2026-07-17-interview-kb-consolidation.md`
