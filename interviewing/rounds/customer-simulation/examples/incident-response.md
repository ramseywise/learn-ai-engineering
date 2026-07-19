# Worked Example: Incident Response

**Scenario**: You're opening a call with a customer COO. Before you can say hello:

---

**Interviewer (COO)**: "Your AI gave our customer wrong information yesterday. Go."

---

**Response**: "That's a serious situation. Before I say anything else — what happened to your customer as a result of that information?"

> **Annotation**: The instinct is to explain. Resist it. The first move is discovery of impact, not defense of system. "Before I say anything else" signals that you're orienting to them, not to your own exposure. The question is genuine — the answer will shape everything you say next.

---

**Interviewer**: "They made a pricing decision based on it. Now they want a credit and they're threatening to escalate to the press."

---

**Response**: "Okay. A customer made a financial decision based on what the system returned, and now they're at risk of escalating publicly. That's a trust problem, not just a technical one. What do you know so far about what the system actually returned?"

> **Annotation**: Mirror before pivoting. "A customer made a financial decision… that's a trust problem, not just a technical one" reflects the weight of what they said in their language. Then a diagnostic question — you need information before you can help. Don't assume you know what happened.

---

**Interviewer**: "It gave them a price that was 30% lower than the actual rate. We don't know why yet."

---

**Response**: "Got it. So the immediate problem is a customer who acted on bad information and is now financially exposed. Here's what I'd want to do in the next 24 hours: First — what's your team doing right now to make the customer whole? That needs to happen today regardless of what the technical root cause is. Second — I want to pull the session logs immediately to see exactly what was returned and why. I can have that analysis back to you by end of business tomorrow. Do you have someone on your side who should be on that call?"

> **Annotation**: This is where the structure shows: **containment first, then investigation, then timeline**. "Make the customer whole… regardless of the technical root cause" demonstrates that you understand trust repair comes before technical resolution. The concrete 24-hour timeline and named deliverable (session log analysis) show ownership. The question at the end pulls them into the solution rather than leaving it fully on your shoulders.

---

**Interviewer**: "What caused this? How can I be sure it won't happen again?"

---

**Response**: "I don't know the cause yet — I won't guess at it before I've seen the logs. What I can tell you is that I'll have a root-cause analysis to you by Thursday, and I'll be honest with you about what it shows whether or not it's favorable to us. On the prevention question: I won't make that promise until I know what broke. What I can commit to is that the fix will be proportionate to the actual failure mode, not a surface-level patch."

> **Annotation**: "I don't know yet — I won't guess" is one of the highest-trust things you can say in a crisis. False confidence is worse than uncertainty. "I'll be honest with you about what it shows whether or not it's favorable to us" is the sentence that repairs trust — it signals your loyalty is to the truth, not to your own position. Refusing to promise prevention before you know the cause is honest; many candidates overpromise here and destroy credibility.

---

**Interviewer**: "My CEO is asking me what to tell the customer. What do I say?"

---

**Response**: "Right now, tell them this: you've escalated it directly, you take full responsibility for the error and its impact, and you'll have a remediation proposal — including how you're making them whole — to them by [date]. Don't get into the technical explanation yet. The customer doesn't need to understand why the system failed; they need to know you're owning the consequences. I'll have the technical picture for you by Thursday, and you can decide then how much to share."

> **Annotation**: This demonstrates **altitude calibration** — you're writing the COO's talking points for a non-technical customer, not explaining the technical failure. "The customer doesn't need to understand why the system failed; they need to know you're owning the consequences" is the key insight. Separating the customer communication from the technical investigation is practical and trust-building.

---

**Interviewer**: "Okay. What happens if the logs show this was our fault — something we configured wrong?"

---

**Response**: "Then the logs will say that and we'll tell you. That changes the remediation path — it's more of a configuration review and training issue than a model reliability issue. It also changes the conversation with your customer. But either way, the customer made a decision based on information they got from our system while working with us, and we both have a stake in making that right."

> **Annotation**: "Either way… we both have a stake in making that right" is the right ending. It holds shared accountability without deflecting your ownership, and it reframes the scenario from adversarial (who's at fault) to collaborative (how do we fix it). The conditional response — "it changes the path" — shows you're genuinely processing the new information rather than defending a predetermined answer.

---

**Close**: "Here's where I am: I'll pull the session logs today and have a root-cause summary to you by Thursday end of business. Tomorrow morning, can we do a quick 15-minute call so I can hear what your customer support team is seeing from the customer's side? That'll help me prioritize what to surface first."

> **Annotation**: Concrete, dated, multi-step next steps. "Can we do a quick 15-minute call" is a specific ask that keeps you in control of the timeline and signals you're not going to disappear while the investigation runs. The framing ("help me prioritize what to surface first") centers the customer's experience rather than your investigation process.

---

## What made this work

1. **Discovery before defense** — every response started by asking what they knew or needed, not by explaining.
2. **Mirroring** — "a trust problem, not just a technical one" / "a customer who acted on bad information" reflected the weight of the situation back before pivoting.
3. **Honest uncertainty** — "I don't know yet, I won't guess" held the line against overpromising.
4. **Altitude calibration** — wrote the COO's customer communication in customer terms, not technical terms.
5. **Concrete next steps** — every response ended with a named deliverable, dated, with an owner.
6. **No blame** — never implied the customer or the COO had done something wrong; never deflected your own accountability.
