---
origin: synthesis
sources:
  - https://www.promptingguide.ai/techniques/ape
  - https://www.promptingguide.ai/techniques/meta_prompting
  - "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly 2024) — Ch 4, Ch 5, Ch 6, Ch 9"
  - "Huyen, AI Engineering (O'Reilly, 2025), ch. 5"
  - https://arxiv.org/abs/2309.03409
  - https://arxiv.org/abs/2406.07496
  - https://arxiv.org/abs/2507.19457
  - https://arxiv.org/abs/2509.10414
confidence: medium
cleaned: 2026-11-01
---
# 8 — Prompt Optimization

> Treating the prompt as an artifact you can search over, version and regression-test, and letting models do part of the writing. Everything here assumes you have an eval ([09](09-evaluating-prompts.md)). An optimizer without a metric is just a rewriter.

Tuning a prompt by feel stops working once a one-word edit can move your scores and nobody remembers which version shipped. Without versions and a metric, you re-try ideas that already failed and can't tell a real gain from noise. This chapter treats the prompt as an artifact you can search over, version and regression-test.

---

## The loop

```mermaid
flowchart LR
    T["Template vN"] --> R["Run on eval set"] --> S["Score"] --> P["Propose changes<br/>you · APE/OPRO · DSPy"]
    P --> T2["Template vN+1"]
    T2 -->|"keep only if it beats vN"| R
```

The proposer can be you, an LLM (APE, OPRO, meta-prompting), or a framework (DSPy, TextGrad, GEPA). The parts that matter are the same in every case: **a fixed eval set, a metric, and a record of every version.**

---

## Prompts as versioned artifacts

- **Template ≠ prompt.** Version the template (static instructions plus slots), not the rendered string ([02](02-prompt-anatomy.md#prompt-templates)).
- **Store it like code**: in the repo or a prompt registry, with an ID, a version, the model it was tuned on, and its eval score.
- **Pin the model version** next to the prompt. A prompt tuned on one model is not portable. Re-run the evals when either changes.
- **Diff behavior, not text.** A one-word change can move the scores; run the regression suite on every edit.
- **Log production I/O per prompt version** — it's your next eval set and the training data for optimizers ([06](06-chaining-and-workflows.md#operating-a-workflow)).

**Keep prompts out of application code.** Put them in their own module or file. That way they can be reused across apps, tested separately from the code, and edited by domain experts who don't read Python. When there are many prompts, wrap each one in a record that carries its metadata (*AI Engineering*, ch. 5):

```python
class Prompt(BaseModel):
    prompt_text: str
    model_name: str            # the model it was tuned on
    application: str
    creator: str
    date_created: datetime
    sampling: dict = {}        # temperature, top_p
    output_schema: dict | None = None
```

File formats such as Firebase's [Dotprompt](https://firebase.google.com/docs/genkit/dotprompt) put the model, input schema and output schema in YAML front matter above the template. **Git or a catalog?** Versioning prompts in the same repo as the code is simple, but when apps share a prompt, an edit forces every consumer onto the new version together. A separate **prompt catalog** versions each prompt on its own, so one team can stay pinned to v3 while another moves to v4. A good catalog also records which apps depend on each prompt and tells their owners when a new version lands.

---

## APE — automatic prompt engineer

Zhou et al. (2022) framed instruction-writing as black-box search:

1. An LLM sees input/output demonstrations and **generates candidate instructions**.
2. Each candidate is run on a **target model** and scored.
3. Keep the best, optionally resample variants of it, and repeat.

![APE pipeline](../sources/images/zhou-ape-overview.png)
*Propose instructions from demonstrations, score each by the log-probability of the correct outputs, and resample near the winners. Zhou et al. (2022), via DAIR.*

The famous result: APE found a better zero-shot CoT trigger than *"Let's think step by step"*. **"Let's work this out in a step by step way to be sure we have the right answer"** improved MultiArith and GSM8K. On MultiArith it scored 82.0 against 78.7 for the human-written trigger. The table also shows how much the wording alone moves the score: human-written triggers range from 45.7 to 78.7, and no trigger at all gets 17.7:

![Zero-shot CoT triggers: APE's discovered prompt vs. human-designed ones](../sources/images/zhou-ape-zero-shot-cot-triggers.png)
*Image Source: Zhou et al. (2022), via DAIR*

Related work, in the same spirit:
- **OPRO** (2023) — the LLM is the optimizer, shown past prompts and their scores in its context. Found *"Take a deep breath and work on this problem step-by-step."*, which scored 80.2% on GSM8K with PaLM 2-L against 71.8% for "Let's think step by step". Across scorer models the best optimized prompts beat human-written ones by up to 8 points on GSM8K and up to 50 on Big-Bench Hard tasks ([arXiv:2309.03409](https://arxiv.org/abs/2309.03409), Yang et al., ICLR 2024). Each scorer model converged on a different best prompt, so re-run the search when you change models.
- **Prompt-OIRL** — offline inverse RL to choose query-dependent prompts.
- **AutoPrompt**, **prefix tuning**, **prompt tuning** — gradient-based search over discrete tokens or continuous "soft prompts." These need model access, and are closer to fine-tuning ([04](04-controlling-output.md#when-prompting-isnt-enough-fine-tuning)).

The lesson is not the magic phrases, which are model-specific and dated, but that **search against a metric beats intuition** once you have one.

---

## Meta-prompting

The term is used in two senses.

**1. Structure-oriented prompting** (Zhang et al., 2024). Give the model an abstract *template* for solving a class of problems rather than worked content examples:

```
Problem: [question]
Solution structure:
  1. Identify the given quantities and what is asked.
  2. State the relevant formula or principle.
  3. Substitute and compute step by step.
  4. Final answer: \boxed{[answer]}
```

![Structure meta-prompt for MATH](../sources/images/zhang-meta-prompting-math-structure.png)
*Top: the structure meta-prompt. Bottom: example solutions that follow it. Zhang et al. (2024), via DAIR.*

Compared with few-shot it's token-efficient, avoids anchoring on specific example content ([03](03-core-techniques.md#few-shot)), and behaves like zero-shot. It assumes the model already knows the domain, so it degrades on genuinely novel tasks.

**2. Using a model to write prompts.** This is the common sense of the term in practice:
- Ask a strong (often reasoning) model to draft a system prompt from a task description, or to **critique and rewrite** an existing one given failing cases.
- Vendor tools do this: Anthropic's prompt generator and prompt improver, and OpenAI's playground optimizer.
- The **evaluator–optimizer** pattern automates it: a judge scores outputs, writes feedback, and a meta-prompt turns that feedback into a revised prompt ([06](06-chaining-and-workflows.md#workflow-patterns-anthropics-taxonomy), [07](07-prompting-reasoning-models.md#where-reasoning-models-earn-their-cost)).

![Evaluator-optimizer prompt loop](../sources/images/dair-evaluator-optimizer-prompt-loop.jpg)
*Each round, the judge's feedback goes to a meta-prompt that rewrites the system prompt, and the best version is logged. DAIR, Reasoning LLMs Guide.*

Generated prompts are a **first draft, not a result** — they still have to win on your eval.

---

## DSPy and programmatic optimization

**DSPy** replaces hand-written prompts with *signatures* (`question -> answer`) and *modules* (`ChainOfThought`, `ReAct`). An **optimizer** (teleprompter) then compiles the program against a metric and a training set:

- **Few-shot selection** — bootstraps demonstrations from successful runs and picks which examples to include, and in what order. This directly addresses the book's few-shot drawbacks: anchoring and spurious order patterns ([03](03-core-techniques.md#few-shot)).
- **Instruction optimization** — proposes and searches over instruction wordings (MIPRO-style).
- **Fine-tuning** — can distill the compiled program into weights.

**TextGrad** does a similar job with "textual gradients": LLM-written critiques propagated back through a pipeline to revise each component's prompt. Optimizing a system prompt for gpt-3.5-turbo, with GPT-4o writing the critiques on 36 training examples, lifted GSM8K from 72.9% to 81.1% with instructions alone, matching DSPy's 8-shot bootstrapped prompt; its headline GPQA gain for GPT-4o (51% to 55%) came from refining each answer at test time, not from a better prompt ([arXiv:2406.07496](https://arxiv.org/abs/2406.07496), Yuksekgonul et al., Nature 2025). **Promptbreeder** (Fernando et al., DeepMind, 2023) treats the search as evolution. An LLM mutates a seed prompt, guided by a set of *mutator prompts*, and the best mutants are mutated again until one meets the target.

**GEPA** combines the two ideas. It runs the pipeline, has an LLM read the full traces (reasoning, tool calls, tool outputs, evaluator feedback) and diagnose what went wrong, and then rewrites one module's prompt. Instead of keeping only the single best prompt, it keeps every candidate that is best on at least one training example (a Pareto front) and mutates from those. On six benchmarks (multi-hop QA, instruction following, privacy-aware delegation, retrieval-augmented claim verification and two math sets) with Qwen3 8B, GEPA improved the average over the unoptimized baseline by 9.62 points. GRPO fine-tuning with 24,000 rollouts improved it by 3.68, and MIPROv2 by 2.61. GEPA beat GRPO on every benchmark except AIME. In the authors' summary, "GEPA outperforms GRPO by 6% on average and by up to 20%, while using up to 35x fewer rollouts." With GPT-4.1 Mini, it gained 12.19 points against 5.64 for MIPROv2 and 6.11 for TextGrad. Two details matter in practice. Choosing candidates from the Pareto front gained 12.44 points where always mutating the current best gained 6.05. GEPA's prompts were also up to 9.2× shorter than MIPROv2's, because it writes instructions rather than piling in few-shot examples ([arXiv:2507.19457](https://arxiv.org/abs/2507.19457) (Agrawal et al., ICLR 2026)). The method needs a metric that can also return text feedback, such as which constraint failed or which document was missing, and not only a score.

Use these when you have a multi-step pipeline, a scorable metric, and dozens to hundreds of labeled examples. Skip them for one-off prompts or tasks you can't score automatically.

Optimized prompts can still overfit their eval set. de Wynter found an APO-optimized prompt lost accuracy as test inputs moved away from the training distribution: the slope was −0.5, against −0.4 for a plain prompt and −1.4 for CoT, on nine synthetic formal-language tasks ([arXiv:2509.10414](https://arxiv.org/abs/2509.10414) (de Wynter, 2025-09)). Hold out test cases that differ from the ones the optimizer saw.

### Before trusting a prompt tool

Huyen's three warnings (*AI Engineering*, ch. 5):

- **Hidden API calls.** Ten variants scored on 30 eval examples is already 300 calls. If each one also needs a validation call ("is this valid JSON?") and a scoring call, that's 900. A tool allowed to design its own chains can grow the bill without limit. Count the calls before you run it.
- **Tool bugs.** The tool might use the wrong chat template ([01](01-how-models-read-prompts.md#property-5--chat-models-are-completion-models-wearing-a-transcript)), concatenate tokens instead of text, or ship typos in its default prompts. LangChain's default critique prompt had several typos. Tools also change their defaults without warning.
- **Show me the prompt.** Write the first version by hand, so you learn the model and your requirements. Then read every prompt a tool generates before you trust it (Husain, [*Fuck You, Show Me the Prompt*](https://hamel.dev/blog/posts/prompt/), 2024).

---

## A manual optimization checklist

Before reaching for a framework:

1. **Find the failure category** in the eval results — format, missing context, wrong reasoning, instruction ignored.
2. **Fix the cheapest layer first**: clarity of the instruction ([02](02-prompt-anatomy.md#writing-instructions)) → missing context → ordering → examples → CoT → splitting the task ([06](06-chaining-and-workflows.md)) → a stronger model → fine-tuning. Ordering includes the assembly's knobs: the priority tiers, scores and elastic versions that decide which snippets make the cut are parameters to tune against the eval like any wording (book, Ch 6; [02](02-prompt-anatomy.md#formatting-injected-content)). A stronger model costs money and latency. When the book was written, GPT-4 could cost 20 times as much as gpt-3.5-turbo, and early Copilot chose the small, fast Codex model because users would not wait for a bigger one (book, Ch 4).
3. **Change one thing at a time** and re-score.
4. **Keep the losers.** Recording what didn't work stops you re-trying it.

---

## Go deeper

- Papers (APE, OPRO, meta-prompting, DSPy, TextGrad, soft prompts): [references.md](../README.md#prompt-optimization)
- Book: [Ch 9 PDF](../sources/prompt-eng-for-llms/reading/09-llm-workflows.pdf) (collecting task I/O for optimization)

---

## Pitfalls

- **Running an optimizer with no real metric.** Symptom: prompts that change every run and scores that don't improve, because an optimizer without a metric is just a rewriter. Fix: fix the eval set and metric first, and keep only versions that beat the current one.
- **Copying a magic phrase.** Symptom: "Take a deep breath" gives no lift on your model. OPRO's scorers each converged on a different best prompt. Fix: copy the search, not the string, and re-run it when the model changes.
- **Overfitting the eval set.** Symptom: scores rise offline and production doesn't move. de Wynter measured accuracy falling as test inputs moved away from training, for optimized prompts too. Fix: hold out test cases that differ from what the optimizer saw.
- **Counting prompts instead of API calls.** Symptom: a surprising bill. Huyen's 10 variants on 30 examples is 300 calls, or 900 with a validation and a scoring call each. Fix: count before you run, and cap what a tool may chain.
- **Trusting a tool's default prompts.** Symptom: quality that shifts between versions or is oddly low, from a wrong chat template or a typo (LangChain's default critique prompt had several). Fix: write the first version by hand, then read every prompt a tool generates.
- **A score-only metric for GEPA.** Symptom: the reflection step has nothing to diagnose. Fix: return text feedback as well, such as which constraint failed or which document was missing.
- **One shared prompt across apps in a single repo.** Symptom: an edit forces every consumer onto the new version together. Fix: use a catalog that versions each prompt, so one team can stay on v3 while another moves to v4.

## Try it

1. A tool scores 5 prompt variants on 50 examples, with one validation call and one scoring call per output. How many API calls is that? Which tool setting would most worry you?
   <details><summary>Answer</summary>5 x 50 x 3 = 750 calls. The worry is any setting letting the tool design its own chains, because that removes the upper bound on calls. Cap it and count before running.</details>
2. Use the [prompt eval harness](../practice/prompt-eval-harness/README.md) to run two prompt versions on its cases, and write the record you would store for the winner. What fields does the record need beyond the text?
   <details><summary>Answer</summary>Those in the note's `Prompt` model: the model it was tuned on (pinned), application, creator, date and sampling parameters, plus the output schema, an ID and version, and its eval score. Keep the loser too, so nobody re-tries it.</details>
3. A classifier's eval shows most failures are "instruction ignored". You could add few-shot examples, split the task, or buy a stronger model. Using the checklist, what's your order, and what do you change at once?
   <details><summary>Answer</summary>Clarity of the instruction first, then missing context, ordering, examples, CoT, splitting, a stronger model and fine-tuning. Change one thing at a time and re-score, because that is the only way to attribute a gain.</details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| How does APE work? | An LLM generates candidate instructions from demonstrations, each is scored on a target model, and the best are kept and resampled. It found a trigger scoring 82.0 on MultiArith against 78.7 for "Let's think step by step". |
| What's the lasting lesson of OPRO's "Take a deep breath"? | Not the phrase, which is model-specific: 80.2% against 71.8% on GSM8K with PaLM 2-L, with a different winner per scorer. Search against a metric beats intuition once you have one. |
| What are the two meanings of meta-prompting? | Structure-oriented templates for a class of problems (Zhang et al.), and using a model to write or critique prompts. Generated prompts are a first draft that must still win on your eval. |
| How does GEPA differ from keeping the best prompt? | An LLM reads full traces to diagnose failures, and it keeps a Pareto front of candidates best on at least one example. The front gained 12.44 points where mutating the current best gained 6.05. |
| When is DSPy worth it? | With a multi-step pipeline, a scorable metric, and dozens to hundreds of labeled examples. Skip it for one-off prompts or tasks you can't score automatically. |
| Prompts in git or a catalog? | Same-repo git is simple, but moves all consumers together. A catalog versions each prompt on its own and can tell owners when a new version lands, which pays off when apps share prompts. |
| Your team wants a stronger model because quality is short. What do you check first? | The cheaper layers: instruction clarity, context, ordering, examples, CoT, splitting. A stronger model costs money and latency, which is why early Copilot chose the small, fast Codex. |

## Next

[Evaluating prompts](09-evaluating-prompts.md): every method here depends on the metric, so that comes next.
