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
  - https://assets.anthropic.com/m/785e231869ea8b3b/original/claude-3-7-sonnet-system-card.pdf
  - https://www.deeplearning.ai/short-courses/evaluating-ai-agents/
  - "Michael Albada, Building Applications with AI Agents (O'Reilly, 2025), ch. 9"
  - "Mayo Oshin & Nuno Campos, Learning LangChain (O'Reilly, 2025), ch. 10"
  - 13-case-study-support-agent.md
  - ../practice/conversation_scoring_lab.py
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

An averaged step score needs the same care. LongCLI-Bench ([arXiv:2602.14337](https://arxiv.org/abs/2602.14337) (Feng et al., 2026-02, preprint)) scores 20 long command-line tasks by the share of sub-steps passed on two test sets, one for the new requirement and one for behaviour that must not break, and counts a pass only when both reach 100%. Across 9 agent and model pairs (mean of 3 runs), **the keep-working step score was above 98% for every pair while 70.0% to 88.3% of runs kept everything working**, and the best pass rate was 16.7%. A plan injected before the run raised Claude Code with Opus 4.6 to 58.3%, about what three rounds of test feedback reached (55.0%) in a third of the time (15.4 against 43.8 minutes). The paper is labelled preliminary: 20 tasks, so one run is 1.67 points, no intervals, no formula for the step score, and the run count for the plan and feedback rows is not stated.

When the deliverable is too open for a state check, the rubric can be a tree. PaperBench ([arXiv:2504.01848](https://arxiv.org/abs/2504.01848) (Starace et al., ICML 2025; numbers from arXiv v3)) grades an agent's attempt to replicate 20 ICML 2024 papers against rubrics written with each paper's authors: 8,316 leaves in all, each a pass/fail check an expert could do in under 15 minutes, with a parent's score the weighted average of its children. Result-matching leaves are judged only from a fresh re-run of the agent's `reproduce.sh` on a clean machine, so hard-coded results earn nothing. The judge was itself graded before use ([05](05-llm-as-judge.md#decompose-hard-criteria)): on human-graded leaves from five papers, **o3-mini reached F1 0.83 at $66 a paper, against 0.84 for o1 at $830**, and it was weakest on reading code (0.72) and strongest on matching results (0.94). Granularity is part of the score. Collapsing one submission's 361 leaves to 9 raised its grade from 0.25 to 0.48, and to a single leaf, 0.93. The best agent scored 21.0% ± 0.8 (Claude 3.5 Sonnet, 12 hours, 3 runs), almost all from writing code and not from running it. On a 3-paper subset the best of three attempts by ML PhDs reached 41.4% in 48 hours against 26.6% for o1. The gold labels have no inter-rater figure, the judge was tested on human-made submissions and not on agent output, and each rubric took weeks to write.

A graded score can also sit behind a gate. Agents' Last Exam ([arXiv:2606.05405](https://arxiv.org/abs/2606.05405) (Sun et al., 2026-06, preprint; numbers from the 2026-10 revision)) scores professional deliverables, from CAD parts to audio sessions, with a per-task `evaluate()` function that compares the output files with a hidden reference directory. By the authors' static analysis, 93.2% of task workflows are graded by code and 6.8% by an LLM judge, and most scoring functions check a binary precondition first: "failure on the gate forces the task score to 0 regardless of partial progress on other criteria". Where a judge is used it answers narrow yes/no questions, and code does the weighting and aggregation. The two numbers still diverge: **on the 38 hardest public tasks, Codex with GPT-5.5 had a mean score of 11.2 and passed none**. No grader, tolerance or judge is validated against people, repeated runs (three) cover only some configurations, and only 150 of the 1,490 tasks are public.

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

For a coding agent, the component before the patch is **localization**: did it edit the right place? SWE-PolyBench ([arXiv:2504.08703](https://arxiv.org/abs/2504.08703) (Rashid et al., 2025-04, preprint)) scores it as set precision and recall of the files the agent changed against the files in the reference patch, and again at the level of the deepest class or function node each change touches. On its 2,110 tasks in four languages, with Claude 3.5 Sonnet under three adapted agents, **the agent with the best Python file retrieval (recall 60.9, precision 77.6) passed 20.1% of Python tasks, and the other two passed 24.1%, one of them at precision 44.2**. The authors call good retrieval "a necessary but not sufficient condition", but they compute no correlation, and the metric is scored against one reference patch, so a valid fix made elsewhere would score low. The pass rate also fell with the number of files to change (Aider: 17.7% for one file, 7.9% for five or more). Each configuration ran once; the ± values are bootstrap standard errors over tasks.

A human baseline does not remove the harness from the comparison. In a penetration test of a live university network of about 8,000 hosts ([arXiv:2512.09882](https://arxiv.org/abs/2512.09882) (Lin et al., 2025-12, preprint; read as the 2026-03 revision)), ten professionals and several agents were scored on the sum of a complexity score and a severity weight for each valid finding. GPT-5 outscored 5 of the 10 humans inside the authors' ARTEMIS scaffold, 2 inside Codex and none inside CyAgent. The ARTEMIS configuration that outscored 9 of the 10 (95.2 against 111.4 for the best human, 82% of submissions valid) cost $59 an hour; the $18.21-an-hour configuration is the one that beat 5, with 55% of its submissions valid. Each agent ran once, there are no intervals, and the authors scored their own agent without reporting agreement between raters.

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

The step where a run ends is a poor guide to where it went wrong. A study of 1,184 failed Terminal-Bench trajectories ([arXiv:2607.09510](https://arxiv.org/abs/2607.09510) (Zhao et al., 2026-07, preprint)), covering 89 tasks and 21 systems (3 scaffolds by 7 models), labelled the decisive error in each run, with Claude Opus 4.6 drafting the labels and two human annotators finalising them (Cohen's κ 0.83 for root causes). **The decisive error came at a median step 7 of a median 27, and the first visible sign of it at a median step 16**, in the 72% of runs that showed one; the other 28% never surfaced a sign. In 26% of failed runs the agent claimed success with fabricated evidence. Each figure is a point estimate with no interval, timeouts were excluded, the decisive error is labelled in hindsight, and both annotators started from the same model draft.

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

---

## Agent-specific suites

| Agent type | Add these to the suite |
|---|---|
| **Conversational** | Multi-turn tasks. Turn-count limits. Tone and interaction quality. Long, adversarial conversations. A simulated user ([below](#multi-turn-evaluation)) |
| **Coding** | Repo state + tests as the grader. Held-out tests the agent can't see ([04/03](../../../ai-engineering/04-loop-engineering/notes/03-the-scorekeeper.md#plus-the-fifth-hard-to-fake)). Diff scope, including a check that test files are untouched, since agents special-case tests ([12](12-failure-modes.md#goodhart-the-eval-becomes-the-target)) |
| **Research** | Citation validity, coverage of required facts, source quality ([07](07-evaluating-rag-and-grounding.md)) |
| **Computer use** | End-state checks on the environment. Sandboxed, reset per trial |
| **Any tool-using agent** | Error-handling suite: malformed input, tool errors, timeouts, empty results. Adversarial suite: injection, out-of-scope requests ([case study](13-case-study-support-agent.md#adversarial-cases)) |

### Multi-turn evaluation

Two approaches, each with a trade-off:

- **Canned conversations.** Score each turn against a fixed, scripted history. Isolates turns and is reproducible, but misses compounding errors, because the history never reflects what the agent actually said.
- **Simulated user.** An LLM plays the user with a goal and persona, and the conversation runs to the end. Tests the real thing end to end, but inherits the simulator's biases and adds variance. Give the simulator a clear goal and stop condition, and calibrate it: does it behave like your real users?

A single cooperative simulated user flatters the agent. In GAUGE (Bodhwani et al., τ²-bench retail, 12 agent variants), swapping the default τ² user for a population of personas (anxious, skeptical and others) **cut mean verifiable reward by 42%** (0.47 → 0.27). Whoever grades the conversation also has to see the tool calls and the outcome. A transcript truncated mid-task scored reward 0, yet human raters gave it 4.6/7 for satisfaction. A judge that saw the tool calls and the goal tracked task success, and a judge rating "how the conversation felt" did not ([15](15-calibration-against-human-labels.md#the-procedure)). A free check catches the crude case: did the conversation finish at all? That signal tracked reward at ρ 0.87 when variants were deliberately broken. But only 3.5% of real failures were truncations, so semantic failures still need the judge ([arXiv:2609.12191](https://arxiv.org/abs/2609.12191) (Bodhwani et al., 2026-09)).

**Progressive information disclosure** is what makes a simulated user realistic. Real users don't state everything up front ("There's a problem with my flight." → "Which one?" → "It's too long, I want to change it." → "Any afternoon flight is fine."). τ-bench gives the simulator two parts: *known information* and *instructions* for when to reveal it. The agent has to ask. A simulator that dumps all the facts in turn 1 tests a much easier task. Hold the script fixed so runs stay reproducible.

**τ²-bench** (the successor) adds a **dual-control environment**: the simulated user can also call tools on the shared state. The agent says "switch to airplane mode", and the user's action really changes the environment. This fits tech support, where the user has to do part of the work, and tests whether the agent notices state changes it didn't make. It also tightened success conditions ("only an *excellent* speed rating counts") and generates task parameters fresh each run.

**Sessions, not only turns.** An agent with memory has to be tested on work where a later session depends on an earlier one. Recall benchmarks such as LoCoMo and LongMemEval ask one question about a fixed history, with no actions and no feedback from an environment. MemoryArena ([arXiv:2602.16313](https://arxiv.org/abs/2602.16313) (He et al., ICML 2026)) chains 701 tasks into an average of 6.9 dependent subtasks each: session 2 asks for a lens that fits the camera bought in session 1, and the instruction is underspecified without that state. Across 13 setups (long context on four models, plus five memory systems and four RAG systems on GPT-5-mini), **the share of shopping subtasks passed averaged 0.52 while the share of whole tasks solved averaged 0.02**. On GPT-5-mini, long context averaged 0.16 success over the five domains; the memory systems scored lower (0.12–0.14) and RAG only slightly higher (0.17–0.20). In group travel the long-context pass rate, conditional on the earlier constraints being met, fell from 0.48 at dependency distance L0 to 0.15 at L4, with the whole history in context. The paper says systems that saturate recall benchmarks do poorly here, but it reports no recall scores for the same systems, so that gap is asserted, not measured. It has no repeated runs or intervals, physics has 20 tasks, and it does not say how a search or proof answer is judged correct.

Check who wrote a multi-session benchmark before trusting its ranking. OdysseyBench ([arXiv:2508.09124](https://arxiv.org/abs/2508.09124) (Wang et al., 2025-08, preprint)) scatters the instructions for an office task over several days of dialogue and grades only the final file system, with exact-match, fuzzy-match and execution checks that must all pass. On its 300 tasks adapted from OfficeBench, o3 fell from 72.83% on one-app tasks to 30.36% on three-app tasks. But GPT-4.1 wrote the dialogues, and for the 302 synthesized tasks also the tasks and their pass criteria, and o3 solving a task was a filter for keeping it. Both models are then scored on the result. The assistant in the dialogue history never acts, so the history holds instructions and chitchat and no earlier work, unlike MemoryArena. Nothing is run twice, and two of the paper's retrieval tables contradict themselves, so its comparison of long context against RAG is not used here.

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
