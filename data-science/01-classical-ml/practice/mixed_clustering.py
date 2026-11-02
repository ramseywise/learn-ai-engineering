# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scipy", "scikit-learn", "matplotlib", "prince==0.23.*", "kmodes", "kmedoids", "stepmix", "catboost", "palmerpenguins"]
# ///
"""Numbers and figure for notes/05b: clustering customers when the columns are categorical or mixed.

Run from this folder:
    uv run mixed_clustering.py

All customer tables are generated and seeded, so none of this measures real-world performance. The one real
table is Palmer penguins (CC0). Timings depend on the machine. Writes classical-mixed-benchmark.png to sources/images.
"""
# %%
import time
import warnings

import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
from kmedoids import fasterpam
from kmodes.kprototypes import KPrototypes
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.feature_extraction import FeatureHasher
from sklearn.metrics import adjusted_rand_score as ari
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEEDS = range(5)
K = 4
NUMERIC = ["log_invoices", "log_revenue", "tenure", "logins", "overdue_share"]
CATEGORICAL = {"plan": 4, "channel": 5, "industry": 10, "size": 3, "payroll": 2, "mobile": 2}
SHARES = [0.4, 0.3, 0.2, 0.1]


# %% generator
def make_customers(world="both", n=1200, seed=0, spread=1.0, concentration=0.6):
    """Tallybook's small-business customers, four archetypes in these worlds:

    both: groups differ in numeric and categorical columns. categorical: only in categorical ones.
    numeric: only in numeric ones. control: `both` with each column shuffled alone, so no groups exist.
    correlated: `both`, plus a business-size factor inside every group that moves three numbers and `size`
    together, which breaks the independence a latent class model assumes.
    """
    # Archetype definitions come from their own stream, so a world's groups stay the same across draws.
    defs = np.random.default_rng(1000)
    means = defs.normal(0, 1.1, (K, len(NUMERIC)))
    probs = {c: defs.dirichlet(np.full(m, concentration), K) for c, m in CATEGORICAL.items()}
    rng = np.random.default_rng(seed)
    y = rng.choice(K, n, p=SHARES)
    numeric_on = world in ("both", "numeric", "control", "correlated")
    categorical_on = world in ("both", "categorical", "control", "correlated")
    df = pd.DataFrame(index=range(n))
    for j, c in enumerate(NUMERIC):
        centre = means[y, j] if numeric_on else 0.0
        df[c] = rng.normal(centre, spread, n)
    for c, m in CATEGORICAL.items():
        pooled = np.array(SHARES) @ probs[c]
        p = probs[c][y] if categorical_on else np.tile(pooled, (n, 1))
        u = rng.random(n)[:, None]
        df[c] = [f"{c}_{i}" for i in (p.cumsum(1) < u).sum(1)]
    if world == "correlated":
        scale = rng.normal(0, 1, n)
        for c in ("log_invoices", "log_revenue", "logins"):
            df[c] += 1.5 * scale
        df["size"] = np.where(scale < -.5, "size_0", np.where(scale < .5, "size_1", "size_2"))
    if world == "control":
        for c in df:
            df[c] = rng.permutation(df[c].to_numpy())
    return df, y


def split(df):
    return [c for c in df if df[c].dtype.kind in "fi"], [c for c in df if df[c].dtype.kind not in "fi"]


# %% representations
def onehot_matrix(df):
    """The default people reach for: z-scored numbers beside raw dummy columns."""
    num, cat = split(df)
    return np.hstack([StandardScaler().fit_transform(df[num]),
                      OneHotEncoder(sparse_output=False).fit_transform(df[cat])])


def famd_matrix(df):
    """FAMD's table before its SVD: z-scores, and dummies divided by the root of their share, then centred."""
    num, cat = split(df)
    dummies = OneHotEncoder(sparse_output=False).fit_transform(df[cat])
    share = dummies.mean(0)
    return np.hstack([StandardScaler().fit_transform(df[num]), (dummies - share) / np.sqrt(share)])


def famd(df, n_components=8):
    """Row coordinates, eigenvalues and the share of each column block in those axes."""
    Z = famd_matrix(df)
    U, S, Vt = np.linalg.svd(Z, full_matrices=False)
    return (U * S)[:, :n_components], S ** 2 / len(df)


def gower(df, numeric_weight=1.0):
    """Weighted mean over columns of range-scaled absolute difference (numbers) or mismatch (categories)."""
    num, cat = split(df)
    n = len(df)
    D = np.zeros((n, n))
    for c in num:
        x = df[c].to_numpy(float)
        D += numeric_weight * np.abs(x[:, None] - x[None, :]) / (x.max() - x.min())
    for c in cat:
        x = pd.factorize(df[c])[0]
        D += x[:, None] != x[None, :]
    return D / (numeric_weight * len(num) + len(cat))


def column_spread(df):
    """Standard deviation of each column's own Gower term over all pairs: how much that column moves the distance."""
    num, cat = split(df)
    spread = {}
    for c in num:
        x = df[c].to_numpy(float)
        spread[c] = (np.abs(x[:, None] - x[None, :]) / (x.max() - x.min())).std()
    for c in cat:
        x = pd.factorize(df[c])[0]
        spread[c] = (x[:, None] != x[None, :]).std()
    return pd.Series(spread)


def mca_eigenvalues(df_cat):
    """Principal inertias of the indicator table: correspondence analysis by SVD."""
    Z = OneHotEncoder(sparse_output=False).fit_transform(df_cat)
    P = Z / Z.sum()
    r, c = P.sum(1), P.sum(0)
    S = (P - np.outer(r, c)) / np.sqrt(np.outer(r, c))
    U, s, Vt = np.linalg.svd(S, full_matrices=False)
    return s ** 2, U, s, Vt, c


def benzecri(eig, J):
    """Benzecri's correction: only axes above 1/J count, and each is rescaled."""
    kept = eig[eig > 1 / J]
    return (J / (J - 1) * (kept - 1 / J)) ** 2


# %% methods
def km(X, k=K, seed=0):
    return KMeans(k, n_init=10, random_state=seed).fit_predict(X)


def pam(D, k=K, seed=0):
    return np.asarray(fasterpam(D, k, random_state=seed, n_cpu=1).labels).astype(int)


def kproto(df, k=K, seed=0):
    num, cat = split(df)
    X = df[num + cat].copy()
    X[num] = StandardScaler().fit_transform(X[num])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = KPrototypes(n_clusters=k, init="Cao", n_init=3, random_state=seed)
        return model.fit_predict(X.to_numpy(), categorical=list(range(len(num), X.shape[1]))), model.gamma


def lca(df, k=K, seed=0):
    """Latent classes: Gaussian columns and categorical columns, independent within a class."""
    from stepmix.stepmix import StepMix
    from stepmix.utils import get_mixed_descriptor
    num, cat = split(df)
    codes = df.copy()
    for c in cat:
        codes[c] = pd.factorize(df[c])[0]
    if num:
        codes[num] = StandardScaler().fit_transform(df[num])
    data, descriptor = get_mixed_descriptor(codes, continuous=num, categorical=cat)
    model = StepMix(n_components=k, measurement=descriptor, n_init=3, max_iter=200, random_state=seed, verbose=0, progress_bar=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(data)
    return model, model.predict(data), data


def all_methods(df, seed=0):
    X = onehot_matrix(df)
    D = gower(df)
    out = {
        "one-hot, k-means": km(X, seed=seed),
        "one-hot, PCA 8, k-means": km(PCA(8, random_state=0).fit_transform(X), seed=seed),
        "FAMD 8, k-means": km(famd(df)[0], seed=seed),
        "Gower, PAM": pam(D, seed=seed),
        "Gower, average link": AgglomerativeClustering(K, metric="precomputed", linkage="average").fit_predict(D),
        "k-prototypes": kproto(df, seed=seed)[0],
        "latent class": lca(df, seed=seed)[1],
    }
    return out, D


# %% benchmark
def benchmark(seeds=SEEDS, spreads=(1.0,)):
    rows = []
    for world in ("both", "categorical", "numeric"):
        for seed in seeds:
            df, y = make_customers(world, seed=seed)
            labels, _ = all_methods(df, seed)
            rows += [{"world": world, "seed": seed, "method": m, "ari": ari(y, l)} for m, l in labels.items()]
    return pd.DataFrame(rows)


def internal_indices(k_range=range(2, 8), seed=0):
    """Does each index find k=4 with groups, and go quiet without any? On FAMD coordinates and on Gower."""
    rows = []
    for world in ("both", "control"):
        df, _ = make_customers(world, seed=seed)
        Z, D = famd(df)[0], gower(df)
        for k in k_range:
            labels = km(Z, k, seed)
            medoid = pam(D, k, seed)
            rows.append({"world": world, "k": k, "sil_famd": silhouette_score(Z, labels),
                         "ch_famd": calinski_harabasz_score(Z, labels), "db_famd": davies_bouldin_score(Z, labels),
                         "sil_gower": silhouette_score(D, medoid, metric="precomputed")})
    return pd.DataFrame(rows)


def subsample_stability(world, method, frac=0.8, reps=10, seed=0):
    """Fit on two overlapping 80% subsamples and compare labels on the customers they share."""
    df, _ = make_customers(world, seed=seed)
    rng = np.random.default_rng(seed)
    scores = []
    for _ in range(reps):
        a = rng.choice(len(df), int(frac * len(df)), replace=False)
        b = rng.choice(len(df), int(frac * len(df)), replace=False)
        both = np.intersect1d(a, b)
        la = pd.Series(method(df.iloc[a].reset_index(drop=True)), index=a)
        lb = pd.Series(method(df.iloc[b].reset_index(drop=True)), index=b)
        scores.append(ari(la[both], lb[both]))
    return float(np.mean(scores))


# %% tandem
def tandem_world(n=1200, seed=0, separation=5.0):
    """Three groups in two quiet columns, beside three loud columns that share one factor and hold no groups."""
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 3, n)
    corners = np.array([[0, 0], [separation, 0], [separation / 2, separation * .87]])
    quiet = corners[y] + rng.normal(0, 1, (n, 2))
    factor = rng.normal(0, 1, (n, 1))
    loud = np.sqrt(.9) * factor + np.sqrt(.1) * rng.normal(0, 1, (n, 3))
    return StandardScaler().fit_transform(np.column_stack([quiet, loud])), y


def tandem_table(seeds=SEEDS):
    rows = []
    for seed in seeds:
        X, y = tandem_world(seed=seed)
        rows.append({"all 5 columns": ari(y, km(X, 3, seed)), "the 2 quiet columns": ari(y, km(X[:, :2], 3, seed)),
                     **{f"PCA {q}": ari(y, km(PCA(q, random_state=0).fit_transform(X), 3, seed)) for q in (1, 2, 4)}})
    return pd.DataFrame(rows).mean().round(3), PCA().fit(X).explained_variance_ratio_.round(3)


# %% encodings
def high_cardinality_world(n=1500, levels=200, columns=3, seed=0):
    """Each level of three high-cardinality columns belongs to one of four groups; 80% of a customer's values follow theirs."""
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 4, n)
    frame = {}
    for j in range(columns):
        home = np.random.default_rng(2000 + j).integers(0, 4, levels)
        pool = [np.flatnonzero(home == g) for g in range(4)]
        picked = np.array([rng.choice(pool[g]) for g in y])
        noise = rng.random(n) < .2
        picked[noise] = rng.integers(0, levels, noise.sum())
        frame[f"c{j}"] = picked
    return pd.DataFrame(frame), y


def binary_encode(df):
    columns = []
    for c in df:
        codes = pd.factorize(df[c])[0] + 1
        bits = int(np.ceil(np.log2(codes.max() + 1)))
        columns.append(((codes[:, None] >> np.arange(bits)) & 1).astype(float))
    return np.hstack(columns)


def encoders(df, dim=32):
    onehot = OneHotEncoder().fit_transform(df)
    rows = [[f"{c}={v}" for c, v in zip(df.columns, row)] for row in df.to_numpy()]
    return {
        "one-hot": onehot.toarray(),
        "one-hot, SVD 8 (MCA-like)": TruncatedSVD(8, random_state=0).fit_transform(onehot),
        "binary": binary_encode(df),
        f"hashing, {dim} dims": FeatureHasher(dim, input_type="string").transform(rows).toarray(),
        "frequency": np.column_stack([df[c].map(df[c].value_counts(normalize=True)) for c in df]),
    }


# %% post-hoc explanation
def surrogate(world="both", seed=0):
    """Predict cluster labels with CatBoost, and report accuracy and the mean absolute SHAP per column."""
    from catboost import CatBoostClassifier, Pool
    df, _ = make_customers(world, seed=seed)
    labels = km(famd(df)[0], K, seed)
    _, cat = split(df)
    params = dict(iterations=200, depth=4, verbose=0, random_seed=seed, allow_writing_files=False)
    fold = np.random.default_rng(seed).integers(0, 3, len(df))
    hits = []
    for f in range(3):
        fit = CatBoostClassifier(**params).fit(Pool(df[fold != f], labels[fold != f], cat_features=cat))
        hits.append(fit.predict(Pool(df[fold == f], cat_features=cat)).ravel() == labels[fold == f])
    accuracy = np.concatenate(hits).mean()
    fitted = CatBoostClassifier(**params).fit(Pool(df, labels, cat_features=cat))
    shap = fitted.get_feature_importance(Pool(df, labels, cat_features=cat), type="ShapValues")
    per_col = np.abs(shap[:, :, :-1]).mean((0, 1))
    return accuracy, pd.Series(per_col, index=df.columns).sort_values(ascending=False)


# %% real data
def penguins():
    from palmerpenguins import load_penguins
    df = load_penguins().dropna().reset_index(drop=True)
    y = pd.factorize(df.species)[0]
    return df[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g", "island", "sex"]], y


# %% checks and stress tests
def block_variance(df):
    num, cat = split(df)
    n_dummies = OneHotEncoder(sparse_output=False).fit_transform(df[cat]).shape[1]
    return {name: (X[:, :len(num)].var(0).sum(), X[:, len(num):].var(0).sum()) for name, X in
            [("one-hot", onehot_matrix(df)), ("FAMD", famd_matrix(df))]}, n_dummies


def famd_criterion(z, df):
    """Sum of squared correlations with numbers and of correlation ratios with categories: what FAMD's axes maximise."""
    num, cat = split(df)
    value = sum(np.corrcoef(z, df[c])[0, 1] ** 2 for c in num)
    for c in cat:
        g = pd.Series(z).groupby(df[c].to_numpy())
        value += (g.size() * (g.mean() - z.mean()) ** 2).sum() / ((z - z.mean()) ** 2).sum()
    return value


def add_outliers(df):
    """One customer per numeric column with a mistyped 500."""
    out = df.copy()
    for i, c in enumerate(split(df)[0]):
        out.loc[i, c] = 500.0
    return out


def scaling(sizes=(1000, 2000, 4000, 8000)):
    rows = []
    for n in sizes:
        df, _ = make_customers("both", n=n)
        t0 = time.perf_counter()
        D = gower(df)
        t1 = time.perf_counter()
        pam(D)
        t2 = time.perf_counter()
        km(famd(df)[0])
        t3 = time.perf_counter()
        rows.append({"n": n, "gower_s": t1 - t0, "pam_s": t2 - t1, "famd_kmeans_s": t3 - t2, "matrix_gb": D.nbytes / 1e9})
    return pd.DataFrame(rows).round(3)


def figure(bench):
    import chartstyle as cs
    cs.apply()
    means = bench.pivot_table(index="method", columns="world", values="ari", aggfunc="mean")
    order = means.mean(axis=1).sort_values().index
    worlds = [("both", "Both kinds of column differ", cs.BLUE), ("categorical", "Only categories differ", cs.ORANGE),
              ("numeric", "Only numbers differ", cs.AQUA)]
    fig, ax = plt.subplots(figsize=(9, 4.2))
    for offset, (world, label, colour) in zip((.22, 0, -.22), worlds):
        ax.barh(np.arange(len(order)) + offset, means.loc[order, world], height=.2, color=colour, label=label)
    ax.set_yticks(range(len(order)), order)
    ax.set(xlabel="Adjusted Rand index against the groups that generated the data (1,200 customers, mean of 5 seeds)",
           title="No method wins every world, and latent class had the generator on its side", xlim=(0, 1))
    ax.legend(loc="lower right")
    ax.grid(False, axis="y")
    cs.save(fig, "classical-mixed-benchmark.png")


if __name__ == "__main__":
    import prince
    from kmodes.kmodes import KModes
    pd.set_option("display.width", 200)
    print("== benchmark: ARI, mean and sd over 5 seeds")
    bench = benchmark()
    print(bench.pivot_table(index="method", columns="world", values="ari", aggfunc="mean").round(3).to_string())
    print(bench.pivot_table(index="method", columns="world", values="ari", aggfunc="std").round(3).to_string())
    rows = []
    for seed in SEEDS:
        df, y = make_customers("correlated", seed=seed)
        rows.append({m: ari(y, l) for m, l in all_methods(df, seed)[0].items()})
    print("correlated world:", pd.DataFrame(rows).mean().round(3).to_dict())
    figure(bench)

    print("\n== why the defaults differ")
    df, y = make_customers("both", seed=0)
    num, cat = split(df)
    blocks, n_dummies = block_variance(df)
    print("total variance (numeric, categorical):", {k: tuple(round(x, 2) for x in v) for k, v in blocks.items()}, "dummies", n_dummies)
    print("Gower term spread per column:", column_spread(df).round(3).to_dict())

    print("\n== Gower variants, ARI over 5 seeds, world both")
    rows = []
    for seed in SEEDS:
        d, t = make_customers("both", seed=seed)
        n_, c_ = split(d)
        rows.append({"all": ari(t, pam(gower(d), K, seed)), "numeric only": ari(t, pam(gower(d[n_]), K, seed)),
                     "categorical only": ari(t, pam(gower(d[c_]), K, seed)),
                     "ranked numbers": ari(t, pam(gower(d.assign(**{c: d[c].rank() for c in n_})), K, seed)),
                     **{f"numbers x{w}": ari(t, pam(gower(d, numeric_weight=w), K, seed)) for w in (2, 3, 5)}})
    print(pd.DataFrame(rows).mean().round(3).to_dict())
    print("restarts at seed 0:", [round(ari(y, pam(gower(df), K, s)), 3) for s in SEEDS])
    for world in ("categorical", "numeric"):
        d, t = make_customers(world, seed=0)
        print(world, {w: round(ari(t, pam(gower(d, numeric_weight=w), K, 0)), 3) for w in (1, 2, 3, 5)})

    print("\n== FAMD: this lab against the criterion and against prince", prince.__version__)
    Z, eig = famd(df)
    print("eigenvalues", eig[:3].round(3), "criterion", [round(famd_criterion(Z[:, i], df), 3) for i in range(3)])
    model = prince.FAMD(n_components=8, random_state=0, categorical_columns=cat).fit(df)
    R = model.row_coordinates(df).to_numpy()
    print("prince eigenvalues", np.round(model.eigenvalues_[:3], 3), "criterion", [round(famd_criterion(R[:, i], df), 3) for i in range(3)])
    print("axis correlation", [round(abs(np.corrcoef(R[:, i], Z[:, i])[0, 1]), 3) for i in range(3)], "ARI", round(ari(y, km(R)), 3), "lab ARI", round(ari(y, km(Z)), 3))
    five = model.row_coordinates(df.iloc[:5]).to_numpy()
    print("row 2 scored in the table", R[2, :2].round(3), "and in a batch of 5", five[2, :2].round(3))

    print("\n== categorical columns only (world both, seed 0)")
    c = df[cat]
    eig_c, *_ = mca_eigenvalues(c)
    J = c.shape[1]
    corrected = benzecri(eig_c, J)
    mca = prince.MCA(n_components=6, random_state=0).fit(c)
    print("MCA eigenvalues", eig_c[:4].round(3), "prince", np.round(mca.eigenvalues_[:4], 3), "1/J", round(1 / J, 3))
    print("raw %", (100 * eig_c / eig_c.sum())[:4].round(1), "Benzecri %", (100 * corrected / corrected.sum())[:4].round(1))
    print({"one-hot, k-means": round(ari(y, km(OneHotEncoder(sparse_output=False).fit_transform(c))), 3),
           "MCA 6, k-means": round(ari(y, km(mca.row_coordinates(c).to_numpy())), 3),
           "k-modes": round(ari(y, KModes(K, init="Cao", n_init=3, random_state=0).fit_predict(c)), 3),
           "latent class": round(ari(y, lca(c)[1]), 3), "Gower, PAM": round(ari(y, pam(gower(c))), 3)})
    rare = c.copy()
    idx = np.random.default_rng(0).choice(len(c), 8, replace=False)
    rare.loc[idx, "channel"] = "channel_rare"
    rare.loc[idx, "plan"] = "plan_rare"
    mca_rare = prince.MCA(n_components=6, random_state=0).fit(rare)
    print("8 rare customers: eigenvalues", np.round(mca_rare.eigenvalues_[:3], 3), "top axis 1 contributions", mca_rare.column_contributions_.iloc[:, 0].sort_values(ascending=False).head(2).round(3).to_dict())
    Rr = mca_rare.row_coordinates(rare).to_numpy()
    print("axis 1 correlation with clean axis 1", round(abs(np.corrcoef(Rr[:, 0], mca.row_coordinates(c).to_numpy()[:, 0])[0, 1]), 3), "ARI", round(ari(y, km(Rr)), 3))

    print("\n== latent class BIC by k")
    for world in ("both", "control", "correlated"):
        d, _ = make_customers(world, seed=0)
        bic = []
        for k in range(1, 8):
            m, _l, data = lca(d, k)
            bic.append(round(m.bic(data)))
        print(world, bic)

    print("\n== k-prototypes gamma")
    for world in ("both", "categorical", "numeric"):
        d, t = make_customers(world, seed=0)
        n_, c_ = split(d)
        X = d[n_ + c_].copy()
        X[n_] = StandardScaler().fit_transform(X[n_])
        row = {"default": round(ari(t, kproto(d)[0]), 3), "default gamma": round(float(kproto(d)[1]), 3)}
        for g in (1, 2, 4, 8):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                m = KPrototypes(n_clusters=K, init="Cao", n_init=3, gamma=g, random_state=0)
                row[g] = round(ari(t, m.fit_predict(X.to_numpy(), categorical=list(range(len(n_), X.shape[1])))), 3)
        print(world, row)

    print("\n== tandem: three groups in 2 quiet columns, 3 loud correlated columns, ARI over 5 seeds")
    table, ratios = tandem_table()
    print(table.to_dict(), "variance ratios", ratios)

    print("\n== high-cardinality encoders, 1,500 rows, 3 columns of 200 levels, 3 seeds")
    results = {}
    for seed in range(3):
        h, t = high_cardinality_world(seed=seed)
        for name, E in encoders(h).items():
            results.setdefault(f"{name} ({E.shape[1]})", []).append(ari(t, km(E, K, seed)))
        results.setdefault("Gower, PAM", []).append(ari(t, pam(gower(h.astype(str)), K, seed)))
    print({k: round(float(np.mean(v)), 3) for k, v in results.items()})

    print("\n== internal indices, seed 0")
    print(internal_indices().round(3).to_string())

    print("\n== 80% subsample stability")
    for world in ("both", "control"):
        print(world, "FAMD k-means", round(subsample_stability(world, lambda d: km(famd(d)[0])), 3),
              "Gower PAM", round(subsample_stability(world, lambda d: pam(gower(d))), 3))

    print("\n== CatBoost predicting FAMD k-means labels")
    for world in ("both", "control"):
        acc, shap = surrogate(world)
        print(world, "accuracy", round(acc, 3), shap.head(4).round(3).to_dict())

    print("\n== Palmer penguins: 3 species, k=3")
    P, t = penguins()
    n_, _c = split(P)
    D = gower(P)
    print(P.shape, {"numbers only": round(ari(t, km(StandardScaler().fit_transform(P[n_]), 3)), 3),
                    "one-hot": round(ari(t, km(onehot_matrix(P), 3)), 3), "FAMD 4": round(ari(t, km(famd(P, 4)[0], 3)), 3),
                    "Gower, PAM": round(ari(t, pam(D, 3)), 3),
                    "Gower, average": round(ari(t, AgglomerativeClustering(3, metric="precomputed", linkage="average").fit_predict(D)), 3),
                    "k-prototypes": round(ari(t, kproto(P, 3)[0]), 3), "latent class": round(ari(t, lca(P, 3)[1]), 3)})

    print("\n== scaling, this machine")
    print(scaling().to_string(index=False))

    print("\n== five mistyped values")
    dirty = add_outliers(df)
    clipped = dirty.copy()
    for c_name in num:
        clipped[c_name] = clipped[c_name].clip(*df[c_name].quantile([.01, .99]))
    print({"FAMD clean": round(ari(y, km(famd(df)[0])), 3), "FAMD dirty": round(ari(y, km(famd(dirty)[0])), 3), "FAMD clipped": round(ari(y, km(famd(clipped)[0])), 3),
           "Gower clean": round(ari(y, pam(gower(df))), 3), "Gower dirty": round(ari(y, pam(gower(dirty))), 3)})
    print("Gower numeric spread clean", column_spread(df)[num].round(3).to_dict(), "dirty", column_spread(dirty)[num].round(3).to_dict())
