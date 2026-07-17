# Case Study (live · take-home · presentation/defense)

## What's tested
Bridging theory to a business problem: problem decomposition, metric selection, MVP
thinking, trade-off narration, and business framing (notes: case-interview — evaluation
dimensions: problem-solving process, applied ML knowledge, business awareness,
communication). **Process > results**: interviewers grade how you structure ambiguity and
use them as a resource, not whether you land their pet answer.

## Format & trends
- **Live case** (45–75 min): "Client wants to automate support / detect churn / process
  documents — design the solution." The FDE version is the loop's highest-weight round
  (~30%) with the lowest pass rate (~40%, research F4) — deliberately ambiguous, and the
  ambiguity *is* the test.
- **Take-home (offline)**: 3h–48h; a dataset or scenario, deliverable = notebook/memo/
  deck. Graded on scoping discipline (a shipped MVP with a risk register beats an
  unfinished tour de force), stated assumptions, and clean writeup.
- **Presentation/defense**: the take-home's second half — present to a panel, then
  defend: "why this model?", "what breaks at 10× scale?", "what would you do with two
  more weeks?" Prepare for challenge; adapting visibly scores higher than defending.

## The working template (one page, memorize it)
Objective & users → constraints (latency, cost/1K tokens, privacy, budget) → data
sources → baseline first → MVP pipeline sketch → offline + online eval plan → risks &
safety → milestones. (From notes: the candidates who pass narrate milestones and why
AUROC-over-accuracy, not code.)

For ML cases: define the business objective as a number ("reduce churn 5%") → data →
baseline model → validation plan → risk register. For LLM cases: the
[system-design guide](../guides/9-system-design/interview-guide.md) §3 architecture + RAG-vs-fine-tune,
cost, hallucination handling, eval ([rag](../guides/3-rag/interview-guide.md),
[evals](../guides/6-evals-observability/interview-guide.md)).

## Prep checklist
- [ ] Rehearse the one-page template until you can write it from memory in 2 minutes.
- [ ] Timebox drills: one Kaggle dataset, 3 hours, full template → writeup. Twice.
- [ ] Practice the clarify-first reflex: never accept the stated solution ("a chatbot")
  — interrogate the problem ([product-business guide](../guides/10-product-delivery/interview-guide.md) §1).
- [ ] ROI arithmetic cold: token math, hours-saved math, error-cost math
  (product-business §2).
- [ ] Prepare "what went wrong" honesty for defense rounds — consulting-style loops ask
  for failures and adaptation explicitly (notes: case-interview).
- [ ] For take-homes: budget 20% of time for the writeup; state assumptions in the first
  paragraph; include a "next steps / not done" section — it reads as judgment, not
  incompleteness.

## Question bank
- "A retailer wants to reduce support costs with AI — walk me through it." — template
  top-to-bottom; deflection rate × cost-per-ticket as the value math; phased rollout.
- "Here's 100K rows of churn data — what do you do in 3 hours?" — EDA (leakage check!),
  baseline logistic, one strong model, calibration, top-3 drivers, honest validation.
- "Your take-home model gets challenged: why not deep learning?" — sample size, tabular
  SOTA is boosting ([ml-foundations](../guides/1-foundations/interview-guide.md) §7), interpretability
  requirement; concede the conditions under which you'd switch.
- "The client's data turns out to be much messier than the brief said." — the ambiguity
  test: triage data quality, renegotiate scope against the objective, ship the reduced
  MVP — narrate the re-plan out loud.
- "What if retrieval quality is poor / chunks truncate the answer / docs grow 10×?" —
  the RAG what-if chain (notes: case-interview) — thresholds, chunking revisit,
  index/rebuild plan ([rag guide](../guides/3-rag/interview-guide.md)).

## Per-role weighting
| AIE | MLE | DS | FDE |
|---|---|---|---|
| ◐ | ◐ | ● | ● |

The FDE signature round (with [customer-simulation](customer-simulation.md)); the DS
take-home-with-presentation is near-universal (24–48h, research F4). AIE/MLE loops fold
case elements into system design instead.

## Links
- Study guides: [product-business](../guides/10-product-delivery/interview-guide.md) (framing + ROI), [system-design](../guides/9-system-design/interview-guide.md) (LLM cases), [ml-foundations](../guides/1-foundations/interview-guide.md) (ML cases — incl. Ng's two case-study quizzes as practice)
- Notes: [case-interview.md](../notes/case-interview.md); research F4 in `.claude/docs/plans/2026-07-17-interview-kb-consolidation.md`
