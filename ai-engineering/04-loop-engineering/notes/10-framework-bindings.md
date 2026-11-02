---
origin: notion-export
sources:
  - https://adk.dev/agents/workflow-agents/loop-agents/
  - https://vercel.com/kb/guide/how-to-run-a-multi-step-research-agent-on-vercel
  - https://vercel.com/i/what-are-agentic-workflows
  - https://www.langchain.com/blog/the-art-of-loop-engineering
  - "Mayo Oshin & Nuno Campos, Learning LangChain (O'Reilly, 2025), ch. 8"
confidence: high
cleaned: 2026-11-01
---
# 10 — Framework Bindings

> The same loop parts in real APIs. Look for where each framework puts the goal, the scorekeeper and the stop rules.

Frameworks name the same loop parts differently, and they differ on the one that causes most trouble: who stops the loop. ADK's `LoopAgent` doesn't decide on its own, Vercel's step ceiling is yours to set, and a LangGraph cycle runs into `recursion_limit` if its conditional edge never routes to `END`. Without a map, you can ship a framework loop whose only exit is the hard cap and read that as success. This chapter maps goal, scorekeeper and stop rules onto each API.

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

The control flow is easy to misread, so here it is as a stand-in you can run without a key. The first critic returns its completion phrase and the refiner calls the exit. The second can never pass.

```python
# A stand-in for the documented LoopAgent control flow, so it runs with no key.
# It is not google-adk. The state keys and the escalate flag mirror the example above.
class Actions:
    escalate = False

def loop_agent(sub_agents, state, max_iterations):
    actions = Actions()
    for i in range(1, max_iterations + 1):
        for agent in sub_agents:
            agent(state, actions)
            if actions.escalate:
                return f"exit_loop on pass {i}"
    return f"max_iterations ({max_iterations}) reached"

DONE = "No major issues found."

def critic_that_can_pass(state, actions):
    missing = [w for w in ("cost", "stop rule") if w not in state["draft"]]
    state["critique"] = DONE if not missing else f"add {missing[0]}"

def critic_that_cannot_pass(state, actions):
    state["critique"] = "add more depth"

def refiner(state, actions):
    if state["critique"] == DONE:
        actions.escalate = True  # what the exit_loop tool does
    else:
        state["draft"] += ", " + state["critique"].removeprefix("add ")

for critic in (critic_that_can_pass, critic_that_cannot_pass):
    state = {"draft": "goal"}
    how = loop_agent([critic, refiner], state, max_iterations=4)
    print(f"{critic.__name__:<24} {how:<28} draft: {state['draft']}")
```

Output:

```text
critic_that_can_pass     exit_loop on pass 3          draft: goal, cost, stop rule
critic_that_cannot_pass  max_iterations (4) reached   draft: goal, more depth, more depth, more depth, more depth
```

Both runs return without error, and the framework doesn't label one of them a success. If you need to know which door a run left by, record it in state, for example a `status` key set in `exit_loop`. Otherwise a loop that used up `max_iterations` looks the same to the caller as one the critic approved. The second critic is also the [reviewer that cannot pass the work](03-the-scorekeeper.md#maker-and-checker) from note 03, with its made-up findings piling into the draft.

The critic/refiner split is the maker/checker pattern from [note 03](03-the-scorekeeper.md#maker-and-checker). Note that the critic's completion phrase is how it returns "clean."

---

## Vercel AI SDK: `ToolLoopAgent` / `WorkflowAgent`

- `ToolLoopAgent` coordinates model calls and tool execution across steps.
- `stopWhen: stepCountIs(25)`: the step ceiling. Treat it as required, especially when tools cost money.
- `generate()` runs the loop and returns `result.text` (final answer) and `result.steps` (tool-call history, your trace).
- Tools are `tool({ description, inputSchema: z.object({...}), execute })`. The model reads the description and schema to decide when to call and what to pass.

**Durability** with `WorkflowAgent` from `@ai-sdk/workflow`: each tool's `execute` carries a `'use step'` directive, which makes it a checkpoint. Completed steps **replay from their recorded output** instead of running again, and failed steps retry automatically. Use `stream()` rather than `generate()` for long runs. Wiring: `withWorkflow()` in `next.config.ts`, `'use workflow'` on the workflow function.

**Model routing per step**: a frontier model (`claude-fable-5-1`) for the loop's reasoning and synthesis, a smaller one (`claude-sonnet-5-5`) for aggregation and structured extraction via `generateObject()`. Model IDs use the `creator/model-name` format through the AI Gateway, with a failover list in `providerOptions.gateway.models`.

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

What a running loop exposes to a watching human (*Learning LangChain*, ch. 8):

- **Stream modes.** `stream_mode="updates"` (the default) yields `{node_name: output}` after each node, which tells you where the loop is. `"values"` yields the full state after each step. `"debug"` adds checkpoint, task and task-result events. Modes can be combined by passing a list. Token-level output comes from `astream_events(..., version="v2")`, filtered on `on_chat_model_stream`.
- **Human controls** ([note 07](07-autonomy-ladder.md#the-controls-a-human-needs-while-a-loop-runs)), all keyed by `config={"configurable": {"thread_id": ...}}` on a graph compiled with a checkpointer. **Interrupt** by breaking out of the stream, wrapped in `aclosing` so the stream closes cleanly. **Resume** by invoking with `None` as input. **Restart** by invoking with new input on the same thread (a new `thread_id` starts blank). **Edit** with `get_state` and then `update_state`, which writes a new checkpoint. **Fork** by picking a config from `get_state_history` (most recent first) and invoking `None` against it.

**Dated.** The book's **authorize** pattern passes `interrupt_before=["tools"]` at call time. Current LangGraph favours calling `interrupt()` inside the node and resuming with `Command(resume=...)`, which lets the node show the human a payload and receive a decision. Static `interrupt_before` at compile time is now mostly used for debugging. The examples also use `gpt-3.5-turbo`, which is retired.

---

## Working reference

`~/.claude/refs/google-adk.md` · `~/.claude/refs/langgraph.md` · `~/.claude/refs/agent-skills/langgraph-fundamentals/` · `~/.claude/refs/agent-skills/adk-cheatsheet/`

---

## Pitfalls

- **Assuming `LoopAgent` stops itself.** Symptom: every run uses all of `max_iterations`. Fix: implement a termination mechanism. A sub-agent sets `tool_context.actions.escalate`, and `max_iterations` stays the backstop rather than the main exit.
- **Treating the hard cap as completion.** Symptom: `max_iterations` or `recursion_limit` ends a run and the caller takes the draft. Fix: record the exit reason in state, and route cap exits to escalation.
- **No `stopWhen` on a Vercel agent.** Symptom: a paid tool gets called without bound. Fix: treat `stopWhen: stepCountIs(25)` as required, especially when tools cost money.
- **Holding a process open past the limit.** Symptom: work dies at Vercel Functions' 800s runtime limit. Fix: checkpoint and resume with `WorkflowAgent` and `'use step'`, so that completed steps replay from recorded output.
- **A critic with no completion phrase.** Symptom: the refiner never gets a clean signal and rewrites forever. Fix: define the phrase, such as "No major issues found", in the critic's criteria.
- **Copying the book's `interrupt_before` at call time.** Symptom: older authorize code that doesn't match current guidance. Fix: call `interrupt()` inside the node and resume with `Command(resume=...)`.
- **Using the frontier model for every step.** Symptom: aggregation and extraction cost what reasoning costs. Fix: route per step, with a smaller model for `generateObject()` work.

## Try it

1. Change the stand-in so the line that sets `escalate` also sets `state["status"] = "approved"`, and have the caller print `state.get("status", "cap reached: escalate")`. What does each critic print?

   <details><summary>Answer</summary>

   `critic_that_can_pass` prints `approved` and `critic_that_cannot_pass` prints `cap reached: escalate`. The caller can now route the second to a human instead of shipping the draft.

   </details>

2. Translate this loop into each framework: a hard cap of 10, an early exit when the rubric passes, and durable state.

   <details><summary>Answer</summary>

   ADK: `LoopAgent(max_iterations=10)`, a critic sub-agent, an `exit_loop` tool that sets `escalate = True`, and session state. Vercel: `ToolLoopAgent` with `stopWhen`, your own check in a tool or step, and `WorkflowAgent` for durability. LangGraph: a conditional edge to `END`, `recursion_limit`, and a checkpointer, with `RubricMiddleware` or an `after_agent` hook as the grader.

   </details>

3. Run the same stop reasons in code in the pillar lab, [loop-scorekeeper-py](../practice/loop-scorekeeper-py/README.md), then bind one maker to the framework you use.

   <details><summary>What to check</summary>

   Each of the lab's stop reasons should map to a framework exit from the mapping table. A stop reason with no mapping means your binding is missing an exit, and that's the one to write before you run it unattended.

   </details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| How does ADK's `LoopAgent` stop? | At `max_iterations`, or when a sub-agent sets `tool_context.actions.escalate`, typically via an `exit_loop` tool. It doesn't decide on its own, so you have to implement termination. |
| How do state and memory move between passes in the ADK refinement shape? | `output_key` writes each agent's reply to session state, and `{draft}` and `{critique}` read it back into the next instruction. That's the whole memory between passes. |
| What's the Vercel AI SDK equivalent of a cap and a trace? | `stopWhen: stepCountIs(n)` for the cap and `result.steps` for the trace. `WorkflowAgent` with `'use step'` adds durability by replaying completed steps. |
| What is a loop in LangGraph? | An explicit cycle: a node, a conditional edge that loops back or routes to `END`, `recursion_limit` as the hard cap, and a checkpointer for durability. |
| You must pick a framework for a refinement loop. How do you compare them? | Look at where each puts the goal, scorekeeper and stop rules. ADK has the critic and refiner shape built in as a documented pattern, Vercel leaves the check to you inside a tool or step, and LangGraph makes the cycle explicit with middleware for rubrics. |
| Why name a sandbox by run ID? | You get one sandbox per run, reused across calls, so retried steps reattach to it. |

## Next

[05-graph-engineering](../../05-graph-engineering/README.md): when one loop isn't enough and several must hand off, make the control flow an explicit graph.
