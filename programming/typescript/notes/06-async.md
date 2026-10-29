---
origin: curated
sources:
  - "MDN, Using promises — https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises (CC-BY-SA 2.5; read, not copied)"
  - "Node.js docs, Event loop / timers — https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick"
  - "typescript-exercises — https://github.com/typescript-exercises/typescript-exercises (MIT; vendored in practice/)"
concepts: [js-event-loop, promises, async-await, promise-combinators, concurrency-limits, abort-signal]
cleaned: 2026-10-29
---
# 6 — Async: Promises and `async`/`await`

> JavaScript runs on one thread with an event loop. Anything slow (network, disk, timers) returns a `Promise`. `await` pauses only the current function, never the whole program.

---

## Mental model, for Python developers

| asyncio | JavaScript | Difference |
|---|---|---|
| `async def` / `await` | `async function` / `await` | Same idea |
| A coroutine object | A `Promise` | **A promise starts running as soon as it's created.** There is no "forgot to schedule it" step |
| `asyncio.gather(*cs)` | `Promise.all(ps)` | Fails fast on the first rejection |
| `gather(..., return_exceptions=True)` | `Promise.allSettled(ps)` | Returns `{status, value \| reason}` for each promise |
| `asyncio.wait_for(c, t)` | `Promise.race([p, timeout])` or `AbortSignal.timeout(ms)` | `race` does **not** cancel the loser |
| `asyncio.Semaphore(n)` | A worker pool (exercise Q3) or the `p-limit` package | |
| `asyncio.run(main())` | Top-level `await` in an ES module | |

The event loop is always running in Node. There is no `run()` call to make.

## Writing async code

```ts
async function loadUser(id: number): Promise<User> {
  const res = await fetch(`https://api.example.com/users/${id}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return (await res.json()) as User;     // `as` checks nothing; see note 08
}
```

- An `async` function **always** returns a `Promise`, so annotate the return type as `Promise<T>`.
- A thrown error becomes a rejected promise. Handle it with `try/catch` around `await`.
- **Sequential vs parallel:**

```ts
const a = await getA(); const b = await getB();               // sequential: total = a + b
const [a, b] = await Promise.all([getA(), getB()]);           // parallel: total = max(a, b)
```

## Common bugs

| Bug | Symptom | Fix |
|---|---|---|
| A forgotten `await` | You get `Promise { <pending> }`, or the error appears later as an unhandled rejection | Turn on the lint rule `@typescript-eslint/no-floating-promises` |
| `await` inside `forEach` | The callbacks aren't awaited | Use `for…of` with `await` (sequential) or `Promise.all(xs.map(…))` (parallel) |
| `Promise.all` over 10,000 requests | Rate limits or exhausted sockets | Limit concurrency (`mapLimit`) |
| A timeout via `race` with no cleanup | The process won't exit, or work continues after the timeout | Clear the timer. Pass an `AbortSignal` to cancel the actual work |

## Cancellation: `AbortController`

```ts
const res = await fetch(url, { signal: AbortSignal.timeout(5_000) });   // cancels the request itself
```

`fetch`, Node streams and most SDKs (including Anthropic's) accept a `signal`. Pass it down through your own async functions too.

## Callbacks → promises

Old Node-style APIs take `(err, result) => …` callbacks. Wrap them once:

```ts
import { promisify } from 'node:util';
const readFileAsync = promisify(fs.readFile);
```

Typing a generic `promisify` yourself is a good generics exercise (vendored exercise 10).

## Async iteration

```ts
for await (const chunk of stream) process.stdout.write(chunk);
```

Streaming LLM responses use exactly this ([note 09](09-typescript-for-ai-apps.md)).

---

## Exercises

- [`practice/exercises/06-async.ts`](../practice/exercises/06-async.ts): `withTimeout`, `retry` with backoff, `mapLimit` and `partitionSettled`. From `practice/`, check with `npm test`.
- [`practice/typescript-exercises/10`](../practice/typescript-exercises/10/index.ts): type a `promisify`. From `practice/`, check with `node check.ts exercises/10/`.
