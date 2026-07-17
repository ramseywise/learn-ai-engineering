# Pillar 5 — Context Engineering & Cost/Latency

What actually goes into the model's context window, in what order, and what it costs.
The unglamorous pillar that separates demos from products: prefix caching, compaction,
context rot, token economics, and latency budgets.

## Learning path

1. **The mental model** — notes: [context-engineering.md](../../notes/context-engineering.md)
   + [context-management.md](../../notes/context-management.md) (the 5 context layers,
   static-first ordering); librarian's *Prefix Caching* page for the caching mechanism.
2. **Why it matters mechanically** — KV cache + prefill/decode economics from the
   [pillar-2 interview guide](../2-llm-fundamentals/interview-guide.md) §§1,4; ALiBi
   (`readings/2108.12409v2.pdf`) for the long-context side.
3. **Inference optimization in depth** — *AI Engineering* ch 9 (Inference Optimization,
   `readings/ai_engineering/ai engineer/`); for how deep the rabbit hole goes:
   *AI Systems Performance Engineering* (`ai performance/`, esp. chs 15–19 on
   multinode inference, prefill/decode disaggregation, KV-cache tuning).
4. **Compaction & summarization** — librarian *Summarization Node* + ADK context pages;
   the static/dynamic-context diagrams in [../../images/](../../images/)
   (adk-static-vs-dynamic-context.png).
5. **Budgeting practice** — do the napkin math for one of your own systems: tokens/query
   × $/M × volume; p50/p95 latency per component. (This habit is graded in every design
   round.)

## Resource map

| Resource | Type | Where | What it teaches |
|---|---|---|---|
| *AI Engineering* ch 9 | pdf | `readings/ai_engineering/ai engineer/` | quantization, distillation, speculative decoding, serving metrics |
| *AI Systems Performance Engineering* (chs 1–20) | pdf | `readings/ai_engineering/ai performance/` | GPU/CUDA-level inference performance (awareness tier) |
| ALiBi (2108.12409) | pdf | `readings/` | long-context positional method |
| Prefix Caching · ADK Context Engineering · Summarization Node | wiki | librarian | caching + compaction patterns from real builds |
| context-engineering.md · context-management.md | note | [../../notes/](../../notes/) | context layers, compaction instructions |
| ADK context diagrams | image | [../../images/](../../images/) | static-vs-dynamic context, vibe-coding stakes spectrum |

## Test yourself
[interview-guide.md](interview-guide.md) · rounds:
[system-design-round](../../rounds/system-design-round.md) (cost/latency trade-offs are
its bread and butter).
