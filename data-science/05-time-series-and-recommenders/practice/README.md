# Practice: time series and recommenders

Run everything from the pillar folder, `data-science/05-time-series-and-recommenders/`.

| File | What it does | Runtime on a laptop CPU | Packages |
|---|---|---|---|
| [`run_note.py`](run_note.py) | Runs a chapter's Python blocks in order and fails on the first error | Chapter 1 several minutes, since its neural backtest alone takes about 3; chapters 2 and 3 a minute or two | As below |
| [`01_forecast_lab.py`](01_forecast_lab.py) | Backtest harness and the exercises for [Time series ML](../notes/01-time-series-ml.md) | A few minutes | `scikit-learn pandas` |
| [`02_cf_lab.py`](02_cf_lab.py) | Exercises for [Collaborative filtering](../notes/02-collaborative-filtering-and-matrix-factorisation.md): split, positives, segments | A minute or two | `numpy pandas scipy` |
| [`03_two_tower_lab.py`](03_two_tower_lab.py) | Exercises for [Two towers and evaluation](../notes/03-two-tower-and-evaluation.md): batch size, sampled metrics, IPS | A few minutes | `numpy pandas scipy torch` |
| [`customer-segments-lab/`](customer-segments-lab/README.md) | Synthetic business customers: sort them into cohorts, test whether to trust the cohorts, and forecast each one's cash flow, for [the case in Time series ML](../notes/01-time-series-ml.md#case-forecasting-each-segments-cash-flow) | One to four minutes | See its README, which pins versions |
| [`04_matching_lab.py`](04_matching_lab.py) | Every number and figure in [Entity matching and learning to rank](../notes/04-entity-matching-and-learning-to-rank.md): blocking, Fellegi-Sunter weights, nine rankers over five ledgers, match errors. Run from `practice/` with `uv run 04_matching_lab.py`, as its packages are declared in the file | About four minutes | `numpy pandas scipy scikit-learn lightgbm matplotlib` |
| [`04_matching_tryit.py`](04_matching_tryit.py) | The measured answers to that chapter's Try it. `uv run 04_matching_tryit.py`, from `practice/` | A few minutes | `numpy pandas scikit-learn lightgbm` |
| [`04_part_pairs_lab.py`](04_part_pairs_lab.py) | The numbers in that chapter's sections on splitting pairs and on similar versus interchangeable, including its fourth Try it. `uv run 04_part_pairs_lab.py`, from `practice/` | About a minute | `numpy pandas scipy scikit-learn lightgbm` |
| [`parts_catalogue.py`](parts_catalogue.py) | Generated parts catalogue with known records, parts and specs, candidate pairs and a rule-based extractor, imported by that lab | | |
| [`matching.py`](matching.py) | Ledger generator, blocking, pair features and ranking metrics, imported by those two | | |
| [`movielens.py`](movielens.py) | Shared MovieLens loader, split, metric and EASE, imported by the two recommender labs | | |

```bash
uv run --with scikit-learn --with pandas --with torch python practice/run_note.py notes/01-time-series-ml.md
uv run --with numpy --with pandas --with scipy python practice/run_note.py notes/02-collaborative-filtering-and-matrix-factorisation.md
uv run --with numpy --with pandas --with scipy --with torch python practice/run_note.py notes/03-two-tower-and-evaluation.md
uv run --with numpy --with pandas --with scikit-learn python practice/run_note.py notes/04-entity-matching-and-learning-to-rank.md

uv run --with scikit-learn --with pandas python practice/01_forecast_lab.py
uv run --with numpy --with pandas --with scipy python practice/02_cf_lab.py
uv run --with numpy --with pandas --with scipy --with torch python practice/03_two_tower_lab.py
```

## Data

The ledger and the parts catalogue in chapter 4 are generated from a seed, with no download. Neither of the two datasets below lives in the repo. The code downloads each to `~/.cache/learn-ai-engineering/` on first use.

- **Bike Sharing** ([UCI](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset), CC BY 4.0, 280 KB). Cite Fanaee-T and Gama, 2014.
- **MovieLens 100K** ([GroupLens](https://grouplens.org/datasets/movielens/100k/), 4.9 MB). Its licence allows research use, forbids redistribution and commercial use, and requires acknowledgement, which is why it is downloaded and not vendored. Cite Harper and Konstan, 2015.

## Ideas beyond the exercises

- Forecast `casual` and `registered` rentals as two series with one global model, and see whether cross-learning helps.
- Replace the genre features in the tower with sentence embeddings of each film's title and plot, as in [LLM embeddings as features](../../03-nlp/notes/07-llm-embeddings-as-features.md).
- Add a FAISS or HNSW index over the item vectors and measure the recall it costs against brute force.
