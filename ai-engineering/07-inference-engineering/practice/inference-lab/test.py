# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
import math

from sim import PARAMS as p
from sim import PrefixCache, Req, Rng, percentile, run_batched, run_continuous, run_prefix, workload

# Same generator in both languages: pinned to the same values as the TypeScript test
r = Rng(42)
assert [r.next() for _ in range(2)] == [0.2523451747838408, 0.08812504541128874], "generator changed"
assert percentile([1, 2, 3, 4], 0.5) == 2 and percentile([1, 2, 3, 4], 0.95) == 4

LOW, HIGH = p["mean_gap_ms"]

# Every request finishes, whichever policy runs it
for run in [lambda w: run_batched(w, p, math.inf), lambda w: run_batched(w, p, 100), lambda w: run_continuous(w, p), lambda w: run_continuous(w, p, 3000)]:
    w = workload(p, HIGH)
    m = run(w)
    assert all(x.done is not None and x.first <= x.done for x in w)
    assert m.tokens_per_s > 0

static, dynamic = run_batched(workload(p, LOW), p, math.inf), run_batched(workload(p, LOW), p, 100)
assert dynamic.ttft_p50 < static.ttft_p50, "at low load, waiting for a full batch is the whole cost"
dynamic, cont = run_batched(workload(p, HIGH), p, 100), run_continuous(workload(p, HIGH), p)
assert cont.ttft_p50 < dynamic.ttft_p50 and cont.e2e_p95 < dynamic.e2e_p95, "under load, slots freed early are what keeps latency down"
assert cont.tokens_per_s > dynamic.tokens_per_s

# A worked two-request batch: both wait for the longer one, in lock-step
two = dict(p, slots=2, decode_base_ms=10, decode_per_seq_ms=0, prefill_ms_per_token=0)
a, b = Req(0, 0.0, 10, 1), Req(1, 0.0, 10, 3)
run_batched([a, b], two, math.inf)
assert (a.first, a.done, b.done) == (10, 10, 30)

# Continuous: a slot frees at once. Static: the third request waits for the whole batch.
one = dict(two, slots=1)
c, d = Req(0, 0.0, 10, 2), Req(1, 0.0, 10, 2)
run_continuous([c, d], one)
assert (c.done, d.first, d.done) == (20, 30, 40)

# KV pressure
big, small = run_continuous(workload(p, HIGH), p, 40000), run_continuous(workload(p, HIGH), p, 2500)
assert big.preemptions == 0 and small.preemptions > 0 and small.recomputed_tokens > 0
assert small.e2e_p95 > big.e2e_p95, "recomputing costs latency"
tight = run_continuous(workload(p, HIGH), p, 4000)
assert tight.peak_kv <= 4000 + p["slots"], "bounded by capacity, plus the step that detects the overflow"

# Prefix cache mechanics
cache = PrefixCache(100, 4)
toks = list(range(10))
assert cache.lookup(toks) == 10, "cold"
assert cache.lookup(toks) == 2, "two full blocks hit, the 2-token tail never caches"
assert cache.lookup([99] + toks[1:]) == 10, "one changed token at the start invalidates everything after it"
lru = PrefixCache(1, 4)
lru.lookup([1, 2, 3, 4])
lru.lookup([5, 6, 7, 8])
assert lru.lookup([1, 2, 3, 4]) == 4, "evicted"

stable, _ = run_prefix(p, "stable", 4000)
mid, _ = run_prefix(p, "stamp_after_system", 4000)
first, _ = run_prefix(p, "stamp_first", 4000)
small_cache, _ = run_prefix(p, "stable", 400)
assert first == 0, "a timestamp in the first token means no hits at all"
assert stable > mid > first
assert small_cache < stable
print("ok: all assertions passed")
