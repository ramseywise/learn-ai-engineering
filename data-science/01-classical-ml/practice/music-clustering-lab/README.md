# Music clustering lab

Clusters a real music library and puts a light reranker on top: why scaling and feature choice decide what the clusters mean, k-means against a Gaussian mixture with soft assignments, choosing k with BIC and silhouette, whether clusters survive a new seed, how to name them honestly, and what a per-playlist LightGBM score means. It also tests what happens when audio features are replaced by derived proxies, the constraint its source project ([listen-wiseer](https://github.com/ramseywise/listen-wiseer/tree/2f03e7dd906cc2362ce602e1fc44849579c2b732)) describes after Spotify restricted its Audio Features API.

```bash
cd data-science/01-classical-ml/practice/music-clustering-lab
uv run --python 3.12 --with scikit-learn --with lightgbm --with pandas --with pyarrow \
    --with matplotlib --with scipy python music_clustering_lab.py
```

It takes about a minute on a 12-core laptop that was busy with other work (46 to 66 seconds, plus package install on the first run), and prints the runtime to stderr. It writes [`results.json`](results.json) and the figure [`wise-music-clustering-lab-fig1.png`](../../../sources/images/wise-music-clustering-lab-fig1.png). A second run reproduced stdout and `results.json` exactly.

## Data

The first run needs internet. It fetches `corpus_features.parquet` (877 KB) from the project's public repo, [pinned to commit `2f03e7d`](https://raw.githubusercontent.com/ramseywise/listen-wiseer/2f03e7dd906cc2362ce602e1fc44849579c2b732/data/cache/corpus_features.parquet), checks its SHA-256 on every load, and caches it in the gitignored `.cache/`. No data is stored in this repo, and you shouldn't commit the cache.

The file has 114 columns and the lab reads 98 through an allow-list (`SAFE_COLUMNS`). `id`, `track_name`, `release_date`, `first_genre` and `color` never load. All output is aggregated, by cluster or by method. Playlists appear only as anonymous integers, in calculations: they are never printed. Keep it that way if you extend the lab.

## Expected output

The full stdout is in [`expected-output.txt`](expected-output.txt). Package versions are its first line, because exact values can shift with a different scikit-learn or LightGBM. The main results:

| Section | Result |
|---|---|
| Scaling | Raw `duration_ms` holds 99.99999% of the variance: ARI 0.988 with duration-only clusters, 0.072 once scaled |
| Feature space, k=8 | Project's 47 columns explain 3.1% of audio variance (NMI with decade 0.714); nine audio features explain 35.7% |
| Choosing k | Best BIC at k=11, best silhouette at k=2 (k-means) and k=3 (GMM), project uses k=8. BIC on shuffled columns still picks k=7 |
| Soft assignment | Recall 0.925 with a pool of 62%, against k-means hard at 0.536 with 20.4% |
| Naming | 3 of 8 clusters reach median Jaccard 0.75 across seeds |
| Reranker, AUC | Audio 0.870, proxies 0.920, audio plus cluster posteriors 0.869, `pp_*` leak 1.000 |
| Project recipe, AUC | 0.947 as written, 0.948 with train-only centroids, 0.934 without playlist columns |

The discussion is in [`notes/05-unsupervised-learning.md`](../../notes/05-unsupervised-learning.md#case-clustering-a-music-library).
