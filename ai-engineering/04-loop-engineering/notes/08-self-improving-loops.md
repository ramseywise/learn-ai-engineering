---
origin: web-authored
sources:
  - https://www.langchain.com/blog/the-art-of-loop-engineering
  - https://www.aibuilderclub.com/blog/self-improving-agent-loops
  - https://github.com/karpathy/autoresearch
  - https://github.com/walkinglabs/learn-harness-engineering (lecture 13)
  - https://arxiv.org/abs/2603.23420
  - https://www.anthropic.com/institute/recursive-self-improvement
  - "Bojie Li, AI Agents in Depth (2026), ch. 8 — https://github.com/bojieli/ai-agent-book"
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

## Verify before you learn

> **Preserving experience is not learning from it.** A vector store full of trajectories lets the agent look up a case. It doesn't compare cases, separate a sound strategy from a lucky one, or notice that a fix only worked on an old API. Learning happens when the system evaluates, compares, generalizes and validates.

The evolve loop's input is only as good as its verdict on each run. If the system doesn't know which step caused a success or a failure, a model-written reflection is just a guess. Once that guess lands in a prompt or in training data, it compounds. A correct outcome also doesn't prove a correct process. Tests pass when the failing tests are deleted. A customer is "satisfied" when promised a refund that never happens.

Li (*AI Agents in Depth*, ch. 8) splits verification into three layers. Each one rests on harder evidence than the layer above it:

| Layer | Question | Evidence |
|---|---|---|
| Outcome | Was the task actually completed? | Environment state, test results, tool returns (code) |
| Process | Was it done in an allowed way? | Policies, permissions, action order (code) |
| Quality | Was it handled well? | Rubric scored by an LLM, item by item, with cited turns |

Only what code can't formalize goes to the LLM layer. **Promise–action consistency** is the check that matters most for agents: for every "I've submitted your refund", confirm the refund tool was called, succeeded and changed the order state.

Keep the result **structured, not scalar**. "Partially succeeded, one unsupported claim, one false promise, policy repeated three times" tells the next step *what* to edit. The unsupported claim points to missing knowledge or a missing citation rule. The false promise points to a harness consistency check. A single 0.57 points nowhere. Calibrate the LLM layer against a small expert-labelled set, and re-run that set when the model version changes. Send low-confidence or high-risk runs to a second verifier or a human. Finally, keep the **verifier and the editor separate**, so the model that judges a run is not the one that rewrites the rules.

Lab: [practice/02-trajectory-verifier](../practice/02-trajectory-verifier/README.md) builds the three layers and compares them with a single score on four labelled trajectories.

---

## Where the lesson goes: four media

The [four edit targets](#the-four-edit-targets) say *which part* of the loop's config to change. The book adds a second question: *what medium* should hold the lesson. The answer depends on how the capability is best represented, not on how long it has been around.

| Medium | Holds | Strength | Weakness |
|---|---|---|---|
| Experience docs | Facts, patterns, exceptions, with sources | Fast, traceable, retrieved on demand | Depends on retrieval, and on the model applying it |
| Prompt / Skill | Judgment and procedures you can state in words | Interpretable, scoped | Bloats, conflicts, gets ignored |
| Program / harness | Deterministic steps and hard constraints | Testable, stable, cheap to run | Costs more to build and maintain |
| Parameters | Perception, style, implicit strategy | Generalizes, no inference overhead | Expensive to update and to regress-test |

A lesson moves along this path as evidence builds up. It starts as an experience doc. After repeated validation it is promoted to a rule in a Skill. If it needs no language understanding, it is compiled into code. If it really is broad, implicit judgment, it goes into post-training ([gen-AI 05-RL](../../../generative-ai/05-RL/README.md)). The rule is **choose the smallest target that is easiest to validate and roll back**. A retry policy written as a prompt sentence ("don't repeat failed calls") is in the wrong medium: it belongs in code.

**Experience docs come from comparison, not summary.** Keep three layers:

1. immutable raw trajectories, for audit;
2. a structured analysis of each run;
3. documents induced across many runs of the same task family.

A strategy is recommended only when at least two non-failed trajectories support it. Each document records when it applies, the strategy, known pitfalls, exceptions, its source trajectories and when it was last validated. Test transfer on tasks that weren't used to write it. Reflexion-style self-reflection can *propose* lessons, but reflection is not evidence.

**Prompt learning means minimal diffs, not rewrites.** Karpathy calls it *system prompt learning*: notes to your future self, edited as text where RL would edit weights. From a cluster of similar failures, produce one `old → new` edit with a stated scope. Check it for conflicts with existing rules. Gate it on both the boundary cases that triggered it and a retention set of old tasks. DSPy, OPRO and GEPA do batch search offline to find a strong starting prompt. Minimal production diffs handle the long tail. For Skills, search the library first and `patch` an existing one before creating a near-duplicate.

**Compiling workflows.** A browser trajectory that repeats with different parameters can be compiled into a parameterized script, with state checks before each action, after each action, and on the final state. The script is only a `candidate` until it has been replayed from a clean reset. When any check fails, it moves to `invalid` and the agent falls back to exploring. In PreAct this gave an **8.5–13× speedup** on repeated tasks. Without the final-state check, you get 100% replay coverage on a task that never completed.

### Updating the update method

There is a second, independent axis: does the loop edit an *artifact*, or the *method that produces artifacts*? The search scope can widen like this: one rule → structured context ([ACE](https://arxiv.org/abs/2510.04618): stable-ID entries merged deterministically, so repeated rewrites don't erode detail) → how context is built ([MCE](https://arxiv.org/abs/2601.21557): an outer loop edits the retrieval and curation operators) → workflow graphs ([AFlow](https://arxiv.org/abs/2410.10762)) → harness code ([Meta-Harness](https://arxiv.org/abs/2603.28052)) → the optimizer itself ([bilevel autoresearch](#bilevel-autoresearch)). Wider scopes cost more to search, evaluate and attribute. **Default to a local patch.** Move outward only when local fixes keep failing on a cross-component problem. At every scope, the evaluators, permission boundaries and held-out tests stay outside what the loop can edit.

---

## Self-modification as a release process

An agent "modifying its own code" never means the running process overwrites itself. Each change goes through the same steps:

1. Branch from the stable version.
2. Have a coding agent write a minimal patch into an isolated candidate directory.
3. Run static checks, unit tests and a security scan.
4. Replay the failure trajectories.
5. Run the old-task regression suite.
6. Emit `release_to_canary` or `reject_candidate`. A passing candidate goes to **canary**; it never overwrites stable directly.

Two additions make the result attributable:

- **A falsifiable change contract** ([Agentic Harness Engineering](https://arxiv.org/abs/2604.25850)). Each edit records the failure evidence, the inferred root cause, the component to change, the behaviour expected to improve, the behaviour that might regress, and tests for both. It states the predicted impact *before* running, and the next round checks that prediction.
- **A bounded candidate space** ([Self-Harness](https://arxiv.org/abs/2606.09498)). Give the generator the failures, the successes it must preserve, and the previously rejected attempts. The successes say what not to break. The rejected list stops it re-submitting the same idea in new words.

Lab: [practice/03-self-modifying-agent](../practice/03-self-modifying-agent/README.md). Repeated `retryable=false` calls trigger a patch to `retry_policy.py`. The release gate replays the failures and re-tests transient-timeout recovery before it emits `release_to_canary`.

### Measuring the evolve loop itself

**Harness updating is not harness benefit** ([Lin et al.](https://arxiv.org/abs/2605.30621)). A Skill can be correct and still never be loaded, or never be followed, by a weaker task model. In that case the end-to-end score shows "no evolution", and the updater gets blamed for it. Measure the stages separately:

| Metric | Question |
|---|---|
| Candidate-change validity | Does the updater propose changes that pass independent validation? |
| Artifact activation rate | Does the task agent load the new Skill, memory or tool when it should? |
| Successful adherence rate | Once loaded, does the agent follow it? |
| Held-out task gain | Does the whole system improve on tasks the loop never saw? |

**Diagnose with a two-way model swap.** First fix the candidate harness and change only the task model:

- The strong model benefits but the weak one never activates the artifact → routing or retrieval is the bottleneck.
- Both activate it but only the strong model executes it → instruction following is the bottleneck.
- Every model regresses → suspect the change itself.

Then fix the task model and change the updater model, to compare updaters directly. Over the long run, track five things: regression, generalization, token efficiency, safety drift and **long-term engineering quality**, meaning maintainability, ownership and migration cost. Passing tests says nothing about that last one.

### Sleep learning: consolidation on a schedule

"Sleep learning" is the book's name for the offline half of a **dual loop**. The online loop finishes tasks and appends immutable evidence; it never rewrites the production agent. The offline loop runs when a threshold is reached: elapsed time, new trajectories, storage used or error rate. It has five steps:

1. **Trigger** on the threshold, while no high-priority online work is running.
2. **Orient**: read the current knowledge, prompts and Skills, and the boundaries that may not change.
3. **Consolidate**: merge duplicates, mark conflicts, prefer local patches.
4. **Validate** on transfer, retention and safety sets. High-risk writes wait for a human.
5. **Prune and re-index**: expire or archive capabilities that are unused or contradicted, while keeping their provenance and rollback versions.

Separating collection from consolidation means one lucky success or one injected web page can't immediately rewrite long-term behaviour. It also lets consolidation run in larger batches on cheaper models. Examples:

- **Claude Code's auto memory**: a bounded `MEMORY.md` index plus topic files loaded on demand.
- **Hermes**: bounded memory files, FTS session search that returns raw messages, background Skill review, and a Curator that prunes after taking a snapshot.

The maintenance list:

- Merge duplicate experience, keeping its provenance.
- Move local rules out of the global prompt and into Skills.
- Keep prompts written like an onboarding handbook, not "99 iron rules".
- Re-validate long-unused tools.
- Delete knowledge that new evidence contradicts.
- Retrain LoRAs from the base model rather than stacking them.

[Voyager](https://arxiv.org/abs/2305.16291) is the canonical complete loop. It combines an automatic curriculum (what to learn next), a skill library of verified, composable code (what was learned) and iterative prompting with environment feedback (how to tell it worked). The result was 3.3× the unique items and up to 15.3× faster tech-tree milestones than its baselines. Remove any one of the three parts and the loop stops compounding.

---

## The worked example: `autoresearch`

Karpathy's `autoresearch` (released 2026-03-06, MIT, ~630 lines of Python) is the smallest artifact that shows the level-4 shape. It's small enough to hold in your head.

Setup: **one Python file, one GPU, one metric.** The agent reads the code, proposes a change, runs a ~5-minute training run, checks whether validation improved, keeps or discards, and repeats.

The load-bearing decision is the **write boundary**: the agent edits `train.py`, nobody edits `prepare.py` (evaluation), the human writes `program.md` ([note 03](03-the-scorekeeper.md#the-write-boundary)).

Each experiment is a ratchet step: commit the change, train for a **fixed 5 minutes of wall clock**, compare validation; if better, keep the commit and append a row to `results.tsv`; if not, `git reset HEAD~1` and log the failure. The fixed budget is what makes results comparable: no change wins just by running longer. `results.tsv` is the loop's memory of every attempt, kept or not.

**The loop is written in English.** `program.md` is a methodology, not code: what to change, what to leave alone, how to judge, what to do on failure, and one iron rule, *never ask for help, keep going*. Give the agent a method, not a task, and the method becomes the loop.

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

### When "done" is not progress

The verifiable loop works best where tests, environment state or deterministic rules give fast feedback. Open-ended research and design are different. Feedback arrives late, there may be no single right answer, and the goals that matter most (research taste, long-term value) don't reduce to a score. A harness can run flawlessly and still produce things that only look like results. [Trehan & Chopra](https://arxiv.org/abs/2601.03315) made four end-to-end attempts at autonomous research, and only one completed. The failures fell into three groups:

- **Implementation drift**: when the proposed method gets hard, the agent falls back to a familiar method that no longer tests the hypothesis.
- **Epistemic over-optimism**: noise gets explained, patched and announced as a finding.
- **Missing tacit judgment**: the agent doesn't know which baseline matters or when to drop a hypothesis.

Fixing these takes structure, not a better writer:

- Separate claims from evidence, recording the provenance of every number and citation.
- Log negative results with the same standing as successes.
- Keep diverse lower-scoring branches alive in the candidate pool.
- Move human involvement *up*: defining the problem, setting the evaluation criteria, reading anomalies, deciding when to stop.

The ceiling of any self-improving loop is set by whether it can evaluate what you actually care about, not the easiest proxy for it.

The risk that connects back to every scale: an **Amdahl's-law bottleneck**. Automating development moves the constraint onto human review and verification. From a nightly test-fixer to a self-improving lab, **the limit becomes verification capacity, not generation capacity.**

> *"The comparative advantage of humans as of right now is still in seeing the bigger picture and thinking beyond the confines of the immediate task."*

---

## Design checklist

- [ ] Is the evolve cadence tied to *runs* (5–10), not wall-clock time?
- [ ] Does the evolve contract explicitly allow "no change needed" as success?
- [ ] Is state pruned and expired as a maintained step, or does it just pile up?
- [ ] Is the evaluator outside the write scope of every loop that's being improved?
- [ ] Is each run verified at three layers (outcome, process, quality), with evidence for each dimension rather than one score?
- [ ] Is each lesson in the smallest medium that holds it (doc → Skill → code → weights)?
- [ ] Does every self-edit land as a candidate with a change contract, a failure replay and a retention set before it reaches canary?
- [ ] Do you measure activation and adherence separately from whether the update was valid?
- [ ] Are evolve diffs reviewed by a human, and are they getting more boring over time?
- [ ] Who decides whether this loop should exist, and when do they revisit it?

---

## Working reference

`~/.claude/refs/agent-context.md` — prompt versioning (the artifacts an evolve loop edits); `~/.claude/refs/agent-observability.md` — the traces the slow loop reads.

---

→ Next: [09-failure-modes-and-guardrails.md](09-failure-modes-and-guardrails.md) — how loops go wrong, and the rules that stop them.
