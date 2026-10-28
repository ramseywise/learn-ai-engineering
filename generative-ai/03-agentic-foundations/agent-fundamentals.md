---
origin: book-synthesis
sources:
  - "Bojie Li, AI Agents in Depth (2026), ch. 1 — https://github.com/bojieli/ai-agent-book"
  - https://www.anthropic.com/engineering/building-effective-agents
  - https://www.anthropic.com/research/next-generation-constitutional-classifiers
confidence: high
cleaned: 2026-10-28
---
# Agent fundamentals

> Agent = LLM + Context + Tools. What each term covers, how the ReAct loop ties them together, and when to choose a workflow or an autonomous agent.

---

## The formula

**Agent = LLM + Context + Tools.** Read each term broadly:

| Term | Role | Covers | RL analogue |
|---|---|---|---|
| **LLM** | Reasoning engine | Understanding intent, planning, choosing the next action. Knowledge comes from pre-training; decision policy from post-training. | Policy |
| **Context** | Working set of information | Everything available at a decision point: environment, user memory, domain knowledge, own state, task progress | Observation space |
| **Tools** | Action interfaces | Predefined tool calls, Skills loaded on demand, generated code, sub-agents, messages to the user, external events | Action space |

The observation and action spaces are the **interface between the model and the world**, much as an ISA is the interface between software and hardware. Information outside the observation space does not exist for the model. An action outside the action space is something the model can only recommend in words.

That makes the **primary lever, with the model held fixed, to expand context and tools**. Many "we need a smarter model" problems are interface problems: put the relevant data into context, or expose the needed operation as a tool. Manus became a general agent by taking the union of three agent types (Deep Research = web; Coding = files and code; Computer Use = screen and clicks), not by swapping models. OpenClaw extended the same spaces into messaging channels and local files.

Expansion has to be **on-demand, relevant and controlled**. Irrelevant context is noise. Every extra tool adds selection cost and attack surface. Retrieval, tool discovery and permissions are what make expansion safe ([tool discovery at scale](../../ai-engineering/03-harness-engineering/notes/03-tool-design.md)).

Production agents of every kind share three traits. The action space is **open-ended**: they generate language and code, not button presses. They **reason internally** before acting. They **interact continuously**, adjusting to feedback from the environment.

---

## Tools

Tools can be sorted by the direction of interaction:

| Type | Direction | Examples |
|---|---|---|
| Perception | World → agent, on request | Search, file read, DB/API queries |
| Execution | Agent → world | Code execution, file writes, system commands, API calls |
| Collaboration | Agent ↔ agent/human | Sub-agent delegation, human confirmation |
| Event trigger | World → agent, unprompted | Incoming email, cron, webhook. The agent doesn't call these; they wake it up. |
| User communication | Agent → user | Progress updates, check-ins by text, voice or email |

**Tool calling has four steps.**

1. The context declares the available tools: name, purpose and parameter schema.
2. The model decides whether to call one, which one and with what arguments.
3. The framework runs the call and appends the result to the context.
4. The model decides what to do next.

The developer defines and runs tools. The model makes every decision about using them.

**General vs. specialized.** Start with the narrowest capability that works and widen it when the task demands. A sandboxed code interpreter composes better than a growing pile of single-purpose tools. Sandbox it with network off by default, a confined working directory, and CPU, memory, time and output limits. High-risk or tightly governed operations stay as **dedicated tools** with explicit parameters, narrow permissions and an audit trail: payments, deletes, outbound email, deploys. Rule of thumb: *general capabilities for composition and exploration; specialized tools to constrain risk and enforce business rules.* Depth: [harness 03 — tool design](../../ai-engineering/03-harness-engineering/notes/03-tool-design.md).

---

## Context

Each LLM call's context has five parts:

| Part | Lifetime | Contents |
|---|---|---|
| System prompt | Static prefix | Role, permissions, rules; also cross-session user memory and injected environment state |
| Tool definitions | Static prefix | Names, descriptions, parameter schemas (since 2026, frameworks can also load schemas on demand at the end of the context without breaking the cached prefix) |
| User messages | Trajectory | Input, plus any RAG-retrieved knowledge |
| Assistant messages | Trajectory | Up to three parts: `reasoning`, `content` and `tool_calls` (typically reasoning + tool_calls, or reasoning + content) |
| Tool results | Trajectory | What the framework returns after running a tool |

**Agent context = static prefix + trajectory.** The first two parts make up the prefix, which is constant for the whole conversation and is what makes KV-caching possible. The last three make up the trajectory, which grows every turn.

### Ablation: what each part is for

Experiment 1-1 removes one part at a time (the system prompt is kept, since without it there is no agent):

| Removed | Observed failure |
|---|---|
| Tool definitions | Can't act at all. It doesn't know any tools exist. |
| Tool results | No feedback, so it calls the same tool repeatedly and loops forever |
| Reasoning in assistant messages | Consecutive decisions contradict each other |
| Message history | Loses continuity, restarts the task and repeats finished steps |

The lesson: *an agent can only decide on what is in its context.* Every component is load-bearing. Lab: [chapter1/context](https://github.com/bojieli/ai-agent-book/tree/main/chapter1/context) (needs an API key; configurable ablation modes).

---

## The ReAct loop

**Reason → act → observe**, repeated until done. On every call the model gets the static prefix plus the full trajectory, then its response is appended to the trajectory:

```
user:      "Q1 2.5M USD, Q2 2.1M EUR, Q3 1.8M GBP, Q4 380M JPY — total and average?"
assistant: reasoning="convert to USD"   tool_calls=[convert×3]      # parallel
tool ×3:   EUR→USD 2282608.7 · GBP→USD 2278481.01 · JPY→USD 2541806.02
assistant: reasoning="aggregate"         tool_calls=[code_interpreter]
tool:      "Total: $9,602,895.73, Average: $2,400,723.93"
assistant: reasoning="done"              content="FINAL ANSWER: ..."
```

That run took three iterations and four tool calls. Because the context accumulates, the model always knows what stage the task is at and what has already been tried. Because the trajectory is structured, it can be read and debugged. It is also the raw material for learning: distill trajectories into a knowledge base, or train on them with RL ([gen-AI 05](../05-RL/README.md)). The cost is that the full trajectory is re-sent every turn, so total tokens grow quadratically with length. [Compaction](../../ai-engineering/02-context-engineering/README.md) is the usual mitigation.

**Exit conditions** for an autonomous loop: a final-output tool is called, the model replies with no tool calls, an unrecoverable error occurs, or the round cap is hit.

---

## Model as agent

Frontier models now internalize **the tool-calling decision policy** through RL: when to call, which tool, what arguments, whether to continue, how to chain hundreds of calls. Examples are Kimi K3, with stable 200–300-call chains, and GPT-5.6 with Responses-API built-in web search and code interpreter, plus an intent-clarification step before research begins. Two points are often confused:

- **RL teaches the decision; it doesn't contain the tool.** `web_search` and the sandbox still run outside the weights, server-side as API built-ins. The orchestration loop has moved from client to server, and the decision has moved into the model.
- **A stronger model makes the harness matter more, not less.** The more decisions the model owns, the more a wrong one costs, so constraint, verification and correction get finer-grained. See [harness 01](../../ai-engineering/03-harness-engineering/notes/01-what-a-harness-is.md).

Freeform tool calling (`type: "custom"`) lets the model send raw text, such as Python or SQL, rather than JSON-escaped arguments. It changes the API format, not the architecture. The loop is still: detect call → execute → return.

Upstream labs: [1-2 web-search-agent](https://github.com/bojieli/ai-agent-book/tree/main/chapter1/web-search-agent) · [1-3 search-codegen](https://github.com/bojieli/ai-agent-book/tree/main/chapter1/search-codegen) (both need API keys).

### How agents learn

Agents learn in three ways, which differ in where the update lives and how long it lasts:

| Path | Where | Persists | Best for |
|---|---|---|---|
| Contextual adaptation | Current context (examples, state, retrieval) | This task only | Fast, cheap adjustment |
| External artifacts | Knowledge docs, prompts/Skills, code and harness | Across tasks; auditable | Facts, language-expressible strategy, deterministic rules |
| Parameters | Weights, via post-training | Permanently | High-dimensional skills rules can't express |

They work together at different timescales. Depth: [loop 08 — self-improving loops](../../ai-engineering/04-loop-engineering/notes/08-self-improving-loops.md).

---

## Choosing a model

Release cycles move too fast for version picks, so here are the directions:

- **Evaluate on your own tasks**, not leaderboards ([06-eval](../../ai-engineering/06-eval/README.md)). Tool-calling ability varies more than general benchmarks suggest.
- **Use a reasoning model** for anything multi-step or dynamic. Non-reasoning models suffice only for single simple steps or fixed-position GUI clicks.
- **Output speed is latency.** Rounds are sequential: 2 s slower per round across 20 rounds adds 40 s.
- **Multimodality** is a hard requirement if inputs include images, audio or video. Coverage differs widely.
- **Open vs. closed.** Closed models lead on capability. Open weights win on cost, private deployment and fine-tuning.

---

## Workflow vs. autonomous agent

Climb the ladder only as far as you need: **a single LLM call → workflow → autonomous agent.** Agents trade latency and cost for task performance; check the trade is worth it.

| | Workflow | Autonomous agent |
|---|---|---|
| Path | Fixed in code; the LLM works only inside nodes | Chosen at runtime from environment feedback |
| Strengths | Steps can't be skipped or reordered ("no booking before payment"); injection is confined to a single node | Handles the unforeseen: layovers, cancellations, mid-flow changes |
| Weakness | Can only follow preset exception branches or hand off | Costlier; errors compound; needs explicit stop conditions |
| Fits | Compliance-critical, decomposable processes | Open-ended tasks with unpredictable step counts (SWE-bench, computer use, research) |

Real systems **mix them**: compliance-critical spine as workflow, flexible parts as agent nodes (n8n canvases do this visually). Anthropic's three principles for either: **keep it simple** (direct API calls over frameworks), **keep it transparent** (show plans, logs, trajectories), and **design the ACI** (agent–computer interface) so misuse is impossible. That is *poka-yoke*: like the SIM card's notched corner, the tool should only fit one way. Depth: [harness 07 — orchestration](../../ai-engineering/03-harness-engineering/notes/07-orchestration.md).

---

## Guardrails

Guardrails are defense in depth. No single one suffices, so layer specialized ones, starting with the risks you've already seen.

| Position | Mechanisms |
|---|---|
| Input | Relevance classifier (off-topic); safety classifier (jailbreak = user attacks directly; prompt injection = attacker acts via external data); content moderation; rules (blocklists, length limits, regex) |
| Execution | Tool risk rating by reversibility, permission level and financial impact; high risk → review or human confirmation |
| Output | PII filter; brand/content validation |

**Constitutional Classifiers** (Anthropic, 2026) is the reference design for classifier guardrails:

- A natural-language constitution generates the synthetic training data.
- The question and answer are judged together, so "food flavorings" can be read as code for reagents.
- Screening has two stages. A near-free activation probe sees every conversation, and anything suspicious goes to a stronger classifier rather than straight to refusal. Stage one can therefore over-flag cheaply.

**Escalate to a human** when a failure threshold is exceeded (retries or operations past their cap) and before high-risk operations (cancellations, large refunds, payments), at least until reliability is proven. Depth: [harness 04 — execution boundaries](../../ai-engineering/03-harness-engineering/notes/04-execution-boundaries.md).

---

→ Next: [harness 01 — what a harness is](../../ai-engineering/03-harness-engineering/notes/01-what-a-harness-is.md) — the production view: Model + Harness.
