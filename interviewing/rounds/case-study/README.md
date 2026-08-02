# Case Study Round (live · code test · take-home · Work Trial · presentation/defense)

## What's tested

Bridging theory to a business problem: problem decomposition, metric selection, MVP thinking, trade-off narration, and business framing. Four evaluation dimensions interviewers use:

- **Problem-solving process** — do you break down ambiguity logically and narrate it?
- **Applied ML/LLM knowledge** — can you go beyond theory and propose actionable steps?
- **Business awareness** — do you anchor on outcomes (churn -5%, cost-per-ticket) not models?
- **Communication** — can you explain your thinking clearly and adapt under challenge?

**Process > results.** Interviewers grade how you structure ambiguity and use them as a resource, not whether you land their pet answer. Adapting visibly under challenge scores higher than defending your original design.

## Formats

| Format | Window | Deliverable | Graded hardest on |
|---|---|---|---|
| Live case | 45–75 min | Verbal design + whiteboard | Clarify-first, trade-off narration |
| **Code test** (emerging) | 1h timed | Running code + README | Triage, shipping, API safety |
| Technical test | 1–3h | Running code + README | Correctness against defined criteria |
| **Work Trial** | 3–6h | Production-shaped repo | Production-readiness ≈ feature completeness |
| Presentation/defense | Panel | Deck + defense | Adapting under challenge |

The 1h timed code test is **emerging, not canonical** — evidenced in CoderPad/CodeSignal pilots, not confirmed as a standard round at major AIE employers. Prepare for it as a compression of the take-home, not as a round you should expect.

### Live case (45–75 min)
"Client wants to automate support / detect churn / process documents — design the solution." The FDE version is the loop's highest-weight round (~30%) with the lowest pass rate (~40%) — deliberately ambiguous, and the ambiguity is the test. Starts with clarifying questions; ends with a milestone plan and measurement story.

### Technical test (offline, 1–3h)
A dataset or scenario; deliverable is a notebook, memo, or deck. Graded on scoping discipline (a shipped MVP with a risk register beats an unfinished tour de force), stated assumptions, and clean writeup. Budget 20% of time for the writeup.

### Work Trial (3–6h)
The long end of the offline spectrum. The deliverable is a production-shaped repo, and production-readiness weighs roughly as heavily as feature completeness — tests, error handling, and a README that explains operational limits are graded, not optional polish. See [study-guide.md](study-guide.md) for how test expectation scales with the timebox.

### Presentation/defense
The take-home's second half — present to a panel, then defend: "why this model?", "what breaks at 10× scale?", "what would you do with two more weeks?" Prepare for challenge; adapting visibly scores higher than defending.

## The working template (one page — memorize it)

```
Objective & users
→ Constraints (latency, cost/1K tokens, privacy, budget)
→ Data sources
→ Baseline first
→ MVP pipeline sketch
→ Offline + online eval plan
→ Risks & safety
→ Milestones
```

**For ML cases:** define the business objective as a number ("reduce churn 5%") → data → baseline model → validation plan → risk register.

**For LLM cases:** system-design architecture + RAG-vs-fine-tune decision + cost + hallucination handling + eval. Treat it as a system design problem with a business framing layer on top.

Deep breakdown of each section: [study-guide.md](study-guide.md).

## Prep checklist

- [ ] Rehearse the one-page template until you can write it from memory in 2 minutes.
- [ ] Timebox drills: one Kaggle dataset, 3 hours, full template → writeup. Twice.
- [ ] **Live rounds** — practice the clarify-first reflex: never accept the stated solution ("a chatbot") — interrogate the problem.
- [ ] **Async submissions** — the opposite reflex: state your interpretation, document the assumption, and proceed. Waiting on clarification burns the window; unstated assumptions are what get penalized, not wrong ones.
- [ ] Confirm the AI-tool policy with your recruiter before starting — it varies by track (typically permitted for Applied AI, restricted for Core Infrastructure and Research).
- [ ] ROI arithmetic cold: token math, hours-saved math, error-cost math.
- [ ] Prepare "what went wrong" honesty for defense rounds.
- [ ] For take-homes: state assumptions in the first paragraph; include a "next steps / not done" section — it reads as judgment, not incompleteness.

## Per-role weighting

| AIE | MLE | DS | FDE |
|---|---|---|---|
| ◐ | ◐ | ● | ● |

The FDE signature round; the DS take-home-with-presentation is near-universal (24–48h). AIE/MLE loops fold case elements into system design instead.

## Folder contents

- [study-guide.md](study-guide.md) — template deep breakdown, ML vs LLM adaptation, ROI arithmetic, take-home best practices, defense prep, common mistakes
- [questions.md](questions.md) — 12 questions with what's tested, model answer structure, study refs
- [sources.md](sources.md) — internal guides and external references
- [examples/](examples/) — worked case walkthroughs, split by domain (ML vs AIE), not by format
  - [ml-track/churn-prediction-takehome.md](examples/ml-track/churn-prediction-takehome.md) — technical test: 100K rows churn data, 3-hour timebox
  - [aie-track/retail-support-automation.md](examples/aie-track/retail-support-automation.md) — live case: retailer reducing support costs with AI
  - [aie-track/one-hour-code-test.md](examples/aie-track/one-hour-code-test.md) — code test: 1h timed retrieval build against the 60-minute clock
  - [aie-track/rag-pipeline-defense.md](examples/aie-track/rag-pipeline-defense.md) — defense round: defending a RAG pipeline under challenge
