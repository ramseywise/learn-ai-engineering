---
origin: notion-export
sources:
  - https://adk.dev/agents/workflow-agents/loop-agents/
  - https://vercel.com/kb/guide/how-to-run-a-multi-step-research-agent-on-vercel
  - https://vercel.com/i/what-are-agentic-workflows
  - https://www.langchain.com/blog/the-art-of-loop-engineering
confidence: high
cleaned: 2026-10-28
---
# 10 — Framework Bindings

> The same loop parts in real APIs. Look for where each framework puts the goal, the scorekeeper and the stop rules.

---

## Mapping table

| Loop part | Google ADK | Vercel AI SDK | LangChain / LangGraph |
|---|---|---|---|
| Agent loop | `LoopAgent` with `sub_agents` | `ToolLoopAgent` | `create_agent` |
| Scorekeeper / checker | a critic sub-agent | your own check inside a tool or step | `RubricMiddleware`, `after_agent` hooks |
| Early exit | `exit_loop` tool sets `escalate = True` | `stopWhen` condition | conditional edge to `END` |
| Hard cap | `max_iterations` | `stopWhen: stepCountIs(n)` | `recursion_limit` |
| Durability | session state | `WorkflowAgent` + `'use step'` | checkpointer |
| Trace | events | `result.steps` | LangSmith |

---

## Google ADK: `LoopAgent`

A workflow agent that runs its `sub_agents` **in order, every pass**, until a stop condition fires.

- `sub_agents`: the ordered list run each pass.
- `max_iterations`: hard cap; the loop halts when it's reached.
- **Stopping is not automatic**: *"the LoopAgent itself does not inherently decide when to stop looping. You must implement a termination mechanism."* A sub-agent ends the loop early by setting `tool_context.actions.escalate = True`, usually through an `exit_loop` tool.

The documented refinement shape: `InitialWriterAgent` (draft) → `CriticAgent` (grade against criteria) → `RefinerAgent` (apply fixes, or call `exit_loop` when the critic returns its completion phrase, e.g. "No major issues found"). Sub-agents share state through the session state dict. Available in Python, TypeScript, Go and Java.

```mermaid
flowchart LR
    W["InitialWriterAgent<br/>writes state['draft']"] --> C
    subgraph L["LoopAgent 'Refine' · max_iterations=5 (backstop)"]
        C["CriticAgent<br/>grades {draft}<br/>→ state['critique']"] --> R{"RefinerAgent:<br/>critique clean?"}
        R -->|no: rewrite<br/>→ state['draft']| C
    end
    R -->|"yes: exit_loop()<br/>escalate = True"| D(["final draft"])
    L -.->|cap reached| D2(["stop without<br/>a clean verdict"])
```

```python
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools.tool_context import ToolContext

def exit_loop(tool_context: ToolContext):
    """Call only when the critic said 'No major issues found'."""
    tool_context.actions.escalate = True     # ends the LoopAgent after this pass
    return {}

critic  = LlmAgent(name="CriticAgent",  instruction="Grade {draft} against the criteria...",
                   output_key="critique")
refiner = LlmAgent(name="RefinerAgent", instruction="If {critique} is clean, call exit_loop. "
                   "Otherwise rewrite {draft}.", tools=[exit_loop], output_key="draft")

refine = LoopAgent(name="Refine", sub_agents=[critic, refiner], max_iterations=5)  # backstop
pipeline = SequentialAgent(name="Write", sub_agents=[initial_writer, refine])
```

`output_key` writes each agent's reply into session state, and `{draft}` / `{critique}` read it back into the next instruction. That's the whole memory between passes.

Practices: write the completion criteria before the loop; always provide the escape hatch; keep `max_iterations` as the backstop, **not** the main exit.

The critic/refiner split is the maker/checker pattern from [note 03](03-the-scorekeeper.md#maker-and-checker). Note that the critic's completion phrase is how it returns "clean."

---

## Vercel AI SDK: `ToolLoopAgent` / `WorkflowAgent`

- `ToolLoopAgent` coordinates model calls and tool execution across steps.
- `stopWhen: stepCountIs(25)`: the step ceiling. Treat it as required, especially when tools cost money.
- `generate()` runs the loop and returns `result.text` (final answer) and `result.steps` (tool-call history, your trace).
- Tools are `tool({ description, inputSchema: z.object({...}), execute })`. The model reads the description and schema to decide when to call and what to pass.

**Durability** with `WorkflowAgent` from `@ai-sdk/workflow`: each tool's `execute` carries a `'use step'` directive, which makes it a checkpoint. Completed steps **replay from their recorded output** instead of running again, and failed steps retry automatically. Use `stream()` rather than `generate()` for long runs. Wiring: `withWorkflow()` in `next.config.ts`, `'use workflow'` on the workflow function.

**Model routing per step**: a frontier model (`claude-fable-5`) for the loop's reasoning and synthesis, a smaller one (`claude-sonnet-5`) for aggregation and structured extraction via `generateObject()`. Model IDs use the `creator/model-name` format through the AI Gateway, with a failover list in `providerOptions.gateway.models`.

**Sandboxing** model-written code:

```typescript
const sandbox = await Sandbox.getOrCreate({
  name: `analysis-${researchId}`,
  runtime: 'node24',
  timeout: 600_000,
  networkPolicy: 'deny-all',
});
```

Naming the sandbox by run ID gives one sandbox per run, reused across calls; retried steps reattach to it.

**Runtime limit:** Vercel Functions with fluid compute run up to 800s. Anything longer has to checkpoint and resume instead of holding the process. Cost and security controls: bearer-token auth on the start/status routes, AI Gateway keys with budgets, and per-call token, latency and cost logging.

The research agent's loop in one line: *"search, read, aggregate, synthesize, then decide whether to keep going."*

---

## LangChain / LangGraph

LangChain's four levels ([note 01](01-what-a-loop-is.md#the-map-of-this-pillar)) map onto its own products: `create_agent` (L1), `RubricMiddleware` and `after_agent` hooks (L2), LangSmith Deployment cron and webhooks (L3), and LangSmith Engine for trace-driven harness rewrites (L4).

In LangGraph a loop is an explicit cycle in the graph: a node, a conditional edge that either loops back or routes to `END`, a `recursion_limit` as the hard cap, and a checkpointer for durability and human-in-the-loop interrupts. Once you are drawing the cycle as a graph, you're at the next layer: [05-graph](../../05-graph-engineering/README.md).

---

## Working reference

`~/.claude/refs/google-adk.md` · `~/.claude/refs/langgraph.md` · `~/.claude/refs/agent-skills/langgraph-fundamentals/` · `~/.claude/refs/agent-skills/adk-cheatsheet/`

---

→ Practice: [../practice/exercises.md](../practice/exercises.md) — build the loops from this syllabus.
