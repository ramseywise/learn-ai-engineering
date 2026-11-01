---
origin: own coursework
sources:
  - https://platform.claude.com/docs/en/about-claude/pricing
  - https://platform.claude.com/docs/en/build-with-claude/prompt-caching
  - https://langfuse.com/docs/observability/features/token-and-cost-tracking
  - https://langfuse.com/docs/metrics/features/metrics-api
  - https://arxiv.org/abs/2411.05285
  - ../practice/support_agent/
confidence: medium
cleaned: 2026-11-01
---
# 6 — Cost and Latency Dashboards

> Turning the support agent's traces into money and milliseconds: pricing a turn with cache reads, cost by trace, route and outcome, p50, p95 and p99 latency, cost per resolved ticket, budgets and alerts in pandas, and what such a dashboard will never tell you.

On 14 October the support agent's bill more than tripled, and nothing broke. Every turn returned 200, every answer looked the way it had the day before, and the quality scores from chapters 2 and 3 didn't move for that cause. A timestamp added to the system prompt had quietly turned every cached read into a cache write. Three days earlier, the invoice vendor had started stalling, and billing customers began waiting twenty seconds, while the average latency across all routes barely changed. Neither problem is a question of answer quality. They are questions about money and time, and they need their own instrument, built from the fields [chapter 5](05-support-agent-observability.md) made every agent log.

A dashboard is a set of decisions about denominators. Spend per day answers a different question from spend per resolved ticket, and an average latency answers a question nobody has. This chapter builds each number from the fortnight's traces in pandas, so you can see what it means and how it goes wrong, then writes the alerts that would have caught both October problems within a day. The Langfuse dashboards compute many of the same numbers for you, and the last section shows how to pull them from its API. Doing it by hand once is how you learn which of its charts to trust.

---

## Price a turn from its usage fields

Everything starts with one model call. A Claude response reports four token counts, and they're charged at four rates. Here are the list prices used across this pillar, read from [Anthropic's pricing page](https://platform.claude.com/docs/en/about-claude/pricing) on 2026-11-01, in USD per million tokens. Prices change, so read the page before you rely on them.

| Model | Base input | Cache write (5 min) | Cache write (1 h) | Cache read | Output |
|---|---|---|---|---|---|
| Fable 5.1 | 10.00 | 12.50 | 20.00 | 0.25 | 50.00 |
| Opus 5.5 | 4.00 | 5.00 | 8.00 | 0.20 | 20.00 |
| Sonnet 5.5 | 2.00 | 2.50 | 4.00 | 0.10 | 10.00 |
| Haiku 5.5, prompts up to 100K tokens | 0.10 | 0.125 | 0.20 | 0.01 | 0.50 |
| Haiku 5.5, prompts over 100K tokens | 0.50 | 0.625 | 1.00 | 0.05 | 2.50 |

The same page gives a 50% discount on input and output through the Batch API, which stacks with caching, and a 1.1x multiplier for US-only inference. The Haiku tier depends on prompt length, which includes cache reads and writes, so a cost function that looks only at `input_tokens` would pick the wrong row. The support agent's Haiku router sends a few hundred tokens, and the code in `practice/support_agent/pricing.py` uses the lower tier.

The detail that trips people up is in the [prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching): `input_tokens` counts only the tokens after the last cache breakpoint. It isn't the size of the prompt. The size of the prompt is the sum of the three input fields.

```text
total input = cache_read_input_tokens + cache_creation_input_tokens + input_tokens
```

So those are separate buckets that don't overlap, and each gets its own price. Langfuse takes the same view: its usage keys are exclusive, and the total is derived by adding them ([token and cost tracking](https://langfuse.com/docs/observability/features/token-and-cost-tracking)). If you send it `input` as the whole prompt and also send `cache_read_input_tokens`, you count the cached tokens twice. Here's the same healthy turn priced correctly and in the two wrong ways you'll meet in real code, next to a turn from the bad release.

```python
from support_agent import generate_traces, llm_cost

traces = generate_traces()
healthy = next(t for t in traces if t.release == "v1" and t.seeded_failure is None and t.route == "account")
broken = next(t for t in traces if t.release == "v2.0" and t.seeded_failure is None and t.route == "account")

def show(label, trace):
    a = next(s for s in trace.spans if s.name == "answer")
    print(f"{label}: input={a.input_tokens} read={a.cache_read_tokens} write={a.cache_write_tokens} output={a.output_tokens}")
    return a

a = show("v1  ", healthy)
print(f"  correct           ${llm_cost(a.model, a.input_tokens, a.output_tokens, a.cache_read_tokens, a.cache_write_tokens):.5f}")
print(f"  cache as input    ${llm_cost(a.model, a.input_tokens + a.cache_read_tokens, a.output_tokens):.5f}")
print(f"  ignoring the cache ${llm_cost(a.model, a.input_tokens, a.output_tokens):.5f}")
b = show("v2.0", broken)
print(f"  correct           ${llm_cost(b.model, b.input_tokens, b.output_tokens, b.cache_read_tokens, b.cache_write_tokens):.5f}")
```

```text
v1  : input=866 read=4200 write=0 output=321
  correct           $0.01072
  cache as input    $0.02668
  ignoring the cache $0.00988
v2.0: input=603 read=0 write=4200 output=293
  correct           $0.02927
```

Pricing cached tokens as plain input overstates the healthy turn, and dropping them understates it, and either mistake would make the October regression hard to see, since the difference between a healthy and a broken turn lies in those fields. Both errors are silent. Reconcile your computed total against an invoice once a month, and investigate if they differ by more than you can explain.

Should the app compute cost or the platform? Langfuse does both: a cost you send it (ingested) takes priority over one it infers from the model name and token counts, using model definitions matched by a regex. Its price changes apply only to data recorded afterwards, so a change in list price won't rewrite history. Sending usage and letting it infer is simplest, but check that the model name matches its definition and that all your buckets are being priced, because an unmatched model shows up as cost zero and it looks like a good day.

---

## Cost per trace, route and outcome

A span has a cost, and a trace's cost is the sum over its spans. The questions come from what you group by. Start with what the money is spent on, because that decides whether anything else matters.

```python
import pandas as pd
from support_agent import PRICES, generate_traces, llm_cost
from support_agent.frames import spans_frame, traces_frame

traces = generate_traces()
df, spans = traces_frame(traces), spans_frame(traces)
llm = spans[spans["model"].notna()].copy()

def bucket_spend(row):
    p = PRICES[row["model"]]
    return pd.Series({"cache_read": row["cache_read_tokens"] * p["cache_read"], "cache_write": row["cache_write_tokens"] * p["cache_write"],
                      "input": row["input_tokens"] * p["input"], "output": row["output_tokens"] * p["output"]}) / 1e6

buckets = pd.concat([llm[["release", "name"]], llm.apply(bucket_spend, axis=1)], axis=1)
per_release = buckets.groupby("release")[["cache_read", "cache_write", "input", "output"]].sum()
per_release["total"] = per_release.sum(axis=1)
per_release["per_turn"] = per_release["total"] / df.groupby("release").size()
print(per_release.round(4).to_string())
print()
print("reconciles with the stored trace cost:", round(per_release["total"].sum(), 4) == round(df["cost_usd"].sum(), 4))
print("router share of model spend:", f"{buckets.loc[buckets['name'] == 'route', ['cache_read', 'cache_write', 'input', 'output']].sum().sum() / per_release['total'].sum():.1%}")
```

```text
         cache_read  cache_write   input  output   total  per_turn
release
v1           0.7942        0.000  2.7823  4.7920  8.3686    0.0093
v2.0         0.0013        7.203  1.0374  1.6615  9.9032    0.0330
v2.1         0.1907        0.000  0.6662  1.0148  1.8717    0.0094

reconciles with the stored trace cost: True
router share of model spend: 0.1%
```

That table is the regression in one view. The cost per turn triples, and the whole increase sits in one column. No token count would have told you that: the number of tokens per turn hardly changed. Only the bucket they landed in did.

Group by route and by outcome next. Medians sit beside means, since a few bad turns can dominate a total.

```python
import pandas as pd
from support_agent import generate_traces
from support_agent.frames import traces_frame

df = traces_frame(generate_traces())
base = df[df["release"] != "v2.0"]

def table(frame, key):
    out = frame.groupby(key).agg(turns=("cost_usd", "size"), spend=("cost_usd", "sum"), mean=("cost_usd", "mean"), median=("cost_usd", "median"))
    out["share"] = (out["spend"] / out["spend"].sum()).round(3)
    return out.round(4).sort_values("spend", ascending=False)

print(table(base, "route").to_string()); print()
print(table(base, "outcome").to_string()); print()
print("Most expensive turns outside v2.0")
worst = base.nlargest(5, "cost_usd")[["trace_id", "route", "outcome", "cost_usd", "latency_ms", "seeded_failure"]]
print(worst.round(4).to_string(index=False))
print()
top_1pct = base["cost_usd"].quantile(0.99)
print(f"top 1% of turns: {base.loc[base['cost_usd'] >= top_1pct, 'cost_usd'].sum() / base['cost_usd'].sum():.1%} of spend")
```

```text
           turns   spend    mean  median  share
route
billing      390  3.6701  0.0094  0.0090  0.358
technical    276  2.5377  0.0092  0.0091  0.248
account      268  2.5110  0.0094  0.0090  0.245
refund       166  1.5215  0.0092  0.0087  0.149

           turns   spend    mean  median  share
outcome
resolved     848  7.6929  0.0091  0.0089  0.751
abandoned    144  1.3382  0.0093  0.0086  0.131
escalated     99  0.9574  0.0097  0.0093  0.093
error          9  0.2518  0.0280  0.0266  0.025

Most expensive turns outside v2.0
trace_id     route   outcome  cost_usd  latency_ms seeded_failure
  t00619   billing escalated    0.0425     20936.8     retry_loop
  t01299    refund     error    0.0373     18739.6     retry_loop
  t00512   billing  resolved    0.0372     21151.4     retry_loop
  t00112 technical abandoned    0.0362     19406.2     retry_loop
  t00180   billing escalated    0.0361     22366.5     retry_loop

top 1% of turns: 3.6% of spend
```

The per-trace list is where a retry loop shows up. These turns aren't a large share of the bill in this synthetic traffic, but each is many times the cost of a normal turn. Treat that list as a queue of things to read rather than something to average: a turn at several times the median has a reason, and the tree from [chapter 1](01-tracing-with-langfuse.md) will show it. The same list is the first thing to check for a runaway agent, since a loop's cost has no natural limit, unlike ordinary traffic's. Set a hard limit on steps per turn in the agent, then chart how close it gets.

---

## Percentiles, and why not the mean

Latency has a long right tail. A support turn is mostly model time plus a tool or two, and one stalled vendor call can add many seconds. The mean mixes that tail into the middle, where it describes neither. Percentiles separate them: p50 is the typical customer, p95 the bad but regular experience, p99 close to the worst. With 100 turns a day, p99 on a single day is the second-slowest turn or thereabouts, so it needs a longer window, and that's worth showing rather than asserting.

```python
import numpy as np
import pandas as pd
from support_agent import generate_traces
from support_agent.frames import traces_frame

df = traces_frame(generate_traces())
df["seconds"] = df["latency_ms"] / 1000
df["period"] = (df["day"] >= "2026-10-11").map({False: "before 11 Oct", True: "from 11 Oct"})

def pct(q):
    return lambda s: s.quantile(q)

table = df.groupby(["route", "period"])["seconds"].agg(n="size", mean="mean", p50=pct(.5), p95=pct(.95), p99=pct(.99))
print(table.round(1).to_string())
print()
everyone = df.groupby("period")["seconds"].agg(mean="mean", p50=pct(.5), p95=pct(.95))
print(everyone.round(1).to_string())
print()

rng = np.random.default_rng(0)
billing = df[(df["route"] == "billing") & (df["period"] == "from 11 Oct")]["seconds"].to_numpy()
for n in (25, 100, len(billing)):
    p99s = [np.quantile(rng.choice(billing, n), .99) for _ in range(2000)]
    print(f"p99 from {n:>3} billing turns: 90% of resamples between {np.quantile(p99s, .05):.1f} s and {np.quantile(p99s, .95):.1f} s")
```

```text
                           n  mean  p50   p95   p99
route     period
account   before 11 Oct  141   6.6  6.4  10.3  15.0
          from 11 Oct    209   6.7  6.5   9.9  14.1
billing   before 11 Oct  219   6.4  6.1   9.4  10.9
          from 11 Oct    276   8.1  7.0  21.0  29.2
refund    before 11 Oct   90   6.3  5.7   9.6  13.2
          from 11 Oct    127   6.9  6.7  10.0  23.3
technical before 11 Oct  150   6.4  6.2   9.5  10.2
          from 11 Oct    188   6.5  6.0   9.8  21.9

               mean  p50   p95
period
before 11 Oct   6.4  6.2   9.8
from 11 Oct     7.2  6.7  11.1

p99 from  25 billing turns: 90% of resamples between 10.3 s and 35.8 s
p99 from 100 billing turns: 90% of resamples between 21.0 s and 37.7 s
p99 from 276 billing turns: 90% of resamples between 22.8 s and 38.3 s
```

Across all routes the mean moves a little, while the billing route's p95 doubles. This is why you break latency down by route before looking at any percentile. A slow route becomes a small tail of the total, and an average across routes hides the customers it's happening to. The resampling lines make the other point: a p99 from a handful of turns is mostly noise, so give it a long window, or chart p95 instead when traffic is thin. The fortnight's traffic is synthetic and small on purpose. A real agent with 100,000 turns a day would have a very stable p99 and could break it down much further.

A percentile tells you which customers are waiting, but not why. For that you go down to spans, and the arithmetic changes in one way that catches people: percentiles don't add. The p95 of a turn isn't the sum of the p95s of its steps, since those rarely occur together. So measure spans by their share of total time, and use percentiles for each span on its own.

```python
import pandas as pd
from support_agent import generate_traces
from support_agent.frames import spans_frame

spans = spans_frame(generate_traces())
billing = spans[(spans["route"] == "billing")]
for label, part in (("before 11 Oct", billing[billing["day"] < "2026-10-11"]), ("from 11 Oct", billing[billing["day"] >= "2026-10-11"])):
    table = part.groupby("name")["latency_ms"].agg(calls="size", total_s=lambda s: s.sum() / 1000, p50=lambda s: s.quantile(.5), p95=lambda s: s.quantile(.95))
    table["share"] = (table["total_s"] / table["total_s"].sum()).round(2)
    print(label); print(table.round(0).astype({"share": float}).assign(share=table["share"]).sort_values("total_s", ascending=False).head(4).to_string()); print()

p95_sum = billing.groupby("name")["latency_ms"].quantile(.95).sum() / 1000
per_turn = billing.groupby("trace_id")["latency_ms"].sum().quantile(.95) / 1000
print(f"sum of the span p95s: {p95_sum:.1f} s. p95 of the summed turns: {per_turn:.1f} s")
```

```text
before 11 Oct
             calls  total_s     p50     p95  share
name
answer         229   1229.0  5301.0  8598.0   0.88
route          219     88.0   385.0   568.0   0.06
kb_search      229     51.0   179.0   414.0   0.04
get_invoice    209     31.0   137.0   232.0   0.02

from 11 Oct
             calls  total_s     p50     p95  share
name
answer         310   1717.0  5472.0  8924.0   0.77
get_invoice    273    328.0   141.0  9624.0   0.15
route          276    108.0   384.0   563.0   0.05
kb_search      310     81.0   170.0   975.0   0.04

sum of the span p95s: 10.7 s. p95 of the summed turns: 13.8 s
```

Time to first token matters too for a streaming chat. If the agent streams, log it as well, because a customer judges a ten-second answer that starts within a second differently from one that sits blank. The synthetic traces don't record it, which is a gap in this case study rather than a recommendation.

---

## Cost per resolved ticket

Total spend answers "what's the bill?" The question a business has is what a resolved ticket costs, and whether that's less than the alternative. So the denominator moves from turns to outcomes, and that's the moment you learn which outcomes you have, which is why the trace contract has an `outcome` enum.

```python
import pandas as pd
from support_agent import generate_traces
from support_agent.frames import traces_frame

df = traces_frame(generate_traces())
df["clean_resolved"] = (df["outcome"] == "resolved") & df["seeded_failure"].isna()

by_release = df.groupby("release").agg(
    turns=("cost_usd", "size"), spend=("cost_usd", "sum"),
    resolved=("outcome", lambda s: (s == "resolved").sum()),
    escalated=("outcome", lambda s: (s == "escalated").sum()),
    clean_resolved=("clean_resolved", "sum"),
)
by_release["usd_per_resolved"] = by_release["spend"] / by_release["resolved"]
by_release["usd_per_clean"] = by_release["spend"] / by_release["clean_resolved"]
by_release["resolved_rate"] = by_release["resolved"] / by_release["turns"]
print(by_release.round(4).to_string())
print()

HUMAN_TICKET_USD = 6.00                    # an assumption for the example, not a benchmark
by_release["usd_all_in"] = (by_release["spend"] + by_release["escalated"] * HUMAN_TICKET_USD) / by_release["turns"]
print(by_release[["usd_all_in"]].round(3).T.to_string())
print()
for rate in (2.0, 6.0, 12.0):
    print(f"human ticket at ${rate:>4.2f}: model spend is {(df['cost_usd'].sum() / (df['cost_usd'].sum() + (df['outcome'] == 'escalated').sum() * rate)):.1%} of the all-in cost")
```

```text
         turns   spend  resolved  escalated  clean_resolved  usd_per_resolved  usd_per_clean  resolved_rate
release
v1         900  8.3686       699         80             656            0.0120         0.0128         0.7767
v2.0       300  9.9032       231         29             209            0.0429         0.0474         0.7700
v2.1       200  1.8717       149         19             130            0.0126         0.0144         0.7450

release        v1   v2.0   v2.1
usd_all_in  0.543  0.613  0.579

human ticket at $2.00: model spend is 7.3% of the all-in cost
human ticket at $6.00: model spend is 2.6% of the all-in cost
human ticket at $12.00: model spend is 1.3% of the all-in cost
```

Read those last lines before you spend a sprint on the model bill. The $6 is a number invented for the example, so you should substitute your own. At any plausible value the escalations dwarf the model cost in this traffic, so a change that resolves slightly more tickets can be worth far more than one that halves the tokens. That's what makes a dashboard on spend alone misleading, and the reason the `outcome` field earns its place in the contract.

Beware the denominator as well. `resolved` here means the conversation ended without a person, and a customer who gives up on a wrong answer can be counted the same way. The `usd_per_clean` column divides by resolved turns with no planted failure, which you can only compute here because the failures are planted. In production, use the judge scores from [chapter 3](03-judge-pipelines-over-trace-exports.md), a sample of labelled tickets, or a business signal such as the customer not writing back within a week. Any ratio you put on a dashboard will be optimised, so choose one that can't improve by giving up on customers.

---

## Budgets and alerts

A dashboard is something a person has to look at. An alert is what makes sure they do on the right day. Each rule below is one number, one threshold and one reason. Replaying them over the fortnight shows what they would have done, and that's a test you can run on any new rule before you let it page anyone.

```python
import pandas as pd
from support_agent import generate_traces
from support_agent.frames import spans_frame, traces_frame

traces = generate_traces()
df, spans = traces_frame(traces), spans_frame(traces)
answers = spans[spans["name"] == "answer"]

daily = df.groupby("day").agg(
    spend=("cost_usd", "sum"), turns=("cost_usd", "size"), resolved=("outcome", lambda s: (s == "resolved").sum()))
daily["usd_per_resolved"] = daily["spend"] / daily["resolved"]
daily["cache_hit"] = answers.groupby("day")["cache_read_tokens"].sum() / answers.groupby("day")[["cache_read_tokens", "cache_write_tokens", "input_tokens"]].sum().sum(axis=1)
daily["billing_p95_s"] = df[df["route"] == "billing"].groupby("day")["latency_ms"].quantile(.95) / 1000
daily["billing_n"] = df[df["route"] == "billing"].groupby("day").size()
daily["max_turn_usd"] = df.groupby("day")["cost_usd"].max()

MONTHLY_BUDGET_USD, DAYS = 45.0, 30
baseline = daily["usd_per_resolved"].rolling(7, min_periods=3).median().shift(1)
RULES = {
    "daily spend over 1.5x the budget's pace": daily["spend"] > 1.5 * MONTHLY_BUDGET_USD / DAYS,
    "cost per resolved over 1.5x trailing median": daily["usd_per_resolved"] > 1.5 * baseline,
    "cache hit rate on answers under 50%": daily["cache_hit"] < 0.5,
    "billing p95 over 15 s, 10+ turns": (daily["billing_p95_s"] > 15) & (daily["billing_n"] >= 10),
    "a single turn over $0.10": daily["max_turn_usd"] > 0.10,
}
alerts = pd.DataFrame(RULES).T
print(pd.DataFrame({"first": [c.idxmax()[5:] if c.any() else "-" for c in alerts.T.items().__iter__() and [alerts.loc[r] for r in alerts.index]],
                    "days": alerts.sum(axis=1).astype(int).values}, index=alerts.index).to_string())
print()
print(daily.loc["2026-10-12":"2026-10-15", ["spend", "usd_per_resolved", "cache_hit", "billing_p95_s"]].round(3).to_string())
print()
month_so_far = daily["spend"].cumsum()
pace = month_so_far / range(1, len(daily) + 1) * DAYS
print("projected month on 13 Oct:", round(pace.loc["2026-10-13"], 2), " on 16 Oct:", round(pace.loc["2026-10-16"], 2), f" budget {MONTHLY_BUDGET_USD}")
```

```text
                                             first  days
daily spend over 1.5x the budget's pace      10-14     3
cost per resolved over 1.5x trailing median  10-14     3
cache hit rate on answers under 50%          10-14     3
billing p95 over 15 s, 10+ turns             10-11     5
a single turn over $0.10                     10-14     3

            spend  usd_per_resolved  cache_hit  billing_p95_s
day
2026-10-12  0.876             0.012      0.851         15.654
2026-10-13  0.942             0.014      0.852         21.125
2026-10-14  3.409             0.042      0.000         21.237
2026-10-15  3.267             0.044      0.000         10.178

projected month on 13 Oct: 27.9  on 16 Oct: 45.68  budget 45.0
```

Notice which rules fired first, and which is the better signal. The cache rule is a ratio, so it doesn't depend on traffic: a marketing email that doubles your tickets moves the daily spend, and the cost per resolved stays flat, but the cache hit rate falls only when the cache breaks. Treat `cache_read_input_tokens > 0` as a standing check on any prefix you expect to be cached, since a change as small as a timestamp in the system prompt causes this regression with no error. The billing latency rule needs a route breakdown and a minimum sample, and without them it would either be hidden by other routes or fire on two slow turns. The budget rule is the slowest and the least specific, though it's the one finance will care about, so keep it as the backstop.

Those thresholds are set to fit a fortnight I generated, which is the wrong way round for real use. On live traffic, replay a candidate threshold against several months, count how many days it would have fired, and read those days. An alert that fires weekly for nothing teaches people to ignore it, including on the day it matters. Every alert should also name its owner and the first thing to check, for instance "cache hit under 50%: diff the system prompt in the last release". That makes it possible to act on at 3 a.m.

![Three panels on one time axis over 5 to 18 October. Model spend per day jumps from about one dollar to over three during release v2.0 and returns afterwards. Spend per resolved ticket follows the same shape. The p95 latency of the billing route climbs from 11 October and stays erratic, while other routes hold near ten seconds.](../sources/images/support-agent-dashboard.png)

*Image Source: rendered for this chapter by `practice/make_dashboard_chart.py` from the synthetic traces, priced at the list prices above. Shaded band: release v2.0.*

Three panels give the three different readings. The top one says something costs more. The middle one says it isn't because more customers were helped, since the cost per outcome moved with it. The bottom one has a different shape and a different start date, and on the top two panels you can't see it at all, which is why it gets its own panel and a route breakdown. They share one time axis, and no chart has two y-scales: dollars and seconds don't belong on one axis, and a dual-axis chart lets you imply any relationship you like by rescaling.

---

## What the dashboard can't see

After 17 October the top two panels are back to normal. A dashboard review would call the incident closed. But the `v2.1` fix restored the cache and not the prompt, which had changed something else too. The bill recovered. The answers didn't. So join the money to the judge pipeline from chapter 3, by release and route.

```python
import pandas as pd
from support_agent import generate_traces
from support_agent.frames import traces_frame
from support_agent.judges import flagged, raw_export, run_pipeline, to_conversation

traces = generate_traces()
df = traces_frame(traces)
results = {t.trace_id: run_pipeline(to_conversation(raw_export(t))) for t in traces}
df["hallucinated"] = df["trace_id"].map(lambda i: flagged(results[i]))
df["group"] = df["route"].where(df["route"] == "billing", "other routes")

view = df.groupby(["group", "release"]).agg(turns=("cost_usd", "size"), usd_per_turn=("cost_usd", "mean"),
                                            p95_s=("latency_ms", lambda s: s.quantile(.95) / 1000),
                                            hallucination=("hallucinated", "mean"))
view["hallucination"] = (view["hallucination"] * 100).round(1)
print(view.round(4).to_string())
```

```text
                      turns  usd_per_turn    p95_s  hallucination
group        release
billing      v1         318        0.0094  10.3529            1.6
             v2.0       105        0.0333  20.1339            7.6
             v2.1        72        0.0097  15.2486           12.5
other routes v1         582        0.0093   9.7143            1.7
             v2.0       195        0.0329  10.2871            3.1
             v2.1       128        0.0092   9.1377            3.1
```

The money and speed columns recover at `v2.1`, while billing's hallucination rate keeps climbing. A dashboard with only the first two would have told the team they had won. This is the argument for one table with cost, latency and quality on the same rows. The AgentOps survey found the same pattern among tools: most focus on LLM metrics, with less support for goals, plans and tools ([arXiv:2411.05285](https://arxiv.org/abs/2411.05285), Dong, Lu and Zhu, 2024-11, preprint). A cost chart is the easiest thing to build and the easiest to mistake for health. Anthropic's guide to agent evals uses a Swiss cheese image for the same idea, with each layer catching what the others let through ([Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Anthropic, 2026-01, engineering blog).

---

## Which lever to pull

Once costs are visible, someone will ask how to reduce them. Answer with the data, by pricing each option on the turns you already have. All of these are arithmetic on recorded tokens, so they're estimates, and each still has to pass the regression gate from [chapter 2](02-scoring-datasets-experiments.md).

```python
import pandas as pd
from support_agent import generate_traces, llm_cost
from support_agent.frames import spans_frame, traces_frame
from support_agent.judges import pipeline_cost, raw_export, run_pipeline, to_conversation

traces = generate_traces()
df, spans = traces_frame(traces), spans_frame(traces)
healthy = spans[(spans["release"] != "v2.0")]
days = healthy["day"].nunique()
answers = healthy[healthy["name"] == "answer"]

def reprice(frame, model):
    return sum(llm_cost(model, r.input_tokens, r.output_tokens, r.cache_read_tokens, r.cache_write_tokens) for r in frame.itertuples())

today = reprice(answers, "claude-opus-5-5") / days
router_today = reprice(healthy[healthy["name"] == "route"], "claude-haiku-5-5") / days
sonnet = reprice(answers, "claude-sonnet-5-5") / days
no_cache = sum(llm_cost("claude-opus-5-5", r.input_tokens + r.cache_read_tokens + r.cache_write_tokens, r.output_tokens) for r in answers.itertuples()) / days
router_opus = reprice(healthy[healthy["name"] == "route"], "claude-opus-5-5") / days

judges = pipeline_cost([run_pipeline(to_conversation(raw_export(t))) for t in traces])["total_usd"] / df["day"].nunique()
retries = df[df["seeded_failure"].eq("retry_loop") & df["release"].ne("v2.0")]
retry_waste = (retries["cost_usd"].sum() - len(retries) * df.loc[df["release"].ne("v2.0") & df["seeded_failure"].isna(), "cost_usd"].mean()) / days

print(f"answer model today (Opus 5.5, cached)      ${today:.2f} a day")
print(f"router today (Haiku 5.5)                   ${router_today:.3f} a day")
print(f"judges online (chapter 3)                  ${judges:.2f} a day")
print()
print(f"keeping the cache is worth                 ${no_cache - today:+.2f} a day")
print(f"answers on Sonnet 5.5 would save           ${today - sonnet:+.2f} a day, and must pass the gate")
print(f"judges through the Batch API would save    ${judges / 2:+.2f} a day, with results up to a day late")
print(f"fixing the retry loop would save           ${retry_waste:+.2f} a day")
print(f"running the router on Opus would add       ${router_opus - router_today:+.2f} a day")
```

```text
answer model today (Opus 5.5, cached)      $0.93 a day
router today (Haiku 5.5)                   $0.002 a day
judges online (chapter 3)                  $0.11 a day

keeping the cache is worth                 $+1.69 a day
answers on Sonnet 5.5 would save           $+0.46 a day, and must pass the gate
judges through the Batch API would save    $+0.05 a day, with results up to a day late
fixing the retry loop would save           $+0.03 a day
running the router on Opus would add       $+0.05 a day
```

The cache is worth much more than anything else on the list, which is why it gets a standing alert. The rest of the ranking shows the model swap as the big remaining lever, and it's the one with quality risk, so it goes through the same experiment as any prompt change. A sensible order: protect the cache, cap the loops, batch whatever can wait, then test cheaper models from the top of the bill. The Batch API takes up to 24 hours, so it suits a nightly judge run and not online scores you alert on. Note the scale, too: a dollar a day in this synthetic traffic of 100 turns. Multiply by your own volume before deciding what's worth an engineer's week.

---

## The same numbers from Langfuse

You don't have to export traces for each of these. Langfuse's Metrics API v2 runs aggregate queries directly ([Metrics API](https://langfuse.com/docs/metrics/features/metrics-api)). You give it a view such as `observations`, metrics, dimensions and a time range. The older `traces` view is gone in v2, and `isRootObservation` is the way to ask about whole turns. High-cardinality dimensions return only the top rows, with a default row limit of 100 and a maximum of 1,000, so a per-trace query isn't its job. It can compute totals and percentiles, but it can't join money to your outcome field unless you logged that outcome as metadata or a score, and it knows nothing about budgets. Keep the pandas version for anything it won't express.

```python
# illustrative: needs LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY for a project with traffic. Offline it hits a local fake that returns no rows.
import json
from support_agent.fakes import offline_langfuse

lf, capture = offline_langfuse()
query = {
    "view": "observations",
    "metrics": [{"measure": "totalCost", "aggregation": "sum"}, {"measure": "latency", "aggregation": "p95"}],
    "dimensions": [{"field": "providedModelName"}],
    "filters": [],
    "timeDimension": {"granularity": "day"},
    "fromTimestamp": "2026-10-05T00:00:00Z",
    "toTimestamp": "2026-10-19T00:00:00Z",
    "orderBy": [{"field": "sum_totalCost", "direction": "desc"}],
    "config": {"row_limit": 100},
}
response = lf.api.metrics.metrics(query=json.dumps(query))
for row in response.data:
    print(row)
```

The dashboards and alerts in the product follow from the same data, and the native MCP server from [chapter 4](04-langfuse-mcp-server.md) exposes alert and dashboard tools alongside `queryMetrics`. The chapter's pandas rules can run on a schedule over this query or over an export. Where the alert runs matters less than having replayed it first, so you know how often it will fire.

---

## Pitfalls

| Pitfall | What happens | Instead |
|---|---|---|
| Treating `input_tokens` as the prompt size | Cached tokens are dropped or double counted | Three exclusive buckets, each with its own price |
| Unmatched model name in the platform | Its cost shows as zero and looks like a saving | Check model definitions, reconcile with the invoice |
| Average latency across routes | One route stalls and the number barely moves | Percentiles by route, and by tool span for the cause |
| Daily p99 on a small sample | Noise gets read as an incident | Longer window, or p95, plus a minimum count |
| Adding span p95s | The total comes out much larger than any real turn | Use share of time for attribution |
| Spend without a denominator | A traffic spike looks like a regression, and the reverse | Cost per resolved ticket, and ratios such as cache hit rate |
| Cost per resolved as the only target | Giving up on customers improves the number | Pair it with quality and a follow-up signal |
| Thresholds nobody replayed | Alerts fire weekly and get ignored | Replay over history, and name an owner and first check |
| Green charts taken as health | The `v2.1` billing hallucinations go unseen | Cost, latency and quality on the same rows |

---

## Try it

1. Add a rule for the planted vendor stall that doesn't name the billing route: for each route, compare its p95 to its own trailing median. When does it fire, and does it fire on anything else?

   <details><summary>Answer</summary>

   Group by day and route, compute p95, and take a shifted rolling median per route. Billing fires around 11 October, when the stall starts. With about 25 turns per route a day, p95 is noisy, so expect some single-day fires on other routes too at a tight threshold. Requiring two days in a row, or raising the multiplier, trades those away for a day of delay. Run it and count, because that trade is the whole decision.

   </details>

2. The note says the cache rule doesn't depend on traffic. Prove it: double a day's rows and recompute daily spend, cost per resolved, and cache hit rate.

   <details><summary>Answer</summary>

   Concatenate one day's frame with itself. Spend doubles, so the budget rule may fire. Cost per resolved and the cache hit rate stay exactly the same, as both numerator and denominator double. That's why ratios go in alerts about the system and totals in alerts about the budget.

   </details>

3. A release moves 500 tokens from the cached prefix to after the breakpoint, in order to personalise them. Using the Opus 5.5 prices, what does it cost per answer? Which column in the bucket table shows it?

   <details><summary>Answer</summary>

   Those 500 tokens move from cache read at $0.20 per million to input at $4.00 per million: `500 * (4.00 - 0.20) / 1e6`, or $0.0019 per call. That's about a fifth of a healthy turn's cost, from a change that wouldn't fail any test. The `input` column rises and `cache_read` falls, and the cache hit rate drops only slightly, so the rule at 50% won't catch it. Cost per turn would, with a tighter threshold.

   </details>

---

## Interview checklist

| Question | A good answer |
|---|---|
| How do you compute the cost of a Claude call with caching? | Input, cache read, cache write and output are separate buckets with separate prices. `input_tokens` is only what comes after the last breakpoint, and the prompt size is the sum of the three input fields |
| Why report p95 by route and not mean latency? | The tail is the experience of real customers, and a slow route gets lost in an overall mean. On low traffic, p99 is noise, so use a longer window |
| Can you add step p95s to get a turn's p95? | No. Slow steps rarely coincide. Use each step's share of total time to attribute, and its own percentile to describe it |
| What's the best single cost metric? | Cost per resolved ticket, paired with a quality signal, because cost per turn ignores whether anyone was helped, and the ratio alone can be gamed by giving up |
| How would you catch a silent prompt-cache regression? | A standing alert on cache hit rate for prefixes you expect to be cached. It's a ratio, so traffic doesn't move it, and usage fields are the only ground truth |
| How do you set an alert threshold? | Replay it over history, count how often it fires, read those days, and name an owner and a first check |
| What can a cost and latency dashboard not tell you? | Whether the answers are right. Put judge scores on the same rows, or a bill that recovers looks like a fix when quality is still falling |
| The bill is too high. What do you do first? | Break it down by bucket, route and model, then price each lever on recorded tokens. Protect the cache, cap loops, batch what can wait, and test cheaper models through the regression gate |

---

## Next

You've followed one regression from a bad trace through scores, judges, an agent asking its own questions, a schema contract and finally the bill. The same case study is taken up from the evaluation side in [ai-engineering/06-eval 13](../../../ai-engineering/06-eval/notes/13-case-study-support-agent.md).

→ [07 — Agentic applications](../../07-agentic-applications/README.md): building complete agents, now that you can see what they do and what they cost.
