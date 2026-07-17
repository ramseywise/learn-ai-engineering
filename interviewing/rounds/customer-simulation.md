# Customer / Stakeholder Simulation

## What's tested
The FDE signature round (research F5), distinct from behavioral: live role-play where the
interviewer plays a customer — skeptical exec, confused domain expert, frustrated
champion — and scores empathy, discovery skill, expectation-setting, and technical
translation under social pressure. Anthropic's version is the loop's hidden filter:
~60% of candidates who pass coding fail it (research F4).

## Format & trends
30–60 min. Scenarios: kickoff discovery call, delivering bad news (the model
underperforms), scope-creep pushback, "the demo failed in front of their CEO",
non-technical exec asks "why is this taking so long?". The interviewer improvises off
your responses — scripts break immediately; *habits* pass. FDE loops weight this plus the
case at ~50% of total evaluation (research F4): the engineering bar filters, but the
customer bar decides.

## The habits that pass
- **Discovery before prescription**: open with questions (workflow today, pain ranking,
  success definition, who decides) — never with your solution.
  ([product-business guide](../guides/product-business.md) §1 framing habit.)
- **Listen and mirror**: restate their problem in their words before answering; catch the
  emotional layer ("it sounds like the team's trust in the tool took a hit").
- **Translate, don't dumb down**: pick the altitude for the audience
  (product-business §5); analogies over jargon; check comprehension ("does that map to
  how you think about it?").
- **Bad news straight, with a path**: state the problem plainly, own your side, bring
  options with trade-offs and a recommendation — never just the problem.
- **Boundaries without "no"**: scope creep → "yes, and here's what it displaces — which
  matters more to you?"; anchor to the success metric agreed at kickoff.
- **Next step always**: every conversation ends with a concrete, dated follow-up.

## Prep checklist
- [ ] Mock the five scenarios above out loud (a peer or an LLM playing the customer
  works); record and review one.
- [ ] Prepare discovery question sets for 2–3 industries you'd serve (and for nonprofit
  clients: capacity, funding cycle, data sensitivity — product-business §4).
- [ ] Rehearse two bad-news deliveries: model quality miss, timeline slip — plain
  statement + options + recommendation.
- [ ] Have ROI arithmetic ready to do live on their numbers (product-business §2).
- [ ] Know your escalation line: what you'd commit to in the room vs take back to the
  team — overpromising in the sim is scored as overpromising with a client.

## Question bank (scenario prompts)
- "I'm the COO. Your AI gave our customer wrong information yesterday. Go." —
  acknowledge, no defensiveness; containment already done/proposed; root cause honestly
  ([security guide](../guides/security-safety.md) incident framing); prevention +
  monitoring; rebuild trust with a review cadence.
- "We want it to do everything your competitor's demo showed." — discovery on which
  capability maps to their actual workflow; demo ≠ production; phase the roadmap by
  value ([agents guide](../guides/agents.md) §9 staged-trust pattern).
- "Why can't we just fine-tune on all our data?" — translate the adaptation ladder
  ([llm-fundamentals](../guides/llm-fundamentals.md) §3) into their terms: freshness,
  cost, privacy; recommend the boring first step.
- "The pilot metrics look bad and the renewal is next month." — reframe what the pilot
  measured vs what success meant; propose the smallest change that moves the decision
  metric; honest go/no-go recommendation.
- "Our IT team says no external APIs. Ever." — don't argue; discover the underlying
  concern (residency? audit?); options: self-hosted, VPC deployment, vendor with
  guarantees ([system-design guide](../guides/system-design.md) §7 on-prem-vs-API).

## Per-role weighting
| AIE | MLE | DS | FDE |
|---|---|---|---|
| ○ | ○ | ◐ | ● |

Decisive for FDE; DS meets a lighter version in stakeholder-facing case defenses; AIE/MLE
rarely see it as a dedicated round but the skills carry the
[project deep-dive](project-deep-dive.md).

## Links
- Study guides: [product-business](../guides/product-business.md) (the whole guide is this round's substrate)
- Research: F4/F5 in `.claude/docs/plans/2026-07-17-interview-kb-consolidation.md`
