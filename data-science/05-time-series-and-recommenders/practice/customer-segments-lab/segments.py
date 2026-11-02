"""Behavioural features, RFM rules, clustering, atlas's fallback rule, and the tests of a clustering."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN, KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

FEATURES = ["log_inflow", "log_invoices", "amount_spread", "growth", "q4_share", "log_burn", "top_share", "recency"]


def behaviour(tx, asof, n_customers=None, window_weeks=52):
    """One row per customer, using only transactions in the `window_weeks` before `asof`."""
    asof = pd.Timestamp(asof)
    recent = tx[(tx.date < asof) & (tx.date >= asof - pd.Timedelta(weeks=window_weeks))]
    money_in = recent[recent.amount > 0]
    invoices = money_in[money_in.kind == "invoice"]
    out = pd.DataFrame(index=pd.Index(range(n_customers or tx.customer_id.max() + 1), name="customer_id"))
    inflow = money_in.groupby("customer_id").amount.sum()
    outflow = -recent[recent.amount < 0].groupby("customer_id").amount.sum()
    out["log_inflow"] = np.log1p(inflow / (window_weeks / 4.345))
    out["log_invoices"] = np.log1p(invoices.groupby("customer_id").size() / (window_weeks / 4.345))
    out["amount_spread"] = np.log(invoices.amount).groupby(invoices.customer_id).std()
    half = asof - pd.Timedelta(weeks=window_weeks // 2)
    early = invoices[invoices.date < half].groupby("customer_id").amount.sum()
    late = invoices[invoices.date >= half].groupby("customer_id").amount.sum()
    out["growth"] = np.log1p(late) - np.log1p(early)
    q4 = invoices[invoices.date.dt.quarter == 4].groupby("customer_id").amount.sum()
    out["q4_share"] = q4 / invoices.groupby("customer_id").amount.sum()
    out["log_burn"] = np.log1p(outflow) - np.log1p(inflow)
    top = money_in.groupby("customer_id").amount.max()
    out["top_share"] = top / inflow
    last = invoices.groupby("customer_id").date.max()
    out["recency"] = np.log1p((asof - last).dt.days)
    return out[FEATURES].astype(float).fillna(0.0)          # no invoice in the window is a real, zero-filled state


def scale(features):
    return StandardScaler().fit_transform(features)


def rfm_segments(tx, asof, seed=42):
    """The rules from the chapter: R and F quintiles, ties broken at random, then named regions."""
    asof = pd.Timestamp(asof)
    inv = tx[(tx.date < asof) & (tx.kind == "invoice") & (tx.date >= asof - pd.Timedelta(weeks=52))]
    rfm = inv.groupby("customer_id").agg(last=("date", "max"), frequency=("amount", "size"), monetary=("amount", "mean"))
    rfm["recency"] = (asof - rfm.pop("last")).dt.days

    def quintile(s, ascending=True):
        shuffled = s.sample(frac=1, random_state=seed)
        return pd.qcut(shuffled.rank(method="first", ascending=ascending), 5, labels=False) + 1

    r, f = quintile(rfm.recency, ascending=False), quintile(rfm.frequency)
    rfm["segment"] = np.select(
        [(r >= 4) & (f >= 4), (r <= 2) & (f >= 4), (r >= 4) & (f <= 2), (r <= 2) & (f <= 2)],
        ["Champions", "At risk", "New", "Hibernating"], default="Middle")
    return rfm


def kmeans_scan(X, k_range=(2, 8), seed=42):
    """Best k by silhouette. Returns (labels, k, silhouette, every silhouette tried)."""
    tried = {}
    for k in range(k_range[0], k_range[1] + 1):
        labels = KMeans(k, n_init=10, random_state=seed).fit_predict(X)
        tried[k] = silhouette_score(X, labels)
    k = max(tried, key=tried.get)
    return KMeans(k, n_init=10, random_state=seed).fit_predict(X), k, tried[k], tried


def hdbscan_labels(X, min_cluster_size=15):
    return HDBSCAN(min_cluster_size=min_cluster_size, copy=True).fit_predict(X)


def clustered_silhouette(X, labels):
    """Silhouette on non-noise points, as atlas computes it. Undefined under two clusters, so -1."""
    keep = labels != -1
    if keep.sum() < 3 or len(set(labels[keep])) < 2:
        return -1.0
    return float(silhouette_score(X[keep], labels[keep]))


def select_best(X, min_cluster_size=15, min_silhouette=0.25, max_noise=0.5, seed=42):
    """Atlas's `select_best` rule, rewritten here: HDBSCAN unless silhouette < 0.25 or noise > 50%, then k-means."""
    labels = hdbscan_labels(X, min_cluster_size)
    sil, noise = clustered_silhouette(X, labels), float((labels == -1).mean())
    if sil >= min_silhouette and noise <= max_noise:
        return labels, "hdbscan", sil, noise
    labels, _, sil, _ = kmeans_scan(X, seed=seed)
    return labels, "kmeans", sil, 0.0


def subsample_stability(X, cluster, reps=20, frac=0.8, seed=42):
    """Mean ARI between a clustering of all customers and clusterings of random 80% subsamples.

    Noise counts as one more label, so a method cannot score well by discarding hard points.
    """
    rng = np.random.default_rng(seed)
    full = cluster(X)
    scores = []
    for _ in range(reps):
        idx = rng.choice(len(X), int(frac * len(X)), replace=False)
        scores.append(adjusted_rand_score(full[idx], cluster(X[idx])))
    return float(np.mean(scores)), float(np.std(scores))
