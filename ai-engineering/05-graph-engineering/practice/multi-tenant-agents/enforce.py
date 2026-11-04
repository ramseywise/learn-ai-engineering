"""The enforcement layer. Each control sits beside the naive version a team usually writes first, behind one interface,
so run.py and test.py can swap them and watch the property hold or break.

| Control | Holds | Breaks |
|---|---|---|
| budget | ReservationLedger | RunScopedBudget, CheckThenSpend |
| retrieval | ScopedRetriever | PostFilterRetriever |
| tools | ToolLayer | PromptOnlyTools |
| queueing | FairQueue with TokenBucket | FifoQueue |
| traces | TenantTraces | AmbientTraces |
| quality | tenant_quality | fleet_mean_alert |
"""
from __future__ import annotations

import math
import re
import sqlite3
import statistics
from collections import Counter, defaultdict, deque
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field

from tenancy import TOOL_CATALOG


# %% Budget
class BudgetExceeded(Exception):
    pass


class BudgetBusy(BudgetExceeded):
    """Refused for now: enough of the budget is only held, not spent, so waiting may free it."""


@dataclass(frozen=True)
class Hold:
    id: int
    tenant: str
    run_id: str
    tokens: int


class RunScopedBudget:
    """What a run-scoped state object can do: read the tenant's spend once at start, then count its own calls."""

    def __init__(self, limits: dict[str, int]):
        self.limits, self.committed = limits, Counter()
        self._runs: dict[str, dict] = {}

    def before_call(self, tenant, run_id, need) -> Hold:
        run = self._runs.setdefault(run_id, {"seen_at_start": self.committed[tenant], "own": 0})
        if run["seen_at_start"] + run["own"] + need > self.limits[tenant]:
            raise BudgetExceeded(tenant)
        return Hold(0, tenant, run_id, need)

    def after_call(self, hold, actual):
        self.committed[hold.tenant] += actual
        self._runs[hold.run_id]["own"] += actual

    def spent(self, tenant) -> int:
        return self.committed[tenant]


class CheckThenSpend:
    """A shared counter, checked before the await and written after it. Every run in flight passes the same check."""

    def __init__(self, limits: dict[str, int]):
        self.limits, self.committed = limits, Counter()

    def before_call(self, tenant, run_id, need) -> Hold:
        if self.committed[tenant] + need > self.limits[tenant]:
            raise BudgetExceeded(tenant)
        return Hold(0, tenant, run_id, need)

    def after_call(self, hold, actual):
        self.committed[hold.tenant] += actual

    def spent(self, tenant) -> int:
        return self.committed[tenant]


class ReservationLedger:
    """Reserve the worst case before the call, settle to the actual after it.

    The conditional UPDATE is the whole trick: check and write are one statement, so it stays atomic across tasks and
    across processes sharing the file. An asyncio-only dict would also pass the single-process test, and would then
    fail the day a second worker starts. Postgres or a Redis script gives the same statement in production.
    """

    def __init__(self, limits: dict[str, int], path: str = ":memory:", wait: bool = True, clock=lambda: 0):
        self.db = sqlite3.connect(path, timeout=30, isolation_level=None)
        self.wait, self.clock = wait, clock
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS ledger (tenant TEXT PRIMARY KEY, cap INT, spent INT DEFAULT 0, held INT DEFAULT 0);
            CREATE TABLE IF NOT EXISTS holds (id INTEGER PRIMARY KEY, tenant TEXT, run_id TEXT, tokens INT,
                                              state TEXT DEFAULT 'open', created INT);
        """)
        for tenant, cap in limits.items():
            self.db.execute("INSERT OR IGNORE INTO ledger (tenant, cap) VALUES (?, ?)", (tenant, cap))

    def before_call(self, tenant, run_id, need) -> Hold:
        self.db.execute("BEGIN IMMEDIATE")
        cur = self.db.execute("UPDATE ledger SET held = held + ? WHERE tenant = ? AND spent + held + ? <= cap",
                              (need, tenant, need))
        if cur.rowcount == 1:
            cur = self.db.execute("INSERT INTO holds (tenant, run_id, tokens, created) VALUES (?, ?, ?, ?)",
                                  (tenant, run_id, need, self.clock()))
            self.db.execute("COMMIT")
            return Hold(cur.lastrowid, tenant, run_id, need)
        row = self.db.execute("SELECT spent, cap FROM ledger WHERE tenant = ?", (tenant,)).fetchone()
        self.db.execute("ROLLBACK")
        if row is None:
            raise BudgetExceeded(f"no ledger row for {tenant}")  # fail closed
        if self.wait and row[0] + need <= row[1]:
            raise BudgetBusy(tenant)
        raise BudgetExceeded(tenant)

    def after_call(self, hold: Hold, actual: int) -> None:
        """Settling twice charges once, so a retry of the settle can't double-bill. A settle arriving after its hold
        expired still charges, because the provider did bill for it, which is the one way spend can pass the cap."""
        self.db.execute("BEGIN IMMEDIATE")
        state = self.db.execute("SELECT state FROM holds WHERE id = ?", (hold.id,)).fetchone()[0]
        if state != "settled":
            released = hold.tokens if state == "open" else 0
            self.db.execute("UPDATE holds SET state = 'settled' WHERE id = ?", (hold.id,))
            self.db.execute("UPDATE ledger SET held = held - ?, spent = spent + ? WHERE tenant = ?",
                            (released, actual, hold.tenant))
        self.db.execute("COMMIT")

    def expire(self, older_than: int) -> int:
        """A worker that dies mid-call never settles. Without this its hold shrinks the tenant's budget for good."""
        self.db.execute("BEGIN IMMEDIATE")
        stale = self.db.execute("SELECT id, tenant, tokens FROM holds WHERE state = 'open' AND created < ?",
                                (older_than,)).fetchall()
        for hold_id, tenant, tokens in stale:
            self.db.execute("UPDATE holds SET state = 'expired' WHERE id = ?", (hold_id,))
            self.db.execute("UPDATE ledger SET held = held - ? WHERE tenant = ?", (tokens, tenant))
        self.db.execute("COMMIT")
        return len(stale)

    def spent(self, tenant) -> int:
        return self.db.execute("SELECT spent FROM ledger WHERE tenant = ?", (tenant,)).fetchone()[0]

    def held(self, tenant) -> int:
        return self.db.execute("SELECT held FROM ledger WHERE tenant = ?", (tenant,)).fetchone()[0]


def _hammer(path: str, tenant: str, calls: int, need: int, actual: int) -> int:
    ledger = ReservationLedger({}, path=path)
    granted = 0
    for i in range(calls):
        try:
            hold = ledger.before_call(tenant, f"p{i}", need)
        except BudgetExceeded:
            continue
        granted += 1
        ledger.after_call(hold, actual)
    return granted


def hammer_from_processes(path: str, tenant: str, cap: int, workers: int, calls: int, need: int, actual: int) -> dict:
    """Several real OS processes spending against one ledger file."""
    ReservationLedger({tenant: cap}, path=path).db.close()
    with ProcessPoolExecutor(workers) as pool:
        futures = [pool.submit(_hammer, path, tenant, calls, need, actual) for _ in range(workers)]
        granted = sum(f.result() for f in futures)
    ledger = ReservationLedger({}, path=path)
    return {"granted": granted, "spent": ledger.spent(tenant), "held": ledger.held(tenant), "cap": cap}


# %% Retrieval
def _vector(text: str) -> Counter:
    return Counter(re.findall(r"[a-z0-9]+", text.lower()))


def _cosine(a: Counter, b: Counter) -> float:
    dot = sum(n * b[w] for w, n in a.items() if w in b)
    return dot / (math.sqrt(sum(n * n for n in a.values())) * math.sqrt(sum(n * n for n in b.values())) or 1)


class Index:
    """A brute-force bag-of-words index. The ranking is a stand-in; where the filter sits is the lesson."""

    def __init__(self, docs):
        self.docs = [(d, _vector(d.text)) for d in docs]

    def top_k(self, query: str, k: int, where=None) -> list:
        q = _vector(query)
        candidates = [(d, v) for d, v in self.docs if where is None or where(d)]  # filter first, then rank
        candidates.sort(key=lambda item: (-_cosine(q, item[1]), item[0].id))
        return [d for d, _ in candidates[:k]]


@dataclass
class Retrieved:
    docs: list            # what reaches the agent's context
    exposed: list         # everything any component saw on the way, such as a reranker prompt


class ScopedRetriever:
    """The scope predicate is part of the query, so foreign text is never a candidate and k means k of yours.
    `IN` has no branch for a missing value: a document whose scope was lost matches nobody."""

    def __init__(self, index: Index):
        self.index = index

    def retrieve(self, scopes, query: str, k: int) -> Retrieved:
        allowed = set(scopes)
        docs = self.index.top_k(query, k, where=lambda d: d.scope in allowed)
        return Retrieved(docs, list(docs))


class PostFilterRetriever:
    """Rank everyone's documents, rerank, then drop what isn't yours. Three separate faults in five lines:
    k is spent before the filter (starves), the reranker sees every candidate (exposes), and a document with no scope
    passes because the code only rejects a known mismatch (leaks into the answer)."""

    def __init__(self, index: Index):
        self.index = index

    def retrieve(self, scopes, query: str, k: int) -> Retrieved:
        allowed = set(scopes)
        candidates = self.index.top_k(query, k)
        reranker_prompt = list(candidates)  # sent to a cross-encoder or a model, and usually logged
        return Retrieved([d for d in candidates if d.scope is None or d.scope in allowed], reranker_prompt)


# %% Tools
class ToolDenied(Exception):
    pass


class _ToolBackend:
    def __init__(self, records: dict[str, dict]):
        self.records = records
        self.effects: list[tuple[str, str, dict]] = []  # side effects that really happened, as (tenant, tool, args)

    def _write(self, tenant, name, args) -> str:
        self.effects.append((tenant, name, args))
        return f"ok: {name} done"


class ToolLayer(_ToolBackend):
    """The allowlist is checked here, at execution. The tenant comes from the run, never from the model's arguments."""

    def call(self, tenant: str, allowed, name: str, args: dict) -> str:
        if name not in allowed:
            raise ToolDenied(f"{name} is not enabled for {tenant}")
        if name == "lookup_record":
            record = self.records.get(args.get("record_id"))
            if record is None or record["owner"] != tenant:
                return "not found"  # the same answer as a missing id, so it doesn't reveal that the id exists
            return f"ok: {record['text']}"
        return self._write(tenant, name, args)


class PromptOnlyTools(_ToolBackend):
    """The allowlist is a sentence in the system prompt, and the executor runs whatever the model names."""

    def call(self, tenant: str, allowed, name: str, args: dict) -> str:
        if name not in TOOL_CATALOG:
            raise ToolDenied(f"no such tool {name}")
        if name == "lookup_record":
            record = self.records.get(args.get("record_id"))
            return f"ok: {record['text']}" if record else "not found"
        return self._write(tenant, name, args)


# %% Queueing
@dataclass(frozen=True)
class Request:
    id: str
    tenant: str
    arrival: int
    cost: int = 1
    ticket: str = ""


class TokenBucket:
    def __init__(self, rate: float, burst: int):
        self.rate, self.burst, self.tokens, self.last = rate, burst, float(burst), 0

    def allow(self, now: int) -> bool:
        self.tokens = min(self.burst, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class FifoQueue:
    """One line for everybody: whoever bursts first is in front of everyone else."""

    def __init__(self, weights=None):
        self.q = deque()

    def push(self, r: Request):
        self.q.append(r)

    def pop(self) -> Request:
        return self.q.popleft()

    def __len__(self):
        return len(self.q)


class FairQueue:
    """Deficit round robin. Each tenant has its own line and earns quantum x weight per turn, spent in request cost, so
    a tenant sending heavier requests doesn't get more capacity. An idle tenant takes no turn, so no capacity is wasted."""

    def __init__(self, weights: dict[str, int], quantum: int = 100):
        self.weights, self.quantum = weights, quantum
        self.lines: dict[str, deque] = defaultdict(deque)
        self.active: deque[str] = deque()
        self.deficit: Counter = Counter()
        self._credited = False

    def push(self, r: Request):
        if not self.lines[r.tenant]:
            self.active.append(r.tenant)
        self.lines[r.tenant].append(r)

    def pop(self) -> Request:
        while True:
            tenant = self.active[0]
            if not self._credited:
                self.deficit[tenant] += self.quantum * self.weights.get(tenant, 1)
                self._credited = True
            line = self.lines[tenant]
            if line[0].cost <= self.deficit[tenant]:
                r = line.popleft()
                self.deficit[tenant] -= r.cost
                if not line:  # an empty line banks nothing, or a tenant could save up a burst while idle
                    self.deficit[tenant] = 0
                    self.active.popleft()
                    self._credited = False
                return r
            self.active.rotate(-1)
            self._credited = False

    def __len__(self):
        return sum(len(line) for line in self.lines.values())


@dataclass
class LoadResult:
    waits: dict = field(default_factory=lambda: defaultdict(list))
    rejected: Counter = field(default_factory=Counter)
    served_cost: Counter = field(default_factory=Counter)
    finished_at: int = 0

    def p95(self, tenant) -> int:
        w = sorted(self.waits[tenant])
        return w[int(0.95 * (len(w) - 1))] if w else 0

    def p50(self, tenant) -> float:
        return statistics.median(self.waits[tenant]) if self.waits[tenant] else 0


def simulate_load(queue, arrivals: list[Request], capacity: int, limiters=None) -> LoadResult:
    """A discrete-time server with `capacity` cost units per tick. One tick stands for one simulated second."""
    by_tick = defaultdict(list)
    for r in arrivals:
        by_tick[r.arrival].append(r)
    result, tick, credit, last = LoadResult(), 0, 0, max(by_tick)
    while tick <= last or len(queue):
        for r in by_tick[tick]:
            if limiters and not limiters[r.tenant].allow(tick):
                result.rejected[r.tenant] += 1  # a 429 with Retry-After, not a place in the line
            else:
                queue.push(r)
        credit += capacity
        while credit > 0 and len(queue):
            r = queue.pop()
            credit -= r.cost
            result.waits[r.tenant].append(tick - r.arrival)
            result.served_cost[r.tenant] += r.cost
        if not len(queue):
            credit = min(credit, 0)  # an idle server can't bank capacity for later
        result.finished_at = tick
        tick += 1
    return result


# %% Traces
@dataclass(frozen=True)
class Span:
    tenant: str
    run_id: str
    config_version: int
    node: str
    status: str = "ok"
    detail: str = ""
    tokens: int = 0


class TenantTraces:
    """The span is stamped from the run's own context, and every read names the caller and sees only that tenant."""

    def __init__(self):
        self._spans: dict[str, list[Span]] = defaultdict(list)

    def begin(self, ctx) -> None:
        pass

    def record(self, ctx, node, status="ok", detail="", tokens=0) -> None:
        self._spans[ctx.tenant_id].append(Span(ctx.tenant_id, ctx.run_id, ctx.config.version, node, status, detail, tokens))

    def read(self, caller: str, run_id: str | None = None) -> list[Span]:
        return [s for s in self._spans[caller] if run_id is None or s.run_id == run_id]

    def all_spans(self) -> list[Span]:
        return [s for spans in self._spans.values() for s in spans]


class AmbientTraces:
    """The tenant lives in one module-level slot, set when a run starts. That works until two runs overlap, and the
    read path trusts a run_id with no check on the caller."""

    def __init__(self):
        self._spans: list[Span] = []
        self.current_tenant = None

    def begin(self, ctx) -> None:
        self.current_tenant = ctx.tenant_id

    def record(self, ctx, node, status="ok", detail="", tokens=0) -> None:
        self._spans.append(Span(self.current_tenant, ctx.run_id, ctx.config.version, node, status, detail, tokens))

    def read(self, caller: str, run_id: str | None = None) -> list[Span]:
        if run_id is not None:
            return [s for s in self._spans if s.run_id == run_id]
        return [s for s in self._spans if s.tenant == caller]

    def all_spans(self) -> list[Span]:
        return list(self._spans)


# %% Quality
Z_ALERT = 2.33   # one-sided, about 1% per test if the normal approximation holds
MIN_RUNS = 30
FLEET_DROP_ALERT = 0.02


def _rate(counts: tuple[int, int]) -> float:
    return counts[0] / counts[1] if counts[1] else 0.0


def fleet_rate(counts: dict[str, tuple[int, int]]) -> float:
    return sum(c[0] for c in counts.values()) / (sum(c[1] for c in counts.values()) or 1)


def fleet_mean_alert(before: dict, after: dict) -> set[str]:
    """Alert when the traffic-weighted pass rate falls. It names nobody, and a large tenant can outvote a small one."""
    return {"fleet"} if fleet_rate(before) - fleet_rate(after) > FLEET_DROP_ALERT else set()


def regression_z(before: tuple[int, int], after: tuple[int, int]) -> float:
    """Two-proportion z, positive when the pass rate fell. Counts are (passes, runs)."""
    pooled = (before[0] + after[0]) / (before[1] + after[1])
    se = math.sqrt(pooled * (1 - pooled) * (1 / before[1] + 1 / after[1])) or 1
    return (_rate(before) - _rate(after)) / se


def tenant_status(before: tuple[int, int], after: tuple[int, int]) -> str:
    """Three answers, not two: too few runs is not a pass."""
    if min(before[1], after[1]) < MIN_RUNS:
        return "too_few_runs"
    return "regressed" if regression_z(before, after) > Z_ALERT else "ok"


def tenant_quality(before: dict, after: dict) -> dict[str, str]:
    return {t: tenant_status(before[t], after.get(t, (0, 0))) for t in before}


def per_tenant_alert(before: dict, after: dict) -> set[str]:
    return {t for t, status in tenant_quality(before, after).items() if status == "regressed"}


def canary_decision(stable: tuple[int, int], canary: tuple[int, int]) -> str:
    return {"too_few_runs": "wait", "regressed": "rollback", "ok": "promote"}[tenant_status(stable, canary)]
