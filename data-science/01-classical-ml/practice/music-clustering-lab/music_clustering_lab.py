#!/usr/bin/env python3
"""Clustering a music library: scaling, k-means vs GMM, choosing k, stability, naming, a reranker.

The data is listen-wiseer's public corpus_features.parquet, fetched at run time from a pinned
commit, checked against a SHA-256 and cached under the gitignored .cache/. Only the columns in
SAFE_COLUMNS are ever read, so track names, Spotify IDs, release dates and raw genre strings
never enter memory. Everything printed is an aggregate: no track row is shown or written.

    uv run --python 3.12 --with scikit-learn --with lightgbm --with pandas --with pyarrow \
        --with matplotlib --with scipy python music_clustering_lab.py
"""
from __future__ import annotations

import hashlib
import itertools
import json
import platform
import sys
import time
import urllib.request
from pathlib import Path

import lightgbm
import numpy as np
import pandas as pd
import sklearn
from joblib import Parallel, delayed
from lightgbm import LGBMClassifier
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (
    adjusted_rand_score,
    average_precision_score,
    normalized_mutual_info_score,
    roc_auc_score,
    silhouette_score,
)
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler

COMMIT = "2f03e7dd906cc2362ce602e1fc44849579c2b732"
URL = f"https://raw.githubusercontent.com/ramseywise/listen-wiseer/{COMMIT}/data/cache/corpus_features.parquet"
SHA256 = "8142f6694780c2a70a9aecb7255528f5a9ac41ce8bc292db111925fb7ff94bd3"
HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache" / "corpus_features.parquet"
FIGURE = HERE.parents[2] / "sources" / "images" / "wise-music-clustering-lab-fig1.png"

AUDIO = ["danceability", "energy", "loudness", "speechiness", "acousticness",
         "instrumentalness", "liveness", "valence", "tempo"]
PP = [f"pp_{c}" for c in AUDIO]        # mean audio of the track's playlists
T2V = [f"t2v_{i}" for i in range(64)]  # word2vec over playlist co-occurrence
ENOA = ["top", "left", "artist_enoa_top", "artist_enoa_left"]
PROJECT_CONT = AUDIO + ["top", "left", "fave_score", "n_playlists",
                        "year_normalized", "duration_ms_normalized"]
DECADES = ["1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]
GEN4 = ["acoustic", "dance", "electronic", "instrumental"]
GEN8 = ["acoustic", "ambient", "dance", "electronica", "house", "jazz", "r&b", "rock"]

# An allow-list, not a drop-list: id, track_name, release_date, first_genre and color stay on disk.
SAFE_COLUMNS = AUDIO + PP + T2V + ENOA + [
    "duration_ms", "duration_ms_normalized", "year_normalized", "decade", "key_mode", "popularity",
    "gen_4", "gen_8", "fave_score", "n_playlists", "playlist_diversity", "features_source",
]
KS = list(range(2, 15))
SEEDS = list(range(10))
PROJECT_K = 8
STABLE_JACCARD = 0.75  # Hennig (2007): below 0.6 a cluster is not a real pattern, above 0.75 it is stable


def load_library(cache: Path = CACHE) -> pd.DataFrame:
    """Fetch the pinned parquet once, verify it, and read only the safe columns."""
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        tmp = cache.with_suffix(".tmp")
        with urllib.request.urlopen(URL, timeout=60) as response:
            tmp.write_bytes(response.read())
        tmp.rename(cache)
    digest = hashlib.sha256(cache.read_bytes()).hexdigest()
    if digest != SHA256:
        cache.unlink()
        raise RuntimeError(f"{cache.name}: sha256 {digest} does not match the pinned {SHA256}; deleted")
    return pd.read_parquet(cache, columns=SAFE_COLUMNS)


def one_hot(series: pd.Series, categories: list[str]) -> np.ndarray:
    """One column per category; values outside the list (1920s, 1940s) and nulls get all zeros."""
    return pd.get_dummies(pd.Categorical(series.where(series.isin(categories)), categories=categories)).to_numpy(float)


def audio_matrix(df: pd.DataFrame) -> np.ndarray:
    """The nine audio features, standardised."""
    return StandardScaler().fit_transform(df[AUDIO])


def project_matrix(df: pd.DataFrame) -> np.ndarray:
    """clustering.py's 47 columns: 15 continuous + 24 key_mode + 8 decade, min-max scaled."""
    parts = [df[PROJECT_CONT].to_numpy(float),
             pd.get_dummies(df["key_mode"]).to_numpy(float),
             one_hot(df["decade"], DECADES)]
    return MinMaxScaler().fit_transform(np.hstack(parts))


def proxy_matrix(df: pd.DataFrame) -> np.ndarray:
    """No audio: playlist co-occurrence (10 PCs of t2v), ENOA map position, release year."""
    t2v = PCA(n_components=10, random_state=0).fit_transform(StandardScaler().fit_transform(df[T2V]))
    rest = df[["artist_enoa_top", "artist_enoa_left", "year_normalized"]].to_numpy(float)
    return StandardScaler().fit_transform(np.hstack([t2v, rest]))


def recover_playlists(df: pd.DataFrame) -> pd.Series:
    """Anonymous playlist ids for tracks in exactly one playlist; NaN for the rest.

    The file has no playlist column, but pp_* is the mean of the track's playlist, so every track
    of a one-playlist membership carries identical pp_* values. That is why pp_* can't be a feature.
    """
    single = df["n_playlists"] == 1
    return df.loc[single].groupby(PP).ngroup().reindex(df.index)


def fit_kmeans(X, k, seed, n_init=1):
    return KMeans(n_clusters=k, n_init=n_init, random_state=seed).fit_predict(X)


def fit_gmm(X, k, seed, n_init=1):
    return GaussianMixture(n_components=k, covariance_type="full", n_init=n_init, random_state=seed).fit(X)


def n_params(k: int, d: int) -> int:
    """Free parameters of a full-covariance mixture: means, covariances, weights."""
    return k * d + k * d * (d + 1) // 2 + k - 1


def seed_ari(labelings: list[np.ndarray]) -> float:
    """Mean adjusted Rand index over all pairs of runs: 1 = same partition, 0 = chance."""
    return float(np.mean([adjusted_rand_score(a, b) for a, b in itertools.combinations(labelings, 2)]))


def k_sweep(X: np.ndarray, ks=KS, seeds=SEEDS) -> pd.DataFrame:
    """BIC, silhouette and seed stability for k-means and a full-covariance GMM at each k."""
    def one_k(k):
        km = [fit_kmeans(X, k, s) for s in seeds]
        models = [fit_gmm(X, k, s) for s in seeds]
        gm = [m.predict(X) for m in models]
        return dict(
            k=k,
            bic=float(np.mean([m.bic(X) for m in models])),
            bic_sd=float(np.std([m.bic(X) for m in models])),
            sil_kmeans=float(np.mean([silhouette_score(X, y) for y in km])),
            sil_gmm=float(np.mean([silhouette_score(X, y) for y in gm])),
            ari_kmeans=seed_ari(km),
            ari_gmm=seed_ari(gm),
            min_cluster_gmm=int(min(np.bincount(y, minlength=k).min() for y in gm)),
        )
    return pd.DataFrame(Parallel(n_jobs=-1)(delayed(one_k)(k) for k in ks))


def shuffle_columns(X: np.ndarray, seed: int = 0) -> np.ndarray:
    """The same marginals with every link between features cut: a library with no real groups."""
    rng = np.random.default_rng(seed)
    return np.column_stack([rng.permutation(X[:, j]) for j in range(X.shape[1])])


def eta2(values: np.ndarray, labels: np.ndarray) -> float:
    """Share of each feature's variance explained by cluster membership, averaged over features."""
    total = ((values - values.mean(0)) ** 2).sum(0)
    within = sum(((values[labels == c] - values[labels == c].mean(0)) ** 2).sum(0) for c in np.unique(labels))
    return float(np.mean(1 - within / total))


def describe_partition(df, labels, X_audio, playlists) -> dict:
    """How a partition relates to sound, taxonomy, filing and artefacts of the file."""
    has_genre = df["gen_8"].notna().to_numpy()
    has_playlist = playlists.notna().to_numpy()
    missing = ((df["top"] == 0) & (df["left"] == 0)).to_numpy().astype(int)
    return dict(
        audio_variance_explained=eta2(X_audio, labels),
        nmi_gen8=float(normalized_mutual_info_score(df["gen_8"][has_genre], labels[has_genre])),
        nmi_playlist=float(normalized_mutual_info_score(playlists[has_playlist], labels[has_playlist])),
        nmi_key_mode=float(normalized_mutual_info_score(df["key_mode"], labels)),
        nmi_decade=float(normalized_mutual_info_score(df["decade"], labels)),
        nmi_missing_map_position=float(normalized_mutual_info_score(missing, labels)),
    )


def match_to(reference: np.ndarray, labels: np.ndarray, k: int) -> np.ndarray:
    """Per-reference-cluster Jaccard after Hungarian matching of another run's cluster ids."""
    jac = np.zeros((k, k))
    for i, j in itertools.product(range(k), range(k)):
        a, b = reference == i, labels == j
        union = (a | b).sum()
        jac[i, j] = (a & b).sum() / union if union else 0
    rows, cols = linear_sum_assignment(-jac)
    return jac[rows, cols]


def name_clusters(df, X, labels, posterior, seeds=SEEDS, k=PROJECT_K) -> pd.DataFrame:
    """One row per cluster: size, confidence, stability, its profile and what the taxonomy says."""
    others = [fit_gmm(X, k, 100 + s).predict(X) for s in seeds]
    jaccard = np.array([match_to(labels, other, k) for other in others])
    overall = df["gen_8"].value_counts(normalize=True)
    z = pd.DataFrame(X, columns=AUDIO)
    rows = []
    for c in range(k):
        mask = labels == c
        profile = z[mask].mean().sort_values(key=np.abs, ascending=False)
        genres = df.loc[mask, "gen_8"].value_counts(normalize=True)
        rows.append(dict(
            cluster=c,
            tracks=int(mask.sum()),
            mean_top_posterior=float(posterior[mask].max(1).mean()),
            jaccard_across_seeds=float(np.median(jaccard[:, c])),
            name=(" / ".join(f"{'high' if value > 0 else 'low'} {feature}" for feature, value in profile.head(2).items())
                  if np.median(jaccard[:, c]) >= STABLE_JACCARD else "(unstable: no name)"),
            profile=", ".join(f"{name} {value:+.1f}" for name, value in profile.head(3).items()),
            top_gen8=genres.index[0],
            top_gen8_share=float(genres.iloc[0]),
            lift=float(genres.iloc[0] / overall[genres.index[0]]),
        ))
    return pd.DataFrame(rows).sort_values("tracks", ascending=False).reset_index(drop=True)


def soft_vs_hard_retrieval(df, playlists, X, k=PROJECT_K, min_prob=0.05, seed=0) -> dict:
    """Clusters as a candidate filter. A playlist's query is the mean posterior of its train tracks.

    Hard keeps its single top cluster; soft keeps every cluster at >= min_prob (clustering.py's
    threshold). Recall is over held-out members; pool is the share of held-out tracks kept.
    k-means has no posterior, so it can only play the hard version.
    """
    idx = np.where(playlists.notna())[0]
    y = playlists.to_numpy()[idx].astype(int)
    keep = np.isin(y, np.where(np.bincount(y) >= 20)[0])
    idx, y = idx[keep], y[keep]
    out = {"kmeans hard": [], "gmm hard": [], "gmm soft": []}
    for train, test in StratifiedKFold(5, shuffle=True, random_state=seed).split(idx, y):
        scaler = StandardScaler().fit(X[idx[train]])
        gm = fit_gmm(scaler.transform(X[idx[train]]), k, seed)
        p_train = gm.predict_proba(scaler.transform(X[idx[train]]))
        dominant = gm.predict(scaler.transform(X[idx[test]]))
        km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(scaler.transform(X[idx[train]]))
        km_test = km.predict(scaler.transform(X[idx[test]]))
        for g in np.unique(y):
            query = p_train[y[train] == g].mean(0)
            positives = y[test] == g
            km_top = np.bincount(km.labels_[y[train] == g], minlength=k).argmax()
            for name, assigned, clusters in (("kmeans hard", km_test, [km_top]),
                                             ("gmm hard", dominant, [query.argmax()]),
                                             ("gmm soft", dominant, np.where(query >= min_prob)[0])):
                kept = np.isin(assigned, clusters)
                out[name].append((kept[positives].mean(), kept.mean()))
    return {name: dict(recall=float(np.mean([r for r, _ in v])), pool=float(np.mean([p for _, p in v])))
            for name, v in out.items()}


# --- the reranker ------------------------------------------------------------------------------


def topk(y, score, k=10) -> float:
    return float(y[np.argsort(-score, kind="stable")[:k]].mean())


def lgbm(seed=0) -> LGBMClassifier:
    return LGBMClassifier(n_estimators=100, learning_rate=0.05, num_leaves=15, min_child_samples=5,
                          class_weight="balanced", random_state=seed, n_jobs=1, verbose=-1)


def feature_sets(df: pd.DataFrame) -> dict[str, np.ndarray]:
    audio = df[AUDIO].to_numpy(float)
    enoa = df[ENOA].replace(0.0, np.nan).to_numpy(float)   # 0,0 is "not on the map", not a place
    genre = one_hot(df["gen_8"], GEN8)
    year = df[["year_normalized"]].to_numpy(float)
    return {
        "audio": np.hstack([audio, year]),
        "proxies": np.hstack([enoa, genre, year]),
        "audio+proxies": np.hstack([audio, enoa, genre, year]),
        "map position only": enoa,
        "t2v only": df[T2V].to_numpy(float),
        "audio+pp (leak)": np.hstack([audio, year, df[PP].to_numpy(float)]),
    }


def rerank_cv(df: pd.DataFrame, playlists: pd.Series, repeats: int = 2, k: int = PROJECT_K) -> pd.DataFrame:
    """One binary model per playlist, as train.py does, scored on tracks it never saw.

    The GMM, scaler and centroids are refit on each training fold. Returns one row per
    (method, repeat, playlist), with metrics averaged over five folds.
    """
    idx = np.where(playlists.notna())[0]
    y_all = playlists.to_numpy()[idx].astype(int)
    keep = np.isin(y_all, np.where(np.bincount(y_all) >= 20)[0])   # train.py's MIN_POSITIVES
    frame = df.iloc[idx[keep]].reset_index(drop=True)
    y_all = y_all[keep]
    sets = feature_sets(frame)
    audio = frame[AUDIO].to_numpy(float)
    groups = np.unique(y_all)

    def score(y, s):
        return roc_auc_score(y, s), average_precision_score(y, s), topk(y, s), min(10, y.sum()) / 10, y.mean()

    def one_fold(repeat, fold, train, test):
        rows = []
        scaler = StandardScaler().fit(audio[train])
        a_train, a_test = scaler.transform(audio[train]), scaler.transform(audio[test])
        gm = fit_gmm(a_train, k, repeat)
        p_train, p_test = gm.predict_proba(a_train), gm.predict_proba(a_test)
        for g in groups:
            y_tr, y_te = (y_all[train] == g).astype(int), (y_all[test] == g).astype(int)
            centroid = a_train[y_tr == 1].mean(0)
            cosine = a_test @ centroid / (np.linalg.norm(a_test, axis=1) * np.linalg.norm(centroid))
            cluster = p_test @ p_train[y_tr == 1].mean(0)
            rows.append(("cosine to centroid", repeat, fold, g, *score(y_te, cosine)))
            rows.append(("GMM posterior overlap", repeat, fold, g, *score(y_te, cluster)))
            for name, X in sets.items():
                model = lgbm(repeat).fit(X[train], y_tr)
                rows.append((f"LightGBM {name}", repeat, fold, g, *score(y_te, model.predict_proba(X[test])[:, 1])))
            with_posterior = lgbm(repeat).fit(np.hstack([sets["audio"][train], p_train]), y_tr)
            s = with_posterior.predict_proba(np.hstack([sets["audio"][test], p_test]))[:, 1]
            rows.append(("LightGBM audio+posteriors", repeat, fold, g, *score(y_te, s)))
        return rows

    splits = [(r, f, tr, te) for r in range(repeats)
              for f, (tr, te) in enumerate(StratifiedKFold(5, shuffle=True, random_state=r).split(audio, y_all))]
    rows = sum(Parallel(n_jobs=-1)(delayed(one_fold)(*s) for s in splits), [])
    cols = ["method", "repeat", "fold", "playlist", "auc", "ap", "p_at_10", "p_at_10_ceiling", "base_rate"]
    return pd.DataFrame(rows, columns=cols).groupby(["method", "repeat", "playlist"], as_index=False)[
        ["auc", "ap", "p_at_10", "p_at_10_ceiling", "base_rate"]].mean()


def project_recipe(df: pd.DataFrame, playlists: pd.Series) -> pd.DataFrame:
    """classifiers.py's protocol on the recoverable tracks: one 70/30 split per playlist.

    "as written" builds similarity_score and tempo_deviation from every positive, test ones
    included. "train-only" builds them from training positives. "no playlist columns" also drops
    fave_score and playlist_diversity. Camelot distance, the all-zero embedding_similarity and
    calibration are left out; population is the one-playlist tracks, because multi-playlist
    membership can't be recovered from the file.
    """
    idx = np.where(playlists.notna())[0]
    y_all = playlists.to_numpy()[idx].astype(int)
    frame = df.iloc[idx].reset_index(drop=True)
    gm = fit_gmm(project_matrix(df), PROJECT_K, 42)
    cluster_prob = gm.predict_proba(project_matrix(df))[idx].max(1)
    sim_cols = AUDIO + ["popularity", "top", "left", "fave_score", "n_playlists", "year_normalized"]
    base = frame[sim_cols].to_numpy(float)
    cats = np.hstack([one_hot(frame["decade"], DECADES), one_hot(frame["gen_4"], GEN4)])
    extra = frame[["playlist_diversity"]].to_numpy(float)
    groups = [g for g in np.unique(y_all) if (y_all == g).sum() >= 20]

    def cos(M, c):
        return (M @ c / (np.linalg.norm(M, axis=1) * np.linalg.norm(c))).reshape(-1, 1)

    def run(g):
        y = (y_all == g).astype(int)
        tr, te = train_test_split(np.arange(len(y)), test_size=0.3, stratify=y, random_state=42)
        out = []
        for name, source, keep_playlist_cols in (("as written", np.arange(len(y)), True),
                                                 ("train-only", tr, True),
                                                 ("train-only, no playlist columns", tr, False)):
            positives = source[y[source] == 1]
            core = base if keep_playlist_cols else np.delete(base, sim_cols.index("fave_score"), axis=1)
            sim = cos(core, core[positives].mean(0))
            tempo = np.abs(frame["tempo"].to_numpy(float) - frame["tempo"].to_numpy(float)[positives].mean()).reshape(-1, 1)
            parts = [core, sim, cluster_prob.reshape(-1, 1), tempo, cats] + ([extra] if keep_playlist_cols else [])
            X = np.hstack(parts)
            model = LGBMClassifier(class_weight="balanced", n_estimators=200, learning_rate=0.05,
                                   num_leaves=31, random_state=42, n_jobs=1, verbose=-1).fit(X[tr], y[tr])
            s = model.predict_proba(X[te])[:, 1]
            out.append((name, g, roc_auc_score(y[te], s), topk(y[te], s), y[te].mean()))
        return out

    rows = sum(Parallel(n_jobs=-1)(delayed(run)(g) for g in groups), [])
    return pd.DataFrame(rows, columns=["variant", "playlist", "auc", "p_at_10", "base_rate"])


def plot_sweep(sweep: pd.DataFrame, path: Path = FIGURE) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    blue, orange, ink, muted = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e"
    plt.rcParams.update({"font.size": 11, "axes.edgecolor": "#c9c8c2", "axes.labelcolor": muted,
                         "xtick.color": muted, "ytick.color": muted, "font.family": "DejaVu Sans"})
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.1), facecolor="#fcfcfb")
    style = dict(linewidth=2, markersize=5.5, markeredgecolor="#fcfcfb", markeredgewidth=1)
    panels = [
        (axes[0], "BIC (lower fits better)", [("bic", "GMM", blue)]),
        (axes[1], "Silhouette (higher separates better)", [("sil_kmeans", "k-means", orange), ("sil_gmm", "GMM", blue)]),
        (axes[2], "Agreement across 10 seeds (ARI)", [("ari_kmeans", "k-means", orange), ("ari_gmm", "GMM", blue)]),
    ]
    for ax, title, series in panels:
        ax.set_facecolor("#fcfcfb")
        ax.axvline(PROJECT_K, color="#c9c8c2", linewidth=1.5, linestyle=(0, (3, 3)), zorder=0)
        for col, label, color in series:
            marker = "s" if label == "k-means" else "o"
            ax.plot(sweep["k"], sweep[col], marker=marker, color=color, label=label, **style)
        ax.set_title(title, fontsize=11.5, color=ink, loc="left")
        ax.set_xlabel("k")
        ax.set_xticks(range(2, 15, 2))
        ax.grid(axis="y", color="#ecebe6", linewidth=1)
        ax.spines[["top", "right"]].set_visible(False)
        if len(series) > 1:
            ax.legend(frameon=False, fontsize=10)
    axes[0].annotate("project's k = 8", xy=(PROJECT_K, 0.93), xycoords=("data", "axes fraction"),
                     xytext=(5, 0), textcoords="offset points", fontsize=9.5, color=muted)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def t2v_separation(df: pd.DataFrame, playlists: pd.Series) -> dict:
    """Mean cosine between t2v vectors of tracks in the same playlist and in different ones."""
    mask = playlists.notna().to_numpy()
    v = df.loc[mask, T2V].to_numpy(float)
    v = v / np.linalg.norm(v, axis=1, keepdims=True)
    groups = playlists[mask].to_numpy()
    cos, same = v @ v.T, groups[:, None] == groups[None, :]
    off = ~np.eye(len(v), dtype=bool)
    return dict(same_playlist=float(cos[same & off].mean()), different_playlist=float(cos[~same].mean()))


def main() -> None:
    start = time.time()
    df = load_library()
    playlists = recover_playlists(df)
    results: dict = {"commit": COMMIT, "versions": dict(
        python=platform.python_version(), sklearn=sklearn.__version__, lightgbm=lightgbm.__version__)}
    print(f"versions: python {platform.python_version()}, scikit-learn {sklearn.__version__}, "
          f"lightgbm {lightgbm.__version__}, numpy {np.__version__}, pandas {pd.__version__}")

    print("\n== 1. The data ==")
    missing = int(((df["top"] == 0) & (df["left"] == 0)).sum())
    corr = df[["energy", "loudness"]].corr().iloc[0, 1]
    results["data"] = dict(
        tracks=len(df), columns_in_file=114, columns_read=len(SAFE_COLUMNS),
        features_source=df["features_source"].value_counts().to_dict(),
        map_position_zero=missing, gen8_missing=int(df["gen_8"].isna().sum()),
        min_n_playlists=int(df["n_playlists"].min()), energy_loudness_r=float(corr),
        playlists_recoverable=int(playlists.nunique()), tracks_one_playlist=int(playlists.notna().sum()),
    )
    for key, value in results["data"].items():
        print(f"{key}: {value}")

    print("\n== 2. Scaling ==")
    raw = df[AUDIO + ["duration_ms"]].to_numpy(float)
    share = raw.var(0) / raw.var(0).sum()
    unscaled = fit_kmeans(raw, PROJECT_K, 0, n_init=10)
    duration_only = fit_kmeans(raw[:, [-1]], PROJECT_K, 0, n_init=10)
    scaled = fit_kmeans(StandardScaler().fit_transform(raw), PROJECT_K, 0, n_init=10)
    results["scaling"] = dict(
        duration_variance_share=float(share[-1]),
        ari_unscaled_vs_duration_only=float(adjusted_rand_score(unscaled, duration_only)),
        ari_scaled_vs_duration_only=float(adjusted_rand_score(scaled, duration_only)),
    )
    print(json.dumps(results["scaling"], indent=1))

    print("\n== 3. Choosing k on the nine audio features (10 seeds each, n_init=1) ==")
    X = audio_matrix(df)
    sweep = k_sweep(X)
    print(sweep.round(3).to_string(index=False))
    results["sweep"] = sweep.round(4).to_dict("records")
    results["k_choice"] = dict(
        bic_best_k=int(sweep.loc[sweep.bic.idxmin(), "k"]),
        sil_best_k_kmeans=int(sweep.loc[sweep.sil_kmeans.idxmax(), "k"]),
        sil_best_k_gmm=int(sweep.loc[sweep.sil_gmm.idxmax(), "k"]),
        ari_best_k_kmeans=int(sweep.loc[sweep.ari_kmeans.idxmax(), "k"]),
        ari_best_k_gmm=int(sweep.loc[sweep.ari_gmm.idxmax(), "k"]),
    )
    print(results["k_choice"])
    plot_sweep(sweep)
    null = k_sweep(shuffle_columns(X), seeds=SEEDS[:3])
    results["null_sweep"] = dict(
        bic_best_k=int(null.loc[null.bic.idxmin(), "k"]),
        sil_kmeans_k2=float(null.loc[null.k == 2, "sil_kmeans"].iloc[0]),
        sil_kmeans_k8=float(null.loc[null.k == PROJECT_K, "sil_kmeans"].iloc[0]),
        sil_gmm_k8=float(null.loc[null.k == PROJECT_K, "sil_gmm"].iloc[0]),
        sil_real_kmeans_k2=float(sweep.loc[sweep.k == 2, "sil_kmeans"].iloc[0]),
        sil_real_kmeans_k8=float(sweep.loc[sweep.k == PROJECT_K, "sil_kmeans"].iloc[0]),
        bic_real_k8=float(sweep.loc[sweep.k == PROJECT_K, "bic"].iloc[0]),
        bic_shuffled_k8=float(null.loc[null.k == PROJECT_K, "bic"].iloc[0]),
    )
    print("same library, each column shuffled separately:", json.dumps(results["null_sweep"], indent=1))

    print(f"\n== 4. Soft assignment at k={PROJECT_K} ==")
    gm = fit_gmm(X, PROJECT_K, 0, n_init=5)
    posterior = gm.predict_proba(X)
    labels = posterior.argmax(1)
    km_labels = fit_kmeans(X, PROJECT_K, 0, n_init=10)
    top = posterior.max(1)
    results["soft"] = dict(
        share_top_posterior_under_0_8=float((top < 0.8).mean()),
        share_top_posterior_under_0_6=float((top < 0.6).mean()),
        median_top_posterior=float(np.median(top)),
        ari_gmm_vs_kmeans=float(adjusted_rand_score(labels, km_labels)),
        retrieval=soft_vs_hard_retrieval(df, playlists, df[AUDIO].to_numpy(float)),
    )
    print(json.dumps(results["soft"], indent=1))

    print(f"\n== 5. What each feature space clusters on, at k={PROJECT_K} (5 seeds) ==")
    spaces = {"audio (9)": X, "project (47)": project_matrix(df), "proxies (13)": proxy_matrix(df)}
    rows, reference = [], {}
    for name, M in spaces.items():
        runs = [fit_gmm(M, PROJECT_K, s) for s in range(5)]
        ys = [m.predict(M) for m in runs]
        reference[name] = ys[0]
        rows.append(dict(space=name, d=M.shape[1], params=n_params(PROJECT_K, M.shape[1]),
                         silhouette=float(np.mean([silhouette_score(M, y) for y in ys])),
                         seed_ari=seed_ari(ys),
                         **describe_partition(df, ys[0], X, playlists)))
    spaces_table = pd.DataFrame(rows)
    print(spaces_table.round(3).T.to_string(header=False))
    results["spaces"] = spaces_table.round(4).to_dict("records")
    results["ari_audio_vs_proxies"] = float(adjusted_rand_score(reference["audio (9)"], reference["proxies (13)"]))
    print("ARI, audio partition vs proxy partition:", round(results["ari_audio_vs_proxies"], 3))

    print(f"\n== 6. Naming the {PROJECT_K} audio clusters (aggregates only) ==")
    names = name_clusters(df, X, labels, posterior)
    print(names.round(3).to_string(index=False))
    results["clusters"] = names.round(3).to_dict("records")
    has_genre = df["gen_8"].notna().to_numpy()
    results["nmi_gmm_vs_gen8"] = float(normalized_mutual_info_score(df["gen_8"][has_genre], labels[has_genre]))
    print("NMI, GMM clusters vs gen_8 taxonomy:", round(results["nmi_gmm_vs_gen8"], 3))

    print("\n== 7. The reranker: one model per playlist, 5-fold x 2 repeats, held-out tracks ==")
    rerank = rerank_cv(df, playlists)
    summary = rerank.groupby("method")[["auc", "ap", "p_at_10", "p_at_10_ceiling", "base_rate"]].mean().sort_values("auc")
    print(summary.round(3).to_string())
    results["t2v_cosine"] = t2v_separation(df, playlists)
    print("t2v cosine:", {k: round(v, 3) for k, v in results["t2v_cosine"].items()})
    per_playlist = rerank.groupby(["method", "playlist"])[["auc"]].mean().reset_index()
    pivot = per_playlist.pivot(index="playlist", columns="method", values="auc")
    def paired(a, b):
        delta = pivot[a] - pivot[b]
        rng = np.random.default_rng(0)
        boots = [rng.choice(delta, len(delta)).mean() for _ in range(2000)]
        return dict(a=a, b=b, delta=float(delta.mean()), ci95=[float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                    a_wins=int((delta > 0).sum()), n=int(len(delta)))
    results["rerank"] = summary.round(4).reset_index().to_dict("records")
    results["rerank_paired"] = [
        paired("LightGBM audio", "cosine to centroid"),
        paired("LightGBM audio", "LightGBM proxies"),
        paired("LightGBM audio+proxies", "LightGBM proxies"),
        paired("LightGBM audio+posteriors", "LightGBM audio"),
    ]
    for row in results["rerank_paired"]:
        print(f"{row['a']} minus {row['b']}: AUC {row['delta']:+.3f} "
              f"(95% CI {row['ci95'][0]:+.3f} to {row['ci95'][1]:+.3f} over playlists; wins {row['a_wins']}/{row['n']})")

    print("\n== 8. The project's recipe, on the same tracks, one 70/30 split per playlist ==")
    recipe = project_recipe(df, playlists)
    recipe_summary = recipe.groupby("variant")[["auc", "p_at_10", "base_rate"]].mean().sort_values("auc")
    print(recipe_summary.round(3).to_string())
    results["recipe"] = recipe_summary.round(4).reset_index().to_dict("records")

    (HERE / "results.json").write_text(json.dumps(results, indent=1) + "\n")
    print(f"\nwrote results.json and {FIGURE.name}")
    print(f"runtime: {time.time() - start:.0f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
