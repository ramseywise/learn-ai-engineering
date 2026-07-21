# 06 — Evaluation Engineering

> Depth layer. Summary: [interviewing/guides/6-evals-observability](../../interviewing/guides/6-evals-observability/00-overview.md)
> Position in the stack: sixth foundation — *measures every layer below; guide = exam summary, here = depth*.
> Deep note: [eval-harness.md](../../interviewing/notes/eval-harness.md)

---

## What it is

Evaluation engineering is the discipline of building systematic measurement for AI systems: defining what "correct" means, writing tests that check it, instrumenting pipelines to observe behavior at scale, and closing the loop from observation back to improvement. Eval is a sixth peer foundation — not just a QA step. It applies at every layer: prompt quality (unit evals), context composition (retrieval precision/recall), harness reliability (error rates, latency), loop behavior (task completion, hallucination), and graph correctness (coordination fidelity, routing accuracy).

*"Eval is the layer that measures all the others."*

**Cross-link discipline:** `06-eval/` (here) is the *depth* layer; [`6-evals-observability`](../../interviewing/guides/6-evals-observability/00-overview.md) is the *summary* layer. The guide is the compressed exam-prep version; this README and its linked notes go deeper. Both cover evals and observability — they are kept in sync by the pointer relationship, not by copying content. If they drift, the guide is the summary and this folder is the source of depth.

**Inherits the weaknesses of:** all five layers below — eval can only measure what the preceding layers expose. If the harness has no observability hooks, eval has no signal to act on.

---

## Resource map

### Deep notes
- [eval-harness.md](../../interviewing/notes/eval-harness.md) — eval as harness primitive: test harness design, LLM-as-judge, golden datasets, CI integration.
- [observability.md](../../interviewing/notes/observability.md) — tracing, logging, metrics for agent systems; LangFuse integration.

### Interviewing guide
- [6-evals-observability](../../interviewing/guides/6-evals-observability/00-overview.md) — compressed summary for interview prep.

### Coursera code
- [DeepLearning.AI-Evaluating-AI-Agents-master](../../generative-ai/coursera-references/DeepLearning.AI-Evaluating-AI-Agents-master/) — agent eval patterns: task completion, faithfulness, safety.
- [Learning-LangFuse-main](../../generative-ai/coursera-references/Learning-LangFuse-main/) — LangFuse observability platform.
- [langfuse-evaluation-main](../../generative-ai/coursera-references/langfuse-evaluation-main/) — evaluation workflows in LangFuse.

### External references
- Anthropic on eval harness design: https://www.anthropic.com/research/evaluating-ai-systems
- awesome-harness-engineering (evals section): https://github.com/ai-boost/awesome-harness-engineering
