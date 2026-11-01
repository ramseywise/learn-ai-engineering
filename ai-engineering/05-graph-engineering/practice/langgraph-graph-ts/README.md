# Lab: a LangGraph support-triage graph (TypeScript)

The LangGraph.js twin of the [Python lab](../langgraph-graph/README.md). It reads the same
`tickets.json` and `kb.json` from that folder, has the same nodes and edges, and prints the same
report. Read the Python README for why the lab exists, the diagram and the exercises.

Unlike the other TypeScript labs this one has real dependencies, so it needs an install:

```bash
npm install        # node_modules is ignored by this folder's .gitignore
npx tsx run.ts     # five tickets, one per route
npx tsx test.ts    # the assertions
```

Real output with the stub, identical to the Python version:

```text
model: stub

t1 [how_to] sent: classify > search:docs > search:tickets > gather > draft > check > send (95 tokens)
t2 paused at approve: Annual plans can be refunded within 30 days of renewal. [doc-refunds]
   outbox holds 1. A new graph object resumes from the checkpoint with: approve
t2 [billing] sent: classify > search:docs > search:tickets > gather > draft > check > approve > send (136 tokens)
t3 [bug] sent: classify > search:docs > search:tickets > gather > draft > check > draft > check > send (203 tokens)
t4 [how_to] escalated: classify > search:docs > search:tickets > gather > escalate (36 tokens)
t5 paused at approve: Annual plans can be refunded within 30 days of renewal. [doc-refunds]
   outbox holds 3. A new graph object resumes from the checkpoint with: deny
t5 [billing] escalated: classify > search:docs > search:tickets > gather > draft > check > approve > escalate (108 tokens)

outbox: 3 sent
  Admins add seats under Settings, Team, Seats. [doc-seats]
  Annual plans can be refunded within 30 days of renewal. [doc-refunds]
  A blank invoice page is a known bug; the fix is to clear the session. [tkt-blank-page]
```

## Where the two versions differ

Building this twin turned up two differences you can hit in real code. Both are visible in `graph.ts`.

- LangGraph.js refuses a node with the same name as a state key (`draft is already being used as a
  state attribute`). Python accepted it, and the shared state key is named `reply` in both versions.
- LangGraph.js treats a falsy resume value as no input: `new Command({ resume: false })` throws
  `EmptyInputError`. The decision is the string `"approve"` or `"deny"` in both versions.

State is declared with `Annotation.Root` and a `reducer` rather than `TypedDict` and `Annotated`, and
`getState` and `invoke` are async.

## Swap in a real model

```bash
export ANTHROPIC_API_KEY=...                # or: ant auth login
MODEL=claude-opus-5-5 npx tsx run.ts        # or claude-haiku-5-5, claude-sonnet-5-5, claude-fable-5-1
```

`model.ts` is the only file that knows about the provider, and it enables the server-side refusal
fallback (`fallbacks: "default"`); its comment says how to remove it.
