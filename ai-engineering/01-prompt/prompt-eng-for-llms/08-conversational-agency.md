---
origin: book
source: "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly) — Ch 8: Conversational Agency"
confidence: high
cleaned: 2026-07-29
---

# Ch 8 — Conversational Agency

## Agency defined

*Agency* is an entity's ability to complete tasks and achieve goals in a self-directed,
autonomous manner. A bare chat model has none: it only knows training-time knowledge plus
what the user typed, can't reach "hidden" (private, post-training, or real-time) information,
is unreliable at math, and can't *do* anything — it only talks. *Conversational agency* adds
tool use to the chat loop: the assistant can reach into the world, gather fresh information,
and take real actions, while still presenting a back-and-forth chat experience to the user.

## Tool usage — the API layer

Tool calling is offered as a fine-tuned capability (OpenAI added it June 2023; other vendors
followed). Mechanics:

1. Define real functions (e.g., `get_room_temp()`, `set_room_temp(temp)`).
2. Describe them to the model as JSON schema (`tools=[...]`), each with a `name`,
   `description`, and typed `parameters`.
3. Build an `available_functions` lookup dict so tool calls can be dispatched by name.
4. Loop: send `messages` + `tools` → model returns a message that may contain
   `tool_calls` → for each, parse `function.name`/`function.arguments`, invoke the real
   function, append a `{"role": "tool", "tool_call_id": ..., "content": result}` message →
   send the extended `messages` back to the model. Repeat until the model returns a plain
   assistant message with no tool calls.

The app owns steps 4–5 (invoking, appending); the model only ever proposes calls and
consumes results — it never talks to the real world directly.

## Under the hood: tools are still just document completion

Tool calling is **not** a separate mechanism — like chat itself, it's a fine-tuned model
plus syntactic sugar at the API layer, implemented as ChatML-formatted text. Reconstructed
internal format:

- Tool definitions are injected into the system message as **TypeScript-style type
  declarations** inside a `namespace functions { ... }` block, with comments carrying the
  `description` text — not raw JSON schema.
- TypeScript is used because: (1) richer type vocabulary than JSON schema, (2) doc comments
  attach naturally to both function and arguments, (3) forcing named (not positional)
  arguments makes the model state each argument's name immediately before its value,
  which keeps function calls consistent and reduces mis-assignment.
- A call is emitted as `<|im_start|>assistant to=functions.set_room_temp\n{"temp": 76}<|im_end|>`.
  The `to=functions.X` syntax and JSON argument object are just more predicted tokens.
- Evaluation results come back as a new `tool` role message (`<|im_start|>tool\nDONE<|im_end|>`) —
  a role introduced specifically for feeding tool output back into the transcript. The
  API-level `tool_call_id` is dropped internally once the API has stitched calls to
  responses in order.

**Key insight**: token-by-token, the model is running a chain of classifiers layered on next-token
prediction — at each step it decides: *who speaks next* (forced by the API inserting
`<|im_start|>assistant`) → *tool or plain message?* (`to=functions.` vs `\n`) → *which tool?* →
*which argument next?* → *what value?* (repeat per arg) → *done?* (`}<|im_end|>`). A single
generic next-token predictor implements ~5 specialized, hierarchical decision procedures in
10–20 tokens.

### Reverse-engineering a model's internal prompt (exercise)
Models resist directly dumping their system prompt. Escalating tricks: ask to print text
above the first message → wrap distinctive text in custom tags (e.g., `<LOGGING>...</LOGGING>`)
and ask it to echo the tagged content → give tools unusual names and ask about the
surrounding text → build a dedicated logging tool (models leak more readily through tool
calls than through chat) → ask for base64/ROT13-obfuscated output (bypasses some
refusal training) → feed any partial hints back into the prompt as assistant-voice
comments to bait continuation.

## Guidelines for tool definitions

Two grounding intuitions: (1) what's easier for a human to read is easier for the model;
(2) prompts patterned after training data work best (Little Red Riding Hood principle —
markdown structure, familiar formats).

- **Selecting tools**: limit the tool count — more tools = more confusion. Tools should
  *partition* the domain (cover as much ground as possible) without overlapping in
  purpose. Never paste a full web API into the prompt — describe a simplified version;
  complex parameter lists and responses eat token budget and hurt accuracy.
- **Naming**: meaningful, self-documenting names; camelCase for OpenAI (matches its
  TypeScript framing); avoid unbroken lowercase concatenations (`retrieveemail`) — hard
  to parse.
- **Defining**: as simple as possible while unambiguous — legalese-y definitions overload
  the model's attention. If the tool wraps a public API the model already knows
  (e.g., GitHub's code search), mirror that API's naming/format — GitHub Copilot work
  showed the model could recite their docs back verbatim, and using matching
  argument names/formats reduced confusion.
- **Arguments**: keep few and simple; OpenAI handles all standard JSON schema types
  (string/number/integer/boolean) and `enum`/`default` fine, but as of the Nov-2023
  models, `minItems`, `uniqueItems`, `minimum`, `maximum`, `pattern`, `format`, and
  nested-parameter descriptions are **not** represented in the internal prompt — don't
  rely on them. Avoid long-form text arguments for OpenAI — JSON-escaping newlines/quotes
  is error-prone at length; Anthropic uses XML-tagged arguments instead of JSON, so
  Claude tools tolerate long-form text better.
- **Argument hallucination**: if a value isn't in the conversation, the model invents
  plausible placeholders (`"my-org"`, `"my-repo"`). Mitigate by (1) removing
  app-known arguments from the schema entirely (or supplying a default the app can
  detect and handle), or (2) instructing the model to ask when unsure (not fully
  reliable, improving over time).
- **Tool outputs**: give the model enough in the definition to anticipate output shape;
  free text or structured JSON both work; don't pad outputs with "just in case" content —
  it distracts the model.
- **Tool errors**: surface errors usefully, phrased in terms of *the tool's own contract*
  (not raw internal exception text) — validation errors should tell the model what it did
  wrong so it can retry correctly.
- **Dangerous tools**: never rely on prompt instructions like "confirm with the user
  first" to gate risky actions — models are unreliable and *will* eventually skip the
  check. Instead, let the model freely request any tool call, but intercept
  side-effect-bearing calls in the **application layer** and require explicit user
  sign-off before actually executing them.

## Reasoning: giving the model an internal monologue

Token-by-token generation is a shallow form of reasoning — no mental review, no comparison
of competing hypotheses, just whatever token statistically fits next. Without a monologue,
an initial yes/no answer is an intuitive guess and the "explanation" that follows is
post-hoc rationalization. Multiple techniques inject a monologue before the final answer:

- **Chain of Thought (CoT)** (Wei et al., Jan 2022): few-shot examples showing
  reason-then-answer pairs condition the model to reason before concluding.
  StrategyQA commonsense accuracy: 69.4% → 75.6% (PaLM 540B). GSM8K math word problems:
  ~20% → ~60% solve rate. Also helps symbolic reasoning tasks.
- **Zero-shot CoT** ("Large Language Models are Zero-Shot Reasoners," May 2022): skip
  the curated few-shot examples — just append the cue **"Let's think step-by-step"**
  (PDF p. 16) and the model spontaneously produces reasoning before its answer.
- **Pause tokens** ("Think Before You Speak," Oct 2023): fine-tune the model on a
  meaningless "pause" token; inject ~10 of them after the question before the answer.
  Extra timesteps let earlier-token information integrate more fully into model state —
  analogous to humans stalling with "uh"/"um."

## ReAct: iterative reasoning and acting

ReAct ("ReAct: Synergizing Reasoning and Acting in Language Models," Oct 2022) interleaves
**Thought → Action → Observation** loops, adding tool use to reasoning for multistep,
information-retrieval tasks (e.g., HotpotQA multi-hop questions). Three tools:

- `Search[entity]` — first 5 sentences of the matching Wikipedia page, or similar-entity
  suggestions if no exact match.
- `Lookup[string]` — next sentence in the current passage containing that string.
- `Finish[answer]` — ends the episode with the final answer.

Example trace: Thought 1 (need to search both magazines) → Action 1 `Search[Arthur's
Magazine]` → Observation 1 (started 1844) → Thought 2 (need First for Women next) →
Action 2 `Search[First for Women]` → Observation 2 (started 1989) → Thought 3 (compare
dates, conclude) → Action 3 `Finish[Arthur's Magazine]`. Conditioned via a preamble
describing the three action types, followed by ~6 worked examples.

**Results (Figure 8-1, HotpotQA)**: with only few-shot prompting, ReAct actually
*underperformed* both standard and CoT prompting at every model size — in-prompt examples
alone didn't teach the tool-use + reasoning pattern well enough. But after fine-tuning the
two smaller models on just ~3,000 examples, ReAct jumped to the lead: fine-tuned ReAct on
the 8B model beat standard prompting on the *much larger* 62B model, and fine-tuned 62B
beat standard-prompted 540B. Lesson: reasoning strategy + light fine-tuning can substitute
for raw scale. Acting without reasoning (**Act**, tools but no Thought step) is worse than
ReAct but still beats no tools at all.

Reasoning is even more critical in decision/action domains like **ALFWorld** (simulated
household task agent). Thinking's contributions there: decomposing goals into
subgoal plans, injecting relevant commonsense knowledge, extracting useful detail from
observations, tracking progress, and adjusting plans when exceptions occur. ReAct hits 71%
success in ALFWorld vs. 45% for Act alone.

## Beyond ReAct

- **Plan-and-solve prompting**: front-load an explicit planning step before execution —
  *"Let's first understand the problem and devise a plan to solve the problem. Then,
  let's carry out the plan and solve the problem step-by-step."* (PDF p. 19) No tool usage; closer in
  spirit to zero-shot CoT than to ReAct. Could combine with ReAct's think-act-observe loop.
- **Reflexion**: lets the model review its own output afterward, identify what went wrong,
  and improve on retry — works only in domains with a do-over (e.g., generating code
  against a unit-test suite: run tests, feed failures back into the prompt, retry). Useless
  for irreversible actions (transferring money can't be un-transferred).
- **Branch-solve-merge**: fan out to *N* independent "solver" conversations tackling the
  same problem (via high temperature or distinct assigned perspectives), then feed all N
  solutions to a merging agent that synthesizes a final answer.

## Context for task-based interactions

A conversational agent's full prompt context (Table 8-1) decomposes into:

- **Preamble** — system-message text conditioning overall behavior: rules, tool
  definitions, few-shot examples if needed.
- **Prior conversation** — all previous user/assistant turns up to (not including) the
  current exchange, plus any **artifacts** attached along the way (structured data
  relevant to the conversation, e.g. a flight list).
- **Current exchange** — the user's latest message + any artifacts attached to it (e.g.,
  "the thing they clicked on"), plus whatever tool calls/responses the model generates
  while handling it.
- **Agent response** — the final assistant-voice message; becomes part of prior
  conversation for the next exchange (the intermediate tool traffic does not re-enter the
  next prompt as-is, only the final summary text does, though it's preserved for the
  *current* processing).

## Selecting and organizing context

No universal recipe — depends on domain, model, and data; the answer is to "evaluate,
evaluate, evaluate" (PDF p. 24; more in Ch. 10). Considerations:

- **Which tools?** Drop tools irrelevant to the current conversational state to reduce
  distraction.
- **Which artifacts to include?** Options: include everything (safe but risks confusing
  the model with irrelevant volume); or have the model actively select relevant artifacts
  (more accurate, but adds real implementation complexity).
- **How to present artifacts?** Inline in an XML tag (`<artifact>...</artifact>`) or a
  markdown section (`## Attached Data`); format (JSON/plain text/etc.) doesn't seem to
  matter much empirically — test for your case. If all artifacts originate from tool
  calls, simplest is to not special-case them at all — just keep the tool call/response
  messages in the prior conversation; this also doubles as extra tool-use examples.
- **How much content per artifact?** Never dump a full document. Options: present a
  bulleted summary with pointers like *"for more information, call `details('section 5')`"*
  that the model can invoke to unfurl more detail on demand (proposed, untested by the
  authors); or wire up traditional retrieval/RAG over the large artifact.
- **How far back should prior conversation reach?** Drop content once the topic shifts.
  Heuristics: auto-drop after a period of user inactivity; or train a small, cheap model
  to judge relevance (using a large model for this is overkill — too slow/expensive).

Trade-off is symmetric: too much context confuses the model, burns prompt budget, raises
latency/cost; too little starves it of what it needs.

## Building a conversational agent

Two pieces complete the loop already built via `process_messages` (tool-call handling):

1. **User input** — a simple `input()` prompt is enough to demonstrate the pattern.
2. **`run_conversation`** — wraps `process_messages` in a `while True` loop: take user
   input, append as a `user` message, call `process_messages`, then inspect the last
   message — if it's a tool-response message, `continue` (loop again without new user
   input, since the model still has work to do); if it's an assistant message, print its
   `content`; break out to wait for the next user input only once `tool_calls is None`.

![Figure 8-2. A sequence diagram representing the design of the conversational agent](images/fig-8-2-conversational-agent-sequence.png)

Sequence diagram (Figure 8-2): User → App (appends message) → Model (prompt) → **loop**
[Model requests function call → App parses call → App calls Tool → Tool responds → App
appends tool call+response → App re-prompts Model] until Model returns a plain assistant
message → App appends and returns it to User.

**Worked example** (thermostat agent) demonstrates real emergent behavior: the model
interprets colloquial phrasing ("Golly gee, it's hot in here"), applies common sense
(volunteers that 64°F is "actually quite cool" when the user's premise contradicts sensor
data), respects informal magnitude cues ("LOTS cooler" → sets 50°F, not an extreme like
0°F), and — critically — correctly restores the *original* temperature (64°F) on request
by reasoning over the **prior conversation**, not just the current exchange (transcript
quotes: PDF pp. 29–30). This cross-turn state tracking is the qualitative leap
conversational agency adds over a single `process_messages` call.

## User experience

- Standard chat UI (turn-taking bubbles) is a solved, expected pattern (AIM → Slack →
  ChatGPT) — don't reinvent it.
- Always show a processing spinner while the agent works.
- Surface tool activity distinctly (e.g., a "Tool calls" pill/button on the agent message)
  rather than hiding it — this is genuinely new relative to plain chat and users benefit
  from visibility into background work.
- Let users **inspect** tool call details (name, arguments as an editable webform,
  results) and **modify arguments and resubmit** — regenerating the conversation from
  that point. This is real, practical error-correction UX: if the model calls a tool with
  wrong arguments, the user course-corrects instead of the conversation derailing (Figure
  8-3's HAL example).
- **Any tool call capable of a real-world side effect must gate on explicit user
  authorization** before execution — shown as a distinct confirmation UI surfacing the
  exact arguments (Figure 8-4: an airfare-purchase authorization card showing destination/
  date/time/amount before an "Authorize" button). This is the concrete UI counterpart to
  the "dangerous tools" guidance above — never trust prompt instructions alone to gate risk.
- Give users visibility into which artifacts the agent is currently attending to (e.g., a
  displayed document) so they can ask sharper follow-ups or dismiss a misattributed
  artifact to keep the conversation on track.

## Key takeaways

- Tool calling is not a new model capability — it's fine-tuning plus API-level syntactic
  sugar over the same document-completion mechanism that powers chat; internally it's
  represented as TypeScript-style type declarations and executed as a token-by-token
  hierarchical classification process (speaker → tool-or-not → which tool → which arg →
  which value → done).
- Reasoning must be manufactured, not assumed — models have no native internal monologue,
  so CoT/zero-shot-CoT/pause-tokens/ReAct-style think-act-observe loops are all techniques
  for forcing deliberation before the final answer, and they measurably improve both
  factual QA and decision-making task success.
- Light fine-tuning on reasoning traces can substitute for raw model scale — a fine-tuned
  8B ReAct model outperformed a 540B model using only standard prompting on HotpotQA.
- Tool design principles: partition the domain with few, simple, well-named tools;
  mirror familiar public APIs when possible; never trust in-prompt instructions to gate
  dangerous actions — enforce authorization in the application layer instead.
- Context assembly for an agent = preamble + prior conversation (with artifacts) + current
  exchange (with artifacts and tool traffic); no fixed recipe exists for sizing/pruning it
  — treat it as an empirical, per-domain tuning problem.
- Conversational agents still depend on a human in the loop for course correction; the
  next chapter moves to LLM-based *workflows* that decompose goals into directed,
  non-conversational task sequences.
