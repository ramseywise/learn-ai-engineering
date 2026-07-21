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
| prompt | [01-prompt/](01-prompt/README.md) | [2-llm-fundamentals](../interviewing/guides/2-llm-fundamentals/00-overview.md) | [prompt-engineering.md](../interviewing/notes/prompt-engineering.md) (new), [prompt-injection.md](../interviewing/notes/prompt-injection.md) (security) |
| context | [02-context/](02-context/README.md) | [5-context-cost](../interviewing/guides/5-context-cost/00-overview.md) | [context-engineering.md](../interviewing/notes/context-engineering.md), [memory.md](../interviewing/notes/memory.md) |
| harness | [03-harness/](03-harness/README.md) | [4-agents](../interviewing/guides/4-agents/00-overview.md) | [agent-harness.md](../interviewing/notes/agent-harness.md), [agents-design.md](../interviewing/notes/agents-design.md) |
| loop | [04-loop/](04-loop/README.md) | [4-agents](../interviewing/guides/4-agents/00-overview.md) | [loop-engineering.md](../interviewing/notes/loop-engineering.md), [reliable-agents.md](../interviewing/notes/reliable-agents.md) |
| graph | [05-graph/](05-graph/README.md) | [4-agents](../interviewing/guides/4-agents/00-overview.md) | [graph-engineering.md](../interviewing/notes/graph-engineering.md) (new), [readings/3-rag-knowledge-graphs/](../readings/3-rag-knowledge-graphs/) |
| eval | [06-eval/](06-eval/README.md) | [6-evals-observability](../interviewing/guides/6-evals-observability/00-overview.md) | [eval-harness.md](../interviewing/notes/eval-harness.md), [observability.md](../interviewing/notes/observability.md) |

---

## Summary vs. depth split

**Interviewing guides** = compressed summaries for exam prep. Each guide covers a pillar end-to-end at interview depth: what you'd need to answer a question in an interview loop.

**This folder** = depth for practitioners. Each pillar README defines the engineering discipline, names its position in the stack ("inherits the weaknesses of the layer below"), maps to the real cleaned notes and coursera code, and links back to the corresponding guide.

No content is duplicated. `ai-engineering/` READMEs link to `interviewing/notes/*.md` — they do not copy them.
