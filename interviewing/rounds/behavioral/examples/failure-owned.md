# Worked STAR Example: Failure Owned

**Prompt**: "Tell me about a time you failed."

**Story category**: Real failure — real stakes, causal role stated plainly, the fix, visible behavior change.

---

## The story

### Situation
> I was the technical lead on a data pipeline migration — moving a legacy ETL system to a new
> streaming architecture that would reduce processing latency from 6 hours to under 15 minutes.
> The migration was a high-priority initiative with a fixed deadline tied to a product launch.

**Annotation**: Sets up real stakes immediately — high-priority initiative, fixed deadline,
product launch dependency. The interviewer knows something real could go wrong here. Note: no
hedging, no foreshadowing of success. The setup doesn't telegraph the outcome.

---

### Task
> I was responsible for the migration plan, the cutover schedule, and the go/no-go call.
> Engineering leadership trusted me to run this autonomously.

**Annotation**: Ownership is explicit and personal. "I was responsible for... the go/no-go
call" is load-bearing — it establishes that when something went wrong, there was nowhere to
point except at yourself.

---

### Action
> I underestimated the schema complexity of the legacy system. I had audited the documented
> schemas, but there were 14 undocumented field variants that only appeared in edge-case
> producer configurations — configurations that hadn't been exercised in our test data.
>
> I ran our standard test suite. Everything passed. I gave the go-ahead.
>
> In the first 4 hours post-cutover, about 8% of records from those edge-case producers were
> silently dropped — no errors, just missing data. The pipeline had no schema validation layer
> that would flag a mismatch; it treated unknown fields as optional and dropped them.
>
> I caught it at hour 4 through a downstream data quality alert — not from the pipeline itself.
> I immediately rolled back to the legacy system, ran a retroactive reconciliation to identify
> affected records, and spent the next 12 hours with the team rebuilding the schema validation
> layer before we attempted cutover again.
>
> I drafted a post-mortem that same day while it was fresh. I named my causal failures
> specifically: I relied on documented schemas without auditing the actual producers; I didn't
> add schema validation to the new pipeline before cutover; I treated "tests pass" as equivalent
> to "edge cases handled."

**Annotation**: This Action section is doing several things correctly:

1. **"I underestimated"** — the first sentence names the failure plainly without hedging. Not
   "the schemas were more complex than anticipated" — "I underestimated."
2. **The mechanism of failure** — explaining *how* the failure happened (undocumented edge cases,
   no validation layer) shows that you understand the failure deeply, not just that it happened.
3. **"I ran our standard test suite. Everything passed. I gave the go-ahead."** — This is a
   critical sentence. It shows the moment of your causal decision. You had information (tests
   passed) and made a judgment call that turned out to be wrong. That's what real failure looks
   like — not negligence, but a gap in your model of the system.
4. **The response** — you rolled back, reconciled, and fixed. Fast. This matters but it's not
   the main point of the story.
5. **The post-mortem naming causal failures specifically** — you held yourself accountable in
   writing, in the same day, while it was fresh. This signals genuine ownership, not just
   performance of ownership.

**Common mistakes at Action**:
- "Due to circumstances outside our control..." — hedging.
- "The team and I..." — diffusion.
- Spending too much time on the fix and not enough on the failure mechanism.

---

### Result
> The product launch was delayed 2 days. The cutover eventually succeeded with zero data loss
> on the second attempt. We recovered all 8% of dropped records through the reconciliation.
>
> Leadership was disappointed about the delay but trusted the process — specifically the
> speed of the rollback and the depth of the post-mortem. Our CTO later used the post-mortem
> as a template for how to handle migration incidents.

**Annotation**: Both the cost and the recovery are named. "The product launch was delayed 2
days" — a real consequence, stated without minimizing. "Leadership was disappointed" — honest
about the relational cost.

The recovery detail ("CTO later used the post-mortem as a template") is not included to soften
the failure — it's included because it's true and it completes the picture. The question is
whether you can recover and what your recovery looks like. The answer here is: fast, thorough,
accountable, and useful to the org.

---

### Reflection
> Since then, I always audit actual data producers and not just documented schemas before any
> migration. I also added a mandatory schema validation step to our migration checklist — new
> pipelines now validate incoming records against an explicit schema with hard failures, not
> silent drops. And I treat "tests pass" as "the cases I thought of are handled" — which is
> not the same as "edge cases are handled."

**Annotation**: Three specific behaviors, not one vague learning:

1. "I always audit actual data producers" — a new step you added.
2. "Mandatory schema validation step to our migration checklist" — a process change, not just
   a mindset change.
3. "I treat 'tests pass' as 'the cases I thought of are handled'" — a cognitive reframe that
   surfaces every time you're evaluating a test suite.

The last one is particularly strong because it shows you updated your mental model, not just
your checklist. The failure happened because your model of what "tests pass" meant was wrong.
The reflection shows you corrected the model.

---

## What this story is doing (structural summary)

| Component | Signal it sends |
|-----------|----------------|
| Situation (real stakes) | Not a near-miss; a real failure with product consequences |
| Task (explicit ownership) | No diffusion possible — you gave the go-ahead |
| Action (named cause) | "I underestimated" — causal role stated without hedging |
| Action (failure mechanism) | Deep understanding of how it happened, not just that it happened |
| Action (post-mortem same day) | Genuine ownership, not performance of ownership |
| Result (cost named) | 2-day delay, stated plainly — no minimizing |
| Result (recovery named) | Fast rollback, full reconciliation, zero data loss after second attempt |
| Reflection (3 specific behaviors) | Not "I'm more careful" — three specific things you do differently |

---

## Calibration: what distinguishes this from a weak failure story

| Weak version | This version |
|-------------|--------------|
| "The migration was harder than expected" | "I underestimated the schema complexity" |
| "There were some undocumented schemas" | "14 undocumented field variants in edge-case configurations I didn't audit" |
| "Tests were run but some cases were missed" | "I ran our standard test suite. Everything passed. I gave the go-ahead." — your decision, your moment |
| "Data was lost but we recovered it" | "8% of records silently dropped, retroactive reconciliation, all recovered" |
| "I learned to be more thorough" | Three specific behaviors: audit actual producers, mandatory schema validation, reframe what 'tests pass' means |
| "It was ultimately fine" | "The product launch was delayed 2 days. Leadership was disappointed." — consequences named plainly |
