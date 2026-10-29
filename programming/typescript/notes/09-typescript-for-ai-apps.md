---
origin: curated
sources:
  - "Anthropic TypeScript SDK — https://github.com/anthropics/anthropic-sdk-typescript (MIT)"
  - "Claude API docs: Messages, Streaming, Tool use, Structured outputs — https://platform.claude.com/docs"
concepts: [anthropic-sdk, llm-streaming, tool-use, structured-output, content-blocks, stop-reasons, refusal-fallback]
cleaned: 2026-10-29
---
# 9 — TypeScript for AI Apps

> An LLM API is an untyped, slow and occasionally failing remote call. Everything from notes 03–08 applies: discriminated unions for content blocks, async for streaming, zod for tool inputs and structured output.

---

## A request

```ts
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();   // reads ANTHROPIC_API_KEY
const message = await client.messages.create({
  model: 'claude-opus-5-5',
  max_tokens: 16000,
  thinking: { type: 'adaptive' },             // the model decides how much to think
  messages: [{ role: 'user', content: 'Explain structural typing in one paragraph.' }],
});
```

The SDK exports types for everything: `Anthropic.MessageParam`, `Anthropic.Message`, `Anthropic.Tool` and so on. Use them rather than redefining the shapes.

## Content blocks are a discriminated union

`message.content` is an array of blocks: `text`, `thinking`, `tool_use` and others. Narrow them by `type` ([note 03](03-unions-and-narrowing.md)):

```ts
const text = message.content
  .filter((b): b is Anthropic.TextBlock => b.type === 'text')
  .map((b) => b.text)
  .join('\n');
```

Never assume `content[0]` is text. With thinking enabled, the first block often isn't.

## `stop_reason` tells you what to do next

| `stop_reason` | Meaning | Your loop |
|---|---|---|
| `end_turn` | Finished | Done |
| `tool_use` | Wants tools run | Run them and send back `tool_result` blocks |
| `max_tokens` | Cut off | Raise `max_tokens` or continue. Don't trust a truncated tool call |
| `pause_turn` | A server tool paused a long turn | Send the turn back to continue |
| `refusal` | Declined by a safety classifier | Handle it before reading `content` (see fallbacks below) |

Write it as an exhaustive `switch` with a `default` branch, because the API adds new values over time.

## Streaming

```ts
const stream = client.messages.stream({ model: 'claude-opus-5-5', max_tokens: 16000, messages });
stream.on('text', (delta) => process.stdout.write(delta));
const final = await stream.finalMessage();   // the complete Message, same type as create()
```

Stream any request with long input or long output. It shows progress and avoids HTTP timeouts. `finalMessage()` handles completion, errors and aborts. Don't wrap the events in your own `new Promise`.

## Tool use

A tool is a name, a description and a JSON Schema for its input. The model returns `tool_use` blocks, your code runs them, and you reply with `tool_result` blocks that carry the same `tool_use_id`. Repeat until `stop_reason` is `end_turn`.

The SDK's **tool runner** runs that loop for you, and `betaZodTool` validates each input against a zod schema before your `run` function sees it:

```ts
import { betaZodTool } from '@anthropic-ai/sdk/helpers/beta/zod';

const getStock = betaZodTool({
  name: 'get_stock',
  description: 'Units in stock for a product SKU.',
  inputSchema: z.object({ sku: z.string() }),
  run: async ({ sku }) => JSON.stringify(await db.stock(sku)),   // sku: string, already validated
});
const final = await client.beta.messages.toolRunner({ model: 'claude-opus-5-5', max_tokens: 16000, tools: [getStock], messages });
```

Tool inputs are model output, which makes them untrusted. Validate them, confine file paths, and gate anything destructive. Write a manual loop only when you need control the runner doesn't give you. The exercise builds the pieces of one.

## Structured output

To get JSON that matches a schema, rather than prose you have to parse:

```ts
import { betaZodOutputFormat } from '@anthropic-ai/sdk/helpers/beta/zod';

const res = await client.beta.messages.parse({
  model: 'claude-opus-5-5',
  max_tokens: 16000,
  messages,
  output_config: { format: betaZodOutputFormat(Review) },
});
res.parsed_output;   // z.infer<typeof Review> | null
```

The response is constrained to the schema. Still check `parsed_output` for `null`, and check for `stop_reason: 'refusal'`.

## Errors, retries and refusals

- The SDK retries connection errors, 429s and 5xx responses itself (`maxRetries`, default 2). Catch the typed errors: `Anthropic.RateLimitError`, `Anthropic.APIError` (which has `.status`).
- Timeouts are in **milliseconds**: `new Anthropic({ timeout: 60_000 })`. Pass an `AbortSignal` to cancel a request.
- **Refusal fallback.** Safety classifiers occasionally decline even benign requests. Opting into `fallbacks: 'default'` (beta header `server-side-fallback-2026-07-01`) re-runs a declined request on Anthropic's recommended fallback model inside the same call, so a false positive doesn't become an outage. The example below turns it on.

## Rules of thumb

- Keep prompt-building, block parsing and the loop logic as **pure functions** that you can test without the API. Only a thin layer should make network calls.
- Log `usage` (input and output tokens) on every response. Cost bugs are invisible otherwise.
- Pin the model ID in one config value, not scattered through the code.

---

## Exercises

- [`practice/exercises/09-ai-helpers.ts`](../practice/exercises/09-ai-helpers.ts): `textOf`, `toolUses`, `runToolCalls` (errors become `is_error` results) and `nextStep` from `stop_reason`. It is tested offline against fake responses. From `practice/`, check with `npm test`.
- [`practice/examples/claude.ts`](../practice/examples/claude.ts): streaming, structured output and a tool-runner loop against the real API. Run `node examples/claude.ts` with `ANTHROPIC_API_KEY` set. It costs a few cents.
