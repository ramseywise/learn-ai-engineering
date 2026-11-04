# Practice: applied analyses

Run everything from this folder, `data-analytics/06-applied-analyses/practice/`. Each lab answers the question its chapter opens with and needs no key. The data is generated, apart from the South German Credit file in `data/` that chapter 2 reads.

| File | What it does | Runtime on a laptop CPU | Packages |
|---|---|---|---|
| [`ch01_forecasting.py`](ch01_forecasting.py) | How many units to staff the warehouse for over the next 13 weeks | 2 to 3 min | numpy, pandas, matplotlib, statsmodels, prophet |
| [`ch02_credit_scoring.py`](ch02_credit_scoring.py) | Which credit applications to approve, and what they cost in capital | about 2 min | numpy, pandas, matplotlib, scikit-learn, scipy |
| [`ch03_cohort_retention.py`](ch03_cohort_retention.py) | Whether new customers are worse, or everyone is | about 1 min | numpy, pandas, matplotlib, scipy |
| [`ch04_funnel.py`](ch04_funnel.py) | Whether the new mobile checkout page is fine when overall conversion is flat | about 1 min | numpy, pandas, matplotlib, scipy |
| [`ch05_segmentation_rfm.py`](ch05_segmentation_rfm.py) | Which customers get the one retention campaign | about 1 min | numpy, pandas, matplotlib, scikit-learn, scipy |
| [`ch06_sql_analytics.py`](ch06_sql_analytics.py) | Whether revenue growth comes from new or returning customers, in SQL | under 1 min | numpy, pandas, matplotlib, duckdb |
| [`ch07_survival.py`](ch07_survival.py) | When a subscriber leaves, and whether the welcome call delays it | about 2 min | numpy, pandas, matplotlib, scipy, statsmodels, lifelines |
| [`ch08_states_sequences.py`](ch08_states_sequences.py) | Which journeys lead to a second order, and what a customer in each state is worth | 1 to 2 min | numpy, pandas, matplotlib, scipy, scikit-learn, sequenzo |
| [`ch09_marketing_measurement.py`](ch09_marketing_measurement.py) | Where next quarter's budget goes, and what a new customer is worth | about 5 min | numpy, pandas, matplotlib, scipy, pymc-marketing, nutpie |
| [`ch10_operations_supply_chain.py`](ch10_operations_supply_chain.py) | How much of each product to hold, and how many packers on a Monday | about 1 min | numpy, pandas, matplotlib, scipy, pulp |
| [`ch11_metric_trees.py`](ch11_metric_trees.py) | Which number to run on, what feeds it, and what would catch it being gamed | under 1 min | numpy, pandas |
| [`ch12_surveys.py`](ch12_surveys.py) | What a survey's number is worth: allocation, clusters, nonresponse, weighting and margins | under 1 min | numpy, pandas, scipy |

Runtimes come from one smoke run with packages already cached and three labs at a time. The first run of a lab also downloads its packages. `chartstyle.py` and `retail.py` are helpers the labs import.

```bash
uv run ch03_cohort_retention.py   # one lab
```

To check that every lab still runs, from the repo root, in a temporary copy with no chart windows:

```bash
make da06-smoke                    # 600 s limit per lab; not part of make test
make da06-smoke SMOKE_TIMEOUT=900 SMOKE_ARGS=--offline
```
