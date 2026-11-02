---
origin: synthesis
sources:
  - https://arxiv.org/abs/2506.12115
  - https://github.com/davidkimai/Context-Engineering (00_foundations/05_cognitive_tools.md, 07_prompt_programming.md, cognitive-tools/cognitive-templates/, cognitive-tools/cognitive-programs/, cognitive-tools/cognitive_patterns.md — snapshot 2026-08-14)
confidence: medium
cleaned: 2026-11-01
---
# 8 — Cognitive Tools and Prompt Programs

> A cognitive tool is a reasoning step packaged like a function: a named prompt with inputs and outputs that the model, or your code, can call. It brings the reusability of code to the way context is structured for reasoning.

---

## The evidence: Ebouky et al. (IBM Research Zurich, 2025)

*Eliciting Reasoning in Language Models with Cognitive Tools* tests the idea directly. Four tools, each a separate prompt the model can call like a tool:

| Tool | What it does |
|---|---|
| `understand_question` | Break the problem down: identify the core concepts, the givens, the goal and relevant techniques |
| `recall_related` | Retrieve analogous solved problems and their solution steps |
| `examine_answer` | Check the current reasoning trace for errors, unmet constraints and miscalculations |
| `backtracking` | When stuck, find where the reasoning went wrong and propose an alternative path |

The key design choice is that **each tool runs in its own context**. The tool call goes out with only what that step needs, and only the result comes back into the main trace. That is context isolation ([10](10-tools-and-multi-agent.md)) applied to reasoning.

![Cognitive prompting puts all operations in one prompt; cognitive tools run each operation as a separate call with its own prompt](../sources/images/ebouky-cognitive-tools-fig1.png)
*Image Source: Ebouky et al. (2025)*

Panel A is *cognitive prompting*: every operation is listed in one prompt and runs in one trace. Panel B is *cognitive tools*: each operation is a tool call with its own prompt, and only its output returns to the main trace.

Result: GPT-4.1 on AIME 2024 rises from **32.0% to 53.0%** pass@1, past o1-preview's 44.6%. No training is involved, only structured prompting. The comparison that matters most for context engineering is the middle condition. The same four operations listed in one prompt (cognitive prompting) reached **42.0%**. **Isolating each operation in its own call is worth another 11 points** over just naming the operations.

Open-weight models gain too, but the gain grows with model size. Qwen2.5-32B on AIME went from 17.2% to 32.1% and Llama3.3-70B from 13.1% to 29.8%. Qwen2.5-7B (12.5% → 14.6%) and Llama3.1-8B (5.8% → 8.8%) barely moved. Those numbers are averaged over at least 8 runs ([arXiv:2506.12115](https://arxiv.org/abs/2506.12115) (Ebouky et al., 2025-06)).

Two caveats. The tool prompts were hand-written and tuned to the models tested; the authors warn they may not transfer to other model families without more prompt work. And these gains are on maths benchmarks with non-reasoning models. On reasoning models (o-series, extended thinking) the model already runs something like this loop internally, so explicit scaffolding adds less and can get in the way ([prompting reasoning models](../../01-prompt-engineering/notes/07-prompting-reasoning-models.md)).

---

## The four families of templates

The upstream library sorts cognitive templates by the job they do. The families are more useful than any individual template:

| Family | Templates | Use before / after |
|---|---|---|
| **Understanding** | Question analysis, information extraction, structure analysis | *Before* solving: make sure the task is understood |
| **Reasoning** | Step-by-step, compare-and-contrast, causal analysis, hypothesis testing, decision matrix, argument construction | *During*: impose a method on the work |
| **Verification** | Solution check, fact check, consistency check, error analysis, alternative perspective | *After*: catch errors before they ship |
| **Composition** | Sequential, conditional, iterative chains of the above | Orchestrating several tools |

### An understanding template

```markdown
Task: Analyse the following question before answering it.

Question: {{question}}

Provide:
1. Question type (factual, conceptual, analytical…)
2. Core task: what specific thinking is required?
3. Key components to address
4. Implicit assumptions
5. Constraints, stated or implied
6. Restatement in your own words

Then stop. Do not answer yet.
```

The final line matters. Separating understanding from answering is the point. A template that analyses and answers in one pass collapses back into ordinary chain-of-thought.

### A verification template

```markdown
Problem: {{problem}}
Proposed solution: {{solution}}

Verify:
1. Does the solution address what was asked?
2. Check each step. Mark any error with the step number.
3. Are all constraints satisfied?
4. Test against one edge case.

Verdict: CORRECT | ERRORS_FOUND
If ERRORS_FOUND, list each error and the fix.
```

The machine-readable verdict line is what lets code drive a loop.

---

## The self-correction loop

```
solve → verify ─┬─ CORRECT ───────────────► done
                └─ ERRORS_FOUND → correct → verify (max N iterations)
```

```python
def self_correct(problem, max_iter=3):
    solution = llm(f"Solve: {problem}")
    for _ in range(max_iter):
        check = llm(VERIFY.format(problem=problem, solution=solution))
        if "Verdict: CORRECT" in check:
            break
        solution = llm(f"Problem: {problem}\nSolution: {solution}\nErrors: {check}\nRevise.")
    return solution
```

Bound the loop. Verification by the same model shares its blind spots, so loops beyond 2–3 iterations rarely help, and the model can "fix" a correct answer into a wrong one. Where a ground-truth check exists (tests, a calculator, a schema validator), use it instead of a model verifier. See [03-harness — verification loops](../../03-harness-engineering/notes/05-verification-loops.md) and [04-loop — layered exits](../../04-loop-engineering/notes/09-failure-modes-and-guardrails.md#layered-exits).

Why a separate verifier matters more than more rounds can be shown with a small model. Each round produces a correct draft with probability 0.5. A verifier always passes a right draft, and wrongly passes a wrong draft with probability `blind`. A self-grading model shares its own blind spots, which puts it at the high end of `blind`. The values here are assumptions chosen to show the shape, not measurements.

```python
# Same model, same verifier budget: how a self-grading loop differs from a real check.
# Each round a draft is correct with probability p. The verifier passes correct drafts,
# and it wrongly passes a wrong draft with probability blind (the shared blind spot).
def final_accuracy(p, blind, rounds):
    right, wrong_open, done_wrong = p, 1 - p, 0.0
    for _ in range(rounds):
        done_wrong += wrong_open * blind             # wrong draft approved: the loop stops
        wrong_open *= 1 - blind                      # wrong draft caught: revise
        right += wrong_open * p                      # the revision may be right
        wrong_open *= 1 - p
    return right, done_wrong + wrong_open

for blind in (0.0, 0.5, 0.9):
    row = [f"{final_accuracy(0.5, blind, r)[0]:.3f}" for r in (0, 1, 2, 3, 5)]
    print(f"blind={blind}: rounds 0,1,2,3,5 -> {row}")
```

Output:

```text
blind=0.0: rounds 0,1,2,3,5 -> ['0.500', '0.750', '0.875', '0.938', '0.984']
blind=0.5: rounds 0,1,2,3,5 -> ['0.500', '0.625', '0.656', '0.664', '0.667']
blind=0.9: rounds 0,1,2,3,5 -> ['0.500', '0.525', '0.526', '0.526', '0.526']
```

With a perfect check, each round closes half the remaining gap, and most of the gain has arrived by round 2 or 3, which is the case for the bound above. At `blind=0.9`, a loop gets almost nothing at any bound, because it stops at the first draft it approves. A deterministic check such as `python_validator` moves you towards `blind=0`, whereas a self-graded 0.8 score doesn't.

The swap is small. Here the verifier is Python's own compiler, from the upstream course's `03_control_loops.py`:

````python
import re

def python_validator(response):
    blocks = re.findall(r"```python(.*?)```", response, re.DOTALL)
    if not blocks:
        return False, "No Python code block found."
    for i, block in enumerate(blocks, 1):
        try:
            compile(block, "<llm>", "exec")       # syntax only; tests would check behaviour
        except SyntaxError as e:
            return False, f"Syntax error in block {i}: {e}"
    return True, "ok"

def generate_checked(task, validate=python_validator, max_attempts=3):
    prompt = task
    for _ in range(max_attempts):
        out = llm(prompt)
        ok, feedback = validate(out)
        if ok:
            return out
        prompt = f"{task}\n\nYour previous answer:\n{out}\n\nProblem: {feedback}\nFix it."
    raise ValueError(f"still failing after {max_attempts} attempts: {feedback}")
````

The opposite design is a weak one. The upstream `07_recursive_patterns.py` stops its self-reflection loop when the model's *own* quality score (parsed by regex, default 0.5) clears 0.8. A self-graded stop condition inherits the blind spots the loop was meant to catch, so treat it as a demo, not a pattern.

---

## Prompt programs

A prompt program applies programming structure to a prompt: **named operations with parameters, composed with control flow.**

```
function analyze_tradeoffs(options, criteria, weight_by="impact") {
  1. For each option, score it against each criterion (1–5) with one-line justification.
  2. Weight scores by {weight_by}.
  3. Rank options; flag any criterion where the top option scores ≤ 2.
  return: ranked table + recommendation + flagged risks
}

analyze_tradeoffs(
  options=["Postgres", "DynamoDB", "SQLite"],
  criteria=["ops burden", "query flexibility", "cost at 10k rps"]
)
```

Why this works when it does:

- **Explicit steps** turn an open-ended request into a procedure the model follows.
- **Parameters** make the same program reusable: swap the options, keep the method.
- **A declared return** fixes the output shape.

Programs compose: `understand → analyze_tradeoffs → verify`. They can branch ("if fewer than two options survive step 3, expand the search") and loop (refine until the verifier passes).

In code, a program is a list of operations plus shared state that later templates can read. This is the shape of the upstream `05_prompt_programs.py` `MultiStepProgram`:

```python
program = [
    {"name": "reason",  "system": "You are a careful analyst.",
     "template": "Solve step by step:\n{problem}"},
    {"name": "verify",  "system": "You are a critical reviewer.",
     "template": "Problem: {problem}\nSolution:\n{reason}\nList any errors, or say NONE."},
    {"name": "correct", "system": "You are a careful analyst.",
     "template": "Problem: {problem}\nDraft:\n{reason}\nReview:\n{verify}\nGive the final answer."},
]

def run(program, **inputs):
    state = dict(inputs)
    for op in program:
        state[op["name"]] = llm(op["template"].format(**state), system=op["system"])
    return state                       # every intermediate output, for audit
```

Because the steps are data, you can log, diff and eval each one, and reorder or drop steps without touching the runner.

### Cognitive tools vs. prompt programs

| | Cognitive tool | Prompt program |
|---|---|---|
| Unit | One reasoning operation | A procedure of several steps |
| Who calls it | The model, as a tool, when it decides it needs it | Your code, or the prompt itself |
| Context | Ideally isolated per call | Usually one window |
| Strength | Model chooses *when* to think harder | Repeatable, auditable method |

The IBM result favours the tool version. The best results came when **the model chose which tool to call and when**, not from a fixed sequence.

---

## When to reach for this

- **Yes:** multi-step reasoning on non-reasoning models; tasks where a check is cheap and errors are expensive; procedures you run repeatedly and want to audit.
- **No:** simple lookups (the scaffolding costs more than it buys); reasoning models on tasks they already handle; anywhere a deterministic check (code, tests, a parser) can replace a model judgment.

---

## Upstream library (what was condensed here)

The upstream `cognitive-tools/` held about 100k words: the template families above, a program library (basic and advanced programs), domain schemas ([07](07-structured-context.md)) and "architectures" that compose tools into solver, tutor and research agents ([13](13-putting-it-together.md)). The upstream repo keeps copyable versions of the core templates (chain of thought, few-shot, minimal context, verification loop) and a `prompt_program_template.py`: [davidkimai/Context-Engineering](https://github.com/davidkimai/Context-Engineering/tree/main/20_templates).

---

## Pitfalls

- **Copying a cognitive tool without its stopping rule.** Symptom: the model keeps calling tools or re-deriving. Ebouky et al.'s templates end with an explicit "Then stop". Fix: keep the stop line and a verdict line in every template.
- **Generalizing one model's gain.** Symptom: expecting +21 points everywhere because GPT-4.1 rose from 32.0 to 53.0 on AIME 2024. Llama3.1-8B moved only from 5.8 to 8.8. Fix: measure on the model you ship.
- **Forcing the sequence.** Symptom: rigid cognitive prompting underperforms. In Ebouky et al., it scored 42.0, where tools the model chose when to use reached 53.0. Fix: offer the tools, and let the model choose when to use them.
- **Trusting a self-graded stop.** Symptom: the loop stops at a confident 0.8 on wrong work, as the `blind=0.9` row shows. Fix: use a deterministic check where one exists, such as `python_validator`'s `compile` step.
- **Unbounded self-correction.** Symptom: rounds pile up, and each adds to the window with little gain. Fix: bound the loop to 2-3 rounds and return the best draft with its verdict.
- **Reaching for a framework first.** Symptom: a prompt program for a task that one good instruction solves. Fix: use the checks in the "When to reach for this" section, and prefer a single tool until an eval says otherwise.

## Try it

1. Use the worked model to find how many rounds a `blind=0.0` loop needs to pass 0.95 when `p=0.5`, and what happens with `blind=0.5`.

   <details><summary>Answer</summary>

   With `blind=0.0`, 5 rounds reach 0.984 and 3 rounds reach 0.938, so four rounds (1 − 0.5⁵ = 0.969) are the first to pass 0.95. With `blind=0.5`, it plateaus at about 0.667 and never gets there, so more rounds won't fix a weak verifier.

   </details>

2. Write a cognitive tool for reading a failing stack trace, in the template's shape: a name, inputs, numbered steps, a verdict line and "Then stop."

   <details><summary>Answer</summary>

   ```text
   Tool: triage_stack_trace
   Input: {trace}, {changed_files}
   1. Name the innermost frame in code you own.
   2. State the exception and the value that caused it.
   3. Say whether a file in {changed_files} appears in the trace.
   Verdict: CAUSE_IN_CHANGE | CAUSE_ELSEWHERE | UNKNOWN
   Then stop.
   ```

   The verdict line gives the calling code something to branch on, and "Then stop" keeps the model from drifting into a fix.

   </details>

3. Which is a better fit for a tool, and which for a program: a) a model working through unfamiliar maths problems, b) an extract, validate, then file workflow that always runs in the same order?

   <details><summary>Answer</summary>

   a) Tools, since the model benefits from choosing when to call them. b) A prompt program, since the order is known and your code should own it.

   </details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| What's a cognitive tool? | A reasoning step packaged like a function: a named prompt with inputs and outputs that the model or your code can call, and which adds no external capability. |
| What's the evidence for them? | Ebouky et al.: GPT-4.1 on AIME 2024 went from 32.0 to 53.0 with tools, against 42.0 for cognitive prompting and 44.6 for o1-preview. |
| Do they help every model equally? | No. Qwen2.5-32B went from 17.2 to 32.1 and Llama3.3-70B from 13.1 to 29.8, but Qwen2.5-7B only from 12.5 to 14.6 and Llama3.1-8B from 5.8 to 8.8. |
| Should a tool call or a fixed order drive the reasoning? | Let the model choose when the problem varies, since that freedom accounts for the +11 over forced cognitive prompting. Use a program with a fixed order when the workflow is known. |
| Your self-correction loop stops at a self-score of 0.8 and quality is flat. Why? | The verifier shares the writer's blind spots. In a simple model with `blind=0.9`, accuracy stays near 0.526 at any bound, so replace the self-score with a deterministic check. |
| How many correction rounds do you allow? | 2-3. In the worked model with a perfect check, 3 rounds reach 0.938 from 0.5, and further rounds add little while each one adds to the window. |

## Next

[09-protocols.md](09-protocols.md): the same ideas, written for people who don't write code.
