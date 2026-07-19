# Study Guide — Project Deep-Dive

## The Three-Altitude Framework

Every project answer must exist at three altitudes. You shift between them on the interviewer's signal.

### Altitude 1: Executive pitch (60 seconds)
**Target**: Anyone — no assumed technical context.

Template:
> "We had [problem], which cost [stakeholders] [consequence]. I built [what], which [mechanism in one sentence]. The result was [quantified outcome]."

Practice constraint: time yourself. If you go over 90 seconds you're not at altitude 1 — you've slipped into altitude 2.

### Altitude 2: Architecture walk (5 minutes)
**Target**: Technical peer — assumes engineering vocabulary, not domain-specific knowledge.

Structure:
1. Data flow narrative: "A request enters here, gets [transformed] by [component], stored in [store], served by [component]"
2. Three key technology choices with one-sentence rationales
3. One constraint that shaped the design
4. Scale/load at operation (concrete numbers)

Draw while you talk. Offer before they ask.

### Altitude 3: Deep dive (unlimited)
**Target**: Domain expert — peer-level interrogation of any component.

You don't prepare this wholesale — you prepare it per-component. For each major component:
- Alternatives considered and why they lost
- One thing that surprised you in implementation
- The operational failure mode you'd guard against
- The number that characterizes its performance

**Transition practice**: Start at altitude 1, have a peer interrupt and ask you to go deeper. Practice switching to 2 mid-sentence. Then have them pick a component and drill altitude 3. Solo rehearsal doesn't surface the gap — you need someone interrupting you.

---

## Decision Documentation Template

Before each interview, fill this out for every significant decision in the project:

```
Decision: [What you chose]
Date context: [When, and what the state of the art was at that time]
Constraints at the time: [Team size, timeline, budget, existing infrastructure, data availability]
Alternative considered: [The main thing you rejected]
Why it lost: [The specific thing that eliminated it given the constraints above]
Why this one won: [Not just "it was better" — the specific advantage that mattered]
Cost of this choice: [What you gave up]
What changed since: [If you were deciding today, what's different?]
Would you make the same choice today: [Yes/No/Depends — and why]
```

Interviewers are checking that your "why" is grounded in constraints, not just taste. "We chose Postgres because it's reliable" is not a decision — it's a preference. "We chose Postgres because we needed ACID guarantees for billing and the team had no operational experience with distributed datastores at our scale" is a decision.

---

## Architecture Drawing Method

Drawing from memory is a threshold skill. If you can't draw it, you don't own it.

**Practice method**:
1. Draw the architecture cold, no notes. Set a 3-minute timer.
2. Compare to any existing diagrams.
3. Note what you forgot or placed wrong.
4. Repeat until you can draw it in 3 minutes with no hesitation.

**Drawing conventions that signal competence**:
- Boxes for services/components, cylinders for databases, arrows for data flow (label the arrows with data format or protocol)
- Separate the read path from the write path visually
- Mark async vs. sync interactions
- Add scale annotations ("~10K rps at peak") to key components

**What forgetting reveals**: If you can't draw it, the interviewer will notice you're reconstructing from memory in real time. This is a signal they are trained to catch.

---

## Failure and Incident Storytelling

Structure every incident story with this five-part frame:

| Part | What it covers | What to avoid |
|------|---------------|---------------|
| Detection | How you knew something was wrong (monitoring, alert, user report, data anomaly) | Saying "a user reported" without explaining why monitoring didn't catch it first |
| Isolation | The debugging process: what you ruled out, in what order, and why | Jumping straight to root cause — the isolation process is what reveals your systems thinking |
| Root cause | The actual cause, not a symptom | "There was a bug" — what was the bug, why did it exist, what assumption did it violate? |
| Fix | What you did to resolve it, immediate and short-term | Only describing the immediate hotfix without the stabilizing change |
| Prevention | What you added to make sure it can't happen again | Saying "we were more careful" — name a concrete artifact (alert, test, runbook, architecture change) |

**Specificity is the signal**: "A cache invalidation bug under concurrent writes" is specific. "A race condition" is not. If you can't recall specifics, pick a different incident.

---

## Impact Quantification

Prepare numbers for every project before the interview. You will not remember them under pressure if you haven't written them down.

**Numbers to prepare**:

| Category | Example metrics |
|----------|----------------|
| Performance | p50/p95/p99 latency, throughput (rps), inference time |
| Reliability | Error rate (%), uptime (%), MTTR |
| Scale | DAU/MAU, data volume, QPS at peak |
| Cost | Monthly infra cost, cost per request, cost reduction % |
| Business | Conversion rate change, time-to-complete, user retention, NPS delta |
| Team | Time saved per week, number of users/teams enabled |

**How to present them**:
- Lead with the most impressive number: "We reduced cost by 60%..."
- Immediately anchor it: "...from $28K/month to $11K/month"
- Contextualize if needed: "...on a workload processing 4M documents/day"
- If you don't have a number: "We didn't instrument this at the time, but the qualitative signal was X, and after adding instrumentation we saw Y"

Not having numbers for a feature you shipped is acceptable. Not having numbers for a project you led is a yellow flag.

---

## Ownership Calibration

Interviewers are calibrating the scope of your contribution. Vague answers ("we built...") read as low ownership. Precise answers signal confidence.

**The framing**:
- "I designed and built X" — you owned it from spec to production
- "I led the design of X, which three engineers implemented" — you owned the architecture
- "I contributed to X, specifically [component]" — honest scope credit
- "I reviewed X and flagged a correctness issue in the [part]" — contribution without ownership

**Common error**: Using "we" for everything. It's not humble — it's ambiguous. The interviewer can't distinguish "we means my team" from "we means I don't want to overclaim." Be specific, then acknowledge the team: "I designed the retrieval layer. The indexing pipeline was built by a colleague with significant input from me on the chunking strategy."

**Honest boundaries**: When the interviewer hits the edge of your ownership, say so: "That component was owned by another team — I can tell you how it behaved from our perspective, but I don't know the internal details." This is a stronger answer than guessing.

---

## "Differently Today" Preparation

Prepare two answers per project:

**Architectural**: A concrete design choice you'd make differently given what you know now. Not "I'd use a better tool" — name the tool, the decision, and the specific failure mode that revealed the issue.

> "I'd separate the ingestion pipeline from the serving layer from day one. We coupled them because it was faster to build, but when we needed to re-index with a new chunking strategy, we had to rebuild both simultaneously. A clean separation would have meant a 2-week job instead of a 6-week one."

**Process**: A workflow, team structure, or communication change.

> "I'd have involved the oncall engineer in architecture review before we wrote a line of code. We discovered operational constraints — specifically around secret rotation and log retention — six months into production. We could have known in week one."

**What to avoid**: "I wouldn't change anything" (disqualifying), and "I'd have had more time" (not a decision — a complaint).

---

## AI Tools Probe Preparation

Treat this as its own project narrative. Prepare:

1. **Where you used AI tools**: Be specific. "I used Claude for generating test scaffolding and initial boilerplate, Cursor for autocomplete in well-understood code paths, and ChatGPT for architecture brainstorming when I wanted an outside perspective."

2. **Verification method per use case**:
   - Code generation: "I read every line before merging. I also ran the full test suite and added specific tests for the generated code's edge cases."
   - Architecture suggestions: "I treated them as a starting point for structured thinking, not as recommendations. I always checked claims against the actual docs."
   - Data analysis: "I verified outputs against a hand-labeled sample before trusting the pattern."

3. **When you didn't trust them**: Name a concrete case. "The model confidently gave me an API call signature that was wrong — the parameter name had changed in the latest version. Now I always verify against the actual docs for any library-specific code."

4. **Where you chose not to use them**: "For anything security-critical or where correctness was load-bearing and tests couldn't fully cover it, I preferred to reason through it myself and then have a peer review it."

---

## Confidentiality Techniques

Client names and proprietary data are protected. The following shapes are safe to share:

- **Scale shape**: "A Fortune 500 retail company" → "A large enterprise retail client with SKU catalog in the tens of millions"
- **Problem shape**: "Built a churn prediction model for [bank]" → "Built a churn prediction model for a consumer financial services company with ~2M monthly active users"
- **Constraint shape**: "The client's data couldn't leave their VPC" → "Strict data residency requirements meant the model had to run in the client's own cloud environment"

Practice once before each interview if the project has sensitive client details. Getting interrupted mid-story because you realized you said a client name is disruptive.

---

## Practice Plan

**Week before**:
- Fill out the decision documentation template for each project
- Write down all numbers — don't rely on memory in the interview
- Draw each architecture cold; repeat until 3 minutes clean

**3 days before**:
- Run one altitude-1 pitch per project out loud (not just in your head)
- Do one full rehearsal with a peer on your strongest project — have them drill

**Day before**:
- Prepare the incident story — write it out with all five parts
- Prep the "differently today" answer for each project

**No-prep moves** (if you have 30 minutes):
- Draw the architectures
- Write the numbers
- Rehearse the three-altitude transitions on your best project

---

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Inflated ownership ("I built the whole system") | Easy to expose — they'll ask about parts you didn't build | Be precise: name what you owned and what you contributed to |
| No numbers | Signals low-stakes project or low ownership | Prepare numbers in advance; if you don't have them, say why and what the qualitative signal was |
| "I wouldn't change anything" | Signals no reflection or hiding something | Prepare one architectural and one process answer |
| Can't draw the architecture | Signals you didn't build it or didn't understand it | Practice drawing from memory; 3-minute target |
| Technology-forward answer ("We used Kafka because Kafka is great") | No decision logic — just technology affinity | Always anchor to the constraint that made it the right choice |
| "We" for everything | Ambiguous ownership | Be specific about your role, then acknowledge the team |
| Skipping the isolation step in incidents | Makes debugging look like guessing | Name what you ruled out and why |
| Can't answer "what broke?" | Projects rarely run perfectly — no failure story reads as low-stakes | Find an incident, even a small one; or talk about a near-miss and what you put in place |
