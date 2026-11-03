# Sources — Case Study Round

## Internal guides

| Guide | Path | What it covers for this round |
|-------|------|-------------------------------|
| Product & business | [scoping an AI product](../../../../generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product.md) | Problem framing, clarify-first reflex, ROI arithmetic (token math, hours-saved, error-cost), stakeholder communication |
| System design | [system-design method](../system-design-round/study-guide.md) | LLM case architecture, §3 architecture + RAG-vs-fine-tune, cost, hallucination handling, trade-off narration formula |
| ML foundations | [classical ML](../../../../data-science/01-classical-ml/README.md) | ML cases — baseline-first discipline, model selection (tabular SOTA is boosting), AUROC-vs-accuracy, SHAP, Ng's two case-study quizzes |
| RAG | [RAG pillar](../../../../generative-ai/02-rag-retrieval/README.md) | LLM case retrieval layer — chunking, embedding, reranking, what-if chains (poor retrieval, index growth, chunk truncation) |
| Agents | [harness pillar](../../../../ai-engineering/03-harness-engineering/README.md) | Agent system design cases — orchestration, tool design, state management, safety |
| Evals & observability | [eval pillar](../../../../generative-ai/08-eval/README.md) | Offline + online eval plans, hallucination monitoring, metrics beyond accuracy |
| Code review round | [../code-review-round/README.md](../code-review-round/README.md) | Your code-test submission is read as a PR by a senior engineer — that round's consequence-ranked reading order is the grader's lens |

## Internal notes


### Code test / Work Trial material

The README format table, the study guide's clock, dial and taxonomy, and `examples/aie-track/one-hour-code-test.md` come from format research kept outside this repo, so nothing here cites it.

Evidence on tests pulls two ways: one account lists a test suite under what *not* to build in a 60-minute window, and another calls a missing suite the top Work Trial rejection reason. The study guide resolves this as a dial that scales with the timebox rather than adopting either verbatim.

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
