# Customer / Stakeholder Simulation

## What's tested

The FDE signature round — live role-play where the interviewer plays a customer (skeptical exec, confused domain expert, frustrated champion) and scores:

- **Empathy** — do you acknowledge their emotional state before solving?
- **Discovery skill** — do you ask before prescribing?
- **Expectation-setting** — are commitments concrete and honest?
- **Technical translation under social pressure** — can you hold altitude while someone's frustrated?

~60% of candidates who pass coding fail this round. The failure mode is consistent: they revert to engineering mode under pressure — defending architecture, deploying jargon, solving before listening.

## Format & trends

30–60 min. The interviewer improvises off your responses — written scripts break immediately. *Habits* pass.

Common scenarios:
- Kickoff discovery call (blank-slate customer)
- Delivering bad news (model underperforms, timeline slips)
- Scope-creep pushback (competitor feature demand)
- The demo failed in front of their CEO
- Non-technical exec: "why is this taking so long?"
- Hostile new contact after champion departure
- IT constraint: "no external APIs"
- Data privacy concern raised mid-engagement
- In-house build threat

## The six habits that pass

1. **Discovery before prescription** — open with questions, never your solution
2. **Listen and mirror** — restate their problem in their words before answering
3. **Translate, don't dumb down** — match the altitude to the audience; analogies over jargon
4. **Bad news straight, with a path** — state the problem plainly, own your side, bring options with trade-offs and a recommendation
5. **Boundaries without "no"** — scope creep → "yes, and here's what it displaces — which matters more to you?"
6. **Next step always** — every conversation ends with a concrete, dated follow-up

## Prep checklist

- [ ] Mock all twelve scenarios in `questions.md` out loud (recording preferred)
- [ ] Prepare discovery question sets for 2–3 industries (templates in `study-guide.md`)
- [ ] Rehearse two bad-news deliveries: model quality miss, timeline slip
- [ ] Have ROI arithmetic ready to do live on their numbers (token math, hours-saved, error-cost)
- [ ] Know your escalation line: what you'd commit to in the room vs. take back to the team
- [ ] Review worked examples in `examples/` — annotated dialogue for incident response, scope negotiation, bad-news delivery

## Per-role weighting

| AIE | MLE | DS | FDE |
|-----|-----|-----|-----|
| ○   | ○   | ◐   | ●   |

Decisive for FDE. Partial signal for DS (stakeholder communication in project sign-off). Minimal weight for AIE/MLE unless the role is client-facing.

## Folder contents

```
customer-simulation/
├── README.md          — this file
├── questions.md       — 12 scenario prompts with testing signal, response structure, red flags
├── study-guide.md     — habits deep dive, discovery frameworks, translation techniques, practice plan
├── sources.md         — internal guides + external methodology references
└── examples/
    ├── README.md
    ├── incident-response.md    — "Your AI gave wrong information" full dialogue
    ├── scope-negotiation.md    — Competitor feature demand + boundary setting
    └── bad-news-delivery.md    — Pilot metrics miss with renewal pressure
```
