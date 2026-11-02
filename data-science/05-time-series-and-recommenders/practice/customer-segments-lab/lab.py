#!/usr/bin/env python3
"""Segment synthetic B2B customers by behaviour, then forecast each segment's cash flow.

Every number in the two case sections of the course comes from this script. Run it from the pillar folder:

    uv run --with numpy --with pandas --with scikit-learn --with umap-learn --with statsforecast --with matplotlib \
        python practice/customer-segments-lab/lab.py

`--seeds 5` repeats the forecasting comparison on five fresh worlds. `--no-figures` leaves the course's images alone.
The data is synthetic. Nothing here says anything about how these methods do on real customers.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "4")     # more threads do not help these small fits; pin it so reruns match

import argparse
import sys
import time
from importlib.metadata import version
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pandas as pd
import umap
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, roc_auc_score
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import NearestNeighbors
from sklearn.tree import DecisionTreeClassifier

from forecast import (FIRST_ISSUE, ORIGINS, customer_score, global_forecast, local_total_forecast, long_table, mase,
                      per_segment_forecast, seasonal_naive, segment_scores, smape, directional, weekly_panel)
from generator import SEED, START, make_world
from segments import (behaviour, clustered_silhouette, hdbscan_labels, kmeans_scan, rfm_segments, scale, select_best,
                      subsample_stability)

N = 400
MIN_CLUSTER = 10           # 2.5% of 400 customers. The tables below show what other values do.
REPO = Path(__file__).resolve().parents[4]
FIG_SEGMENTS = REPO / "data-analytics/sources/images/applied-segments-umap-control.png"
FIG_FORECAST = REPO / "data-science/sources/images/ts-segment-forecast-mase.png"

# Colours copied from data-analytics/06-applied-analyses/practice/chartstyle.py. That palette stops at four, and purple is the fifth.
BLUE, ORANGE, AQUA, YELLOW, PURPLE = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#4a3aa7"
INK, SECONDARY, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"


def heading(text):
    print(f"\n=== {text} ===", flush=True)


def n_clusters(labels):
    return len(set(labels)) - (1 if -1 in labels else 0)


def recovery(truth, labels):
    """ARI against the planted archetypes. A control world has none, so there is nothing to recover."""
    return adjusted_rand_score(truth, labels) if truth.nunique() > 1 else float("nan")


def part_data(worlds):
    heading("1. The data")
    print(f"seed {SEED}, {N} customers, {START.date()} for 156 weeks. Segments and features use data before {FIRST_ISSUE.date()}.")
    for name, (tx, truth) in worlds.items():
        counts = truth.value_counts().to_dict()
        print(f"{name:8s} {len(tx):7,d} transactions  {counts}")
    tx = worlds["planted"][0]
    print(tx.head(3).round(2).to_string(index=False))


def part_rfm(worlds):
    heading("2. RFM rules against the planted archetypes")
    tx, truth = worlds["planted"]
    rfm = rfm_segments(tx, FIRST_ISSUE)
    labels = rfm.segment.reindex(range(N)).fillna("No invoices")
    print(pd.crosstab(truth, labels).to_string())
    print(f"ARI against archetypes {adjusted_rand_score(truth, labels):.3f}; Spearman(recency, frequency) {spearmanr(rfm.recency, rfm.frequency)[0]:.3f}")
    print("No customer churns in this generator, so recency carries only invoice rate. That is a limit of the data, and it favours clusters.")
    return labels.to_numpy()


def part_clusters(worlds):
    heading("3. Clusters on eight behavioural features")
    print(f"{'world':8s} {'method':22s} {'k':>3s} {'noise':>6s} {'silhouette':>10s} {'ARI truth':>9s}")
    best = {}
    for name, (tx, truth) in worlds.items():
        X = scale(behaviour(tx, FIRST_ISSUE, N))
        labels, k, sil, _ = kmeans_scan(X)
        print(f"{name:8s} {'k-means, best of 2-8':22s} {k:3d} {0:6.1%} {sil:10.3f} {recovery(truth, labels):9.3f}")
        for m in (5, 10, 15):
            labels = hdbscan_labels(X, m)
            sil = clustered_silhouette(X, labels)
            print(f"{name:8s} {f'HDBSCAN m={m}':22s} {n_clusters(labels):3d} {(labels == -1).mean():6.1%} {sil:10.3f} {recovery(truth, labels):9.3f}")
        labels, algo, sil, noise = select_best(X, MIN_CLUSTER)
        print(f"{name:8s} {'atlas rule picks ' + algo:22s} {n_clusters(labels):3d} {noise:6.1%} {sil:10.3f} {recovery(truth, labels):9.3f}")
        best[name] = labels
    tx, truth = worlds["planted"]
    print("\nPlanted world, the rule's choice against the archetypes:")
    print(pd.crosstab(truth, pd.Series(best["planted"], name="cluster")).to_string())
    print("\nControl world, what the rule's clusters look like (mean feature, before scaling):")
    features = behaviour(worlds["control"][0], FIRST_ISSUE, N)
    print(features.assign(cluster=best["control"]).groupby("cluster")[["top_share", "log_burn", "log_inflow"]].mean().round(3)
          .assign(customers=pd.Series(best["control"]).value_counts()).to_string())
    return best


def jaccard_distance_knn(X, U, k=30):
    a = NearestNeighbors(n_neighbors=k + 1).fit(X).kneighbors(X, return_distance=False)[:, 1:]
    b = NearestNeighbors(n_neighbors=k + 1).fit(U).kneighbors(U, return_distance=False)[:, 1:]
    return float(np.mean([1 - len(set(p) & set(q)) / len(set(p) | set(q)) for p, q in zip(a, b)]))


def part_umap(worlds):
    heading("4. UMAP: what it does to the same customers")
    print(f"{'world':8s} {'UMAP settings':26s} {'m':>3s} {'k':>3s} {'noise':>6s} {'sil on map':>10s} {'sil raw':>8s} {'ARI truth':>9s} {'dist rho':>8s} {'30-NN Jaccard dist':>18s}")
    maps = {}
    for name in ("planted", "control"):
        tx, truth = worlds[name]
        X = scale(behaviour(tx, FIRST_ISSUE, N))
        for seed in (42, 0, 1):
            for metric in ("cosine", "euclidean"):
                U = umap.UMAP(n_components=2, n_neighbors=15, metric=metric, random_state=seed).fit_transform(X)
                rho, jac = spearmanr(pdist(X), pdist(U))[0], jaccard_distance_knn(X, U)
                if (seed, metric) == (42, "euclidean"):
                    maps[name] = U
                for m in (3, MIN_CLUSTER):
                    labels = hdbscan_labels(U, m)
                    print(f"{name:8s} {f'{metric}, seed {seed}':26s} {m:3d} {n_clusters(labels):3d} {(labels == -1).mean():6.1%} "
                          f"{clustered_silhouette(U, labels):10.3f} {clustered_silhouette(X, labels):8.3f} {recovery(truth, labels):9.3f} {rho:8.3f} {jac:18.3f}")
    return maps


def part_stability(worlds):
    heading("5. Stability: does the clustering come back?")
    print("Subsample: ARI between all customers and random 80% subsamples, 20 draws. Temporal: ARI between two non-overlapping years.")
    print(f"{'world':8s} {'method':14s} {'subsample':>9s} {'sd':>6s} {'temporal':>8s}")
    methods = {"k-means k=5": lambda A: KMeans(5, n_init=10, random_state=SEED).fit_predict(A),
               "k-means k=2": lambda A: KMeans(2, n_init=10, random_state=SEED).fit_predict(A),
               f"HDBSCAN m={MIN_CLUSTER}": lambda A: hdbscan_labels(A, MIN_CLUSTER)}
    for name in ("planted", "control"):
        tx, _ = worlds[name]
        X = scale(behaviour(tx, FIRST_ISSUE, N))
        earlier = scale(behaviour(tx, FIRST_ISSUE - pd.Timedelta(weeks=52), N))
        for label, cluster in methods.items():
            mean, sd = subsample_stability(X, cluster)
            print(f"{name:8s} {label:14s} {mean:9.3f} {sd:6.3f} {adjusted_rand_score(cluster(X), cluster(earlier)):8.3f}")


def part_action(worlds, rfm_labels, best):
    heading("6. Can anyone act on it? Predicting who burns cash next quarter")
    print("Outcome: net cash below zero over the 13 weeks after the freeze. Score: each group's burn rate in the 13 weeks before the")
    print("freeze, used to rank customers; AUC on the outcome. Tree: 5-fold accuracy of a depth-3 tree reproducing the group from features.")
    print(f"{'world':8s} {'grouping':22s} {'groups':>6s} {'AUC':>6s} {'tree':>6s}")
    for name in ("planted", "control"):
        tx, _ = worlds[name]
        F = behaviour(tx, FIRST_ISSUE, N)
        X = scale(F)
        y = weekly_panel(tx, N)
        issue = (FIRST_ISSUE - START).days // 7
        future = (y.iloc[issue:issue + 13].sum() < 0).astype(int).to_numpy()
        past = (y.iloc[issue - 13:issue].sum() < 0).astype(int).to_numpy()
        rfm = rfm_labels if name == "planted" else rfm_segments(tx, FIRST_ISSUE).segment.reindex(range(N)).fillna("No invoices").to_numpy()
        groupings = {f"atlas rule (m={MIN_CLUSTER})": best[name],
                     "k-means k=5": KMeans(5, n_init=10, random_state=SEED).fit_predict(X),
                     "RFM rules": rfm,
                     "one rule: costs > income": (F.log_burn > 0).to_numpy().astype(int),
                     "random, same sizes": np.random.default_rng(SEED).permutation(best[name])}
        print(f"{name:8s} burn rate next quarter {future.mean():.3f}")
        for label, groups in groupings.items():
            rate = pd.Series(past).groupby(groups).transform("mean").to_numpy()
            auc = roc_auc_score(future, rate)
            tree = "" if label.startswith("random") else f"{cross_val_score(DecisionTreeClassifier(max_depth=3, random_state=0), F, groups, cv=5).mean():6.3f}"
            print(f"{name:8s} {label:24s} {len(set(groups)):4d} {auc:6.3f} {tree:>6s}")
        if name == "planted":
            print("Burn rate next quarter, by cluster:", pd.Series(future).groupby(best[name]).mean().round(3).to_dict())


def score_local(y, labels):
    """Segment totals only: statsforecast has no customer-level forecast here, so the customer column stays blank."""
    fc = local_total_forecast(y, labels)
    labels = np.asarray(labels)
    rows = []
    for o in ORIGINS:
        weeks = list(range(o, o + 4))
        for s in np.unique(labels):
            total = y[y.columns[labels == s]].sum(axis=1)
            pred = fc[(fc.unique_id == str(s)) & fc.week.isin(weeks)].sort_values("week").pred.to_numpy()
            actual = total.loc[weeks].to_numpy()
            rows.append(dict(fold=o, segment=s, mase=mase(actual, pred, total.loc[: o - 1].to_numpy()),
                             smape=smape(actual, pred), direction=directional(actual, pred)))
    return pd.DataFrame(rows)


def run_models(y, labels, truth, seed=SEED, slim=False):
    """Every forecaster on the same walk-forward folds, as a dict of name -> wide predictions (or a score table)."""
    table = long_table(y)
    preds = {"naive, same week last year": seasonal_naive(y, 52),
             "naive, 4 weeks ago": seasonal_naive(y, 4),
             "global GBM": global_forecast(table),
             "global + segment feature": global_forecast(table, labels),
             "one GBM per segment": per_segment_forecast(table, labels),
             "one GBM per random group": per_segment_forecast(table, np.random.default_rng(seed).permutation(labels))}
    if truth.nunique() > 1 and not slim:
        preds["one GBM per true archetype"] = per_segment_forecast(table, truth.astype("category").cat.codes.to_numpy())
    return preds


def part_forecast(worlds, best):
    heading("7. Walk-forward forecasting: eight issue dates, four weeks ahead")
    print(f"First issue {FIRST_ISSUE.date()}, segments frozen there. MASE scale: the same-week-last-year naive, on data before each issue date.")
    print("Customer: mean of each customer's MASE. Segment total: MASE, SMAPE and direction on the summed forecast, averaged over segments and folds.")
    results, tables = {}, {}
    for name in ("planted", "control"):
        tx, truth = worlds[name]
        y = weekly_panel(tx, N)
        labels = best[name]
        preds = run_models(y, labels, truth)
        scores = {model: segment_scores(y, pred, labels) for model, pred in preds.items()}
        customers = {model: customer_score(y, pred) for model, pred in preds.items()}
        try:
            scores["local MSTL on each total"] = score_local(y, labels)
            customers["local MSTL on each total"] = float("nan")
        except ImportError:
            print("statsforecast is not installed, so the local row is skipped")
        by_fold = {model: s.groupby("fold").mase.mean() for model, s in scores.items()}
        print(f"\n{name}: sizes {pd.Series(labels).value_counts().sort_index().to_dict()}")
        print(f"{'model':28s} {'customer':>8s} {'segment':>8s} {'SMAPE':>6s} {'direct':>6s} {'folds < naive':>13s} {'folds < global':>14s}")
        rows = {}
        for model, s in scores.items():
            beats_naive = int((by_fold[model] < by_fold["naive, same week last year"]).sum())
            beats_global = int((by_fold[model] < by_fold["global GBM"]).sum())
            print(f"{model:28s} {customers[model]:8.3f} {s.mase.mean():8.3f} {s.smape.mean():6.1f} {s.direction.mean():6.1f} {beats_naive:9d}/8 {beats_global:10d}/8")
            rows[model] = (customers[model], s.mase.mean())
        results[name] = rows
        tables[name] = scores
    print("\nPlanted world, MASE on each segment's total (-1 is HDBSCAN's noise group):")
    labels = best["planted"]
    keep = ["naive, same week last year", "global GBM", "global + segment feature", "one GBM per segment"]
    print(pd.DataFrame({m: tables["planted"][m].groupby("segment").mase.mean() for m in keep}).assign(customers=pd.Series(labels).value_counts()).round(3).to_string())
    return results


def part_seeds(n_seeds):
    heading(f"8. The same comparison on {n_seeds} fresh worlds")
    print("Segment total and customer MASE from each world; a different seed draws different customers and different clusters.")
    print(f"{'world':8s} {'seed':>4s} {'algo':8s} {'k':>2s} {'noise':>6s} {'global':>7s} {'+feature':>8s} {'per seg':>7s} {'random':>7s}   {'customer: global':>16s} {'+feature':>8s} {'per seg':>7s} {'random':>7s}")
    rows = []
    for name in ("planted", "control"):
        for seed in range(100, 100 + n_seeds):
            tx, truth = make_world(name, N, seed)
            X = scale(behaviour(tx, FIRST_ISSUE, N))
            labels, algo, _, noise = select_best(X, MIN_CLUSTER)
            y = weekly_panel(tx, N)
            preds = run_models(y, labels, truth, seed, slim=True)
            seg = {m: segment_scores(y, p, labels).mase.mean() for m, p in preds.items()}
            cus = {m: customer_score(y, p) for m, p in preds.items()}
            g, f, s, r = "global GBM", "global + segment feature", "one GBM per segment", "one GBM per random group"
            print(f"{name:8s} {seed:4d} {algo:8s} {n_clusters(labels):2d} {noise:6.1%} {seg[g]:7.3f} {seg[f]:8.3f} {seg[s]:7.3f} {seg[r]:7.3f}   {cus[g]:16.3f} {cus[f]:8.3f} {cus[s]:7.3f} {cus[r]:7.3f}", flush=True)
            rows.append(dict(world=name, seg_global=seg[g], seg_feature=seg[f], seg_per=seg[s], seg_random=seg[r],
                             cus_global=cus[g], cus_feature=cus[f], cus_per=cus[s], cus_random=cus[r]))
    print(pd.DataFrame(rows).groupby("world").mean().round(3).T.to_string())


def figure_segments(worlds, maps):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "text.color": INK, "savefig.facecolor": SURFACE, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE})
    truth = worlds["planted"][1]
    fig, (left, right) = plt.subplots(1, 2, figsize=(8, 4.5), dpi=150)
    for colour, archetype in zip((BLUE, ORANGE, AQUA, YELLOW, PURPLE), sorted(truth.unique())):
        pts = maps["planted"][(truth == archetype).to_numpy()]
        left.scatter(pts[:, 0], pts[:, 1], s=16, color=colour, edgecolor=SURFACE, linewidth=0.4, label=archetype.replace("_", " "))
    left.legend(frameon=False, fontsize=8, loc="best", labelcolor=SECONDARY)
    left.set_title("Planted: five archetypes", fontsize=10, color=INK, loc="left")
    pts = maps["control"]
    right.scatter(pts[:, 0], pts[:, 1], s=16, color=BLUE, edgecolor=SURFACE, linewidth=0.4)
    right.set_title("Control: one Gaussian, no groups were planted", fontsize=10, color=INK, loc="left")
    for ax in (left, right):
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_xlabel("UMAP 1", color=SECONDARY, fontsize=9); ax.set_ylabel("UMAP 2", color=SECONDARY, fontsize=9)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG_SEGMENTS)
    plt.close(fig)


def figure_forecast(results):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "text.color": INK, "savefig.facecolor": SURFACE, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE})
    order = ["naive, same week last year", "naive, 4 weeks ago", "local MSTL on each total", "global GBM", "global + segment feature",
             "one GBM per segment", "one GBM per random group", "one GBM per true archetype"]
    fig, axes = plt.subplots(1, 2, figsize=(8, 4.5), dpi=150, sharex=True, sharey=True)
    for ax, name in zip(axes, ("planted", "control")):
        ys = list(range(len(order)))[::-1]
        for pos, model in zip(ys, order):
            if model in results[name]:
                customer, segment = results[name][model]
                if not np.isnan(customer):
                    ax.plot([segment, customer], [pos, pos], color=GRID, lw=1.5, zorder=1, solid_capstyle="round")
                    ax.scatter(customer, pos, s=46, color=ORANGE, edgecolor=SURFACE, linewidth=1, zorder=2, label="Single customers" if pos == ys[0] else None)
                ax.scatter(segment, pos, s=46, color=BLUE, edgecolor=SURFACE, linewidth=1, zorder=3, label="Segment totals" if pos == ys[0] else None)
        ax.axvline(1.0, color=MUTED, lw=1, ls="--", zorder=0)
        ax.set_title(name.capitalize() + (" world" if name == "planted" else " world: nothing planted"), fontsize=10, loc="left", color=INK)
        ax.set_yticks(ys); ax.set_yticklabels(order, color=SECONDARY, fontsize=9)
        ax.set_xlabel("MASE (lower is better; dashed line is 1)", color=SECONDARY, fontsize=9)
        ax.tick_params(colors=SECONDARY, length=0)
        ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
    axes[0].legend(frameon=False, fontsize=8, loc="lower right", labelcolor=SECONDARY)
    fig.tight_layout()
    fig.savefig(FIG_FORECAST)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=0, help="only repeat the forecasting comparison on this many fresh worlds")
    parser.add_argument("--no-figures", action="store_true")
    args = parser.parse_args()
    print("versions:", ", ".join(f"{p} {version(p)}" for p in ("numpy", "pandas", "scikit-learn", "umap-learn", "statsforecast", "matplotlib")))
    if args.seeds:
        part_seeds(args.seeds)
        return
    worlds = {name: make_world(name, N, SEED) for name in ("planted", "blurred", "control")}
    part_data(worlds)
    rfm_labels = part_rfm(worlds)
    best = part_clusters(worlds)
    maps = part_umap(worlds)
    part_stability(worlds)
    part_action(worlds, rfm_labels, best)
    results = part_forecast(worlds, best)
    if not args.no_figures:
        figure_segments(worlds, maps)
        figure_forecast(results)
        print(f"\nfigures: {FIG_SEGMENTS.relative_to(REPO)}, {FIG_FORECAST.relative_to(REPO)}")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\nruntime {time.time() - start:.0f} s")
