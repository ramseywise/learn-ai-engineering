# Customer Simulation — Study Guide

## The six habits — deep dive

### 1. Discovery before prescription

The most common failure in this round: arriving with a solution and defending it. The interviewer plays someone with a problem, not a requirements doc. If you lead with your solution, you've failed before they've finished their first sentence.

**What it looks like in practice**: Your first two or three turns should be questions. Not rhetorical questions that set up your answer — genuine questions that could surface information that changes what you say next.

**Practice exercise**: Take any scenario from `questions.md`. Set a rule: you cannot make a claim or recommendation for the first two minutes. You can only ask questions. Record yourself. Notice how long it takes before the urge to explain becomes overwhelming.

**The test**: After two minutes of questions, does your eventual recommendation differ from what you would have said immediately? If yes — you discovered something. If no — your questions weren't real discovery.

---

### 2. Listen and mirror

Mirroring is not parroting. It's restating the emotional content of what they said in their words — briefly — before responding. It signals you heard the weight of it, not just the text.

**Formula**: "[Restate the core problem in their language]. [Brief acknowledgment of what that means for them]. [Then your question or response]."

Example:
- They say: "The pilot numbers look bad and renewal is next month."
- Wrong: "I understand. Here's our plan…"
- Right: "The renewal is next month and the numbers aren't there yet. That's a hard position. Before I share what I'm thinking — what does your VP need to see to feel confident continuing?"

**Practice exercise**: Listen to a podcast interview. After each guest answer, pause and write a one-sentence mirror of what they said. It should capture the feeling, not just the fact.

---

### 3. Translate, don't dumb down

Dumbing down is condescending and loses technical credibility. Translation is altitude-matching: you choose the level of abstraction that maps to how your audience makes decisions, not how you build systems.

**Altitude guide**:
- C-suite / board: outcomes and risk. Business impact, dollars, time, competitive position.
- VP / Director: trade-offs and timelines. What decisions does this force, what does each option cost.
- Manager / champion: implementation and adoption. What does this change about how their team works.
- Technical team: architecture and constraints. What actually connects to what, what breaks under load.

**Analogy construction**:
1. Find the familiar concept (something they already understand and trust).
2. Map the key relationship (not all the details — just the structural parallel).
3. Name the limit ("this analogy breaks down when…") to show you're not hiding complexity.

Example for fine-tuning vs. RAG: "Fine-tuning is like accent training — it changes how the model speaks. RAG is like giving it a reference library. If you want your model to sound like your brand, fine-tune. If you want it to know your latest product specs, use RAG. Most companies need the library, not the accent."

**Practice exercise**: Pick a technical concept from the LLM fundamentals guide. Explain it in 90 seconds to three different audiences (COO, customer success manager, ML engineer). Record each. Notice where you reach for jargon under time pressure.

---

### 4. Bad-news delivery framework

**Structure: Problem → Ownership → Options → Recommendation → Next step**

1. **Problem** — State it plainly in the first sentence. Don't bury it in context.
2. **Ownership** — What was within your control. Don't over-own (false responsibility) or under-own (deflection). Be specific.
3. **Options** — Two or three paths, each with honest trade-offs. No sandbagging, no padding.
4. **Recommendation** — Name one. "I recommend X because Y." Fence-sitting here is a red flag.
5. **Next step** — Concrete, dated, owner named.

**Common failure**: Rushing to options without owning. The customer hears "options" as deflection if you haven't demonstrated you understand what went wrong and accepted your part of it.

**The pressure test**: The interviewer will push back on your recommendation. Hold it if you believe it. Adjust it if they surface new information. The difference matters — one is strength, the other is responsiveness.

**Practice exercise**: Write out bad-news delivery for a model quality miss (accuracy target was 85%, you're at 71%) and a timeline slip (6-week delay). Read each out loud. Time how long before you say "I recommend." It should be under 2 minutes.

---

### 5. Scope management language

Saying "no" to scope is a social failure in a customer relationship. The goal is to say yes to the need and surface the trade-off.

**The core move**: "Yes — and here's what it displaces. Which matters more to you?"

This reframes the conversation from your limitation to their priority. You're not blocking them; you're asking them to choose.

**Variants**:
- Feature creep: "We can add that. It would push [X] out by [N] weeks or cost [Y]. Which milestone matters most to you right now?"
- Competitor comparison: "Tell me which parts of that demo were most relevant — I want to make sure we're solving the right problem, not just matching a feature list."
- "Just one more thing": "Happy to scope that. Let me make sure I understand what's driving it so we can figure out the fastest path."

**What you never say**:
- "That's out of scope." (Hard boundary, no discovery, no path)
- "That's not what you asked for." (Technically correct, relationship-damaging)
- "We can try to fit it in." (False commitment)

**Practice exercise**: Take the scope-creep question from `questions.md`. Practice three different ways to redirect the demand to a priority conversation without using the word "no."

---

### 6. Next step always

Every conversation without a concrete next step is a relationship in decay. The next step must be:
- **Specific** — not "we'll follow up" but "I'll send the revised metrics framework"
- **Dated** — not "soon" but "by Thursday"
- **Owned** — one person's name on it

The next step is also your way of controlling the conversation exit. If you end without one, you've left the relationship in their hands.

**Formula**: "Here's what I'm taking away from today: [summary of commitments]. I'll have [specific deliverable] to you by [date]. Does that work, and is there anything I'm missing?"

---

## Discovery question frameworks

Discovery questions by industry. These aren't scripts — they're prompts to surface the constraints that matter most in each context.

### Retail / e-commerce

- "Walk me through what a customer complaint looks like from intake to resolution today."
- "Where does your team spend the most time on tasks that feel repetitive?"
- "What does a bad week look like in terms of customer experience metrics?"
- "Is there a season or event where errors cost you the most?"

### Financial services / fintech

- "What does your compliance team need to know about any system that touches customer data?"
- "How are decisions documented for audit purposes today?"
- "What's the tolerance for false positives vs. false negatives in [specific decision]?"
- "Who else needs to sign off before a new tool goes into a production workflow?"

### Healthcare

- "Which workflows touch patient data, and what's your current data classification for those?"
- "What does your IRB or compliance team need to see before any AI system touches clinical data?"
- "How do clinicians currently validate AI outputs before acting on them?"
- "What would happen if the system was wrong 1% of the time on [specific decision]?"

### Nonprofit / mission-driven

- "What does success look like for the people you're serving, not just the organization?"
- "Where are your volunteers or staff spending time that feels disconnected from the mission?"
- "What do funders ask about when it comes to AI use?"
- "What's the risk tolerance if the system makes a mistake in front of a community member?"

### Technical audience (internal teams)

- "What does your current stack look like for this problem?"
- "Where are the seams that cause the most friction — data handoffs, deployment, monitoring?"
- "What's the on-call load for the current system?"
- "What would you build differently if you were starting from scratch?"

---

## Technical translation techniques

### Altitude matching checklist

Before explaining anything technical, ask yourself:
1. What decision is this person making?
2. What do they need to understand to make it well?
3. What can I leave out without misleading them?

Then explain only what answers those three questions.

### Analogy construction template

1. **Target concept**: [the thing you're explaining]
2. **Familiar analog**: [something they already understand]
3. **The parallel**: [how the structure is the same]
4. **The limit**: [where the analogy breaks down — say this out loud]

Practiced analogies for common AI concepts:

| Concept | Analogy |
|---------|---------|
| RAG | A reference library the model looks things up in before answering |
| Fine-tuning | Accent/style training — changes how it speaks, not what it knows |
| Embeddings | A filing system that groups similar ideas near each other |
| Hallucination | Confident autocomplete — it fills in what sounds right, not what is right |
| Context window | Working memory — it can only hold so much at once before earlier things drop out |
| Model evaluation | Spell-check for correctness: it can catch some errors but misses others |
| Staged rollout | A new employee starting on low-stakes tasks before handling critical ones |

---

## ROI arithmetic practice

The goal is to do this live on the customer's numbers, not yours. Have the framework ready; populate it with what they tell you.

### Token math (API cost)

- Baseline: how many documents/requests per day?
- Average tokens per request (input + output)?
- Cost per 1K tokens (current model)?
- Monthly cost = (requests/day × 30 × avg_tokens / 1000) × cost_per_1k

Example: 10,000 requests/day × 1,500 tokens avg = 15M tokens/day × 30 = 450M tokens/month. At $0.003/1K = $1,350/month.

### Hours-saved calculation

- Task: [specific workflow being automated or assisted]
- Current time per task: [X minutes]
- Volume: [N tasks per week]
- Expected time reduction: [Y%]
- Hours saved per week = (N × X × Y%) / 60
- Annual value = hours_saved × 52 × [fully-loaded hourly rate]

### Error-cost calculation

- Error type: [false positive / false negative in a specific decision]
- Current error rate: [X%]
- Volume: [N decisions per month]
- Cost per error: [dollar value — could be rework, churn, compliance, reputation]
- Current monthly cost = N × X% × cost_per_error
- Expected reduction: [Y%]
- Monthly savings = current_monthly_cost × Y%

**Drill**: Practice with these numbers:
- A 200-person customer service team spends 30% of their time on FAQ responses. Average salary $55K fully-loaded. What's the annual cost of that 30%?
- A lending company processes 5,000 applications/month. Manual review takes 20 min each. An AI system could handle 80% in 2 min each. What's the time savings?

---

## Emotional intelligence signals

### Mirroring (see Habit 2)

Reflect the emotional content before the factual content.

### Acknowledging frustration

The formula: "I can see why that's frustrating." + silence. Don't immediately follow with "but." The silence is doing work — it lets them feel heard before you move.

What not to say:
- "I understand how you feel." (Claimed empathy, not demonstrated)
- "Let me explain why that happened." (Immediately defensive)
- "Actually, the metrics show…" (Factually correct, emotionally deaf)

### Reading the room in real-time

Signals the interviewer might give that you should respond to, not override:
- Repeating the same concern in different words → they don't feel heard yet; mirror harder before moving on
- Short yes/no answers → they've disengaged; ask what's on their mind
- Escalating emotional tone → stop solving, start listening
- "That's fine" with flat affect → it's not fine; "It doesn't sound like it is — what's actually going on?"

### Pacing

You don't have to fill silence. Pausing 2–3 seconds after they speak before responding signals you're actually processing rather than queuing. Practice it — it's harder than it sounds in a role-play under pressure.

---

## Practice plan

### Week 1 — Habits foundation (15 min/day)

- Days 1–2: Read this guide fully. Annotate the six habits with your natural failure modes.
- Days 3–5: Pick two scenarios from `questions.md`. Practice out loud — no notes. Record yourself.
- Days 6–7: Review recordings. Identify: where did you skip discovery? Where did you use jargon? Did every conversation end with a next step?

### Week 2 — Scenario coverage (20 min/day)

- Work through all twelve scenarios in `questions.md`, two per day.
- For each: spend 5 min preparing the discovery questions, 10 min doing the scenario out loud, 5 min self-critique against the habit list.
- Focus on scenarios in your weak category (discovery vs. bad news vs. translation — they're different skills).

### Week 3 — Adversarial practice (30 min sessions)

- Find a practice partner (peer, AI role-play, or record yourself playing both roles).
- Have them improvise off your responses — don't give them a script.
- Debrief on: first response instinct, jargon frequency, whether you ended with a next step.
- Run two sessions: one easy scenario, one hostile scenario.

### Recording yourself

The habits you rely on under pressure are visible only in playback, not in the moment. Record at least three sessions. Listen for:
- First word out of your mouth (solution vs. question)
- Jargon density under time pressure
- Tone shift when challenged
- Whether you paused before responding

---

## Anti-patterns

These are the habits that fail — common enough to name explicitly.

| Anti-pattern | What it looks like | Why it fails |
|-------------|-------------------|--------------|
| Defending | "Actually, the model performed within spec." | Signals you prioritize being right over solving their problem |
| Jargon-dumping | "We can use RAG with a vector store over your embedding space" | Leaves them lost; signals you're not reading the room |
| Overpromising | "We can absolutely add that feature in the next sprint." | Destroys trust the moment you can't deliver |
| Solution-first | "Here's what I recommend." [before any questions] | You don't know their problem yet |
| No follow-up | Ending with "great, thanks" and no concrete next step | Leaves relationship in their hands; signals low ownership |
| False empathy | "I totally understand." [then immediately pivoting] | Feels scripted; they noticed you didn't actually listen |
| Blame transfer | "The customer's data quality was the issue." | Even if true, leads with deflection |
| Hedging the recommendation | "It could go either way, it depends…" | You're there to help them decide; sitting on the fence isn't help |
