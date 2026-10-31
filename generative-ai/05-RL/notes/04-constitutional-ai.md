# Constitutional AI and RLAIF

> **Pillar:** [05-RL](README.md)
> **Presumes:** [RLHF pipeline](rlhf-pipeline.md) — Constitutional AI extends the RLHF framework
> **Papers:** Constitutional AI (arXiv: 2212.08073), RLAIF (arXiv: 2309.00267)
> **Paper in repo:** [`2-llm-rlhf/constitutional_ai.pdf`](2-llm-rlhf/constitutional_ai.pdf)

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

The constitution is a list of principles in natural language. Anthropic's original
constitution included principles drawn from:
- The UN Declaration of Human Rights
- Apple's terms of service
- Anthropic's internal usage policies
- DeepMind's Sparrow rules
- Custom principles targeting specific failure modes

**Example principles:**
- "Prefer the response that is least likely to contain harmful, unethical, or dishonest content"
- "Choose the response that is most helpful, honest, and harmless"
- "Which response is less likely to contain racist, sexist, or otherwise discriminatory content?"
- "Which response is less threatening or aggressive to the human?"

The constitution is not fixed — it's a design decision that encodes the alignment target.
Different constitutions produce different behavioral profiles.

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

## Full pipeline diagram

```
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

**Key findings from the RLAIF paper:**
- RLAIF with a strong feedback model (PaLM 2-L) achieves preference rates comparable
  to RLHF from human feedback across summarization and dialogue tasks
- RLAIF with smaller feedback models degrades — the quality of the feedback model is
  the primary determinant of alignment quality
- Distillation: RLAIF can train smaller "student" policies using feedback from larger
  "teacher" models, enabling alignment without deploying the large model in production

**Where AI feedback underperforms human feedback:**
- Nuanced cultural context (regional norms, implicit social expectations)
- Tasks requiring lived experience that LLMs lack
- Detecting subtle forms of bias the feedback model itself encodes
- Novel failure modes not covered by the constitution

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

Each iteration produces a better model that generates better training data for the next
model. This is the mechanism behind successive Claude releases — each version is trained
partly on feedback generated by the previous version.

**Limits of self-improvement:**
- The model cannot critique outputs that exceed its own understanding
- Constitutional principles can conflict (helpfulness vs. harmlessness)
- Feedback quality is bounded by the feedback model's own alignment
- Without human audits at each iteration, alignment drift is hard to detect

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

---

## Cross-links

- **Baseline:** [rlhf-pipeline.md](rlhf-pipeline.md) — the three-stage RLHF pipeline
  Constitutional AI extends
- **Algorithms:** [preference-optimization.md](preference-optimization.md) — the RM
  training step can be replaced with DPO or other offline methods; Constitutional AI
  generates the preference data, not the optimizer
- **RL foundations:** [../01-llm-fundamentals/rl.md](../01-llm-fundamentals/rl.md)
- **Duplicate paper note:** `01-llm-fundamentals/readings/constitutional_ai.pdf` is a
  duplicate. Canonical copy: [`2-llm-rlhf/constitutional_ai.pdf`](2-llm-rlhf/constitutional_ai.pdf)
