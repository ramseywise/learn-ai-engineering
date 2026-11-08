---
origin: synthesis
sources:
  - "Makridakis et al., The M5 uncertainty competition, International Journal of Forecasting, 2022 (abstract only)"
confidence: high
cleaned: 2026-11-02
---

# Operations and supply chain: stock and reserve

A forecast of 1,120 units is not an order of 1,120 units. Fernhill's warehouse manager has to commit to stock months ahead, and the decision turns on a spread and two prices rather than on an average. We work out how much to order, how often, and how much to hold in reserve with the standard formulas, then run each one against a simulated truth to see where the formula holds and where it doesn't. The packers, the other half of the warehouse question, are in [10b](10b-packers-queues-and-a-shift-plan.md).

---

## The question and the data

The business question is **how much of each product should the warehouse hold, and how many packers on a Monday?**

Four tables come from `practice/retail.py`, and all are overlays on the shop's other tables:

- **`load_products()`** has 12 products with price, cost, salvage value, holding cost and order cost. Three are sold only for the eight weeks before Christmas.
- **`load_product_demand()`** has weekly units per product for three years. **`load_purchase_orders()`** has 20 orders per product with their lead times, but no quantities.
- **`load_packing_line()`** has every parcel over 13 weeks: when it arrived, when packing started and ended, and the wait. `load_truth("packing_line")` has the arrival rates, the service rate of 12 parcels an hour and the wage.
- **`load_fulfilment()`** has pick and pack times and delivery lead time per order line, used at the end.

These tables don't reconcile with each other, and we say where that matters. The code blocks are the main sections of `practice/ch10_operations_supply_chain.py` in order, each relying on those before it, with the chart code left to the script. Run them with `uv run ch10_operations_supply_chain.py` from the practice folder; it takes about half a minute.

## One season's order: the newsvendor

A Christmas line is ordered once, before the season, and what's left after Christmas is sold off cheaply. This is the **newsvendor** problem. Each unit short loses the **underage cost**, price minus cost. Each unit left over loses the **overage cost**, cost minus salvage. Ordering one more unit pays when the chance it sells, times the underage cost, beats the chance it doesn't, times the overage cost. That gives the order as a quantile of demand, at the **critical fractile**:

    fractile = underage / (underage + overage)

It is the same argument as the critical ratio in [the forecasting chapter](01-forecasting.md#from-forecast-to-decision), where short staff cost £12 and spare staff £4. Here it's run from the season's forecast and the spread of that forecast's error. We forecast 2025 from the two earlier seasons, so the error includes both the season's own noise and the mistake in the forecast. The plan named Cachon and Terwiesch's *Matching Supply with Demand* as the text for this chapter. We haven't read it, so the formulas here are stated from the derivation above and tested against simulation.

```python
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
```

```text
order from the ratio quantile, chapter 1's route: {'KIT-03': 738.0, 'TEX-03': 1215.0, 'LGT-03': 892.0}
```

The margin on these lines is nearly three times what a leftover costs, so the fractiles are all near 0.73: order well above the forecast. Chapter 1's route takes the ratio of actual to forecast and reads its quantile. With two past seasons there are only six ratios, three mirror-image pairs between 0.95 and 1.05, so it produces smaller orders. The true spread is about 13% of a season.

Now score each order on 200,000 seasons from the generator's own demand process, which is what a real retailer never has.

```python
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
```

```text
        profit_point  profit_fractile  profit_ratio  profit_true_q  profit_sim_best  sim_quantile  stockout_point  stockout_fractile  target     gain  gain_pct
sku
KIT-03     14630.757        14895.726     14821.497      14897.602        14897.919         776.0           0.538              0.289   0.267  264.968     0.018
TEX-03     16805.553        16666.546     16840.310      16843.556        16843.923        1203.0           0.365              0.114   0.273 -139.007    -0.008
LGT-03     16754.662        17614.895     17252.483      18085.886        18086.214        1037.0           0.800              0.592   0.259  860.233     0.051
what 2025 actually did, one season:
  KIT-03: demand 652, forecast 708, order 770; profit at the forecast 13,900, at the fractile 13,404
  TEX-03: demand 996, forecast 1164, order 1296; profit at the forecast 14,925, at the fractile 14,136
  LGT-03: demand 1082, forecast 854, order 927; profit at the forecast 17,090, at the fractile 18,536
```

Adding up the three lines, ordering the forecast earns £48,191, the ratio route £48,914, the fractile £49,177, and knowing the truth £49,827. So the fractile earns about 2% more than ordering the forecast, and it gets most of the way to the best possible.

It doesn't win everywhere, and the two exceptions say something:

- **TEX-03 loses £139.** Two good seasons put its forecast at 1,164 against a true mean of 1,120, and its error spread came out at 218 against a true 144. The forecast is already above the mean, so adding a buffer to it overshoots. The stockout rate of 11% is far below the 27% target.
- **LGT-03 stocks out 59% of the time** against a 26% target, because its forecast of 854 is far below the true 960. The fractile helps, adding £860, and is still £471 short of the best.
- **One real season isn't a verdict.** On the 2025 demand that really happened, the fractile lost on two lines and won on the third, ending £161 up across all three. A rule that's right on average is often wrong in a given year.

Over seeds 100 to 111, the average gain across the three lines was 1.70%, and it was positive on 11 of the 12. So the gain is real and small, and the forecast matters more: the distance between our orders and the best orders is mostly forecast error, not the choice of quantile.

![Three panels of expected profit against units ordered, for KIT-03, TEX-03 and LGT-03. Each curve rises steeply, peaks and falls more slowly. On KIT-03 and LGT-03 the fractile order sits higher on the curve than the forecast; on TEX-03 the forecast sits nearer the peak.](../../sources/images/applied-newsvendor-profit.png)

*Image Source: generated by `practice/ch10_operations_supply_chain.py`. The fractile beats the forecast on two lines; the third was forecast too high to begin with. Profit falls faster to the left of the peak than to the right, which is why the order sits above the mean.*

This is why stock decisions need a forecast distribution and not a point. The M5 uncertainty competition, of which we read the abstract only, asked for nine quantiles of each of 42,840 Walmart unit-sales series, and those quantiles are the input that this calculation needs.

## How much to order at a time: EOQ

The nine staple products sell all year and can be reordered. Ordering more at a time means fewer order costs and more stock to hold. Balancing those gives the **economic order quantity**, EOQ = √(2 × annual units × order cost / holding cost per unit per year). The purchase orders table goes out every eight weeks and holds no quantities, so we take today's order to be eight weeks of 2025 demand. That is our assumption.

```python
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
```

```text
        annual_units  order_cost  holding    eoq  true_eoq  now_q  cost_now  cost_eoq  saving
sku
KIT-01          3175        40.0      4.5  237.6     246.1  486.8    1356.1    1069.1   287.0
KIT-02          6169        40.0      1.5  573.6     577.3  945.8     970.3     860.4   109.9
TEX-01          5009        35.0      2.2  394.8     387.6  768.0    1092.2     888.2   204.0
TEX-02          1923        35.0      5.2  160.1     162.8  294.8    1002.2     840.7   161.5
LGT-01          2549        45.0      3.5  256.0     256.4  390.8     977.4     896.1    81.3
LGT-02          1083        45.0      7.0  118.0     120.9  166.0     874.7     826.0    48.6
FUR-01           485       120.0     21.2   74.0      71.6   74.4    1572.8    1572.7     0.0
FUR-02           217       120.0     35.0   38.6      39.5   33.3    1364.9    1350.1    14.8
FUR-03           673       120.0     15.0  103.8     104.4  103.2    1556.6    1556.5     0.0
total cycle cost now £10,767, at EOQ £9,860, saving 8.4%
cost against the best, ordering a multiple of EOQ: {0.5: 1.25, 0.75: 1.042, 1.25: 1.025, 1.5: 1.083, 2: 1.25}
```

Estimates sit close to the truth, which is calculated from expected demand rather than 2025's. EOQ saves 8.4%, or £907 a year, and nothing on furniture, where eight weeks happens to be about right. The last line explains why EOQ isn't worth arguing over: an order 25% over the best costs only 2.5% more, and 50% over costs 8.3% more. The cost curve is flat near the bottom, and a rounder number that fits a pallet is usually fine.

## How much to keep in reserve: safety stock

Stock is reordered when it falls to a **reorder point**: expected demand over the lead time, plus **safety stock** for the times demand runs high or the delivery runs late. Both sources of noise count:

    safety stock = z × √(lead time × weekly demand variance + weekly mean² × lead time variance)

Here z comes from the **service level**, the chance of getting through one order cycle without running out. That number is a decision, not an estimate, and the second table prices it.

```python
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
```

```text
        weekly_mean  weekly_var  lead_weeks  lead_sd_weeks  ss_95  true_ss  ss_no_lead_noise
sku
KIT-01         69.6      1041.0         2.8            0.7  120.0    108.7              88.6
KIT-02        124.7      3022.8         2.2            0.4  159.7    144.5             133.0
TEX-01         96.6      1451.8         3.9            1.2  225.7    192.9             124.1
TEX-02         38.9       297.4         4.0            1.1   88.9     80.9              56.7
LGT-01         48.8       455.8         4.7            1.3  128.4    124.3              75.8
LGT-02         21.4        85.3         5.1            1.4   59.2     56.7              34.3
FUR-01          9.0        23.7         8.0            2.6   44.9     35.4              22.6
FUR-02          4.5         8.9         9.3            2.0   21.2     20.9              14.9
FUR-03         12.7        48.4         6.5            0.9   35.0     46.3              29.2
share of safety stock owed to lead-time noise: 0.344
      safety_stock  cost_per_year
0.80         452.0         2476.0
0.90         688.0         3770.0
0.95         883.0         4839.0
0.98        1102.0         6042.0
0.99        1249.0         6844.0
```

Going from 95% to 99% costs another £2,005 a year in held stock, against £4,839 for the whole of the 95% buffer. About a third of the safety stock is there only because deliveries vary, and leaving that out is the commonest shortcut. Most of the estimates run above the truth because the sample variance of weekly demand includes the seasonal swing. FUR-03 runs below, because 20 orders happened to give a lead-time spread of 0.9 weeks when the true one is about 1.8.

### Does the buffer deliver what it promises?

Each policy goes through 200 simulated years of the generator's demand and lead times, with unmet demand lost.  is a daily loop, left to the script. **Cycle service** is the share of order cycles with no stockout, and **fill rate** is the share of units sold.

```python
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
```

```text
        cycle_service_off_season  cycle_service_in_season  cycle_service_all  fill_off_season  fill_in_season  cycles_per_year  mean_on_hand
sku
FUR-03                     0.864                    0.691              0.825            0.973           0.923            6.275        83.442
cycle_service_off_season      0.948
cycle_service_in_season       0.794
cycle_service_all             0.914
fill_off_season               0.991
fill_in_season                0.947
cycles_per_year               9.602
mean_on_hand                211.094
 target  cost_per_year  cycle_service_all  cycle_service_off_season  cycle_service_in_season  fill_off_season  fill_in_season
   0.80       2476.020              0.816                     0.862                    0.640            0.974           0.892
   0.90       3770.279              0.883                     0.925                    0.731            0.985           0.931
   0.95       4839.100              0.916                     0.944                    0.814            0.991           0.945
   0.98       6042.056              0.947                     0.968                    0.872            0.994           0.968
   0.99       6844.032              0.959                     0.978                    0.891            0.997           0.976
```

Outside the season, the formula gets what it promises: 94.8% against a target of 95%. In season it gets 79.4% (81.4% in the ladder's separate draw), because the reorder point uses a year-round mean, and demand runs 60% higher in those weeks. The all-year figure of 91.4% hides this. So does the fill rate, which still looks healthy at 94.7%, because a stockout late in a cycle loses few units. FUR-03 shows the other way to miss, at 86.4% off season, because its lead-time spread was underestimated. Asking the formula for 99% only lifts in-season service to 89%. A higher z is a costly fix for a wrong mean, and exercise 2 tries the proper one.

![Line chart of simulated cycle service against the service level the formula was asked for, from 80% to 99%. Cycles ordered off season run near the target line. Cycles ordered in season run 10 to 20 points below it.](../../sources/images/applied-safety-stock-service.png)

*Image Source: generated by `practice/ch10_operations_supply_chain.py`. The same reorder point serves two different demand rates, so it misses on the higher one at every setting.*

## The packing line

The packers, utilisation, Little's law, Erlang C, the Monday and Wednesday crews, the shift plan and the wider fulfilment log are in [10b, Packers: queues, Little's law and a shift plan](10b-packers-queues-and-a-shift-plan.md).

## Recommendation

- **Christmas lines: order at the fractile, near 73%, above the forecast.** Expect about 2% more profit on average and don't judge the rule by one season. Spend more effort on the forecast: on LGT-03 forecast error cost more than the rule earned.
- **Staples: move to EOQ where it's far from eight weeks,** on kitchen and textiles, for about £900 a year.
- **Set the reorder point by season.** A flat one gives 79% in season against a 95% target. Raising z is the expensive way to fix this.
- **Treat 95% as a decision.** Going to 99% costs about £2,000 a year more in held stock.

These are simulated tables and real demand won't match the simulation. What would change the stock recommendations: a better forecast error than the two seasons here gave. Cachon and Terwiesch, and Hillier and Lieberman, are the textbook treatments; neither was read here.

The packer recommendations (Monday's crew and the plan) are in [10b](10b-packers-queues-and-a-shift-plan.md#recommendation).

## Pitfalls

- **Ordering the point forecast.** The symptom is a stockout rate of 37% to 80% here, against a target of about 27%. The mean is the right order only when underage and overage cost the same.
- **Trusting the forecast's own error.** Two seasons gave TEX-03 an error spread 50% too large and LGT-03 a mean 11% too low. A quantile of a poor forecast is a precise-looking poor order.
- **A year-round mean in a seasonal reorder point.** The symptom is a healthy annual service level and stockouts every December. Split service by period.
- **Reporting cycle service and fill rate as one thing.** Here 79% and 95% describe the same weeks. Say which you mean.
- **Dropping lead-time variance.** It's a third of the buffer here, and 20 orders can underestimate it by half.

## Try it

1. Set TEX-03's salvage value to zero. What happens to the fractile, the order and the profit?

   <details><summary>Answer</summary>

   The fractile falls from 0.727 to 0.667 and the order from 1,207 to 1,182. Expected profit goes from £16,844 to £16,644, and keeping the old order would make £16,619, so reacting to the change is worth only £25. Losing salvage hurts much more than the order choice can recover.
   </details>

2. Make the reorder point follow the season: base level off season, and base level times 1.6 from one lead time before the season. What service do you get, and what does it cost?

   <details><summary>Answer</summary>

   Using the same safety stock, in-season cycle service goes from 80.0% to 94.7% and off-season stays at 95%. Holding cost goes from £9,972 to £10,346 a year, so about £374. Getting anywhere near that in-season service by raising z would cost over £2,000 and still miss. Note that the base here uses the true level, as a real business would use a seasonal forecast.
   </details>

## Interview checklist

| Question | Answer |
|---|---|
| What is the newsvendor critical fractile? | Underage over underage plus overage cost. Order that quantile of demand, not the mean |
| When is the mean the right order? | Only when underage and overage cost the same and the distribution is symmetric |
| What does the point forecast miss in a stock decision? | The error spread, which is what turns margins into an order |
| What is EOQ, and why not worry about precision? | √(2DS/H). The cost is flat near the bottom: 25% over costs 2.5% more here |
| What goes into safety stock? | z for the service level, and both demand and lead-time noise |
| What is cycle service against fill rate? | The share of cycles with no stockout against the share of units served |
| Why might a 95% buffer give 79%? | The reorder point used a year-round mean through a season where demand runs 60% higher |

## Next

[10b — Packers: queues, Little's law and a shift plan](10b-packers-queues-and-a-shift-plan.md): the stock decisions are made. Now roster the packers, starting from a queue that begins the day empty.
