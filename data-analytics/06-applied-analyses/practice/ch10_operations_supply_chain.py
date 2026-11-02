# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = ["numpy", "pandas", "matplotlib", "scipy", "pulp[cbc]==4.2.0"]
# ///
"""Chapter 10: how much of each product should the warehouse hold, and how many packers on a Monday?

Run from this folder with: uv run ch10_operations_supply_chain.py
Add --seeds for the extra-seed checks quoted in the note.
"""
import heapq
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pulp
from scipy.stats import norm

import chartstyle as cs
from retail import (erlang_c, load_fulfilment, load_packing_line, load_product_demand, load_products,
                    load_purchase_orders, load_truth)

cs.apply()
pd.set_option("display.width", 130)
rng = np.random.default_rng(10)
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# %% load
products, demand, orders, truth = load_products().set_index("sku"), load_product_demand(), load_purchase_orders(), load_truth("products")
K = truth["demand_dispersion_k"]
print(products.drop(columns="category").head(4).to_string())
print(len(demand), "demand rows;", len(orders), "purchase orders;", demand.week.min().date(), "to", demand.week.max().date())
LINES = products.index[products.christmas_only].tolist()
season_rows = demand[demand.sku.isin(LINES) & (demand.units > 0)].assign(year=lambda d: d.week.dt.year)
print(season_rows.groupby(["sku", "year"]).units.agg(["size", "sum"]).unstack("year").to_string())


# %% newsvendor_forecast
def season_forecast(frame, sku, before=2025):
    """Point forecast of one season from earlier seasons, with the spread of its error."""
    rows = frame[(frame.sku == sku) & (frame.units > 0) & (frame.week.dt.year < before)]
    seasons = rows.groupby(rows.week.dt.year).units.sum()
    weekly_var = rows.groupby(rows.week.dt.year).units.var().mean()
    season_var = 8 * weekly_var                       # one season's own noise
    error_sd = (season_var * (1 + 1 / len(seasons))) ** .5     # plus the error in the forecast itself
    return seasons.mean(), error_sd


def critical_fractile(row):
    under, over = row.unit_price - row.unit_cost, row.unit_cost - row.salvage_value
    return under, over, under / (under + over)


rows = []
for sku in LINES:
    p = products.loc[sku]
    mean, sd = season_forecast(demand, sku)
    under, over, fractile = critical_fractile(p)
    rows.append({"sku": sku, "underage": under, "overage": over, "fractile": fractile, "forecast": mean, "error_sd": sd,
                 "order_q": mean + norm.ppf(fractile) * sd, "true_q": truth["by_sku"][sku]["newsvendor_q"],
                 "true_mean": truth["by_sku"][sku]["season_mean"], "true_sd": truth["by_sku"][sku]["season_sd"]})
plan = pd.DataFrame(rows).set_index("sku")
print(plan.round(2).to_string())
past = season_rows[season_rows.year < 2025].groupby(["sku", "year"]).units.sum().unstack("year")
ratios = pd.concat([past[2023] / past[2024], past[2024] / past[2023]])     # each past season against a forecast made from the other
print("actual over forecast, past seasons:", ratios.round(3).sort_values().tolist())
plan["ratio_q"] = [plan.forecast[s] * ratios.quantile(plan.fractile[s]) for s in LINES]
print("order from the ratio quantile, chapter 1's route:", plan.ratio_q.round(0).to_dict())


# %% newsvendor_truth
def season_draws(level, generator, n=200_000, k=K):
    """Season demand from the generator's own process: eight Gamma-Poisson weeks."""
    return generator.poisson(generator.gamma(k, level / k, (n, 8))).sum(axis=1)


def profit(q, d, p):
    sold = np.minimum(q, d)
    return (p.unit_price * sold + p.salvage_value * (q - sold) - p.unit_cost * q).mean()


rows = []
sims = {}
for sku in LINES:
    p = products.loc[sku]
    d = sims[sku] = season_draws(truth["by_sku"][sku]["weekly_level"], rng)
    row = plan.loc[sku]
    rows.append({"sku": sku, "profit_point": profit(row.forecast, d, p), "profit_fractile": profit(row.order_q, d, p),
                 "profit_ratio": profit(row.ratio_q, d, p), "profit_true_q": profit(row.true_q, d, p), "profit_sim_best": profit(np.quantile(d, row.fractile), d, p),
                 "sim_quantile": np.quantile(d, row.fractile), "stockout_point": (d > row.forecast).mean(), "stockout_fractile": (d > row.order_q).mean(), "target": 1 - row.fractile})
outcome = pd.DataFrame(rows).set_index("sku")
outcome["gain"] = outcome.profit_fractile - outcome.profit_point
outcome["gain_pct"] = outcome.gain / outcome.profit_point
print(outcome.round(3).to_string())
actual = season_rows[season_rows.year == 2025].groupby("sku").units.sum()
print("what 2025 actually did, one season:")
for sku in LINES:
    p, row = products.loc[sku], plan.loc[sku]
    d = np.array([actual[sku]])
    print(f"  {sku}: demand {actual[sku]}, forecast {row.forecast:.0f}, order {row.order_q:.0f}; profit at the forecast {profit(row.forecast, d, p):,.0f}, at the fractile {profit(row.order_q, d, p):,.0f}")

fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
for ax, sku in zip(axes, LINES):
    p, row = products.loc[sku], plan.loc[sku]
    centre = row.true_q
    grid = np.linspace(centre * .7, centre * 1.3, 61)
    ax.plot(grid, [profit(q, sims[sku], p) for q in grid], color=cs.BLUE, lw=2)
    for q, colour, label in ((row.forecast, cs.ORANGE, "forecast"), (row.order_q, cs.AQUA, "fractile")):
        ax.scatter([q], [profit(q, sims[sku], p)], color=colour, zorder=3, s=55, label=f"Order the {label}: {q:,.0f}")
    ax.set_title(sku, loc="left")
    ax.set_xlabel("Units ordered")
    ax.legend(frameon=False, loc="lower center")
axes[0].set_ylabel("Expected profit (£)")
fig.suptitle("Ordering at the fractile wins on two lines of three: TEX-03's forecast was already too high", x=0.01, ha="left", fontweight="bold")
cs.save(fig, "applied-newsvendor-profit.png")

# %% eoq
staples = products.index[~products.christmas_only]
year = demand[demand.week.dt.year == 2025].groupby("sku").units.sum()
eoq = pd.DataFrame({"annual_units": year[staples], "order_cost": products.order_cost[staples], "holding": products.holding_cost_per_year[staples]})
eoq["eoq"] = (2 * eoq.annual_units * eoq.order_cost / eoq.holding) ** .5
eoq["true_eoq"] = [truth["by_sku"][s]["eoq"] for s in staples]
eoq["now_q"] = eoq.annual_units * truth["po_interval_weeks"] / 52.18     # purchase orders go out every eight weeks and carry no quantity
cost = lambda q, e: e.annual_units / q * e.order_cost + q / 2 * e.holding
eoq["cost_now"] = cost(eoq.now_q, eoq)
eoq["cost_eoq"] = cost(eoq.eoq, eoq)
eoq["saving"] = eoq.cost_now - eoq.cost_eoq
print(eoq.round(1).to_string())
print(f"total cycle cost now £{eoq.cost_now.sum():,.0f}, at EOQ £{eoq.cost_eoq.sum():,.0f}, saving {eoq.saving.sum() / eoq.cost_now.sum():.1%}")
print("cost against the best, ordering a multiple of EOQ:", {m: round((m + 1 / m) / 2, 3) for m in (.5, .75, 1.25, 1.5, 2)})

# %% safety_stock
leads = orders.groupby("sku").lead_time_days.agg(["mean", "std"])
history = demand[demand.sku.isin(staples)].groupby("sku").units.agg(["mean", "var"])
stock = pd.DataFrame({"weekly_mean": history["mean"][staples], "weekly_var": history["var"][staples], "lead_weeks": leads["mean"][staples] / 7, "lead_sd_weeks": leads["std"][staples] / 7})


def safety_stock(frame, level):
    """Spread of demand over the lead time: demand's own noise plus lead-time noise, times z for the service level."""
    return norm.ppf(level) * (frame.lead_weeks * frame.weekly_var + frame.weekly_mean ** 2 * frame.lead_sd_weeks ** 2) ** .5


stock["ss_95"] = safety_stock(stock, .95)
stock["true_ss"] = [truth["by_sku"][s]["safety_stock"] for s in staples]
stock["ss_no_lead_noise"] = norm.ppf(.95) * (stock.lead_weeks * stock.weekly_var) ** .5
print(stock.round(1).to_string())
print("share of safety stock owed to lead-time noise:", (1 - stock.ss_no_lead_noise.sum() / stock.ss_95.sum()).round(3))
choices = {s: {"safety_stock": safety_stock(stock, s).sum(), "cost_per_year": (safety_stock(stock, s) * products.holding_cost_per_year[staples]).sum()} for s in (.80, .90, .95, .98, .99)}
print(pd.DataFrame(choices).T.round(0).to_string())


# %% stock_simulation
def simulate_policy(sku, reorder, quantity, generator, years=200, sigma=None, season_reorder=None):
    """Daily (Q, R) stock with the generator's weekly demand and lognormal lead times. Returns service by cycle and fill."""
    t = truth["by_sku"][sku]
    sigma = truth["lead_time_sigma"] if sigma is None else sigma
    level, lead_mean = t["weekly_level"], t["mean_lead_time_days"]
    on_hand, pipeline, due = quantity + reorder, 0, []
    cycles, served, wanted, season_cycles = [], np.zeros(2), np.zeros(2), []
    short_in_cycle = False
    days = 364 * years
    stock_days = 0
    raise_from = 364 - 56 - lead_mean                 # a season-aware rule has to raise the point one lead time early
    for day in range(days):
        if day % 7 == 0:
            in_season = (day % 364) >= 364 - 56
            mean = level * (1 + truth["staple_season_lift"] * in_season)
            rate = generator.gamma(K, mean / K) / 7
        while due and due[0][0] <= day:
            _, amount, placed = heapq.heappop(due)
            on_hand += amount
            pipeline -= amount
            cycles.append(short_in_cycle)
            season_cycles.append(placed)
            short_in_cycle = False
        d = generator.poisson(rate)
        sold = min(d, on_hand)
        slot = int(in_season)
        served[slot] += sold
        wanted[slot] += d
        if sold < d:
            short_in_cycle = True
        on_hand -= sold
        stock_days += on_hand
        point = season_reorder if season_reorder is not None and day % 364 >= raise_from else reorder
        while on_hand + pipeline <= point:
            lead = max(round(lead_mean * generator.lognormal(-sigma ** 2 / 2, sigma)), 1)
            heapq.heappush(due, (day + lead, quantity, in_season))
            pipeline += quantity
    cycles, season_cycles = np.array(cycles), np.array(season_cycles)
    return {"cycle_service_off_season": 1 - cycles[~season_cycles].mean(), "cycle_service_in_season": 1 - cycles[season_cycles].mean() if season_cycles.any() else np.nan,
            "cycle_service_all": 1 - cycles.mean(), "fill_off_season": served[0] / wanted[0], "fill_in_season": served[1] / wanted[1], "cycles_per_year": len(cycles) / years, "mean_on_hand": stock_days / days}


results = []
for sku in staples:
    weekly = stock.loc[sku, "weekly_mean"]
    lead = stock.loc[sku, "lead_weeks"]
    results.append({"sku": sku, **simulate_policy(sku, weekly * lead + stock.loc[sku, "ss_95"], eoq.loc[sku, "eoq"], rng)})
run = pd.DataFrame(results).set_index("sku")
print(run.round(3).to_string())
print(run.mean().round(3).to_string())
ladder = []
for level in (.80, .90, .95, .98, .99):
    ss = safety_stock(stock, level)
    one = pd.DataFrame([simulate_policy(s, stock.weekly_mean[s] * stock.lead_weeks[s] + ss[s], eoq.eoq[s], rng, years=100) for s in staples]).mean()
    ladder.append({"target": level, "cost_per_year": (ss * products.holding_cost_per_year[staples]).sum(), **one[["cycle_service_all", "cycle_service_off_season", "cycle_service_in_season", "fill_off_season", "fill_in_season"]]})
ladder = pd.DataFrame(ladder)
print(ladder.round(3).to_string(index=False))

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(ladder.target, ladder.cycle_service_off_season, color=cs.BLUE, marker="o", lw=2)
ax.plot(ladder.target, ladder.cycle_service_in_season, color=cs.ORANGE, marker="o", lw=2)
ax.plot(ladder.target, ladder.target, color=cs.MUTED, lw=1, ls="--")
ax.text(.992, ladder.cycle_service_off_season.iloc[-1], "Cycles ordered\noff season", color=cs.BLUE, va="center")
ax.text(.992, ladder.cycle_service_in_season.iloc[-1], "Cycles ordered\nin season", color=cs.ORANGE, va="center")
ax.text(.845, .825, "Target", color=cs.MUTED, va="center")
ax.set_xlim(.78, 1.03)
ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
ax.set_xlabel("Service level the formula was asked for")
ax.set_ylabel("Share of cycles with no stockout, simulated")
ax.set_title("A flat reorder point misses its target when the season arrives", loc="left")
cs.save(fig, "applied-safety-stock-service.png")

# %% packing_line
line, line_truth = load_packing_line(), load_truth("packing_line")
service = line_truth["service_rate_per_hour"]
print(len(line), "parcels over", line.date.nunique(), "days, pack minutes", round(line.pack_minutes.mean(), 2))
summary = line.groupby("weekday").agg(days=("date", "nunique"), parcels=("parcel_id", "size"), mean_wait=("wait_minutes", "mean"), p95_wait=("wait_minutes", lambda s: s.quantile(.95)), share_waiting=("wait_minutes", lambda s: (s > 0).mean())).reindex(WEEKDAYS)
summary["per_hour"] = summary.parcels / summary.days / 8
summary["packers"] = [line_truth["packers"][d] for d in WEEKDAYS]
summary["rho"] = summary.per_hour / (service * summary.packers)
summary["erlang_c"] = [erlang_c(line_truth["arrivals_per_hour"][d], service, line_truth["packers"][d])["mean_wait"] * 60 for d in WEEKDAYS]
print(summary.round(3).to_string())


# %% littles_law
def little_day(day):
    """Queue length as a step function of time, and the two sides of L = lambda W on one day."""
    start = day.arrived.min().normalize() + pd.Timedelta(hours=8)
    arrive = (day.arrived - start).dt.total_seconds().to_numpy() / 60
    begin = (day.pack_start - start).dt.total_seconds().to_numpy() / 60
    finish = (day.pack_end - start).dt.total_seconds().to_numpy() / 60
    times = np.r_[arrive, begin]
    steps = np.r_[np.ones(len(arrive)), -np.ones(len(begin))]
    order = np.argsort(times, kind="stable")
    queue = np.cumsum(steps[order])
    span = finish.max()
    area = (queue[:-1] * np.diff(times[order])).sum()
    in_queue = area / span
    return pd.Series({"span": span, "L_q": in_queue, "lambda_W": len(day) / span * (begin - arrive).mean(), "busy": (finish - begin).sum() / span})


days = line.groupby(["date", "weekday"]).apply(little_day, include_groups=False).reset_index()
print(days.head(3).assign(date=lambda d: d.date.dt.date).round(4).to_string(index=False))
print("largest gap between L_q and lambda times W across", len(days), "days:", f"{(days.L_q - days.lambda_W).abs().max():.2e}")
print(days.groupby("weekday")[["L_q", "busy"]].mean().reindex(WEEKDAYS).round(2).to_string())
counts = []
for date, day in line.groupby("date"):
    start = date + pd.Timedelta(hours=8)
    for clock in pd.date_range(start, periods=16, freq="30min"):
        counts.append({"weekday": day.weekday.iloc[0], "queue": ((day.arrived <= clock) & (day.pack_start > clock)).sum()})
floor = pd.DataFrame(counts).groupby("weekday").queue.mean().reindex(WEEKDAYS)
print(pd.DataFrame({"mean_queue_seen_every_30_min": floor, "wait_implied": floor / summary.per_hour * 60, "wait_recorded": summary.mean_wait}).round(2).to_string())


# %% queue_simulation
def simulate_days(arrivals, packers, generator, n_days=2000, service_rate=service, hours=8):
    """The generator's own day: Poisson count, uniform arrivals, exponential service, first come first served, empty at 08:00."""
    waits, overruns, day_means = [], [], []
    for _ in range(n_days):
        n = generator.poisson(arrivals * hours)
        times = np.sort(generator.uniform(0, hours * 60, n))
        minutes = generator.exponential(60 / service_rate, n)
        free = [0.0] * packers
        heapq.heapify(free)
        w = np.zeros(n)
        for i in range(n):
            soonest = heapq.heappop(free)
            begin = max(times[i], soonest)
            w[i] = begin - times[i]
            heapq.heappush(free, begin + minutes[i])
        waits.append(w)
        overruns.append(max(free) - hours * 60)
        day_means.append(w.mean())
    return np.concatenate(waits), np.array(overruns), np.array(day_means)


rows = []
for day, c in [("Monday", 5), ("Monday", 6), ("Monday", 7), ("Tuesday", 4), ("Tuesday", 5), ("Wednesday", 4), ("Wednesday", 5), ("Thursday", 3), ("Thursday", 4), ("Friday", 3), ("Friday", 4)]:
    rate = line_truth["arrivals_per_hour"][day]
    w, over, means = simulate_days(rate, c, rng)
    theory = erlang_c(rate, service, c)
    recorded = summary.loc[day, "mean_wait"] if c == line_truth["packers"][day] else np.nan
    rows.append({"day": day, "packers": c, "rho": theory["rho"], "erlang_c": theory["mean_wait"] * 60, "simulated": w.mean(), "recorded": recorded,
                 "p95": np.quantile(w, .95), "over_10_min": (w > 10).mean(), "day_sd": means.std(), "overrun_min": max(0, over.mean())})
queue_table = pd.DataFrame(rows)
print(queue_table.round(3).to_string(index=False))
simulated = queue_table.set_index(["day", "packers"])

fig, ax = plt.subplots(figsize=(8.5, 4.2))
for day, c, colour in (("Monday", 6, cs.BLUE), ("Wednesday", 4, cs.ORANGE)):
    rate = line_truth["arrivals_per_hour"][day]
    n_days = 3000
    sums, numbers = np.zeros(8), np.zeros(8)
    for _ in range(n_days):
        n = rng.poisson(rate * 8)
        times = np.sort(rng.uniform(0, 480, n))
        minutes = rng.exponential(5, n)
        free = [0.0] * c
        heapq.heapify(free)
        for i in range(n):
            soonest = heapq.heappop(free)
            begin = max(times[i], soonest)
            hour = int(times[i] // 60)
            sums[hour] += begin - times[i]
            numbers[hour] += 1
            heapq.heappush(free, begin + minutes[i])
    profile = sums / numbers
    ax.plot(np.arange(8) + 8.5, profile, color=colour, lw=2, marker="o")
    level = erlang_c(rate, service, c)["mean_wait"] * 60
    ax.axhline(level, color=colour, lw=1, ls="--")
    ax.text(16.1, level, f"{day} {c} packers:\nErlang C {level:.1f} min", color=colour, va="center")
    print(day, "wait by arrival hour:", profile.round(2).tolist())
ax.set_xlim(8, 18.4)
ax.set_xticks(range(8, 17), [f"{h:02d}:00" for h in range(8, 17)])
ax.set_ylabel("Mean wait (minutes)")
ax.set_xlabel("Hour the parcel arrived")
ax.set_title("Every day starts empty, so the morning runs well under the steady-state wait", loc="left")
cs.save(fig, "applied-packing-wait-by-hour.png")

# %% marginal_packer
wage_day = line_truth["wage_per_hour"] * 8
rows = []
for day in WEEKDAYS:
    c = line_truth["packers"][day]
    rate = line_truth["arrivals_per_hour"][day]
    now, _, _ = simulate_days(rate, c, rng)
    more, _, _ = simulate_days(rate, c + 1, rng)
    rows.append({"day": day, "packers": c, "wait_now": now.mean(), "wait_with_one_more": more.mean(), "parcel_minutes_saved_per_day": (now.mean() - more.mean()) * rate * 8,
                 "break_even_per_parcel_hour": wage_day / ((now.mean() - more.mean()) * rate * 8 / 60)})
marginal = pd.DataFrame(rows)
print(marginal.round(2).to_string(index=False))
print(f"a packer-day costs £{wage_day:.0f}")

# %% requirements
requirement = {}
wait_tables = {}
for day in WEEKDAYS:
    rate = line_truth["arrivals_per_hour"][day]
    wait_tables[day] = {c: simulate_days(rate, c, rng, n_days=1000)[0].mean() for c in range(max(1, int(rate // service)), int(rate // service) + 5)}
print(pd.DataFrame(wait_tables).round(2).T.to_string())
for target in (1, 2, 3, 5):
    requirement[target] = {day: min(c for c, w in wait_tables[day].items() if w <= target) for day in WEEKDAYS}
requirement = pd.DataFrame(requirement).T.rename_axis("max_mean_wait")
requirement["packer_days"] = requirement.sum(axis=1)
print(requirement.to_string())


# %% shift_plan
def shift_plan(need, premium=1.5, integer=True):
    """Cheapest cover: permanent packers work all five days, agency cover is bought by the day at a premium."""
    model = pulp.LpProblem("shifts", pulp.LpMinimize)
    kind = "Integer" if integer else "Continuous"
    permanent = model.add_variable("permanent", lowBound=0, cat=kind)
    agency = {day: model.add_variable(f"agency_{day}", lowBound=0, cat=kind) for day in WEEKDAYS}
    model += 5 * wage_day * permanent + pulp.lpSum(premium * wage_day * agency[day] for day in WEEKDAYS)
    for day in WEEKDAYS:
        model += permanent + agency[day] >= need[day], day
    model.solve(pulp.COIN_CMD(msg=False))
    prices = {c.name: c.pi for c in model.constraints()} if not integer else None
    return {"cost": pulp.value(model.objective), "permanent": permanent.value(), "agency": {d: agency[d].value() for d in WEEKDAYS}, "prices": prices}


print("solvers available:", pulp.listSolvers(onlyAvailable=True))
current = {d: line_truth["packers"][d] for d in WEEKDAYS}
print(f"today's rota: {sum(current.values())} packer-days, £{sum(current.values()) * wage_day:,.0f} a week at the flat wage")
for premium in (1.2, 1.5, 2.0):
    for target in (3, 5):
        need = requirement.loc[target, WEEKDAYS].to_dict()
        relaxed, whole = shift_plan(need, premium, integer=False), shift_plan(need, premium)
        print(f"premium {premium}, mean wait at most {target} min, need {list(need.values())}: £{whole['cost']:,.0f} (LP £{relaxed['cost']:,.0f}), "
              f"permanent {whole['permanent']:.0f}, agency {[round(whole['agency'][d]) for d in WEEKDAYS]}, shadow prices {[round(relaxed['prices'][d]) for d in WEEKDAYS]}")
for value in (5, 7, 10, 20):
    picks = {}
    for day in WEEKDAYS:
        rate = line_truth["arrivals_per_hour"][day]
        costs = {c: c * wage_day + value * rate * 8 * w / 60 for c, w in wait_tables[day].items()}
        picks[day] = min(costs, key=costs.get)
    print(f"a parcel-hour of waiting worth £{value}: cheapest packers {list(picks.values())}, {sum(picks.values())} packer-days")

# %% plan_against_truth
plan_need = requirement.loc[3, WEEKDAYS].to_dict()
whole = shift_plan(plan_need)
chosen = {d: int(round(whole["permanent"] + whole["agency"][d])) for d in WEEKDAYS}
rows = []
for day in WEEKDAYS:
    rate = line_truth["arrivals_per_hour"][day]
    new, over_new, _ = simulate_days(rate, chosen[day], rng)
    old, over_old, _ = simulate_days(rate, current[day], rng)
    rows.append({"day": day, "packers_now": current[day], "wait_now": old.mean(), "p95_now": np.quantile(old, .95), "packers_plan": chosen[day], "wait_plan": new.mean(), "p95_plan": np.quantile(new, .95), "overrun_plan": over_new.mean()})
check = pd.DataFrame(rows)
print(check.round(2).to_string(index=False))
parcels = np.array([line_truth["arrivals_per_hour"][d] * 8 for d in WEEKDAYS])
print(f"parcel-weighted mean wait: now {np.average(check.wait_now, weights=parcels):.2f} min, plan {np.average(check.wait_plan, weights=parcels):.2f} min; packer-days now {sum(current.values())}, plan {sum(chosen.values())}")
for uplift in (1.1, 1.2, 1.3):
    needs = {}
    for day in ("Monday", "Wednesday"):
        rate = line_truth["arrivals_per_hour"][day] * uplift
        for c in range(int(rate // service) + 1, int(rate // service) + 6):
            if simulate_days(rate, c, rng, n_days=500)[0].mean() <= 3:
                needs[day] = c
                break
    print(f"parcels up {uplift - 1:.0%}: packers to hold a 3-minute mean wait", needs)

# %% fulfilment
fulfil, fulfil_truth = load_fulfilment(), load_truth("fulfilment")
fulfil["peak"] = fulfil.order_date.dt.month.isin([11, 12])
print(fulfil.groupby("peak")[["pick_minutes", "pack_minutes", "lead_time_days"]].mean().round(2).to_string())
print(fulfil.groupby("category")[["pick_minutes", "pack_minutes", "lead_time_days"]].mean().round(2).to_string())
print("pick multiplier in peak by category:", (fulfil[fulfil.peak].groupby("category").pick_minutes.mean() / fulfil[~fulfil.peak].groupby("category").pick_minutes.mean()).round(2).to_dict())
outage = fulfil.order_date.between(fulfil_truth["outage_start"], fulfil_truth["outage_end"])
print("lead time in the June 2023 outage:", round(fulfil[outage].lead_time_days.mean(), 2), "| rest of non-peak:", round(fulfil[~outage & ~fulfil.peak].lead_time_days.mean(), 2))
print("delivered within 3 days, not peak:", round((fulfil[~fulfil.peak & ~outage].lead_time_days <= 3).mean(), 3), "| peak:", round((fulfil[fulfil.peak].lead_time_days <= 3).mean(), 3))
print("mean pack minutes here", round(fulfil.pack_minutes.mean(), 2), "| on the packing line", round(line.pack_minutes.mean(), 2))
print("rows per weekday in 2025, Monday first:", fulfil[fulfil.order_date.dt.year == 2025].groupby(fulfil.order_date.dt.dayofweek).size().tolist())
print("packing-line parcels per Monday by month:", line[line.weekday == "Monday"].groupby(line.date.dt.month).size().div(line[line.weekday == "Monday"].groupby(line.date.dt.month).date.nunique()).round(0).to_dict())

# %% try_it
print("Try it 1: TEX-03 with no salvage value")
p = products.loc["TEX-03"].copy()
t = truth["by_sku"]["TEX-03"]
for salvage in (p.salvage_value, 0.0):
    p.salvage_value = salvage
    u, o, f = critical_fractile(p)
    q = norm.ppf(f, t["season_mean"], t["season_sd"])
    print(f"  salvage £{salvage:.0f}: fractile {f:.3f}, order {q:,.0f}, expected profit £{profit(q, sims['TEX-03'], p):,.0f}, profit at the old order £{profit(t['newsvendor_q'], sims['TEX-03'], p):,.0f}")
print("Try it 2: a reorder point that knows about the season")
rows = []
for s_ in staples:
    weekly_, lead_, ss_ = stock.weekly_mean[s_], stock.lead_weeks[s_], stock.ss_95[s_]
    base_ = truth["by_sku"][s_]["weekly_level"]
    flat = simulate_policy(s_, weekly_ * lead_ + ss_, eoq.eoq[s_], rng, years=100)
    aware = simulate_policy(s_, base_ * lead_ + ss_, eoq.eoq[s_], rng, years=100, season_reorder=base_ * (1 + truth["staple_season_lift"]) * lead_ + ss_)
    rows.append({"flat_in": flat["cycle_service_in_season"], "flat_off": flat["cycle_service_off_season"], "aware_in": aware["cycle_service_in_season"], "aware_off": aware["cycle_service_off_season"],
                 "flat_stock_cost": flat["mean_on_hand"] * products.holding_cost_per_year[s_], "aware_stock_cost": aware["mean_on_hand"] * products.holding_cost_per_year[s_]})
print(pd.DataFrame(rows).agg({"flat_in": "mean", "flat_off": "mean", "aware_in": "mean", "aware_off": "mean", "flat_stock_cost": "sum", "aware_stock_cost": "sum"}).round(3).to_string())
print("Try it 3: parcels up 10%, packers unchanged")
for day in ("Monday", "Wednesday"):
    rate = line_truth["arrivals_per_hour"][day] * 1.1
    w, over, _ = simulate_days(rate, current[day], rng)
    print(f"  {day} {current[day]} packers, {rate:.1f} parcels an hour: rho {rate / (service * current[day]):.3f}, mean wait {w.mean():.2f} min, p95 {np.quantile(w, .95):.1f}, overrun {over.mean():.0f} min")
print("Try it 4: the packing line at the fulfilment table's pack time, 3.5 minutes")
for day, c in (("Monday", 4), ("Monday", 5), ("Monday", 6), ("Wednesday", 3), ("Wednesday", 4)):
    rate = line_truth["arrivals_per_hour"][day]
    w, _, _ = simulate_days(rate, c, rng, service_rate=60 / 3.5)
    print(f"  {day} {c} packers: rho {rate * 3.5 / 60 / c:.3f}, mean wait {w.mean():.2f} min")

# %% extra_seeds
if "--seeds" in sys.argv:
    rows = []
    for s in range(100, 112):
        pr, dm, tr = load_products(seed=s).set_index("sku"), load_product_demand(seed=s), load_truth("products", seed=s)
        gens = np.random.default_rng(s)
        gains = []
        for sku in LINES:
            mean, sd = season_forecast(dm, sku)
            under, over, fractile = critical_fractile(pr.loc[sku])
            d = season_draws(tr["by_sku"][sku]["weekly_level"], gens, n=100_000)
            gains.append((profit(mean + norm.ppf(fractile) * sd, d, pr.loc[sku]) - profit(mean, d, pr.loc[sku])) / profit(mean, d, pr.loc[sku]))
        waits = load_packing_line(seed=s).groupby("weekday").wait_minutes.mean().reindex(WEEKDAYS)
        rows.append({"seed": s, "newsvendor_gain_pct": 100 * np.mean(gains), **waits.round(2).to_dict()})
    seeds = pd.DataFrame(rows)
    print(seeds.round(2).to_string(index=False))
    print(seeds.drop(columns="seed").agg(["mean", "sem"]).round(2).T.to_string())
    print("seeds where Wednesday waits longer than Monday:", (seeds.Wednesday > seeds.Monday).sum(), "of", len(seeds), "| newsvendor gain positive:", (seeds.newsvendor_gain_pct > 0).sum())
