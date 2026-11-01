"""Discrete simulations of the mechanisms in notes 06 and 07. Timing comes from params.json, whose
numbers are assumptions and not measurements. Only the shape of each comparison means anything."""
from __future__ import annotations

import json
import math
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

PARAMS = json.loads((Path(__file__).parent / "params.json").read_text())


class Rng:
    """A linear congruential generator, written out so Python and TypeScript draw the same numbers."""

    def __init__(self, seed: int):
        self.x = seed

    def next(self) -> float:
        self.x = (self.x * 1664525 + 1013904223) % 4294967296
        return self.x / 4294967296

    def between(self, lo: int, hi: int) -> int:
        return lo + math.floor(self.next() * (hi - lo + 1))


@dataclass
class Req:
    id: int
    arrive: float
    prompt: int
    output: int
    made: int = 0
    first: float | None = None
    done: float | None = None
    preempted: int = 0


def workload(p: dict, mean_gap_ms: float) -> list[Req]:
    rng = Rng(p["seed"])
    t, out = 0.0, []
    for i in range(p["requests"]):
        t += -math.log(1 - rng.next()) * mean_gap_ms
        band = p["long_output"] if rng.next() < p["long_share"] else p["short_output"]
        out.append(Req(i, t, rng.between(*p["prompt_tokens"]), rng.between(*band)))
    return out


def percentile(xs: list[float], q: float) -> float:
    s = sorted(xs)
    return s[min(len(s) - 1, math.ceil(q * len(s)) - 1)]


@dataclass
class Metrics:
    ttft_p50: float
    ttft_p95: float
    e2e_p50: float
    e2e_p95: float
    tokens_per_s: float
    mean_batch: float
    preemptions: int = 0
    recomputed_tokens: int = 0
    peak_kv: int = 0


def _metrics(reqs: list[Req], end: float, steps: int, occupied: int, preempts=0, recomputed=0, peak=0) -> Metrics:
    ttft = [r.first - r.arrive for r in reqs]
    e2e = [r.done - r.arrive for r in reqs]
    return Metrics(percentile(ttft, 0.5), percentile(ttft, 0.95), percentile(e2e, 0.5), percentile(e2e, 0.95),
                   sum(r.output for r in reqs) / (end / 1000), occupied / steps, preempts, recomputed, peak)


def run_batched(reqs: list[Req], p: dict, window: float) -> Metrics:
    """Static (window is infinite) and dynamic batching. A batch runs until its longest member
    finishes, and a finished sequence's slot stays empty and still costs a step."""
    now, i, queue, steps, occupied = 0.0, 0, [], 0, 0
    while i < len(reqs) or queue:
        while i < len(reqs) and reqs[i].arrive <= now:
            queue.append(reqs[i])
            i += 1
        if not queue:
            now = reqs[i].arrive
            continue
        deadline = queue[0].arrive + window
        if len(queue) < p["slots"] and now < deadline and i < len(reqs):
            now = min(reqs[i].arrive, deadline)
            continue
        batch, queue = queue[: p["slots"]], queue[p["slots"] :]
        now += sum(r.prompt for r in batch) * p["prefill_ms_per_token"]
        for step in range(1, max(r.output for r in batch) + 1):
            now += p["decode_base_ms"] + p["decode_per_seq_ms"] * len(batch)
            steps += 1
            for r in batch:
                if step == 1:
                    r.first = now
                if step == r.output:
                    r.done = now
                if step <= r.output:
                    occupied += 1
    return _metrics(reqs, now, steps, occupied)


def run_continuous(reqs: list[Req], p: dict, kv_capacity: float = math.inf) -> Metrics:
    """Iteration-level scheduling: after every decode step, finished sequences leave and waiting ones
    join. The KV cache holds one token per prompt and generated token. Over capacity, the most recently
    admitted sequence is evicted, and it recomputes everything when it is readmitted."""
    now, i, steps, occupied, preempts, recomputed, peak = 0.0, 0, 0, 0, 0, 0, 0
    queue: list[Req] = []
    active: list[Req] = []
    kv = lambda: sum(r.prompt + r.made for r in active)
    finished = 0
    while finished < len(reqs):
        while i < len(reqs) and reqs[i].arrive <= now:
            queue.append(reqs[i])
            i += 1
        while queue and len(active) < p["slots"] and kv() + queue[0].prompt + queue[0].made <= kv_capacity:
            r = queue.pop(0)
            prefill = r.prompt + r.made
            if r.preempted:
                recomputed += prefill
            now += prefill * p["prefill_ms_per_token"]  # on one GPU, prefill stalls every decode in the batch
            active.append(r)
        if not active:
            now = reqs[i].arrive
            continue
        now += p["decode_base_ms"] + p["decode_per_seq_ms"] * len(active)
        steps += 1
        occupied += len(active)
        for r in active:
            r.made += 1
            if r.first is None:
                r.first = now
        peak = max(peak, kv())
        for r in [r for r in active if r.made == r.output]:
            r.done = now
            finished += 1
            active.remove(r)
        while kv() > kv_capacity and len(active) > 1:
            victim = active.pop()
            victim.preempted += 1
            preempts += 1
            queue.insert(0, victim)
    return _metrics(reqs, now, steps, occupied, preempts, recomputed, peak)


class PrefixCache:
    """Automatic prefix caching as note 07 describes it: full blocks only, each identified by its own
    tokens chained with its parent, so a match has to be exact from the first token. LRU eviction."""

    def __init__(self, capacity: int, block: int):
        self.capacity, self.block = capacity, block
        self.blocks: OrderedDict[tuple, bool] = OrderedDict()
        self.ids: dict[tuple, int] = {}
        self.hit_tokens = self.total_tokens = 0

    def lookup(self, tokens: list[int]) -> int:
        """Returns how many tokens need prefill, and caches this prompt's full blocks."""
        parent = 0
        hits, matching = 0, True
        for start in range(0, len(tokens) - self.block + 1, self.block):
            key = (parent, tuple(tokens[start : start + self.block]))
            if matching and key in self.blocks:
                hits += self.block
                self.blocks.move_to_end(key)
            else:
                matching = False
                self.blocks[key] = True
                self.blocks.move_to_end(key)
                if len(self.blocks) > self.capacity:
                    self.blocks.popitem(last=False)
            parent = self.ids.setdefault(key, len(self.ids) + 1)
        self.hit_tokens += hits
        self.total_tokens += len(tokens)
        return len(tokens) - hits

    @property
    def hit_rate(self) -> float:
        return self.hit_tokens / self.total_tokens


def session_prompts(p: dict, layout: str) -> list[list[int]]:
    """Every turn of every session, interleaved. `layout` is where the changing token goes:
    `stable` puts it last, `stamp_after_system` puts it between the system prompt and the
    history, and `stamp_first` puts it at the very start."""
    rng = Rng(p["seed"])
    tok = lambda n: [rng.between(0, 50000) for _ in range(n)]
    system = tok(p["system_tokens"])
    prompts: list[list[int]] = []
    histories = [[] for _ in range(p["sessions"])]
    stamp = 60000
    for turn in range(p["turns"]):
        for s in range(p["sessions"]):
            histories[s] = histories[s] + tok(p["turn_tokens"])
            stamp += 1
            body = system + histories[s]
            if layout == "stable":
                prompts.append(body + [stamp])
            elif layout == "stamp_after_system":
                prompts.append(system + [stamp] + histories[s])
            else:
                prompts.append([stamp] + body)
    return prompts


def run_prefix(p: dict, layout: str, capacity: int) -> tuple[float, float]:
    cache = PrefixCache(capacity, p["block_tokens"])
    prompts = session_prompts(p, layout)
    prefill_tokens = sum(cache.lookup(t) for t in prompts)
    return cache.hit_rate, prefill_tokens * p["prefill_ms_per_token"] / len(prompts)
