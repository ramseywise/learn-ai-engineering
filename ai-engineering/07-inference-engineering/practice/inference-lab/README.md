# Lab: inference by simulation (Python)

Pillar 07 explains why a server's scheduler can matter more than its chip. You cannot try that on a
laptop without a GPU, so this lab simulates the three mechanisms instead, in plain Python with no
dependencies. It runs batching policies ([note 06](../../notes/06-serving-at-scale.md#batching)), KV
cache eviction and prefix caching ([note 07](../../notes/07-prefill-decode-kv-cache.md)) on one
seeded workload.

**The numbers are not measurements.** Every timing follows from the assumptions in `params.json`,
such as 20 ms per decode step. No GPU, model or server was measured. Only the shape of each comparison
carries over, and `measure.py` is how you get real numbers.

The [TypeScript version](../inference-lab-ts/README.md) reads the same `params.json`, draws the same
random numbers and prints the same report.

```bash
uv run run.py        # the three simulations
uv run test.py       # the assertions, including small cases worked by hand
uv run measure.py    # real TTFT and TPOT if MODEL is set; otherwise a fake stream
```

Real output:

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

Under these assumptions:

- **Batching.** At low load, static batching waits to fill up, and dynamic batching still queues behind
  a batch held open by its longest member. Continuous batching gives a first token almost at once. At
  high load the two batch-at-a-time policies fall behind, because slots freed early stay empty (about
  2 of 8 busy), so their queues grow for the whole run. Continuous batching keeps up.
- **KV cache.** Below the working set, preempted sequences recompute. Latency degrades before
  throughput does.
- **Prefix cache.** Moving one changing token decides the result. Stamped after the system prompt, the
  system prompt still hits and the conversation history never does. Stamped first, nothing hits. A
  small cache also loses a stable prompt's history blocks through LRU eviction.

## Things to try

1. Set `decode_per_seq_ms` to 10 and rerun. What happens to each policy at the higher load?
   <details><summary>Answer</summary>All of them slow down, because each step now costs more per
   sequence. Continuous batching stops keeping up at the 600 ms load too (its TTFT p50 goes from 0.1 s
   to about 79 s), and it still stays well ahead, because the batch policies pay for empty slots.</details>
2. Raise `prefill_ms_per_token` to 1. This is the head-of-line blocking in note 07. What happens to
   continuous batching's E2E p95? <details><summary>Answer</summary>It climbs, because every admission
   stalls every sequence decoding in the batch. Chunked prefill or a separate prefill pool is the fix
   the note describes.</details>
3. Change `victim = active.pop()` to evict the oldest sequence. Compare the recomputed tokens.
   <details><summary>Answer</summary>They rise, because the oldest sequence holds the most KV and made
   the most progress. Run it to see by how much under your parameters.</details>
4. Set `block_tokens` to 64 and rerun the prefix table. Why does the stable layout's hit rate fall at
   the large cache and rise at the small one? <details><summary>Answer</summary>Only full blocks
   count, so more of each prompt's tail goes unmatched (92.9% to 91.2%). But 400 blocks now hold four
   times the tokens, so the small cache stops evicting (82.0% to 91.2%).</details>

## Swap in a real model

There is no model in the simulation. `measure.py` is the real path: it streams the same prompt twice
with a cached system prompt, then reports TTFT, time per token and tokens read from the cache.

```bash
export ANTHROPIC_API_KEY=...                # or: ant auth login
MODEL=claude-opus-5-5 uv run --with anthropic measure.py    # or claude-haiku-5-5, claude-sonnet-5-5, claude-fable-5-1
```

This makes two paid calls. A hosted API measures its queue and network too, and you cannot see its
batching. Use it to see the TTFT and TPOT split and the effect of a cache read, not to benchmark a
server. To run the same report against a server you control, point `ANTHROPIC_BASE_URL` at a compatible
endpoint, or adapt `measure.py` to its client.
