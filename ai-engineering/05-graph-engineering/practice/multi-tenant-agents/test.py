# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Isolation properties. Each paired check must pass on the real control and must FAIL on the naive one: a test that
also passes on the naive version proves nothing, so that counts as a failure of this file. Generated data throughout."""
import asyncio
import random
import re
import tempfile
from functools import partial
from pathlib import Path

from agent import run_agent
from enforce import (AmbientTraces, BudgetBusy, BudgetExceeded, CheckThenSpend, FairQueue, FifoQueue,
                     PostFilterRetriever, PromptOnlyTools, Request, ReservationLedger, RunScopedBudget, ScopedRetriever,
                     TenantTraces, TokenBucket, ToolLayer, canary_decision, fleet_mean_alert, hammer_from_processes,
                     per_tenant_alert,
                     simulate_load, tenant_status)
from model import ModelError
from scenarios import (BUDGET_TENANT, INDEX, bad_configs, budget_scenario, canary_run, fleet_scenario, load_scenario,
                       make_controls, quality_scenario, retrieval_scenario, reworded_tallow, shortened_larkspur,
                       tool_scenario, trace_scenario)
from tenancy import (TENANT_IDS, ConfigError, ConfigStore, NaiveConfigStore, UnknownTenant, load_raw_configs,
                     load_store, score_answer, validate_config)

RAWS = {r["tenant_id"]: r for r in load_raw_configs()}
QUIET = ("larkspur-clinic", "tallow-legal", "ferrous-freight")


# %% Paired properties: pass on the control, fail on the naive version
def budget_holds_across_concurrent_runs(make_budget):
    r = budget_scenario(make_budget)
    assert r["bill"] <= r["cap"], f"billed {r['bill']} against a cap of {r['cap']}"


def retrieval_never_starves(make_retriever):
    for tenant, row in retrieval_scenario(make_retriever).items():
        assert row["starved"] == 0 and row["missed"] == 0, f"{tenant} starved: {row}"


def retrieval_never_shows_foreign_text(make_retriever):
    for tenant, row in retrieval_scenario(make_retriever).items():
        assert row["foreign_in_context"] == 0 and row["foreign_exposed"] == 0, f"{tenant} saw foreign text: {row}"


def disallowed_tool_never_executes(make_tools):
    r = tool_scenario(make_tools)
    assert not r["disallowed_effects"], r["disallowed_effects"]
    assert len(r["denied_spans"]) == 1, "the denial is recorded"
    assert r["injected_run_status"] == "answered", "and the run carries on"
    assert len(r["allowed_effects"]) == 1, "the allowlist must not simply block the tool for everyone"


def allowed_tool_stays_inside_the_tenant(make_tools):
    assert not tool_scenario(make_tools)["foreign_record_in_answer"]


def quiet_tenants_survive_a_burst(make_queue):
    r = load_scenario(make_queue)
    for tenant in QUIET:
        assert r[tenant]["p95"] <= 2, f"{tenant} waited p95 {r[tenant]['p95']} ticks"


def spans_are_filed_under_their_own_tenant(make_traces):
    r = trace_scenario(make_traces)
    assert r["spans"] > 0 and r["misattributed"] == 0, f"{r['misattributed']} of {r['spans']} misfiled"


def spans_cannot_be_read_across_tenants(make_traces):
    assert trace_scenario(make_traces)["foreign_spans_read"] == 0


_quality = None


def one_tenant_regression_is_named(alert):
    global _quality
    _quality = _quality or quality_scenario()
    assert "larkspur-clinic" in alert(_quality["before"], _quality["after"])


def invalid_config_is_rejected(make_store):
    store = make_store()
    for label, raw in bad_configs().items():
        try:
            store.propose(raw)
        except ConfigError:
            continue
        raise AssertionError(f"accepted: {label}")


def rollback_moves_one_tenant_only(make_store):
    store = load_store(make_store())
    store.propose(shortened_larkspur(RAWS["larkspur-clinic"]))
    tallow = store.propose(reworded_tallow(RAWS["tallow-legal"]))
    store.start_canary("tallow-legal", tallow, 100)
    store.promote("tallow-legal")
    store.rollback("larkspur-clinic")
    assert "You help clients" in store.resolve("tallow-legal", "r").system_prompt, "tallow's edit was undone"


def proposing_does_not_change_live_traffic(make_store):
    store = load_store(make_store())
    store.propose(shortened_larkspur(RAWS["larkspur-clinic"]))
    assert "Always end with" in store.resolve("larkspur-clinic", "r").system_prompt


def unknown_tenant_fails_closed(make_store):
    store = load_store(make_store())
    try:
        cfg = store.resolve("no-such-tenant", "r")
    except UnknownTenant:
        return
    raise AssertionError(f"served {cfg.tenant_id} config to an unknown tenant")


PAIRED = [
    (budget_holds_across_concurrent_runs, ReservationLedger, [RunScopedBudget, CheckThenSpend]),
    (retrieval_never_starves, ScopedRetriever, [PostFilterRetriever]),
    (retrieval_never_shows_foreign_text, ScopedRetriever, [PostFilterRetriever]),
    (disallowed_tool_never_executes, ToolLayer, [PromptOnlyTools]),
    (allowed_tool_stays_inside_the_tenant, ToolLayer, [PromptOnlyTools]),
    (quiet_tenants_survive_a_burst, FairQueue, [FifoQueue]),
    (spans_are_filed_under_their_own_tenant, TenantTraces, [AmbientTraces]),
    (spans_cannot_be_read_across_tenants, TenantTraces, [AmbientTraces]),
    (one_tenant_regression_is_named, per_tenant_alert, [fleet_mean_alert]),
    (invalid_config_is_rejected, ConfigStore, [NaiveConfigStore]),
    (rollback_moves_one_tenant_only, ConfigStore, [NaiveConfigStore]),
    (proposing_does_not_change_live_traffic, ConfigStore, [NaiveConfigStore]),
    (unknown_tenant_fails_closed, ConfigStore, [NaiveConfigStore]),
]


def run_paired():
    for check, good, naives in PAIRED:
        check(good)
        for naive in naives:
            try:
                check(naive)
            except AssertionError as err:
                print(f"  {check.__name__}: holds on {good.__name__}; {naive.__name__} fails. {str(err)[:60]}")
            else:
                raise SystemExit(f"{check.__name__} passed on the naive {naive}: the check has no teeth")


# %% The ledger, beyond the headline
def test_ledger_holds_across_processes():
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "ledger.db")
        r = hammer_from_processes(path, "t", cap=5_000, workers=4, calls=200, need=100, actual=60)
    assert r["spent"] <= r["cap"] and r["held"] == 0, r
    assert r["granted"] == r["spent"] // 60, "every grant was settled exactly once"
    assert r["spent"] > r["cap"] - 100, "the budget was actually used up, not just refused"


def test_ledger_releases_and_settles_correctly():
    ledger = ReservationLedger({"a": 1000})
    hold = ledger.before_call("a", "r", 600)
    assert ledger.held("a") == 600 and ledger.spent("a") == 0
    ledger.after_call(hold, 100)
    ledger.after_call(hold, 100)  # a retried settle
    assert ledger.spent("a") == 100 and ledger.held("a") == 0, "settling twice charges once"


def test_ledger_busy_versus_exceeded():
    ledger = ReservationLedger({"a": 1000})
    hold = ledger.before_call("a", "r1", 800)
    try:
        ledger.before_call("a", "r2", 800)
        raise AssertionError("over-reserved")
    except BudgetBusy:
        pass  # only held, so waiting might work
    ledger.after_call(hold, 800)
    try:
        ledger.before_call("a", "r3", 800)
        raise AssertionError("overspent")
    except BudgetBusy:
        raise AssertionError("spent money does not come back, so waiting is pointless")
    except BudgetExceeded:
        pass


def test_ledger_expires_a_dead_workers_hold():
    now = [0]
    ledger = ReservationLedger({"a": 1000}, clock=lambda: now[0])
    dead = ledger.before_call("a", "crashed", 900)
    now[0] = 100
    assert ledger.expire(older_than=50) == 1 and ledger.held("a") == 0
    ledger.before_call("a", "next", 900)  # the budget is usable again
    ledger.after_call(dead, 300)  # the provider billed the dead call after all
    assert ledger.spent("a") == 300, "a late settle still counts"


def test_unknown_tenant_has_no_budget():
    try:
        ReservationLedger({"a": 1}).before_call("b", "r", 1)
        raise AssertionError("no ledger row must mean no spend")
    except BudgetExceeded:
        pass


def test_failed_call_releases_and_cancelled_call_is_charged():
    async def outage(req):
        await asyncio.sleep(0)
        raise ModelError("down")

    async def hang(req):
        await asyncio.sleep(3600)

    async def scenario():
        ledger = ReservationLedger({BUDGET_TENANT: 10_000})
        c = make_controls(budget=ledger)
        c.model = outage
        r = await run_agent(c, BUDGET_TENANT, "o", "what is the refund policy")
        assert r.status == "model_error" and ledger.held(BUDGET_TENANT) == 0 and ledger.spent(BUDGET_TENANT) == 0
        c.model = hang
        task = asyncio.create_task(run_agent(c, BUDGET_TENANT, "h", "what is the refund policy"))
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert ledger.held(BUDGET_TENANT) == 0 and ledger.spent(BUDGET_TENANT) > 0, "unknown bill: assume the worst"

    asyncio.run(scenario())


def test_one_tenants_empty_budget_does_not_touch_another():
    limits = {t: 1_000_000 for t in TENANT_IDS} | {"pinwheel-retail": 1}
    c = make_controls(budget=ReservationLedger(limits))

    async def scenario():
        return await asyncio.gather(run_agent(c, "pinwheel-retail", "p", "what is the refund policy"),
                                    run_agent(c, "tallow-legal", "t", "what is the refund policy"))

    pinwheel, tallow = asyncio.run(scenario())
    assert pinwheel.status == "budget_refused" and tallow.status == "answered"


def test_waiting_uses_more_of_the_budget_than_refusing():
    refuse = budget_scenario(partial(ReservationLedger, wait=False))
    wait = budget_scenario(ReservationLedger)
    assert refuse["bill"] <= refuse["cap"] and wait["bill"] <= wait["cap"]
    assert wait["answered"] > refuse["answered"]


# %% Config
def test_validation_reports_each_problem():
    for raw in bad_configs().values():
        try:
            validate_config(raw)
            raise AssertionError("accepted")
        except ConfigError as err:
            assert err.errors
    bad = {**RAWS["larkspur-clinic"], "tools": ["wire_transfer"], "monthly_tokens": 0}
    try:
        validate_config(bad)
        raise AssertionError("accepted")
    except ConfigError as err:
        assert len(err.errors) == 2, "all the problems at once"


def test_canary_splits_repeatably_and_only_for_that_tenant():
    store = load_store()
    v = store.propose(shortened_larkspur(RAWS["larkspur-clinic"]))
    store.start_canary("larkspur-clinic", v, 20)
    first = [store.resolve("larkspur-clinic", f"r{i}").version for i in range(2000)]
    assert first == [store.resolve("larkspur-clinic", f"r{i}").version for i in range(2000)], "a run keeps its bucket"
    assert 0.16 < first.count(v) / 2000 < 0.24
    assert all(store.resolve("tallow-legal", f"r{i}").version == 1 for i in range(200))


def test_rollback_abandons_a_canary_then_walks_back_stable():
    store = load_store()
    v2 = store.propose(RAWS["larkspur-clinic"])
    store.start_canary("larkspur-clinic", v2, 100)
    assert store.resolve("larkspur-clinic", "r").version == v2
    store.promote("larkspur-clinic")
    v3 = store.propose(RAWS["larkspur-clinic"])
    store.start_canary("larkspur-clinic", v3, 50)
    assert store.rollback("larkspur-clinic") == v2, "first the canary goes"
    assert store.rollback("larkspur-clinic") == 1, "then stable walks back"
    assert store.rollback("larkspur-clinic") == 1, "and stops at the first version"


def test_a_running_run_keeps_its_config_through_a_rollback():
    async def scenario():
        store = load_store()
        v = store.propose(shortened_larkspur(RAWS["larkspur-clinic"]))
        store.start_canary("larkspur-clinic", v, 100)
        traces = TenantTraces()
        c = make_controls(store=store, traces=traces)
        task = asyncio.create_task(run_agent(c, "larkspur-clinic", "pinned", "what is the refund policy"))
        await asyncio.sleep(0)
        store.rollback("larkspur-clinic")
        result = await task
        assert result.config_version == v
        assert {s.config_version for s in traces.read("larkspur-clinic", "pinned")} == {v}
        assert store.resolve("larkspur-clinic", "next").version == 1

    asyncio.run(scenario())


def test_canary_gate_catches_the_bad_edit_and_passes_the_good_one():
    store = load_store()
    bad = store.propose(shortened_larkspur(RAWS["larkspur-clinic"]))
    good = store.propose(reworded_tallow(RAWS["tallow-legal"]))
    store.start_canary("larkspur-clinic", bad, 20)
    store.start_canary("tallow-legal", good, 20)
    lark = canary_run(store, "larkspur-clinic", 300, "l")
    tallow = canary_run(store, "tallow-legal", 300, "t")
    assert canary_decision(lark[1], lark[bad]) == "rollback"
    assert canary_decision(tallow[1], tallow[good]) == "promote"
    assert canary_decision((90, 100), (1, 5)) == "wait", "five runs are not evidence, in either direction"


def test_one_core_really_is_driven_by_config():
    source = (Path(__file__).parent / "agent.py").read_text()
    assert not re.search("|".join(TENANT_IDS), source), "the core must not name a tenant"
    closings = {"larkspur-clinic": "clinician", "tallow-legal": "legal advice", "pinwheel-retail": "Anything else",
                "ferrous-freight": "shipment reference"}
    c = make_controls()

    async def scenario():
        return await asyncio.gather(*(run_agent(c, t, f"cfg-{t}-{i}", "what is the refund policy")
                                      for t in TENANT_IDS for i in range(10)))

    results = asyncio.run(scenario())
    for tenant, phrase in closings.items():
        answers = [r.answer for r in results if r.tenant_id == tenant]
        assert any(phrase in a for a in answers), f"{tenant}'s prompt didn't drive its answers"
        others = [p for t, p in closings.items() if t != tenant]
        assert not any(p in a for a in answers for p in others), f"{tenant} got another tenant's wording"


def test_rubrics_differ_per_tenant():
    store = load_store()
    answer = "Text [lk-000]"
    assert score_answer(store.get("larkspur-clinic"), answer, ["lk-000"]) == 50
    assert score_answer(store.get("pinwheel-retail"), answer, ["lk-000"]) == 60
    assert score_answer(store.get("pinwheel-retail"), answer, ["other"]) == 0, "an invented citation scores nothing"


# %% Retrieval details
def test_scope_filter_applies_inside_a_tenant_too():
    store = load_store()
    scopes = store.get("larkspur-clinic").knowledge_scopes
    got = ScopedRetriever(INDEX).retrieve(scopes, "what is the refund policy", 50)
    assert got.docs and all(d.scope in ("larkspur-clinic/policies", "shared/product") for d in got.docs)


# %% Queueing details
def test_fair_queue_wastes_no_capacity():
    assert load_scenario(FairQueue)["finished_at"] == load_scenario(FifoQueue)["finished_at"]
    solo = [Request(str(i), "a", 0, 10) for i in range(100)]
    assert simulate_load(FairQueue({"a": 1}), list(solo), 100).finished_at == 9, "alone, a tenant gets the whole server"


def test_fair_queue_shares_by_cost_and_weight():
    heavy = [Request(f"h{i}", "heavy", 0, 90) for i in range(300)]
    light = [Request(f"l{i}", "light", 0, 10) for i in range(3000)]
    queue = FairQueue({"heavy": 1, "light": 1})
    for r in heavy + light:
        queue.push(r)
    served = {"heavy": 0, "light": 0}
    for _ in range(1000):
        r = queue.pop()
        served[r.tenant] += r.cost
    assert 0.8 < served["heavy"] / served["light"] < 1.25, f"shared by cost, not by request count: {served}"
    queue = FairQueue({"gold": 3, "free": 1})
    for i in range(2000):
        queue.push(Request(str(i), "gold" if i % 2 else "free", 0, 10))
    served = {"gold": 0, "free": 0}
    for _ in range(1000):
        served[queue.pop().tenant] += 1
    assert 2.5 < served["gold"] / served["free"] < 3.5, served


def test_idle_tenant_banks_nothing():
    queue = FairQueue({"a": 1, "b": 1})
    queue.push(Request("a1", "a", 0, 1))
    queue.pop()
    assert queue.deficit["a"] == 0


def test_rate_limit_rejects_the_burst_and_refills():
    bucket = TokenBucket(rate=2.0, burst=5)
    assert sum(bucket.allow(0) for _ in range(20)) == 5
    assert sum(bucket.allow(1) for _ in range(20)) == 2
    limited = load_scenario(FairQueue, with_limits=True)
    assert limited["pinwheel-retail"]["rejected"] > 0
    assert all(limited[t]["rejected"] == 0 for t in QUIET), "a neighbour's burst costs the quiet tenants nothing"
    unlimited = load_scenario(FairQueue)
    assert limited["pinwheel-retail"]["p95"] < unlimited["pinwheel-retail"]["p95"], "a fast 429 beats a slow line"


# %% Quality details
def test_detector_stays_quiet_when_nothing_changed():
    rng = random.Random(7)
    alarms = 0
    for _ in range(2000):
        n = rng.choice([100, 200, 600])
        before = (sum(rng.random() < 0.9 for _ in range(n)), n)
        after = (sum(rng.random() < 0.9 for _ in range(n)), n)
        alarms += tenant_status(before, after) == "regressed"
    assert alarms / 2000 < 0.03, f"false alarm rate {alarms / 2000:.1%}"


def test_too_few_runs_is_not_a_pass():
    assert tenant_status((90, 100), (0, 10)) == "too_few_runs"
    assert tenant_status((90, 100), (45, 100)) == "regressed"


def test_quality_regression_is_what_the_fleet_hides():
    q = quality_scenario()
    assert per_tenant_alert(q["before"], q["after"]) == {"larkspur-clinic"}, "no tenant blamed by mistake"
    assert not fleet_mean_alert(q["before"], q["after"])


# %% Everything at once
def test_whole_path_holds_every_property_at_once():
    f = fleet_scenario()
    for tenant, cap in f["limits"].items():
        assert f["bill"][tenant] <= cap, f"{tenant} over budget"
    assert f["foreign_text_in_prompts"] == 0
    assert {e[0] for e in f["tools"].effects} <= {"pinwheel-retail"}
    refused = {r.tenant_id for r in f["results"] if r.status == "budget_refused"}
    assert refused == {"pinwheel-retail"}, f"only the capped tenant is refused, got {refused}"
    assert all(s.tenant == f["owner"][s.run_id] for s in f["traces"].all_spans())
    assert all(f["ledger"].held(t) == 0 for t in f["limits"]), "no reservation left behind"
    assert not any("PW-CONFIDENTIAL" in r.answer for r in f["results"] if r.tenant_id != "pinwheel-retail")


if __name__ == "__main__":
    print("paired properties, each failing on its naive version:")
    run_paired()
    tests = [(k, v) for k, v in list(globals().items()) if k.startswith("test_")]
    for name, fn in tests:
        fn()
    print(f"ok: {len(PAIRED)} paired properties and {len(tests)} further tests passed")
