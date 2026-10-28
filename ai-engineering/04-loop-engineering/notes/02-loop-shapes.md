---
origin: notion-export
sources:
  - https://machinelearningmastery.com/an-introduction-to-loop-engineering/
  - https://www.mindstudio.ai/blog/what-is-loop-engineering-ai-coding-agents
  - https://medium.com/@adnanmasood/loop-engineering-a-guide-for-engineers-and-practitioners-893bb65ea943
  - https://www.langchain.com/blog/the-art-of-loop-engineering
  - https://vercel.com/i/what-are-agentic-workflows
  - https://claude.com/blog/building-agents-with-the-claude-agent-sdk
  - https://www.aibuilderclub.com/blog/loop-engineering-anthropic-playbook
confidence: high
cleaned: 2026-10-28
---
# 2 — Loop Shapes

> The five parts every loop needs, the skeleton they make, and which pattern fits which task. Design the shape before you write the prompt.

---

## Loop shape before prompt

Anthropic built Claude Code around one loop (gather → act → verify → repeat), then extracted the Claude Agent SDK so teams could "build their own agents on the same machinery instead of maintaining a homegrown loop." The message: **the loop is the reusable object, not the prompt inside it.**

Before tuning any prompt, answer the shape questions:

- What context does each pass **gather**?
- Which **tools** can it act with?
- How is "done" **judged**?
- When does it **stop** if "done" never arrives?

Each answer is a line in the skeleton below. A prompt cannot fix a missing line.

---

## The five required parts

ML Mastery, MindStudio and Masood agree on these. A loop missing any one will hang, thrash, or quietly ship garbage.

| Part | What it means | Missing it looks like |
|---|---|---|
| **1. Testable goal** | Specific enough to evaluate. "Make all auth tests pass." | Loop never finishes; scope drifts |
| **2. Tool set** | Real access to the environment: code execution, filesystem, terminal, test runner, docs lookup | The agent can't see consequences, so it guesses repeatedly |
| **3. Context management** | Summarize and prune earlier passes into compact working memory | Token overflow; the agent forgets what it tried |
| **4. Termination logic** | *Layered, independent* exits: success check, iteration cap, budget cap, stall detector, escalation to a human | Runs forever or stops at random |
| **5. Error handling** | Tell recoverable errors from hard blockers; change strategy based on error type | Retries the same failed approach |

Part 1 is half of the foundation from [note 01](01-what-a-loop-is.md#two-things-before-anything-runs). The other half, the scorekeeper, is what part 4's success check calls ([note 03](03-the-scorekeeper.md)).

---

## The canonical skeleton

```
initialize state with goal
for step in range(MAX_STEPS):
    reason about current state                  # the model
    choose a concrete action                    # the model
    execute the tool against the real environment
    update state with the outcome
    compact context to prevent overflow
    if scorekeeper says goal met: save; return success
    if score went down: roll back this step
    if no progress for N steps or budget exhausted: escalate
escalate to human  # cap reached, not success
```

*"Engineering is everything wrapped around"* the model (Masood). The model supplies two lines; every other line is yours.

Two lines come from the KodeKloud course and are worth making explicit: **save** on success, and **roll back** on a score drop. Together they make progress a ratchet: the score only goes up. See [note 09](09-failure-modes-and-guardrails.md#the-two-ratchet-rules).

---

## Loop patterns: pick by task shape

| Pattern | Use when | Shape |
|---|---|---|
| **Retry** | Atomic task, clear pass/fail | act → check → act again with the error |
| **Plan–Execute–Verify** | Multi-step work where order matters | plan once, run steps, verify each |
| **Explore–Narrow** | Unfamiliar territory | fan out in parallel, then converge on the best lead |
| **Human-in-the-loop** | Ambiguity or high stakes | pause at decision points for approval |

### Planning variants inside the agent loop

| Variant | How it plans | Trade-off |
|---|---|---|
| **ReAct** | Reason → act → observe, one step at a time | Adaptive; can wander on long tasks |
| **Plan-then-Act** | Write the full plan up front, then execute | Predictable; brittle when step 3 invalidates step 5 |
| **Plan-and-Revise** | Plan up front, re-plan when an observation breaks it | The usual production compromise |

For long work the plan should live in a file, not in the context window, so a fresh pass can read and revise it. See [harness note 06](../../03-harness/notes/06-long-horizon-execution.md#plans-as-first-class-artifacts).

### Vercel's sequencing advice

Vercel groups agentic workflows into **planning**, **tool use**, **reflection** and **multi-agent collaboration**, and gives an order for adding them:

1. Start with **tool use**.
2. Add **reflection** (a verification pass) once that is stable.
3. Introduce **planning** and **multi-agent** only after eval infrastructure exists.

That is the green-first rule from [note 01](01-what-a-loop-is.md#green-first) applied to patterns: each one is added in response to a failure you have measured.

---

## Loop vs workflow vs graph

| | Workflow | Loop | Graph |
|---|---|---|---|
| Control flow | Fixed by your code | Decided by feedback each pass | Explicit nodes and edges, may contain loops |
| Use when | Steps are known in advance | Steps depend on what the last one found | Several loops or agents must hand off |
| Layer | prompt / harness | **this pillar** | [05-graph](../../05-graph/README.md) |

Start at the left column and move right only when the task forces you to.

---

## Working reference

`~/.claude/refs/agent-architecture.md` — loop shapes, planning variants, turn termination control.

---

→ Next: [03-the-scorekeeper.md](03-the-scorekeeper.md) — the part of the loop everything else depends on.
