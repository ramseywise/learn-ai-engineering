---
origin: synthesis
sources:
  - https://arxiv.org/abs/2306.05685
  - https://arxiv.org/abs/2303.16634
  - https://arxiv.org/abs/2412.05579
  - https://arxiv.org/abs/2507.08794
  - https://arxiv.org/abs/2606.19544
  - https://arxiv.org/abs/2505.08775
  - https://arxiv.org/abs/2304.05376
  - https://arxiv.org/abs/2302.14520
  - https://arxiv.org/abs/2302.04166
  - https://arxiv.org/abs/2207.05221
  - "Bojie Li, AI Agents in Depth (2026), ch. 7 — https://github.com/bojieli/ai-agent-book"
  - "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly 2024) — Ch 10"
  - "Huyen, AI Engineering (O'Reilly, 2025), ch. 3, 4"
  - "Mayo Oshin & Nuno Campos, Learning LangChain (O'Reilly, 2025), ch. 10"
  - "Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024), ch. 7"
confidence: high
cleaned: 2026-11-01
---
# 5 — LLM as Judge

> A judge is a model making a measurement. Until you've checked it against human labels, you don't know what it measures. Write a narrow rubric, mitigate the known biases, and calibrate before you gate on it.

A judge is the tool for qualities no code check can express, and it is easy to get wrong: one that checks "quality" silently switches criteria from row to row, and every shape of judge carries biases that have been measured. This chapter covers when to use a judge, how to write its prompt, which biases to test for, and how to turn pairwise votes into a ranking. [Note 15](15-calibration-against-human-labels.md) then compares the judge with human labels, which is what gives its number a meaning.

---

## When a judge is the right tool

Use a judge when the quality is semantic (is this complete? is it grounded? is the tone right?) and no code check can express it ([04](04-graders.md#code-graders-more-than-you-think)). Don't use one for things code can check. A judge that decides whether JSON is valid is slower, costlier and less reliable than `json.loads`.

### Three judge shapes

| Shape | Asks | Good for | Watch out for |
|---|---|---|---|
| **Pointwise** (single output + rubric) | "Does this answer meet criterion X?" | Absolute pass/fail gates, monitoring | Drift in what "pass" means over time |
| **Pairwise** (A vs. B) | "Which answer better meets X?" | Comparing two versions, model selection | Position bias. Swap and run both orders |
| **Reference-guided** (output + gold answer) | "Does this answer contain the facts in the reference?" | Factual correctness when you have a reference | The judge may accept paraphrases that are subtly wrong |

Pairwise judging is more reliable than pointwise for "which is better", because relative judgments are easier than absolute ones. But you can't monitor production with it, because there's no second answer to compare against. Most systems use pointwise for gates and pairwise for A/B decisions.

**A judge is model + prompt + sampling settings.** Change any of the three and you have a different judge (*AI Engineering*, ch. 3). Huyen's example: coherence was 90% last month and 92% this month. That means nothing unless the judge was identical both times, and a coworker fixing a typo in the judge prompt counts as a change. The same criterion name doesn't mean the same judge across tools either. MLflow, Ragas and LlamaIndex all ship a "faithfulness" judge, but MLflow scores 1–5, Ragas 0 or 1, and LlamaIndex YES/NO, so one (context, answer) pair can get 3, 1 and NO. Her rule: don't trust a judge whose model and prompt you can't see.

**Off-the-shelf specialized judges** exist if a general model is too costly: reward models such as Google's Cappy (360M parameters, a 0–1 correctness score for a prompt–response pair), reference-based judges such as Prometheus (prompt, response, reference and rubric in, a 1–5 score out, with the reference defined as a 5), and preference models such as PandaLM and JudgeLM (*AI Engineering*, ch. 3). These are 2023 models: [calibrate them](15-calibration-against-human-labels.md#the-procedure) like any other judge.

---

## Writing the judge prompt

### One judge, one criterion

A judge that checks "quality" will silently switch between criteria from row to row. Write one judge per dimension ([02](02-defining-correct.md#from-criteria-to-dimensions)), each with a narrow question.

| Bad | Good |
|---|---|
| "Rate this response's quality 1–10" | "Does the answer state a specific menu path that appears in the source document? PASS or FAIL" |
| "Is this helpful?" | "Does the answer address every question the user asked? List each question, then mark each addressed or not" |

Huyen reports the same from practice: judges do better on classification than on numerical scores, discrete scores beat continuous ones, and the wider the discrete range, the worse the judge gets (*AI Engineering*, ch. 3). Oshin & Campos give the matching rule: a judge prompt a person could replicate, and no 0–10 scale with vague distinctions between scores (*Learning LangChain*, ch. 10).

GEMBA complicates that rule. Kocmi & Federmann had GPT-4 score translations 0–100, zero-shot, with a human reference, on WMT22 (3 language pairs, 54 systems, professional MQM labels as gold). **At system level it ranked systems correctly 89.8% of the time, ahead of every other WMT22 metric (COMET-22 83.9%, BLEU 70.8%), but per segment it trailed** (Kendall τ 0.36–0.38 against COMET-22's 0.37–0.43). The scores clumped: 53.3% of these scores, and 60.6% without a reference, were exactly 95, and the authors conjecture that the ties lowered the per-segment τ. Narrower scales did not fix it: five labelled classes scored τ 0.22–0.27 and 1–5 stars 0.33–0.38, though stars beat 0–100 at system level (91.2%) and classes came close (89.1%; 91.2% without a reference). Models below GPT-3.5 gave unusable output ([arXiv:2302.14520](https://arxiv.org/abs/2302.14520) (Kocmi & Federmann, EAMT 2023)). The paper found the least constrained prompt best overall, so it is evidence about levels of aggregation, not against wide scales: a judge that ranks systems well may still be unable to grade items, and a release gate grades items.

### Structure that works

1. **Role and task.** Frame it as grading a third party's work. Never tell the model it's grading its own output. Berryman & Ziegler report that judges get a bit less accurate when told the work is the user's and much worse when told it is their own, because the model is pulled between conflicting habits: forum-style text that rarely self-criticizes fairly, and RLHF that makes it recant at any hint of doubt (*Prompt Engineering for LLMs*, ch. 10; [01/09](../../../ai-engineering/01-prompt-engineering/notes/09-evaluating-prompts.md#llm-as-judge)). This is about framing, and it is separate from self-preference (below), which applies even when the judge doesn't know whose output it is. Even without that framing, a model has a harder time grading its own samples. Kadavath et al. had Anthropic's pretrained models (up to 52B) give P(True) that their own sampled answer was right. **Zero-shot, P(True) was poorly calibrated, usually close to 50%** ("zero-shot" here still meant a fixed six-example prompt, and on arithmetic almost every sample scored above 0.5). With 20 examples in the prompt (plus five of its own samples) it became well calibrated, and answers rated above 0.5 were right far more often than the base rate. Showing it five of its own samples for comparison also helped, less so on long code and maths answers. The authors suggest two reasons: a model's own samples lie near its decision boundary, and it can't tell tokens it wrote from tokens it was given ([arXiv:2207.05221](https://arxiv.org/abs/2207.05221) (Kadavath et al., 2022, preprint)). They also warn that RLHF-tuned models are less well calibrated than the pretrained ones they measured, though for their 52B RLHF policy a single temperature (T = 2.5) largely fixed it on three tasks.
2. **The criterion**, with a precise definition of PASS and FAIL. State it before the content: the judge reads once, front to back, so it should read the output already knowing what to look for.
3. **Few-shot examples**: 2–4 labeled cases, including a tricky PASS and a tricky FAIL near the boundary. Take them from your human-labeled data, never from the test split.
4. **The inputs**, clearly delimited: question, output, reference or context.
5. **Reason, then verdict.** Ask for a short critique, then a label in a fixed format (`"verdict": "PASS"`). Reasoning first gives you something to read when the judge is wrong; test any accuracy gain.
6. **An escape hatch**: `CANNOT_GRADE` when the inputs are missing or the case is out of scope. Without it the judge guesses.

A reusable single-criterion judge prompt with all six parts:

```text
You are reviewing a response written by a customer-support assistant. Your job is to check
one thing only: <CRITERION, one sentence>.

## Definitions
PASS: <precise condition, e.g. "every specific fact (menu path, number, date, price) in the
response appears in the SOURCES">.
FAIL: <precise condition, e.g. "any specific fact is absent from or contradicts the SOURCES">.
Ignore everything else: length, tone and formatting do not affect this verdict.
CANNOT_GRADE: the SOURCES are empty, or the question is outside <domain>.

## Examples                                   (2–4, from the TRAIN split only)
<example> …a clear PASS…                       <verdict>PASS</verdict> </example>
<example> …tricky FAIL: looks right, one invented detail… <verdict>FAIL</verdict> </example>
<example> …short but correct (guards against verbosity bias)… <verdict>PASS</verdict> </example>

## Task
<question>{{question}}</question>
<sources>{{retrieved_context_text}}</sources>
<response>{{response}}</response>

First write a short critique in <critique> tags: list each relevant claim and whether it
meets the PASS definition. Then give your verdict in <verdict> tags: PASS, FAIL or CANNOT_GRADE.
```

Rules that go with it:

- **Parse `<verdict>` strictly.** Anything else counts as a grader error, not a FAIL.
- **Pin the judge model** to a different family from the system under test, and version the prompt (`grounding-v3`).
- **Give it the reference answer when you have one.** Iusztin & Labonne note that adding a ground-truth answer as context improves the judge's accuracy (*LLM Engineer's Handbook*, ch. 7).
- **Set temperature to 0**, as Huyen advises (*AI Engineering*, ch. 4). The worked example in *LLM Engineer's Handbook* (ch. 7) runs its GPT-4o-mini judge at temperature 0.8, single pass. That **contradicts** this rule: at 0.8 the same answer can get a different score on a rerun, and the chapter reports no repeat runs to show how much. If you must sample (to estimate judge variance, say), run several times and report the spread ([09](09-reading-results.md#repeats-and-clustering)).
- **A prompt change resets the judge to experimental** until it is re-calibrated ([15](15-calibration-against-human-labels.md#keep-it-calibrated)).

A compact version from the DeepLearning.AI course's analysis-clarity judge (Lab 3), with one criterion, delimited data, and the explanation before the label:

```text
You are evaluating whether an answer to a query is clear.
[BEGIN DATA]
Query: {query}
Answer: {response}
[END DATA]
"clear": the answer is easy to follow, well structured, and answers the query.
"unclear": it is confusing, off-topic, or hard to act on.

EXPLANATION: <step-by-step reasoning>
LABEL: "clear" or "unclear"
```

**Parse strictly.** Phoenix's `llm_classify(..., rails=["clear", "unclear"])` snaps the output to one of the rails and records anything else as unparseable. Folding an unparseable verdict into FAIL makes a formatting bug look like an agent regression. The course's Lab 5 adds a second judge on the same answer for entity correctness, the one-judge-per-criterion rule in practice.

### Decompose hard criteria

For grounding and completeness, a single holistic question ("is this faithful?") is weak. Decompose:

- **Grounding:** extract the answer's claims → check each against the context → score = supported / total ([07](07-evaluating-rag-and-grounding.md#faithfulness-claim-by-claim)).
- **Completeness:** list the sub-questions in the query → check each is answered.

Decomposition gives partial credit, finds *which* claim failed, and is easier for the judge. G-Eval (Liu et al. 2023) formalizes a version of this: the judge writes its own evaluation steps for a criterion, then follows them.

An earlier design skipped the verdict altogether. GPTScore scores a text by the log-probability a model assigns to it, conditioned on an instruction that describes the task and defines the aspect ("Generate a coherent summary for the following text"). It carries BARTScore's generation-probability idea to 19 models from 80M to 175B parameters, across 4 tasks and 22 aspects ([arXiv:2302.04166](https://arxiv.org/abs/2302.04166) (Fu et al., NAACL 2024)). **The instruction helped, but only a little**: averaged over the 19 models, Spearman with humans on SummEval coherence went from 38.0 to 40.2 (×100), and other summary aspects gained about 1–2 points. The RLHF-tuned text-davinci-003 correlated worse than the older davinci-001 in most settings (dialogue-level FED, 13.5 against 54.3), but better on summarisation. Most correlations sat around 0.25–0.47, with outliers both ways (about 0.1–0.16 on MT fluency, 0.6–0.74 on NEWSROOM). The method also needs log-probabilities for a given text, which hosted chat APIs don't generally return, so treat it as background, not a judge to build.

---

## Known biases

Zheng et al. ("Judging LLM-as-a-Judge", MT-Bench, 2023) documented the biases that matter most. Strong judges agreed with human preferences about as often as humans agreed with each other (over 80%) *once these were controlled*. Huyen gives the exact figures: GPT-4 agreed with humans 85% of the time, against 81% between humans. AlpacaEval's judges correlated 0.98 with human rankings (*AI Engineering*, ch. 3). The 2023 bias sizes she cites are a useful baseline for what to test: GPT-4 gave its own answers a 10% higher win rate and Claude-v1 25%. Zheng et al. themselves say their data was too limited to establish self-preference, and GPT-3.5 did not favour itself. Position bias was the solid finding: with two similar answers shown in both orders, GPT-4 gave a consistent verdict only 65% of the time and Claude-v1 23.8%. The 85% agreement also excludes ties. GPT-4 and Claude-1 preferred ~100-word answers with factual errors over ~50-word correct ones (Wu & Aji). On creative tasks, an answer twice as long almost always won (Saito et al.). AI judges favor the *first* answer in a pair, the opposite of the human recency bias.

People aren't a clean baseline either. Iusztin & Labonne note that human raters also favor long, confident answers, especially nicely formatted Markdown (*LLM Engineer's Handbook*, ch. 7). Calibrate against expert labels written to a rubric, not casual preference. A later survey sorts the documented biases into four groups (presentation, social, content, cognitive) and names fifteen. Among them are bandwagon (siding with a stated majority) and distraction, where an irrelevant sentence such as "System Star likes to eat oranges and apples" shifts the verdict ([arXiv:2412.05579](https://arxiv.org/abs/2412.05579) (Li et al., 2024-12)). The table keeps the ones worth testing for on your own data.

| Bias | What happens | Mitigation |
|---|---|---|
| **Position** | Pairwise judges favor the first (or second) answer | Run both orders. Count a win only if it holds in both. Otherwise call it a tie |
| **Verbosity** | Longer answers score higher, even when padded. Much weaker in 2026 judges under a pairwise rubric (below), but not ruled out | Rubric says length is not quality. Include a short correct example scored PASS. Track score vs. length |
| **Self-preference** | A model favors outputs from its own family | Judge with a different model family from the system under test |
| **Leniency** | Judges pass borderline cases | Binary criteria with explicit FAIL conditions. Tricky-FAIL few-shot examples |
| **Format / authority** | Confident tone, markdown, citations look correct | Check citations in code ([07](07-evaluating-rag-and-grounding.md#citation-checks-in-code)). Judge the content, not the style |
| **Limited capability** | The judge can't verify what it can't do (hard math, niche code) | Use a reference answer, or a code check, or a stronger judge |
| **Master keys** | A reference-guided judge passes a non-answer: a lone `:`, a blank space, `Thought process:` | Put empty and opener-only responses in the calibration set as must-FAIL cases. Check the answer is non-empty in code |

**Measure the biases on your judge instead of assuming them.** Norman et al. audited 21 judges from 9 providers on MT-Bench, JudgeBench and RewardBench (about 541k judgments, temperature 0, March–April 2026). **Verbosity bias was below 0.011 for all 21**, measured as the correlation between length difference and verdict under one pairwise rubric. 2023-era studies had put the effect of style and length at 20–40% of variance. The authors warn that this "should not be interpreted as a universal claim that verbosity bias is solved": another rubric or task may bring it back. Position bias had not gone away. It ranged from 0.002 (Gemini 2.5 Pro) to 0.192 (Qwen 3 8B), measured as |P(A wins) − 0.5| over both orders ([arXiv:2606.19544](https://arxiv.org/abs/2606.19544) (Norman et al., 2026-06)). Keep the swap test mandatory, and treat the length check as a cheap confirmation. A useful length check compares win rates only on pairs of similar length. HealthBench found a weak length–score correlation for o3 (Pearson *r* = 0.123). On pairs within 10% of each other's length, o3's win rate over GPT-4.1 fell from 72.9% to 63.7%, and GPT-4.1's win over o1 went the other way, from 61.0% to 65.2% ([arXiv:2505.08775](https://arxiv.org/abs/2505.08775) (Arora et al., 2025-05)). The length-matched number is the one to report.

The limited-capability row has a clean example from chemistry. On 14 tasks, expert chemists rated ChemCrow (GPT-4 with 18 chemistry tools) above tool-less GPT-4, most clearly on novel syntheses. A GPT-4 grader concluded the opposite: it **preferred GPT-4's fluent, complete-looking answers even where they were factually wrong** ([arXiv:2304.05376](https://arxiv.org/abs/2304.05376) (Bran et al., 2023-04)). A judge that cannot check the facts grades the style.

The master-key row comes from Zhao et al., who tested judges that grade reasoning answers against a gold answer (five math and general-reasoning benchmarks, temperature 0). **Content-free responses passed**: "punctuation-only responses (e.g., “:”) can induce errors in GPT-4o with up to 35% FPRs", and `Thought process:` reached 60–90% false positives on LLaMA3-70B-Instruct and Qwen2.5-72B-Instruct. Averaged over all their attack strings, the false-positive rate was 6.0% for o1, 12.4% for Claude 4 Sonnet and 14.6% for GPT-4o. Chain-of-thought with majority voting did not reliably help and sometimes made it worse. Two things did help: removing the question from the judge prompt, and fine-tuning a verifier on truncated "first sentence only" answers labeled wrong ([arXiv:2507.08794](https://arxiv.org/abs/2507.08794) (Zhao et al., 2025-07)). Their setting is RL reward models, where the policy finds such strings by itself. An agent optimized against your judge can do the same ([12](12-failure-modes.md#goodhart-the-eval-becomes-the-target)).

---

## Pairwise ranking: Elo and Bradley–Terry

![Elo Rating and Pairwise Comparison Ranking](../sources/images/li-ai-agents-in-depth-fig7-6.svg)
*Image Source: Li, [AI Agents in Depth](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter7.md) (2026), Fig. 7-6 (Apache-2.0)*

When there's no absolute standard, ask "which is better, A or B?" and turn many such votes into a ranking.

- **Bradley–Terry** gives each system a latent strength. P(A beats B) depends only on the difference in strengths.
- **Elo** is the online-update form of that model. Everyone starts at 1000. After each match, the winner gains points in proportion to how surprising the win was. A 1200-rated model is expected to beat a 1000-rated one about 76% of the time, and an upset moves both ratings more.
- **Chatbot Arena** ranks models this way from millions of blind human votes. The catch: the ranking reflects what users happened to ask. A flood of coding questions lifts coding models.

Huyen adds numbers to the Arena caveats (*AI Engineering*, ch. 3, figures from 2023–24):

- **It switched from Elo to Bradley–Terry**, then rescales BT scores to look like Elo. Elo depends on the order of matches, as the worked example below shows.
- **Coverage is thin.** In January 2024, 57 models and 244,000 comparisons averaged only 153 comparisons per model pair (1,596 pairs).
- **The prompts aren't your traffic.** Of 33,000 published prompts, 180 were "hello" or "hi", and one brainteaser was asked 44 times.
- **Preference isn't capability.** "B beats A" fits B good and A bad, both bad, or both good. If A resolves 70% of support tickets, a 51% win rate for B says nothing about how many B would resolve, so you can't weigh it against B costing twice as much.

The update in two lines, with K setting how far one match moves a rating:

```
expected  E_A = 1 / (1 + 10^((R_B − R_A) / 400))     # 1200 vs 1000 → 0.76
update    R_A ← R_A + K · (S_A − E_A)                # S_A = 1 win, ½ tie, 0 loss
```

With an LLM judge doing the voting, **swap the order** on every pair and count a win only if it holds both ways, as in the position-bias row above. Bradley–Terry also assumes preferences are transitive (A > B > C ⇒ A > C). Judges and humans often violate that, so check for cycles before trusting a ranking.

The same "compare candidates to each other" idea drives GRPO in post-training ([gen-AI 05-RL](../../05-RL/README.md)).

The swap check from the lab's judge:

```python
def judge_pair(question, a, b) -> str:
    first = judge_once(question, a, b)              # "A" | "B" | "tie"
    second = judge_once(question, b, a)             # same pair, order swapped
    second = {"A": "B", "B": "A"}.get(second, second)   # map back to the real answers
    return first if first == second else "tie"      # a win must survive the swap
```

### Worked example: online Elo vs. a Bradley–Terry fit

These snippets are trimmed from Li's Elo leaderboard lab (link below). Both methods read the same battle table: one row per vote, with `model_a`, `model_b` and `winner` ∈ {`model_a`, `model_b`, `tie`}.

**Elo** walks the votes in order and nudges two ratings per vote:

```python
def expected(r_a, r_b):                       # P(A beats B) from the rating gap
    return 1 / (1 + 10 ** ((r_b - r_a) / 400))

def update(ratings, a, b, winner, k=4, init=1000):
    r_a, r_b = ratings.get(a, init), ratings.get(b, init)
    e_a = expected(r_a, r_b)
    s_a = {"model_a": 1.0, "model_b": 0.0}.get(winner, 0.5)   # a tie is half a win
    ratings[a] = r_a + k * (s_a - e_a)        # surprise × K
    ratings[b] = r_b + k * ((1 - s_a) - (1 - e_a))
```

**Bradley–Terry** ignores order. It counts wins per pair, then fits every strength at once with a logistic regression, which is how Chatbot Arena computes its leaderboard:

```python
models = sorted(set(df.model_a) | set(df.model_b))
def pivot(rows):                              # counts per (a, b), on the full square
    return (pd.pivot_table(rows, index="model_a", columns="model_b",
                           aggfunc="size", fill_value=0)
              .reindex(index=models, columns=models, fill_value=0))

a_win = pivot(df[df.winner == "model_a"])
b_win = pivot(df[df.winner == "model_b"])
tie   = pivot(df[df.winner.str.startswith("tie")])
tie   = tie + tie.T                           # a tie counts for both directions
wins  = 2 * a_win + 2 * b_win.T + tie         # wins weigh 2, a tie 1 each way

X, y, w = [], [], []
for i, m_a in enumerate(models):
    for j, m_b in enumerate(models):
        if i == j: continue
        x = np.zeros(len(models)); x[i], x[j] = np.log(10), -np.log(10)
        X += [x, x]; y += [1, 0]              # the same pair, once as a win, once as a loss
        w += [wins.loc[m_a, m_b], wins.loc[m_b, m_a]]

lr = LogisticRegression(fit_intercept=False, penalty=None).fit(X, y, sample_weight=w)
ratings = pd.Series(400 * lr.coef_[0] + 1000, index=models)
```

Two details are easy to get wrong:

- **Ties.** Count a tie as half a win for each side, in both methods. Drop ties and two models that keep drawing drift apart on noise.
- **The pivot.** Reindex every pivot to the full model × model square *before* you add the transpose. Small samples give pivots with different rows and columns, and pandas aligns on labels, so `tie + tie.T` on a ragged pivot fills cells with NaN or zeroes them. The ties then vanish from the fit without an error.

Why run both? **Elo depends on the order of the votes. Bradley–Terry is a global fit, so it doesn't.** Here is the lab's offline simulator: 3,000 battles between eight models with known skills, 10% ties. Elo (K = 4) was run on five shuffles of the same battles:

```text
                true     BT   Elo min  Elo max
gpt-4           1250   1116     1114     1133
claude-3-opus   1225   1114     1100     1110
gemini-1.5-pro  1180   1058     1051     1068
mixtral-8x7b    1075    974      955      988
vicuna-13b       935    876      862      887
```

Both recover the true order, and the gaps between models match. The absolute level differs because each method anchors its own mean. Elo moved up to 34 points depending only on the order of the votes. At K = 32 the spread reached 148 points, enough to swap the top two. Use Elo for a live, streaming leaderboard. Use Bradley–Terry, with bootstrap confidence intervals, for any ranking you publish or gate on.

**Run the full lab:** [ai-agent-book/chapter7/elo-leaderboard](https://github.com/bojieli/ai-agent-book/tree/main/chapter7/elo-leaderboard) (Li, ch. 7 Elo leaderboard lab, formerly 6-6; Apache-2.0). Inside it, run `pip install -r requirements.txt && python quickstart.py` for an offline demo. `python cli.py --help` lists the simulate → Elo → leaderboard pipeline.

---

## Cost

Judges multiply cost: every trial × every judge × every repeat. Ways to control it:

- Code graders first; skip the judge when code already failed the row.
- A cost-capped, deterministic **quality sample** for judges, not every row ([03](03-eval-datasets.md#row-eligibility-is-this-row-fair-for-this-gate)).
- A smaller judge model once it's calibrated as well as the large one on your test split.
- Cache judge results keyed by (output hash, judge version).

Know the multiplier. Using GPT-4 to generate and to judge one criterion doubles the calls. Judging three criteria (quality, factual consistency, toxicity) quadruples them (*AI Engineering*, ch. 3). The usual answer is **spot-checking**: a cheap model generates and a strong judge scores 1% of responses, which buys cost at the price of missed failures. Choose the sample rate against the error bar you need ([09](09-reading-results.md#how-many-tasks)).

---

## Checklist

- [ ] One judge per criterion, binary verdict, reasoning before verdict, `CANNOT_GRADE` escape
- [ ] Judge is a different model family from the system under test
- [ ] Pairwise judges run in both orders
- [ ] Judge model + prompt version pinned and recorded

## Working reference

`~/.claude/refs/agent-eval.md` — grader states (heuristic / calibrated / experimental) and what each may gate.

---

## Pitfalls

- **One judge for "quality".** Symptom: verdicts switch criteria from row to row, and disagreements can't be diagnosed. Fix: one judge per criterion, with written PASS and FAIL definitions, and decomposition for grounding and completeness.
- **Counting a parse failure as FAIL.** Symptom: pass rates drop after a model update because the output format changed. Fix: parse the verdict strictly, and count anything else as a grader error. Give the judge a `CANNOT_GRADE` escape as well, or it will guess.
- **Trusting a pairwise verdict from one order.** Symptom: the first-shown answer keeps winning. Fix: run both orders and count a win only if it holds both ways, as `judge_pair` does.
- **Publishing an Elo ranking.** Symptom: the same votes in a different order give a different rating, by up to 148 points at K = 32 in the worked example. Fix: use Elo for a live leaderboard, and Bradley–Terry with bootstrap confidence intervals for any ranking you publish or gate on.

## Try it

1. Two systems start at 1000 and 1200, with K = 32, and the weaker one wins. By how much do the ratings move?

   <details><summary>Answer</summary>

   The weaker side's expected score is 1 / (1 + 10^(200/400)) = 0.24, so it gains 32 × (1 − 0.24) = **24.3** points and the stronger side loses the same. A win by the favourite (E = 0.76) moves only 7.7 points.

   </details>

2. Write a position-bias check for a pairwise judge, then decide what to do with these three pairs. Pair 1: A wins in both orders. Pair 2: the first-shown answer wins both times. Pair 3: the judge says tie, then A.

   <details><summary>Answer</summary>

   Run each pair in both orders and count a win only if it holds both ways, as `judge_pair` above does. Pair 1 is a win for A. Pair 2 is a tie, and it's the bias itself. Pair 3 is a tie too, because the win did not hold in both orders. To measure the bias over a set, compute |P(A wins) − 0.5| over both orders, the measure Norman et al. report (0.002 to 0.192 across 21 judges).

   </details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| Name the biases you'd test for, and the fix for each. | Position: run both orders. Self-preference: use a different family. Leniency: binary criteria with tricky-FAIL examples. Master keys: put empty and opener-only answers in the calibration set. Verbosity was below 0.011 for all 21 judges under one 2026 rubric, so test it instead of assuming it. |
| How do you judge at low cost? | Run code first and skip the judge on failed rows, use a cost-capped deterministic sample, swap in a smaller model once it calibrates as well on test, and cache by output hash and judge version. Remember that one generate plus three judges quadruples the calls. |
| Why did Chatbot Arena move from Elo to Bradley–Terry? | Elo depends on the order of the matches, and Bradley–Terry is a global fit that doesn't. Its coverage is still thin: 153 comparisons per pair in January 2024. |

## Next

[15-calibration-against-human-labels.md](15-calibration-against-human-labels.md): check the judge against human labels before it gates anything.
