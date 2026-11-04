# Lab: one agent core, many tenants (Python)

[Note 08](../../notes/08-governance-and-production.md) says a tenant budget has to hold across concurrent runs, and that
a run-scoped framework can't do it alone. This lab shows that happening, then fixes it, along with the other things
that break when one agent serves several clients: another tenant's text in the context, a tool enabled for the wrong
client, a neighbour's burst, traces filed under the wrong name, and a regression the fleet average hides.

The scenario is a fictional support-agent SaaS with four clients: Larkspur Clinic (healthcare), Tallow Legal (legal),
Pinwheel (retail) and Ferrous Freight (logistics). They share one agent core, and everything that differs between them
lives in [`tenants.json`](tenants.json). `test.py` checks that `agent.py` doesn't name any of them.

```bash
uv run run.py      # about 2 seconds, standard library only, no API key
uv run test.py     # about 4 seconds, the assertions
```

**What is real and what is generated.** The tenants, corpus, records, traffic and costs are generated, and the model is
a stub with planted misbehaviours. The asyncio scheduling, the SQLite ledger, the validation, the queues and the rubric
scoring are real. Model latency is counted in event-loop yields rather than milliseconds, so the task interleaving is
real asyncio and also repeatable. Every number below describes this setup, not any product.

## Why no LangGraph here

The sibling [LangGraph lab](../langgraph-graph/README.md) is about a graph. This one is about what sits underneath a
graph. A budget, a scoped query and a tool allowlist have to hold wherever calls converge, whatever orchestrates them,
and a run-scoped framework is the thing being shown not to be enough. So `agent.py` is a plain loop, and adding nodes
would not change a single number. To use these controls from a graph, call `complete_call`, `retriever.retrieve` and
`tools.call` inside your nodes.

## Files

| File | What it holds |
|---|---|
| `tenants.json` | The per-tenant config: prompt, rubric, tools, scopes, model alias, limits |
| `tenancy.py` | Validation, versioned `ConfigStore` with canary and rollback, `NaiveConfigStore` |
| `enforce.py` | Each control beside its naive version, behind one interface |
| `agent.py` | The one core, plus `serve`, the whole path from admission to answer |
| `model.py`, `stub.py` | The model call shape, the stub, and the generated corpus and records |
| `scenarios.py` | The experiments, each taking the implementation to test |
| `run.py`, `test.py` | Print the experiments; assert on them |

## What the run shows

Real output from `uv run run.py`, trimmed to the rows that carry the point.

```text
2. Budget: 60 overlapping runs of pinwheel-retail, cap 6,000 tokens
  budget                              billed  of cap  answered  refused
  run-scoped (reads spend at start)   13,879    231%        60        0
  shared counter, check then spend    11,291    188%        46       14
  ledger, refuse if held               3,005     50%        13       47
  ledger, wait for held to settle      5,688     95%        24       36
```

The bill is read at the model, not from the budget object, so a budget can't mark its own homework. A shared counter is
not the fix: every run checks it before the await and writes it after, so all the runs in flight pass the same check.
The ledger reserves the worst case before the await, in one conditional `UPDATE`, and settles to the actual after it.
Reserving has its own cost. Refusing whenever money is merely held leaves half the budget unused, because held money
comes back. Waiting for holds to settle uses 95% of it. `test.py` also hammers one ledger file from four OS processes,
because a dict guarded by the event loop would pass the single-process test and then fail when a second worker starts.

```text
3. Retrieval: 6 generic questions per tenant, top 3, over 578 generated documents
  retriever    tenant              no docs  no on-topic  foreign in context  foreign exposed
  post-filter  larkspur-clinic           3            6                   5               18
  post-filter  pinwheel-retail           0            3                   5               12
  in the query larkspur-clinic           0            0                   0                0
  in the query pinwheel-retail           0            0                   0                0
```

Post-filtering breaks three ways. **Starving:** the top 3 are spent on the biggest tenant before the filter runs, so
Larkspur, with 12 documents among 578, finds nothing on topic for any of its six questions. **Exposure:** the reranker
sees every candidate before the filter, and what it sees usually gets logged. **Leak:** a Tallow Legal document whose
scope was lost at ingest passes a filter that only rejects a known mismatch, and lands in other tenants' context. That
last one is really a fail-open bug and could exist anywhere, but a predicate in the query has no branch for a missing
value, so it fails closed. The price is that those five Tallow documents now match nobody, so they need their own alert.

```text
4. Tools: the stub tries issue_refund for a tenant that doesn't have it, and reads another tenant's record
  prompt only  refunds executed for larkspur: 1, denied spans: 0, foreign record in the answer: True
  tool layer   refunds executed for larkspur: 0, denied spans: 1, foreign record in the answer: False
```

The stub ignores the sentence in its prompt, as a model can after a prompt injection. The second failure is the one an
allowlist doesn't catch: `lookup_record` is allowed, and the record belongs to someone else. The tool takes the tenant
from the run, never from the model's arguments, and answers "not found" as it would for an id that doesn't exist.

```text
5. Queueing: pinwheel-retail bursts 400 requests at tick 50. Wait in ticks, one tick = one simulated second
  policy                  tenant               p50   p95  served  rejected
  one FIFO line           larkspur-clinic      154   224      60         0
  fair queue              larkspur-clinic        0     1      60         0
  fair queue              pinwheel-retail      166   289     550         0
  fair queue + rate limit larkspur-clinic        0     0      60         0
  fair queue + rate limit pinwheel-retail        0    10     169       381
```

The fair queue moves the wait onto the tenant who caused it, and it doesn't waste capacity: FIFO and the fair queue both
finish at tick 400. It still lets Pinwheel wait 289 ticks in its own line. The rate limit turns most of that wait into
381 fast rejections, which a client can retry.

```text
6. Traces: 40 overlapping runs across four tenants
  one ambient tenant slot  spans 120, filed under the wrong tenant 60, another tenant's spans readable by run_id 3
  stamped from the run     spans 120, filed under the wrong tenant 0, another tenant's spans readable by run_id 0

7. Quality: a shared model alias moves from v1 to v2 for every tenant (generated runs, planted fault)
  tenant               runs  v1 pass  v2 pass  status
  pinwheel-retail      1600    90.2%    94.8%  ok
  ferrous-freight       600    89.8%    96.2%  ok
  tallow-legal          200    82.0%    95.0%  ok
  larkspur-clinic       100    86.0%    49.0%  regressed
  fleet, by traffic    2500    89.3%    93.3%  alert: none
```

The fleet pass rate went up while one client's fell by 37 points, and that client is the one where a dropped clinician
caveat matters most. The per-tenant check has three answers, not two: a tenant with too few runs reports `too_few_runs`,
which is not a pass. The same check gates each config canary in section 1, where a tidied Larkspur prompt that loses the
caveat scores 0/67 and is rolled back while Tallow's harmless edit promotes. The naive store's fleet-wide undo does
the opposite: `rollback("larkspur-clinic")` leaves Larkspur on the bad prompt and undoes Tallow's good edit.

Section 8 runs everything at once, and `test.py` runs each paired property against the control and against the naive
version. If a check ever passes on the naive version, the test file itself fails, because that check proves nothing.

## Things to try

1. In `scenarios.py`, call `retrieval_scenario(PostFilterRetriever, k=50)`, which is the usual over-fetch fix. What
   happens to starving and to exposure? <details><summary>Answer</summary>Starving goes to zero, and Larkspur's foreign
   documents exposed to the reranker go from 18 to 293. The five in its context are still there. Over-fetching trades
   one fault for more of another.</details>
2. In `tenants.json`, set every `max_tokens` to 60, then to 1000, and rerun section 2. What does the reservation cost
   you? <details><summary>Answer</summary>Reserving 60 bills 5,869 tokens either way, with no gap between the two ledger
   rows. Reserving 1000 bills 4,907 when waiting and 1,193 when refusing. The stub's answers never get near either limit,
   so the only thing that moved is how much budget sits held against a worst case.</details>
3. Give `AmbientTraces` a `contextvars.ContextVar` instead of its plain attribute, set in `begin` and read in `record`.
   <details><summary>Answer</summary>Misfiled spans go from 60 to 0, since each asyncio task has its own copy of the
   context. The read still leaks 3 spans, because the read path has its own check to add.</details>
4. Change Larkspur's volume in `QUALITY_VOLUME` to 20, 40 and 600. When does each alert fire?
   <details><summary>Answer</summary>At 20 the tenant reports `too_few_runs`, at 40 it reports `regressed`. The fleet
   alert stays silent until Larkspur has 600 runs, when the fleet mean falls from 88.9% to 86.7%.</details>
5. Set Pinwheel's `rate_per_s` to 20 and `burst` to 400. Do the quiet tenants suffer?
   <details><summary>Answer</summary>Barely: their p95 goes from 0 to 1 tick, and Pinwheel's own p95 goes to 288. The
   fair queue protects the neighbours; the rate limit protects Pinwheel from its own backlog.</details>
6. Change a tenant's `monthly_tokens` in a new config version and promote it. Does the ledger notice?
   <details><summary>Answer</summary>No. The ledger's cap is set once at start-up, which is a gap on purpose. Fix it by
   having `promote` and `rollback` write the cap, and add a test that a rollback restores it.</details>

## What this lab leaves out

A reservation can refuse a run's second call after its first was billed, so section 2 bills tokens for runs that never
answer. Reserving a whole run at admission would avoid that, at the cost of holding more. Nothing here calls
`ledger.expire` on a schedule, and a real system needs that sweep. The scoped index is a brute-force scan: a real
approximate-nearest-neighbour index can lose recall under a selective filter, which is one reason teams give large
tenants their own index. The detector runs one test per tenant with no correction for testing many tenants or many
windows. Per-tenant keys, residency and approval flows are out of scope.

There is no real-model switch in this lab. Its stub misbehaves on purpose, and a real model may not. To try one, write
an adapter with the `Model` signature in `model.py` and pass it to `make_controls`.
