# TypeScript — LLM Fundamentals

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
| `02-structured-output.ts` | Structured JSON via `tool_choice: { type: "tool" }` |
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

- **Model**: `claude-sonnet-4-20250514` throughout.
- **Streaming**: `client.messages.stream()` returns an async iterable of server-sent events; call `.finalMessage()` for the completed message object.
- **Tool use**: define tools with a JSON Schema `input_schema`; use `tool_choice: { type: "tool", name: "..." }` to force a call.
- **Multi-turn**: pass the full `messages` array (user + assistant turns) on each request; the SDK does not manage history automatically.
- **Error handling**: the SDK throws `Anthropic.APIError` for 4xx/5xx responses.
