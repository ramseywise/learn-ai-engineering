# Project Deep-Dive / Experience Review

## What's Tested

The interviewer is checking whether you actually built what your resume claims, at the depth you claim. Three signals matter:

1. **Ownership depth** — Can you walk the architecture from memory, explain every component's role, and name the alternatives you rejected? People who only reviewed or debugged someone else's system can't do this.
2. **Decision defense** — "Why X over Y" answered with the constraints *at decision time*, not hindsight rationalization. Seniority reads as decisions defended, not technologies listed.
3. **Impact quantification** — Numbers prepared in advance. Latency, throughput, cost, user growth, error rate reduction. If you can't quantify the outcome, the project reads as low-stakes.

Expect drilling until the interviewer hits the boundary of your ownership. They are intentionally looking for that boundary — the goal is calibration, not exposure.

## Format

- **Duration**: 45–60 minutes on one or two projects (your choice, or they pick from your resume)
- **Structure**: You lead with a brief overview, then the interviewer drills into whatever interests them
- **Depth probes**: "What would you do differently?", "What broke?", "What did the alternative look like?", "How much of this was you?"
- **2026 addition**: "Where did you use AI tools, and how did you verify their output?" is now a standard probe at most shops

## The Three-Altitude Method

Every project answer should exist at three altitudes, and you should be able to shift between them on demand:

| Altitude | Duration | Content |
|----------|----------|---------|
| Executive pitch | 60 seconds | What problem, what approach, what outcome — no jargon |
| Architecture walk | 5 minutes | Components, data flow, key technology choices |
| Deep dive | Unlimited | Any single component at full detail — trade-offs, constraints, incidents |

The interviewer controls which altitude you're at. Practice transitions both ways.

## Prep Checklist

- [ ] Pick 2–3 projects; prepare all three altitudes for each
- [ ] For each project, write down: constraint set at decision time, 2–3 decisions with the rejected alternative and why, one failure/incident with root cause and fix, the numbers
- [ ] Draw each architecture from memory — practice until you can do it in under 3 minutes
- [ ] Prepare a "differently today" answer for each project (one architectural, one process)
- [ ] Prepare the AI tools probe: where you used them, how you verified output, when you didn't trust them
- [ ] Scrub client confidentiality: practice describing constraint shapes without naming clients
- [ ] Rehearse with a peer who drills down — solo rehearsal doesn't surface the gaps

## Per-Role Weighting

| AIE | MLE | DS | FDE |
|-----|-----|----|-----|
| Core | Core | Moderate | Core |

Core in every senior loop. For FDE it doubles as a customer-communication sample — clarity and audience calibration matter as much as depth.

## Folder Contents

| File | Purpose |
|------|---------|
| `questions.md` | 15 questions with signals, answer structures, follow-up probes |
| `study-guide.md` | Frameworks: three-altitude method, decision docs, incident storytelling, impact quantification |
| `sources.md` | Internal study guides + external resources |
| `examples/` | Worked answers for architecture walkthrough, decision defense, incident story |
