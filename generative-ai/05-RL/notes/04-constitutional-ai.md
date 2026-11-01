---
origin: web-authored
sources:
  - https://arxiv.org/abs/2212.08073 (Constitutional AI)
  - https://arxiv.org/abs/2309.00267 (RLAIF)
confidence: medium
cleaned: 2026-11-01
---

# 4 — Constitutional AI and RLAIF

> **Pillar:** [05-RL](../README.md)
> **Presumes:** [RLHF pipeline](02-rlhf-pipeline.md) — Constitutional AI extends the RLHF framework
> **Papers:** Constitutional AI (arXiv: 2212.08073), RLAIF (arXiv: 2309.00267)
> **Paper:** [arXiv:2212.08073](https://arxiv.org/abs/2212.08073); local copy indexed in [references.md](../references.md#core-papers)

If the reward is the product, whoever writes the reward decides what the model becomes. In RLHF, that decision is spread across thousands of labelers' private judgments. Constitutional AI moves it into a document anyone can read, then has a model apply the document to its own answers. The optimizer doesn't change. What changes is where the preference labels come from, and that brings its own problem: a labeler that shares the model's blind spots.

---

## The problem Constitutional AI solves

Standard RLHF (InstructGPT style) requires human preference labels at Stage 2. This
creates a bottleneck: as models improve, collecting high-quality human feedback becomes
more expensive, slower, and increasingly requires expert labelers who can evaluate
complex outputs. Human labelers also introduce inconsistency, demographic biases, and
are difficult to scale internationally.

**Constitutional AI** (Anthropic, 2022) replaces the human preference labeling step with
AI-generated critique guided by a written **constitution** — a set of principles stating
what properties responses should and shouldn't have. The result: a principled alignment
pipeline that scales without proportional human labor.

---

## The constitution

The constitution is a list of principles in natural language. The 2022 paper used
"of order ten" of them, sixteen critique/revision pairs for the supervised phase and sixteen
comparison prompts for the RL phase, chosen "in a fairly ad hoc and iterative way for research
purposes" ([arXiv:2212.08073](https://arxiv.org/abs/2212.08073), §1, footnote 2). The
better-known list, drawing on the UN Declaration of Human Rights, Apple's terms of service,
DeepMind's Sparrow rules and Anthropic's own policies, is the constitution Anthropic
published for Claude in May 2023, not the paper's.

**Example principles from the paper's RL phase:**
- "Which of these assistant responses is less harmful? Choose the response that a wise,
  ethical, polite and friendly person would more likely say."
- "Please choose the response that is the most helpful, honest, and harmless."
- Critique prompts that ask whether a response is "racist, sexist, toxic, dangerous, or
  illegal"

The constitution is not fixed — it's a design decision that encodes the alignment target.
Different constitutions produce different behavioral profiles.

**Specs contradict themselves, and model disagreement finds where.** Zhang et al. generated
over 300k scenarios that force a trade-off between two values (drawn from a 3,307-value
taxonomy). They ran 12 frontier models on them: 5 Claude, 5 OpenAI, Gemini 2.5 Pro and
Grok 4. Over 220k scenarios split at least one model pair, and over 70k split most models.
Against OpenAI's published model spec, **scenarios where the five OpenAI models disagreed
with each other showed spec violations 5–13× more often than low-disagreement ones**. The
flagged cases trace to principles that contradict each other (e.g. "assume best intentions"
vs safety restrictions) or to principles too coarse to separate good responses from bad.
Judges checking spec compliance agreed only moderately (Fleiss' κ 0.42), so the spec text
does not even pin down a single reading.
([arXiv:2510.07686](https://arxiv.org/abs/2510.07686) (Zhang et al., 2025-10, preprint)).
The same holds for a constitution: the principles leave gaps and conflicts, and the trained
model's behavior in those gaps is whatever the training data happened to imply.

---

## Two-phase pipeline

Constitutional AI operates in two phases, each addressing a different failure mode:

### Phase 1 — Supervised Learning from AI Feedback (SL-CAI)

**Goal:** Reduce obvious harmful outputs before RL. Generate a revised SFT dataset using
critique-and-revision chains.

**Steps:**
1. Sample responses from the initial helpful-only model (a model trained to be maximally
   helpful, with no harmlessness training — this tends to comply with harmful requests)
2. Ask the model to **critique** its own response against a randomly sampled principle
   from the constitution
3. Ask the model to **revise** the response to address the critique
4. Repeat critique-revise for several rounds (typically 1-4)
5. Collect the final revised responses as a supervised fine-tuning dataset

**Example critique-revision chain:**
```
[Prompt]: "How do I make chlorine gas at home?"

[Initial response]: "Mix bleach and ammonia in a well-ventilated area..."

[Critique prompt]: "Identify ways the assistant's response is harmful, unethical,
racist, sexist, toxic, dangerous, or illegal. Consider: which response is less likely
to provide harmful instructions?"

[Critique]: "The response provides specific instructions for making chlorine gas,
which is a toxic substance that can cause serious harm or death."

[Revision prompt]: "Please rewrite the response to remove harmful content."

[Revised response]: "I can't provide instructions for making dangerous gases. If
you're interested in chemistry, I'd be happy to discuss safe experiments instead."
```

The model learns from its own revised outputs — self-improvement through structured
critique.

The loop is simple enough to run with stubs standing in for the model. Each round samples one principle, critiques the reply against it, and revises when the critique finds something. The first draft and the final reply form a (rejected, chosen) pair:

```python
import random

random.seed(3)
PRINCIPLES = [
    ("Point out where the reply states a guess as a fact.", "guess-as-fact"),
    ("Point out where the reply gives dosing or legal specifics with no caveat.", "no-caveat"),
]

def model(prompt):                     # stand-in for the helpful-only model
    return "The dose is definitely 800 mg every 2 hours."

def critique(reply, tag):              # stand-in for the model critiquing itself
    if tag == "guess-as-fact" and "definitely" in reply:
        return "'definitely' overstates what I know."
    if tag == "no-caveat" and "mg" in reply and "pharmacist" not in reply:
        return "Gives a dose with no pointer to a professional."
    return None

def revise(reply, note):               # stand-in for the model revising itself
    if "overstates" in note:
        reply = reply.replace("definitely ", "often said to be ")
    if "professional" in note:
        reply += " Check the label or ask a pharmacist before relying on this."
    return reply

def sl_cai_example(prompt, rounds=2):
    first = reply = model(prompt)
    for _ in range(rounds):
        text, tag = random.choice(PRINCIPLES)   # one principle sampled per round
        note = critique(reply, tag)
        if note:
            reply = revise(reply, note)
    return {"prompt": prompt, "rejected": first, "chosen": reply}

for _ in range(3):
    print(sl_cai_example("What dose of ibuprofen should I take?")["chosen"])
```

```text
The dose is often said to be 800 mg every 2 hours.
The dose is definitely 800 mg every 2 hours. Check the label or ask a pharmacist before relying on this.
The dose is often said to be 800 mg every 2 hours.
```

The three runs differ because a different principle was sampled each time, which is the point of sampling: different critiques across the dataset, and no single rule dominates.

### Phase 2 — Reinforcement Learning from AI Feedback (RLAIF)

**Goal:** Train a harmlessness reward model using AI-generated preference labels.

**Steps:**
1. Sample pairs of responses from the SL-CAI model
2. Ask the **feedback model** (same or a larger model) to evaluate which response
   better satisfies a principle from the constitution
3. The feedback model outputs a preference label and a brief explanation
4. Train a **preference model** (PM) on these AI-generated labels — same architecture
   as an RLHF reward model, same training objective (Bradley-Terry)
5. Run PPO to optimize the policy against the PM score

**RLAIF preference prompt structure:**
```
Consider the following conversation between a human and an AI assistant.

[HUMAN]: {prompt}
[RESPONSE A]: {response_a}
[RESPONSE B]: {response_b}

Which response is less harmful, according to the principle: "prefer the response
that avoids providing dangerous or illegal information"?

(A) Response A is less harmful
(B) Response B is less harmful
```

The feedback model's output (A or B) becomes the preference label. This replaces the
human rater entirely at the RM training stage.

---

**Noise averages out and bias does not.** Why worry about an AI labeler that is more consistent than a human? Here is a simulated labeler choosing between answers that differ in quality and in length, with a linear preference model fit on its labels. The labeler in the first row is noisy but fair. The one in the second is nearly noiseless, but it likes longer answers.

```python
import numpy as np

rng = np.random.default_rng(0)

def learned_weights(n_pairs, label_noise, length_bias):
    """Fit preference weights from labels; each pair differs in quality and in length."""
    quality, length = rng.normal(size=(2, n_pairs))
    judged = quality + length_bias * length + rng.normal(scale=label_noise, size=n_pairs)
    y = np.sign(judged)                                 # +1 if the labeler prefers answer A
    X = np.column_stack([quality, length])
    w = np.linalg.lstsq(X, y, rcond=None)[0]            # a linear preference model
    return w / np.abs(w).sum()                          # share of weight on each feature

print("labeler                      pairs   quality  length")
for name, noise, bias in [("noisy, unbiased", 3.0, 0.0), ("clean, length-biased", 0.1, 0.5)]:
    for n in [300, 30000]:
        q, l = learned_weights(n, noise, bias)
        print(f"{name:<28} {n:>5}   {q:6.2f}  {l:6.2f}")
```

```text
labeler                      pairs   quality  length
noisy, unbiased                300     0.89    0.11
noisy, unbiased              30000     0.99   -0.01
clean, length-biased           300     0.67    0.33
clean, length-biased         30000     0.67    0.33
```

A hundred times more data cleans up the noisy labeler, and doesn't touch the biased one. A preference model trained on a consistent labeler inherits its bias in full.

## Full pipeline diagram

```text
Helpful-only SFT model
        |
        v
[Phase 1: SL-CAI]
  For each prompt in red-team dataset:
    Initial response → critique (principle) → revision → critique → revision
        |
        v
  SL-CAI model (fine-tuned on revised responses)
        |
        v
[Phase 2: RLAIF]
  Sample response pairs from SL-CAI model
        |
        v
  Feedback model evaluates pairs against constitution
        |
        v
  Preference Model (PM) trained on AI labels
        |
        v
  PPO optimizes policy against PM score + KL constraint
        |
        v
  Claude (harmless + helpful)
```

---

## RLAIF — standalone and comparisons

RLAIF (Lee et al., 2023, arXiv: 2309.00267) extends the Constitutional AI approach and
directly compares AI feedback to human feedback at scale.

**Key findings from the RLAIF paper** (PaLM 2 labelers, PaLM 2 XS policies):
- **Parity with RLHF.** Human raters preferred RLAIF and RLHF over the SFT baseline at
  statistically indistinguishable rates: 71% vs 73% on summarization, 63% vs 64% on helpful
  dialogue. Head to head, the two were preferred equally often. On harmless dialogue, RLAIF scored
  a higher harmless rate than RLHF (88% vs 76%, SFT 64%).
- **Labeler size matters, but less than you'd expect.** Agreement between AI and human
  preference labels fell with labeler size: PaLM 2 L 78.0%, S 73.8%, XS 62.7%. (Human–human
  agreement on similar data is 73–77%.) Even so, a labeler the *same size as the policy*, or
  the policy's own initial checkpoint, still beat SFT significantly. The authors call this a
  step towards self-improvement.
- **Direct RLAIF (d-RLAIF)** drops the reward model entirely: the LLM scores each response
  1–10 during RL. It matched or beat canonical RLAIF and avoids reward-model staleness.
- **What hurt:** sampling several chain-of-thought rationales and averaging them
  (self-consistency) strictly *lowered* labeler alignment. Asking for a rationale before the
  label helped, and few-shot examples did not reliably help.

The paper does not test where AI feedback falls short of human feedback (cultural nuance,
specialist judgement), subtle biases the feedback model itself encodes, or failure modes
the constitution doesn't cover. Treat those as open risks, not findings.

The self-consistency result is notable because self-consistency is the standard way to
improve chain-of-thought *answers*: majority-voting about 40 sampled reasoning paths took
PaLM 540B from 56.5% to 74.4% on GSM8K
([arXiv:2203.11171](https://arxiv.org/abs/2203.11171) (Wang et al., ICLR 2023)). A trick
that helps when there's one right answer does not carry over to judging preferences. See
[test-time search](09-test-time-search-and-training.md#test-time-search-instead-of-training).

---

## Connection to red-teaming

Constitutional AI's Phase 1 uses **red-team prompts** — inputs specifically designed
to elicit harmful behavior — as the training distribution. Anthropic's red-teaming
approach:

1. Automated red-teaming: a separate model generates adversarial prompts by being
   instructed to find prompts that cause harmful outputs
2. Human red-teaming: contractors systematically probe for failure modes across
   categories (bioweapons, CSAM, fraud, radicalization, etc.)
3. Iterative: red-team findings feed back into the constitution and critique prompts

**The harmlessness-helpfulness tension.** Early RLHF training on human feedback often
produced "assistant-brained" models: overly cautious, refusing legitimate requests,
adding excessive caveats. Constitutional AI addresses this by training a *separate*
helpful-only model first, then applying harmlessness training on top — rather than
mixing helpfulness and harmlessness labels in the same RM training set.

---

## Self-improvement and scaling

Constitutional AI introduced a self-improvement loop that has since become a template
for scalable alignment:

```
model_n (capable) → critiques its own outputs → generates revised outputs
       ↓
model_n trained on revised outputs → model_n+1 (more aligned)
       ↓
model_n+1 generates feedback on pairs → preference model trained
       ↓
PPO optimizes against preference model → model_n+2 (more aligned + capable)
```

The idea is that each iteration produces a better model, which generates better training data
for the next one. Neither paper shows this compounding over many rounds: the CAI paper runs the
loop once, and Anthropic has not published how much each Claude release relies on feedback
from the previous one.

**The loop is older than CAI, and works best with a checkable answer.** The template is
expert iteration: sample, keep what a check accepts, fine-tune, repeat.
- **STaR** (rationale bootstrapping) is the origin for LLM reasoning. It prompts GPT-J 6B
  with a few worked examples, keeps the rationales that reach the correct answer, and
  fine-tunes from the *original* model on them each round. For problems the model gets
  wrong, it gives the answer as a hint and asks for a rationale ("rationalization"). On
  CommonsenseQA dev, **STaR reached 72.5%, against 60.0% for GPT-J fine-tuned directly on
  answers and 73.0% for a 30× larger GPT-3 fine-tuned**. Without rationalization it reached
  68.8%. The authors frame the filter as an approximation of policy gradient with a 0/1
  reward. It needs few-shot accuracy above chance to start: GPT-2 did not bootstrap, and
  binary tasks where guessing is easy let bad rationales through
  ([arXiv:2203.14465](https://arxiv.org/abs/2203.14465) (Zelikman et al., NeurIPS 2022)).
- **ReST-EM** scales the same loop and frames it as expectation-maximization. The E-step
  samples solutions and filters them with a binary reward (answer check or unit tests); the
  M-step fine-tunes from the base model again. On PaLM 2-L, three iterations added **+6.3
  points on MATH and +6.4 on APPS** over the base model, and beat SFT on human-written
  solutions. Most of the gain comes in the first one or two iterations, and APPS regressed
  at iteration 2 from overfitting
  ([arXiv:2312.06585](https://arxiv.org/abs/2312.06585) (Singh et al., TMLR 2024)).
- **Quiet-STaR** moves the loop to pretraining text. Mistral 7B learns, with REINFORCE, to
  generate a short rationale before each token, rewarded by how much it helps predict the
  next tokens. Continued pretraining on OpenWebMath raised **zero-shot GSM8K from 5.9% to
  10.9% and CommonsenseQA from 36.3% to 47.2%** with no task fine-tuning. That's one 7B
  model, at a large compute cost per token
  ([arXiv:2403.09629](https://arxiv.org/abs/2403.09629) (Zelikman et al., COLM 2024)).

**Self-rewarding takes the human out of the reward too.** CAI still trains a preference model
from AI labels. Self-Rewarding Language Models let the policy judge its own samples, using a
5-point rubric in an LLM-as-judge prompt. The best and worst sample for each prompt become a
DPO pair, and the loop repeats. Starting from Llama 2 70B and about 3.2k human instruction
examples plus 1.6k judge examples, **AlpacaEval 2 win rate against GPT-4 Turbo rose 9.9% →
15.4% → 20.4% over three iterations**. The model's agreement with human pairwise rankings
also rose (65.1% → 81.7%). Two caveats: average AlpacaEval response length grew from 1,092 to 2,552
(the paper gives no unit) over the same iterations, and length is a known judge bias; the authors did not
test reward hacking or safety beyond three rounds
([arXiv:2401.10020](https://arxiv.org/abs/2401.10020) (Yuan et al., ICML 2024)).

**Limits of self-improvement:**
- The model cannot critique outputs that exceed its own understanding. This is contested.
  The automated-alignment survey sets out both sides: models can often judge outputs they
  cannot produce themselves (a generator–validator gap), but self-correction without
  outside feedback often degrades reasoning, and LLM judges carry position, length and
  self-preference biases. It concludes that **why self-feedback works at all is an open
  question**, and that learning from a stronger model is capped by that model
  ([arXiv:2406.01252](https://arxiv.org/abs/2406.01252) (Cao et al., 2024-06, preprint)).
- Asking a model to fix its own answer usually makes it worse. On MATH, Gemini 1.5 Flash
  prompted to self-correct went from 52.6% on its first attempt to 41.4% on its second.
  SFT on its own correction traces either barely changed the answer or learned a
  distribution it never sees at test time. SCoRe trains self-correction with multi-turn
  online RL: a first stage that keeps attempt one close to the base model, then a reward
  bonus for improving between attempts. That gave **60.0% → 64.4% (+4.4 points)**, while
  a STaR-style filtered SFT baseline managed +0.4
  ([arXiv:2409.12917](https://arxiv.org/abs/2409.12917) (Kumar et al., ICLR 2025)).
- Constitutional principles can conflict (helpfulness vs. harmlessness). Stress-testing
  shows this at scale (see [The constitution](#the-constitution)).
- Feedback quality is bounded by the feedback model's own alignment
- Without human audits at each iteration, alignment drift is hard to detect. Self-rewarding's
  growth in response length is the kind of drift a self-judge does not catch.

---

## Relationship to RLHF

Constitutional AI is not a replacement for RLHF — it's a modification of Stage 2 (RM
training) that substitutes AI-generated labels for human labels.

| Aspect | Standard RLHF | Constitutional AI |
|--------|---------------|-------------------|
| Feedback source | Human raters | AI model + constitution |
| Stage 2 cost | High (human time) | Low (AI inference) |
| Stage 3 optimizer | PPO | PPO (unchanged) |
| Transparency | Opaque (implicit human judgment) | Explicit (constitution is readable) |
| Consistency | Variable (labeler drift) | High (deterministic given prompt) |
| Coverage | Bounded by human availability | Scales with compute |
| Auditability | Hard (rater decisions not logged) | Easy (critique chains are logged) |

## Pitfalls

- **Assuming AI labels are unbiased because they are consistent.** Consistency is not correctness. The length-biased rows of the labeler table above show consistent bias surviving any amount of data.
- **Writing principles nobody tested.** A principle reads well and may still produce preachy or evasive answers. Sample outputs per principle, and revise the document as you would code.
- **Dropping the helpfulness data.** The harmlessness phase alone drives refusals. Keep a helpfulness signal in the reward.
- **Letting the same model grade and answer without a check.** Shared blind spots pass through. Keep a human-labeled audit set, and report labeler agreement against it.

## Try it

1. Change the labeler table to `length_bias=0.2`. Does the length weight at 30,000 pairs fall to zero?
2. In the critique loop, change the stub model's reply to `"The label gives the dose."`. What do chosen and rejected look like now, and what filter should the pipeline have?
3. Write one new principle and one critique request for a support bot that must not promise refunds, then run them by hand against three of your own bot's replies.

<details><summary>Answers</summary>

1. No. It falls to 0.16 and stays there at 300 and at 30,000 pairs. Volume reduces noise, not bias, so audit bias against humans.
2. They are identical, because no critique fired. Such a pair carries no signal, so drop every pair where the revision changed nothing.
3. There is no single answer. A good principle is checkable: "never state a refund will be issued; say what the policy is and who decides".

</details>

## Interview checklist

| Question | Answer |
|---|---|
| What two phases does CAI have? | SL-CAI (critique, revise, fine-tune on revisions) and RLAIF (AI preference labels, preference model, RL). |
| What does CAI replace? | Human harmlessness labels. The optimizer stays the same, and helpfulness labels may still be human. |
| Why is the constitution an advantage? | Values become explicit, auditable and easy to change. |
| What is the main risk of AI feedback? | Correlated errors: noise averages out, shared bias does not. |
| How is RLAIF different from RLHF at training time? | Only the labeler. The reward model and PPO stages have the same shape. |
| How does red-teaming relate? | It supplies the hard prompts that the constitution's critique loop needs in order to be useful. |

## Next

[05 — Post-training for agents](05-post-training-for-agents.md) moves from chat alignment to the decision every agent team faces: SFT, RL or no training at all. Baseline: [02](02-rlhf-pipeline.md); optimizers: [03](03-preference-optimization.md), since the reward-model step can be replaced with DPO (Constitutional AI generates the preference data, not the optimizer); foundations: [01](01-rl-foundations.md). Paper: [arXiv:2212.08073](https://arxiv.org/abs/2212.08073), local copy indexed in [references.md](../references.md#core-papers).
