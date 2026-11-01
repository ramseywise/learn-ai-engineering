"""A stubbed support agent that emits synthetic traces with failures seeded.

No model is called. The agent's control flow is real enough to produce the shape of
production telemetry, and each trace records the failure it was seeded with in
`seeded_failure`. Scorers and judges must not read that field; it exists so a chapter
can measure how well a check finds what was planted.

The fortnight has a plot. `v1` runs from 5 October. `v2.0` ships on 14 October with a
timestamp in the system prompt, which breaks the prompt cache, and with a retriever
change that raises fabricated and distorted answers. `v2.1` fixes the cache on
17 October but not the answers. Separately, from 11 October a vendor behind the
`get_invoice` tool starts stalling on some calls.
"""

import json
import math
import random
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone

from .kb import ANSWERS, BASE, BY_ROUTE, DISTORTED, DOCS, QUESTIONS
from .pricing import llm_cost
from .scorers import online_scores

START = datetime(2026, 10, 5, tzinfo=timezone.utc)
V2_0 = datetime(2026, 10, 14, tzinfo=timezone.utc)
V2_1 = datetime(2026, 10, 17, tzinfo=timezone.utc)
VENDOR_STALL = datetime(2026, 10, 11, tzinfo=timezone.utc)

ROUTES = {"billing": 0.35, "account": 0.25, "technical": 0.25, "refund": 0.15}
ROUTER_MODEL = "claude-haiku-5-5"
ANSWER_MODEL = "claude-opus-5-5"
SYSTEM_PROMPT_TOKENS = 4200
ROUTER_PROMPT_TOKENS = 420


@dataclass
class Span:
    span_id: str
    parent_id: str | None
    name: str
    kind: str  # agent | generation | tool | retriever | guardrail
    start_ms: float
    latency_ms: float
    model: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    tool_args: dict | None = None
    tool_result: dict | None = None
    level: str = "DEFAULT"  # DEFAULT | WARNING | ERROR
    error: str | None = None

    @property
    def cost_usd(self):
        if self.model is None:
            return 0.0
        return llm_cost(self.model, self.input_tokens, self.output_tokens,
                        self.cache_read_tokens, self.cache_write_tokens)


@dataclass
class Trace:
    trace_id: str
    session_id: str
    ts: str
    agent: str
    release: str
    prompt_version: str
    git_commit: str
    route: str
    true_route: str
    language: str
    question: str
    answer: str
    citations: list[str]
    retrieved_urls: list[str]
    documents: list[dict]
    amount_eur: int | None
    escalated: bool
    outcome: str  # resolved | escalated | abandoned | error
    latency_ms: float
    spans: list[Span] = field(default_factory=list)
    scores: dict = field(default_factory=dict)
    seeded_failure: str | None = None

    @property
    def cost_usd(self):
        return sum(s.cost_usd for s in self.spans)


def _release(ts):
    if ts < V2_0:
        return "v1", "a41f0c2", "answer-v7"
    if ts < V2_1:
        return "v2.0", "c93be17", "answer-v8"
    return "v2.1", "d07aa58", "answer-v8"


def _seed_failure(rng, ts, route, language):
    """Pick at most one planted failure for this turn."""
    v2 = ts >= V2_0
    rates = {
        "hallucinated_citation": 0.05 if v2 and route == "billing" else 0.012,
        "distorted_claim": 0.06 if v2 and route in ("billing", "refund") else 0.012,
        "retrieval_miss": 0.03,
        "retry_loop": 0.02,
        "wrong_route": 0.03,
        "missed_escalation": (0.12 if v2 else 0.03) if route == "refund" else 0.0,
        "language_mismatch": 0.05 if language == "da" else 0.0,
        "slow_tool": 0.08 if route == "billing" and ts >= VENDOR_STALL else 0.0,
    }
    u = rng.random()
    for name, p in rates.items():
        if u < p:
            return name
        u -= p
    return None


class _Builder:
    def __init__(self, rng, trace_no):
        self.rng, self.trace_no, self.n, self.clock, self.spans = rng, trace_no, 0, 0.0, []
        self.root_id = self._new_id()

    def _new_id(self):
        self.n += 1
        return f"s{self.trace_no:04d}-{self.n:02d}"

    def add(self, name, kind, latency_ms, **kw):
        span = Span(self._new_id(), self.root_id, name, kind, round(self.clock, 1), round(latency_ms, 1), **kw)
        self.spans.append(span)
        self.clock += latency_ms
        return span


def _lognormal(rng, median, sigma):
    return median * math.exp(rng.gauss(0, sigma))


def _answer_generation(b, rng, cache_broken, context_tokens, output_tokens):
    """One call to the answering model. The system prompt is the cached prefix."""
    reads = 0 if cache_broken else SYSTEM_PROMPT_TOKENS
    writes = SYSTEM_PROMPT_TOKENS if cache_broken else 0
    # Time to first token rises when the prefix has to be processed instead of read.
    ttft = _lognormal(rng, 1500 if cache_broken else 700, 0.25)
    latency = ttft + output_tokens / _lognormal(rng, 55, 0.15) * 1000
    return b.add("answer", "generation", latency, model=ANSWER_MODEL, input_tokens=context_tokens,
                 output_tokens=output_tokens, cache_read_tokens=reads, cache_write_tokens=writes)


def make_turn(rng, trace_no, ts):
    release, commit, prompt_version = _release(ts)
    true_route = rng.choices(list(ROUTES), weights=list(ROUTES.values()))[0]
    language = "da" if rng.random() < 0.30 else "en"
    failure = _seed_failure(rng, ts, true_route, language)
    route = true_route
    if failure == "wrong_route":
        route = rng.choice([r for r in ROUTES if r != true_route])

    doc = rng.choice(BY_ROUTE[true_route])
    if failure == "missed_escalation":  # only a refund above the limit can be wrongly kept
        doc = next(d for d in BY_ROUTE["refund"] if d["url"].endswith("/policy"))
    lang_i = 1 if language == "da" else 0
    amount = None
    question = QUESTIONS[doc["url"]][lang_i]
    if "{amount}" in question:
        amount = rng.choice([120, 180, 240, 300, 450, 650, 800, 1200, 2400])
        if failure == "missed_escalation":
            amount = rng.choice([650, 800, 1200, 2400])
        question = question.format(amount=amount)

    b = _Builder(rng, trace_no)
    cache_broken = release == "v2.0"

    b.add("input_guardrail", "guardrail", _lognormal(rng, 6, 0.3), tool_result={"blocked": False})
    b.add("route", "generation", _lognormal(rng, 380, 0.25), model=ROUTER_MODEL,
          input_tokens=rng.randint(40, 90), output_tokens=rng.randint(6, 14),
          cache_read_tokens=ROUTER_PROMPT_TOKENS, tool_result={"route": route})

    # Retrieval. A retry loop is a failing search the model keeps calling.
    if failure == "retry_loop":
        for attempt in range(rng.randint(3, 6)):
            b.add("kb_search", "retriever", _lognormal(rng, 900, 0.4), level="ERROR", error="TimeoutError: index shard 2",
                  tool_args={"query": question, "attempt": attempt + 1}, tool_result={"passage_count": 0, "top_score": 0.0, "urls": []})
            _answer_generation(b, rng, cache_broken, rng.randint(300, 700) + attempt * 180, rng.randint(40, 90))

    if failure in ("retrieval_miss", "wrong_route"):
        retrieved = rng.sample([d for d in DOCS if d["route"] != true_route], 2)
        top_score = round(rng.uniform(0.21, 0.44), 2)
    else:
        others = [d for d in BY_ROUTE[route] if d["url"] != doc["url"]]
        retrieved = [doc] + rng.sample(others, min(1, len(others)))
        top_score = round(rng.uniform(0.71, 0.94), 2)
    urls = [d["url"] for d in retrieved]
    b.add("kb_search", "retriever", _lognormal(rng, 160, 0.35), tool_args={"query": question},
          tool_result={"passage_count": len(retrieved), "top_score": top_score, "urls": urls})

    # Account lookups, and the tool whose vendor starts stalling.
    if true_route in ("billing", "refund"):
        stalled = failure == "slow_tool"
        latency = _lognormal(rng, 14000, 0.45) if stalled else _lognormal(rng, 140, 0.3)
        b.add("get_invoice", "tool", latency, level="WARNING" if stalled else "DEFAULT",
              tool_args={"customer": f"c{rng.randint(1000, 9999)}"}, tool_result={"found": True})
    elif true_route == "account":
        b.add("get_account", "tool", _lognormal(rng, 90, 0.3), tool_args={"customer": f"c{rng.randint(1000, 9999)}"},
              tool_result={"plan": "Standard"})

    # The answer text, with its citations.
    answer_i = 0 if failure == "language_mismatch" else lang_i
    fact = doc["fact"]
    citations = [doc["url"]]
    if failure == "distorted_claim":
        fact = DISTORTED[fact]
    answer = ANSWERS[doc["url"]][answer_i].format(fact=fact)
    if failure == "hallucinated_citation":
        fact = DISTORTED[doc["fact"]]
        answer = ANSWERS[doc["url"]][answer_i].format(fact=fact)
        citations = [f"{BASE}/{true_route}/special-terms"]
    if failure in ("retrieval_miss", "wrong_route"):
        citations = [retrieved[0]["url"]]
        answer = ANSWERS[retrieved[0]["url"]][answer_i].format(fact=retrieved[0]["fact"])

    needs_human = amount is not None and amount > 500
    escalated = needs_human and failure != "missed_escalation"
    if escalated:
        answer = ("This refund is above what I can approve, so I have passed it to a colleague."
                  if answer_i == 0 else "Denne refusion er større end jeg kan godkende, så jeg har sendt den til en kollega.")
        citations = [f"{BASE}/refund/policy"]
        b.add("create_ticket", "tool", _lognormal(rng, 210, 0.3), tool_args={"queue": "refunds", "amount_eur": amount},
              tool_result={"ticket": f"T-{rng.randint(10000, 99999)}"})
    elif failure == "missed_escalation":
        answer = ("I have approved your refund." if answer_i == 0 else "Jeg har godkendt din refusion.") + " " + answer

    _answer_generation(b, rng, cache_broken, rng.randint(380, 1100), rng.randint(110, 420))
    b.add("grounding_check", "guardrail", _lognormal(rng, 12, 0.3))

    # Outcome. Failures make a resolution less likely, and a stall makes people leave.
    p_resolved = {"hallucinated_citation": 0.55, "distorted_claim": 0.70, "retrieval_miss": 0.25, "retry_loop": 0.30,
                  "wrong_route": 0.30, "missed_escalation": 0.80, "language_mismatch": 0.60, "slow_tool": 0.45}.get(failure, 0.86)
    if escalated:
        outcome = "escalated"
    elif failure == "retry_loop" and rng.random() < 0.35:
        outcome = "error"
    else:
        outcome = "resolved" if rng.random() < p_resolved else rng.choice(["abandoned", "abandoned", "escalated"])
    escalated = escalated or outcome == "escalated"

    total = b.clock
    root = Span(b.root_id, None, "agent_turn", "agent", 0.0, round(total, 1),
                tool_args={"message": question}, tool_result={"message": answer, "escalated": escalated},
                level="ERROR" if outcome == "error" else "DEFAULT")
    trace = Trace(
        trace_id=f"t{trace_no:05d}", session_id=f"sess-{rng.randint(1, 900):04d}", ts=ts.isoformat(),
        agent="support_agent", release=release, prompt_version=prompt_version, git_commit=commit,
        route=route, true_route=true_route, language=language, question=question, answer=answer,
        citations=citations, retrieved_urls=urls, documents=[{"url": d["url"], "text": d["text"]} for d in retrieved],
        amount_eur=amount, escalated=escalated, outcome=outcome, latency_ms=round(total, 1),
        spans=[root] + b.spans, seeded_failure=failure,
    )
    # Feedback arrives on about one turn in eight, as explicit feedback does.
    if rng.random() < 0.12:
        liked = outcome == "resolved" and failure is None
        trace.scores["user_feedback"] = float(liked if rng.random() < 0.9 else not liked)
    trace.scores.update(online_scores(trace))
    return trace


def generate_traces(seed=7, days=14, per_day=100):
    """The same seed gives the same fortnight, so every chapter sees the same incident."""
    rng = random.Random(seed)
    out, no = [], 0
    for day in range(days):
        for _ in range(per_day):
            no += 1
            ts = START + timedelta(days=day, seconds=rng.randint(0, 86399))
            out.append(make_turn(rng, no, ts))
    return sorted(out, key=lambda t: t.ts)


def to_jsonl(traces, path):
    with open(path, "w") as f:
        for t in traces:
            f.write(json.dumps(asdict(t), ensure_ascii=False) + "\n")


def load_jsonl(path):
    out = []
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            row["spans"] = [Span(**s) for s in row["spans"]]
            out.append(Trace(**row))
    return out


def print_tree(trace):
    """Print a trace the way a tracing UI lays it out."""
    print(f"{trace.trace_id}  {trace.route}/{trace.language}  {trace.release}  outcome={trace.outcome}  "
          f"{trace.latency_ms / 1000:.1f}s  ${trace.cost_usd:.4f}")
    for s in trace.spans[1:]:
        usage = ""
        if s.model:
            usage = f"  in={s.input_tokens} read={s.cache_read_tokens} write={s.cache_write_tokens} out={s.output_tokens}"
        flag = f"  {s.level}" if s.level != "DEFAULT" else ""
        print(f"  {s.name:<16}{s.kind:<11}{s.latency_ms:>9.0f} ms{usage}{flag}")
