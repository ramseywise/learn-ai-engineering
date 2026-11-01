# Lab: a loop with a scorekeeper (Python)

The Python twin of the [TypeScript lab](../loop-scorekeeper/README.md). Same eight checks, same five
scripted makers and the same six stop reasons, so the iteration tables compare directly. The
candidates are Python lambdas rather than JavaScript functions, so token counts differ slightly. A
candidate runs in a child process with a timeout, where the TypeScript lab uses `node:vm`.

```bash
uv run run.py      # five scripted makers, one per way a loop ends
uv run test.py     # the assertions, one per stop reason
```

Real output with the stub:

```text

--- honest maker: stop=passed, 3 iterations, 314 tokens, shippable=true
  #1  visible 1/4   held-out 0/4
  #2  visible 3/4   held-out 0/4
  #3  visible 4/4   held-out 4/4

--- maker memorises the visible checks: stop=gamed, 3 iterations, 301 tokens, shippable=false
  #1  visible 1/4   held-out 0/4
  #2  visible 3/4   held-out 0/4
  #3  visible 4/4   held-out 0/4

--- ordinary overfit: stop=gamed, 2 iterations, 184 tokens, shippable=false
  #1  visible 1/4   held-out 0/4
  #2  visible 4/4   held-out 3/4

--- stuck maker: stop=no_progress, 3 iterations, 289 tokens, shippable=false
  #1  visible 1/4   held-out 0/4
  #2  visible 1/4   held-out 0/4
  #3  visible 1/4   held-out 0/4

--- expensive maker: stop=budget, 2 iterations, 176 tokens, shippable=false
  #1  visible 1/4   held-out 0/4
  #2  visible 3/4   held-out 0/4
```

Each maker here is built fresh per run. The fifth run shows the `budget` stop.

## Swap in a real model

```bash
export ANTHROPIC_API_KEY=...                # or: ant auth login
MODEL=claude-opus-5-5 uv run --with anthropic run.py    # or claude-haiku-5-5, claude-sonnet-5-5, claude-fable-5-1
```

The child process stops accidents only. Do not run a real model's code this way outside a lab.
