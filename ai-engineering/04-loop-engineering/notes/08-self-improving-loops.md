---
origin: web-authored
sources:
  - https://www.langchain.com/blog/the-art-of-loop-engineering
  - https://www.aibuilderclub.com/blog/self-improving-agent-loops
  - https://github.com/karpathy/autoresearch
  - https://arxiv.org/abs/2603.23420
  - https://www.anthropic.com/institute/recursive-self-improvement
confidence: medium
cleaned: 2026-10-28
---
# 8 — Self-Improving Loops

> Capability level 4: the hill-climbing loop. The first three levels automate work; this one automates improvement. Practitioner scale first, then the frontier.

---

## Level 4 in one sentence

LangChain: trace → analysis agent → rewritten harness config (prompt tweaks, tool changes, grader refinements). *"The return arrow doesn't just loop back to the top — it reaches inside and updates the agent loop directly."* For open-weight models the same traces can feed an RL fine-tuning pipeline.

The same shape appears at three scales:

| Scale | What gets rewritten | Example |
|---|---|---|
| Practitioner | The loop's config files | The evolve loop (below) |
| Research | The training code, or the search method itself | `autoresearch`, bilevel autoresearch |
| Frontier | The next model | Recursive self-improvement |

---

## The evolve loop

> **An evolve loop is a loop with a second, slower loop pointed at it. The fast loop does the work. The slow loop edits the fast loop.**

It **doesn't retrain weights, it rewrites files**. What improves is the scaffolding (contract, state, triggers, procedure) while the model stays fixed. That's why any practitioner can run one today.

### Cadence and inputs

The slow loop runs about **every 5–10 runs of the fast loop**: often enough to catch drift, rarely enough that there's real evidence to read. It reviews three inputs:

1. **Configuration**: contract, goals, boundaries. *What did we say success was?*
2. **State and logs**: what the agent believed vs what happened. *Where did its picture of the world diverge from the world?*
3. **Raw conversation history**: where the agent flailed. The richest input, because the thrashing points to cheap structural fixes no metric shows.

### The four edit targets

| Target | What gets rewritten | Symptom that triggers it |
|---|---|---|
| **Contract** | The definition of success | Loop "succeeds" on runs you'd call failures |
| **State** | Stale or wrong entries | Agent acts on facts that expired |
| **Trigger logic** | When the loop wakes | Wakes constantly, finds nothing to do |
| **SOP steps** | The mechanical procedure | Same manual correction, every run |

**Worked example (Superdesign's support triage loop).** An expensive trigger kept waking the agent to find no work. The evolve run wrote a small script: fetch support-platform updates from the last 30 minutes, and wake the agent only when real work exists. No human designed that fix. The slow loop read the logs, saw the empty wakeups and rewrote its own trigger. The improvement was **structural and deterministic**, not a better prompt.

### The anti-busywork rule

The most important guardrail, learned from a production failure:

> **Agents default to doing something even when nothing needs doing.**

Ask an evolve session "what should change?" and it will always answer, inventing plausible edits to justify having run. Those edits degrade a working loop.

**The fix: make `no change needed` an explicit, successful outcome** in the evolve contract. If "no change" counts as failure, you have built a machine that damages itself on a schedule. The same rule applies to any reviewer or critic: *a reviewer that cannot return "clean" is a reviewer that invents findings* ([note 03](03-the-scorekeeper.md#maker-and-checker)).

### Evolve-loop failure modes

1. **Invented improvements**: changes made up to justify the run. Countered by the rule above.
2. **State rot**: state is one of the three inputs, so bad state → bad diagnosis → worse state.
3. **Compounding errors**: the next evolve session reads a config that is already wrong and reasons forward from it.
4. **Scope limit**: it can improve a loop but **can't decide whether the loop should exist**. A well-tuned loop doing useless work will tune itself further into uselessness. That judgment stays human.

Start it at autonomy rung 1 ([note 07](07-autonomy-ladder.md)), with a human approving each config diff, and climb only once the diffs are boring.

---

## The worked example: `autoresearch`

Karpathy's `autoresearch` (released 2026-03-06, MIT, ~630 lines of Python) is the smallest artifact that shows the level-4 shape. It's small enough to hold in your head.

Setup: **one Python file, one GPU, one metric.** The agent reads the code, proposes a change, runs a ~5-minute training run, checks whether validation improved, keeps or discards, and repeats.

The load-bearing decision is the **write boundary**: the agent edits `train.py`, nobody edits `prepare.py` (evaluation), the human writes `program.md` ([note 03](03-the-scorekeeper.md#the-write-boundary)).

**Results:** 700 experiments over two days → **20 real, stackable improvements**, cutting GPT-2 training from **2.02 → 1.80 hours (11%)**. Shopify's Tobi Lütke reported 19% on the same setup after 37 experiments.

The hit rate is **under 3%**. The loop isn't valuable because it's clever. It's valuable because a 3% hit rate is fine when attempts are cheap and unattended. *"If you have an objective metric, you are the bottleneck."* Humans tire after a dozen experiments; the loop doesn't.

The prerequisite limits where this transfers: **an automatic gate that can fail the work.** Model training, refactors, content rewrites and pipeline tuning qualify. Work whose success is only "looks right" doesn't.

### Bilevel autoresearch

[arXiv:2603.23420](https://arxiv.org/abs/2603.23420) (Qu & Lu, 2026-03-24) closes the circle: an outer loop reads the inner loop's traces and **writes new search mechanisms as Python code, injected at runtime.** The inner loop optimizes the task; the outer loop optimizes *how the inner loop searches*.

- **5× improvement** over the inner loop alone (−0.045 vs −0.009 val_bpb) on Karpathy's GPT pretraining benchmark.
- **Tuning parameters without changing the mechanism gave no reliable gain.** The outer loop had to write new *code*, the same lesson as the evolve loop's "rewrite files, not weights."
- **Both loops use the same model.** The gain comes from loop *structure*, not model capability. That's the strongest available evidence for this pillar's main claim.

The outer loop reached for combinatorial optimization, multi-armed bandits and design of experiments without being told those fields existed.

---

## At the frontier: recursive self-improvement

Anthropic's institute piece takes level 4 to its endpoint: AI systems that design and build their successors. The escalation it traces runs from humans writing code (2021–23), to chatbots emitting snippets (2023–25), to agents writing whole files (2025–26), to systems that build and train models.

Measurements worth quoting when arguing about loop horizons:

- The length of task an AI completes on its own is **doubling every ~4 months** (was ~7). ~4-minute tasks (Claude Opus 3, Mar 2024) → 12-hour tasks (Claude Opus 4.6, 2026).
- **>80% of merged production code at Anthropic written by Claude** (May 2026), up from single digits before Feb 2025.
- CORE-Bench (research reproduction): ~20% in 2024 → saturated within 15 months.
- On open-ended research problems, models chose a better next step than humans **64%** of the time (Apr 2026), up from 51% (Nov 2025).

The risk that connects back to every scale: an **Amdahl's-law bottleneck**. Automating development moves the constraint onto human review and verification. From a nightly test-fixer to a self-improving lab, **the limit becomes verification capacity, not generation capacity.**

> *"The comparative advantage of humans as of right now is still in seeing the bigger picture and thinking beyond the confines of the immediate task."*

---

## Design checklist

- [ ] Is the evolve cadence tied to *runs* (5–10), not wall-clock time?
- [ ] Does the evolve contract explicitly allow "no change needed" as success?
- [ ] Is state pruned and expired as a maintained step, or does it just pile up?
- [ ] Is the evaluator outside the write scope of every loop that's being improved?
- [ ] Are evolve diffs reviewed by a human, and are they getting more boring over time?
- [ ] Who decides whether this loop should exist, and when do they revisit it?

---

## Working reference

`~/.claude/refs/agent-context.md` — prompt versioning (the artifacts an evolve loop edits); `~/.claude/refs/agent-observability.md` — the traces the slow loop reads.

---

→ Next: [09-failure-modes-and-guardrails.md](09-failure-modes-and-guardrails.md) — how loops go wrong, and the rules that stop them.
