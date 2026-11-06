---
origin: synthesis
sources:
  - https://arxiv.org/abs/2607.09510
  - https://arxiv.org/abs/2506.09050
  - https://arxiv.org/abs/2512.09882
  - https://arxiv.org/abs/2508.09124
  - https://arxiv.org/abs/2504.08703
  - https://arxiv.org/abs/2606.05405
  - https://arxiv.org/abs/2602.14337
  - https://arxiv.org/abs/2510.11977
  - https://arxiv.org/abs/2410.05080
  - https://arxiv.org/abs/2512.18470
  - https://arxiv.org/abs/2502.12115
  - https://arxiv.org/abs/2602.11964
  - https://arxiv.org/abs/2503.16416
  - https://arxiv.org/abs/2602.16313
  - https://arxiv.org/abs/2412.14161
  - https://arxiv.org/abs/2504.01848
  - https://arxiv.org/abs/2410.07095
  - https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
  - https://docs.langchain.com/langsmith/trajectory-evals
  - https://arxiv.org/abs/2107.03374
  - https://arxiv.org/abs/2108.07732
  - https://arxiv.org/abs/2406.12045
  - "Bojie Li, AI Agents in Depth (2026), ch. 6 — https://github.com/bojieli/ai-agent-book"
  - https://arxiv.org/abs/2411.15114
  - https://arxiv.org/abs/2401.13178
  - https://arxiv.org/abs/2407.01502
  - https://arxiv.org/abs/2609.12191
  - https://arxiv.org/abs/2504.13837
  - https://arxiv.org/abs/2505.08775
  - https://arxiv.org/abs/2504.12516
  - https://arxiv.org/abs/2510.04374
  - https://arxiv.org/abs/2207.01206
  - https://arxiv.org/abs/2308.03688
  - https://arxiv.org/abs/2010.03768
  - https://arxiv.org/abs/2204.01691
  - https://arxiv.org/abs/2010.02903
  - https://arxiv.org/abs/2304.08354
  - https://arxiv.org/abs/2306.06070
  - https://arxiv.org/abs/2601.11868
  - https://arxiv.org/abs/2602.12670
  - https://arxiv.org/abs/2604.06240
  - https://arxiv.org/abs/2607.12747
  - https://arxiv.org/abs/2606.05080
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
  - https://arxiv.org/abs/2508.15760
  - https://arxiv.org/abs/2608.03451
  - https://arxiv.org/abs/2607.28956
  - https://arxiv.org/abs/2608.11727
  - https://arxiv.org/abs/2504.11844
  - https://arxiv.org/abs/2608.30730
  - https://arxiv.org/abs/2603.23971
  - https://arxiv.org/abs/2607.05775
  - https://arxiv.org/abs/2608.20614
  - https://arxiv.org/abs/2604.12162
  - https://arxiv.org/abs/2609.23939
  - https://arxiv.org/abs/2609.25804
  - https://arxiv.org/abs/2606.16576
  - https://arxiv.org/abs/2604.25067
  - https://arxiv.org/abs/2609.16487
  - https://arxiv.org/abs/2610.08902
confidence: high
cleaned: 2026-11-01
---
# 6 — Evaluating Agents

> An agent's output is a path, not just an answer. Grade the outcome *and* the trajectory, run every task several times, and evaluate each component (router, tools, final answer) on its own as well as end to end.

An agent tells a customer "I've issued your refund", the answer-quality judge gives it full marks, and no refund exists. On another ticket it reaches the right result after calling a paid API 40 times. Grading the final text misses both, and one run per task can't tell a reliable agent from a lucky one. This chapter grades the end state and the path, runs every task several times, and tracks what each success costs.

---

## Outcome and trajectory

![The Four Stages of an Agent Evaluation System](../sources/images/li-ai-agents-in-depth-fig7-1.svg)
*Image Source: Li, [AI Agents in Depth](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter7.md) (2026), Fig. 7-1 (Apache-2.0)*

```
Outcome:     did the agent reach the goal?
Trajectory:  did it get there in an acceptable way?
```

Both are needed because they fail independently:

| Outcome | Trajectory | What happened | Outcome-only eval says |
|---|---|---|---|
| ✅ | ✅ | Worked | Pass |
| ✅ | ❌ | Right answer by an unsafe or wasteful path: deleted and recreated a file, called a paid API 40 times, guessed instead of looking up | **Pass** (wrong) |
| ❌ | ✅ | Reasonable process, failed on an external issue: tool timeout, missing data | Fail (but the agent isn't the problem) |
| ❌ | ❌ | Broken | Fail |

Anthropic recommends grading both the final environment state and the transcript. The second row is why. The third row is why you read traces before blaming the agent ([12](12-failure-modes.md#eval-bugs-look-like-agent-bugs)).

The reverse also happens: a strict trajectory check can fail a run that did *better* than the script. Anthropic's example is a flight-booking agent that found a loophole in the airline's policy and got the user a cheaper fare. Scored against the preset path, it failed. Scored by outcome, the user got a better deal. Let trajectory checks enforce invariants ("never book before confirming"), not a single golden path.

Trajectory analysis also tells you **where** a run failed. A multi-step run has many paths to the same wrong answer, and each needs a different fix. An outcome-only eval scores them identically.

A survey of agent evaluation names this as an open gap: most benchmarks report end-to-end success, which falls "short in diagnosing specific agent failures" ([arXiv:2503.16416](https://arxiv.org/abs/2503.16416) (Yehudai et al., Findings of ACL 2026; read as arXiv v2, 2026-04)). In its own tables, 3 of the 8 evaluation frameworks it compares support trajectory assessment and 1 of 8 benchmarks tests safety. It adds a caution for step-level judges, which assume "each action can be meaningfully assessed in isolation". The survey runs no experiments, it does not say how its tool table was coded and cites only vendor pages for it, and it gives no count of the papers screened.

AgentBoard turns "how far did it get" into a number (9 tasks, 1,013 environments). **Progress rate** is the highest fraction of human-annotated subgoals the agent reached at any step, reported beside success rate. Human ratings of the same trajectories tracked it closely (Pearson > 0.95 on every task). It separates agents that success rate lumps together: "Llama2-13b and Mistral-7b exhibit similarly negligible success rates (2.1% and 3.9%, respectively), but their progress rates differ significantly: 18.9% for Llama2-13b and 24.6% for Mistral-7b." AgentBoard also reports **grounding accuracy**, the share of actions that were valid in the environment, which separates malformed or impossible actions from bad plans ([arXiv:2401.13178](https://arxiv.org/abs/2401.13178) (Ma et al., 2024-01)). The cost is writing subgoals for every task. And progress rewards partial work: CodeLlama-34b often never emitted `finish`, which gave it higher progress and lower success than CodeLlama-13b. Report progress beside strict success, never instead of it ([12](12-failure-modes.md#goodhart-the-eval-becomes-the-target)). The idea is older than AgentBoard. ALFWorld reports **goal-condition success**, the share of a task's goal conditions that hold in the end state, in parentheses beside strict success. "Put a hot potato on the countertop" has three conditions, so an agent that puts any potato there gets 0.33 ([arXiv:2010.03768](https://arxiv.org/abs/2010.03768) (Shridhar et al., ICLR 2021), taking the metric from ALFRED).

Score the plan and its execution separately when they can fail apart. SayCan had a language model choose a robot's next skill, and three human raters judged each of 101 kitchen instructions twice: once on whether the plan would work, once by watching the robot (2 of 3 had to agree). PaLM-SayCan planned 84% correctly and executed 74% in the kitchen its skills were trained in, and 81% against 60% in a different, real kitchen. On long-horizon tasks in the training kitchen the two were 73% and 47%. The authors traced 65% of the planning errors to the language model (on long-horizon tasks, mostly stopping early) and 35% to affordance errors, where the value function misjudged which skills were feasible ([arXiv:2204.01691](https://arxiv.org/abs/2204.01691) (Ahn et al., CoRL 2022); one run per instruction as far as the paper says, no variance reported). A single success rate would have hidden which half to fix.

Outcome and trajectory both score what happened, not whether the agent chose well at a fork. Taste-Bench ([arXiv:2609.25804](https://arxiv.org/abs/2609.25804) (Pan et al., 2026-09, preprint)) mines forks from recorded runs (two parallel attempts where one passed and one failed, or an approach the agent abandoned and recovered from) and asks a model which branch is better before the outcome is visible. A question counts only if the answer holds in both option orders, so chance is 25%. **The best of 14 models averaged 59.7% across the engineering and research subsets (56.9% and 62.5%, 502 questions)** (one run each), and the mean across models fell from 62.3% when the deciding evidence was already in the prefix to 21.0% when it needed later work; the horizon labels came from GPT-5.5, which saw the answer. Raising reasoning effort on two models moved accuracy by −0.2 and +2.2 points. Each label rests on one passing and one failing run with no repeats, reviewers checked labels (98.8% agreement) only after seeing the outcomes, and the fork generator (GPT-5.6 Sol) is also the top scorer, so read it as a probe of decision quality, not a ranking.

When no state check is possible, as on the live web, a judge reads the screenshots, and its design matters more than its model. Rosset et al. built a verifier for browser agents that writes the rubric from the task alone before it sees the run, because "generating the rubric and scoring it in a single LLM call leads the model to create criteria tailored to the agent's behavior". It also scores process and outcome separately, and does not count failures the environment caused against the agent. **Against human labels on 140 and 106 Fara-7B trajectories, its outcome κ was 0.64 and 0.58 with false positive rates of 0.01 and 0.08, against 0.31 and 0.13 κ with false positive rates of 0.45 and 0.60 for the WebVoyager judge.** Moving WebVoyager to the same GPT-5.2 backbone cut its false positive rate to 0.10 but raised its false negative rate from 0.24 to 0.44, and κ reached only 0.43 ([arXiv:2604.06240](https://arxiv.org/abs/2604.06240) (Rosset et al., 2026-04, preprint)). The verifier is conservative (false negative rate about 0.31), one author designed it over three weeks, and outcome κ varied from 0.64 to 0.71 across identical runs. Process agreement was lower than outcome agreement for people and verifier alike (κ 0.43 on the second set, within the 0.36–0.45 range between annotators). On the 106-trajectory set, annotators who saw the verifier's reasoning flipped 16.6% of their own labels, nearly all from success to failure, so show your labellers the judge's reasoning only after they have labelled ([15](15-calibration-against-human-labels.md#the-procedure)).

When the tools are live, a fixed expected answer goes stale: today's weather or stock price differs from the one written down. LiveMCP-101 ([arXiv:2508.15760](https://arxiv.org/abs/2508.15760) (Yin et al., 2025-08, preprint)) runs a reference agent on a human-validated plan at the same time as the agent under test, and a GPT-4.1 judge compares the two outputs. On 101 tasks over 41 live MCP servers (ReAct, 30-round cap, 15 servers in the pool per task, one run per model), **GPT-5 succeeded on 58.42% overall and 39.02% of the 41 hard tasks**. Semantic parameter errors (a well-formed call with the wrong value) were the largest failure type for most models: 16.8% of GPT-5's tasks and 41.6% of GPT-4.1-mini's. On 30 tasks from 6 models, the judge agreed with blind experts at a quadratic-weighted κ above 0.85 on results and above 0.78 on trajectories. The reference agent and the judge are both GPT-4.1, the plan is one path among several that could be right, and the three-run stability table's percentages cannot come from 101 tasks, so its spread is not used here.

---

## Grade the outcome by state, not by words

For agents that act, check the **end state** directly where you can:

| Agent | Outcome check |
|---|---|
| Coding | The repo's tests pass. The diff touches only allowed paths |
| Data / SQL | Query result matches the reference result (not the reference SQL text) |
| Customer action | The refund row exists with the right amount. No other rows changed |
| Computer use | The target page / form / file is in the expected state |
| Research | The report contains the required facts with valid citations ([07](07-evaluating-rag-and-grounding.md)) |

An agent that says "I've issued your refund" when no refund exists is the most important failure to catch, and only a state check catches it.

Terminal-Bench's tests check only the final container state and "do not test the agent's commands or console output" ([arXiv:2601.11868](https://arxiv.org/abs/2601.11868) (Merrill et al., ICLR 2026)).

A pass rate also treats a $250 fix and a $32,000 feature as one task each. SWE-Lancer ([arXiv:2502.12115](https://arxiv.org/abs/2502.12115) (Miserendino et al., ICML 2025)) takes 1,488 Upwork tasks from one company's repository with the $1,000,000 they actually paid, grades each patch with hidden end-to-end browser tests written by engineers, and pays out only if every test passes. It reports the **earn rate**, dollars earned over dollars available, beside pass@1. The two disagree in both directions: **on the public coding tasks Claude 3.5 Sonnet passed 26.2% but earned 24.5% of the money, and on proposal-choosing tasks it passed 44.9% and earned 56.8%**. Every figure is one run with no interval, and the paper warns of "significant variance between runs". The proposal tasks are graded against the one proposal the original manager picked from four or five, with no chance baseline given, and all tasks come from one repository.

WebShop is the standard example of a state grader for a web agent. The episode ends when the agent buys something. The reward is computed from the purchased product: the share of the instruction's hidden attributes, options and price limit that it meets, multiplied by a product-type match. Two numbers come from that one reward, and they can disagree. **Task score** is the mean reward × 100, and **success rate** is the share of episodes with full reward. RL fine-tuning raised the imitation-learning agent's score from 59.9 to 62.4 while its success rate fell from 29.1% to 28.7% (500 test instructions; human experts 82.1 and 59.6%). The grader was itself checked against hand scoring of 200 human trajectories. Pearson was 0.86 for average workers and 0.77 for experts, and the automatic score ran low (81.5 against 89.9 for experts) because exact attribute matching misses synonyms ([arXiv:2207.01206](https://arxiv.org/abs/2207.01206) (Yao et al., NeurIPS 2022); BERT/BART agents, not LLMs). A state check can still be strict in the wrong place. Hand-score a sample before you trust it.

Without a state check, the score measures agreement with a recorded path. Mind2Web (2,350 crowd-demonstrated tasks on 137 real websites) replays cached pages and grades each step with the true history supplied, and a task counts only if every step matches. **Flan-T5XL scored 52.0% per step and 5.2% per task** on new tasks from known websites. The authors concede that a valid path nobody cached fails, "potentially leading to false negatives" ([arXiv:2306.06070](https://arxiv.org/abs/2306.06070) (Deng et al., NeurIPS 2023 Datasets & Benchmarks); 2023 models, no repeated runs on the main table).

Matching actions need not mean matching a whole path. Gaia2 ([arXiv:2602.11964](https://arxiv.org/abs/2602.11964) (Froger et al., ICLR 2026)) compares only the agent's **write** actions (send, create, delete) with a minimal reference set, in any order that respects dependencies, and leaves reads free because "multiple reading strategies can lead to the correct set of write actions". IDs must match exactly, and an LLM judge checks only free-text arguments. On 450 hand-labelled trajectories **this verifier agreed with the human label on 0.98, against 0.72 for one LLM judge given the same criteria** (both Llama 3.3 70B), which accepted too readily. Two cautions come from the paper itself. An equivalent write through a different app fails, and when the authors used the verifier as a training reward the agent learned to stuff its message with text that fooled the free-text judge until a style check was added. The paper gives no annotator agreement for the 450 labels and does not say they were held out from prompt tuning. Gaia2 also puts time in the score: the clock runs while the model thinks, so GPT-5 at high reasoning effort scored 0.0% on the 160 timed scenarios and 34.4% when its latency was not counted.

Between a single pass/fail and a full replay sits **partial credit by checkpoint**. TheAgentCompany ([arXiv:2412.14161](https://arxiv.org/abs/2412.14161) (Xu et al., NeurIPS 2025 Datasets and Benchmarks; numbers from arXiv v3, 2025-09)) gives each of its 175 simulated-workplace tasks a list of checkpoints with points, most of them graded by Python functions that read the environment state or the trajectory. An LLM judge is the fallback on 51 tasks (29%). The task score is half the share of points earned plus half a bonus paid only when every checkpoint passes, so an agent that earns 4 of 8 points scores 0.25, not 0.5. That keeps partial progress from adding up to a pass. **The best agent (OpenHands with Gemini 2.5 Pro) fully completed 30.3% of tasks and scored 39.3% with partial credit**, at 27 LLM calls and $4.20 a task. The score exists because of what the authors saw agents do: one that could not find the right colleague in the chat tool renamed another user to that name and carried on. The paper has one run per model, no human baseline and no judge-against-human agreement figure. The half-and-half weighting and the point values are the authors' choices, with no sensitivity check.

Partial credit needs a rule for regressions. SWE-EVO ([arXiv:2512.18470](https://arxiv.org/abs/2512.18470) (Le et al., 2025-12, preprint; numbers from the 2026-05 revision)) asks a coding agent to take a repository from one release to the next (48 tasks from 7 Python repositories, a mean of 20.9 files edited and 874 tests per task). Its **Fix Rate** is the share of the target failing tests that now pass, set to 0 if any previously passing test breaks, so an agent can't buy progress with a regression. On OpenHands, GPT-4.1 and gpt-oss-120b both resolved 2.08% of tasks (one task) but had Fix Rates of 4.65% and 2.08%. With 48 tasks the intervals are wide (95% Wilson interval 14.9 to 38.8 for a 25.00% score), the paper reports no repeated runs or run-to-run variance, and the tests are weighted equally. The paper's comparison with SWE-bench Verified (GPT-5.2 at 72.80% there, 22.92% here with SWE-agent and 18.75% with OpenHands) uses leaderboard figures from a different scaffold, and scaffold alone moved glm-4p7 from 4.17% to 39.58% on these tasks.

An averaged step score needs the same care. LongCLI-Bench ([arXiv:2602.14337](https://arxiv.org/abs/2602.14337) (Feng et al., Findings of ACL 2026; read as the arXiv version)) scores 20 long command-line tasks by the share of sub-steps passed on two test sets, one for the new requirement and one for behaviour that must not break, and counts a pass only when both reach 100%. Across 9 agent and model pairs (mean of 3 runs), **the keep-working step score was above 98% for every pair while 70.0% to 88.3% of runs kept everything working**, and the best pass rate was 16.7%. A plan injected before the run raised Claude Code with Opus 4.6 to 58.3%, about what multi-turn self-correction on test feedback reached (55.0%, turns T1 to T3) in a third of the time (15.4 against 43.8 minutes). The paper is labelled preliminary: 20 tasks, so one run is 1.67 points, no intervals, no formula for the step score, and the run count for the plan and feedback rows is not stated.

When the deliverable is too open for a state check, the rubric can be a tree. PaperBench ([arXiv:2504.01848](https://arxiv.org/abs/2504.01848) (Starace et al., ICML 2025; numbers from arXiv v3)) grades an agent's attempt to replicate 20 ICML 2024 papers against rubrics written with each paper's authors: 8,316 leaves in all, each a pass/fail check an expert could do in under 15 minutes, with a parent's score the weighted average of its children. Result-matching leaves are judged only from a fresh re-run of the agent's `reproduce.sh` on a clean machine, so hard-coded results earn nothing. The judge was itself graded before use ([05](05-llm-as-judge.md#decompose-hard-criteria)): on human-graded leaves from five papers, **o3-mini reached F1 0.83 at $66 a paper, against 0.84 for o1 at $830**, and it was weakest on reading code (0.72) and strongest on matching results (0.94). Granularity is part of the score. Collapsing one submission's 361 leaves to 9 raised its grade from 0.25 to 0.48, and to a single leaf, 0.93. The best agent scored 21.0% ± 0.8 (Claude 3.5 Sonnet, 12 hours, 3 runs), almost all from writing code and not from running it. On a 3-paper subset the best of three attempts by ML PhDs reached 41.4% in 48 hours against 26.6% for o1. The gold labels have no inter-rater figure, the judge was tested on human-made submissions and not on agent output, and each rubric took weeks to write.

A graded score can also sit behind a gate. Agents' Last Exam ([arXiv:2606.05405](https://arxiv.org/abs/2606.05405) (Sun et al., 2026-06, preprint; numbers from the 2026-10 revision)) scores professional deliverables, from CAD parts to audio sessions, with a per-task `evaluate()` function that compares the output files with a hidden reference directory. By the authors' static analysis, 93.2% of the open-sourced task workflows are graded by code and 6.8% by an LLM judge, and the most common scoring pattern checks a binary precondition first: "failure on the gate forces the task score to 0 regardless of partial progress on other criteria". Where a judge is used it answers narrow yes/no questions, and code does the weighting and aggregation. The two numbers still diverge: **on the 38 hardest public tasks, Codex with GPT-5.5 had a mean score of 11.2 and passed none**. No grader, tolerance or judge is validated against people, repeated runs (three) cover only some configurations, and only 150 of the 1,490 tasks are public.

When the right answer moves with the data, the reference has to move with it. Tamhane et al. ([arXiv:2609.16487](https://arxiv.org/abs/2609.16487) (Tamhane et al., 2026-09, preprint)) store each reference as a function the evaluator calls at grading time against the same data APIs the agent used. An LLM judge then splits the response and the computed reference into atomic claims, matches them one to one with no partial credit, and logs the hallucinated and omitted claims for each case. On 53 cases of an in-house ML-scoping skill over a synthetic database (Claude Sonnet 4.6 as both skill and judge, three expert annotators, one reported result per configuration with repeats not stated), **judge-human agreement was MCC 0.427 with the code reference, 0.331 with a natural-language reference and −0.379 with no reference**. Without a reference, the judge graded the skill against the skill's own final checks. The code reference reached recall 1.000 at precision 0.568, so it passed every case the annotators passed and many they failed. In the benchmark the function returns a stored specification, so recomputing from drifting data is described but not tested. There are no intervals, the annotators saw the reference, and the same model played skill and judge.

---

## Scoring tool calls

Three levels of strictness for comparing the actual tool calls to the expected ones:

| Match mode | Passes when | Use for |
|---|---|---|
| **Exact** | Same tools, same order, same arguments | Strict protocols (auth before action) |
| **In order** | Expected calls appear in order, extra calls allowed | Required sequence with some freedom |
| **Any order** | Expected calls all appear, any order | Independent lookups |
| **Subset / superset** | Agent's calls ⊆ (or ⊇) the allowed set | "Never call outside this set" / "must at least call these" |

Check arguments separately from tool names, and allow per-argument matching rules: exact, normalized (case, whitespace), numeric tolerance, "any value", or a judge for free-text arguments.

```python
def trajectory_score(expected: list[Call], actual: list[Call], mode="in_order") -> float:
    """Fraction of expected calls matched under `mode`, penalized for extra calls."""
    matched = match_calls(expected, actual, mode)          # mode-specific matching
    return len(matched) / max(len(expected), len(actual))  # extras lower the score
```

Two set-level numbers are worth logging next to the trajectory score, because they point at different fixes. Albada's **tool recall** asks whether the agent made every expected call; low recall means it skipped an essential action. **Tool precision** asks whether it avoided calls it didn't need; low precision means it misread the goal (*Building Applications with AI Agents*, ch. 9). Rewritten from his version:

```python
def tool_metrics(pred_tools: list[str], expected_calls: list[dict]) -> dict:
    exp, pred = {c["tool"] for c in expected_calls}, set(pred_tools)
    if not exp:                                    # nothing expected
        return {"tool_recall": 1.0, "tool_precision": 0.0 if pred else 1.0}
    tp = len(exp & pred)
    return {"tool_recall": tp / len(exp), "tool_precision": tp / len(pred) if pred else 0.0}
```

These are sets, so a tool that should be called twice counts once, and order is ignored. Use them as diagnostics beside a match mode, not instead of one. (Albada's version returns perfect precision when nothing was expected, even if the agent called a refund tool. That hides exactly the negative cases from [02](02-defining-correct.md#positive-and-negative-cases).)

> **Contradiction.** Albada's companion `param_accuracy` counts an expected call as matched only if `pred["params"] == exp["params"]`: whole-dict equality (*Building Applications with AI Agents*, ch. 9). That fails a refund of `19.990` against `19.99`, or an extra optional argument, as hard as a wrong order ID. Use the per-argument rules above. Keep exact equality for IDs, where it is the rule.

Oshin & Campos test agents at three granularities (*Learning LangChain*, ch. 10): the **final response**, a **single step** (given this prompt and tool set, is the next tool call right?), and the **trajectory**. Their trajectory checks are the match modes in the table: "all expected tools, any order" is `set(expected) <= set(calls)`, "in order" is a subsequence check, and exact match compares the lists. Single-step tests are the cheap ones. They need no environment and pin down one decision, so write them for the steps that fail most. Their examples run each case three times (`num_repetitions=3`) because the agent is non-deterministic ([below](#non-determinism-run-every-task-k-times)).

Score a no-tool baseline beside the tool runs, on tasks the model could attempt without the tool. In Qin et al.'s survey experiment (18 tools, text-davinci-003 and ChatGPT, prompted with the API documentation), giving ChatGPT a calculator dropped its ASDiv maths accuracy from 91.7 without the tool to 74.1 zero-shot, and few-shot examples brought it back to 92.5. On HotpotQA, ChatGPT with a Wikipedia tool scored 19.0 few-shot against 34.5 without it ([arXiv:2304.08354](https://arxiv.org/abs/2304.08354) (Qin et al., ACM Computing Surveys 2025); 2023 models without native function calling, test sets of 10–266 items, one run, no intervals). The authors grade most of their ChatGPT-generated, hand-filtered test sets from the trace, counting a task correct only if a person judges every call accurate and the result reasonable, but report no rubric or agreement figure, and warn that differing setups make the scores hard to compare across tools.

Do the same for anything you add to an agent. SkillsBench ran 87 tasks with and without curated Skills on 18 model-harness pairs, three trials per cell. **Mean pass rate rose from 33.9% to 50.5%, but the lift ran from +4.1 to +25.7 points by pair, and 13 tasks got worse.** On the three pairs tested, Skills the agent wrote for itself scored 8.1 to 11.5 points below none. Read the lift as optimistic: tasks "with no measurable separation between conditions" were rejected, and the benchmark's Skills outscore the ecosystem's (quality 10.1 against 6.2 of 12) ([arXiv:2602.12670](https://arxiv.org/abs/2602.12670) (Li et al., 2026-02, v4 2026-06, preprint); terminal tasks, no length-matched control).

ACES ([arXiv:2608.20614](https://arxiv.org/abs/2608.20614) (Kevin et al., 2026-08, preprint)) runs the same paired design on 58 production skills from NVIDIA's internal repositories across 4 harnesses (947 paired cases), keeping the other installed skills present in both arms, so the lift belongs to the skill and not to having one fewer option to route between. **Mean composite lift was +0.21 (95% CI 0.197 to 0.230 over paired cases; 0.190 to 0.235 when resampling whole skills), and the static gates predicted none of it: structural-lint and LLM-judge scores correlated with live lift at ρ = −0.018 and −0.027 over 62 skills.** Lift fell at the strongest baseline (in Codex, +0.09, +0.11 and +0.05 for GPT-5.2, 5.4 and 5.5, a three-model slice the authors call a demonstration), varied by harness from 0.09 in Terminus-2 to 0.36 in OpenCode, and was negative in 87 of the 947 cases. The composite averages six metrics, two of which the baseline may be unable to satisfy without the skill, so outcome-only lift is lower (0.18). The live judges are unnamed and not checked against people, most cells ran once or twice, and the authors wrote both the skills and the tasks.

Labeling expected tool calls is real work. Two shortcuts:

- **Label from successful traces.** Run the agent, have a human confirm the good runs, and save their trajectories as references.
- **Bootstrap from metadata.** If the system already logs which domain or sub-agent handled a request, that's a free routing label ([case study](13-case-study-support-agent.md#free-labels-from-response-metadata)).

If there's no single correct path, don't force one. Use a **judge over the trajectory** with a rubric ("did the agent look up the order before changing it?") or check **invariants** ("never `issue_refund` before `lookup_order`").

---

## Evaluate the components, then the whole

An agent is a router plus skills plus a final answer. Evaluate each, because an end-to-end failure doesn't say which one broke. The DeepLearning.AI [*Evaluating AI Agents*](https://www.deeplearning.ai/short-courses/evaluating-ai-agents/) course (code: [upstream repo](https://github.com/ginny100/DeepLearning.AI-Evaluating-AI-Agents)) builds exactly this on a sales-data agent: a function-calling router that picks between three tools and loops until it can answer.

![Course agent: a GPT-4o-mini router with function calling dispatches to three tools (lookup sales data, data analysis, data visualization) and loops back](../sources/images/deeplearning-ai-evaluating-ai-agents-lab1-agent.png)
*Image Source: DeepLearning.AI & Arize, Evaluating AI Agents (2025), Lab 1*

Each box gets its own grader. Three are LLM judges and one is plain code:

![One evaluator per component: router function-calling choice and parameter extraction (LLM judge), SQL generation correctness (LLM judge), analysis clarity (LLM judge), visualization code is runnable (code)](../sources/images/deeplearning-ai-evaluating-ai-agents-lab3-router-skill-eval.png)
*Image Source: DeepLearning.AI & Arize, Evaluating AI Agents (2025), Lab 3*

| Component | Question | Grader in the course |
|---|---|---|
| **Router** | Did it pick the right tool with the right parameters? | LLM judge over the tool-call span (Phoenix `TOOL_CALLING_PROMPT_TEMPLATE`) |
| **Skill: SQL lookup** | Does the SQL answer the question? | LLM judge with the instruction and query |
| **Skill: analysis** | Is the analysis clear? Are entities correct? | Two LLM judges, one per criterion |
| **Skill: visualization** | Does the generated code run? | Code: `exec()` it |
| **Path** | Did it converge in a reasonable number of steps? | Code: optimal steps ÷ actual steps |

The router judge, in the course's code. It pulls every LLM span from the traces, judges each tool choice against the tool definitions, and writes the label back onto the span:

```python
# Pull LLM spans that made a tool call (Lab 3)
query = SpanQuery().where("span_kind == 'LLM'").select(
    question="input.value", tool_call="llm.tools")
df = px.Client().query_spans(query, project_name=PROJECT).dropna(subset=["tool_call"])

with suppress_tracing():                     # don't trace the judge itself
    evals = llm_classify(
        dataframe=df,
        template=TOOL_CALLING_PROMPT_TEMPLATE,   # course pastes tool JSON into it
        rails=["correct", "incorrect"],          # output is snapped to these labels
        model=OpenAIModel(model="gpt-4o"),
        provide_explanation=True)                # reasoning stored next to the label
evals["score"] = (evals["label"] == "correct").astype(int)
px.Client().log_evaluations(SpanEvaluations(eval_name="Tool Calling Eval", dataframe=evals))
```

The visualization check needs no judge:

````python
def code_is_runnable(output: str) -> bool:
    code = output.strip().replace("```python", "").replace("```", "")
    try:
        exec(code)        # course shortcut: run untrusted code only in a sandbox
        return True
    except Exception:
        return False
````

These APIs have moved since the course was recorded. `px.Client()` and `SpanEvaluations`/`log_evaluations` are legacy: current Phoenix uses `phoenix.client.Client` and logs span annotations. phoenix.evals 2.x replaces `llm_classify(dataframe=…)` and `OpenAIModel` with `create_classifier` and `LLM(provider="openai", model=…)`. The course also fills the template's `{tool_definitions}` slot with string `.replace()` calls that turn the JSON braces into quotes. Pass the definitions in as a template variable instead. "Runs without raising" is also a weak check: code that draws an empty chart passes it.

The harness is a component too, so report model and harness together. On Terminal-Bench (89 tasks, at least 5 runs per pair, about ±3 points), GPT-5 resolved 49.6% in Codex CLI and 35.2% in Terminus 2, though the authors conclude that "model selection is usually more important than agent scaffold" (Merrill et al., [above](#grade-the-outcome-by-state-not-by-words)).

Inside a harness, an instruction-following score also counts rules the agent would have kept anyway. Harness-IF ([arXiv:2608.11727](https://arxiv.org/abs/2608.11727) (Huang et al., 2026-08, preprint)) labels each rule by what agents do with no instruction at all, and scores the rules that go against that default separately. Over 12 models on 60 multi-turn coding items in 3 rounds (2,160 runs, one harness setup), **every model scored lower on against-default rules, by 3.6 to 7.4 points (mean 5.81)**: Claude Opus 4.7 went from 85.9% to 78.6%. Where a rule lives matters too. In a small synthetic pilot (9 older model builds, 916 runs, deterministic scoring), rules placed in tool or skill descriptions lost conflicts more often than rules in the system prompt, a project file or the user turn, though only 6 of the 9 builds reproduced that ordering. Read the levels with care: 86.8% of the verdicts involve a GPT-5.2 judge, swapping the judge gave 62.1% agreement (κ 0.163 on 116 paired verdicts), and the 60 items were picked from 80 for difficulty.

The same holds for whole agent products on production work. AlphaEval ([arXiv:2604.12162](https://arxiv.org/abs/2604.12162) (Lu, Xu, Zhang, Hua et al., 2026-04, preprint)) built 94 tasks with 7 companies that deploy agents, scored each with at least two kinds of grader weighted by the company's experts, and ran 14 model-and-product pairs. **The same Claude Opus 4.6 scored 64.41 in Claude Code, 61.85 in Cursor, 61.31 in GitHub Copilot and 53.45 in Codex**, and 64.41 was the best score of any pair. Only that top pair ran three times (64.41, 95% CI ±1.83), so the 0.5-to-3-point gaps among the first three products are within run-to-run noise; the Codex gap is not, though each product ran its own pinned CLI version and every other pair ran once. On 20 tasks, the Opus 4.6 judge agreed with each of two experts (κ 0.697 and 0.780 over 1,000 rubric-point judgments) about as well as the experts agreed with each other (κ 0.691), but the judge is also the top-scoring model and no judge swap was run.

For a coding agent, the component before the patch is **localization**: did it edit the right place? SWE-PolyBench ([arXiv:2504.08703](https://arxiv.org/abs/2504.08703) (Rashid et al., 2025-04, preprint)) scores it as set precision and recall of the files the agent changed against the files in the reference patch, and again at the level of the deepest class or function node each change touches. On its 2,110 tasks in four languages, with Claude 3.5 Sonnet under three adapted agents, **the agent with the best Python file retrieval (recall 60.9, precision 77.6) passed 20.1% of Python tasks, and the other two passed 24.1%, one of them at precision 44.2**. The authors call good retrieval "(most of the time) a necessary but not sufficient condition", but they compute no correlation, and the metric is scored against one reference patch, so a valid fix made elsewhere would score low. The pass rate also fell with the number of files to change (Aider: 17.7% for one file, 7.9% for five or more). The run count is not stated; the ± values are bootstrap standard errors, which match what resampling tasks from one run would give.

A human baseline does not remove the harness from the comparison. In a penetration test of a live university network of about 8,000 hosts ([arXiv:2512.09882](https://arxiv.org/abs/2512.09882) (Lin et al., ICLR 2026; read as the 2026-03 arXiv revision)), ten professionals and several agents were scored on the sum of a complexity score and a severity weight for each valid finding. GPT-5 outscored 5 of the 10 humans inside the authors' ARTEMIS scaffold, 2 inside Codex and none inside CyAgent. ARTEMIS was scored on the first 10 hours of a 16-hour run, while Codex and CyAgent stopped within 20 minutes and 2 hours, and the hourly costs are averages over the 16 hours. The ARTEMIS configuration that outscored 9 of the 10 (95.2 against 111.4 for the best human, 82% of submissions valid) cost $59 an hour; the $18.21-an-hour configuration is the one that beat 5, with 55% of its submissions valid. Each agent ran once, there are no intervals, and the authors scored their own agent without reporting agreement between raters.

Component scores also give you a ceiling for the whole. Everitt, Garbacea et al. ([arXiv:2504.11844](https://arxiv.org/abs/2504.11844) (Everitt et al., 2025-04, preprint)) measure each subtask alone, then compare the composite task against what full use of those capabilities would earn, scaled so a random policy scores 0 and full use scores 1. In Blocksworld (8 models queried in March and April 2025, several of them older builds, 3 to 5 blocks, 30 seeds each), **every model took fewer height measurements when the measuring was one step of a larger task than when it was the whole task**, and GPT-4 Turbo and GPT-4o, near-perfect at executing plans alone, did no better than the rest on the Plan and Execute composite. Most models fell short of full use; Claude 3.7 Sonnet and Gemini 2.0 Flash came closest. A low composite score can therefore mean an agent that has the skill and doesn't use it, not one that lacks it. It is one synthetic environment, the capability estimates assume the subtasks compose, thinking models were excluded, and the effect of a motivating prompt was tested on one model and one task. A narrative synthesis of 27 benchmark, taxonomy and audit papers from 2023 to 2026 ([arXiv:2607.05775](https://arxiv.org/abs/2607.05775) (Albayaydh, Zhao and Flechais, 2026-07, preprint)) reaches the same conclusion across the field: sub-skill competence does not reliably compose into end-to-end success, and failure compounds non-linearly with task length, which the authors offer as candidate patterns rather than established laws. It groups failures into six clusters (tool invocation, planning and constraints, long-horizon degradation, multi-agent coordination, safety, and measurement validity), the last of which says that part of the leaderboard progress is corrected measurement error. It reruns nothing and rarely gives the setup behind the figures it quotes, so use it as a map to the primary studies, not as a source for their numbers.

### Routing vs. domain evals in multi-agent systems

With a supervisor and sub-agents, split the suites ([case study](13-case-study-support-agent.md#architecture-routing-vs-domain-evals)):

- **Routing eval**: does the supervisor pick the right sub-agent? Seed with queries on the boundaries between domains.
- **Domain eval**: given correct routing, does each sub-agent call the right tools and produce the right output?

Neither replaces the other. A retrieval-quality eval and an answer-quality eval together still miss "right answer, wrong sub-agent" and "right sub-agent, wrong tool path".

---

## Non-determinism: run every task k times

The same task can pass on one trial and fail on the next. A single run per task tells you about luck. Run each task **k** times (3–10 is typical) and report rates.

Two metrics answer different questions:

| Metric | Definition | Question | Rises or falls with k |
|---|---|---|---|
| **pass@k** | P(at least one of k trials succeeds) | "Can it do this at all, given retries?" | Rises |
| **pass^k** | P(all k trials succeed) | "Does it do this *every* time?" | Falls |
| **Best@k** | Score of the best of k trials | "What's the quality ceiling?" (continuous scores, open-ended tasks) | Rises |
| **Worst@k** | Score of the worst of k trials | "How bad is the bad day?" (the continuous-score version of pass^k) | Falls |

If per-trial success is *p* and trials are independent: pass@k = 1 − (1 − p)^k, and pass^k = p^k. At p = 0.75 and k = 3: pass@3 = 0.98, pass^3 = **0.42**.

- **pass@k** fits tools where a user or system can retry and pick a good result: code generation with tests, candidate generation. From *n* samples with *c* correct, the unbiased estimator is pass@k = 1 − C(n−c, k) / C(n, k) (Chen et al. 2021, the Codex paper). Codex drew n = 200 samples per HumanEval problem to report k ≤ 100. Plugging the observed pass rate into 1 − (1 − p̂)^k underestimates pass@k by a wide margin, and the gap doesn't fully close even at n > 5k. The best sampling temperature also rises with k: 0.2 for pass@1 and 0.8 for pass@100 on a 679M model. Codex-12B scores 28.8% pass@1 and 72.3% pass@100 ([arXiv:2107.03374](https://arxiv.org/abs/2107.03374) (Chen et al., 2021 ⚑), Appendix A). Choosing a candidate needs a grader: from 100 Codex-S samples, taking the one with the highest mean log-probability solves 44.5% of problems, while an oracle that picks a sample passing the tests solves 77.5%. MBPP's 137B model shows the same temperature pattern (low temperature is best with one try, higher wins within 10 samples), and beam search did worst of all because it looped ([arXiv:2108.07732](https://arxiv.org/abs/2108.07732) (Austin et al., 2021 ⚑)).
- **pass^k** fits customer-facing agents, where every user gets one try. τ-bench (Yao et al. 2024) introduced it and showed agents that look fine on pass@1 falling sharply at pass^8.

The two can rank models in opposite orders. On math benchmarks, RLVR-trained models beat their base models at k=1 but lose at large k: base Qwen2.5-32B solves about 9% more Minerva problems than its RL-trained version at k=128 ([arXiv:2504.13837](https://arxiv.org/abs/2504.13837) (Yue et al., 2025-04)). Pick the k that matches how the system is used before comparing.

The attempt budget can move the score as much as the model does. MLE-bench ([arXiv:2410.07095](https://arxiv.org/abs/2410.07095) (Chan et al., ICLR 2025)) scores an agent on 75 Kaggle competitions by the share of attempts that would have earned a medal on the competition's private leaderboard. With the AIDE scaffold, 24 hours and one GPU per competition, **o1-preview medalled on 16.9% ± 1.1 of attempts at pass@1 and 34.1% at pass@8, and GPT-4o at pass@6 (17.0%) matched o1-preview at pass@1** (16 and 36 seeds, mean ± standard error). The scaffold moved it as far: GPT-4o scored 8.7% under AIDE, 4.4% under OpenHands and 0.8% under MLAB. Giving GPT-4o 100 hours instead of 24, and ten times the search nodes, raised it only to 11.8%. So a leaderboard row needs its k, scaffold and time limit beside the model name. The pass@k here counts a medal on any of k attempts as graded on the hidden test set, and the agent has no way to make that pick itself. The medal bar is approximate too, since the authors rebuilt each train/test split and grader, and the agents had 24 hours and newer tools where the human competitors had weeks.

Check which of the k runs a headline reports. ScienceAgentBench ([arXiv:2410.05080](https://arxiv.org/abs/2410.05080) (Chen et al., ICLR 2025)) runs each of its 102 data-science tasks, drawn from 44 publications, three times and reports the best run, chosen by success first and cost last. **Claude 3.5 Sonnet with self-debug solved 32.4% of tasks as best of three and 22.9% (standard deviation 2.0) as the mean of the three runs**; o1-preview went from 42.2% to 27.1%. The reported cost is that of the selected run, not of all three. The same table has a scaffold result: for Claude 3.5 Sonnet without expert-provided knowledge, best of three, the simple self-debug loop beat OpenHands CodeAct by 10.8 points (32.4% against 21.6%) at $0.057 a task against $0.958. Tasks are graded by executing the program against a per-task criterion, and figures by a GPT-4o judge averaged over three samples, whose agreement with people the paper does not measure. To stop an agent reading test labels instead of training a model, the authors replaced the labels with dummy values, but they show one case of this catching a shortcut, not a count.

The aggregate over tasks needs the same care as the aggregate over runs. ALE-Bench ([arXiv:2506.09050](https://arxiv.org/abs/2506.09050) (Imajuku et al., NeurIPS 2025 Datasets and Benchmarks)) places an agent's score on the original human leaderboard of 40 AtCoder heuristic contests and converts the rank to a per-problem performance figure. AtCoder's rating, in the authors' words, "is designed to reward high scores without penalizing low ones". With four hours of iterative refinement per problem, o4-mini-high sat in **the top 11.8% of humans by rating (2104) but the top 22.3% by average performance (1520)**, and it reached a performance of 1600 on 32.5% of problems against 56.2% for humans in its rating band. The authors recommend the average. These are single runs; only the one-shot setting has a five-run check.

Worst@k does for rubric scores what pass^k does for pass/fail. HealthBench samples *N* responses per conversation, takes the minimum score over every subset of size *k*, and averages those minima. That gives an unbiased estimate, the same idea as Chen et al.'s pass@k estimator. o3 scores 0.60 on average, but its worst-of-16 is about a third lower, and GPT-3.5 Turbo's worst-case score reaches 0 by k = 7 ([arXiv:2505.08775](https://arxiv.org/abs/2505.08775) (Arora et al., 2025-05); OpenAI benchmarking OpenAI models on its own rubrics). In a domain where one bad answer does harm, the bottom of the curve is the number to gate on.

![Worst-at-k score against k from 1 to 16 for five OpenAI models. o3 falls from about 0.60 to about 0.36; GPT-3.5 Turbo falls to zero by k = 7](../sources/images/arora-healthbench-fig7.png)
*Image Source: Arora et al., [HealthBench](https://arxiv.org/abs/2505.08775) (2025), Fig. 7*

State which one you report. Yang et al. (2026) give both for a common set of *n* tasks and *R* repeats: **Mean@R** = average over all n·R binary attempts (the expected one-shot success rate), and **pass@R** = fraction of tasks solved in *at least one* repeat. Neither can be reconstructed from the other once aggregated, so log per-attempt results, not just the summary.

Also report the **per-task pass rate distribution**. A suite at 70% could be "every task passes 70% of the time" (flaky) or "70% of tasks always pass, 30% never do" (capability gaps). They need different fixes. Real suites are usually a mix. Over 64 trials per question on BrowseComp, Deep Research solved 16% of the questions every time, failed 14% every time, and landed somewhere in between on the rest ([arXiv:2504.12516](https://arxiv.org/abs/2504.12516) (Wei et al., 2025-04)).

Report the spread per task, and say which score you took from each run. CALM ran five seeds per Jericho text game. On `library` the mean was 9.02 with a standard deviation of 5.07, against 30.39 ± 3.01 on `zork1`, and most of its ablations ran once each. Each run's score was the mean of its last 100 training episodes: 9.4% of the maximum averaged over 28 games. The best trajectories the same agents had found during exploration averaged 14.7%, higher than any model in the paper ([arXiv:2010.02903](https://arxiv.org/abs/2010.02903) (Yao et al., EMNLP 2020); GPT-2 action generator with an RL agent, 2020 baselines). The final policy and the best run seen are Mean@R and Best@k by other names, and they can differ by half again.


With 8 runs per agent, a gap that looks large can still fail a significance test. Sherwood, Aybar and Kaplan ([arXiv:2604.25067](https://arxiv.org/abs/2604.25067) (Sherwood et al., 2026-04, preprint)) gave four coding agents 3 hours on one consumer GPU to build an AlphaZero-style Connect Four player, then rated every trial in a round-robin tournament that includes a perfect solver, fixed at a Bradley-Terry rating of 2000. **Claude Opus 4.7 beat the solver moving first in 7 of 8 trials, against 2 of 8 for Opus 4.6 and 0 of 8 for GPT-5.4 and Gemini 3.1 Pro**, yet the Opus 4.7 vs 4.6 rating gap was not significant after Holm correction (p = 0.062); the abstract's "significantly better" holds only for the first-mover wins against the other agents. Log time used as well as the score: GPT-5.4 stopped after a mean 0.92 of its 3 hours. With a shorter, casual prompt it used 1.89 to 2.73 hours, but its rating did not change significantly, so the authors' sandbagging probe (4 trials per cell) stays inconclusive. The task prompt was mostly written with Claude, and the Gemini CLI configuration changed before trial 5 and again before the last three of its 8 trials.

---

## Efficiency metrics

Log these on every trial. They catch regressions that pass rates miss:

| Metric | Why |
|---|---|
| **Steps / turns to completion** | Rising steps at a flat pass rate means the agent is thrashing toward the right answer |
| **Tool calls** (total, per tool, failed) | Retry storms, wrong-tool loops |
| **Tokens** (input / output / cached) | Cost driver. Context bloat shows here first |
| **Latency** (p50 / p95, time to first token) | User experience |
| **Cost per success** | The sustainability metric. Failed runs are pure cost, so at 50% success the real cost is 2× the per-run cost |
| **Convergence** | Optimal steps ÷ actual steps (the course's Lab 4 metric, [below](#convergence-in-practice)) |

**Log why each failed run ended, not only that it failed.** AgentBench (29 LLMs, 8 environments from an OS shell to ALFWorld and WebShop, temperature 0) sorts every run into completed, context limit exceeded, invalid format, invalid action, or task limit exceeded (out of turns, or stopped for repeating itself). The mix depends on the environment. Averaged over all models, task limit exceeded was 82.5% of outcomes on lateral-thinking puzzles and 67.9% on knowledge-graph tasks, invalid format was 53.3% on database tasks, and invalid action was 64.1% in ALFWorld. **Over 90% of the runs that hit the task limit had two responses with ROUGE-L ≥ 0.8 in their last 10 rounds**: the agent was looping, not making slow progress (partly by construction, since the ALFWorld harness ends a run that repeats itself three times). Open models of 70B or less produced invalid actions about three times as often as API models (13.6% against 4.6%) ([arXiv:2308.03688](https://arxiv.org/abs/2308.03688) (Liu et al., ICLR 2024)). Each reason has a different fix: a format failure points at the prompt or the parser, and a loop at a repetition check in the harness. AgentBench itself ran each model once, greedily, so its per-model scores carry no variance estimate ([below](#non-determinism-run-every-task-k-times)).

On long tasks, how a run ends also tells you whether the agent kept working. AutoLab ([arXiv:2606.05080](https://arxiv.org/abs/2606.05080) (Xu et al., 2026-06, preprint)) gives agents 36 optimisation tasks (faster kernels, better training runs) with budgets of 2 to 12 hours and scores the improvement each one reaches. With 11 models in one harness, 3 rollouts each, **Claude Opus 4.6 averaged 0.68 over its rollouts, with a median of 57 steps, against 0.50 for Gemini 3.1 Pro, with 12**. Hand-reading 302 zero-score rollouts found two opposite failures: some models submitted after a first pass, and others ran out the clock without submitting. Score rose with steps and runtime, but the paper gives the correlation as plots across models, with no coefficient and no controlled test. The harness moved scores as far as the model did. Moving Kimi K2.6 from the pi-mono harness to the authors' modified mini-swe-agent, prompted not to submit on the first pass, raised it from 0.21 to 0.64 on 25 CPU tasks, at $2.05 a trial against $0.40. Three rollouts leave a wide spread (the gap between best-of-3 and mean grows with per-task standard deviation, r = 0.84 across the 11 models), and the appendix gives Opus's averages as 0.77 and 0.85 against 0.68 and 0.76 in the main table, unexplained. Log the submit step and the budget used beside the score, so "quit early" and "never finished" don't both read as a zero.

The step where a run ends is a poor guide to where it went wrong. A study of 1,184 failed Terminal-Bench trajectories ([arXiv:2607.09510](https://arxiv.org/abs/2607.09510) (Zhao et al., 2026-07, preprint)), covering 89 tasks and 21 systems (3 scaffolds by 7 models), labelled the decisive error in each run, with Claude Opus 4.6 drafting the labels and two of four human annotators finalising each run (Cohen's κ 0.83 for root causes). **The decisive error came at a median step 7 of a median 27, and the first visible sign of it at a median step 16**, in the 72% of runs that showed one; the other 28% never surfaced a sign. In 26% of failed runs the agent claimed success with fabricated evidence. Each figure is a point estimate with no interval, timeouts were excluded, the decisive error is labelled in hindsight, and both annotators started from the same model draft.

Finding that step need not take a judge. OAT ([arXiv:2607.12747](https://arxiv.org/abs/2607.12747) (Yeh et al., NeurIPS 2026)) learns from successful runs only. It reads each step's hidden states from Qwen3.5-27B, models how they usually evolve, and scores each step of a failed run by how far it strays. Trained on 103 successful MCP-Atlas trajectories and tested on 88 failed ones the authors annotated (5 seeds), **its change-point variant reached step-level F1 0.435 against 0.181 for a prompted GPT-5 judge and 0.255 for picking steps at random, at 7 ms against about 40 s a trajectory**. A plain Isolation Forest on the same features reached 0.411, so most of the gain comes from using success as the reference, not from the sequence model. On 184 Who&When failures from other agents its top-k variant reached F1 0.225 (the change-point one 0.211) against 0.152 for GPT-5, after aligning its features to the unlabelled test set. The authors call it anomaly detection, "not equivalent to causal attribution": it often flags a later symptom and misses the root cause, it needs hidden-state access, and the labels carry no agreement figure. Read its flags as where to start reading a trace ([08](08-tracing-and-observability.md#traces--evals--datasets)), not as the cause.

A task with a known optimum lets you split a failure into "didn't gather the evidence" and "gathered it but didn't use it". Menaged et al. ([arXiv:2606.16576](https://arxiv.org/abs/2606.16576) (Menaged et al., 2026-06, preprint, read as v2 2026-09, under review)) hide a randomly sampled finite automaton behind two tools (is this string accepted? is this my automaton?) and give the agent twice the queries that the classic learning algorithms L* and TTT need, so every instance is solvable within budget and size sets the difficulty. **At 8 to 9 states the best of 3 models solved 30.0% of instances, or 57.5% with a scaffold that carries working memory between turns** (40 instances per size bucket, one run each), and among successful runs at that size the best pair still used about 23.5% more queries than TTT. To classify a failure, the authors hand the agent's collected answers to classic passive learners: if none of them can recover the automaton, the agent planned its queries badly; if one can, the agent had the evidence and reasoned badly. Only DeepSeek and Gemini models ran, and the stateful prompt also lets the model write its reasoning, which the stateless one forbids, so the scaffold gain mixes the two.

### Convergence in practice

The course's Lab 4 asks the same question 17 ways ("average quantity per transaction", paraphrased), runs the agent on each, and scores how close each run came to the shortest path:

![Convergence experiment: a dataset of paraphrased questions goes through the task run_agent_and_track_path, the evaluator evaluate_path_length, and out comes a convergence score](../sources/images/deeplearning-ai-evaluating-ai-agents-lab4-convergence-experiment.png)
*Image Source: DeepLearning.AI & Arize, Evaluating AI Agents (2025), Lab 4*

```python
def run_and_track(example):                      # the experiment's task
    msgs = run_agent([{"role": "user", "content": example.input["question"]}])
    return {"path_length": len(msgs)}            # counts messages, not tool calls

experiment = run_experiment(dataset, run_and_track, experiment_name="Convergence Eval")
optimal = min(o["path_length"] for o in outputs if o)   # shortest run observed

@create_evaluator(name="Convergence Eval", kind="CODE")
def convergence(output) -> float:
    return optimal / output["path_length"] if output else 0.0   # 1.0 = shortest

experiment = evaluate_experiment(experiment, evaluators=[convergence])
```

Read the score for what it is. "Optimal" means the shortest run *observed*, not the shortest possible, so a suite where every run thrashes can still score near 1.0. The score is also relative to this batch, so it doesn't compare across agent versions unless you fix the reference length. Set the optimum by hand (or from a confirmed good trace) before using it as a regression gate.

### Why agent cost grows faster than the step count

Every turn re-sends the whole context. Li's worked example (*AI Agents in Depth*, Table 6-4) is a three-turn refund agent: 9,500 input tokens, 470 output, **$0.022** in total. Prefix caching saves nearly half the input cost. The amplifiers are what break the budget:

- **Thinking tokens.** 500–2,000 extra per turn can multiply cost 3–5×. At 50 tokens/s, 2,000 thinking tokens is 40 s of latency.
- **Big tool outputs.** A 5,000-token web page returned on turn 2 is billed again on every later turn.
- **Detours.** Ten turns instead of three, and the context passes 20,000 tokens.

So the levers are turn count and context growth, not just a cheaper model ([02-context/03](../../../ai-engineering/02-context-engineering/notes/03-budgeting-the-window.md)). Set a **per-task cost cap** in the harness, and log thinking tokens separately.

**Latency has two stages.** Prefill reads the context and sets **time to first token** (queueing + prefill; grows with context). Decode sets tokens/s. Report **p95**, not the mean: the mean hides the slow minority.

**Report a budget–capability curve, not one point.** RE-Bench (Wijk et al. 2025): at a 2-hour budget the best agent scored about 4× human experts. At 8 hours humans narrowly passed it, and with 32 hours total across attempts they scored about 2× the agent. Leading at a short budget doesn't predict long-horizon ability. Compare at budgets close to the real workload.

**Count the human review time in any speedup claim.** GPT-5 finished GDPval's expert tasks 90× faster than the experts, but someone has to check the output. Once the authors added an expert's 109-minute average review and the expert redoing the work whenever the model lost (61% of the time), the speedup fell to 1.12× for "try the model once, then fix it yourself" and 1.39× for "retry until it's good enough". The cost advantage fell from 474× to 1.18–1.63×. For GPT-4o, which won 12.5% of comparisons, the retry strategy ended up *slower* than the expert alone, at 0.46× ([arXiv:2510.04374](https://arxiv.org/abs/2510.04374) (Patwardhan et al., 2025-10); OpenAI-run, self-reported human times, 220 tasks).

**Plot accuracy against cost, and include simple baselines.** Kapoor et al. reran the HumanEval agents from the leaderboard (164 problems, five runs each, April 2024 prices). A warming baseline (retry GPT-4 when the example tests fail, raising temperature from 0 to 0.5 across retries) reached 93.2% for $2.45. LDB with GPT-4 reached 93.3% for $6.36, and LATS with GPT-4 reached 88.0% for $134.50. "For substantially similar accuracy, the cost can differ by almost two orders of magnitude." None of the original papers reported cost as a headline metric, and the authors found none that compared against such baselines. Log **input and output token counts, not just dollars**, so the comparison can be re-priced when rates change ([arXiv:2407.01502](https://arxiv.org/abs/2407.01502) (Kapoor et al., 2024-07)).

![Accuracy against cost on HumanEval. A dashed Pareto frontier runs from GPT-3.5 through Escalation to Warming (GPT-4) and LDB (GPT-4). LATS (GPT-4) sits far right at about $134 with lower accuracy](../sources/images/kapoor-2024-ai-agents-that-matter-fig1.png)
*Image Source: Kapoor et al., [AI Agents That Matter](https://arxiv.org/abs/2407.01502) (2024), Fig. 1*

The same group repeated the exercise at scale. The Holistic Agent Leaderboard ([arXiv:2510.11977](https://arxiv.org/abs/2510.11977) (Kapoor et al., ICLR 2026; read as arXiv v1, 2025-10)) ran 21,730 rollouts of 9 models on 9 benchmarks for about $40,000 at September 2025 prices. **The most expensive model sat on the cost-accuracy frontier for 1 of 9 benchmarks, and in 21 of 36 same-scaffold comparisons a higher reasoning setting gave equal or lower accuracy.** On Online Mind2Web (300 tasks), SeeAct with GPT-5 cost $171 and Browser-Use with Claude Sonnet 4 cost $1,577 for 42.3% against 40.0%. Most of these are single runs, which the authors say they "were forced to rely on", so the 21 of 36 has no noise estimate and several benchmarks are subsets of 33 to 50 tasks. They also had a GPT-5 judge read 2,184 transcripts against six rubrics (1,634 once TAU-bench is set aside for the failure-rate tables) and found what a pass rate hides: a scaffold in a benchmark's official repository carried benchmark examples in its few-shot prompt, agents located gold answers on HuggingFace or arXiv, and a customer-service agent charged the wrong card. The judge's flags were checked against people for precision only (0.87 to 1.00 on 31 to 49 samples, one rubric per benchmark), so the paper can show that these things happen, not how often.

The listed price does not rank cost either. Chen et al. ([arXiv:2603.23971](https://arxiv.org/abs/2603.23971) (Chen et al., 2026-03, preprint; read as v2, 2026-05)) ran 8 models on 12 tasks (9 single-turn, 3 agentic) at 2026-05-01 prices: **in 106 of 336 model-pair-by-task comparisons (31.5%), the model with the lower listed price cost more in total**. Gemini 3 Flash lists at $3.50 per million input plus output tokens against $17.50 for GPT-5.4, yet cost $705 against $509 over all 12 tasks. On the reversed single-turn pairs, thinking tokens explained over 95% of the gap; on agentic tasks, turns and cached input tokens did (turns alone drove over 80% of Kimi K2.6's gap to GPT-5.4 on Cybench). The same query on the same model varied in cost by up to 9.7× across runs, which suggests a verdict from one run can flip. Each model ran at one reasoning setting, and the paper scores cost alone, not cost per success, so measure cost per success on your own tasks, over repeats.

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

### Multi-turn evaluation

Two approaches, each with a trade-off:

- **Canned conversations.** Score each turn against a fixed, scripted history. Isolates turns and is reproducible, but misses compounding errors, because the history never reflects what the agent actually said.
- **Simulated user.** An LLM plays the user with a goal and persona, and the conversation runs to the end. Tests the real thing end to end, but inherits the simulator's biases and adds variance. Give the simulator a clear goal and stop condition, and calibrate it: does it behave like your real users?

A single cooperative simulated user flatters the agent. In GAUGE (Bodhwani et al., τ²-bench retail, 12 agent variants), swapping the default τ² user for a population of personas (anxious, skeptical and others) **cut mean verifiable reward by 42%** (0.47 → 0.27). Whoever grades the conversation also has to see the tool calls and the outcome. A transcript truncated mid-task scored reward 0, yet human raters gave it 4.6/7 for satisfaction. A judge that saw the tool calls and the goal tracked task success, and a judge rating "how the conversation felt" did not ([15](15-calibration-against-human-labels.md#the-procedure)). A free check catches the crude case: did the conversation finish at all? That signal tracked reward at ρ 0.87 when variants were deliberately broken. But only 3.5% of real failures were truncations, so semantic failures still need the judge ([arXiv:2609.12191](https://arxiv.org/abs/2609.12191) (Bodhwani et al., 2026-09)).

A user who is confidently wrong is a harder test still. XYEval ([arXiv:2609.23939](https://arxiv.org/abs/2609.23939) (Wu, Li, Tafjord and Kim, 2026-09, preprint)) appends one plausible but wrong suggestion ("I think the issue is in…"), written by an LLM that saw the reference answer (or by expert rules for τ²-bench), to each task of six existing benchmarks (five agentic, plus single-turn HLE), and leaves the environment and grader unchanged, so the score drop measures how far the agent follows the user's bad idea instead of the goal. **All 5 frontier models lost score on Terminal-Bench, and in nearly every other cell: Gemini 3.1 Pro fell from 67.4 to 36.0 on Terminal-Bench (89 tasks)**, and GPT 5.5 from 80.5 to 64.0 on a 200-task SWE-bench Verified subsample. On τ²-bench the Gemini agents' thinking disagreed with the suggestion in 92.1% of traces on average (per an LLM judge with no human check), yet they often complied without telling the user. A generic "beware the XY problem" system prompt cut Gemini 3.1 Pro's relative drop on Terminal-Bench from 46.7% to 18.3%, not to zero. The paper reports no run count or intervals, the distractor generator differs between cells, and the defence tests cover Gemini models only. The recipe is cheap to copy: mutate your own suite's inputs, keep its oracle, and compare.

Generating the scenarios scales the suite but moves the trust problem to the generator. IntellAgent ([arXiv:2501.11067](https://arxiv.org/abs/2501.11067) (Levi and Kadar, 2025-01, preprint)) turns the agent's system prompt into a graph of policies, samples policy combinations at a chosen complexity, writes 1,000 scenarios with matching database states per domain, and has an LLM critique each dialog policy by policy, which catches failures such as acting without user consent that a final-state check cannot see. On τ-bench's airline and retail domains **its success rates correlated with τ-bench's across six 2024 models (Pearson 0.98 airline, 0.92 retail), in nearly the same order**, but its absolute scores ran far higher (claude-3.5-sonnet 0.70 against 0.46 on airline), so it reproduces the order, not the difficulty. Six points per domain is a small sample, GPT-4o generates, plays the user, judges and is one of the six agents, and nothing was checked against human labels.

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
- **Isolate trials.** Parallel trials must not share mutable resources, and neither should sequential ones. WebArena's Reddit clone rate-limits posting, so "if the tasks involving Reddit posts are evaluated one after another, they are much more likely to fail." Task order changed the score (Kapoor et al., [above](#efficiency-metrics)). Shuffle task order between runs. A score that moves with order means the tasks are not independent.
- **Re-run the scoring, not just the agent.** The same audit found two leaderboard agents (LATS, STeP) that marked some failed tasks as correct and dropped a few tasks from the benchmark.
- **Stub or record unstable externals** (live web, third-party APIs) for regression suites. Keep a separate live suite for capability checks.
- **Treat a 0% task as suspect.** If a task fails every trial across several model versions, check the task before the agent. It's often broken: unreachable state, wrong reference, missing permission. On BrowseComp, 21 of the 118 questions that Deep Research never solved had a bad reference answer ([03](03-eval-datasets.md#lessons-from-public-benchmarks)). For the rest, the authors gave the model the reference answer and asked it to find supporting evidence. It usually could, which showed the questions were hard rather than broken (Wei et al., [above](#non-determinism-run-every-task-k-times)). [12](12-failure-modes.md#eval-bugs-look-like-agent-bugs) has more checks for a broken task.
- **Keep the answer out of reach.** An agent that can't do the task the intended way will look for another way. In one of Anthropic's capture-the-flag evals, Claude 3.7 Sonnet couldn't connect to the vulnerable service, so it reasoned that the service was running locally, searched the whole machine and found the flag in plaintext ([PDF](https://assets.anthropic.com/m/785e231869ea8b3b/original/claude-3-7-sonnet-system-card.pdf) (Anthropic, 2025-02)). Store reference answers, grader code and hidden tests where the agent's tools can't read them, and read the transcripts of surprising passes.

---

## Checklist

- [ ] Outcome graded by end state where possible, not by what the agent says
- [ ] Trajectory graded: match mode chosen per task, or invariants, or a trajectory judge
- [ ] Router, each skill, and end-to-end evaluated separately
- [ ] Each task run k times; pass^k reported for user-facing agents
- [ ] Steps, tokens, latency and cost per success logged per trial
- [ ] Error-handling and adversarial suites present
- [ ] Environment reset per trial; 0% tasks investigated before blaming the agent

---

## Pitfalls

- **Grading what the agent says.** Symptom: "I've issued your refund" passes with no refund row. Fix: check the end state directly: the row with the right amount, the repo's tests, the query's result rather than its SQL text.
- **Enforcing a single golden path.** Symptom: Anthropic's flight-booking agent found a cheaper fare through a policy loophole and failed the trajectory check. Fix: use trajectory checks for invariants such as "never book before confirming", with match modes chosen per task.
- **Reporting pass@k for a customer-facing agent.** Symptom: a high headline with users hitting failures. At p = 0.75 and k = 3, pass@3 is 0.98 and pass^3 is 0.42. Fix: report pass^k or Worst@k where each user gets one try, and say which metric you report.
- **Treating a suite average as one thing.** Symptom: 70% hides either flakiness or a capability gap. Fix: plot the per-task pass rate. On BrowseComp, Deep Research solved 16% of questions in all 64 trials and failed 14% in all 64.
- **Sharing state between trials.** Symptom: order-dependent failures, as with WebArena's rate-limited Reddit clone. Fix: reset state each trial, isolate parallel runs, and shuffle task order. A score that moves with order means the tasks aren't independent.
- **Blaming the agent for a 0% task.** Symptom: weeks spent on a broken task. 21 of the 118 BrowseComp questions Deep Research never solved had a bad reference answer. Fix: check the task first, and give a capable model the reference to see if evidence can be found.
- **Leaving the answer in reach.** Symptom: a surprising pass, such as Claude 3.7 Sonnet finding a capture-the-flag answer in plaintext after searching the machine. Fix: keep references, grader code and hidden tests away from the agent's tools, and read surprising passes.
- **Speed and cost claims without review or baselines.** Symptom: GPT-5's 90× speedup on GDPval falls to 1.12× to 1.39× once review and redo time are counted. Fix: count human time, plot accuracy against cost, and include simple baselines.

## Try it

1. Expected calls are `lookup_order`, then `issue_refund`. The agent calls `lookup_order`, `lookup_order`, `get_policy`, `issue_refund`. Score it under exact and in-order match, and with `tool_metrics` above.

   <details><summary>Answer</summary>

   Exact fails, because there are extra calls. In-order passes, since the expected calls appear in order. Running `tool_metrics` gives recall 1.0 and precision 0.67: nothing essential was skipped, and `get_policy` was extra. The duplicate `lookup_order` doesn't show, because these are sets, which is why they sit beside a match mode rather than replacing one.

   </details>

2. An agent's per-trial success is 0.95 and trials are independent. What is pass^8? And what is the real cost per success of Li's $0.022 refund run at 50% success?

   <details><summary>Answer</summary>

   0.95⁸ = **0.66**, so an agent that looks fine trial by trial gets through all eight only two-thirds of the time. Cost per success is $0.022 / 0.5 = **$0.044**, since failed runs are paid for too.

   </details>

3. Your support agent sits at 70%. The first run shows half the tasks pass 5 of 5 and half pass 2 of 5. What do you do differently than if 70% of tasks always passed and 30% never did?

   <details><summary>Answer</summary>

   Here half the suite is flaky, which points at non-determinism: ambiguous instructions, unstable tools or shared state, so read the failing trials against the passing ones. With the 70/30 split the agent has a capability gap on a set of tasks, so check those tasks for faults, then add tools or instructions for them.

   </details>

4. Run section 4 of the [conversation scoring lab](../practice/conversation_scoring_lab.py) (`cd practice && uv run conversation_scoring_lab.py`). On which pattern does the minimum of turn scores beat the mean by most, and on which does neither work? Why can no threshold fix the second without breaking the other rows?

   <details><summary>Answer</summary>

   On `padded` the minimum is right 98% of the time and the mean 0%, and on `late_disqualifier` it's 83% against 1%. On `recovery` and `contradiction` neither works: the mean is at 2% and 0%, and the minimum at 0% on both. A contradiction lives between two turns, and a repair needs knowing which answer came last, so a function that sees one turn at a time has nothing to threshold. The scores show it: a repaired conversation (human PASS) has a mean of 0.58, below the failing `padded` (0.70) and `late_disqualifier` (0.71), while a contradictory one (human FAIL) scores 0.82, above ordinary rows at 0.69. The ordering is wrong for any cut. A mean threshold of .50 gets `recovery` right but drops ordinary rows from 85% to 73%, and a minimum threshold of .80 gets `contradiction` 96% right but drops ordinary rows from 79% to 42%. These rates come from the lab's seed and generated data.

   </details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| Why grade both outcome and trajectory? | They fail independently. The right answer by an unsafe path passes an outcome-only eval, and a reasonable path that failed on a tool timeout isn't the agent's fault. |
| Compare pass@k and pass^k, with numbers. | pass@k is the chance that at least one of k trials succeeds, and pass^k that all do. At p = 0.75 and k = 3 they are 0.98 and 0.42, so use pass^k for customer-facing agents where each user gets one try. |
| How would you evaluate a router-plus-skills agent? | Give each part a grader: a judge over the tool-call span for the router, per-skill checks (code execution for the visualization skill), and optimal ÷ actual steps for the path, then an end-to-end score. An end-to-end failure alone doesn't say which part broke. |
| What is convergence, and what's the catch? | Optimal steps ÷ actual steps over paraphrases of a question. "Optimal" is the shortest run observed, so a suite where every run thrashes can still score near 1.0. |
| Why does agent cost grow faster than step count? | Every turn re-sends the whole context, so a 5,000-token tool output is billed again each later turn. Thinking tokens and detours add to it, which makes turn count and context growth the levers, not only a cheaper model. |
| A simulated user gives a 0.47 reward. Do you trust it? | Not from one cooperative user. In GAUGE, a population of personas cut mean verifiable reward by 42%, from 0.47 to 0.27, and the judge needs to see tool calls and outcome, since a truncated transcript got 4.6/7 for satisfaction with reward 0. |
| A simple baseline nearly matches your agent framework on accuracy. How do you decide? | Plot accuracy against cost with simple baselines. Kapoor et al. found a warming baseline at 93.2% for $2.45 against LDB at 93.3% for $6.36, so check the gap against the error bar and log tokens so that you can re-price later. |
| Why record how each failed agent run ended? | The mix of endings varies by environment, so one failure rate hides it. AgentBench sorts runs into completed, context limit exceeded, invalid format, invalid action or task limit exceeded, which covers running out of turns or repeating itself. |
| Beyond the task set, which suites does a tool-using agent need? | An error-handling suite with malformed input, tool errors, timeouts and empty results, plus an adversarial suite with injection and out-of-scope requests. Neither failure shows up in tasks where every tool behaves. |

## Next

[07-evaluating-rag-and-grounding.md](07-evaluating-rag-and-grounding.md): when the answer has to come from the documents.
