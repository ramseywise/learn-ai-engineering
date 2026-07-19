# Case Study Round (live · take-home · presentation/defense)

## What's tested

Bridging theory to a business problem: problem decomposition, metric selection, MVP thinking, trade-off narration, and business framing. Four evaluation dimensions interviewers use:

- **Problem-solving process** — do you break down ambiguity logically and narrate it?
- **Applied ML/LLM knowledge** — can you go beyond theory and propose actionable steps?
- **Business awareness** — do you anchor on outcomes (churn -5%, cost-per-ticket) not models?
- **Communication** — can you explain your thinking clearly and adapt under challenge?

**Process > results.** Interviewers grade how you structure ambiguity and use them as a resource, not whether you land their pet answer. Adapting visibly under challenge scores higher than defending your original design.

## Three formats

### Live case (45–75 min)
"Client wants to automate support / detect churn / process documents — design the solution." The FDE version is the loop's highest-weight round (~30%) with the lowest pass rate (~40%) — deliberately ambiguous, and the ambiguity is the test. Starts with clarifying questions; ends with a milestone plan and measurement story.

### Take-home (offline, 3h–48h)
A dataset or scenario; deliverable is a notebook, memo, or deck. Graded on scoping discipline (a shipped MVP with a risk register beats an unfinished tour de force), stated assumptions, and clean writeup. Budget 20% of time for the writeup.

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
- [ ] Practice the clarify-first reflex: never accept the stated solution ("a chatbot") — interrogate the problem.
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
- [examples/](examples/) — worked case walkthroughs
  - [retail-support-automation.md](examples/retail-support-automation.md) — live case: retailer reducing support costs with AI
  - [churn-prediction-takehome.md](examples/churn-prediction-takehome.md) — take-home: 100K rows churn data, 3-hour timebox
  - [rag-pipeline-defense.md](examples/rag-pipeline-defense.md) — defense round: defending a RAG pipeline under challenge
