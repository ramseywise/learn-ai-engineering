---
origin: synthesis
sources:
  - https://github.com/davidkimai/Context-Engineering (00_foundations/08–14, 00_COURSE/08_field_theory_integration/00–03, NOCODE/00_foundations/05–10, NOCODE/10_mental_models/01–05 — snapshot 2026-08-14)
  - https://arxiv.org/abs/2502.15208
  - https://arxiv.org/abs/2506.10077
  - https://arxiv.org/abs/2502.20332
confidence: low
cleaned: 2026-11-01
---
# 99 — Appendix: The Speculative Field Track

> About a third of the upstream course treats context as a continuous "semantic field" with attractors, resonance and boundaries. It is a metaphor, not an engineering method. This appendix summarises it so you can recognise the vocabulary and pull out the few practical ideas.

---

## How to read this appendix

Chapters 01–13 cover techniques with evidence behind them. Nothing here does in the same way. The upstream field-theory material:

- borrows terms from physics and dynamical systems (fields, attractors, resonance, quantum superposition),
- cites a handful of real papers, then extrapolates well beyond what they show,
- offers "protocols" (`/attractor.co.emerge`, `/field.resonance.scaffold`) whose effect is that of an ordinary structured prompt ([09](09-protocols.md)).

Treat every claim below as **hypothesis or metaphor** unless it's tied to a paper.

---

## The core claims, and what's under them

| Upstream concept | Claim | Grounded reading |
|---|---|---|
| **Neural field** | Context is a continuous field, not a sequence of tokens; information persists through resonance rather than position | Attention spreads influence across the whole window, so content can stay relevant without being recent. True, and already covered by positional effects ([02](02-context-anatomy.md), [11](11-failure-modes.md)) |
| **Attractors** | Stable patterns of meaning that the conversation falls into and is hard to leave | Models do settle into recurring framings, and early framing biases later turns. Wang et al. (2502.15208) find that successive paraphrasing converges to stable 2-cycles. Practical version: an early mistake keeps pulling later turns back ([context poisoning](11-failure-modes.md)) |
| **Resonance** | Related concepts reinforce each other; "tuning" the field strengthens desired patterns | Repeating and cross-referencing key constraints raises their salience. That's ordinary emphasis and recency |
| **Boundaries** | Permeable membranes control what enters and leaves the field | Gating what gets into the window. This is the Select lever ([04](04-retrieval.md)) |
| **Persistence / decay** | Field patterns fade unless reinforced | Older content loses influence and is lost first under compaction ([05](05-compression-compaction.md)) |
| **Symbolic mechanisms** | LLMs implement abstraction → induction → retrieval | **Real result** (Yang et al., ICML 2025): identified attention heads for each stage. Applied in [07](07-structured-context.md) |
| **Quantum semantics** | Meaning is undetermined until "observed" by an interpretive context; Bell-style tests show non-classical contextuality | Agostino et al. (2506.10077) report CHSH-style violations in LLM interpretation of ambiguous phrases: S values from 1.2 to 2.8, with several runs at 2.3–2.4 against the classical bound of 2. The authors themselves caution that the test assumes no-signalling, which behavioural experiments often violate, so the excess correlation may come from direct influence between the settings rather than genuine contextuality. Practical version: an ambiguous prompt has no fixed meaning, so disambiguate with context. The quantum framing adds no technique |
| **Unified field theory** | Combines symbolic, field and quantum views into one framework | No testable content beyond the parts above |

Two of the rows rest on real papers, and their figures show how modest the grounded versions are. Wang et al.'s "attractor" is a 2-cycle: paraphrase a text over and over and it alternates between two clusters of near-identical outputs.

![Successive paraphrasing falls into a 2-cycle between two clusters](../sources/images/wang-attractor-cycles-fig1.png)
*Image Source: Wang et al. (2025)*

Yang et al.'s "symbolic mechanism" is a three-stage circuit of attention heads. Abstraction heads map tokens to variables, induction heads find the pattern over variables, and retrieval heads map the predicted variable back to a token. The tasks are small, such as ABA/ABB rule induction from two examples, where Llama-3.1 70B scored 95%. The circuit showed up clearly in Gemma-2, Qwen2.5 and Llama-3.1, with weaker evidence in GPT-2.

![Symbol abstraction, symbolic induction and retrieval heads](../sources/images/yang-emergent-symbolic-mechanisms-fig1.png)
*Image Source: Yang et al. (2025)*

Agostino's result turns on the bound of 2 in the CHSH test, and the script below shows why that bound alone doesn't establish anything quantum. It's arithmetic, not an LLM experiment. A fixed classical strategy can't exceed 2, a quantum singlet reaches 2.828 at the best angles, and a setup where one side's outcome directly depends on the other's setting reaches 4. That is the authors' own caution from the table above: the test assumes no-signalling, and behavioural experiments often violate it.

```python
import math
# CHSH: S = |E(a,b) - E(a,b') + E(a',b) + E(a',b')|. Any local classical model has |S| <= 2.
def chsh(e): return abs(e["ab"] - e["ab'"] + e["a'b"] + e["a'b'"])

# Deterministic classical strategies: each setting's outcome fixed in advance.
best = max(chsh({"ab": a*b, "ab'": a*b2, "a'b": a2*b, "a'b'": a2*b2})
           for a in (1, -1) for a2 in (1, -1) for b in (1, -1) for b2 in (1, -1))
print("best fixed strategy:", best)

# Quantum singlet at the optimal angles reaches 2*sqrt(2).
angles = {"a": 0, "a'": math.pi / 2, "b": math.pi / 4, "b'": 3 * math.pi / 4}
e = {f"{x}{y}": -math.cos(angles[x] - angles[y]) for x in ("a", "a'") for y in ("b", "b'")}
print("singlet:", round(chsh(e), 3))

# Signalling: Alice's outcome copies Bob's setting. No quantum effect, yet S = 4.
def signalling(a_setting, b_setting):
    if (a_setting, b_setting) == ("a", "b'"):
        return -1
    return 1
print("direct influence:", chsh({f"{x}{y}": signalling(x, y) for x in ("a", "a'") for y in ("b", "b'")}))
```

Output:

```text
best fixed strategy: 2
singlet: 2.828
direct influence: 4
```

---

## The NOCODE advanced modules

The NOCODE track continues past protocols into six more modules. Their practical cores:

| Module | Practical core | Where it lives now |
|---|---|---|
| **Field theory** | Keep a few anchor concepts stated explicitly and repeat them | [02](02-context-anatomy.md) |
| **Meta-recursion** | Ask the model to critique and improve its own output or prompt | [08](08-cognitive-tools.md#the-self-correction-loop) |
| **Interpretability** | Ask for confidence, sources and reasoning alongside the answer. Treat self-reports as unreliable | [12](12-evaluating-context.md) |
| **Collaboration** | Divide work explicitly between human and model; checkpoint for review | [10](10-tools-and-multi-agent.md) |
| **Cross-modal** | Describe how text, image and data inputs relate before asking for synthesis | [07](07-structured-context.md) |
| **Cross-model** | Write prompts that don't depend on one model's quirks; test on several | [12](12-evaluating-context.md) |

---

## The mental models

The upstream offers five metaphors for thinking about a context window. They are teaching aids, not methods:

| Model | Picture | Useful for |
|---|---|---|
| **Garden** | Context is cultivated: plant (add), prune (remove), weed (fix errors), tend over time | Long-lived system prompts and memory hygiene |
| **Budget** | Tokens are a fixed budget to allocate and spend | Allocation ([03](03-budgeting-the-window.md)). The most directly useful of the five |
| **River** | Context flows; information has a source, a current and tributaries | Pipelines and multi-step flows |
| **Biopsychosocial** | Consider the foundational (facts), the experiential (user's state) and the contextual (social setting) layers | User-facing assistants and tutoring |
| **Alchemy** | Combine ingredients (instructions, examples, data) in the right order to transform them | Prompt assembly and ordering |

Pick whichever helps you explain a design to someone else. Don't design from them.

---

## What to keep

Three ideas from this track survive translation into engineering:

1. **Early framing is sticky.** Get the first turns and the system prompt right, and restart rather than argue a model out of a wrong framing.
2. **Salience is earned by structure and repetition.** If a constraint matters, state it clearly, place it at the edges of the window and restate it at decision points.
3. **Ambiguity is resolved by context, not by the words alone.** When outputs vary unpredictably, look for the underspecified term.

Everything else is vocabulary. If you meet "attractor", "resonance" or "field" in an agent design discussion, ask what the measurable behaviour is, and map it to a chapter above.

---

## Papers behind the track

- Wang et al., *Unveiling Attractor Cycles in Large Language Models: A Dynamical Systems View of Successive Paraphrasing* (2025). [arXiv:2502.15208](https://arxiv.org/abs/2502.15208)
- Agostino et al., *A Quantum Semantic Framework for Natural Language Processing* (2025). [arXiv:2506.10077](https://arxiv.org/abs/2506.10077)
- Yang et al., *Emergent Symbolic Mechanisms Support Abstract Reasoning in LLMs* (ICML 2025). [arXiv:2502.20332](https://arxiv.org/abs/2502.20332) · [OpenReview](https://openreview.net/forum?id=y1SnRPDWx4)

PDFs are in [../sources/](../sources/).

## Pitfalls

- **Treating the metaphor as a method.** Symptom: a design doc says "tune the field's resonance" and no one can name a parameter. Fix: ask what would change in the assembled window, and write that down instead.
- **Reading a CHSH score above 2 as quantum.** Symptom: citing Agostino's S of 1.2-2.8 as proof of a quantum effect. Fix: check the no-signalling assumption, since direct influence alone reaches 4 in the script above.
- **Stretching a narrow result.** Symptom: Yang et al.'s circuit, measured on small ABA and ABB tasks in Llama-3.1 70B at 95%, gets cited as proof that all context behaves symbolically. Fix: cite it for what it tested.
- **Treating paraphrase cycles as design advice.** Symptom: "attractors" are used to justify a prompt pattern. Wang et al.'s 2-cycle concerns repeated paraphrasing. Fix: use it as a warning about iterated rewriting, and nothing more.
- **Dismissing the whole track.** Symptom: you miss its usable points. Fix: keep the three that survive: early framing is sticky, salience comes from structure and repetition, and ambiguity is resolved by context.
- **Using the vocabulary with stakeholders.** Symptom: reviewers can't tell measured results from analogy. Fix: use the plain terms, such as anchoring, repetition and retrieval, as in the tables here.

## Try it

1. Change `signalling` in the worked example so that Alice always outputs 1. What is S, and why?

   <details><summary>Answer</summary>

   `|1 − 1 + 1 + 1| = 2`. A fixed output is a local strategy, so it can't exceed the classical bound.

   </details>

2. Translate into plain engineering terms: "Strengthen the attractor by reinforcing resonance across the field boundary."

   <details><summary>Answer</summary>

   One reasonable version is: "State the key concept early and repeat it in the relevant sections, and control what enters the window." If a claim can't be translated into something testable about the window, it's still only a metaphor.

   </details>

3. Pick one keeper from this appendix and design an eval for it.

   <details><summary>Answer</summary>

   For "early framing is sticky": run the same task with a framing sentence at the start, in the middle, and absent, across enough samples to compare outcomes. Use the position sweep from [12](12-evaluating-context.md#long-context-behaviour), and report the differences together with their setup.

   </details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| Is the semantic field a real mechanism? | It's a metaphor for context behaviour, useful as vocabulary but not as an engineering method. |
| Does a CHSH value above 2 show quantum semantics? | No. Agostino's S of 1.2-2.8 (several runs at 2.3-2.4) breaks the classical bound only if no-signalling holds, and direct influence alone reaches 4. |
| What did Yang et al. show? | A three-stage circuit of abstraction, induction and retrieval heads in Llama-3.1 70B at 95% on small tasks such as ABA and ABB. It supports structure as a mechanism on those tasks, no further. |
| What's a practical takeaway from Wang's paraphrasing result? | Iterated rewriting can fall into a 2-cycle between clusters, so don't assume that repeated summarization converges on the meaning. |
| What do you keep from the track? | That early framing is sticky, salience comes from structure and repetition, and ambiguity gets resolved by context. All three translate into window design choices. |
| A colleague proposes a "resonance score" as an eval metric. How do you respond? | Ask for its definition in measurable terms, and whether it predicts task success better than existing metrics, otherwise I'd stick with fact retention and task success. |

## Next

[03 Harness Engineering](../../03-harness-engineering/README.md): context is what the model sees, and the harness is the code that assembles it across a stateful loop.
