# Lab: a context budgeter

Language: TypeScript. The [Python version](../context-budgeter-py/README.md) does the same job on the same inputs. Supports [Budgeting the window](../../notes/03-budgeting-the-window.md) and
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
model: stub. Unpacked context is 4581 tokens.

--- roomy: window 8000, reserve 1000, limit 6600, used 4581
  everything kept
  by layer: system 173, tools 300, memory 162, retrieved 2518, history 1414, task 14
  answer: annual plans can be refunded within 30 days of renewal [doc-refunds]

--- tight: window 3500, reserve 500, limit 2825, used 2825
  truncated doc-seats    900 -> 852
  dropped   doc-sso      900 -> 0
  dropped   turn-1       202 -> 0
  dropped   turn-2       202 -> 0
  dropped   turn-3       202 -> 0
  dropped   turn-4       202 -> 0
  by layer: system 173, tools 300, memory 162, retrieved 1570, history 606, task 14
  answer: annual plans can be refunded within 30 days of renewal [doc-refunds]

--- tight, relevance ranked wrongly: window 3500, reserve 500, limit 2825, used 2651
  dropped   doc-refunds  718 -> 0
  dropped   turn-1       202 -> 0
  dropped   turn-2       202 -> 0
  dropped   turn-3       202 -> 0
  dropped   turn-4       202 -> 0
  dropped   turn-5       202 -> 0
  dropped   turn-6       202 -> 0
  by layer: system 173, tools 300, memory 162, retrieved 1800, history 202, task 14
  answer: I can't find that in the supplied documents.
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
