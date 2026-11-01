# Lab: inference by simulation (TypeScript)

The TypeScript twin of the [Python lab](../inference-lab/README.md). It reads that folder's
`params.json`, draws the same random numbers from the same generator, and prints the same report. Read
the Python README for why the lab exists, how to read the tables and the exercises.

**The numbers are not measurements.** Every timing follows from the assumptions in `params.json`.

```bash
npx tsx run.ts       # the three simulations
npx tsx test.ts      # the assertions
npx tsx measure.ts   # real TTFT and TPOT if MODEL is set; otherwise a fake stream
```

Real output, identical to the Python version:

```text
All timings follow from the assumptions in params.json. They are not measurements.

1. Batching: 200 requests, 8 slots, one arrival per 2000 ms on average
policy        TTFT p50   TTFT p95    E2E p50    E2E p95   tokens/s  busy slots
static           7.3 s     16.7 s     11.1 s     23.8 s       56.8         2.3
dynamic          4.9 s     11.9 s      7.8 s     19.0 s       56.9         1.5
continuous       0.1 s      0.1 s      1.1 s     11.2 s       57.8         1.7

1. Batching: 200 requests, 8 slots, one arrival per 600 ms on average
policy        TTFT p50   TTFT p95    E2E p50    E2E p95   tokens/s  busy slots
static          85.5 s    169.8 s     89.5 s    171.6 s       80.5         2.3
dynamic         87.6 s    175.6 s     92.0 s    177.0 s       77.3         2.2
continuous       0.1 s      0.5 s      1.3 s     13.0 s      183.8         4.8

2. KV cache, continuous batching, one arrival per 600 ms: capacity in tokens, evicting the newest sequence
capacity   peak used   preemptions   tokens recomputed   E2E p95   tokens/s
   40000        7063             0                   0    13.0 s      183.8
    6000        6008             6                4138    13.8 s      183.6
    4000        4006            35               20761    18.0 s      171.4
    2500        2506            31               20257    74.3 s      116.3

3. Prefix cache: 20 sessions, 5 turns, 1600-token system prompt, 16-token blocks
layout              cache blocks   token hit rate   mean prefill
stable                      4000            92.9%         7.0 ms
stable                       400            82.0%        17.6 ms
stamp_after_system          4000            80.8%        18.9 ms
stamp_after_system           400            80.8%        18.9 ms
stamp_first                 4000             0.0%        98.0 ms
stamp_first                  400             0.0%        98.0 ms
```

To keep the two versions identical, the mean prefill is computed from an integer token total. Summing
the float timings differs between the languages, because Python's `sum` compensates for rounding since
3.12 and a plain `reduce` does not. On ties that changed the last printed digit.

## Swap in a real model

```bash
npm install                                 # installs the optional SDK; delete node_modules afterwards
export ANTHROPIC_API_KEY=...                # or: ant auth login
MODEL=claude-opus-5-5 npx tsx measure.ts    # or claude-haiku-5-5, claude-sonnet-5-5, claude-fable-5-1
```

This makes two paid calls. A hosted API measures its queue and network too, so use it to see the TTFT
and TPOT split and a cache read, not to benchmark a server.
