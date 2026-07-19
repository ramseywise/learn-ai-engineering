# Worked Example: Bad News Delivery

**Scenario**: Six-month pilot with a financial services company. The pilot was supposed to demonstrate 85% accuracy on document review. You're at 71%. The contract renewal is in 30 days. You're opening a call with the VP of Operations.

---

**Interviewer (VP of Operations)**: "So — walk me through where we are."

---

**Response**: "I want to be direct with you. The pilot accuracy is at 71%, and our target was 85%. That's a meaningful gap, and I'm not going to walk you into a renewal conversation without being honest about it upfront."

> **Annotation**: **Don't bury the lead.** The instinct is to open with what went well, then slide into the miss. That's spin, and experienced stakeholders recognize it immediately. Stating the number plainly in the first sentence signals you're not going to manage them — you're going to level with them. "I'm not going to walk you into a renewal conversation without being honest about it" demonstrates you're prioritizing the relationship over the deal.

---

**Interviewer**: "71%. That's significantly below what we agreed to. What happened?"

---

**Response**: "There are two things I want to separate. The first is what's within our control: the model configuration we deployed wasn't tuned for the subset of documents that have mixed-language fields — about 20% of your corpus. That's on us to have caught in scoping. The second is outside our control: the document format changed mid-pilot when your team migrated vendors, and we weren't notified until four weeks in. Both of those contributed, and I want to be clear about which is which before we talk about what to do next."

> **Annotation**: **Ownership with specificity** — not "there were some challenges" and not "it was actually your fault." This response names exactly what was in your control (missed scoping on mixed-language docs) and exactly what was outside it (undisclosed format change), and separates them explicitly. Claiming ownership for the former while accurately describing the latter is not deflection — it's honest accounting. The setup for "what to do next" is intentional: don't pivot to solutions before ownership is established.

---

**Interviewer**: "The renewal is in 30 days. My CFO is going to ask me if this is worth continuing."

---

**Response**: "That's the right question to put on the table. Before I answer it, I want to understand what's driving it from your side — is the concern the 71% number itself, or is there a downstream decision or process that was depending on hitting 85%?"

> **Annotation**: **Discovery before prescription** — the VP said the renewal is in 30 days and the CFO will ask if it's worth it. The instinct is to immediately make the case for continuing. Don't. Ask what's actually at stake for them. Sometimes the miss matters because it affects a specific downstream workflow; sometimes the number matters because it was used to justify headcount reduction that didn't happen. The answer determines what recovery looks like.

---

**Interviewer**: "We told our compliance team they could reduce manual review by 40% if accuracy hit 85%. At 71%, we don't have the confidence level to reduce review."

---

**Response**: "Okay — that's the real constraint. It's not 85% as an abstract target; it's the confidence threshold your compliance team needs to pull back manual review. That's actually useful to know, because it changes what we're solving for. Can I ask: is that 85% a hard line from your compliance team, or is it a proxy for a different confidence requirement they haven't fully specified?"

> **Annotation**: **Surface the real constraint** — the 85% target turned out to be a proxy for compliance confidence, not an end in itself. This is critical information: if the compliance team would accept 82% with a different error profile (e.g., lower false negatives on a specific doc type), then the path to renewal looks different than "hit 85% overall." The follow-up question — "is 85% a hard line or a proxy?" — opens up solution space without dismissing their requirement.

---

**Interviewer**: "It's pretty firm. They ran the numbers on 85%."

---

**Response**: "Alright. Then here's what I want to offer you — three paths, and I'll tell you what I recommend. First: we extend the pilot 60 days with targeted retraining focused on the mixed-language subset. Based on what I'm seeing in the error analysis, I think we can get to 83–86% in that window. That's a commitment I'm comfortable making, not a guess. Second: we scope a reduced deployment — apply the model only to the document types where we're already at or above 85%, which is about 65% of your volume, and keep manual review on the rest. Third: we wind down cleanly, with full data handover and documentation of what we learned. I'm not going to pretend that's not on the table."

> **Annotation**: **Three options, named honestly** — including the wind-down option. Many candidates won't name option three because they're afraid of losing the deal. But not naming it reads as desperation, and it also leaves the customer to infer it alone. Naming it demonstrates confidence and signals you're not just fighting for revenue. The recommendation hasn't come yet — present options before advocating.

---

**Interviewer**: "You said you're comfortable committing to 83–86%. Why should I believe that?"

---

**Response**: "Fair pushback. Here's the basis: the error analysis shows that 68% of misclassifications come from the mixed-language subset, and we know exactly why — the tokenizer we're using treats certain field formats as noise. That's a solvable problem with targeted retraining, not a fundamental model limitation. I've seen similar fixes move accuracy 8–12 points in comparable corpora. I'm not committing to a number I can't explain the mechanism for."

> **Annotation**: **Defend with evidence, not assertion** — when challenged on a commitment, don't say "trust me" or capitulate. Name the specific mechanism (tokenizer treating mixed-language fields as noise), the specific data point (68% of misclassifications from one subset), and the comparable evidence (8–12 point improvements in similar cases). This is the difference between a credible commitment and a sales promise.

---

**Interviewer**: "And if you don't hit it in 60 days?"

---

**Response**: "If we're not at 83% at day 45, I'll tell you. We won't wait until day 60 to surface it. And if we can't get there, I'd rather help you scope the reduced deployment option or wind down cleanly than renew a contract that isn't working. A 30-day renewal that fails in month two is worse for both of us than a clean close now."

> **Annotation**: **Early-warning commitment** — naming a mid-point check (day 45) before the deadline demonstrates accountability and takes the ambiguity out of the risk. "I'd rather help you wind down cleanly than renew a contract that isn't working" is the highest-trust thing you can say. It's counterintuitive — you're offering to not close the deal — but it signals your incentives are aligned with their success, not your revenue.

---

**Interviewer**: "What do you recommend?"

---

**Response**: "The 60-day extension with targeted retraining. The mechanism is understood, the scope is bounded, and you'd have a day-45 checkpoint to make the renewal decision with current data rather than six-month-old data. I'd also recommend getting your compliance team to define the confidence criteria more precisely — is it overall accuracy, or is it false negative rate on specific document types? That specification will make the 60-day evaluation cleaner for both of us."

> **Annotation**: **Name one recommendation** — not "it depends on your priorities." The recommendation is specific (60-day extension), includes a mechanism for de-risking it (day-45 checkpoint), and adds a constructive ask that makes their decision easier (compliance team specifying the success criteria). The ask is in their interest — it makes the outcome clearer — which makes it easy to agree to.

---

**Close**: "Here's what I'd like to do: I'll send you a one-pager by end of week — the three options with the timelines and costs for each, and the specific retraining plan for option one. Then we can loop in your compliance lead before the renewal conversation so they're not hearing this second-hand. Does Thursday work for a quick follow-up call?"

> **Annotation**: **Concrete next steps** — not "I'll follow up." A one-pager by end of week (specific deliverable, dated), a named next meeting (Thursday, specific), and a stakeholder to include (compliance lead). Pulling in compliance proactively, rather than waiting for the VP to relay the conversation, demonstrates confidence and ensures the decision-maker has accurate information.

---

## What made this work

1. **Led with the number** — no burying, no softening sequence. Said "71%" in the first sentence.
2. **Separated owned vs. external causes** — named both specifically, without using external causes as deflection from owned ones.
3. **Discovery before options** — asked what was actually at stake (the compliance confidence threshold) before presenting recovery paths.
4. **Three options including wind-down** — naming the hard option signals alignment with their success over your revenue.
5. **Defended commitments with mechanism** — when challenged on the 83–86% estimate, named the specific cause and fix, not a general assurance.
6. **Early-warning commitment** — day-45 checkpoint turned an opaque 60-day gamble into a structured decision point.
7. **One named recommendation** — didn't hedge; said "I recommend the extension" and gave the reason.
8. **Compliance lead included in follow-up** — proactively pulling in the real decision-maker signals you understand how this organization works.
