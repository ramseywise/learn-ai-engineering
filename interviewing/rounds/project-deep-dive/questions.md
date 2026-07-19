# Project Deep-Dive — Question Bank

15 questions across 9 categories. Each entry: what they're testing, how to structure the answer, what they'll drill into.

---

## Architecture Walkthrough

### 1. "Walk me through the architecture of X."

**What they're testing**: Whether you actually built it. People who only touched pieces can't narrate the whole system coherently. They're also checking whether you understand *why* each component exists.

**Model answer structure**:
1. State the problem the system solved (1 sentence)
2. Name the major components and their roles (left to right, top to bottom — follow data flow)
3. Highlight the two or three design choices that weren't obvious
4. Land on the outcome

Don't wait to be asked to draw it — offer to draw it. The act of drawing reveals whether you own it.

**Follow-up probes**:
- "How does data get from A to B? What format?"
- "What happens if C goes down?"
- "Why is D a separate service rather than part of E?"
- "What's the read path vs. the write path?"

**Study refs**: system-design guide §6 (your systems as interview answers)

---

### 2. "How did you handle scale as the system grew?"

**What they're testing**: Whether you've operated a system over time, not just launched it. Real systems change. Did you anticipate growth, react to it, or get caught by it?

**Model answer structure**:
1. What scale you started at (concrete numbers)
2. The first bottleneck you hit and how you diagnosed it
3. The solution you chose and what you rejected
4. Where the system is now vs. where it started

**Follow-up probes**:
- "At what point did you realize you had a bottleneck?"
- "What was the monitoring that caught it?"
- "What did you have to re-architect vs. what scaled without changes?"

**Study refs**: system-design guide §6

---

### 3. "Draw the data flow from user request to response."

**What they're testing**: Systems thinking at the component level. Can you trace a single request through the system — including the happy path and the error path?

**Model answer structure**:
- Narrate while drawing: "Request hits the API gateway, gets authenticated here, routed to this service, which reads from this store..."
- Call out latency budgets at each hop if you know them
- Mention where things can fail and what happens

**Follow-up probes**:
- "What's the p99 latency of this hop?"
- "What happens if the database call times out?"
- "Where is state persisted? Where is it ephemeral?"

**Study refs**: system-design guide §6

---

## Decision Defense

### 4. "Why did you choose [stack/model/store/framework]?"

**What they're testing**: Decision ownership. Anyone can list technologies; you need to explain why *these* technologies given *these constraints* at *that point in time*. Hindsight rationalization fails here — interviewers know what the right answer looks like in 2026 and they'll spot a retrofitted justification.

**Model answer structure**:
1. State the constraints that shaped the choice (team size, timeline, existing infra, budget)
2. Name the alternative you seriously considered
3. Explain what made this one win given those constraints
4. Acknowledge what you'd choose differently now, and why

**Follow-up probes**:
- "What did [alternative] offer that [chosen] didn't?"
- "Were there constraints pushing you toward [chosen] that weren't purely technical?"
- "If you were starting fresh today with no legacy constraints, what would you pick?"

**Study refs**: system-design guide §6, product-business guide §5

---

### 5. "What trade-offs did you make that you're not fully satisfied with?"

**What they're testing**: Intellectual honesty and engineering judgment. The answer "none" is a failure signal. They want to know if you can see the seams in your own work.

**Model answer structure**:
- Name a real trade-off, not a humble-brag ("we had to move fast" is not a trade-off)
- Explain the pressure that caused it (time, resource, information available at the time)
- Describe what the cost has been (tech debt, operational burden, missed capability)
- Say what you'd do differently and what it would take

**Follow-up probes**:
- "Have you started paying down any of that debt?"
- "What would it cost to fix it now?"
- "Who would need to be convinced to prioritize it?"

**Study refs**: system-design guide §6

---

### 6. "Did you evaluate any open-source alternatives before building custom?"

**What they're testing**: Build-vs-buy judgment. Senior engineers don't default to building. They know when to build and can defend the choice.

**Model answer structure**:
1. Name what you evaluated
2. State the gap — what the OSS solution couldn't do or couldn't do fast enough
3. Scope what you built (not the whole thing, just the gap)
4. If you built the whole thing: be ready to explain why, with specifics

**Follow-up probes**:
- "How long did evaluation take? Was that the right amount of time?"
- "Has the OSS landscape changed since you made that call?"
- "Did any of the OSS projects catch up?"

---

## Failure and Incident Analysis

### 7. "What was the hardest bug or incident?"

**What they're testing**: How you operate under pressure, how you reason about failure, and whether you've actually run a production system. Rehearsed answers here are obvious — the story should be specific enough that it couldn't be generic.

**Model answer structure** (detection → isolation → root cause → fix → prevention):
1. What you were seeing (symptoms, not cause — what the monitoring showed)
2. How you isolated it (what you ruled out, in what order)
3. Root cause (the actual thing, not "a bug")
4. Immediate fix
5. Long-term prevention (the thing you added to make sure it can't happen again)

**Follow-up probes**:
- "How long did it take to detect?"
- "What was the customer impact?"
- "What would have caught this before it hit production?"
- "What did you add to monitoring after?"

**Study refs**: evals-observability guide

---

### 8. "Tell me about a time the system failed in a way you didn't anticipate."

**What they're testing**: Whether your mental model of the system was accurate, and what you learned when it wasn't. Unanticipated failures reveal assumption debt.

**Model answer structure**:
1. The assumption that turned out to be wrong
2. What happened when reality diverged from the model
3. How you discovered the divergence (monitoring? user report? data anomaly?)
4. What the correct mental model turned out to be
5. How you encoded that new model (runbook, test, monitoring, architecture change)

**Follow-up probes**:
- "Was there a way to have known this in advance?"
- "Who else had the wrong mental model?"
- "How did you communicate the corrected model to the team?"

**Study refs**: evals-observability guide

---

## Measurement and Impact

### 9. "How did you measure success?"

**What they're testing**: Whether you connected engineering work to outcomes. People who only measured latency and throughput (technical metrics) but not business impact get a lower score than people who linked both.

**Model answer structure**:
1. What you measured at the system level (latency, error rate, throughput)
2. What you measured at the product level (user behavior, task completion, retention)
3. What you measured at the business level (cost, revenue, NPS, whatever was tracked)
4. The number that mattered most, and why

**Follow-up probes**:
- "How did you know you were measuring the right thing?"
- "Were there metrics you tracked that turned out not to matter?"
- "What would you add to your measurement plan if you were starting over?"

**Study refs**: evals-observability guide, product-business guide §5

---

### 10. "What was the quantified impact of the system?"

**What they're testing**: Whether you prepared numbers. Unprepared answers ("it improved things significantly") read as low-stakes projects or low ownership. Prepared numbers signal that you actually cared about the outcome.

**Model answer structure**:
- Lead with the number: "We reduced inference cost by 40% and brought p99 latency from 4.2s to 1.1s"
- Then explain what you changed to get there
- Contextualize the number (40% of what baseline? Over what time period?)

**Follow-up probes**:
- "How did you get that baseline?"
- "Was that improvement sustained over time?"
- "What would it have cost not to do this project?"

**Study refs**: product-business guide §5

---

## Team and Ownership

### 11. "How much of this was you?"

**What they're testing**: Precise credit. They need to calibrate whether they're hiring the person who designed the system or the person who implemented one part of it. Imprecise answers ("it was a team effort") fail — they want specificity.

**Model answer structure**:
- Name what you personally owned: "I designed the retrieval layer and built the evaluation harness. I also drove the architectural review."
- Name what others built: "The frontend was a different team. The embedding pipeline was a colleague."
- Name what you contributed to but didn't own: "I reviewed the data pipeline design and flagged a correctness issue."

**Follow-up probes**:
- "Who made the final call on [specific decision]?"
- "Were there parts of the architecture you disagreed with?"
- "What would have been different if you weren't on the team?"

---

### 12. "Tell me about a technical disagreement you had with your team."

**What they're testing**: Whether you can collaborate on ambiguous technical decisions, hold a position under pressure, and update when you're wrong.

**Model answer structure**:
1. The disagreement (what were the two positions?)
2. How you made the case (data, prototype, reference, analogy)
3. How it resolved (you won, you lost, you compromised, you let it go)
4. Whether the outcome was right in retrospect

**Follow-up probes**:
- "What would you have done if you'd had final say?"
- "Did the outcome validate your position or theirs?"
- "How did you handle it if you were overruled?"

---

## "Differently Today"

### 13. "What would you do differently?"

**What they're testing**: Learning and growth. "Nothing" is a disqualifying answer. They want to see that you've developed judgment since you built it — that you now see things you couldn't see then.

**Model answer structure**:
Prepare two answers, one architectural and one process:

*Architectural*: "I would have decoupled X from Y earlier. We made them tightly coupled because of timeline pressure, and it cost us six months of refactoring when requirements changed."

*Process*: "I would have done a design review with the team operating the system before writing the first line. We discovered operational constraints in production that we could have known in week one."

**Follow-up probes**:
- "What would it cost to make that change now?"
- "What was the specific failure mode that made you see this?"
- "Is there a lesson you've already applied to the next project?"

---

## AI Tools Usage (2026)

### 14. "Where did you use AI tools in this project, and how did you verify their output?"

**What they're testing**: Judgment about AI tool use. They're not asking whether you used AI tools (everyone does) — they're asking whether you used them well and whether you know when not to trust them.

**Model answer structure**:
1. Where you used them (code generation, test scaffolding, documentation, data analysis, architecture brainstorming)
2. What your verification method was for each use case (ran the tests, read every line before merging, spot-checked against ground truth)
3. Where you chose *not* to trust them (and why)
4. Any case where AI output was wrong in a way that mattered, and how you caught it

**Follow-up probes**:
- "Have you had a case where AI-generated code passed tests but had a logic error?"
- "How do you verify AI-generated architecture recommendations?"
- "Do you have a rule of thumb for when to trust vs. verify?"

---

## Scale and Growth Stories

### 15. "Tell me about a system you built that outgrew its original design."

**What they're testing**: Whether you've operated a system through growth, and whether you made architectural decisions that aged well or aged poorly. This is often a proxy for seniority — you need a system that existed long enough to outgrow itself.

**Model answer structure**:
1. Original design assumptions (scale, usage patterns, team size)
2. The first thing that broke when assumptions were violated
3. The intermediate solutions (the ones that bought time)
4. The eventual re-architecture (or why you haven't done it yet)
5. What you'd design differently to handle growth from day one

**Follow-up probes**:
- "At what scale did the original design start straining?"
- "Were there early signs you missed?"
- "What did the re-architecture cost in terms of time and stability?"

**Study refs**: system-design guide §6
