import assert from "node:assert/strict";
import { PARAMS as p, PrefixCache, Rng, percentile, req, runBatched, runContinuous, runPrefix, workload } from "./sim.ts";

// Same generator in both languages: pinned to the same values as the Python test
const r = new Rng(42);
assert.deepEqual([r.next(), r.next()], [0.2523451747838408, 0.08812504541128874], "generator changed");
assert.equal(percentile([1, 2, 3, 4], 0.5), 2);
assert.equal(percentile([1, 2, 3, 4], 0.95), 4);

const [LOW, HIGH] = p.mean_gap_ms;

// Every request finishes, whichever policy runs it
for (const run of [(w: any) => runBatched(w, p, Infinity), (w: any) => runBatched(w, p, 100), (w: any) => runContinuous(w, p), (w: any) => runContinuous(w, p, 3000)]) {
  const w = workload(p, HIGH);
  const m = run(w);
  assert.ok(w.every((x) => x.done !== null && x.first! <= x.done));
  assert.ok(m.tokensPerS > 0);
}

const lowStatic = runBatched(workload(p, LOW), p, Infinity);
const lowDynamic = runBatched(workload(p, LOW), p, 100);
assert.ok(lowDynamic.ttftP50 < lowStatic.ttftP50, "at low load, waiting for a full batch is the whole cost");
const dyn = runBatched(workload(p, HIGH), p, 100);
const cont = runContinuous(workload(p, HIGH), p);
assert.ok(cont.ttftP50 < dyn.ttftP50 && cont.e2eP95 < dyn.e2eP95, "under load, slots freed early are what keeps latency down");
assert.ok(cont.tokensPerS > dyn.tokensPerS);

// A worked two-request batch: both wait for the longer one, in lock-step
const two = { ...p, slots: 2, decode_base_ms: 10, decode_per_seq_ms: 0, prefill_ms_per_token: 0 };
const a = req(0, 0, 10, 1), b = req(1, 0, 10, 3);
runBatched([a, b], two, Infinity);
assert.deepEqual([a.first, a.done, b.done], [10, 10, 30]);

// Continuous: a slot frees at once. Static: the third request waits for the whole batch.
const one = { ...two, slots: 1 };
const c = req(0, 0, 10, 2), d = req(1, 0, 10, 2);
runContinuous([c, d], one);
assert.deepEqual([c.done, d.first, d.done], [20, 30, 40]);

// KV pressure
const big = runContinuous(workload(p, HIGH), p, 40000), small = runContinuous(workload(p, HIGH), p, 2500);
assert.ok(big.preemptions === 0 && small.preemptions > 0 && small.recomputedTokens > 0);
assert.ok(small.e2eP95 > big.e2eP95, "recomputing costs latency");
assert.ok(runContinuous(workload(p, HIGH), p, 4000).peakKv <= 4000 + p.slots, "bounded by capacity, plus the step that detects the overflow");

// Prefix cache mechanics
const cache = new PrefixCache(100, 4);
const toks = [...Array(10).keys()];
assert.equal(cache.lookup(toks), 10, "cold");
assert.equal(cache.lookup(toks), 2, "two full blocks hit, the 2-token tail never caches");
assert.equal(cache.lookup([99, ...toks.slice(1)]), 10, "one changed token at the start invalidates everything after it");
const lru = new PrefixCache(1, 4);
lru.lookup([1, 2, 3, 4]);
lru.lookup([5, 6, 7, 8]);
assert.equal(lru.lookup([1, 2, 3, 4]), 4, "evicted");

const [stable] = runPrefix(p, "stable", 4000);
const [mid] = runPrefix(p, "stamp_after_system", 4000);
const [first] = runPrefix(p, "stamp_first", 4000);
const [smallCache] = runPrefix(p, "stable", 400);
assert.equal(first, 0, "a stamp in the first token means no hits at all");
assert.ok(stable > mid && mid > first);
assert.ok(smallCache < stable);
console.log("ok: all assertions passed");
