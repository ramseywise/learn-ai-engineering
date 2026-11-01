// Discrete simulations of the mechanisms in notes 06 and 07. Timing comes from params.json, whose
// numbers are assumptions and not measurements. Only the shape of each comparison means anything.
import { readFileSync } from "node:fs";

export const PARAMS = JSON.parse(readFileSync(new URL("../inference-lab/params.json", import.meta.url), "utf8"));
export type Params = typeof PARAMS;

/** A linear congruential generator, written out so Python and TypeScript draw the same numbers. */
export class Rng {
  constructor(private x: number) {}
  next(): number {
    this.x = (this.x * 1664525 + 1013904223) % 4294967296;
    return this.x / 4294967296;
  }
  between(lo: number, hi: number): number {
    return lo + Math.floor(this.next() * (hi - lo + 1));
  }
}

export interface Req { id: number; arrive: number; prompt: number; output: number; made: number; first: number | null; done: number | null; preempted: number }
export const req = (id: number, arrive: number, prompt: number, output: number): Req => ({ id, arrive, prompt, output, made: 0, first: null, done: null, preempted: 0 });

export function workload(p: Params, meanGapMs: number): Req[] {
  const rng = new Rng(p.seed);
  let t = 0;
  const out: Req[] = [];
  for (let i = 0; i < p.requests; i++) {
    t += -Math.log(1 - rng.next()) * meanGapMs;
    const band = rng.next() < p.long_share ? p.long_output : p.short_output;
    const prompt = rng.between(p.prompt_tokens[0], p.prompt_tokens[1]);
    out.push(req(i, t, prompt, rng.between(band[0], band[1])));
  }
  return out;
}

export function percentile(xs: number[], q: number): number {
  const s = [...xs].sort((a, b) => a - b);
  return s[Math.min(s.length - 1, Math.ceil(q * s.length) - 1)];
}

export interface Metrics {
  ttftP50: number; ttftP95: number; e2eP50: number; e2eP95: number; tokensPerS: number; meanBatch: number;
  preemptions: number; recomputedTokens: number; peakKv: number;
}

function metrics(reqs: Req[], end: number, steps: number, occupied: number, preemptions = 0, recomputedTokens = 0, peakKv = 0): Metrics {
  const ttft = reqs.map((r) => r.first! - r.arrive);
  const e2e = reqs.map((r) => r.done! - r.arrive);
  return {
    ttftP50: percentile(ttft, 0.5), ttftP95: percentile(ttft, 0.95), e2eP50: percentile(e2e, 0.5), e2eP95: percentile(e2e, 0.95),
    tokensPerS: reqs.reduce((a, r) => a + r.output, 0) / (end / 1000), meanBatch: occupied / steps, preemptions, recomputedTokens, peakKv,
  };
}

/** Static (window is infinite) and dynamic batching. A batch runs until its longest member
 *  finishes, and a finished sequence's slot stays empty and still costs a step. */
export function runBatched(reqs: Req[], p: Params, window: number): Metrics {
  let now = 0, i = 0, steps = 0, occupied = 0;
  let queue: Req[] = [];
  while (i < reqs.length || queue.length) {
    while (i < reqs.length && reqs[i].arrive <= now) queue.push(reqs[i++]);
    if (!queue.length) { now = reqs[i].arrive; continue; }
    const deadline = queue[0].arrive + window;
    if (queue.length < p.slots && now < deadline && i < reqs.length) {
      now = Math.min(reqs[i].arrive, deadline);
      continue;
    }
    const batch = queue.slice(0, p.slots);
    queue = queue.slice(p.slots);
    now += batch.reduce((a, r) => a + r.prompt, 0) * p.prefill_ms_per_token;
    const longest = Math.max(...batch.map((r) => r.output));
    for (let step = 1; step <= longest; step++) {
      now += p.decode_base_ms + p.decode_per_seq_ms * batch.length;
      steps++;
      for (const r of batch) {
        if (step === 1) r.first = now;
        if (step === r.output) r.done = now;
        if (step <= r.output) occupied++;
      }
    }
  }
  return metrics(reqs, now, steps, occupied);
}

/** Iteration-level scheduling: after every decode step, finished sequences leave and waiting ones
 *  join. The KV cache holds one token per prompt and generated token. Over capacity, the most recently
 *  admitted sequence is evicted, and it recomputes everything when it is readmitted. */
export function runContinuous(reqs: Req[], p: Params, kvCapacity = Infinity): Metrics {
  let now = 0, i = 0, steps = 0, occupied = 0, preempts = 0, recomputed = 0, peak = 0, finished = 0;
  const queue: Req[] = [];
  let active: Req[] = [];
  const kv = () => active.reduce((a, r) => a + r.prompt + r.made, 0);
  while (finished < reqs.length) {
    while (i < reqs.length && reqs[i].arrive <= now) queue.push(reqs[i++]);
    while (queue.length && active.length < p.slots && kv() + queue[0].prompt + queue[0].made <= kvCapacity) {
      const r = queue.shift()!;
      const prefill = r.prompt + r.made;
      if (r.preempted) recomputed += prefill;
      now += prefill * p.prefill_ms_per_token; // on one GPU, prefill stalls every decode in the batch
      active.push(r);
    }
    if (!active.length) { now = reqs[i].arrive; continue; }
    now += p.decode_base_ms + p.decode_per_seq_ms * active.length;
    steps++;
    occupied += active.length;
    for (const r of active) {
      r.made++;
      if (r.first === null) r.first = now;
    }
    peak = Math.max(peak, kv());
    for (const r of active.filter((x) => x.made === x.output)) {
      r.done = now;
      finished++;
    }
    active = active.filter((x) => x.made !== x.output);
    while (kv() > kvCapacity && active.length > 1) {
      const victim = active.pop()!;
      victim.preempted++;
      preempts++;
      queue.unshift(victim);
    }
  }
  return metrics(reqs, now, steps, occupied, preempts, recomputed, peak);
}

/** Automatic prefix caching as note 07 describes it: full blocks only, each identified by its own
 *  tokens chained with its parent, so a match has to be exact from the first token. LRU eviction. */
export class PrefixCache {
  private blocks = new Map<string, true>(); // a Map keeps insertion order, which gives LRU
  private ids = new Map<string, number>();
  hitTokens = 0;
  totalTokens = 0;
  constructor(private capacity: number, private block: number) {}
  /** Returns how many tokens need prefill, and caches this prompt's full blocks. */
  lookup(tokens: number[]): number {
    let parent = 0, hits = 0, matching = true;
    for (let start = 0; start + this.block <= tokens.length; start += this.block) {
      const key = `${parent}|${tokens.slice(start, start + this.block).join(",")}`;
      if (matching && this.blocks.has(key)) {
        hits += this.block;
        this.blocks.delete(key);
        this.blocks.set(key, true);
      } else {
        matching = false;
        this.blocks.delete(key);
        this.blocks.set(key, true);
        if (this.blocks.size > this.capacity) this.blocks.delete(this.blocks.keys().next().value!);
      }
      if (!this.ids.has(key)) this.ids.set(key, this.ids.size + 1);
      parent = this.ids.get(key)!;
    }
    this.hitTokens += hits;
    this.totalTokens += tokens.length;
    return tokens.length - hits;
  }
  get hitRate(): number {
    return this.hitTokens / this.totalTokens;
  }
}

/** Every turn of every session, interleaved. `layout` is where the changing token goes:
 *  `stable` puts it last, `stamp_after_system` puts it between the system prompt and the
 *  history, and `stamp_first` puts it at the very start. */
export function sessionPrompts(p: Params, layout: string): number[][] {
  const rng = new Rng(p.seed);
  const tok = (n: number) => Array.from({ length: n }, () => rng.between(0, 50000));
  const system = tok(p.system_tokens);
  const prompts: number[][] = [];
  const histories: number[][] = Array.from({ length: p.sessions }, () => []);
  let stamp = 60000;
  for (let turn = 0; turn < p.turns; turn++) {
    for (let s = 0; s < p.sessions; s++) {
      histories[s] = [...histories[s], ...tok(p.turn_tokens)];
      stamp++;
      if (layout === "stable") prompts.push([...system, ...histories[s], stamp]);
      else if (layout === "stamp_after_system") prompts.push([...system, stamp, ...histories[s]]);
      else prompts.push([stamp, ...system, ...histories[s]]);
    }
  }
  return prompts;
}

export function runPrefix(p: Params, layout: string, capacity: number): [number, number] {
  const cache = new PrefixCache(capacity, p.block_tokens);
  const prompts = sessionPrompts(p, layout);
  const prefillTokens = prompts.reduce((a, t) => a + cache.lookup(t), 0);
  return [cache.hitRate, (prefillTokens * p.prefill_ms_per_token) / prompts.length];
}
