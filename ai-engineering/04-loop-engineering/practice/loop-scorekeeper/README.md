# Lab: a loop with a scorekeeper

Language: TypeScript. The [Python version](../loop-scorekeeper-py/README.md) does the same job on the same inputs. Supports [The scorekeeper](../../notes/03-the-scorekeeper.md) and
[Failure modes and guardrails](../../notes/09-failure-modes-and-guardrails.md).

A loop that asks its maker whether it is done will hear yes. Here a maker keeps writing a `slugify`
function, and a deterministic scorekeeper decides: visible checks feed back as failure messages,
held-out checks are never shown, and the checks are fingerprinted so a maker cannot edit them. The
loop stops for one of six named reasons: `passed`, `gamed`, `max_iterations`, `budget`,
`no_progress`, `tampered`.

## Run it (offline, no key)

```bash
npx tsx run.ts     # five scripted makers, one per way a loop ends
npx tsx test.ts    # the assertions, one per stop reason
```

Real output with the stub:

```text

--- honest maker: stop=passed, 3 iterations, 308 tokens, shippable=true
  #1  visible 1/4   held-out 0/4
  #2  visible 3/4   held-out 0/4
  #3  visible 4/4   held-out 4/4

--- maker memorises the visible checks: stop=gamed, 3 iterations, 310 tokens, shippable=false
  #1  visible 1/4   held-out 0/4
  #2  visible 3/4   held-out 0/4
  #3  visible 4/4   held-out 0/4

--- ordinary overfit: stop=gamed, 2 iterations, 189 tokens, shippable=false
  #1  visible 1/4   held-out 0/4
  #2  visible 4/4   held-out 3/4

--- stuck maker: stop=no_progress, 3 iterations, 299 tokens, shippable=false
  #1  visible 1/4   held-out 0/4
  #2  visible 1/4   held-out 0/4
  #3  visible 1/4   held-out 0/4

--- expensive maker: stop=passed, 1 iterations, 76 tokens, shippable=true
  #1  visible 4/4   held-out 4/4
```

The second run is the one to study. Its visible score reaches 4/4 by memorising the inputs, and only
the held-out checks show it. The third has no bad intent: the same 4/4 with a plain regex that
misses accents. To a loop, both look like success on the visible checks, and that is why `gamed`
exists as an outcome. A real project would then review the run, since the two need different fixes.

## Swap in a real model

```bash
npm install                                 # installs @anthropic-ai/sdk
export ANTHROPIC_API_KEY=...                # or: ant auth login
MODEL=claude-opus-5-5 npx tsx run.ts        # or claude-haiku-5-5, claude-sonnet-5-5, claude-fable-5-1
```

A real model's output is not guaranteed to be bare code. If it adds fences, the scorekeeper reports
`does not load`, and that feedback goes into the next prompt, which is the loop working as designed.
`vm` protects against accidents only. Do not run a real model's code this way outside a lab.

## Exercises

1. Set `patience` to 0. What goes wrong with the honest maker?
2. Add a held-out check to `visible`. Why does the maker now pass with less effort, and what did you
   give up?
3. Add a maker that writes a correct function with a `console.log` on every call. Should the
   scorekeeper care? Add a check if so.
