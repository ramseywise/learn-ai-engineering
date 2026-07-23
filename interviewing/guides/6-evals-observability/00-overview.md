# Pillar 6 — Evals & Observability

How you know an AI system works — and keeps working. Graders, golden sets, LLM-as-judge,
regression vs capability testing, tracing, drift. The pillar interviewers use to separate
people who've shipped from people who've demoed: "how did you measure it?" has to have a
real answer.

## Learning path

1. **The taxonomy** — [eval-harness.md](../../../ai-engineering/06-eval/eval-harness.md) (from Anthropic's
   eval article) + librarian's *Anthropic Eval Taxonomy* page: unit/trajectory/e2e tiers,
   capability vs regression harnesses.
2. **Formal methodology** — *AI Engineering* chs 3–4 (Evaluation Methodology, Evaluate AI
   Systems — `ai-engineering/readings/ai_engineering/ai engineer/`): the most systematic written
   treatment.
3. **RAG-specific metrics** — RAGAS/ARES from [pillar 3](../3-rag/00-overview.md);
   faithfulness vs answer relevance vs context precision.
4. **Agent evals** — *Validation and Measurement* + *Monitoring in Production* +
   *Improvement Loops* (agent-applications book chs 9–11); pass@k vs pass^k; the
   two-layer human/LLM calibration diagram in [../../images/](../../images/).
5. **Observability in practice** — [observability.md](../../../ai-engineering/06-eval/observability.md) +
   langfuse course refs (`generative-ai/06-observability/`): traces, spans, online
   sampling, thumbs-down → eval-set loops.
6. **Close the loop** — librarian `wiki/eval/` (16 pages) for judge design, annotation
   pipelines, threshold governance from real systems.

## Resource map

| Resource | Type | Where | What it teaches |
|---|---|---|---|
| *AI Engineering* chs 3–4 | pdf | `ai-engineering/readings/ai_engineering/ai engineer/` | evaluation methodology end to end |
| *Building Applications with AI Agents* chs 9–11 | pdf | `ai-engineering/readings/ai_engineering/ai_agent_applications/` | agent validation, monitoring, improvement loops |
| RAGAS · ARES papers | pdf | `generative-ai/02-rag-retrieval/3-rag/` | automated RAG evaluation |
| TruthfulQA + judge-bias papers | pdf | `ai-engineering/readings/general/` | why judges need calibration |
| langfuse/langsmith course repos | code | `generative-ai/06-observability/` | hands-on tracing |
| Anthropic Eval Taxonomy · LLM-judge + annotation pages (wiki/eval, 16pp) | wiki | librarian | compiled harness designs |
| eval-harness.md · observability.md | note | [ai-engineering/06-eval/](../../../ai-engineering/06-eval/) | taxonomy + tracing |
| agents-self-training.md | note | [../../notes/agents-self-training.md](../../notes/agents-self-training.md) | eval-driven training |
| two-layer eval calibration · agentic lifecycle evals | image | [../../images/](../../images/) | human/LLM grading loop diagrams |

## Test yourself
[interview-guide.md](interview-guide.md) · rounds:
[system-design-round](../../rounds/system-design-round/README.md) ("how do you know it works?"),
[project-deep-dive](../../rounds/project-deep-dive/README.md) (the measurement story).
