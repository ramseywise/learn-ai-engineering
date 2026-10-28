---
origin: video-transcript
sources:
  - YouTube breakdown of Andrej Karpathy's AISN 2026 talk + interview clips (secondary; no primary transcript of the talk available)
confidence: medium
cleaned: 2026-08-05
---
# The Karpathy Method — spec, verifier, environment

> "You can outsource your thinking, but you can't outsource your understanding." — Karpathy

Secondary-source distillation of Karpathy's AISN 2026 framing, as relayed by a YouTube
breakdown. Confidence is `medium` because the layering ("three layers") is the
YouTuber's packaging; the direct Karpathy material is the quotes and the
animals-vs-ghosts model. Cross-check against primary sources when the talk transcript
lands.

---

## The motivating gap

The car-wash test: *"The car wash is 50 m away — should I drive or walk?"* Frontier
models say walk, because distance is measurable and the-car-must-be-at-the-car-wash is
contextual. **AI is brilliant at what can be measured and blind to context it was never
given a signal for.** Every layer below is a mechanism for delivering your context in a
form the model can act on.

---

## Layer 1 — the spec

A spec is how your understanding reaches the model. Karpathy on plan mode: *"I don't
even like the plan mode… you have to work with your agent to design a spec that is very
detailed."* Plan mode isn't wrong — it's too high-level. Three disciplines:

1. **Uncover the goal, not the task.** "Create an end-of-month report" is a task; the
   goal is the decision the report drives. The goal is the one thing the model can never
   infer — extract it deliberately (e.g. *"interview me to identify the goal of this
   project"*).
2. **Agile specking, not waterfall.** Tight scope, clear checkpoint, review, adjust,
   repeat. People default to waterfall with agents — hand over everything at once —
   because delegation feels efficient. Bias the agent toward *smaller,
   compartmentalized specs*.
3. **Precision + your own brain.** Every assumption the model makes is a drift
   opportunity. When the model drafts the spec, force explicit sign-off: *"make me
   verify key decisions explicitly."*

---

## Layer 2 — the verifier

### The mental model: animals vs ghosts

Humans ("animals") have intrinsic motivators — threaten or plead and behavior changes.
Models are *"statistical simulation circuits"* — Karpathy's ghosts, the video's **robot
librarian**: it answers only from the books in its library and doesn't know which books
are missing, so it confidently improvises. Social pressure ("make this better") is not a
lever. **The lever is verification** — that's playing within the rules the system
actually follows.

### Three verification moves

| Move | Mechanism |
|---|---|
| **Criteria before work** | Define "good" precisely *before* generation — "three sections, each ends with a recommendation," not "make it look good" |
| **Second librarian** | A different model as critic — a different library grading the first library's answer (e.g. Codex plugin inside a Claude Code session for complex builds) |
| **External signal** | Connect the system that holds ground truth — deploy target for "did it deploy," historical reports for format conformance |

Boris Cherny (Claude Code creator), as quoted: **a feedback loop 2–3×'s final quality.**
This layer is the depth treatment of [notes/05-verification-loops.md](notes/05-verification-loops.md);
the "criteria before work" move is eval-first, and "second librarian" is asymmetric QA
by another name.

---

## Layer 3 — the environment

The workshop the other two layers live in: spec = blueprint on the wall, verifier = QA
station by the door, environment = the workshop itself. Most people rebuild it from
scratch every session. Four components:

1. **CLAUDE.md as the operating contract** — repo layout, skill routing, knowledge
   architecture ("where to look for what"), standing rules. *"It's your world and AI is
   living in it — not the other way around."*
2. **LLM knowledge base** — a folder system of your own curated material, structured so
   the model knows where information lives. *"Your data is your moat."*
3. **Skills for anything repeated** — a handbook per recurring task. *"The best way to
   find a leak in a hose is to run water through it"* — usage exposes where a skill
   needs fixing; the system compounds.
4. **Rules vs requests.** A CLAUDE.md line ("don't touch /important") is a request the
   model can ignore; a **pre-tool-use hook** that blocks the write is a rule it cannot.
   Bucket everything into **always-do** (autopilot), **ask-first** (double-check), and
   **never-do** (hook-enforced, not prompt-enforced). Enforcement level should match
   the cost of getting it wrong.

---

## The one thing

The three layers all route through the same bottleneck: *your* understanding of the
goal, of what good looks like, of what must never happen. Thinking is outsourceable;
understanding is not — it's the input the layers exist to transmit.

---

→ Related: [notes/05-verification-loops.md](notes/05-verification-loops.md) (verifier layer in depth),
[notes/01-what-a-harness-is.md](notes/01-what-a-harness-is.md) (environment as harness).
