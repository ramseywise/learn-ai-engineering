# Worked STAR Example: Ambiguity Rescued

**Prompt**: "Tell me about a time you had to deliver with incomplete requirements."

**Story category**: Ambiguous scope — assumption documentation, reversible build first, iterate on feedback.

---

## The story

### Situation
> I was building an internal RAG-based Q&A tool for a nonprofit client with a volunteer
> cohort of 40+ researchers. Mid-project, the product owner left and wasn't replaced for
> 6 weeks. Requirements we'd been iterating on verbally were now undocumented, and two
> stakeholders who stepped in had conflicting views of what "a good answer" meant —
> one wanted citation-heavy summaries, the other wanted short direct answers.

**Annotation**: The ambiguity is specific and structural, not just "things were unclear." Two
competing stakeholders with genuinely different definitions of success — that's a real
ambiguity, not a process gap you could have solved by asking better questions. The 6-week
vacuum is the precipitating event; the conflicting successor stakeholders are the actual
challenge.

---

### Task
> I was the sole engineer on the project and responsible for the delivery. The client
> deadline was fixed — the tool needed to be in pilot with 10 researchers in 5 weeks.

**Annotation**: "Sole engineer" and "fixed deadline" establish the constraint clearly. You
couldn't wait for clarity and you couldn't hand off the decision. The task owns the
stakes.

---

### Action
> My first move was to write down all the things I didn't know, organized by how much
> they would cost to change after delivery: things I'd need to get right the first time
> (underlying retrieval architecture, data ingestion pipeline), and things I could change
> quickly after a pilot (response format, citation density, output length).
>
> I sent that list to both stakeholders as a "what I'm treating as settled vs. still open"
> doc — not a questions document, but an explicit statement of my working assumptions. I
> asked them to flag anything in the "settled" column they disagreed with. One stakeholder
> came back with two corrections; the other didn't respond.
>
> On the open questions — citation vs. brevity — I didn't try to resolve the conflict before
> building. I built a single interface with a response-style toggle: "detailed" (citation-heavy)
> vs. "concise" (direct answer, one citation max). The toggle cost me half a day. It meant
> neither stakeholder had to lose.
>
> I documented the toggle decision in the handoff doc with a note: "One of these styles will
> probably win in the pilot. Let researchers choose for two weeks, then measure which they use
> and what their satisfaction scores are."

**Annotation**: The Action section has four distinct moves:

1. **Assumptions audit by reversibility** — distinguishing what must be right from the start
   vs. what can be changed later. This is the core ambiguity-tolerance skill. You're not just
   making assumptions; you're evaluating which assumptions are safe to get wrong.

2. **Assumptions doc sent proactively** — not a questions document (which puts the burden on
   stakeholders to think through a spec they haven't written) but a statement of working
   assumptions. Stakeholders review a claim, which is lower-friction than answering an open
   question. The one who didn't respond? You have a timestamp on the assumption.

3. **Reversible resolution of the conflict** — a toggle is the key move here. You didn't
   force a decision you weren't empowered to make; you built something that let the evidence
   decide. This is "build the reversible version" in practice.

4. **Built-in feedback mechanism** — you handed off the decision to the pilot data, with
   a timeline. This extends the ambiguity tolerance into the post-launch phase and frames
   it as a feature, not a gap.

**Common mistakes at Action**:
- "I asked stakeholders to clarify." That's not a decision, it's a handoff.
- "I picked one direction and went with it." Valid if you explain *why that direction* and
  what you would have done if you were wrong.
- "I escalated to leadership." Sometimes right, but it signals you couldn't operate in
  ambiguity yourself.

---

### Result
> We hit the pilot deadline. The pilot ran with 11 researchers over 3 weeks. 8 of 11 defaulted
> to "concise" mode after the first week. The two stakeholders agreed to default the tool
> to concise with detailed available on demand. That decision took 20 minutes in the pilot
> debrief — it would have taken weeks of unresolved debate before we built anything.
>
> The client team lead mentioned in the debrief that the assumptions doc had been unusually
> useful — they'd never been handed one by an external engineer before and it surfaced two
> miscommunications they hadn't caught.

**Annotation**: The Result has three things working:

1. **The number**: "8 of 11 defaulted to concise mode" — specific, not "most researchers
   preferred one style." Numbers make results real.
2. **The comparison**: "That decision took 20 minutes in the pilot debrief — it would have
   taken weeks of unresolved debate before we built anything." This is the payoff of the
   reversible build. Naming the counterfactual makes the strategy legible.
3. **The feedback on the assumptions doc**: The client calling it out specifically validates
   that your process artifact had real value, not just your code.

---

### Reflection
> Since then, I start every project with an explicit "settled vs. open" doc and send it
> before any build work starts. And when I hit a genuine stakeholder conflict I can't
> resolve with data, my default is to ask: "Can I build something that lets the pilot
> decide this?" — rather than trying to force a decision from people who don't have
> enough information to make it yet.

**Annotation**: Two behaviors. The first is a process artifact (the settled/open doc, sent
before build starts). The second is a decision heuristic — "Can I build something that lets
the pilot decide this?" — that you can apply to the next ambiguous situation.

Note the precision in the second behavior: "when I can't resolve with data." This shows you
haven't over-generalized — you still try to resolve conflicts before building workarounds.
The workaround is the fallback when resolution isn't available, not the first move.

---

## What this story is doing (structural summary)

| Component | Signal it sends |
|-----------|----------------|
| Situation (structural ambiguity) | Not "unclear requirements" — competing stakeholders, a specific gap, a real constraint |
| Task (sole owner, fixed deadline) | No one else to pass the decision to |
| Action (reversibility audit) | You thought about which assumptions were safe to get wrong |
| Action (assumptions doc) | You made your assumptions legible and reviewable, not just implicit |
| Action (reversible resolution) | You built something that let evidence settle a decision you couldn't force |
| Action (built-in feedback loop) | The ambiguity management extends past launch |
| Result (number) | 8 of 11 — specific user behavior data, not "most users preferred" |
| Result (counterfactual) | 20 min vs. weeks of debate — shows the value of the reversible approach |
| Reflection (two specific behaviors) | A process artifact + a decision heuristic, both immediately applicable |

---

## Calibration: startup vs. enterprise angle

This story can be re-angled depending on the audience:

**Startup emphasis**: Lead with the speed. "I hit the deadline" is the headline. The toggle
move is clever because it didn't slow you down. The assumptions doc is fast to produce and
prevents rework. Keep Situation and Task tight, expand on the "move fast with safe assumptions"
logic in Action.

**Enterprise emphasis**: Lead with the stakeholder management. The "settled vs. open doc sent
to both stakeholders" is the headline move — you navigated a conflict without escalating and
without forcing a decision on people who weren't ready. The pilot-decides framing is about
building trust with skeptical stakeholders, not about speed.

**FDE/consulting emphasis**: The assumptions doc is the key artifact — this is what good
consulting discipline looks like, making your working model legible to the client. The
client's comment in the debrief ("we'd never been handed one by an external engineer before")
is the signal the interviewer wants to hear.
