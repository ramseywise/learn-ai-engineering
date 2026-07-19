# Customer Simulation — Scenario Question Bank

Twelve scenario prompts. For each: the setup, what's being scored, the habit sequence that works, and the failure modes.

---

## 1. Incident — Wrong Output to a Customer

**The scenario**: You're the COO. Your AI gave our customer wrong information yesterday. Go.

**What they're testing**: Crisis empathy, ownership without deflection, immediate containment thinking, trust repair instinct.

**Strong response structure**:
1. Acknowledge the impact immediately — not the technical cause. "That's a serious situation. Before anything else — what happened to the customer as a result?"
2. Listen fully before explaining anything.
3. Own your side clearly: what failed, what you know and don't know yet.
4. Containment first: what's happening right now to prevent recurrence.
5. Investigation timeline: concrete, not "we'll look into it."
6. Follow-up: "I'll have a root-cause summary to you by [date]. What else does your team need from me right now?"

**Red flags**:
- Jumping to technical explanation before acknowledging the customer harm
- Deflecting ("it depends on how the prompt was written")
- Vague commitments ("we'll investigate")
- No follow-up date or owner

**Study refs**: `sources.md` → security guide (incident response protocol); `examples/incident-response.md`

---

## 2. Scope Creep — Competitor Feature Demand

**The scenario**: We want it to do everything your competitor's demo showed.

**What they're testing**: Scope discipline, discovery under pressure, boundary-setting without antagonism, prioritization skill.

**Strong response structure**:
1. Explore before reacting: "Tell me which parts of that demo resonated most — what problem were you hoping it would solve?"
2. Identify the two or three underlying needs — features are usually proxies.
3. Map what you can and can't deliver: "We can do X and Y in the current scope. Z would require [trade-off]. Which matters more to you?"
4. Never say "no" directly — say "yes, and here's what it displaces."
5. Concrete next step: "Let me document what we heard today and we can align on priority in our planning call Thursday."

**Red flags**:
- Promising everything ("we can absolutely do that")
- Defensive comparison ("our product actually does more than theirs")
- Dismissing the request without discovery
- No follow-up

**Study refs**: `study-guide.md` → Scope management language; `examples/scope-negotiation.md`

---

## 3. Technical Misunderstanding — Fine-Tuning Question

**The scenario**: Why can't we just fine-tune on all our data?

**What they're testing**: Technical translation without condescension, discovery of real concern beneath the ask, analogy construction.

**Strong response structure**:
1. Validate the instinct: "That's a reasonable first impulse — it makes sense that more data feels like more accuracy."
2. Ask what's driving the question: "Is there a specific behavior you're trying to change, or a capability you feel is missing?"
3. Translate the actual constraint: fine-tuning changes style/format, not knowledge; RAG is usually the right tool for domain knowledge. Use an analogy: "Fine-tuning is like accent training — it changes how the model speaks. RAG is like giving it a reference library to look things up."
4. Recommend: "For your use case, I'd suggest [X] because [Y]."
5. Check comprehension without condescending: "Does that match what you were hoping to achieve?"

**Red flags**:
- Technical dump ("well, fine-tuning updates the weights and RAG uses retrieval-augmented generation with embeddings…")
- Not discovering the underlying concern
- Leaving them uncertain about what you recommend

**Study refs**: `sources.md` → llm-fundamentals §3 (adaptation ladder); `study-guide.md` → Technical translation techniques

---

## 4. Bad News — Pilot Metrics Miss with Renewal Pressure

**The scenario**: The pilot metrics look bad and the renewal is next month.

**What they're testing**: Honesty under commercial pressure, bad-news delivery discipline, recovery framing, commitment calibration.

**Strong response structure**:
1. State the problem plainly: "The metrics missed target. I won't minimize that."
2. Own your side: what you know was within your control vs. what was outside it.
3. Diagnose before prescribing: "Can you walk me through which numbers matter most for the renewal decision?"
4. Bring options with trade-offs: a path to improve before renewal, a revised scope, an extension, a structured wind-down — present two or three, with a recommendation.
5. Don't overpromise: "I can commit to [X] by [date]. I'm not in a position to guarantee [Y] by the renewal."
6. Next step: "Let's set a call with your VP this week so we're aligned before the renewal review."

**Red flags**:
- Spin ("but look at these other metrics that are positive")
- Overpromising to save the deal
- No ownership of the miss
- Leaving the renewal outcome vague

**Study refs**: `study-guide.md` → Bad-news delivery framework; `examples/bad-news-delivery.md`

---

## 5. Constraint — IT Says No External APIs

**The scenario**: Our IT team says no external APIs. Ever.

**What they're testing**: Discovery of the real constraint (security? compliance? data residency?), solution architecture flexibility, ability to work with the constraint rather than against the person.

**Strong response structure**:
1. Discover the underlying concern: "That's a firm constraint — do you know what's driving it? Data residency, compliance requirements, security posture?"
2. Validate it: "That's a legitimate concern, especially in [industry]."
3. Map deployment options honestly: VPC deployment, on-prem, private cloud — with trade-offs in cost, latency, maintenance.
4. Identify what you need to move forward: "The right architecture depends on whether this is a data-residency requirement or a network security policy — can I get 30 minutes with your IT lead to understand the specifics?"
5. Next step with a concrete path.

**Red flags**:
- Arguing with the constraint ("but our APIs are secure")
- Assuming you know what's driving IT's position
- Proposing a solution before understanding the requirement

**Study refs**: `sources.md` → system-design guide §7 (on-prem vs API); `study-guide.md` → Discovery question frameworks

---

## 6. Frustration — "Why Is This Taking So Long?"

**The scenario**: Non-technical exec: "Why is this taking so long?"

**What they're testing**: Empathy first, translation to business terms (not engineering terms), expectation reset, relationship repair.

**Strong response structure**:
1. Acknowledge the frustration directly: "That's a fair question, and I understand this isn't where you expected to be at this point."
2. Translate the delay to business terms: not "we had infrastructure blockers" — "we hit a dependency on [X] that we didn't scope for originally, and that added [N] weeks."
3. Clarify what they care about: "Is the concern the timeline itself, or is there a business event this is tied to?"
4. Reframe what's done and what's left: concrete percentages or milestones, not vague assurances.
5. Commitment: "Here's what I can promise by [date], and here's what I need from your team to hit it."

**Red flags**:
- Engineering explanation ("we had to refactor the pipeline")
- Defending the team without acknowledging impact
- No concrete revised estimate
- Leaving the exec without a next milestone

**Study refs**: `study-guide.md` → Emotional intelligence signals; ROI arithmetic practice

---

## 7. Onboarding — Skeptical Technical Team

**The scenario**: You're meeting the customer's ML engineers for the first time. They've been told to "adopt your solution." They don't want to be there.

**What they're testing**: Peer respect vs. sales posture, discovery of technical concerns, credibility establishment without overreach.

**Strong response structure**:
1. Don't open with a pitch. "I'd rather start by understanding how you're already solving this — what does your current stack look like?"
2. Ask about pain: "What's the part of this workflow that causes the most friction?"
3. Find genuine overlap: acknowledge where your solution adds vs. where they've solved it better.
4. Be honest about trade-offs: "We're stronger on X, but what you've built for Y is more tailored than what we offer."
5. Establish a collaboration frame: "I'd like to figure out where we can reduce your load, not replace what's already working."
6. Next step: concrete technical sync or sandbox access, dated.

**Red flags**:
- Pitching features at engineers who didn't choose to be there
- Claiming superiority without knowing their setup
- Ignoring their existing work
- Leaving without a specific technical next step

**Study refs**: `study-guide.md` → Discovery question frameworks (technical audience variant)

---

## 8. Board Presentation — Explaining AI Value

**The scenario**: The board wants a 5-minute briefing on why the AI initiative is worth continuing. You have one slide.

**What they're testing**: Altitude calibration (board = outcome language, not feature language), ROI framing, concision, handling hostile questions.

**Strong response structure**:
1. Lead with business outcome, not technical capability: "We're reducing [X] by [Y%] / saving [N] hours per week / catching [Z] errors that previously cost $[amount]."
2. State the current status honestly: "We're [milestone]. The next milestone is [X] by [date]."
3. Frame risk clearly: "The main risk is [X]. We're mitigating it by [Y]."
4. Ask for the decision you need, if any.
5. Handle hostile questions with curiosity: "Can you say more about what's driving that concern?" before answering.

**Red flags**:
- Technical features on a board slide ("our RAG pipeline retrieves context from…")
- Hedging on outcomes
- Not knowing the ROI numbers
- Getting defensive at a hostile question

**Study refs**: `study-guide.md` → ROI arithmetic practice; Technical translation techniques (altitude matching)

---

## 9. Data Privacy Concern

**The scenario**: A customer raises mid-engagement: "We just realized your system processes PII. Our legal team wants to understand how."

**What they're testing**: Composure, accurate scoping of data handling, ability to not overcommit on compliance, appropriate escalation instinct.

**Strong response structure**:
1. Acknowledge the concern immediately: "This is exactly the kind of question we want on the table — let's make sure we get it right."
2. Clarify what data actually flows: be precise, not defensive. What's sent to the model, what's logged, what's retained.
3. Be honest about what you know and don't know in the room: "I can confirm [X] right now. For the specific retention policy your legal team needs, I want to get our data compliance lead on a call rather than give you an answer I'm not certain of."
4. Timeline: "I can have the right person on a call within 48 hours and a written summary within a week."
5. Don't promise compliance certifications you haven't verified.

**Red flags**:
- Minimizing: "Oh, we don't really store that"
- Overcommitting: "Yes, we're fully HIPAA compliant" without verification
- Defensive posture
- No escalation path or timeline

**Study refs**: `sources.md` → security guide (data handling, compliance scenarios)

---

## 10. Timeline Expectation Reset

**The scenario**: Two months in, you need to tell the customer the go-live is slipping by six weeks.

**What they're testing**: Bad-news delivery discipline, discovery of downstream impact, commitment calibration, trust maintenance.

**Strong response structure**:
1. Don't bury the lead: "I need to share that our go-live is moving from [date] to [date] — six weeks later than planned."
2. Own the cause clearly: what was in your control, what wasn't.
3. Discover impact before prescribing: "I want to understand what this affects on your side — is there a business event or dependency tied to that date?"
4. Options with trade-offs: accelerated scope (what gets cut), additional resource (cost/time), phased launch (partial go-live on original date).
5. Recommendation: name one.
6. Commitment: what you'll have confirmed by when.

**Red flags**:
- Burying the news in qualifications
- Overpromising recovery ("we can probably make it up")
- Not discovering downstream impact
- Vague next steps

**Study refs**: `examples/bad-news-delivery.md`; `study-guide.md` → Bad-news delivery framework

---

## 11. In-House Threat — "We're Thinking of Building This Ourselves"

**The scenario**: The customer says: "Our CTO thinks we should just build this in-house. Why should we keep working with you?"

**What they're testing**: Non-defensive response to existential challenge, honest capability comparison, discovery of what's really driving the question.

**Strong response structure**:
1. Don't defend — discover: "That's a significant decision. What's driving the conversation — cost, control, capability concerns?"
2. Listen for the real driver: often it's dissatisfaction with something specific (speed, fit, price) that's being expressed as "build vs. buy."
3. Engage the build analysis honestly: "Building well takes [realistic timeline and cost]. The teams I've seen succeed at it invested [X]. Is that scope your CTO is planning for?"
4. Acknowledge where build makes sense: if their use case is truly differentiated and they have ML capability, say so.
5. Identify what you offer that's hard to build: speed to value, maintained infrastructure, ongoing model improvements.
6. Leave with a question, not a pitch: "What would need to be true for continuing with us to be the obvious choice?"

**Red flags**:
- Getting defensive or selling harder
- Dismissing their build capability
- Not discovering what's really driving the question
- No concrete comparison on timeline/cost

**Study refs**: `study-guide.md` → Discovery question frameworks; ROI arithmetic practice

---

## 12. Hostile New Contact — Champion Left

**The scenario**: Your champion left. The new contact opens with: "I wasn't part of this decision. I'm not convinced this is the right tool for us."

**What they're testing**: Relationship reset instinct, discovery before justification, patience with a cold start, credibility under skepticism.

**Strong response structure**:
1. Acknowledge the situation: "That's a fair starting point. You're inheriting a decision you didn't make."
2. Don't defend the past — start fresh: "I'd rather earn your confidence than assume it transfers. Can we start with what you're trying to accomplish?"
3. Discovery-first: understand their priorities, what success looks like to them, what concerns they have.
4. Be honest about the engagement history: what's worked, what hasn't.
5. Offer a concrete way to demonstrate value: a short scope evaluation, a specific success metric, a check-in cadence they control.
6. Let them set the pace: "What would make you comfortable continuing to the next milestone?"

**Red flags**:
- Defending the previous champion's decision
- Overwhelming them with success metrics from before they arrived
- Assuming continuity of relationship
- No offer to re-earn trust concretely

**Study refs**: `study-guide.md` → Emotional intelligence signals; Discovery question frameworks
