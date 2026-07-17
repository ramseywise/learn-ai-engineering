# Project Deep-Dive / Experience Review

## What's tested
Whether you actually built what your resume claims, at the depth you claim: architecture
recall, decision ownership ("why X over Y" with the constraints of the time), honest
failure analysis, and impact quantification. The standard senior-signal round (research
F5) — seniority reads as *decisions defended*, not technologies listed.

## Format & trends
45–60 min on one or two projects you choose (or they pick from your resume). The
interviewer drills down until they hit the boundary of your ownership — expect "what
would you do differently?", "what broke?", "what did the alternative look like?". 2026
twist: expect "where did you use AI tools, and how did you verify their output?" as a
standard probe.

## Prep checklist
- [ ] Pick 2–3 projects; for each, prepare the three-altitude version
  ([product-business guide](../guides/product-business.md) §5): 60s exec pitch →
  5-min architecture walk → deep dive on any component.
- [ ] For each project, write down: the constraint set at decision time, 2–3 decisions
  with the rejected alternative and why, one failure/incident and its fix, the numbers
  (latency, cost, users, error rates, business impact).
- [ ] Draw each architecture from memory — you'll be asked to.
- [ ] Rehearse the librarian drill systems as deep-dive answers (the system-design
  guide §6 writeups are your own systems in interview format).
- [ ] Prepare the "differently today" answer per project — it demonstrates growth, and
  its absence reads as stagnation.
- [ ] Scrub client confidentiality: practice describing constraint shapes without naming
  names ("a public-sector client with strict data-residency requirements").

## Question bank
- "Walk me through the architecture of X." — top-down: problem → constraints → boxes →
  one interesting component in depth; invite steering ("happy to go deeper on any box").
- "Why did you choose that stack/model/store?" — constraints-at-the-time + alternatives
  considered + the trade-off that decided it; concede what's changed since.
- "What was the hardest bug/incident?" — detection → isolation → root cause → fix →
  prevention; the prevention step is the senior signal.
- "How did you measure success?" — metrics stated unprompted, eval/monitoring story
  ([evals guide](../guides/evals-observability.md)); tie to a business number.
- "What would you do differently?" — one architectural, one process answer, both with
  reasons — never "nothing".
- "How much of this was you?" — precise ownership, credit the team; inflated claims die
  on the next follow-up.

## Per-role weighting
| AIE | MLE | DS | FDE |
|---|---|---|---|
| ● | ● | ◐ | ● |

Core in every senior loop; for FDE it doubles as a customer-communication sample — the
interviewer is watching *how* you explain as much as what
([customer-simulation](customer-simulation.md)).

## Links
- Study guides: [system-design](../guides/system-design.md) §6 (your systems as drills), [product-business](../guides/product-business.md) §5 (three-audience pitch), [evals-observability](../guides/evals-observability.md) (the measurement story)
- Repo: `../PORTFOLIO.md`; research F5 in `.claude/docs/plans/2026-07-17-interview-kb-consolidation.md`
