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

---

## Working References

Claude Code convention references that map to this pillar. These files live at `~/.claude/refs/` and can be consulted in any Claude Code session.

### `agent-observability.md`
Conventions for what a trace must contain to debug a bad agent run after the fact, and how to attribute cost to the agent, route, or user that generated it.

Key topics for this pillar:
- Four required span types: agent invocation (`invoke_agent`), model call (`chat`/`completions`), tool execution (`execute_tool`), retrieval (`retrieve`) — all nested under a root invocation span
- Minimum span attributes: `trace_id`, `span_id`, `parent_span_id`, `operation_name`, `start_time`, `end_time`, `status`, `error_message`
- Cost attribution: `agent_id`, `user_id`/`tenant_id`, and token counts on every span; derived metrics: cost per invocation/session/route, cache hit rate
- `finish_reason: max_tokens` is an error, not a completion — log at WARN; truncated outputs are wasted spend
- Six questions a complete trace must answer: which turn failed, finish_reason, tool inputs/outputs, token budget at failure, prompt version, run cost
- OTel GenAI semconv v1.41 coverage gaps: output quality scoring, safety scoring, and grounding/citation checks are project-local — do not wait for a standard

### `agent-eval.md`
Conventions for knowing whether a change made the system better, at what confidence, and what is unit-testable vs. only eval-testable.

Key topics for this pillar:
- Unit/eval seam: deterministic behaviors (schema validation, tool routing, retry logic, prompt rendering) → unit tests; nondeterministic behaviors (answer quality, grounding, end-to-end) → evals; never assert a specific LLM response string in a unit test
- Grader interface contract: standard input (query, response, expected, retrieved_context, metadata) and output (score, is_correct, reasoning, dimensions, labels) schema
- Gate ladder: data quality → retrieval → generation → grader calibration → release; each gate emits pass/fail, metrics, row diagnostics, failure labels, recommended next action
- Failure taxonomy: stable labels including `citation_hallucination`, `unsupported_claim`, `rank_miss`, `wrong_escalation`, `schema_violation`, `refusal`
- Golden dataset curation rules: real user queries (not synthetic alone), balanced coverage, eligibility labels per gate, versioned, 50–200 rows for LLM grading
- Grader states: heuristic (hard gate eligible), calibrated (LLM-as-judge with liked/disliked separation evidence), experimental (tracking only — never a release gate)
