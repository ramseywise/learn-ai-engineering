---
origin: synthesis
sources:
  - https://arxiv.org/abs/2508.09124
  - https://arxiv.org/abs/2602.16313
  - https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
  - https://docs.langchain.com/langsmith/trajectory-evals
  - "Bojie Li, AI Agents in Depth (2026), ch. 6 — https://github.com/bojieli/ai-agent-book"
  - https://arxiv.org/abs/2609.12191
  - https://arxiv.org/abs/2606.24530
  - https://arxiv.org/abs/2501.11067
  - https://arxiv.org/abs/2505.14963
  - https://arxiv.org/abs/2605.26302
  - https://assets.anthropic.com/m/785e231869ea8b3b/original/claude-3-7-sonnet-system-card.pdf
  - https://www.deeplearning.ai/short-courses/evaluating-ai-agents/
  - "Michael Albada, Building Applications with AI Agents (O'Reilly, 2025), ch. 9"
  - "Mayo Oshin & Nuno Campos, Learning LangChain (O'Reilly, 2025), ch. 10"
  - 13-case-study-support-agent.md
  - ../practice/conversation_scoring_lab.py
  - https://arxiv.org/abs/2608.03451
  - https://arxiv.org/abs/2607.28956
  - https://arxiv.org/abs/2608.30730
  - https://arxiv.org/abs/2609.23939
  - https://arxiv.org/abs/2610.08902
  - https://arxiv.org/abs/1909.05398
  - https://arxiv.org/abs/2309.10691
confidence: high
cleaned: 2026-11-01
---
# 6c — Evaluating Agents: Suites and Environment Hygiene

> The tasks you pick and the environment they run in decide what an agent eval can see. Add the suites your kind of agent needs, test conversations and sessions as wholes, and reset, isolate and audit the environment before blaming the agent.

Notes [06](06-evaluating-agents.md) and [06b](06b-components-trials-and-cost.md) graded runs: end state, path, components, repeated trials and cost. This chapter is about what the runs are run on. Each trial should move through the same isolated lifecycle, so that one trial's side effects never become the next trial's failure, as this loop shows.

```text
 per trial, k times per task

 snapshot ──► agent runs ──► grade end state ──► log steps, tokens, cost ──► tear down
    ▲          (tools on a       and path            and how the run ended         │
    │           private copy)                                                      │
    └──────────────────────── fresh state for the next trial ◄────────────────────┘
```

---

## Agent-specific suites

| Agent type | Add these to the suite |
|---|---|
| **Conversational** | Multi-turn tasks. Turn-count limits. Tone and interaction quality. Long, adversarial conversations. A simulated user ([below](#multi-turn-evaluation)) |
| **Coding** | Repo state + tests as the grader. Held-out tests the agent can't see ([04/03](../../../ai-engineering/04-loop-engineering/notes/03-the-scorekeeper.md#plus-the-fifth-hard-to-fake)). Diff scope, including a check that test files are untouched, since agents special-case tests ([12](12-failure-modes.md#goodhart-the-eval-becomes-the-target)) |
| **Research** | Citation validity, coverage of required facts, source quality ([07](07-evaluating-rag-and-grounding.md)) |
| **Computer use** | End-state checks on the environment. Sandboxed, reset per trial |
| **Any tool-using agent** | Error-handling suite: malformed input, tool errors, timeouts, empty results. Adversarial suite: injection, out-of-scope requests ([case study](13-case-study-support-agent.md#adversarial-cases)) |

Research suites need a breakdown by depth and by kind of win, because one accuracy figure hides both. MedBrowseComp ([arXiv:2505.14963](https://arxiv.org/abs/2505.14963) (Chen et al., 2025-05, preprint)) builds BrowseComp-style questions that chain 1 to 5 hops across HemOnc.org, PubMed, ClinicalTrials.gov and the FDA Orange Book. On its 50-question set (10 per hop depth, one run per system, graded by GPT-4.1 mini and checked by two annotators), **O3 deep research answered 51.0% overall (25.5 of 50, with one half-credit item) but 1 of 10 at five hops**, and Claude 3.7 Sonnet computer use answered 36.0%. On the 605-question set, graded by the LLM alone, about a quarter of gold answers are "not applicable": dropping those questions took GPT-4.1 without search on 4-hop questions from 60/121 to 0/39, so a benchmark that lets "N/A" count needs that cut reported. Each system ran once, the subscription products were run on different dates, and the coverage is oncology only. NatureBench ([arXiv:2606.24530](https://arxiv.org/abs/2606.24530) (Wang et al., 2026-06, preprint)) asks coding agents to match the published state of the art on 90 tasks (333 instances) taken from Nature-family papers, with 4 hours, no web and one run per configuration. **Claude Opus 4.7 in Claude Code surpassed the paper's result on 17.8% and matched it on 47.8%**. Across 900 annotated runs from ten agents, 82.7% of the runs that matched won by engineering, and only 8.3% by domain reasoning and 9.0% by the paper's own method; of the runs that fell short or gave no valid score, 61.1% failed at the method layer and 28.7% at execution. A "matches the paper" score can be earned by tuning a generic model on the target metric, which is the [Goodhart](12-failure-modes.md#goodhart-the-eval-becomes-the-target) problem at task level. The paper does not say who labelled the 900 runs or how well they agreed, nine of its 12 configurations share the Claude Code harness, and when given the source paper, Opus 4.6 reproduced 30 of the 90 published results within 4 hours (35 for either of two models), which the authors put down to the budget, not bad anchors.

Data and operations agents add two things a pass rate hides: what the output looks like, and whether the agent keeps working. DataSpace ([arXiv:2608.03451](https://arxiv.org/abs/2608.03451) (Li et al., 2026-08, preprint)) gives the agent a question and a workspace of CSV, JSON, SQLite, PDF and video files (410 tasks) and grades the CSV it returns with a model-free checker that ignores header names and normalizes types and precision. One run per configuration: Grok 4.5 solved 66.34% and Claude Sonnet 5 32.93% in the same ReAct agent, and **with MiMo-V2.5 fixed, the harness alone moved the score 15.36 points** (46.34% in Grok Build against 30.98% in Smolagents), though each harness kept its own action budget. Of Grok 4.5's 136 failures, 77 (56.6%) returned the wrong columns or row grain, and only 3 used the wrong source, so a strict output contract is part of what it measures. MerchantBench ([arXiv:2607.28956](https://arxiv.org/abs/2607.28956) (Shi et al., 2026-08, preprint)) runs a seller-side shop for 365 simulated days on real product and supplier records, with the agent acting every 12 hours and scored on final net assets. Over 3 runs per configuration (8 models, 2 frameworks), **the best LLM setup averaged 59.46 thousand RMB against 217.61 for three human novices, 27.3%**, and a rule-based baseline (24.48) beat several LLM setups. Agents faded: one concluded on day 104 that the store could not recover and took no action in 355 of the remaining 523 windows, and ReAct with Kimi K2.6 averaged (over its 3 runs) only 10.6% of 12-hour windows with any tool call in each run's worst 30-day stretch. The top configuration's three runs varied by a coefficient of 55.1%, so its rank is noise at n = 3, and the human baseline is three people. E-Commerce Bench ([arXiv:2608.30730](https://arxiv.org/abs/2608.30730) (Fan, Shen et al., 2026-08, preprint)) makes the counterparts deterministic: customers follow a fixed demand model and suppliers a rule-based negotiation kernel, with an LLM only rewording the replies, so differences between runs come from the agent. Over 18 models × 5 episodes of a 365-day year running up to 4 stores, **the richest agent was not the safest**: GPT-5.6 Sol ended with the highest mean assets (¥1.43 million from ¥100,000) but sent 18.48% of its spend to fraudulent suppliers, 16th of 18, against 0.12% for Claude Opus 4.7. No model led all seven axes the paper scores, 10 of the 90 episodes went bankrupt, and only 0.66% of tool calls revised a price. It is one fixed world, 5 episodes per model, no human baseline and no cost score, and it comes from the Qwen team, whose model leads the open-weight tier.

Text-game suites show what a "mean progress" number hides. Jericho wraps 32 human-written interactive-fiction games with a template action space of about 98 million actions against 240 billion for four free-form words. DRRN reached **10.7% mean normalised progress against 6.1 for TDQN, 4.9 for NAIL and 1.8 for random**, and no agent scored in 5 of the 32 games. The agents had different handicaps (DRRN and TDQN used save/load and a valid-action detector, NAIL did not), the hyperparameters were tuned on Zork1, and NAIL was developed on many of the evaluation games, so the scores are benchmarks, not a fair ranking ([arXiv:1909.05398](https://arxiv.org/abs/1909.05398) (Hausknecht et al., AAAI 2020)). Report the handicaps beside the score and count the zero-score games.

### Multi-turn evaluation

Two approaches, each with a trade-off:

- **Canned conversations.** Score each turn against a fixed, scripted history. Isolates turns and is reproducible, but misses compounding errors, because the history never reflects what the agent actually said.
- **Simulated user.** An LLM plays the user with a goal and persona, and the conversation runs to the end. Tests the real thing end to end, but inherits the simulator's biases and adds variance. Give the simulator a clear goal and stop condition, and calibrate it: does it behave like your real users?

A single cooperative simulated user flatters the agent. In GAUGE (Bodhwani et al., τ²-bench retail, 12 agent variants), swapping the default τ² user for a population of personas (anxious, skeptical and others) **cut mean verifiable reward by 42%** (0.47 → 0.27). Whoever grades the conversation also has to see the tool calls and the outcome. A transcript truncated mid-task scored reward 0, yet human raters gave it 4.6/7 for satisfaction. A judge that saw the tool calls and the goal tracked task success, and a judge rating "how the conversation felt" did not ([15](15-calibration-against-human-labels.md#the-procedure)). A free check catches the crude case: did the conversation finish at all? That signal tracked reward at ρ 0.87 when variants were deliberately broken. But only 3.5% of real failures were truncations, so semantic failures still need the judge ([arXiv:2609.12191](https://arxiv.org/abs/2609.12191) (Bodhwani et al., 2026-09)).

A user who is confidently wrong is a harder test still. XYEval ([arXiv:2609.23939](https://arxiv.org/abs/2609.23939) (Wu, Li, Tafjord and Kim, 2026-09, preprint)) appends one plausible but wrong suggestion ("I think the issue is in…"), written by an LLM that saw the reference answer (or by expert rules for τ²-bench), to each task of six existing benchmarks (five agentic, plus single-turn HLE), and leaves the environment and grader unchanged, so the score drop measures how far the agent follows the user's bad idea instead of the goal. **All 5 frontier models lost score on Terminal-Bench, and in nearly every other cell: Gemini 3.1 Pro fell from 67.4 to 36.0 on Terminal-Bench (89 tasks)**, and GPT 5.5 from 80.5 to 64.0 on a 200-task SWE-bench Verified subsample. On τ²-bench the Gemini agents' thinking disagreed with the suggestion in 92.1% of traces on average (per an LLM judge with no human check), yet they often complied without telling the user. A generic "beware the XY problem" system prompt cut Gemini 3.1 Pro's relative drop on Terminal-Bench from 46.7% to 18.3%, not to zero. The paper reports no run count or intervals, the distractor generator differs between cells, and the defence tests cover Gemini models only. The recipe is cheap to copy: mutate your own suite's inputs, keep its oracle, and compare.

Generating the scenarios scales the suite but moves the trust problem to the generator. IntellAgent ([arXiv:2501.11067](https://arxiv.org/abs/2501.11067) (Levi and Kadar, 2025-01, preprint)) turns the agent's system prompt into a graph of policies, samples policy combinations at a chosen complexity, writes 1,000 scenarios with matching database states per domain, and has an LLM critique each dialog policy by policy, which catches failures such as acting without user consent that a final-state check cannot see. On τ-bench's airline and retail domains **its success rates correlated with τ-bench's across six 2024 models (Pearson 0.98 airline, 0.92 retail), in nearly the same order**, but its absolute scores ran far higher (claude-3.5-sonnet 0.70 against 0.46 on airline), so it reproduces the order, not the difficulty. Six points per domain is a small sample, GPT-4o generates, plays the user, judges and is one of the six agents, and nothing was checked against human labels.

Turns also buy accuracy, and the gain depends on who gives feedback. MINT gave 20 LLMs up to five Python tool-use turns, with GPT-4-simulated natural-language feedback in some arms: each extra tool turn added **1-8 points** and feedback **2-17 points**. gpt-4-0613 reached 69.5% success at five turns, and claude-instant-1 overtook claude-2 as turns grew (45.9% against 39.9% at k=5) despite losing at k=1. Feedback lifted gpt-3.5-turbo from 36.2% to 51.4%, but GPT-4 gained nothing from its own (-0.7). Supervised instruction tuning cut CodeLlama-34B by 11.1 points at k=5 and RLHF cut LLaMA-2-70B by 8.5 ([arXiv:2309.10691](https://arxiv.org/abs/2309.10691) (Wang et al., ICLR 2024)). Single-turn pass rates do not rank models on multi-turn work. The metric is outcome only, and repetitive guessing is not penalized.

**Progressive information disclosure** is what makes a simulated user realistic. Real users don't state everything up front ("There's a problem with my flight." → "Which one?" → "It's too long, I want to change it." → "Any afternoon flight is fine."). τ-bench gives the simulator two parts: *known information* and *instructions* for when to reveal it. The agent has to ask. A simulator that dumps all the facts in turn 1 tests a much easier task. Hold the script fixed so runs stay reproducible.

**τ²-bench** (the successor) adds a **dual-control environment**: the simulated user can also call tools on the shared state. The agent says "switch to airplane mode", and the user's action really changes the environment. This fits tech support, where the user has to do part of the work, and tests whether the agent notices state changes it didn't make. It also tightened success conditions ("only an *excellent* speed rating counts") and generates task parameters fresh each run.

**Sessions, not only turns.** An agent with memory has to be tested on work where a later session depends on an earlier one. Recall benchmarks such as LoCoMo and LongMemEval ask one question about a fixed history, with no actions and no feedback from an environment. MemoryArena ([arXiv:2602.16313](https://arxiv.org/abs/2602.16313) (He et al., ICML 2026)) chains 701 tasks into an average of 6.9 dependent subtasks each: session 2 asks for a lens that fits the camera bought in session 1, and the instruction is underspecified without that state. Across 13 setups (long context on four models, plus five memory systems and four RAG systems on GPT-5-mini), **the share of shopping subtasks passed averaged 0.52 while the share of whole tasks solved averaged 0.02**. On GPT-5-mini, long context averaged 0.16 success over the five domains; the memory systems scored lower (0.12–0.14) and RAG only slightly higher (0.17–0.20). In group travel the long-context pass rate, conditional on the earlier constraints being met, fell from 0.48 at dependency distance L0 to 0.15 at L4, with the whole history in context. The paper says systems that saturate recall benchmarks do poorly here, but it reports no recall scores for the same systems, so that gap is asserted, not measured. It has no repeated runs or intervals, physics has 20 tasks, and it does not say how a search or proof answer is judged correct. AgingBench ([arXiv:2605.26302](https://arxiv.org/abs/2605.26302) (Zhu et al., 2026-05, preprint)) adds the time axis: it tracks capability across sessions of synthetic, template-generated tasks for 14 models in compaction-summary memory, and reruns each with oracle retrieval and oracle context to say whether the write, the read or the use failed. **The memory policy moved results more than the model did**: on its first scenario GPT-5-mini's final score was 1.00 with append-only (and careful) memory and 0.26 with a deliberately lossy summary. In one run (Gemma-4-31B, lossy compaction, sessions 0–9) constraint precision fell from 0.90 to 0.37 while the constraint-violation rate stayed near zero, so a guardrail metric stayed flat while the facts decayed. Most runs are 8 to 12 sessions, standard deviations often match the mean, and no production traffic was measured.

An agent that writes its own tools, skills and notes between episodes needs a learning curve, not an endpoint. Singh et al. ([arXiv:2610.08902](https://arxiv.org/abs/2610.08902) (Singh et al., 2026-10, preprint)) freeze the weights, let each agent play and reflect across 20 checkpoints, and score it on held-out games after each one. **Plasticity** is the held-out gain per $1,000 of learning cost, reflection included, read where a fitted curve reaches 90% of its rise. On the mean over chess (Hard and Easy), 5×5 Go and 6×6 Hex, **the agent with the highest fitted score was not the most plastic: Claude Fable 5 gained 57 percentage points per $1,000 and GPT-5.6 Sol 298**. In Hard chess against Stockfish, Fable 5 rose from 37.5% at checkpoint 0 to 73.3% (mean of checkpoints 16–20), while Sol rose from near 0% to 36.9%. Improvement was task-dependent: Opus 4.8 lost ground in Go but gained in Hex, Sol declined in NetHack, and only one of six models there (Claude Opus 5.5) improved reliably. Each game used separately trained lineages, so transfer across games was not tested. The authors call plasticity a property of the agent under that protocol, not of the model. Each model ran one lineage per game, the reuse and failure labels come from a single Gemini 3.1 Pro labeller with no human check, the NetHack harnesses differ by model, and the design does not separate environment feedback from the extra compute spent reflecting.

Check who wrote a multi-session benchmark before trusting its ranking. OdysseyBench ([arXiv:2508.09124](https://arxiv.org/abs/2508.09124) (Wang et al., 2025-08, preprint)) scatters the instructions for an office task over several days of dialogue and grades only the final file system, with exact-match, fuzzy-match and execution checks that must all pass. On its 300 tasks adapted from OfficeBench, o3 fell from 72.83% on one-app tasks to 30.36% on three-app tasks. But GPT-4.1 wrote the dialogues, and for the 302 synthesized tasks also the tasks and their pass criteria, and o3 solving a task was the filter for keeping it in the automated stage, though human curators then added back some tasks it could not solve. Both models are then scored on the result. The assistant in the dialogue history never acts, so the history holds instructions and chitchat and no earlier work, unlike MemoryArena. Nothing is run twice, and two of the paper's retrieval tables contradict themselves, so its comparison of long context against RAG is not used here.

Grade multi-turn runs at both levels: per turn (grounded, on-policy) and per conversation (goal reached, turns used, escalation correct). Don't build the second number by averaging the first. A mean of turns can't see order, so a disqualifying last answer gets outvoted, a misunderstanding the agent repaired still drags the score, small talk inflates it, and two answers that contradict each other each look fine alone. Taking the minimum fixes the first case and breaks the repaired one. The [conversation scoring lab](../practice/conversation_scoring_lab.py) plants these in generated conversations with stub scorers: at a threshold tuned on ordinary rows, the mean gets 85% of ordinary conversations right and 0% to 2% of the planted ones. Its whole-conversation stub follows the labellers' rule by construction, so that comparison shows what a mean can't express and doesn't measure any real judge.

Albada's example release gate for a support agent puts both kinds of number in the gate: at least 95% tool recall on refund and cancellation scenarios, and promotion blocked on any regression in multi-turn tests such as address changes (*Building Applications with AI Agents*, ch. 9). The 95% is an illustration, not a measured threshold. Set yours from the cost of a missed refund ([10](10-evals-in-ci.md#the-regression-gate)).

---

## Environment hygiene

An agent eval environment has five parts. Each one can be wrong on its own:

| Part | Holds | Gets it wrong when |
|---|---|---|
| **Dataset** | Initial state, goal, optional reference solution | Ambiguous goals ([03](03-eval-datasets.md)) |
| **Environment state** | Mutable records (orders, balances, files) | It doesn't follow business rules, or can't reset to the same start |
| **Tools** | Atomic operations (look up order, modify booking) | They're too high-level ("solve the user's problem") and skip the planning you meant to test |
| **Rubric** | Binary, continuous or multi-dimensional score | See [04](04-graders.md) |
| **Interaction protocol** | Who acts when: single-shot, multi-turn, simulated user, dual control | The user model is unrealistic ([above](#multi-turn-evaluation)) |

- **Reset state for every trial.** Fresh sandbox, database snapshot, clean working directory. Shared state turns one trial's side effects into the next trial's failure.
- **Isolate trials.** Parallel trials must not share mutable resources, and neither should sequential ones. WebArena's Reddit clone rate-limits posting, so "if the tasks involving Reddit posts are evaluated one after another, they are much more likely to fail." Task order changed the score (Kapoor et al., [above](06b-components-trials-and-cost.md#efficiency-metrics)). Shuffle task order between runs. A score that moves with order means the tasks are not independent.
- **Re-run the scoring, not just the agent.** The same audit found two leaderboard agents (LATS, STeP) that marked some failed tasks as correct and dropped a few tasks from the benchmark.
- **Stub or record unstable externals** (live web, third-party APIs) for regression suites. Keep a separate live suite for capability checks.
- **Treat a 0% task as suspect.** If a task fails every trial across several model versions, check the task before the agent. It's often broken: unreachable state, wrong reference, missing permission. On BrowseComp, 21 of the 118 questions that Deep Research never solved had a bad reference answer ([03](03b-splits-contamination-and-public-benchmarks.md#lessons-from-public-benchmarks)). For the rest, the authors gave the model the reference answer and asked it to find supporting evidence. It usually could, which showed the questions were hard rather than broken (Wei et al., [above](06b-components-trials-and-cost.md#non-determinism-run-every-task-k-times)). [12](12-failure-modes.md#eval-bugs-look-like-agent-bugs) has more checks for a broken task.
- **Keep the answer out of reach.** An agent that can't do the task the intended way will look for another way. In one of Anthropic's capture-the-flag evals, Claude 3.7 Sonnet couldn't connect to the vulnerable service, so it reasoned that the service was running locally, searched the whole machine and found the flag in plaintext ([PDF](https://assets.anthropic.com/m/785e231869ea8b3b/original/claude-3-7-sonnet-system-card.pdf) (Anthropic, 2025-02)). Store reference answers, grader code and hidden tests where the agent's tools can't read them, and read the transcripts of surprising passes.

---

## Checklist

- [ ] Suites chosen for the agent type: conversational, coding, research, computer use
- [ ] Error-handling and adversarial suites present
- [ ] Multi-turn runs graded per turn and per conversation, not by averaging turns
- [ ] Environment reset per trial; 0% tasks investigated before blaming the agent
- [ ] References, grader code and hidden tests out of the agent's reach

---

## Pitfalls

- **Sharing state between trials.** Symptom: order-dependent failures, as with WebArena's rate-limited Reddit clone. Fix: reset state each trial, isolate parallel runs, and shuffle task order. A score that moves with order means the tasks aren't independent.
- **Blaming the agent for a 0% task.** Symptom: weeks spent on a broken task. 21 of the 118 BrowseComp questions Deep Research never solved had a bad reference answer. Fix: check the task first, and give a capable model the reference to see if evidence can be found.
- **Leaving the answer in reach.** Symptom: a surprising pass, such as Claude 3.7 Sonnet finding a capture-the-flag answer in plaintext after searching the machine. Fix: keep references, grader code and hidden tests away from the agent's tools, and read surprising passes.
- **Averaging turn scores into a conversation score.** Symptom: a padded or late-disqualified conversation passes. A mean can't see order. Fix: grade the conversation on its own terms (goal reached, turns used, escalation correct) beside the per-turn scores.

## Try it

1. Run section 4 of the [conversation scoring lab](../practice/conversation_scoring_lab.py) (`cd practice && uv run conversation_scoring_lab.py`). On which pattern does the minimum of turn scores beat the mean by most, and on which does neither work? Why can no threshold fix the second without breaking the other rows?

   <details><summary>Answer</summary>

   On `padded` the minimum is right 98% of the time and the mean 0%, and on `late_disqualifier` it's 83% against 1%. On `recovery` and `contradiction` neither works: the mean is at 2% and 0%, and the minimum at 0% on both. A contradiction lives between two turns, and a repair needs knowing which answer came last, so a function that sees one turn at a time has nothing to threshold. The scores show it: a repaired conversation (human PASS) has a mean of 0.58, below the failing `padded` (0.70) and `late_disqualifier` (0.71), while a contradictory one (human FAIL) scores 0.82, above ordinary rows at 0.69. The ordering is wrong for any cut. A mean threshold of .50 gets `recovery` right but drops ordinary rows from 85% to 73%, and a minimum threshold of .80 gets `contradiction` 96% right but drops ordinary rows from 79% to 42%. These rates come from the lab's seed and generated data.

   </details>

To run the lab:

```bash
cd generative-ai/08-eval/practice
uv run conversation_scoring_lab.py
```

2. A WebArena-style suite fails more often when its Reddit tasks run back to back. Name the cause and two fixes.

   <details><summary>Answer</summary>

   Shared state: the Reddit clone rate-limits posting, so one trial's posts make the next one fail. Isolate trials so that they don't share mutable resources, reset state per trial, and shuffle task order; a score that moves with order means the tasks aren't independent.

   </details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| A simulated user gives a 0.47 reward. Do you trust it? | Not from one cooperative user. In GAUGE, a population of personas cut mean verifiable reward by 42%, from 0.47 to 0.27, and the judge needs to see tool calls and outcome, since a truncated transcript got 4.6/7 for satisfaction with reward 0. |
| Beyond the task set, which suites does a tool-using agent need? | An error-handling suite with malformed input, tool errors, timeouts and empty results, plus an adversarial suite with injection and out-of-scope requests. Neither failure shows up in tasks where every tool behaves. |
| A task fails every trial across several model versions. What do you do? | Check the task before the agent. On BrowseComp, 21 of the 118 questions Deep Research never solved had a bad reference answer. |
| An agent passes a task it shouldn't be able to. What do you check? | Whether the answer was in reach. Claude 3.7 Sonnet found a capture-the-flag answer in plaintext after searching the machine, so keep references, grader code and hidden tests away from the agent's tools and read surprising passes. |

## Next

[07-evaluating-rag-and-grounding.md](07-evaluating-rag-and-grounding.md): when the answer has to come from the documents.
