# Worked Example: Evaluating a Startup Through the Reverse Interview

## Setup

Company: Series A AI startup, 18 months old, building AI-native contract review for mid-market legal teams. ~25 employees, CTO is a former lawyer-turned-engineer, Head of Product from a LegalTech company. You're at the final stage.

You have 15 minutes of reverse-interview time split across the CTO and founder.

---

## With the CTO (8 minutes)

You've prepared three questions. You'll ask two, and use the third if time permits.

---

**Question 1:** "I was reading your engineering blog post about your shift from GPT-4 to a hybrid approach with fine-tuned models. How has that played out? What's been the hardest part?"

*Why this question:* It's specific. It shows you read their content. It asks for honest reflection, not a pitch.

**CTO's answer (paraphrased):**
"It's been a bigger lift than expected. The fine-tuned models perform better on our specific contract clause extraction tasks — we're getting about 15% better precision on the benchmark we care about — but the eval infrastructure to validate each model update before it ships has been harder to build than the model work itself. We're still not where I want to be on that."

*What this tells you:*
- Green: CTO is candid about the gap between ambition and execution
- Green: They have a benchmark they care about (not just vibes)
- Yellow: "Still not where I want to be" on eval infrastructure — this is a real gap, and it's the kind of thing that causes production incidents. Worth probing.

**Follow-up:** "When you say eval infrastructure — what does the current path to production look like for a model update?"

**CTO's answer:**
"Right now it's mostly manual review. We have a holdout test set we run against, but it's one engineer doing a qualitative pass before we push. We want to automate more of that but haven't gotten there."

*What this tells you:*
- Yellow/Red: Manual review at Series A velocity is a setup for regressions. This is a real technical risk.
- But also: the CTO knows it and is honest about it. That's a green flag on culture even if it's a yellow flag on state.

*Your read:* This is a place where you could add real value — and it's a real gap, not a manufactured one for the interview. Worth noting as a positive signal if this is the kind of work you want to do.

---

**Question 2:** "What would make the person in this role fail in the first year?"

*Why this question:* Surfaces unspoken expectations, role definition, and the CTO's theory of how the role works.

**CTO's answer:**
"Honestly? Moving too fast in the wrong direction. We've had engineers who are technically strong but who ship things that solve the wrong problem — they're executing before they really understand the use case. Legal contracts have a lot of domain nuance that you have to learn before you optimize for. The person who fails here is usually the one who comes in with a solution before they have the problem."

*What this tells you:*
- Green: Self-aware about a real failure mode. Specific and non-generic.
- Green: "Learn the domain" is a cultural value, not just a throwaway line
- Implication: Your 90-day sketch should emphasize the listen-and-map phase explicitly

---

## With the founder (7 minutes)

**Question 3:** "What's the runway, and what milestone does the next raise depend on?"

*Why this question:* Due diligence. The answer tells you about financial stability, strategic clarity, and how honest they are with candidates.

**Founder's answer:**
"We have about 18 months of runway at current burn. We're targeting a Series B in about 14 months — which gives us some buffer. The milestone we've committed to is $3M ARR. We're at $1.2M now, so it's a real lift but we have line-of-sight on it from our pipeline."

*What this tells you:*
- Green: Specific numbers, clear milestone, honest about the gap
- Green: 18 months with a 14-month target is a reasonable buffer, not reckless
- Green: $1.2M to $3M in 14 months is aggressive but plausible for B2B SaaS with a defined ICP
- Note: "line-of-sight from pipeline" is worth understanding — is this closed ARR-equivalent or just pipeline?

**Follow-up:** "When you say line-of-sight — is that from signed contracts or active pipeline?"

**Founder's answer:**
"Mix — we have $400K in LOIs and the rest is in late-stage deals. Two deals could close in the next 60 days that would get us to $2M."

*What this tells you:*
- Yellow: LOIs are not ARR. Two deals in late stage is real but concentrated risk.
- But: The founder answered honestly and with specifics. That's a positive signal on transparency.

---

**Question 4 (bonus if time):** "Who left recently, and why?"

*Why this question:* Retention is one of the most honest signals about leadership and culture.

**Founder's answer:**
"We had one senior engineer leave about four months ago. She'd been with us since the beginning — she left because she got an offer from OpenAI that was hard to turn down. We also let one person go about six months ago who wasn't a fit — more of a performance issue than culture."

*What this tells you:*
- Green: Founder distinguishes between voluntary departure and managed exit — doesn't lump them together
- Green: A departure to OpenAI is competitive, not a leadership signal
- Green: Willing to mention the managed exit and frame it accurately
- Neutral: 2 departures in 18 months at 25 people is within normal range

---

## Post-interview read

**Green flags from this session:**
- CTO is honest about eval infrastructure gap (real candor)
- Failure mode answer was specific and self-aware
- Founder gave real numbers on runway and ARR milestone
- Departure explanation was honest and differentiated

**Yellow flags to investigate before offer:**
- Eval infrastructure gap is a real technical risk — if you join, this is likely your most urgent project. Worth asking explicitly: "Is this something you'd expect the person in this role to own?"
- ARR milestone depends on two late-stage deals closing — pipeline concentration risk
- LOIs included in "line-of-sight" — needs verification

**Red flags:** None surfaced in this interview. Absence of red flags is notable.

**Your verdict:** This is a company worth pursuing. The gaps are real but knowable, the leadership is honest, and the technical problems are interesting. The eval infrastructure gap in particular is the kind of problem where you could have clear, measurable impact in the first 90 days.

---

## What the candidate did well

**Prepared specific questions.** Referenced the engineering blog post directly — signals research, enables a real conversation instead of a generic exchange.

**Used follow-ups, not just questions.** "When you say line-of-sight, is that closed or pipeline?" — this is where the real information is. Every good answer has a follow-up.

**Listened for what wasn't said.** The CTO's answer about eval infrastructure was candid; a weaker interviewer might have heard it as a problem. A stronger read is: it's an opportunity, and the CTO's honesty about it is a culture signal.

**Decoded signals in real-time.** Translated answers into green/yellow/red on the spot, not just collected information.

**Didn't ask about perks or growth trajectory.** Both would have dropped the altitude of the conversation and signaled that the candidate was optimizing for the offer, not evaluating the opportunity.
