# Lab: a context budgeter

Language: TypeScript. Supports [Budgeting the window](../../notes/03-budgeting-the-window.md) and
[Failure modes](../../notes/11-failure-modes.md).

A context window is a budget, and something has to decide what loses when it runs out. This budgeter
takes the layers of a support agent's context (system, tools, memory, retrieved documents, history,
task), reserves room for the answer, and spends the rest by priority: pinned items are untouched,
the lowest priority goes first, older turns go before newer ones, and retrieved text is cut rather
than dropped when a cut is enough. It reports every decision, so a bad answer can be traced to what
was left out.

## Run it (offline, no key)

```bash
npx tsx run.ts     # three budgets, each with its decisions and the stub's answer
npx tsx test.ts    # the assertions
```

Real output with the stub:

```text
RUN_OUTPUT
```

The third run is the lesson: the budget is the same as the second, and only the relevance ranking
changed. The packer did what it was told and dropped the one document that held the answer. A
budgeter can only be as good as the priorities it gets.

## Swap in a real model and a real counter

```bash
npm install                                 # installs @anthropic-ai/sdk
export ANTHROPIC_API_KEY=...                # or: ant auth login
MODEL=claude-opus-5-5 npx tsx run.ts        # or claude-haiku-5-5, claude-sonnet-5-5, claude-fable-5-1
```

`estimate` is characters over four, which is why `safety` exists. For real counts, use the token
counting endpoint: count each item ahead of the call, cache the numbers by item id, and give
`pack` a `count` that looks them up. `pack` calls `count` synchronously and many times, so do not
make a network call inside it.

```ts
const client = new Anthropic();
const { input_tokens } = await client.messages.countTokens({
  model: "claude-opus-5-5",
  messages: [{ role: "user", content: item.text }],
});
```

## Exercises

1. Set `reserveOutput` to 0 on the tight budget. What does the report show, and what would a real
   model do when it reached the end of the window?
2. Give memory a higher priority than the refund document. What is dropped first now?
3. Add a `summary` item that replaces turns 1 to 4 for 100 tokens. How much retrieved text does it
   buy back?
