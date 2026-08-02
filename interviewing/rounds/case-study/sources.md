# Sources — Case Study Round

## Internal guides

| Guide | Path | What it covers for this round |
|-------|------|-------------------------------|
| Product & business | [../../guides/10-product-delivery/interview-guide.md](../../guides/10-product-delivery/interview-guide.md) | Problem framing, clarify-first reflex, ROI arithmetic (token math, hours-saved, error-cost), stakeholder communication |
| System design | [../../guides/9-system-design/interview-guide.md](../../guides/9-system-design/interview-guide.md) | LLM case architecture, §3 architecture + RAG-vs-fine-tune, cost, hallucination handling, trade-off narration formula |
| ML foundations | [../../guides/1-foundations/interview-guide.md](../../guides/1-foundations/interview-guide.md) | ML cases — baseline-first discipline, model selection (tabular SOTA is boosting), AUROC-vs-accuracy, SHAP, Ng's two case-study quizzes |
| RAG | [../../guides/3-rag/interview-guide.md](../../guides/3-rag/interview-guide.md) | LLM case retrieval layer — chunking, embedding, reranking, what-if chains (poor retrieval, index growth, chunk truncation) |
| Agents | [../../guides/4-agents/interview-guide.md](../../guides/4-agents/interview-guide.md) | Agent system design cases — orchestration, tool design, state management, safety |
| Evals & observability | [../../guides/6-evals-observability/interview-guide.md](../../guides/6-evals-observability/interview-guide.md) | Offline + online eval plans, hallucination monitoring, metrics beyond accuracy |
| Code review round | [../code-review-round/README.md](../code-review-round/README.md) | Your code-test submission is read as a PR by a senior engineer — that round's consequence-ranked reading order is the grader's lens |

## Internal notes

- [../../notes/case-interview.md](../../notes/case-interview.md) — raw source material: evaluation dimensions, RAG what-if chain, defense round tips, consulting-style loop patterns

### Code test / Work Trial provenance

The code-test and Work Trial material (README format table, study-guide clock/dial/taxonomy, `examples/aie-track/one-hour-code-test.md`) derives from three research passes dated 2026-08-01, in `.claude/docs/research/`:

- `2026-08-01_code-test_format-and-flaws.md` — format evidence, hidden-flaw taxonomy, the 60-minute clock, pragmatism/defensibility rubrics
- `2026-08-01_code-test_openai-work-trial.md` — OpenAI Work Trial vs technical test; test-rigour dial, PR-review lens, observability weighting, async ambiguity protocol
- `2026-08-01_code-test_tooling-audit.md` — starter-kit tooling audit; **not a source for the current round docs**, tracked separately

Note the two-source tension on tests: the first lists a test suite under what *not* to build in a 60-minute window; the second calls a missing suite the top Work Trial rejection reason. The study-guide resolves this as a dial that scales with the timebox rather than adopting either verbatim.

## External references

### Case interview frameworks
- **Case in Point** (Cosentino) — consulting-style problem decomposition framework; the structure transfers well to technical AI cases even though the domain differs
- **CaseStudyPrep.AI** — AI/ML-specific case interview practice with structured feedback
- **Interview Query** — ML and AI system design case practice problems; realistic scenarios with model solutions

### LLM system design
- Anthropic and OpenAI engineering blogs — production case studies on RAG, cost optimization, and failure modes
- LangChain documentation — patterns for chains, agents, and retrieval; useful for citing concrete implementation choices in LLM cases

### ML fundamentals
- Kaggle datasets — practice take-home material; pick a classification or forecasting problem and timebox yourself to 3 hours
- Andrew Ng's ML Specialization case-study quizzes (Coursera) — brief structured exercises on problem framing and metric selection
- "Why not deep learning?" reference: tabular data SOTA benchmarks (XGBoost / LightGBM vs. neural nets on structured data)

### ROI frameworks
- Token math baseline: OpenAI/Anthropic pricing pages — cost/1K tokens by model tier; used to build the "does this pencil out?" calculation
- Hours-saved arithmetic: $X/hour × hours_saved/week × 52 = annual value
- Error-cost math: error_rate × volume × cost_per_error = risk exposure that justifies the build
