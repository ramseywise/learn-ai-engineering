# Lab: a context budgeter (Python)

The Python twin of the [TypeScript lab](../context-budgeter/README.md). Same scenario, budgets and
packing rules, same report. Read the TypeScript README for why the lab exists and for the exercises.

```bash
uv run run.py      # three budgets, each with its decisions and the stub's answer
uv run test.py     # the assertions
```

Real output with the stub, identical to the TypeScript version:

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

## Swap in a real model and a real counter

```bash
export ANTHROPIC_API_KEY=...                # or: ant auth login
MODEL=claude-opus-5-5 uv run --with anthropic run.py    # or claude-haiku-5-5, claude-sonnet-5-5, claude-fable-5-1
```

`estimate` is characters over four, which is why `safety` exists. For real counts, count each item
ahead of the call, cache the numbers by item id, and pass a `count` that looks them up. `pack` calls
`count` synchronously and many times, so do not make a network call inside it.

```python
client = anthropic.Anthropic()
n = client.messages.count_tokens(
    model="claude-opus-5-5",
    messages=[{"role": "user", "content": item.text}],
).input_tokens
```
