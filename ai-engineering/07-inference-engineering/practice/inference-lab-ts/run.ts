// Same parameters, workload and report as the Python lab in ../inference-lab.
import { PARAMS as p, runBatched, runContinuous, runPrefix, workload } from "./sim.ts";

const pad = (x: string | number, n: number) => String(x).padStart(n);
const s = (ms: number, n: number) => pad((ms / 1000).toFixed(1), n);

console.log("All timings follow from the assumptions in params.json. They are not measurements.\n");
const HIGH: number = p.mean_gap_ms.at(-1);
for (const gap of p.mean_gap_ms) {
  console.log(`1. Batching: ${p.requests} requests, ${p.slots} slots, one arrival per ${gap} ms on average`);
  console.log("policy        TTFT p50   TTFT p95    E2E p50    E2E p95   tokens/s  busy slots");
  const rows = [
    ["static", () => runBatched(workload(p, gap), p, Infinity)],
    ["dynamic", () => runBatched(workload(p, gap), p, p.dynamic_window_ms)],
    ["continuous", () => runContinuous(workload(p, gap), p)],
  ] as const;
  for (const [name, fn] of rows) {
    const m = fn();
    console.log(`${name.padEnd(12)} ${s(m.ttftP50, 7)} s ${s(m.ttftP95, 8)} s ${s(m.e2eP50, 8)} s ${s(m.e2eP95, 8)} s ${pad(m.tokensPerS.toFixed(1), 10)} ${pad(m.meanBatch.toFixed(1), 11)}`);
  }
  console.log();
}

console.log(`2. KV cache, continuous batching, one arrival per ${HIGH} ms: capacity in tokens, evicting the newest sequence`);
console.log("capacity   peak used   preemptions   tokens recomputed   E2E p95   tokens/s");
for (const cap of p.kv_capacities) {
  const m = runContinuous(workload(p, HIGH), p, cap);
  console.log(`${pad(cap, 8)} ${pad(m.peakKv, 11)} ${pad(m.preemptions, 13)} ${pad(m.recomputedTokens, 19)} ${s(m.e2eP95, 7)} s ${pad(m.tokensPerS.toFixed(1), 10)}`);
}

console.log(`\n3. Prefix cache: ${p.sessions} sessions, ${p.turns} turns, ${p.system_tokens}-token system prompt, ${p.block_tokens}-token blocks`);
console.log("layout              cache blocks   token hit rate   mean prefill");
for (const layout of ["stable", "stamp_after_system", "stamp_first"]) {
  for (const cap of p.cache_blocks) {
    const [hit, ms] = runPrefix(p, layout, cap);
    console.log(`${layout.padEnd(19)} ${pad(cap, 12)} ${pad((100 * hit).toFixed(1), 15)}% ${pad(ms.toFixed(1), 11)} ms`);
  }
}
