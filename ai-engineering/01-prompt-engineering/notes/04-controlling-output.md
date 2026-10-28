---
origin: synthesis
sources:
  - "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly 2024) — Ch 7"
  - https://www.promptingguide.ai/introduction/settings
  - https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
confidence: high
cleaned: 2026-10-28
---
# 4 — Controlling Output

> Getting a completion your code can use: the right shape, the right length, a clean place to stop, and a signal of how confident the model was.

---

## Anatomy of the ideal completion

```
[preamble] → [the solution] → [recognizable end] → [fluffy postscript]
```

Every token *before* the solution costs latency and money. Nothing after the recognizable end matters if you stop generating there. So the job is to **shape the preamble** and **make the end detectable**.

| Preamble type | What to do |
|---|---|
| **Structural boilerplate** (an opening `{`, a heading) | Put it in the *prompt*. Cheaper, and it guarantees the format |
| **Reasoning** | Let it run long — this is CoT, and it buys correctness ([03](03-core-techniques.md#chain-of-thought)) |
| **Fluff** (disclaimers, "Great question!") | Don't fight it; give it a slot: `1. [answer] 2. [caveats] 3. [background]`, then parse slot 1 |

---

## Sampling parameters

| Parameter | Effect | Typical use |
|---|---|---|
| `temperature` | Flattens (high) or sharpens (low) the next-token distribution. 0 ≈ always the top token | Low for extraction, classification, factual QA. Higher for brainstorming and creative writing |
| `top_p` (nucleus) | Sample only from the smallest set of tokens whose probability mass reaches p | Low = conservative. **Tune temperature *or* top_p, not both** |
| `max_tokens` | Hard cap on output length | Cost and latency control. A cut-off is not a stop — check the stop reason |
| `stop` | Strings that end generation server-side | The cheapest way to end on your recognizable end |
| `frequency_penalty` | Penalty grows with how often a token has appeared | Reduces word-level repetition |
| `presence_penalty` | Flat penalty on any token that has appeared | Pushes toward new topics. **Tune one penalty, not both** |

Caveats:
- **Temperature 0 is not deterministic** in practice (batching and floating-point effects). Tests need to tolerate variation or mock the model.
- **Reasoning models often fix or ignore these** — some don't accept temperature/top_p at all ([07](07-prompting-reasoning-models.md)).
- Provider support differs — penalties and logprobs are OpenAI-style features many APIs don't expose.

**Best-of-n:** generate n completions at moderate temperature and keep the best-scoring one. Rule of thumb from the book: `temperature ≈ sqrt(n) / 10`. At temperature 0, the n completions are identical.

---

## Recognizable start and end

Decide up front how your parser will find the answer.

| Structure | Start | End | Plain substring stop? |
|---|---|---|---|
| Markdown section | the expected header | the next header (`\n#`) | Yes |
| Fenced code | ` ```lang\n ` | `\n```\n` | Yes |
| Numbered list, first item | `1.` | `\n2.` | Yes |
| XML | `<answer>` | `</answer>` | Yes |
| JSON / YAML / braced code | key or `{` | matching brace or dedent | No — parse it |

Stop-sequence tips:
- **Prefer stop sequences to streaming-and-cancel.** Stopping server-side wastes nothing; cancelling over the network always wastes some tokens.
- **Lead with a newline** (`\n#`, not `#`) so a `#` in a comment or phone number doesn't trigger a stop.
- Add *likely* continuations as extra stops — after a Python function, `\ndef` and `\nclass` are safe because method bodies are indented.

---

## Structured output

From weakest to strongest guarantee:

1. **Ask for it** — "Return JSON with keys `name`, `date`." Fine for prototypes, breaks at scale.
2. **Show it** — a schema or one complete example in the prompt. Matching the format of the prompt to the format you want also helps: markdown in, markdown out; prose in, prose out.
3. **Fence it** — XML tags (`<answer>…</answer>`) give an unambiguous parse target even inside a chatty reply.
4. **Prefill it** — start the assistant turn with `{` or `<answer>` so the model can only continue the structure. This is the book's "push boilerplate into the prompt" in chat form. **Some newer models no longer accept a prefilled last assistant turn** — check your model's docs, and use options 5–6 instead.
5. **Constrain it** — JSON mode or schema-constrained decoding (OpenAI Structured Outputs, Anthropic structured outputs, `strict` tool schemas). The decoder can't emit tokens that break the schema.
6. **Route it through a tool** — define a tool whose parameters *are* your output schema and require the model to call it ([05](05-tools-and-function-calling.md)).

A schema guarantees **shape, not truth**: a valid JSON object can still hold hallucinated values. Validate the content as well ([09](09-evaluating-prompts.md)).

Controlling *style* (Anthropic's guidance):
- Say what to do, not what not to do: "Write in flowing prose paragraphs," not "Don't use markdown."
- Explain why a constraint exists — a text-to-speech destination, a fixed-width display.
- Ask explicitly for the level of effort you want. Recent models do what's asked rather than going "above and beyond" unless prompted to.

---

## Logprobs: reading confidence

A logprob is the log-probability of each emitted token (0 = certain; `exp()` converts it to a probability). Where the API exposes them, they're your best instrument:

- **Quality score.** Average token probability over the completion (or its first tokens — what Copilot found most predictive). Use it to gate: show only high-confidence suggestions, warn on low ones, retry, add context, or escalate to a stronger model.
- **Classification.** Use a format like `1. [positive | negative | neutral]` so the decision is the first token after a known start, then read the probabilities of each label.
  - **Prefix-collision pitfall:** "North America" and "Northeast Asia" share the first token `North`, so their probabilities add up and can beat a better answer ("Europe") on the first token. **Give every label a distinct first token.**
  - **Calibration:** the model's 50% isn't your threshold. Shift per-label logprobs by constants fitted on labeled data, or use **logit bias** where available.
- **Prompt debugging.** With `echo=true` (where supported), logprobs on the *prompt* flag surprising tokens: typos and odd phrasing show up as deep dips, below roughly −13.

---

## Choosing the model

The trade-offs, in rough order: **intelligence → speed → cost → ease of use → features** (tool use, logprobs, vision, context length) **→ special requirements** (open weights, data residency). Tightening one narrows the rest; cheap and very smart don't coexist.

- Put an abstraction layer between your code and the provider ([notebooks/pe-litellm-intro.ipynb](../notebooks/pe-litellm-intro.ipynb)).
- Prototype on a slightly bigger model than you think you can afford. Prices fall, and your prompts will already be tuned for it.
- A prompt tuned for one model is not portable. Re-run your evals when you switch ([09](09-evaluating-prompts.md)).

---

## When prompting isn't enough: fine-tuning

Fine-tuning is prompt engineering by other means — moving what's in the prompt into the weights.

| Approach | Learns | Needs | Time |
|---|---|---|---|
| Full fine-tuning / continued pre-training | New facts, a new domain | Tens of thousands of examples | Weeks–months |
| LoRA (parameter-efficient) | *Which* existing behaviors to use; formats; priors | Hundreds–thousands | Days |
| Soft prompting | What a static prompt would say | Hundreds | Hours |

Reach for it when the static part of your prompt is long, stable, and still not followed reliably — or when you have outcome data encoding preferences you can't articulate. After fine-tuning, **make the prompt look like the start of your fine-tuning documents**. If it resembles pre-training data instead, the model follows the old path (a modified Little Red Riding Hood principle).

---

## Go deeper

- Book: [Ch 7](../sources/prompt-eng-for-llms/07-taming-the-model.md) (preamble types, logprobs, calibration, model choice, fine-tuning)
- Vendor docs on structured outputs and sampling: [references.md](../README.md#vendor-guides)
- Runnable: [notebooks/pe-chatgpt-intro.ipynb](../notebooks/pe-chatgpt-intro.ipynb) (parameters) · [notebooks/pe-mixtral-introduction.ipynb](../notebooks/pe-mixtral-introduction.ipynb) (open-weight model)

---

→ Next: [05-tools-and-function-calling.md](05-tools-and-function-calling.md) — giving the model actions.
