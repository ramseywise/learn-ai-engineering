# Worked Example: Scope Negotiation

**Scenario**: You're in a quarterly check-in with the customer's VP of Product. Three months into a document classification project. Things are going well — until:

---

**Interviewer (VP of Product)**: "We want it to do everything your competitor's demo showed. Their system summarizes documents, drafts responses, and routes tickets automatically. We need all of that."

---

**Response**: "I saw that demo too — there's a lot in there. Before I react to the full list, I want to make sure we're solving the right problem for you. Which part of what you saw would have the most impact on your team right now?"

> **Annotation**: **Discovery before prescription** — the instinct is to say "we can do some of that" or to defend what you've built. Neither is right. The VP just listed three capabilities; they probably care most about one or two. Ask which one. This also buys time and information, and it reframes the conversation from "why don't you have this" to "what do you actually need."

---

**Interviewer**: "The auto-routing is the big one. Our support team is drowning. They're manually sorting tickets into queues and it's taking hours every morning."

---

**Response**: "Hours every morning — that's a real cost. How many tickets are coming in, roughly, and how many queues are they routing to?"

> **Annotation**: Mirror ("hours every morning — that's a real cost") then go immediately into discovery. The numbers matter: 200 tickets into 5 queues is a different problem than 5,000 tickets into 40 queues. The answer will determine whether this is a configuration to your existing classifier or a new capability entirely. Don't commit to anything until you know.

---

**Interviewer**: "About 800 tickets a day, six queues. It's two people, three hours each, every morning."

---

**Response**: "Okay, so six person-hours a day, 800 tickets, six queues. That's roughly 130 hours a month of manual routing. That's the number I'd want to use when we're talking about what this is worth. Here's where I am honestly: the document classifier we've built shares a lot of underlying structure with routing — you're assigning a label to a unit of text either way. The gap is in the training data. Do you have historical tickets with the correct queue labels attached?"

> **Annotation**: Two things happening here: **ROI arithmetic done live** on their numbers (130 hours/month = real dollar value at their team's rate), and **honest scoping** that leads with what you can build on rather than what you can't do. "Here's where I am honestly" signals you're not going to oversell. The question at the end is both discovery and a genuine prerequisite — you can't build a routing classifier without labeled data.

---

**Interviewer**: "We have two years of closed tickets. I don't know if they're labeled."

---

**Response**: "Two years is a good foundation if they have queue labels. Can you check with your ops team? If the labels are there, routing is definitely buildable — probably a 4-to-6-week addition once we have the data confirmed. If they're not labeled, we'd need to either label a sample or define rules manually, which changes the timeline significantly. I'd rather know that now than commit to a date I can't keep."

> **Annotation**: **Honest scoping with branching options** — not "yes we can do that" (oversell) and not "that's not in scope" (hard no). Two clear paths, with a timeline for one of them and a caveat for the other. "I'd rather know that now than commit to a date I can't keep" is the key line — it signals you prioritize accuracy over winning the moment.

---

**Interviewer**: "What about the summarization and response drafting? Why can't we just add all of it?"

---

**Response**: "We could. Here's what it displaces: we're currently on track for the classification accuracy milestone at the end of Q3. Adding summarization and drafting in parallel means we either extend that timeline by 6 to 8 weeks or we split the team's attention and risk both. Which matters more to you — the Q3 accuracy milestone, or getting the full suite sooner and pushing that milestone out?"

> **Annotation**: **"Yes, and here's what it displaces"** — this is the core scope management move. Not "no, that's out of scope." The question at the end is genuine: some customers will say "push the milestone, we need the suite." That's a valid answer. You're surfacing the trade-off and letting them decide, which is both honest and gives them agency.

---

**Interviewer**: "The Q3 milestone is tied to our board review. We can't move it."

---

**Response**: "Then here's what I'd recommend: we stay heads-down on classification accuracy through Q3. In parallel, I'll scope out what routing would take, assuming the labeled data exists, and have a proposal to you by [date two weeks out] so you can plan it into Q4. Summarization and drafting we can evaluate after the board review when you know what the next priority cycle looks like. Does that work?"

> **Annotation**: **Concrete recommendation** — not "it depends." The plan: stay the course on Q3, scope routing in parallel (non-blocking), defer the rest until after a natural decision point. The follow-up date is specific. The question at the end checks alignment rather than assuming it. This closes the conversation with a clear next step and no broken commitments.

---

**Interviewer**: "That sounds reasonable. But I want the full scope in the contract before we close Q4."

---

**Response**: "That's a reasonable thing to want locked in. I'll include routing and the summarization/drafting scope in the proposal I send in two weeks — with timelines that depend on the data check and a clear note on which dependencies are on your side. You'll have everything you need to take it into a contract conversation. Who on your side would be involved in that?"

> **Annotation**: "That's a reasonable thing to want" — don't fight reasonable requests. The response commits to include the scope in writing (not in the verbal call), names the dependency clearly so there's no ambiguity later, and ends by pulling in the next stakeholder who'll need to be involved. This keeps the conversation moving without overclaiming.

---

## What made this work

1. **Discovery first** — asked which feature mattered most before engaging with the full list. Got the real answer (routing) in the second exchange.
2. **Live ROI arithmetic** — translated "hours every morning" to "130 hours/month" on the spot. Made the value of the ask concrete.
3. **Honest branching** — "if the labels exist, 4–6 weeks; if not, different timeline" named the uncertainty without hiding it.
4. **"Yes, and here's what it displaces"** — never said no. Surfaced the trade-off and let the customer decide.
5. **Concrete recommendation** — when they named the constraint (Q3 milestone), gave a specific plan, not another question.
6. **Written follow-up** — committed to a scoping proposal in two weeks with all dependencies documented. No verbal-only commitments.
