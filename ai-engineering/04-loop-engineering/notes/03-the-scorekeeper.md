---
origin: web-authored
sources:
  - https://notes.kodekloud.com/docs/Loop-Engineering/What-Is-a-Loop/The-Scorekeeper/page.md
  - https://notes.kodekloud.com/docs/Loop-Engineering/Components/Sub-agents/page.md
  - https://www.langchain.com/blog/the-art-of-loop-engineering
  - https://claude.com/blog/building-agents-with-the-claude-agent-sdk
  - https://www.aibuilderclub.com/blog/loop-engineering-anthropic-playbook
  - https://adk.dev/agents/workflow-agents/loop-agents/
  - https://github.com/karpathy/autoresearch
confidence: high
cleaned: 2026-10-28
---
# 3 — The Scorekeeper

> Capability level 2: the verification loop. The scorekeeper decides what "correct" means. A loop without one can run forever and never know if it is winning.

---

## Why it carries the load

In a loop the generator runs cheaply, over and over. The **scorekeeper** (also called the verifier or grader) decides whether all that motion turns into value or slop.

Anthropic's own data says the same. In their web-app example, Claude did much better once it had browser-automation tools and was told to test features the way a human would, because it could then find bugs that were invisible from the code alone. Verification, not a better prompt, is what improved the results.

> **Build the verifier before you scale the generator.** A generator that can't check itself just produces plausible-looking work faster.

LangChain's level-2 loop wraps the agent in a grader that checks output against criteria and feeds failures back. They state the trade-off plainly: *"adding verification increases latency and cost per run. It's worth it when quality matters more than speed"*, which is most production use.

---

## What a scorekeeper is

The mechanism that turns work into a **result the loop can read**: a test suite, a build that must pass, a linter, a checklist, or a rubric another agent grades against. Each pass it returns a score. Higher means progress, lower means a regression, and without the signal the loop cannot tell progress from noise.

### The four traits (KodeKloud)

| Trait | Why it matters |
|---|---|
| **Objective** | Same work gives the same result every time. No randomness or guesswork |
| **Automatic** | One command or CI trigger. No manual step |
| **Fast** | Cheap enough to run every pass, so failures show up immediately |
| **Clear** | One unambiguous score, so the loop knows exactly where it stands |

### Plus the fifth: hard to fake

If the loop can pass by cheating (faking outputs, editing the tests, skipping the real work) the score becomes a lie, and the loop reports success while the system stays broken. **A loop that can lower the bar will take the easiest path to green.**

| Defense | How |
|---|---|
| **Held-out checks** | Keep some checks hidden from the loop during normal passes; run them only as the final gate. Stops the loop overfitting to the visible tests |
| **Tamper-proof location** | Scoring logic lives where the loop can't write: another repo, a protected CI job, read-only paths |
| **Auditable artifacts** | Logs and outputs needed for verification are immutable or diffable |
| **Watch the trend** | Track the score across runs, not just single passes. A sudden jump is a reason to look, not to celebrate |

---

## The write boundary

The cleanest example of "hard to fake" is Karpathy's `autoresearch` (full case in [note 08](08-self-improving-loops.md#the-worked-example-autoresearch)):

| File | Who writes it | Why |
|---|---|---|
| `train.py` | **Agent** | The search space |
| `prepare.py` (evaluation) | **Nobody**. The agent cannot touch it | The verifier must not be editable by the thing it grades |
| `program.md` | **Human** | The contract |

> An agent that can edit its own evaluator does not have a verifier; it has a negotiation.

Enforce the boundary **structurally** (file permissions, a hook that blocks writes, a separate repo), not just with an instruction in the prompt. Instructions are suggestions; permissions are rules. See [harness note 04](../../03-harness-engineering/notes/04-execution-boundaries.md#encode-constraints-dont-document-them).

---

## Deterministic first, model judgment above the floor

Masood's rule: **anchor on deterministic checks** (tests, compilers, linters, type checkers, schema validation) and use model judgment only *above* that floor, for things no check can express.

| Layer | Example | Gameable? |
|---|---|---|
| Deterministic | `pytest`, `tsc`, link checker, "diff touches only `src/auth/`" | Only by editing the check, so protect it |
| Rubric + separate model | "Does the PR description explain *why*?" graded against written criteria | Somewhat. Needs a fixed rubric and a grader that isn't the maker |
| Human | Taste, architecture, "should this exist?" | No, but it's slow and doesn't scale |

If the end state can only be described as "looks right," you have no scorekeeper yet. Stay at autonomy rung 1 ([note 07](07-autonomy-ladder.md)) until you can write one.

---

## Maker and checker

The maker trusts its own output and misses its own mistakes. Split the roles:

- **Maker** produces the change.
- **Checker** reviews it: a fresh agent with its own instructions and stricter rules, often a stronger model, and **without the maker's history**.

Three sources, one pattern:

| Source | Maker | Checker |
|---|---|---|
| Osmani | implementer sub-agent | verifier sub-agent |
| LangChain L2 | agent loop | `RubricMiddleware` / `after_agent` grader |
| Google ADK | `RefinerAgent` | `CriticAgent` ([note 10](10-framework-bindings.md)) |

A checker must be allowed to return **"clean."** A reviewer that cannot pass the work will make up findings. The same rule protects evolve loops ([note 08](08-self-improving-loops.md#the-anti-busywork-rule)).

---

## Write it first

> **Write the scorekeeper before the loop.** Defining it up front makes "done" explicit and gives every later decision something to measure against.

Quick checklist:

- [ ] Tests or rubric written before the loop's first pass
- [ ] Scoring runs automatically (one command / CI job)
- [ ] Some checks held out for the final gate
- [ ] Scoring logic outside the loop's write scope
- [ ] Checker is a different agent from the maker, and can return "clean"
- [ ] Score trends are visible across runs

---

## Deeper in the harness layer

[Harness note 05: Verification loops](../../03-harness-engineering/notes/05-verification-loops.md) covers the machinery underneath this note: the three-layer termination check, asymmetric QA, grading criteria over vibes, loop detection, the retry taxonomy and eval-first development. This note covers *what* to measure; that one covers *how the harness enforces it*.

For the scorekeeper as an eval artifact (building its dataset, calibrating a judge-based scorekeeper, telling a real gain from noise, and how optimizers game it), see [06-eval](../../06-eval/README.md): [04 — Graders](../../06-eval/notes/04-graders.md), [05 — LLM-as-judge](../../06-eval/notes/05-llm-as-judge.md), [09 — Reading results](../../06-eval/notes/09-reading-results.md) and [12 — When evals go wrong](../../06-eval/notes/12-failure-modes.md#goodhart-the-eval-becomes-the-target).

---

## Working reference

`~/.claude/refs/agent-eval.md` — graders, rubrics, held-out sets.

---

→ Next: [04-building-blocks.md](04-building-blocks.md) — the six parts that surround the scorekeeper.
