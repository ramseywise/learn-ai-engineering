# Study Guide — Technical / ML/LLM Breadth Round

## The core method: 60-second + one deeper

Every answer has two modes. Know both before any interview.

**Mode 1: The 60-second answer**
- One crisp definition sentence.
- The mechanism in plain terms (analogy to a PM if needed).
- One concrete example or implication.
- Stop there. Do not pre-load the deeper content — let them ask.

**Mode 2: One level deeper**
- The underlying math or mechanism (just enough, not a lecture).
- The failure mode or edge case the basic answer ignores.
- The trade-off or design decision it creates.
- At most 90 seconds. If you're going longer, you're lecturing, not interviewing.

**The signal is in the transition.** When they say "can you go deeper?" you should have something real to say — not a memorized extension of the first answer, but a genuinely different layer of understanding. That's what separates candidates who passed a course from candidates who built things.

### Practice drill

For each question in `questions.md`:
1. Cover the "one level deeper" column.
2. Answer cold from the 60-second column header only.
3. Uncover and compare. Where did you stop short? Where did you add noise?
4. Repeat until you can produce both layers naturally.

---

## The honest-gap move

When you don't know something well, say so — then redirect.

**Formula**: "My understanding there is fairly surface-level — I know [the basic shape of the thing], but I haven't gone deep on [the specific mechanism]. I'd approach it by [how you'd figure it out]. What I do have solid experience with is [related thing you can speak to]."

**Why it works**:
- Interviewers can tell when you're bluffing. An honest gap with clear meta-awareness reads better than a confident wrong answer.
- The redirect shows intellectual honesty and gives the interviewer something to work with.
- It's memorable — most candidates bluff, so the honest move stands out.

**When to use it**: Any time you'd need to speculate more than one sentence to answer. Not for total unknowns (that's just a gap), but for things you know the shape of but not the depth.

**When NOT to use it**: Don't make it a habit for things you should know for your target role. If you're interviewing for an AIE role and you don't know what attention is, that's a skill gap to close before the interview, not a gap-move situation.

---

## Trade-off pairs master list

These are the most common "compare X and Y" questions. For each: know the key axis (what actually drives the decision) and a one-sentence call.

| Pair | Key axis | Call |
|------|----------|------|
| RAG vs fine-tuning | What's missing: knowledge or behavior? | RAG for knowledge, FT for behavior |
| LoRA vs full fine-tuning | Compute budget and data volume | LoRA unless you have large data and compute |
| Precision vs recall | Cost of false positive vs false negative | Domain-dependent; know your error costs |
| Batch vs streaming inference | Latency requirement vs throughput | Streaming for UX, batch for cost |
| On-prem vs API | Data sensitivity, cost at scale, team ops burden | API until scale or compliance forces on-prem |
| Dense vs sparse retrieval | Semantic similarity vs exact match | Hybrid in production; neither alone |
| Cross-encoder vs bi-encoder | Accuracy vs speed | Bi-encoder for retrieval, cross-encoder for reranking |
| k-NN (exact) vs ANN | Recall vs latency at scale | ANN in production; exact only for small corpora |
| Temperature 0 vs high T | Determinism vs diversity | 0 for reasoning/evals, higher for creative generation |
| CoT vs direct answer | Task complexity | CoT for multi-step; direct for classification |
| Single agent vs multi-agent | Context length + specialization need | Single agent unless task exceeds window or needs parallelism |
| Workflow vs agent | Predictability vs flexibility | Workflow first; agent only where decisions can't be enumerated |
| L1 vs L2 regularization | Sparsity need | L1 for feature selection; L2 for general shrinkage |
| Online vs offline eval | Coverage vs control | Both — offline before deploy, online in production |
| LLM-as-judge vs human eval | Scale vs ground truth quality | LLM-judge for scale, human for calibration |
| Summarization vs sliding window (history) | Context quality vs completeness | Summarization for long sessions; sliding for short |
| Fixed-size chunking vs semantic chunking | Speed vs retrieval quality | Semantic for quality-critical retrieval |
| RLHF vs DPO | Training complexity vs simplicity | DPO unless you need online exploration |
| F1 vs AUC-ROC | Balanced classes vs imbalanced | F1 for balanced, PR-AUC for imbalanced |
| Top-p vs top-k sampling | Adaptive cutoff vs fixed cutoff | Top-p more robust; top-k simpler to reason about |
| Prompt injection defense: structural vs filter | Completeness vs ease | Structural separation first; filter as supplement |
| Zero-shot vs few-shot prompting | Example availability vs token cost | Few-shot for hard tasks; zero-shot + CoT often competitive |
| k=5 vs k=10 cross-validation | Speed vs variance reduction | k=5 for large datasets, k=10 for small |

**Drill method**: Make these into flashcards (pair on front, key axis + call on back). The goal is instant recall of the axis, not memorization of the call — the call is context-dependent, the axis is what you actually need to reason in the interview.

---

## Per-role topic weighting

Know your role's depth requirements. AIE and FDE share most topics; MLE adds classical depth; DS folds this into the stats screen.

### AIE (AI Engineer)
Priority order: LLM fundamentals → RAG → Agents → Context & cost → Evals → Security → Classical ML (sanity check only)
- Own the full transformer/LLM stack: attention, tokenization, RLHF/DPO, context windows
- RAG pipeline end-to-end: chunking, retrieval, reranking, eval
- Agent architecture: loop engineering, tool design, multi-agent patterns
- Context engineering and token economics (you build the systems that run this)
- Classical ML: just enough to not get stumped on bias-variance or precision-recall

### MLE (ML Engineer)
Priority order: Classical ML (deep) → LLM fundamentals → Evals → RAG → Agents → Context & cost → Security
- Classical ML is first-class: regularization, cross-validation, bias-variance, optimization
- LLM fundamentals at depth: training dynamics, fine-tuning, RLHF
- Evals: rigorous quantitative eval frameworks, not just "LLM-as-judge"
- RAG and agents: working knowledge, not deep expertise
- Security: awareness level

### DS (Data Scientist)
This round often folds into the stats/SQL screen. Weight:
Priority order: Classical ML → Evals → LLM fundamentals (awareness) → RAG (awareness)
- Deep on statistical inference, A/B testing, bias-variance
- Evals: the eval framework is close to statistical methodology
- LLM/RAG: demonstrate awareness of the paradigm, not deep building experience

### FDE (Full-stack/Deployment Engineer)
Priority order: Context & cost → Security → Agents → RAG → LLM fundamentals → Evals → Classical ML
- Cost and latency are first-class concerns: token economics, caching, batching
- Security: prompt injection, trust boundaries, PII handling
- Agent and RAG system architecture: operational concerns (failure modes, monitoring)
- LLM fundamentals: enough to understand what you're deploying

---

## Domain priority order (by role)

| Domain | AIE | MLE | DS | FDE |
|--------|-----|-----|----|-----|
| LLM fundamentals | 1 | 2 | 3 | 4 |
| RAG | 2 | 4 | 5 | 3 |
| Agents | 3 | 5 | 6 | 2 |
| Evals | 4 | 3 | 2 | 5 |
| Security | 5 | 6 | 7 | 1 |
| Context & cost | 6 | 7 | 8 | 1 |
| Classical ML | 7 | 1 | 1 | 7 |

Lower number = higher priority for prep time.

---

## Flashcard method

**What goes on cards**: trade-off pairs (above) + domain definitions (one per concept)

**Card format**:
- Front: the question the interviewer would ask ("RAG or fine-tuning?")
- Back: the key axis + 60-second call. Not the full answer — the decision logic.

**Drill schedule**:
- Day 1-3: Build cards for your top-priority domains (role-dependent).
- Day 4-7: Daily 15-minute drill, all cards. Flag anything you hesitate on.
- Week 2+: Drill flagged cards 2x/day; unflagged cards every other day.
- 48h before interview: Full deck, no skips.

**Spaced repetition**: Any card you got wrong goes back to the top of the pile immediately. Cards you've gotten right 3 times in a row move to the "refresh" pile (every 3 days).

**Peer rapid-fire**: The best drill is a partner asking questions and timing your 60-second answer. Do this at least twice per week in the two weeks before interview. The pressure of real-time delivery is different from self-review.

---

## Claim audit checklist

Everything on your resume is in scope. For each item on your resume that touches ML/LLM:

1. **What you built**: be specific — not "built a RAG system" but "built a RAG pipeline using LangChain + Pinecone with hybrid search and BGE reranking, serving X queries/day."
2. **Why you made the key decisions**: chunking strategy, model choice, eval approach. Know the trade-offs you actually navigated.
3. **What didn't work**: the honest failure story is often the most interesting part. What did you try that didn't work and why?
4. **The metrics**: what did you measure, what did you hit? Even rough numbers ("reduced hallucination rate by ~30% on our golden set") are better than vague claims.
5. **The follow-up question**: for every claim, assume they'll ask "can you go deeper?" Prepare one more layer.

**Audit process**: Go line by line through your resume. For each claim, try to answer those 5 questions cold. Anything you can't answer is a preparation gap — either go deeper on it or soften the claim on the resume.

---

## Practice plan

### Week 1 (breadth pass)
- Day 1: Read all domain sections of `questions.md`. Don't drill — just read.
- Day 2: Build flashcards for your top 2 domains (role-priority order above).
- Day 3-4: First drill pass — all 30 questions, self-timed. Flag what you hesitated on.
- Day 5: Peer rapid-fire session (15 min, 10 questions). Debrief immediately after.
- Day 6-7: Fill gaps from the drill — read the study guide sections for flagged questions.

### Week 2 (depth pass)
- Day 1-2: Drill flagged questions. Add the "one level deeper" layer to your card backs.
- Day 3: Trade-off pairs only — 20-minute focused drill.
- Day 4: Full practice interview (mock, 30 min, timed). Ask someone to follow up on 3-5 answers.
- Day 5-6: Claim audit (above). Tighten resume language for any gaps found.
- Day 7: Rest. Light card review only.

### Interview week
- Daily: 10-minute flashcard warm-up, trade-off pairs.
- Day before: Full deck, one pass. No new material.
- Day of: Trade-off pairs only (5 min). Trust the preparation.

---

## Anti-patterns

**Memorized definitions without depth**
The trap: you study the 60-second answers and stop. The interviewer asks one follow-up and you freeze. Fix: always prepare both layers. If you can't explain the mechanism behind the definition, you don't know it yet.

**Bluffing on gaps**
The tell: long confident answer with no specific details. Interviewers have heard every version of this. The honest-gap move (above) is almost always the better play — it demonstrates self-awareness, which is a signal that transfers to on-the-job performance.

**No trade-off reasoning**
The trap: you state facts without engaging the "why this over that" question. Every technical question in this round has a trade-off buried in it. Proactively surface it: "This is the standard approach, but it breaks down when [X] — in that case you'd [Y]."

**Answering the question you prepared instead of the one they asked**
Common when you're nervous and pattern-match to a similar question. Slow down. Paraphrase the question back if needed. Specific questions deserve specific answers — general knowledge dumps signal low situational awareness.

**Length creep**
More words is not more depth. 3 minutes on a question that should take 60 seconds loses the interviewer's attention and leaves no time for follow-up. The 60-second target is real. Time yourself in practice.

**Skipping classical ML**
If you're an AIE who thinks classical ML doesn't apply anymore — you're wrong, and interviewers will test it. Precision-recall, bias-variance, cross-validation: know them at the level described in `questions.md`. They're the sanity-check layer.
