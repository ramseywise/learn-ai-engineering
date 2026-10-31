---
origin: synthesis
sources:
  - generative-ai/01-llm-fundamentals/practice/01-typescript-sdk/
  - https://github.com/anthropics/anthropic-sdk-typescript
  - https://docs.anthropic.com/en/api/messages
confidence: high
cleaned: 2026-10-31
---

# 6 — Calling Models from Code

> Four patterns cover almost every application: one request, a stream, a forced tool call for structured output, and a loop that feeds tool results back. The [TypeScript lab](../practice/01-typescript-sdk/) has one runnable file per pattern.

---

## The request shape

Every Messages API call is the same object. Learn its fields once:

| Field | Meaning |
|---|---|
| `model` | Model id. Pin it; ids are retired over time. The lab uses `claude-sonnet-4-20250514`; swap in a current id from the models page |
| `max_tokens` | Hard cap on output tokens. Hitting it sets `stop_reason: "max_tokens"` |
| `system` | Instructions for the whole conversation (direction, persona, rules: [note 03](03-prompting-fundamentals.md)) |
| `messages` | Alternating `user` / `assistant` turns. The API is stateless: you send the full history every time |
| `tools`, `tool_choice` | Tool definitions (JSON Schema) and whether the model must, may or must not call one |
| `temperature` etc. | Decoding settings ([note 01](01-how-llms-work.md#decoding)) |

The response's `content` is an **array of blocks** (`text`, `tool_use`, `thinking`), not a string. `stop_reason` says why generation ended: `end_turn`, `max_tokens`, `stop_sequence` or `tool_use`. `usage` reports input and output tokens, which is your cost.

---

## Pattern 1: one request ([`01-api-call.ts`](../practice/01-typescript-sdk/01-api-call.ts))

```ts
const message = await client.messages.create({
  model, max_tokens: 256,
  messages: [{ role: "user", content: "What is a large language model?" }],
});
const text = message.content.filter(b => b.type === "text").map(b => b.text).join("");
```

The file also shows deliberately hitting `max_tokens: 1` so you can see a truncated `stop_reason`, and catching `Anthropic.APIError` for 4xx/5xx responses. Always check `stop_reason` before trusting the output: a truncated JSON object parses as an error, a truncated sentence passes silently.

## Pattern 2: streaming (same file)

`client.messages.stream()` returns an async iterable of server-sent events; print text deltas as they arrive and call `.finalMessage()` for the assembled message and usage. Stream anything a person waits for. Time-to-first-token matters more to perceived speed than total time.

## Pattern 3: structured output via a forced tool ([`02-structured-output.ts`](../practice/01-typescript-sdk/02-structured-output.ts))

Define one tool whose `input_schema` is the shape you want, then force it:

```ts
tools: [{ name: "record_book_review", description: "...", input_schema: { type: "object", properties: {...}, required: [...] } }],
tool_choice: { type: "tool", name: "record_book_review" },
```

The answer arrives as the `input` of a `tool_use` block, already parsed. This is the API-level form of "specify format" and the mechanism behind LangChain's `with_structured_output` ([note 04](04-langchain-basics.md)). Validate it anyway (zod, or a JSON Schema validator); schema adherence is strong but enum and range constraints are worth checking.

## Pattern 4: the tool loop ([`03-function-calling.ts`](../practice/01-typescript-sdk/03-function-calling.ts))

```
loop:
  response = create(messages, tools)
  if stop_reason == "end_turn" or no tool_use blocks: print text, stop
  messages += assistant turn (all of response.content, including tool_use blocks)
  results  = run each tool_use → tool_result {tool_use_id, content}
  messages += one user turn containing all tool_result blocks
```

Three details the lab gets right and hand-rolled loops often get wrong:

1. Append the assistant's **entire** content array, not just its text; the API needs the `tool_use` blocks to match results to calls.
2. Return **all** results for a turn in **one** user message, each with its `tool_use_id`. The model may call several tools in parallel.
3. Put a cap on iterations in production (the lab loops until `end_turn`). A model that keeps calling tools is a cost incident.

This loop is the seed of every agent in [03-agentic-foundations](../../03-agentic-foundations/README.md) and of the loop discipline in [ai-engineering/04-loop-engineering](../../../ai-engineering/04-loop-engineering/README.md).

## Pattern 5: conversation state ([`04-multi-turn.ts`](../practice/01-typescript-sdk/04-multi-turn.ts))

The model remembers nothing between calls. A chat is an array you append to: user turn, assistant turn, user turn… The lab runs as an interactive REPL, or a scripted demo when stdin is not a TTY. Once history grows, you decide what to keep, summarize or drop; that decision is [context engineering](../../../ai-engineering/02-context-engineering/README.md).

---

## Production habits

| Habit | Why |
|---|---|
| Read the key from the environment (`ANTHROPIC_API_KEY`), never from source | The SDK does this by default |
| Retry 429 and 5xx with backoff; do not retry 400 | The SDK retries some errors automatically; know which |
| Log `usage` per call | Cost and context growth show up here first |
| Set a timeout and an iteration cap on tool loops | Bounds worst-case latency and spend |
| Pin the model id; test before changing it | Behaviour shifts between versions |
| Cache long, stable prefixes (system prompt, tool definitions) | Prompt caching cuts cost and latency on repeated prefixes; see [ai-engineering/02-context-engineering](../../../ai-engineering/02-context-engineering/README.md) |

Depth on tool design and function calling: [05 — Tools and function calling](../../../ai-engineering/01-prompt-engineering/notes/05-tools-and-function-calling.md). Output control: [04 — Controlling output](../../../ai-engineering/01-prompt-engineering/notes/04-controlling-output.md).

---

**Next pillar:** [02-rag-retrieval](../../02-rag-retrieval/README.md) gives the model knowledge it was not trained on.
