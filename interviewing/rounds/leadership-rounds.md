# Leadership Rounds (CTO · Head of Product · founder) + Reverse Interview

## What's tested
These are interviewer-centric rounds — the content is *alignment*, not a fixed syllabus
(research F5): the CTO tests technical judgment and whether they'd trust you unsupervised;
the Head of Product tests product sense and whether engineering-you can be reasoned with;
a founder tests mission fit and ambiguity appetite. At startups these rounds mix system
design + judgment + your questions back — the reverse interview is **evaluated signal,
not politeness time**.

## Format & trends
30–60 min conversation, usually final stages. Low structure, high variance: expect one
deep technical-judgment thread (CTO), one product-thinking thread (HoP), and genuine
back-and-forth. They're also selling to you — engaged, specific questions from you are
scored as seriousness.

## Per-interviewer prep angle
- **CTO**: opinions with reasons about *their* likely stack tensions — build-vs-buy,
  model vendor strategy, eval discipline, tech-debt honesty. Expect "how would you
  approach our X?" — clarify like a design round, answer with trade-offs
  ([system-design guide](../guides/9-system-design/interview-guide.md) §2). Have one strong-opinion-loosely-
  held ready and one "here's where I'd need your context" — both land.
- **Head of Product**: think in user problems and metrics trees
  ([product-business guide](../guides/10-product-delivery/interview-guide.md) §3); expect "should we build
  feature X?" → interrogate the problem first (§1); show you'll push back on solution-
  first requests *respectfully*.
- **Founder/CEO**: why this mission, specifically; what you'd do in the first 90 days;
  comfort with wearing multiple hats; a real question about their strategy that proves
  you did the reading.

## Reverse interview — question bank (also startup due-diligence)
Pick 3–4 per round; tailor. These do double duty: they signal judgment *and* protect you.

**Technical/judgment (for the CTO)**
- "What's the most expensive technical decision you'd revisit if you could?"
- "How do you evaluate model/vendor changes — is there an eval gate?" (their answer
  tells you the [evals](../guides/6-evals-observability/interview-guide.md) maturity)
- "Where does AI-generated code sit in your review process?"
- "What does on-call / incident load actually look like?"

**Product/org (for HoP)**
- "How do you decide what *not* to build?"
- "Walk me through the last feature you killed and why."
- "How do eng and product disagree here — recent example?"

**Due-diligence (founder/any)**
- "What's the runway, and what milestone does the next raise depend on?"
- "Who left recently and why?" (asked kindly — the answer's texture matters more than
  the content)
- "What would make the person in this role fail in the first year?"
- "How has the team's use of AI changed how you hire?" (2026 signal both ways)

## Prep checklist
- [ ] Research: their engineering blog, the CTO/HoP's talks or posts, recent product
  launches, funding stage — one specific reference per interviewer.
- [ ] Prepare your 90-day sketch: learn (systems, users, metrics) → small shippable win
  → one process improvement offered, not imposed.
- [ ] Rehearse two judgment threads: a technology bet you'd make today with reasons, and
  a hype you'd resist with reasons — both must survive follow-ups.
- [ ] Pick your reverse-interview set per interviewer; write them down — reading from
  notes here is fine and even reads as prepared.
- [ ] Decide your real deal-breakers beforehand (comp floor, remote needs, mission fit)
  so due-diligence answers register instead of washing past.

## Per-role weighting
| AIE | MLE | DS | FDE |
|---|---|---|---|
| ● | ◐ | ◐ | ● |

Near-certain in startup loops (research: CTO/HoP rounds imply small-company processes);
FDE adds a customer-executive flavor — the [customer-simulation](customer-simulation.md)
habits apply to the interview itself.

## Links
- Study guides: [product-business](../guides/10-product-delivery/interview-guide.md), [system-design](../guides/9-system-design/interview-guide.md) (judgment threads run on its method)
- Research: F5 (incl. the interviewer-centric → what-is-tested reframing) in `.claude/docs/plans/2026-07-17-interview-kb-consolidation.md`
