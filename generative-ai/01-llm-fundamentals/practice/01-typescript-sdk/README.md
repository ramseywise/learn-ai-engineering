# Lab 1 — Calling Claude from TypeScript

> Concepts: [06 — Calling models from code](../../notes/13-calling-models-from-code.md). Run label: needs Node, `@anthropic-ai/sdk`, `tsx` and `ANTHROPIC_API_KEY`; each run makes a few paid API calls.

Runnable TypeScript examples using the [Anthropic SDK](https://github.com/anthropic-ai/anthropic-sdk-node). Each file is self-contained and covers one core pattern.

## Setup

```bash
npm install @anthropic-ai/sdk tsx typescript
export ANTHROPIC_API_KEY=sk-ant-...
```

No `tsconfig.json` is required — `tsx` compiles on the fly.

## Examples

| File | Pattern |
|------|---------|
| `01-api-call.ts` | Basic message creation, streaming, error handling |
| `02-structured-output.ts` | Structured JSON via a `strict` tool under `tool_choice: { type: "auto" }` |
| `03-function-calling.ts` | Multi-tool agentic loop with tool dispatch |
| `04-multi-turn.ts` | Conversation history management; interactive REPL + scripted demo |

## Running

```bash
npx tsx 01-api-call.ts
npx tsx 02-structured-output.ts
npx tsx 03-function-calling.ts
npx tsx 04-multi-turn.ts        # scripted demo when stdin is not a TTY
```

## Key SDK patterns

- **Model**: `claude-opus-5-5` throughout. Replace it with a current model id if this one has been retired.
- **Streaming**: `client.messages.stream()` returns an async iterable of server-sent events; call `.finalMessage()` for the completed message object.
- **Tool use**: define tools with a JSON Schema `input_schema`. Forcing a call with `tool_choice: { type: "tool" }` returns a 400 on current models, so use `auto`, `strict: true`, and a prompt that names the tool, then check that the `tool_use` block is there.
- **Multi-turn**: pass the full `messages` array (user + assistant turns) on each request; the SDK does not manage history automatically.
- **Error handling**: the SDK throws `Anthropic.APIError` for 4xx/5xx responses.
