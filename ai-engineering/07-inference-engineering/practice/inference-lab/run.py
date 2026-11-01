# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Same parameters, workload and report as the TypeScript lab in ../inference-lab-ts."""
import math

from sim import PARAMS as p
from sim import run_batched, run_continuous, run_prefix, workload

print("All timings follow from the assumptions in params.json. They are not measurements.\n")
HIGH = p["mean_gap_ms"][-1]
for gap in p["mean_gap_ms"]:
    print(f"1. Batching: {p['requests']} requests, {p['slots']} slots, one arrival per {gap} ms on average")
    print("policy        TTFT p50   TTFT p95    E2E p50    E2E p95   tokens/s  busy slots")
    rows = [
        ("static", lambda: run_batched(workload(p, gap), p, math.inf)),
        ("dynamic", lambda: run_batched(workload(p, gap), p, p["dynamic_window_ms"])),
        ("continuous", lambda: run_continuous(workload(p, gap), p)),
    ]
    for name, fn in rows:
        m = fn()
        print(f"{name:<12} {m.ttft_p50 / 1000:>7.1f} s {m.ttft_p95 / 1000:>8.1f} s {m.e2e_p50 / 1000:>8.1f} s {m.e2e_p95 / 1000:>8.1f} s {m.tokens_per_s:>10.1f} {m.mean_batch:>11.1f}")
    print()

print(f"2. KV cache, continuous batching, one arrival per {HIGH} ms: capacity in tokens, evicting the newest sequence")
print("capacity   peak used   preemptions   tokens recomputed   E2E p95   tokens/s")
for cap in p["kv_capacities"]:
    m = run_continuous(workload(p, HIGH), p, cap)
    print(f"{cap:>8} {m.peak_kv:>11} {m.preemptions:>13} {m.recomputed_tokens:>19} {m.e2e_p95 / 1000:>7.1f} s {m.tokens_per_s:>10.1f}")

print(f"\n3. Prefix cache: {p['sessions']} sessions, {p['turns']} turns, {p['system_tokens']}-token system prompt, {p['block_tokens']}-token blocks")
print("layout              cache blocks   token hit rate   mean prefill")
for layout in ["stable", "stamp_after_system", "stamp_first"]:
    for cap in p["cache_blocks"]:
        hit, ms = run_prefix(p, layout, cap)
        print(f"{layout:<19} {cap:>12} {100 * hit:>15.1f}% {ms:>11.1f} ms")
