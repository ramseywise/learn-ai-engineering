# Customer segments lab

Sort synthetic business customers into cohorts from their transactions, test whether the cohorts deserve trust, then forecast each cohort's cash flow and compare that with one global model. It backs two case sections: [Segmenting B2B customers by behaviour](../../../../data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm.md#case-segmenting-b2b-customers-by-behaviour) and [Forecasting each segment's cash flow](../../notes/01-time-series-ml.md#case-forecasting-each-segments-cash-flow).

The idea comes from [atlas](https://github.com/ramseywise/atlas), a public project. The code is written fresh and needs nothing from atlas, and the agent and LLM layers of atlas aren't part of it. Where this lab quotes atlas's thresholds (silhouette 0.25, noise 50%, MASE 1, SMAPE 15, direction 55%), those are its design choices, not evidence.

Run everything from the pillar folder, `data-science/05-time-series-and-recommenders/`.

| File | What it does | Runtime on a laptop CPU | Packages |
|---|---|---|---|
| [`lab.py`](lab.py) | Every table and both figures in the two case sections. `--no-figures` leaves the course's images alone, and `--seeds 5` repeats only the forecasting comparison on fresh worlds | About 70 s on a 12-core Mac with other work running, 240 s under heavy load. `--seeds 5` took about 3 minutes | `numpy pandas scikit-learn umap-learn statsforecast matplotlib` |
| [`generator.py`](generator.py) | Synthetic transactions in three worlds: planted, blurred and control | Seconds | `numpy pandas` |
| [`segments.py`](segments.py) | Behavioural features, RFM rules, k-means, HDBSCAN, atlas's fallback rule, stability | | `numpy pandas scikit-learn` |
| [`forecast.py`](forecast.py) | Walk-forward folds, MASE, SMAPE, direction, global and per-segment models, and MSTL on totals | | `numpy pandas scikit-learn`, plus `statsforecast` for MSTL |
| [`output.txt`](output.txt) | What `lab.py` printed, to compare yours against | | |
| [`output_seeds.txt`](output_seeds.txt) | What `lab.py --seeds 5` printed | | |

```bash
uv run --with numpy==2.5.4 --with pandas==3.1.0 --with scikit-learn==1.9.1 --with umap-learn==0.5.12 --with statsforecast==2.0.1 --with matplotlib==3.11.2 python practice/customer-segments-lab/lab.py
uv run --with numpy==2.5.4 --with pandas==3.1.0 --with scikit-learn==1.9.1 --with umap-learn==0.5.12 --with statsforecast==2.0.1 --with matplotlib==3.11.2 python practice/customer-segments-lab/lab.py --seeds 5
```

The versions are pinned because UMAP's layout and HDBSCAN's labels can move between releases, and the case sections quote exact numbers. `lab.py` sets `OMP_NUM_THREADS=4` unless you have set it, because more threads don't help these small fits.

## Data

**All of it is synthetic. Nothing here measures how these methods do on real customers.** `generator.py` simulates 400 businesses from 2 January 2023 for 156 weeks, with seed 42.

- **Planted.** Five tight archetypes: growing SaaS, small services firms, manufacturers, seasonal retailers and early-stage firms living on funding. A clusterer finding these is a weak test, since the generator put them there.
- **Blurred.** The same five with 2.5 times the spread within each.
- **Control.** Every customer drawn from one Gaussian with the planted population's mean and covariance, then simulated by the same code. There is nothing to find, so any cluster here is a false alarm.

Two limits to keep in mind. No customer churns in this generator, which takes away most of what recency does for RFM and so favours clusters over RFM. And the eight issue dates are one short stretch of one simulated history, which is why `--seeds 5` exists.

## Ideas beyond the exercises

- Add churn to the generator, and see whether RFM's score against the archetypes recovers.
- Run the fallback rule with the silhouette computed over all customers, counting noise as a cluster, and see whether it still prefers HDBSCAN on the planted world.
- Compare HDBSCAN's `leaf` cluster selection with the default `eom` on the blurred world.
- Forecast with a hierarchical reconciliation, so that the customer forecasts add up to the segment forecast.
- Point the features at a real transaction table, keep the control by permuting each feature independently, and see which checks survive.
