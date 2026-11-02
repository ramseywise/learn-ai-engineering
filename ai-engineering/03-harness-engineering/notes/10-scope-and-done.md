---
origin: web-authored
sources:
  - https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
  - https://openai.com/index/harness-engineering/
  - https://github.com/walkinglabs/learn-harness-engineering
  - "Karpathy, AISN 2026 talk (secondary: YouTube breakdown)"
confidence: medium
cleaned: 2026-11-01
---
# 10 — Scope and Done

> An agent left alone starts five things and finishes none. Limit it to one active feature, and let a passing check be the only way that feature counts as done.

The [acceptance baseline](01-what-a-harness-is.md#the-four-parts) from note 01, made concrete for a coding agent: a feature list in the repo that defines the work, gates completion, and carries state between sessions. Adapted from *learn-harness-engineering* lectures 07–08.

---

## Overreach and under-finish

Ask an agent to "add user registration" and it will create the model, write the route, notice email verification and add a mail service, add password hashing, decide the error middleware is inconsistent and refactor it, then reorganize the test directory. Six things are touched, none of them work end to end, and the next session gets a pile of coupled half-implementations.

Anthropic's long-running-agents post names this directly: broad prompts make agents **start multiple things rather than finish one.** Two failures feed each other:

- **Overreach.** More tasks active than the session can finish.
- **Under-finish.** Of the activated tasks, too few pass end-to-end verification.

Overreach spreads attention thin, which causes under-finish. The half-done code raises complexity, which invites more overreach. Humans have a sense of "that's enough for now". Agents don't: one more "while I'm here" costs nearly nothing to generate. It's the same queueing math as Kanban (Little's Law): more work in progress means longer lead time per item and more items that never land.

The tell is that **lines of code written goes up while verified features stay flat.**

---

## Before the list: the spec

A feature list is only as good as the understanding behind it. Karpathy (as relayed from his AISN 2026 talk) puts the spec first: it is how your understanding reaches the model. He finds plan mode too high-level: *"you have to work with your agent to design a spec that is very detailed."* Three disciplines:

1. **Uncover the goal, not the task.** "Create an end-of-month report" is a task. The goal is the decision the report drives, and it is the one thing the model can never infer. Extract it on purpose, for example: *"interview me to identify the goal of this project."*
2. **Agile specs, not waterfall.** People hand an agent everything at once because delegation feels efficient. Bias toward smaller, compartmentalized specs with a checkpoint, a review and an adjustment each round. This is WIP = 1 below, applied to the spec.
3. **Precision with explicit sign-off.** Every assumption the model makes is a chance to drift. When the model drafts the spec, have it ask: *"make me verify key decisions explicitly."*

The feature list below is that spec in a form the harness can check.

---

## WIP = 1

The default for a coding-agent harness: **exactly one feature is `active` at any time.** The next starts only after the current one passes verification or is explicitly marked `blocked`.

```markdown
## Work rules                       (AGENTS.md)
- One feature at a time.
- Start the next only after the current one passes end-to-end verification.
- Don't "also refactor" B while implementing A. Note it in progress.md instead.
- A narrow supporting fix is allowed only when it blocks the active feature.
```

A small **next-task block** at the start of each feature keeps the scope honest:

```markdown
- Active feature:
- Why it's next:
- What counts as passing:
- What must NOT change during this step:
```

The last line matters most. Naming what is out of bounds is cheaper than reverting it afterwards.

Track the **verified completion rate (VCR)** = verified features ÷ activated features. Under WIP=1 it should sit at 1.0 between features. A harness can refuse to activate a new feature while VCR < 1.

---

## The feature list is a primitive, not a memo

Compare a typical progress note:

```
Did user auth, cart mostly done, still need payments
```

What does "mostly done" mean? Which cart checks pass? What's blocking payments? A fresh session can't tell, so it re-derives everything or reimplements finished work.

A feature list differs from a memo because **other parts of the harness read it:**

| Component | Uses the list to |
|---|---|
| **Scheduler** | Pick the next `not_started` feature by priority and dependencies |
| **Verifier** | Run that feature's checks and decide whether the state may change |
| **Handoff reporter** | Generate "what's passing / active / blocked" with no prose |
| **Progress tracker** | Count states for project health; the remaining non-passing count is the back-pressure |

A document can be ignored. A primitive is a constraint like a database check: other parts of the harness depend on it, so the agent can't route around it.

---

## The triple

Every entry has three parts, and is incomplete without any one:

| Part | Tells the agent |
|---|---|
| **Behavior** | What to build, as user-visible behavior, not implementation |
| **Verification** | What counts as done: executable steps or a command |
| **State** | Where it stands now |

Plus **evidence** once it passes: a commit, test output or screenshot.

```json
{
  "id": "cart-002",
  "priority": 2,
  "depends_on": ["cart-001"],
  "user_visible_behavior": "POST /api/cart/items with {product_id, quantity} returns 201 and the item appears in GET /api/cart",
  "verification": [
    "curl -s -o /dev/null -w '%{http_code}' -X POST localhost:3000/api/cart/items -d '{\"product_id\":1,\"quantity\":2}'  → 201",
    "curl -s localhost:3000/api/cart | jq '.items | length'  → 1"
  ],
  "status": "passing",
  "evidence": ["commit abc123", "logs/verify-cart-002.txt"]
}
```

A JSON Schema for the file lets a pre-commit hook reject entries missing any part of the triple.

---

## States and the pass gate

```mermaid
stateDiagram-v2
  [*] --> not_started
  not_started --> active: scheduler picks it (WIP = 1)
  active --> passing: verification run succeeds
  active --> blocked: explicit blocker recorded
  blocked --> active: blocker resolved
  passing --> [*]
```
*Image Source: diagram based on learn-harness-engineering, lecture 08*

Four states only. The important rule is **pass-state gating: the only way into `passing` is a successful run of that feature's verification.** Ideally a script runs the checks and flips the state. The agent requests verification; it doesn't edit the status field to say it passed.

The gate is short to write, which leaves little excuse for trusting an agent's word. Here is one, with the VCR refusal from [WIP = 1](#wip--1). The agent calls `request_pass`, and only a zero exit code from the feature's own check changes the state. The check commands are stubs so that the script runs anywhere.

```python
import subprocess
import sys

PASS = [sys.executable, "-c", "raise SystemExit(0)"]
FAIL = [sys.executable, "-c", "print('POST /cart returned 500'); raise SystemExit(1)"]

features = [
    {"id": "cart-001", "behavior": "User can add an item to the cart",
     "verify": PASS, "state": "active"},
    {"id": "cart-002", "behavior": "Cart total updates when quantity changes",
     "verify": FAIL, "state": "not_started"},
    {"id": "cart-003", "behavior": "User can remove an item",
     "verify": PASS, "state": "not_started"},
]

def request_pass(feature):
    """The agent asks. Only a zero exit code moves the state."""
    run = subprocess.run(feature["verify"], capture_output=True, text=True)
    if run.returncode == 0:
        feature["state"], feature["evidence"] = "passing", "verify exited 0"
    else:
        feature["evidence"] = run.stdout.strip()
    return feature["state"]

def vcr(items):
    """Verified completion rate: verified / activated."""
    activated = [f for f in items if f["state"] != "not_started"]
    verified = [f for f in activated if f["state"] == "passing"]
    return len(verified), len(activated)

def activate(item, items):
    done, started = vcr(items)
    if done < started:
        return f"refused: VCR {done}/{started}, finish or block the active feature"
    item["state"] = "active"
    return f"{item['id']} is active"

print("cart-001 ->", request_pass(features[0]))
print(activate(features[1], features))
print("cart-002 ->", request_pass(features[1]), "|", features[1]["evidence"])
print("VCR", "{}/{}".format(*vcr(features)))
print(activate(features[2], features))

features[1]["verify"] = PASS  # stands in for fixing the code, with the check unchanged
print("cart-002 ->", request_pass(features[1]))
print("VCR", "{}/{}".format(*vcr(features)))
print(activate(features[2], features))
```

Output:

```text
cart-001 -> passing
cart-002 is active
cart-002 -> active | POST /cart returned 500
VCR 1/2
refused: VCR 1/2, finish or block the active feature
cart-002 -> passing
VCR 2/2
cart-003 is active
```

`cart-002` stayed `active` when its check failed, and `cart-003` couldn't start until the rate returned to 1.0. Notice what the agent can't do here: no call sets the state directly, and nothing in `request_pass` reads a claim from the model. In a real harness, keep `feature_list.json` writes behind this function and put the check commands where the agent can't change them mid-implementation.

A feature may move to `passing` only when:

- the expected workflow was actually exercised
- the evidence is recorded
- no blocking error is present on the tested path
- the app isn't left broken or ambiguous

Rules worth stating explicitly in `AGENTS.md`, because each one is a shortcut agents take:

- Don't mark complete just because code was added.
- Don't rewrite the feature list to hide unfinished work.
- Don't weaken or delete tests to make a feature pass.
- Don't change the verification rules mid-implementation.

---

## Granularity

**One feature should be finishable in one session.**

| Too broad | Right | Too narrow |
|---|---|---|
| "Implement the shopping cart" | "User can add an item to the cart" | "Add `name` field to Cart model" |
| "Implement indexing" | "Split imported docs into chunks" · "Persist chunk metadata" · "Show indexing status in UI" · "Add a re-index action" | — |

Too broad and it never finishes inside the WIP=1 limit. Too narrow and list management costs more than the work. Write behaviors from the user's side, and let dependencies (`depends_on`) carry the order, which turns the list into a small DAG.

---

## Strict vs. loose verification

The value of the list depends on the strength of its checks:

| Loose (false positives) | Strict |
|---|---|
| "Code compiles" | "E2E test for the flow passes" |
| "Component renders" | "User can click New Chat and see an empty thread" |
| "Endpoint exists" | "POST returns 201 and the item is retrievable" |

Loose checks give you a list of `passing` features that don't work. When in doubt, verify the *behavior* the user would see, not the artifact the agent wrote. Layered checks and E2E are covered in [note 05](05-verification-loops.md#the-three-layer-termination-check).

---

## Single source of truth

Every "what's left to do" lives in the feature list, not in chat history, TODO comments or a side note. If scope shows up anywhere else, either move it into the list or delete it. Two sources of scope will eventually disagree, and the agent will pick one at random.

---

## Pitfalls

- **Broad prompts.** Symptom: "add user registration" becomes a mail service, an error-middleware refactor and a reorganized test directory, with lines written rising and verified features flat. Fix: WIP = 1, plus a next-task block whose last line names what is out of bounds.
- **A progress memo instead of a primitive.** Symptom: "cart mostly done", and a fresh session re-derives everything. Fix: a feature list that the scheduler, verifier and handoff reporter actually read.
- **Letting the agent set `passing`.** Symptom: features pass because code was added, or the list was rewritten to hide unfinished work. Fix: pass-state gating, so a script runs the checks and flips the state.
- **Weakening the check to get through.** Symptom: tests deleted or rules changed mid-implementation. Fix: state the prohibitions in `AGENTS.md`, and keep the check outside what the agent edits.
- **Loose verification.** Symptom: a list of `passing` features that don't work, verified by "code compiles" or "endpoint exists". Fix: verify the behavior a user would see, such as "POST returns 201 and the item is retrievable".
- **Wrong granularity.** Symptom: "implement the shopping cart" never finishes inside the limit, while "add `name` field to Cart model" makes list management cost more than the work. Fix: one feature, finishable in one session, written from the user's side.
- **Two sources of scope.** Symptom: chat history, TODO comments and the list disagree about what's left. Fix: move the item into the feature list or delete it.

## Try it

1. Five features were activated and three verified. What is the VCR, and what may the harness do next?

   <details><summary>Answer</summary>

   VCR = 3/5 = 0.6. Under WIP = 1 it should be 1.0 between features, so the harness refuses to activate a new one until the other two pass verification or are explicitly marked `blocked`. Two features being open at all is itself a sign the limit wasn't enforced.

   </details>

2. Rewrite "Implement the export feature" into a triple with a strict check.

   <details><summary>One good answer</summary>

   Behavior: "User can download their cart as a CSV." Verification: "An E2E test clicks Export and the file has one row per item with the correct total." State: `not_started`, with evidence added once it passes. A loose version would be "the export endpoint exists", which passes without working. Split further if it won't finish in one session.

   </details>

3. Change the script above so that `activate` also accepts `blocked` features as finished. Which line changes, and what does it let through?

   <details><summary>Answer</summary>

   Have `vcr` drop `blocked` items from the `activated` list, for example with `f["state"] not in ("not_started", "blocked")`. A feature marked `blocked` then no longer holds up the next, which matches the rule that the next starts after a pass or an explicit `blocked`. It also lets an agent escape a hard feature by marking it blocked, so log who set that state and review it.

   </details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| What are overreach and under-finish? | Overreach is more tasks active than a session can finish, and under-finish is too few of them passing end-to-end verification. They feed each other, and the tell is lines written rising while verified features stay flat. |
| What is verified completion rate? | Verified features divided by activated features. Under WIP = 1 it sits at 1.0 between features, and a harness can refuse to activate a new one below that. |
| Why is a feature list a primitive rather than a memo? | Other parts of the harness read it: the scheduler, verifier, handoff reporter and progress tracker. A document can be ignored, while a primitive works like a database check. |
| What's in a feature entry? | The triple: behavior as user-visible behavior, verification as executable steps or a command, and state. Evidence such as a commit or test output is added once it passes. |
| How does a feature get to `passing`? | Only by a successful run of its own verification, ideally through a script that flips the state. The agent requests verification rather than editing the status. |
| Your team wants faster delivery and proposes WIP = 3 for the agent. What's your response? | The cost is half-done code that raises complexity and invites more overreach. Keep WIP = 1 per agent, and if you need parallelism, use isolated agents with their own worktrees and progress files. |

## Next

[04-loop-engineering](../../04-loop-engineering/README.md): run the harness again, against a goal, until a scorekeeper says stop.
