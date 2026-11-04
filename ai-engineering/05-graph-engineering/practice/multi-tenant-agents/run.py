# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""One agent core serving four fictional tenants, each isolation control printed beside the naive version it replaces.

Run from this folder (a few seconds, standard library only, no API key, downloads nothing):
    uv run run.py
    uv run test.py

Generated: the tenants, corpus, records, traffic and costs. The model is a stub with planted misbehaviours (stub.py).
Real: asyncio scheduling (latency is counted in event-loop yields, so the interleaving is real and repeatable), the
SQLite ledger, the validation, the queueing and the rubric scoring. Every number describes these assumptions, not any
product. Change tenants.json or the constants at the top of a scenario and rerun.
"""
# %%
from functools import partial

from enforce import (AmbientTraces, CheckThenSpend, FairQueue, FifoQueue, PostFilterRetriever, PromptOnlyTools,
                     ReservationLedger, RunScopedBudget, ScopedRetriever, TenantTraces, ToolLayer, canary_decision,
                     fleet_mean_alert, fleet_rate, per_tenant_alert, tenant_quality)
from scenarios import (BUDGET_CAP, BUDGET_RUNS, BUDGET_TENANT, CORPUS, QUALITY_VOLUME, bad_configs, budget_scenario,
                       canary_run, fleet_scenario, load_scenario, quality_scenario, retrieval_scenario, reworded_tallow,
                       shortened_larkspur, tool_scenario, trace_scenario)
from tenancy import TENANT_IDS, ConfigError, NaiveConfigStore, load_raw_configs, load_store, validate_config

RAWS = {r["tenant_id"]: r for r in load_raw_configs()}


def header(text):
    print(f"\n{text}\n{'-' * len(text)}")


print("model: stub. All tenants and data are generated.")

# %% 1. Validated config, canary, per-tenant rollback
header("1. Config: validate, canary, roll back one tenant")
for label, raw in bad_configs().items():
    try:
        validate_config(raw)
        raise AssertionError(f"accepted a bad config: {label}")
    except ConfigError as err:
        print(f"  rejected ({label}): {err.errors[0]}")

store = load_store()
bad = store.propose(shortened_larkspur(RAWS["larkspur-clinic"]))
good = store.propose(reworded_tallow(RAWS["tallow-legal"]))
store.start_canary("larkspur-clinic", bad, 20)
store.start_canary("tallow-legal", good, 20)
for tenant, version in (("larkspur-clinic", bad), ("tallow-legal", good)):
    counts = canary_run(store, tenant, 300, f"canary-{tenant}")
    decision = canary_decision(counts[1], counts[version])
    print(f"  {tenant:16} stable v1 {counts[1][0]}/{counts[1][1]} passed, canary v{version} "
          f"{counts[version][0]}/{counts[version][1]} passed: {decision}")
    if decision == "promote":
        store.promote(tenant)
    elif decision == "rollback":
        store.rollback(tenant)
print("  stable versions now:", {t: store.stable_version(t) for t in TENANT_IDS})
assert store.stable_version("larkspur-clinic") == 1 and store.stable_version("tallow-legal") == good

naive = load_store(NaiveConfigStore())
naive.propose(shortened_larkspur(RAWS["larkspur-clinic"]))
naive.propose(reworded_tallow(RAWS["tallow-legal"]))
naive.rollback("larkspur-clinic")
print("  naive store, rollback(larkspur-clinic):")
print("    larkspur still on the bad prompt:", "Always end with" not in naive.get("larkspur-clinic").system_prompt)
print("    tallow's good edit was undone:   ", "You help clients" not in naive.get("tallow-legal").system_prompt)

# %% 2. A tenant budget across concurrent runs
header(f"2. Budget: {BUDGET_RUNS} overlapping runs of {BUDGET_TENANT}, cap {BUDGET_CAP:,} tokens")
print(f"  {'budget':34}{'billed':>8}{'of cap':>8}{'answered':>10}{'refused':>9}")
for label, make in (("run-scoped (reads spend at start)", RunScopedBudget),
                    ("shared counter, check then spend", CheckThenSpend),
                    ("ledger, refuse if held", partial(ReservationLedger, wait=False)),
                    ("ledger, wait for held to settle", ReservationLedger)):
    r = budget_scenario(make)
    print(f"  {label:34}{r['bill']:>8,}{r['bill'] / r['cap']:>8.0%}{r['answered']:>10}{r['refused']:>9}")
    if isinstance(make, partial) or make is ReservationLedger:
        assert r["bill"] <= r["cap"]

# %% 3. Retrieval
header(f"3. Retrieval: 6 generic questions per tenant, top 3, over {len(CORPUS)} generated documents")
print(f"  {'retriever':13}{'tenant':18}{'no docs':>9}{'no on-topic':>13}"
      f"{'foreign in context':>20}{'foreign exposed':>17}")
for name, make in (("post-filter", PostFilterRetriever), ("in the query", ScopedRetriever)):
    rows = retrieval_scenario(make)
    for tenant, row in rows.items():
        print(f"  {name:13}{tenant:18}{row['starved']:>9}{row['missed']:>13}"
              f"{row['foreign_in_context']:>20}{row['foreign_exposed']:>17}")
    if make is ScopedRetriever:
        assert all(r["foreign_exposed"] == 0 and r["missed"] == 0 for r in rows.values())
lost = [d for d in CORPUS if d.scope is None]
print(f"  {len(lost)} documents lost their scope at ingest. In the query they match nobody, which needs its own alert.")

# %% 4. Tools
header("4. Tools: the stub tries issue_refund for a tenant that doesn't have it, and reads another tenant's record")
for name, make in (("prompt only", PromptOnlyTools), ("tool layer", ToolLayer)):
    r = tool_scenario(make)
    print(f"  {name:12} refunds executed for larkspur: {len(r['disallowed_effects'])}, "
          f"denied spans: {len(r['denied_spans'])}, foreign record in the answer: {r['foreign_record_in_answer']}, "
          f"pinwheel's allowed refund executed: {len(r['allowed_effects'])}")
assert not r["disallowed_effects"] and not r["foreign_record_in_answer"]

# %% 5. Noisy neighbour
header("5. Queueing: pinwheel-retail bursts 400 requests at tick 50. Wait in ticks, one tick = one simulated second")
print(f"  {'policy':24}{'tenant':18}{'p50':>6}{'p95':>6}{'served':>8}{'rejected':>10}")
for label, make, limits in (("one FIFO line", FifoQueue, False), ("fair queue", FairQueue, False),
                            ("fair queue + rate limit", FairQueue, True)):
    r = load_scenario(make, limits)
    for tenant in TENANT_IDS:
        row = r[tenant]
        print(f"  {label:24}{tenant:18}{row['p50']:>6.0f}{row['p95']:>6}{row['served']:>8}{row['rejected']:>10}")
    print(f"  {label:24}finished at tick {r['finished_at']}")

# %% 6. Traces
header("6. Traces: 40 overlapping runs across four tenants")
for name, make in (("one ambient tenant slot", AmbientTraces), ("stamped from the run", TenantTraces)):
    r = trace_scenario(make)
    print(f"  {name:24} spans {r['spans']}, filed under the wrong tenant {r['misattributed']}, "
          f"another tenant's spans readable by run_id {r['foreign_spans_read']}")
assert r["misattributed"] == 0 and r["foreign_spans_read"] == 0

# %% 7. Quality
header("7. Quality: a shared model alias moves from v1 to v2 for every tenant (generated runs, planted fault)")
q = quality_scenario()
before, after = q["before"], q["after"]
status = tenant_quality(before, after)
print(f"  {'tenant':18}{'runs':>7}{'v1 pass':>9}{'v2 pass':>9}  status")
for tenant in QUALITY_VOLUME:
    print(f"  {tenant:18}{after[tenant][1]:>7}{before[tenant][0] / before[tenant][1]:>9.1%}"
          f"{after[tenant][0] / after[tenant][1]:>9.1%}  {status[tenant]}")
fleet_alert = sorted(fleet_mean_alert(before, after)) or "none"
print(f"  {'fleet, by traffic':18}{sum(c[1] for c in after.values()):>7}"
      f"{fleet_rate(before):>9.1%}{fleet_rate(after):>9.1%}  alert: {fleet_alert}")
print(f"  per-tenant alert names: {sorted(per_tenant_alert(before, after))}")
assert per_tenant_alert(before, after) == {"larkspur-clinic"} and not fleet_mean_alert(before, after)

# %% 8. All of it at once
header("8. The whole path: admission, fair queue, 16 workers, agent, ledger, with hostile tickets mixed in")
f = fleet_scenario()
print(f"  {'tenant':18}{'billed':>8}{'cap':>8}{'answered':>10}{'refused':>9}{'429s':>6}")
for tenant in TENANT_IDS:
    answered = sum(x.status == "answered" for x in f["results"] if x.tenant_id == tenant)
    refused = sum(x.status == "budget_refused" for x in f["results"] if x.tenant_id == tenant)
    limited = sum(x.tenant == tenant for x in f["rejected"])
    print(f"  {tenant:18}{f['bill'][tenant]:>8,}{f['limits'][tenant]:>8,}{answered:>10}{refused:>9}{limited:>6}")
    assert f["bill"][tenant] <= f["limits"][tenant]
print(f"  another tenant's text in any model prompt: {f['foreign_text_in_prompts']}")
print(f"  side effects by tenant: {sorted({e[0] for e in f['tools'].effects})}")
assert f["foreign_text_in_prompts"] == 0 and {e[0] for e in f["tools"].effects} <= {"pinwheel-retail"}
print("\nok: all invariants in this script held")
