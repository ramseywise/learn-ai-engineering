---
origin: synthesis
sources:
  - "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly 2024) — Ch 7"
  - https://www.promptingguide.ai/introduction/settings
  - https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
  - https://arxiv.org/abs/2408.02442
confidence: high
cleaned: 2026-10-31
---
# 4 — Controlling Output

> Getting a completion your code can use: the right shape, the right length, a clean place to stop, and a signal of how confident the model was.

---

## Anatomy of the ideal completion

```mermaid
flowchart LR
    P["Preamble<br/>boilerplate · reasoning · fluff"] --> S["The solution"]
    S --> E["Recognizable end<br/>closing tag · next header · stop sequence"]
    E -.->|"stop here"| F["Fluffy postscript<br/>never generated"]
    style S fill:#1E3A5F,color:#fff
    style E fill:#D4621A,color:#fff
    style F fill:#CBD5E1
```

Every token *before* the solution costs latency and money. Nothing after the recognizable end matters if you stop generating there. So the job is to **shape the preamble** and **make the end detectable**.

| Preamble type | What to do |
|---|---|
| **Structural boilerplate** (an opening `{`, a heading) | Put it in the *prompt*. Cheaper, and it guarantees the format |
| **Reasoning** | Let it run long — this is CoT, and it buys correctness ([03](03-core-techniques.md#chain-of-thought)) |
| **Fluff** (disclaimers, "Great question!") | Mostly an RLHF habit, though models without RLHF occasionally do it too. Few-shot examples that skip the intro, or an explicit "answer directly" instruction. Failing that, give it a slot: `1. [answer] 2. [caveats] 3. [background]`, then parse slot 1. A slot doesn't always kill the intro (the book shows ChatGPT adding one against explicit instructions), so parse defensively |

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
- **Temperature 0 is not deterministic** in practice (batching and floating-point effects). The book reports computed probabilities moving by several percentage points between reruns, enough to change which token is on top. Tests need to tolerate variation or mock the model.
- **The book's temperature regimes:** 0 when correctness matters most; 0.1–0.4 for a few alternatives or a slightly more colourful single answer; 0.5–0.7 for many (10+) independent solutions; 1 to mirror the training distribution. Above 1, errors compound over long generations, because temperature acts only at the last step: the model reads its own earlier slips as a pattern and imitates them.
- **Reasoning models often fix or ignore these** — some don't accept temperature/top_p at all ([07](07-prompting-reasoning-models.md)).
- Provider support differs — penalties and logprobs are OpenAI-style features many APIs don't expose.

**Best-of-n:** generate n completions at moderate temperature (most APIs take an `n` parameter; OpenAI's maxed out at 128, and the book notes n = 128 doesn't take much longer than n = 1, since the completions run in parallel) and keep the one with the best logprob score ([below](#logprobs-reading-confidence)). The book's rule of thumb, which it calls "completely unscientific": `temperature ≈ sqrt(n) / 10`, so 0.2 for n = 4. At temperature 0, the n completions are identical.

**Beam search** is the decoding-side cousin: instead of committing token by token, it keeps several candidate continuations alive and looks a few tokens ahead so the model doesn't paint itself into a corner. Output is more globally coherent, but compute is much higher, so hosted APIs rarely expose it. Best-of-n is the version you control.

---

## Recognizable start and end

Decide up front how your parser will find the answer.

| Structure | Start | End | Plain substring stop? |
|---|---|---|---|
| Markdown section | the expected header | the next header (`\n#`) | Yes |
| Fenced code | ` ```lang\n ` | `\n```\n` | Yes |
| Numbered list, first item | `1.` | `\n2.` | Yes |
| XML | `<answer>` | `</answer>` | Yes |
| JSON string value | `"key": "` | the next unescaped `"` | No — a plain `"` stop would fire on `\"` |
| Braced code (Java), whole JSON object | `{` | matching closing brace | No — count braces while streaming, or parse |
| YAML / indented languages (Python) | the key or `def` line | first line back at the starting indent | Partly — `\n` + a top-level token works if you know what comes next |

Stop-sequence tips:
- **Prefer stop sequences to streaming-and-cancel.** Stopping server-side wastes nothing; cancelling over the network always wastes some tokens. More APIs accept stops than support cancelling a stream. But a stop is a fixed string, so for the "No" rows above (a matching brace, a dedent) streaming and cancelling in your own code is the only way to end early. Combine the two: add the common fixed-string endings as stops and catch the rest while streaming.
- **Lead with a newline** (`\n#`, not `#`) so a `#` in a comment or phone number doesn't trigger a stop.
- Add *likely* continuations as extra stops — after a Python class, `\nclass`, `\ndef` and `\nif` are safe because the class's own methods are indented.
- **Use domain knowledge to sharpen stops.** If you know what *follows* the answer in this kind of document (the next section's header, the next field), stop on exactly that.

```python
resp = client.completions.create(          # legacy completions endpoint; chat APIs take `stop` too
    model=MODEL,
    prompt=prompt + "\n## Summary\n",      # boilerplate pushed into the prompt
    stop=["\n#"],                          # end at the next markdown header
    max_tokens=300,
    logprobs=1,                            # per-token logprobs, where the provider allows it
)
text = resp.choices[0].text
if resp.choices[0].finish_reason == "length":   # hit max_tokens, not the stop
    ...                                          # truncated: retry or discard
```

---

## Structured output

From weakest to strongest guarantee. Climb only as far as you need:

```mermaid
flowchart LR
    A[Ask] --> B[Show] --> C[Fence] --> D[Prefill] --> E[Constrain] --> F[Tool schema]
```

1. **Ask for it** — "Return JSON with keys `name`, `date`." Fine for prototypes, breaks at scale.
2. **Show it** — a schema or one complete example in the prompt. Matching the format of the prompt to the format you want also helps: markdown in, markdown out; prose in, prose out.
3. **Fence it** — XML tags (`<answer>…</answer>`) give an unambiguous parse target even inside a chatty reply.
4. **Prefill it** — start the assistant turn with `{` or `<answer>` so the model can only continue the structure. This is the book's "push boilerplate into the prompt" in chat form. **Some newer models no longer accept a prefilled last assistant turn** — check your model's docs, and use options 5–6 instead.
5. **Constrain it** — JSON mode or schema-constrained decoding (OpenAI Structured Outputs, Anthropic structured outputs, `strict` tool schemas). The decoder can't emit tokens that break the schema.
6. **Route it through a tool** — define a tool whose parameters *are* your output schema and require the model to call it ([05](05-tools-and-function-calling.md)).

A schema guarantees **shape, not truth**: a valid JSON object can still hold hallucinated values. Validate the content as well ([09](09-evaluating-prompts.md)).

Format can also cost accuracy, through two routes. The first is **key order**. Tam et al. found that in JSON mode, "100% of GPT 3.5 Turbo JSON-mode responses placed the 'answer' key before the 'reason' key, resulting in zero-shot direct answering instead of zero-shot chain-of-thought reasoning." The model committed to an answer before it had reasoned. The second is **schema strictness**. On GSM8K, Claude 3 Haiku scored 86.99% when told to "reply in JSON" and 23.44% when the prompt also spelled out a `{"reason": …, "answer": …}` schema. The losses were not parse failures: LLaMA 3 8B failed to parse only 0.148% of the time on the Last Letter task in JSON, yet still lost 38.15 points to free text. The effect reversed on classification. Answering in JSON instead of free text lifted Gemini 1.5 Flash on DDXPlus (medical diagnosis) from 41.6% to 60.3%, which the authors attribute to the format narrowing the possible answers. The paper tested only small and mid-size 2024 models (GPT-3.5 Turbo, Claude 3 Haiku, Gemini 1.5 Flash, LLaMA 3 8B, Gemma 2 9B) on simple schemas ([arXiv:2408.02442](https://arxiv.org/abs/2408.02442) (Tam et al., 2024-08)). For reasoning steps, put the reasoning field before the answer field, or let the model answer in prose and convert it to JSON in a second call. The paper's "NL-to-Format" setup did that and scored about the same as free text.

Controlling *style* (Anthropic's guidance):
- Say what to do, not what not to do: "Write in flowing prose paragraphs," not "Don't use markdown."
- Explain why a constraint exists — a text-to-speech destination, a fixed-width display.
- Ask explicitly for the level of effort you want. Recent models do what's asked rather than going "above and beyond" unless prompted to.

---

## Logprobs: reading confidence

A logprob is the log-probability of each emitted token (0 = certain; `exp()` converts it to a probability: logprobs of −0.405 for "Yes" and −1.099 for "No" mean about 67% and 33%). The API can also return the top alternatives the model considered at each position, at no extra compute, since the model computes the full distribution anyway. Where the API exposes them — some providers disable them, the book says for fear of being reverse-engineered — they're your best instrument. If you'll need them, that constrains your model choice.

Reading the numbers: the chosen token usually sits between −2 and 0, single-digit negatives are normal for free text; double-digit negatives mean something odd happened. Tokens near the *start* of a text run lower because the model has less context to go on. Expect jitter of about ±1 between identical calls (the same nondeterminism as temperature 0).

- **Quality score.** Average rather than sum: a summed logprob falls with length and with harmless paraphrase ("for example" vs. "for instance" can halve a probability without lowering quality). The plain mean of the token logprobs is a good default when you can't experiment. Building Copilot, Ziegler found the mean of the *probabilities* (not logprobs) of the *first* tokens, `(exp(lp_1) + … + exp(lp_n)) / n`, predictive of overall quality. Use it to gate: show only high-confidence suggestions, warn on low ones, retry, add context, or escalate to a stronger model. The book's warning: **don't be like Clippy** — interrupting users with low-confidence output costs more trust than staying quiet.
- **Classification.** Use a format like `1. [positive | negative | neutral]` so the decision is the first token after a known start, then read the probabilities of each label.
  - **Prefix-collision pitfall:** in the book's region classifier (real gpt-3.5-turbo-instruct probabilities), the first token was `North` at 55% and `Europe` at 44%. After `North`, `-East` took 76% and `America` 23%, so Northeast Asia totals 55% × 76% ≈ 42% and North America about 13%. Europe, at 44%, is the single most likely label, but greedy decoding commits to `North` first because two labels pool their mass there, then picks `-East`, and outputs "Northeast Asia". **Give every label a distinct first token.**

    ![Prefix collision: North 55% vs. Europe 44%, then -East 76% vs. America 23%](../sources/images/berryman-prompt-engineering-for-llms-fig7-5.png)
    *Image Source: Berryman & Ziegler (2024), Fig. 7-5*
  - **Calibration:** the model's 50% isn't your threshold. In the book's example, an app blocks emails the model judges unprofessional, and it blocks too many. Shift per-label logprobs by constants (add 0.3 to "Yes" before comparing with "No", so the model must be clearly surer of "No" to block). Find the constants by experiment or by minimizing cross-entropy on labeled data, as in logistic regression. **Logit bias** applies the same shift at generation time where available.
- **Prompt debugging.** With `echo=true` (where supported), logprobs on the *prompt* flag surprising tokens, even with zero completion tokens requested. In the book's test, the typo "complution" tokenized as `compl` + `ution` and dipped below −13. The same signal marks passages of high information density, which you can point the app's or the user's attention to.

---

## Choosing the model

The trade-offs, in rough order: **intelligence → speed → cost → ease of use → features** (tool use, logprobs, vision, context length) **→ special requirements** (open weights, data residency). Tightening one narrows the rest; cheap and very smart don't coexist.

- Pick the smallest model that reliably does the task. Cost matters at volume: a solo project making one request a day can splurge on a premium model, while high-volume simple requests want a small one.
- Match the model to the step, not the app: a small fast model for autocomplete, classification or routing; a frontier model for multistep reasoning; an open-weight model when data can't leave your infrastructure or you need logprobs the API hides.
- Put an abstraction layer between your code and the provider (for example [LiteLLM](https://docs.litellm.ai/)).
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

- **LoRA** freezes the base weights and trains small low-rank "diff" matrices. They're cheap to store, so one deployment can serve many LoRAs, one per customer or task. LoRA doesn't teach new tricks; it teaches *which* existing ones to use. It's good at shifting *priors*. In the book's example, a European travel app can bake "the customer is European" into the weights instead of stating it in every prompt. Trained on outcome data, it also picks up priors nobody wrote down: budget-conscious users reject "Monaco" but book after "Prague" suggestions.
- **Data.** Training documents should show successful interactions: factually correct, using only the background you want learned, in the target format. Sources: write them, hire contractors, synthesize them ([11](11-applications.md#synthetic-data-generation)), or mine telemetry for successes (accepted suggestions, likes) or logs of humans doing the task you're automating. Whether you can get them decides whether fine-tuning is worth it. **Loss masking**, where the framework supports it, trains only on the answer part of each document, not on the prompt part.
- **Trade-off.** Fine-tuning usually weakens the model on generic documents while sharpening it on yours.
- **Soft prompting** uses gradient descent over a few dozen example outputs to find an input *embedding* that reliably puts the model in the right "state of mind": a prompt made of vectors instead of words. It's the cheapest and fastest option, but many frameworks don't offer it.

![Should you fine-tune? A decision flow](../sources/images/berryman-prompt-engineering-for-llms-fig7-8.png)
*Image Source: Berryman & Ziegler (2024), Fig. 7-8*

Reach for it when the static part of your prompt is long, stable, and still not followed reliably — or when you have outcome data encoding preferences you can't articulate. The payoff: after continued pre-training or LoRA you can typically **drop the static context entirely** — instructions and examples now live in the weights, so prompts get shorter, cheaper and faster. Then **make the prompt look like the start of your fine-tuning documents**. If it resembles pre-training data instead, the model follows the old path (a modified Little Red Riding Hood principle).

---

## Go deeper

- Book (PDF): [Ch 7](../sources/prompt-eng-for-llms/reading/07-taming-the-model.pdf) (preamble types, logprobs, calibration, model choice, fine-tuning) · [Ch 2](../sources/prompt-eng-for-llms/reading/02-understanding-llms.pdf) (sampling, beam search)
- Vendor docs on structured outputs and sampling: [references.md](../README.md#vendor-guides)

---

→ Next: [05-tools-and-function-calling.md](05-tools-and-function-calling.md) — giving the model actions.
