# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy"]
# ///
"""Page retrieval on a synthetic corpus for notes/03: text summaries, one vector per page, late interaction and pooling.

Run from this folder (under a minute on a laptop CPU, downloads no data, needs no model):
    uv run multimodal_rag_lab.py

Everything is generated from a seed: no image is rendered and no encoder runs. A page is a set of patch vectors, mostly
background around the page's subject, plus a few sharp patches for the one chart that holds the answer. The assumptions
are constants below and printed with the results. The fixture shows how each design behaves when answers sit in small
regions, and it isn't evidence about any real encoder or dataset. The published comparisons are in the note.
"""
# %%
import time

import numpy as np

SEED = 7
N_PAGES, N_QUERIES = 200, 120
PATCHES, DIM, SHARP_PATCHES, QUERY_TOKENS = 1030, 128, 4, 12  # patch count and dim as in the note's ColPali setup
N_SUBJECTS, N_FACTS = 12, 600     # pages about the same subject look alike, which is what makes retrieval hard
TEXT_SHARE = 0.4                  # share of chart facts that the page's text or caption also states
DECOY_FACTS, DECOY_PATCHES = 30, 4  # every page also shows other charts, so a page's mean is crowded by unrelated facts
QUERY_NOISE, PATCH_NOISE = 2.0, 1.2 # noise over signal per vector: a query only loosely matches the patch it wants
BYTES_PER_VALUE = 2               # half-precision storage, as in the note's index_gb
POOL_FACTOR = 3
rng = np.random.default_rng(SEED)


def unit(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


# %% Fixture
subjects = unit(rng.normal(size=(N_SUBJECTS, DIM)))
facts = unit(rng.normal(size=(N_FACTS, DIM)))
page_subject = rng.integers(N_SUBJECTS, size=N_PAGES)
page_fact = rng.permutation(N_FACTS)[:N_PAGES]        # each page holds one fact that nothing else holds
in_text = rng.random(N_PAGES) < TEXT_SHARE


def make_page(i):
    background = unit(subjects[page_subject[i]] + 0.9 * rng.normal(size=(PATCHES, DIM)) / np.sqrt(DIM))
    def sharp(fact, n):
        return unit(fact + PATCH_NOISE * rng.normal(size=(n, DIM)) / np.sqrt(DIM))

    background[:SHARP_PATCHES] = sharp(facts[page_fact[i]], SHARP_PATCHES)
    others = rng.choice(np.delete(np.arange(N_FACTS), page_fact[i]), DECOY_FACTS, replace=False)
    for j, f in enumerate(others):
        start = SHARP_PATCHES + j * DECOY_PATCHES
        background[start:start + DECOY_PATCHES] = sharp(facts[f], DECOY_PATCHES)
    return rng.permutation(background).astype(np.float32)


pages = [make_page(i) for i in range(N_PAGES)]

targets = rng.integers(N_PAGES, size=N_QUERIES)


def make_query(i):
    """Most tokens name the fact, and the rest are general words about the subject."""
    t = targets[i]
    n_fact = QUERY_TOKENS // 2
    fact_tokens = facts[page_fact[t]] + QUERY_NOISE * rng.normal(size=(n_fact, DIM)) / np.sqrt(DIM)
    subject_tokens = subjects[page_subject[t]] + QUERY_NOISE * rng.normal(size=(QUERY_TOKENS - n_fact, DIM)) / np.sqrt(DIM)
    return unit(np.vstack([fact_tokens, subject_tokens])).astype(np.float32)


queries = [make_query(i) for i in range(N_QUERIES)]


# %% Pooling
def pool_adjacent(patches, factor):
    """Average patches in order. Cheap, and it blends a sharp patch with whatever sits beside it."""
    n = len(patches) // factor
    return unit(patches[:n * factor].reshape(n, factor, DIM).mean(axis=1))


def pool_clustered(patches, factor, iters=4):
    """k-means over a page's patches, keeping one centroid each. Similar patches merge and rare ones keep a centroid."""
    k = len(patches) // factor
    local = np.random.default_rng(0)
    centres = patches[local.choice(len(patches), k, replace=False)]
    for _ in range(iters):
        assign = (patches @ centres.T).argmax(axis=1)
        sums = np.zeros_like(centres)
        np.add.at(sums, assign, patches)
        counts = np.bincount(assign, minlength=k)
        worst = np.argsort((patches * centres[assign]).sum(axis=1))    # reseed empty clusters on the worst-fit patches
        sums[counts == 0] = patches[worst[: int((counts == 0).sum())]]
        centres = unit(sums)
    return centres


# %% Scorers
single = unit(np.stack([p.mean(axis=0) for p in pages]))


def score_single(q):
    return single @ unit(q.mean(axis=0))


def score_maxsim(q, index):
    return np.array([(q @ p.T).max(axis=1).sum() for p in index])


def score_text(i):
    """A text index finds the page only when the text states the fact, and otherwise matches on subject alone."""
    t = targets[i]
    tie_break = rng.random(N_PAGES) * 1e-3
    return (page_subject == page_subject[t]).astype(float) + 2.0 * ((np.arange(N_PAGES) == t) & in_text[t]) + tie_break


def rrf(*scores, k=60):
    total = np.zeros(N_PAGES)
    for s in scores:
        ranks = np.empty(N_PAGES, dtype=int)
        ranks[np.argsort(-s)] = np.arange(1, N_PAGES + 1)
        total += 1 / (k + ranks)
    return total


def two_stage(q, keep=20):
    """Single-vector first stage, then MaxSim only on the shortlist, which is cheap enough to serve."""
    s = score_single(q)
    shortlist = np.argsort(-s)[:keep]
    out = s - 10.0                                 # anything outside the shortlist ranks below it
    out[shortlist] = score_maxsim(q, [pages[j] for j in shortlist])
    return out


# %% Run
t0 = time.perf_counter()
pooled_adjacent = [pool_adjacent(p, POOL_FACTOR) for p in pages]
pooled_clustered = [pool_clustered(p, POOL_FACTOR) for p in pages]
pool_secs = time.perf_counter() - t0

patch_bytes = PATCHES * DIM * BYTES_PER_VALUE
pooled_bytes = (PATCHES // POOL_FACTOR) * DIM * BYTES_PER_VALUE
single_bytes = DIM * BYTES_PER_VALUE
designs = {
    "text summaries only": (lambda i, q: score_text(i), 512),
    "one vector per page": (lambda i, q: score_single(q), single_bytes),
    "hybrid: text + one vector (RRF)": (lambda i, q: rrf(score_text(i), score_single(q)), 512 + single_bytes),
    "MaxSim, every patch": (lambda i, q: score_maxsim(q, pages), patch_bytes),
    f"MaxSim, adjacent pooling /{POOL_FACTOR}": (lambda i, q: score_maxsim(q, pooled_adjacent), pooled_bytes),
    f"MaxSim, clustered pooling /{POOL_FACTOR}": (lambda i, q: score_maxsim(q, pooled_clustered), pooled_bytes),
    "one vector, MaxSim rerank top 20": (lambda i, q: two_stage(q), patch_bytes + single_bytes),
}

print(f"{N_PAGES} synthetic pages, {PATCHES} patches x {DIM} dims, {SHARP_PATCHES} sharp patches hold each answer, {DECOY_FACTS} other charts per page,")
print(f"{N_QUERIES} queries of {QUERY_TOKENS} tokens, {TEXT_SHARE:.0%} of facts also in the page text, seed {SEED}\n")
print(f"{'design':38}{'recall@5':>9}{'MRR':>7}{'ms/query':>10}{'KB/page':>9}{'GB at 1M pages':>16}")
for name, (fn, size) in designs.items():
    hits, rr = 0, 0.0
    start = time.perf_counter()
    for i, q in enumerate(queries):
        rank = int(np.where(np.argsort(-fn(i, q)) == targets[i])[0][0]) + 1
        hits += rank <= 5
        rr += 1 / rank
    ms = 1000 * (time.perf_counter() - start) / N_QUERIES
    print(f"{name:38}{hits / N_QUERIES:9.2f}{rr / N_QUERIES:7.2f}{ms:10.2f}{size / 1024:9.1f}{size * 1e6 / 1e9:16,.1f}")
print(f"\npooling all pages took {pool_secs:.1f}s; ms/query is brute force in numpy on this machine, with no index")
