---
origin: web-authored
sources:
  - https://medium.com/data-science-collective/ai-agents-complete-course-f226aa4550a1
  - https://medium.com/google-cloud/harness-engineering-for-multi-agent-systems-using-google-adk-2-0-e248b885cb95
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://www.anthropic.com/engineering/harness-design-long-running-apps
  - https://vercel.com/academy/build-ai-agent-harness
  - https://robearlam.com/blog/an-introduction-to-harness-engineering
  - "Bojie Li, AI Agents in Depth (2026), ch. 4 — https://github.com/bojieli/ai-agent-book"
  - Faldor, Singh, Raileanu, A team of Gemini 4 Argon agents beats Minecraft (2026), arXiv 2610.22319 — https://arxiv.org/abs/2610.22319
  - "Michael Albada, Building Applications with AI Agents (O'Reilly, 2025), ch. 5"
  - "Denis Rothman, Context Engineering for Multi-Agent Systems (Packt, 2025), ch. 4, 5, 8"
  - "Mayo Oshin & Nuno Campos, Learning LangChain (O'Reilly, 2025), ch. 8"
confidence: high
cleaned: 2026-11-01
---
# 7 — Orchestration and Multi-Agent Harnesses

> Subagents are a context management technique before they are an architecture. Treat the second as a consequence of the first.

Adding agents feels like adding capacity, but agents that coordinate only by conversation forget commitments, both claim one task, and overwrite each other's work. Measured runs in Rothman's engine took 148 s and 151 s for three-step plans against an estimate near 10.7 s. Multi-agent also has a real payoff, because a subagent that reads 40 files can hand back the 3 that matter and keep the parent's window clean. This chapter covers how to get that payoff with protocols, ownership and handoff rules, and when one agent is the better answer.

---

## Subagents as context firewall

The primary justification is not division of labor — it is **context isolation**:

> Sub-agents function as a **"context firewall"**: discrete tasks run in isolated windows so intermediate noise never accumulates in the parent thread responsible for orchestration.

A search that reads 40 files and finds 3 relevant ones should return **the 3**, not the 40. The subagent absorbs the exploration; the orchestrator receives a **condensed summary (~1,000–2,000 tokens)**. The parent stays coherent far longer than it otherwise could.

*"When working on hard problems that require many, many context windows to solve, sub-agents are the key to maintaining coherency across many sessions."*

The settled default: **orchestrator holds the plan; subagents hold the details.** Sub-agents return summaries only — search and debugging detail stays in their own contexts.

The sizing rule that follows: **give each subagent the minimum context, authority and execution budget needed to finish one clearly defined task.** Deep Agents' built-in `task` tool encodes the same contract. Each call gets a fresh agent instance, runs on its own until it finishes, and returns **one final report**. It is stateless, so it can't send a stream of messages back to the parent. The parent can still watch: `stream.subagents` gives a typed stream per subagent for UIs and tracing, without that output entering the parent's context.

---

## Protocols precede collaboration

The sequencing rule:

> **Establish a task graph and isolation boundaries *before* introducing parallelism.**

Parallelism added to an undefined task structure produces collision, not speed. Define what each agent owns, what it receives, what it returns, and what it may touch — then parallelize.

**Use natural language inside a task and protocols between tasks.** Agents that coordinate only by conversation fail in predictable ways: an agent forgets what it committed to, two agents both think they own a task, work starts before its dependency finishes, a failure is silently treated as done, a retried request runs twice, two workers edit the same files, and after a crash nobody can reconstruct the global state. Each of those is a missing piece of one of three foundations:

| Foundation | Defines | Prevents |
|---|---|---|
| **Communication protocol** | Message meanings; how requests, results, failures and acks are sent; valid state transitions | Lost acks, silent failures, double execution |
| **Task graph** | What work exists, who owns each task, which tasks depend on which | Duplicate ownership, premature starts, unknown global state |
| **Isolation boundary** | Which files, branches, tools and resources each agent may modify | Write collisions, cross-agent damage |

At the infrastructure level that becomes durable messaging, explicit task state, dependency tracking, idempotent processing, isolated side effects, structured handoffs and deterministic verification.

Isolate is also the **most expensive of the four context levers** ([02-context/10](../../02-context-engineering/notes/10-tools-and-multi-agent.md#costs)): real tokens multiply and cross-agent context is lost. Reach for it when a genuine context or trust boundary exists, not for tidiness.

---

## Role-based separation

The reliable patterns, from cheapest to most involved:

### Explorer / Executor

| Role | Tools | Model | Context |
|---|---|---|---|
| **Explorer** | Read-only | Cheaper | Isolated, disposable |
| **Executor** | Full | Stronger | Holds the plan |

Read-only exploration is safe and parallelizable, so it can run cheap and wide. Constraining the tool set *per role* is the point — the explorer physically cannot mutate anything.

### Planner / Executor

Splits decomposition from implementation. The fix for "the agent got lost in a 40-step task."

### Generator / Evaluator

Splits production from judgment — the structural answer to self-evaluation bias ([note 05](05-verification-loops.md#separating-generation-from-evaluation)).

### Topologies

| Topology | Shape | Use when |
|---|---|---|
| **Sequential** | A → B → C, each consumes the last one's artifact | Stages genuinely depend on each other |
| **Parallel** | Fan out independent workers, join the results | Subtasks share no state |
| **Manager hierarchy** | One orchestrator delegates and integrates; it can nest | The default for open-ended work |
| **All-to-all** | Agents chat freely | Brainstorming and low-stakes creative work only, because it is hard to predict and control |

Albada's rules for the static shapes (*Building Applications with AI Agents*, ch. 5): **set a maximum chain length**, because errors compound down a chain. Move to a graph only when you must both branch *and* later consolidate. A graph costs more model calls and adds new failure classes: cycles, unreachable nodes and conflicting state merges. So cap its depth and branching factor, unit-test every router function, and use tracing to check that every path reaches a terminal node.

How to cut the work is a separate choice from the topology. **Functional** decomposition splits by expertise (research, code, review). **Spatial** splits by file or directory, which parallelizes well until the files depend on each other. **Temporal** splits into stages where later ones need earlier ones finished. **Data-driven** splits by data partition for large datasets processed chunk by chunk.

### Full pipeline

Rob Earlam's harness runs a role chain end to end: **Orchestrator → PO-Spec → Feature Design → Tech Lead → Build → QA.** Around it, three supporting concepts worth naming:

- **Roles** — behavioral definitions holding each agent's logic, prerequisites, constraints, and process.
- **Artifacts** — concrete deliverables from each agent, **tagged with task IDs for traceability**.
- **Workflow standards** — governance covering technology practice, inter-agent communication, and state tracking.

Because artifacts are stored and indexed by task ID, they become a **searchable historical record**: past implementations serve as reference patterns for future work (reuse the pagination approach from task 214). Multi-agent state that persists is organizational memory, not just plumbing.

---

## Graph-based orchestration: ADK 2.0

Google's ADK 2.0 replaces ad-hoc Python loops with **structured, declarative, graph-based primitives**. The harness becomes a topology rather than control flow buried in code.

| Primitive | Role |
|---|---|
| **Agent** | Model definition, instructions, state target mappings |
| **`@node`** | Arbitrary Python — deterministic computation, tool calls, classification |
| **Edge** | Declarative routing based on state values or return codes |
| **JoinNode** | Synchronization barrier — blocks until parallel branches complete |

### Typed state

Pydantic schemas replace unstructured dictionaries:

```python
class GatewayContext(BaseModel):
    raw_payload: str = ""
    detected_language: str = "UNKNOWN"
```

ADK **validates inputs and outputs at node boundaries**, so key errors surface at the boundary rather than three nodes downstream. Schema inheritance lets base configurations extend across workflows.

This is [note 04](04-execution-boundaries.md#encode-constraints-dont-document-them) applied to orchestration: the contract between agents is *enforced*, not documented.

### Event-driven routing

Nodes return `Event` objects carrying routing instructions:

```python
return Event(actions=EventActions(route="loop_back"))
```

The engine evaluates and executes the matching edge. This **decouples node logic from graph topology** — a node states its outcome; the graph decides what that means. Rewiring the workflow doesn't touch node code.

### Subgraph composition

ADK 2.0 treats **compiled workflows as first-class nodes**, so self-contained sub-flows nest inside higher-level coordinators. The same composition property that makes functions useful, applied to agent graphs.

---

## A plan-execute engine, end to end

![Context Engine: a Planner reads the Agent Registry and has the LLM produce a JSON plan; the Executor runs Librarian, Researcher and Writer steps in order, chaining each output into the next, while a Tracer logs every step](../sources/images/context-engineering-multi-agent-systems-fig4-1.png)
*Image Source: Rothman, *Context Engineering for Multi-Agent Systems* (Packt, 2025), Fig. 4.1*

Rothman's Context Engine (*Context Engineering for Multi-Agent Systems*, ch. 4) is a compact, fully coded manager hierarchy. Four parts:

- **Agent Registry.** Maps each agent name to a handler and a capability description. The Planner reads only those descriptions, so "the clarity of this description directly determines the quality of the Planner's reasoning". Agent descriptions are tool descriptions ([note 03](03-tool-design.md)) one level up.
- **Planner.** One LLM call in JSON mode turns the goal into a list of `{step, agent, input}`. Inputs can point at earlier outputs with a placeholder such as `"$$STEP_1_OUTPUT$$"`. The parser accepts a bare list and also unwraps `{"plan": [...]}`, because models add the wrapper unprompted.
- **Executor.** Runs steps in order. It resolves placeholders against a state dict, calls the agent, and stores the result under `STEP_N_OUTPUT`.
- **ExecutionTrace.** Logs the planned input, the resolved input and the output of every step. It is returned even when the run fails.

The resolver is where the design pays off:

```python
import re
REF = re.compile(r"^\$\$(STEP_\d+_OUTPUT)\$\$$")

def resolve(value, state):
    if isinstance(value, str) and (m := REF.match(value)):
        key = m.group(1)
        if key not in state:          # the plan referenced a step that never ran
            raise ValueError(f"Dependency Error: {key} not found")
        return state[key]
    if isinstance(value, dict):
        return {k: resolve(v, state) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(v, state) for v in value]
    return value
```

A missing reference **fails fast** instead of passing the literal placeholder string to the next agent. The run halts at that step, and the trace shows which step broke and what it was given.

Two cautions:

- **The book's "MCP" is not the Model Context Protocol.** In the code it is a homegrown `create_mcp_message(sender, content)` dict envelope passed between in-process functions. That is fine as a message format, but nothing in it is MCP as [note 03](03-tool-design.md#mcp-vs-in-process) uses the term.
- **One skipped chunk can take down the run.** In ch. 8, a sanitizer skipped a retrieved chunk of legitimate testimony, and a later step failed with a fatal Dependency Error ([note 04](04-execution-boundaries.md#moderation-around-the-whole-engine)). Fail-fast is right, but the step that drops data has to say so.

### The latency budget of a sequential plan

Sequential plans add their latencies together. Rothman's ch. 8 estimate for a three-step plan (Librarian → Researcher → Writer) with moderation on both ends. These are illustrative figures that vary with model, network and load:

| Call | ≈ ms |
|---|---|
| Moderation, pre-flight | 200 |
| Planner | 3,000 |
| Embeddings (×2) | 150 each |
| Vector-DB queries (×2) | 250 each |
| Researcher synthesis | 4,000 |
| Writer | 2,500 |
| Moderation, post-flight | 200 |
| **Total** | **≈ 10,700** |

That is at least eight API calls in a row, and the generation calls dominate. Measured runs in ch. 5 were far slower than the estimate: **148 s and 151 s** for three-step plans with gpt-5 as the generation model, run from Colab. Rothman's levers: run independent calls in parallel, cache repeated retrievals and plans, and use smaller, faster models for the simpler steps. The broader point is that each extra agent in a sequential plan adds its full latency to the user's wait.

---

## Multi-agent failure modes

Loop oscillation, context pollution, concurrency collision and consensus deadlock are all *harness* bugs. None is fixed by a better model, and all four get worse as agent count rises, which is the practical argument for keeping agent counts as low as the task allows. The table of fixes, the research taxonomy and how to attribute a failure are in [graph 05 — how multi-agent systems fail](../../05-graph-engineering/notes/05-topology-patterns.md#how-multi-agent-systems-fail), the authoritative note.

---

## Handoff design

What crosses a boundary is the whole design. The short version: **define interfaces, not vibes.** Each agent needs a schema for its inputs and outputs: which fields, which types, which IDs or references get passed along. Handoffs break more often than the models do.

- **Structured, not prose.** A typed schema — findings, files touched, confidence, open questions — beats a paragraph.
- **Summaries, never transcripts.** Sending a subagent's full history back defeats the firewall.
- **State on disk, references in the message.** Large artifacts go to files; the handoff carries paths ([note 06](06-long-horizon-execution.md#tool-call-offloading)).
- **Declare what was *not* done.** Scoped claims prevent the orchestrator from assuming coverage that doesn't exist.
- **Label every source in the subagent's prompt.** Li's convention: a role statement, then inputs tagged `[FROM_MAIN_AGENT]`, `[FROM_USER]` and `[TOOL_RESULT]`, then explicit boundaries, then a JSON output schema. A subagent that can't tell instructions from data will follow injected text.
- **Key the payload, and keep the keys stable.** Rothman's engine broke when two agents were "upgraded" to return dicts (`{"blueprint_json": ...}`, `{"facts": ...}`) instead of strings. The Writer still expected raw strings, so the upgraded pipeline broke at its last step (*Context Engineering for Multi-Agent Systems*, ch. 5). Whenever an agent's output shape changes, every consumer of that output has to change in the same commit.
- **Synthesize, don't delegate understanding.** "Based on your findings, fix the auth bug" pushes the orchestrator's job onto the worker. The orchestrator reads the findings and hands down a precise spec: the file, the line, the change, and what done looks like.

---

Collaboration tools reduce to a small set of primitives: `spawn` and `cancel`, `send_message`, and `list_agents`. Each one runs in one of four modes: **sync** (wait for the result), **async** (task ID plus an event later), **streaming** (partial results as they come), or **multi-turn** (a conversation with the worker). Choose the mode per task; a 30-minute research job should never be a sync call.

---

## Asynchronous agents: events and safe points

![Three ways to handle an event that arrives mid-task: cancel and restart, queue until a safe point, or run in parallel](../sources/images/li-ai-agents-in-depth-fig6-2.svg)
*Image Source: Li, [AI Agents in Depth](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter6.md) (2026), Fig. 6-2 (Apache-2.0)*

A resident agent receives user messages, tool results, timers, webhooks and messages from other agents, all at unpredictable times. Li's model (ch. 4) is an **event loop**: each iteration drains a batch of events from the queue, appends them to the trajectory, calls the LLM once, and runs the tools it chose. Events are consumed **only at safe points**, meaning the end of a reasoning stretch or a tool return, never mid-step. Cancellation is checked at safe points too, the same discipline as Go's `ctx.Done()`.

**Model each input as a structured event:** source (who), channel (how), content (what, including urgency), and context (which thread or task it belongs to). This keeps a user command distinct from a tool result that *contains* a command, which is the prompt-injection case.

Three strategies, which differ only in how they treat the safe point:

| Strategy | For | Mechanics |
|---|---|---|
| **Cancel** (force a safe point now) | `user.interrupt`, supervisor orders, urgent alerts | Abort the streaming response or tool, drain the queue, append everything, and re-invoke the LLM |
| **Queue** (wait for the next safe point) | Routine input, tool results, timers | Append as a batch when the current step finishes. "Only last month" arrives with the search results it modifies, saving a round trip |
| **Parallel** (don't wait) | Independent, cheap queries ("what's the weather?") | Answer in a side session; append the exchange to the main trajectory, marked as parallel |

Hard-coded rules miss semantics. Li recommends a **small classifier LLM as the event router** to pick the strategy.

**Keeping a synchronous model sane** (five rules):

1. Write the assistant message, including any tool call, to the trajectory as soon as it is produced.
2. Write the tool result only when the tool completes.
3. If an interrupt arrives mid-tool, insert a **placeholder result** ("still running in the background; handle the new event first") so every call stays paired, and deliver the real result later as a new event.
4. If an interrupt arrives mid-thought, discard the partial thinking.
5. Queue non-urgent events and append them in a batch.

Placeholders invite hallucinated results, so interrupt only when it is genuinely urgent. For batches, the model tends to answer only the last event. Number them (`[Unprocessed event 2/4] User note: Beijing data only`) and end with a summary line ("4 events: 1 tool result, 2 user messages, 1 reminder; address all of them").

Polling is the fallback, not the design. Timers and heartbeats make an agent *look* proactive, but an OTP request during a live phone call can't wait five minutes for the next tick. Real proactivity needs a push channel from the outside world into the queue.

### Double texting: the same problem in a chat app

Oshin and Campos (*Learning LangChain*, ch. 8) list the options for a user who sends a second message while the first run is still going:

| Strategy | Behaviour | Cost |
|---|---|---|
| **Refuse** | Reject new input until the run finishes | Simplest; pushes concurrency onto the caller |
| **Handle independently** | Start a second run on a new thread | The user sees two separate runs that can't be reconciled |
| **Queue** | Run the new input after the current run | Queue grows without bound, and later inputs may already be stale |
| **Interrupt** | Stop the current run and restart with both inputs | Choose what to keep: nothing, the last completed step, the in-progress step too, or wait for the current node to finish |
| **Fork and merge** | Run both in parallel and merge the state afterwards | Needs merge-friendly state (CRDT-style) or manual conflict resolution. If you have either, the authors rate this the best option overall |

The interrupt row hits the same pairing constraint as Li's rule 3. OpenAI's API requires every assistant message carrying tool calls to be followed immediately by its tool messages, so an interrupted run's state must be cleaned up or padded before the next model call.

Labs, upstream: [4-4 event-triggered email agent](https://github.com/bojieli/ai-agent-book/tree/main/chapter6/agent-with-event-trigger) · [4-5 async agent with interruption](https://github.com/bojieli/ai-agent-book/tree/main/chapter6/async-agent).

---

## Coordination without a coordinator: four agents in Minecraft

Most of this note designs coordination in advance. The Gemini Minecraft run (Faldor et al., 2026; harness in [note 02](02-harness-anatomy.md#one-harness-read-through-the-five-subsystems), timeline in [note 06](06-long-horizon-execution.md#what-a-27-hour-run-looks-like)) shows how much four agents organize on their own when the harness gives them the right shared surfaces. There was no orchestrator. Each agent had the same instructions, a shared chat and shared notes.

What emerged over 27 hours:

| Behaviour | What happened | The harness surface behind it |
|---|---|---|
| **Specialization** | One agent took tools, the fortress and the stronghold; one took supplies and six of the ten crystals; one the Nether portal and the crystal plan; one built Enderman shelters and landed the final blow | Shared chat, where agents announced what they were taking |
| **Shared memory** | Locations, plans and lessons were written to notes every agent could read | Shared notes outside every context window |
| **Own tools** | 42 reusable helper functions, reused across thousands of later programs | A code-writing action space ([note 03](03-tool-design.md)) |
| **Rescues** | Agents went to help a teammate stuck or dying | Shared chat plus each agent's position in the world |
| **Corrections** | Agents retracted false claims and flagged teammates' contradictions | The instruction to report honestly, plus an Observer agent checking claims ([note 05](05-verification-loops.md#an-observer-that-checks-claims-against-the-record)) |

The chat stayed small: **229 messages** across 2,783 programs, roughly 50 to 80 per agent. Coordination happened through a few short messages and a shared written record, not constant conversation. That is the [protocols-between-tasks](#protocols-precede-collaboration) rule arriving on its own.

The caution: one run, one game, on Easy. It shows that emergent coordination *can* hold for a day. It doesn't show that it will in your domain, where a silently wrong shared note costs more than a death in Minecraft.

---

## When *not* to go multi-agent

Multi-agent is the expensive option. Single agent with verification is the correct default; escalate only when:

- **Context genuinely doesn't fit** — the firewall argument, the strongest reason.
- **Roles need different tools or trust levels** — read-only explorer, sandboxed executor.
- **Self-evaluation bias is the blocker** — you need an external evaluator.
- **Branches are genuinely independent** — real parallelism, not sequential work in costume.

Absent one of these, added agents multiply token cost and introduce the four failure modes above while solving nothing. The three architectural patterns, in order of increasing cost: **single agent with verification → two-agent supervisor → multi-agent with a shared harness layer.**

---

## Pitfalls

- **Parallelizing before defining the protocol.** Symptom: two agents own one task, or work starts before its dependency finishes. Fix: define what each agent owns, receives, returns and may touch. Use natural language inside a task and protocols between tasks.
- **Returning the exploration instead of the result.** Symptom: the parent window fills with all 40 files. Fix: the subagent returns the 3 relevant ones in a condensed summary of about 1,000–2,000 tokens, with large artifacts on disk.
- **An unresolved placeholder passed along as text.** Symptom: the next agent receives the literal string `$$STEP_1_OUTPUT$$`. Fix: fail fast on a missing reference, as Rothman's executor does, so the trace shows which step broke.
- **Cycles without counters.** Symptom: two nodes bounce work indefinitely. Fix: put iteration counters on cyclic edges and force escalation.
- **Parallel branches writing the same state.** Symptom: a concurrency collision, with one branch's result overwritten. Fix: per-branch ownership of state keys, and JoinNode barriers.
- **Reviewers with no way to finish.** Symptom: consensus deadlock blocks the run. Fix: a tie-break rule, a majority threshold or a final arbiter.
- **Going by a latency estimate.** Symptom: a plan estimated near 10.7 s takes about 150 s. Fix: measure real runs, then run independent calls in parallel, cache repeated retrievals and plans, and use smaller models for simpler steps.
- **Generalizing from a showcase.** Symptom: "the Minecraft agents coordinated with almost no messages, so ours can". Fix: remember it was one run, one game, on Easy. A silently wrong shared note costs more in your domain.

## Try it

1. The planner emits three steps, and step 3 references `$$STEP_4_OUTPUT$$`. What should the executor do, and what goes wrong if it doesn't?

   <details><summary>Answer</summary>

   It halts at step 3, with a trace naming the step and what it was given. Without that, the literal placeholder reaches the next agent, which may treat it as text and produce a plausible answer built on nothing.

   </details>

2. A user sends a second message while the agent is working on the first. From the note's double-texting table, pick a strategy for (a) a typo correction and (b) an unrelated new request, and say what each costs.

   <details><summary>Answer</summary>

   (a) Interrupt: stop the run and restart with both inputs. You must choose what to keep, and the state has to be cleaned up or padded so every tool call keeps its result. (b) Queue, at the risk that later inputs go stale, or handle independently on a new thread, where the user sees two runs that can't be reconciled.

   </details>

3. For one multi-agent system you know, fill in the protocol table: communication protocol, task graph and isolation boundary. Then say what it would take to remove one agent.

   <details><summary>What to look for</summary>

   Any cell you can't fill is a place conversation is standing in for a protocol, and it maps to a failure such as double execution or write collisions. If an agent has the same tools and trust level as its parent and doesn't need context isolation, it is a candidate for removal under [when not to go multi-agent](#when-not-to-go-multi-agent).

   </details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| What is a subagent's main value? | Context isolation, as a firewall. A search that reads 40 files and finds 3 returns the 3 in a summary of about 1,000–2,000 tokens, so the parent stays coherent longer. |
| Why define protocols before parallelism? | Parallelism on an undefined task structure produces collision, not speed. Use natural language inside tasks and protocols between them. |
| Name four orchestration failures and their fixes. | Loop oscillation: iteration counters. Context pollution: boundary schemas, returning summaries only. Concurrency collision: per-branch state ownership and JoinNode barriers. Consensus deadlock: a tie-break or arbiter. |
| Why was Rothman's measured latency so far above the estimate? | The estimate was about 10.7 s and measured three-step runs took 148 s and 151 s with gpt-5 from Colab, with generation calls dominating. The levers are parallel independent calls, caching and smaller models. |
| Does the Minecraft run prove agents can self-coordinate? | It shows emergent coordination can hold for a day: 229 messages across 2,783 programs. It was one run, one game, on Easy, so don't extrapolate to domains where a wrong note is costly. |
| When do you stay with one agent? | When tasks don't need separate tools, trust levels or context isolation, because coordination overhead can exceed the parallel gain. Find the single-agent limit first. |
| One agent's invention reaches the final answer of a multi-agent run. How do you catch it and find the culprit? | Cross-validate claims that cross a handoff. Evaluate each component and the end-to-end result separately: if end-to-end fails while every component passes, the bug is in a handoff; if one component fails, you know which agent to fix. |

## Next

[08-maturity-and-failure-modes.md](08-maturity-and-failure-modes.md): staging the build, and what goes wrong.
