# AI Engineering

> **Depth domain.** This folder goes deep on the six foundations of AI engineering.
> The [interviewing guides](../interviewing/guides/00-start-here.md) are the compressed
> summary layer — read those for exam prep. Read here for synthesis and depth.

---

## The six peer foundations

```
prompt → context → harness → loop → graph → eval
```

The order is not a matter of taste — it encodes a nesting rule:

- **Harness** implements loops.
- Each **loop** step assembles **context**.
- Each assembled **context** contains **prompts**.
- **Graph** builds on loops — graphs make multi-agent organizations programmable the way loops make individual agent behavior programmable.
- **Eval** measures every layer: prompt quality, context composition, harness reliability, loop behavior, graph correctness.

All six are peer foundations. Graph is ordered fifth (after loop) because it *presumes loop mastery*, but it is a first-class discipline — not a frontier add-on.

---

## Pillar → interviewing-guide crosswalk

| Foundation | Depth (here) | Summary guide | Seed note(s) |
|---|---|---|---|
| prompt | [01-prompt/](01-prompt/README.md) | [2-llm-fundamentals](../interviewing/guides/2-llm-fundamentals/00-overview.md) | [prompt-engineering.md](01-prompt/prompt-engineering.md), [prompt-injection.md](01-prompt/prompt-injection.md) (security) |
| context | [02-context/](02-context/README.md) | [5-context-cost](../interviewing/guides/5-context-cost/00-overview.md) | [context-engineering.md](02-context/context-engineering.md), [context-management.md](02-context/context-management.md), [memory.md](02-context/memory.md) |
| harness | [03-harness/](03-harness/README.md) | [4-agents](../interviewing/guides/4-agents/00-overview.md) | [agent-harness.md](03-harness/agent-harness.md), [agents-design.md](03-harness/agents-design.md) |
| loop | [04-loop/](04-loop/README.md) | [4-agents](../interviewing/guides/4-agents/00-overview.md) | [loop-engineering.md](04-loop/loop-engineering.md), [deep-agents.md](04-loop/deep-agents.md) |
| graph | [05-graph/](05-graph/README.md) | [4-agents](../interviewing/guides/4-agents/00-overview.md) | [graph-engineering.md](05-graph/graph-engineering.md), [memory.md](05-graph/memory.md) |
| eval | [06-eval/](06-eval/README.md) | [6-evals-observability](../interviewing/guides/6-evals-observability/00-overview.md) | [eval-harness.md](06-eval/eval-harness.md), [observability.md](06-eval/observability.md) |

---

## Summary vs. depth split

**Interviewing guides** = compressed summaries for exam prep. Each guide covers a pillar end-to-end at interview depth: what you'd need to answer a question in an interview loop.

**This folder** = depth for practitioners. Each pillar README defines the engineering discipline, names its position in the stack ("inherits the weaknesses of the layer below"), maps to the real cleaned notes and coursera code, and links back to the corresponding guide.

Notes are colocated with their pillar directories. `ai-engineering/` READMEs link to the notes living alongside them — they do not copy them.
