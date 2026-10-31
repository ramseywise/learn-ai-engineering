---
origin: vendored snapshot: Intro to Machine Learning in Python (kept as practice) + own coursework (Ng ML ex7, ex8)
sources:
  - https://github.com/amueller/introduction_to_ml_with_python
  - ../practice/Intro to Machine Learning in Python/03-unsupervised-learning.ipynb
  - ../Ng's Machine Learning Nbks/ex7/ex7.ipynb
  - ../Ng's Machine Learning Nbks/ex8/ex8.ipynb
  - ../sources/mueller-guido-introduction-to-ml-with-python.pdf
confidence: high
cleaned: 2026-10-31
---
# 5 — Unsupervised Learning

> No labels: transform the data (scaling, PCA, NMF, t-SNE) or group it (k-means, agglomerative, DBSCAN), then judge the result mostly by looking at it. Plus the two Ng exercises that sit next door: Gaussian anomaly detection and collaborative filtering.

---

## Two kinds, one problem

| Kind | Goal | Examples |
|---|---|---|
| Transformations | A new representation: fewer dimensions, more interpretable parts, a 2-D picture | Scaling, PCA, NMF, t-SNE |
| Clustering | Partition the data into groups of similar items | k-means, agglomerative, DBSCAN |

**The challenge:** there is no ground truth, so there is no score that says the model did well. Was the clustering of face photos by pose, lighting or identity? You have to look. Unsupervised methods are therefore used most for *exploration* and as *preprocessing* for a supervised model, where the downstream score does give feedback.

---

## Preprocessing and scaling

| Scaler | Result | Use when |
|---|---|---|
| `StandardScaler` | Mean 0, variance 1 per feature | Default for SVMs, linear models, MLPs, PCA |
| `RobustScaler` | Median and IQR | Outliers present |
| `MinMaxScaler` | Range [0, 1] | Bounded inputs needed (images, some NNs) |
| `Normalizer` | Each *row* to unit length | Only direction matters (text vectors, cosine) |

**Scale train and test with the same fitted scaler.** Fitting a second `MinMaxScaler` on the test set maps it to [0, 1] independently and shifts every point relative to the training data: M&G's plot shows the test points visibly displaced. `fit` on train, `transform` both, inside a pipeline ([03](03-feature-engineering-and-pipelines.md#pipelines)).

Effect on a kernel SVM on breast cancer: 0.63 unscaled, 0.97 with `MinMaxScaler`, 0.96 with `StandardScaler`.

---

## Principal component analysis

PCA rotates the data so the first axis follows the direction of maximum variance, the second the maximum variance orthogonal to it, and so on. Keep the first $k$ to reduce dimensions.

```python
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

X_scaled = StandardScaler().fit_transform(cancer.data)    # PCA is scale-sensitive: scale first
pca = PCA(n_components=2).fit(X_scaled)
X_pca = pca.transform(X_scaled)                            # 569 x 30 -> 569 x 2
pca.components_                     # (2, 30): each row is a direction in feature space
pca.explained_variance_ratio_       # how much variance each component keeps
```

The 2-D projection of breast cancer separates benign and malignant well, so even a linear classifier on two components does reasonably. Components are hard to interpret: each mixes all 30 features with positive and negative weights.

### Eigenfaces: PCA as feature extraction

On Labeled Faces in the Wild (3,023 images, 87×65 px = 5,655 pixels), a 1-nearest-neighbour classifier on raw pixels scores 0.23. After `PCA(n_components=100, whiten=True)` it scores 0.31. Distances between principal-component vectors are a better measure of face similarity than distances between pixels. Reconstructing a face from 10, 50, 100, 500 components shows coarse-to-fine detail.

### From scratch: Ng ex7

```python
# Ng ex7: PCA via SVD of the covariance matrix
def pca(X_norm):
    m = X_norm.shape[0]
    Sigma = X_norm.T @ X_norm / m              # covariance (features already normalised)
    U, S, _ = np.linalg.svd(Sigma)
    return U, S                                 # columns of U = principal directions

def project(X_norm, U, K):  return X_norm @ U[:, :K]
def recover(Z, U, K):       return Z @ U[:, :K].T

# Choose K: smallest K with sum(S[:K]) / sum(S) >= 0.99  ("99% of variance retained")
```

Ex7 applies this to 2-D toy data (projection and reconstruction lines), then to 5,000 32×32 faces reduced to 100 dimensions.

---

## Non-negative matrix factorisation

Like PCA, but components and coefficients are constrained to be **non-negative**. The data must be non-negative too (pixels, word counts, audio spectra). The result is additive parts: a face as "a bit of this lighting plus a bit of this pose."

```python
from sklearn.decomposition import NMF
nmf = NMF(n_components=15, random_state=0).fit(X_train)
X_nmf = nmf.transform(X_test)
```

| | PCA | NMF |
|---|---|---|
| Components | Orthogonal, ordered by variance | Not ordered; all equally important |
| Signs | Mixed | Non-negative |
| Changing `n_components` | First components unchanged | All components change |
| Good for | Compression, decorrelation, visualisation | Interpretable parts; separating additive sources (M&G unmix three signals) |

NMF over word counts is a topic model: see [10](10-topic-models-and-summarization.md).

---

## Manifold learning: t-SNE

t-SNE finds a 2-D layout that preserves *neighbourhoods*: points close in the original space stay close. It is for visualisation only.

```python
from sklearn.manifold import TSNE
digits_tsne = TSNE(random_state=42).fit_transform(digits.data)   # no transform(): can't map new points
```

On the 8×8 digits, PCA's 2-D projection overlaps most classes; t-SNE separates nearly all ten without seeing labels. Rules for reading a t-SNE plot: cluster sizes and distances between clusters mean little; run more than one `perplexity`; never use it as features for a model. UMAP is the faster, more structure-preserving alternative in current practice. [11](11-embeddings-and-similarity.md) uses t-SNE to plot word vectors.

---

## Clustering

### k-means

Alternate two steps until assignments stop changing: assign each point to the nearest centre; move each centre to the mean of its points.

```python
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=3, n_init="auto", random_state=0).fit(X)
kmeans.labels_, kmeans.cluster_centers_
kmeans.predict(X_new)       # new points go to the nearest centre
```

Ng's ex7 version shows there is nothing more to it:

```python
def find_closest(X, centroids):
    d = ((X[:, None, :] - centroids[None, :, :]) ** 2).sum(-1)   # (m, K) squared distances
    return d.argmin(1)

def compute_centroids(X, idx, K):
    return np.array([X[idx == k].mean(0) for k in range(K)])

def run_kmeans(X, K, iters=10, seed=0):
    rng = np.random.default_rng(seed)
    C = X[rng.choice(len(X), K, replace=False)]   # init from random data points
    for _ in range(iters):
        idx = find_closest(X, C)
        C = compute_centroids(X, idx, K)
    return C, idx
```

Ex7 then compresses a 128×128 bird photo by clustering its pixels' RGB values into 16 colours: each pixel stores a 4-bit index instead of 24 bits. That is **vector quantisation**: k-means as a decomposition where each point is represented by one component (its centre). M&G show that with many clusters (more than the input dimensions), k-means can be used as a feature expansion: 10 cluster distances make `two_moons` linearly separable.

**Failure cases.** k-means assumes clusters are round, of similar size and similar density, because it only uses distance to the centre. It fails on stretched clusters, clusters of different density and non-convex shapes (`two_moons`). Results depend on initialisation, hence `n_init`.

### Agglomerative clustering

Start with every point as its own cluster; repeatedly merge the two most similar clusters until `n_clusters` remain.

| `linkage` | Merges the pair that | Tends to give |
|---|---|---|
| `ward` (default) | Least increases total within-cluster variance | Equally sized clusters |
| `average` | Has smallest average pairwise distance | |
| `complete` | Has smallest maximum pairwise distance | |
| `single` | Has smallest minimum distance | Chains; one giant cluster |

No `predict` for new points. The merge history is a tree, drawn as a **dendrogram**:

![Dendrogram of the clustering, with lines indicating splits into two and three clusters](../sources/images/mueller-guido-dendrogram.png)
*Image source: Müller & Guido, Introduction to Machine Learning with Python, companion repo `images/`*

```python
from scipy.cluster.hierarchy import dendrogram, ward
linkage_array = ward(X)
dendrogram(linkage_array)   # long vertical lines = merging very different clusters: a natural cut
```

Sarkar uses the same Ward dendrogram to cluster movies by their descriptions in [10](10-topic-models-and-summarization.md).

### DBSCAN

Density-based: a point with at least `min_samples` neighbours within `eps` is a core point; clusters are connected core points plus their neighbours; everything else is **noise** (label −1).

```python
from sklearn.cluster import DBSCAN
X_scaled = StandardScaler().fit_transform(X)       # eps is a distance: scale first
labels = DBSCAN(eps=0.5, min_samples=5).fit_predict(X_scaled)
```

DBSCAN finds the number of clusters itself, handles arbitrary shapes (it solves `two_moons`), and flags outliers. `eps` is the hard parameter: too small and everything is noise, too large and everything is one cluster. `HDBSCAN` (scikit-learn 1.3+) removes most of that sensitivity.

### Comparing and evaluating

| With ground truth | Without ground truth |
|---|---|
| **Adjusted Rand Index** (ARI), normalised mutual information: 1 = same partition, ~0 = random. Ignore label names | **Silhouette** (−1 to 1): compactness vs separation. Favours round clusters; DBSCAN's correct `two_moons` gets a *worse* silhouette than k-means's wrong one |
| Never use accuracy: cluster 0 vs label 0 is arbitrary | Robustness: do clusters survive noise, different parameters, subsampling? |

In practice, the only reliable check is to inspect the clusters by hand. M&G's LFW case study runs all three algorithms on eigenfaces: DBSCAN finds one big cluster plus noise (the noise is faces with hats, open mouths, odd angles: an outlier detector); k-means with 10 clusters gives blurred "average faces" by pose and lighting; agglomerative gives similar groups with less uniform sizes. None finds identity.

| Algorithm | Specify | New points | Shapes | Noise |
|---|---|---|---|---|
| k-means | `n_clusters` | `predict` | Round, similar size | No |
| Agglomerative | `n_clusters` or distance cut | No | Depends on linkage | No |
| DBSCAN | `eps`, `min_samples` | No | Any | Yes |
| Gaussian mixture | `n_components` | `predict_proba` | Ellipses | Via low likelihood |

---

## Anomaly detection: Ng ex8, part 1

Model normal behaviour with a Gaussian per feature, then flag points with low density. Ex8 does this on server latency and throughput.

```python
def fit_gaussian(X):
    return X.mean(0), X.var(0)

def density(X, mu, var):
    # product of independent per-feature Gaussians (ex8 also does the full multivariate version)
    return np.prod(np.exp(-(X - mu) ** 2 / (2 * var)) / np.sqrt(2 * np.pi * var), axis=1)

def select_threshold(y_val, p_val):
    best_eps, best_f1 = 0, 0
    for eps in np.linspace(p_val.min(), p_val.max(), 1000):
        pred = p_val < eps
        tp = (pred & (y_val == 1)).sum(); fp = (pred & (y_val == 0)).sum(); fn = (~pred & (y_val == 1)).sum()
        if tp == 0: continue
        f1 = 2 * tp / (2 * tp + fp + fn)
        if f1 > best_f1: best_eps, best_f1 = eps, f1
    return best_eps, best_f1
```

Two points worth carrying forward:

- **Train on unlabeled normal data, choose $\varepsilon$ on a labelled validation set by F1.** Accuracy would be useless: anomalies are rare ([04](04-model-evaluation.md#imbalanced-data-and-the-dummy-baseline)).
- **Anomaly detection vs supervised classification.** Use density estimation when positives are very few and future anomalies may look unlike past ones; use a classifier when you have many positives of a stable kind.

scikit-learn equivalents: `EllipticEnvelope` (Gaussian), `IsolationForest`, `LocalOutlierFactor`, `OneClassSVM`.

---

## Recommender systems: Ng ex8, part 2

Collaborative filtering on MovieLens (1,682 movies × 943 users, ratings 1–5, most missing). Learn a feature vector $x^{(i)}$ per movie and a preference vector $\theta^{(j)}$ per user so that $\theta^{(j)} \cdot x^{(i)}$ predicts the rating.

$$J = \tfrac{1}{2}\sum_{(i,j): r(i,j)=1} \left(\theta^{(j)\top} x^{(i)} - y^{(i,j)}\right)^2 + \tfrac{\lambda}{2}\lVert\Theta\rVert^2 + \tfrac{\lambda}{2}\lVert X\rVert^2$$

```python
def cofi_cost(X, Theta, Y, R, lam):
    E = (X @ Theta.T - Y) * R                      # only rated entries count
    J = 0.5 * (E ** 2).sum() + lam / 2 * ((Theta ** 2).sum() + (X ** 2).sum())
    X_grad = E @ Theta + lam * X
    Theta_grad = E.T @ X + lam * Theta
    return J, X_grad, Theta_grad
```

Ex8 checks the gradient numerically, adds a new user's ratings, **mean-normalises** each movie's ratings (otherwise a user with no ratings gets predicted 0 for everything), and optimises with `scipy.optimize.fmin_cg`. This is low-rank matrix factorisation: the same idea as PCA and NMF, fitted only on observed entries. It is the ancestor of the embedding models in [11](11-embeddings-and-similarity.md): $x^{(i)}$ is a learned movie embedding.

---

## Practice

| Notebook | Covers | Runs |
|---|---|---|
| [`03-unsupervised-learning.ipynb`](../practice/Intro%20to%20Machine%20Learning%20in%20Python/03-unsupervised-learning.ipynb) | Scaling, PCA, eigenfaces, NMF, t-SNE, k-means, agglomerative, DBSCAN, evaluation | Needs internet once: `fetch_lfw_people` downloads ~200 MB; otherwise offline with `scikit-learn>=1.4`, `mglearn` |
| [`ex7.ipynb`](../Ng's%20Machine%20Learning%20Nbks/ex7/ex7.ipynb) | k-means from scratch, image compression, PCA, eigenfaces | Legacy: Python 2.7; `scipy.misc.imread`/`toimage` removed in SciPy 1.2 (use `imageio` / `PIL`) |
| [`ex8.ipynb`](../Ng's%20Machine%20Learning%20Nbks/ex8/ex8.ipynb) | Gaussian anomaly detection, collaborative filtering | Legacy: Python 2.7 kernel; data in `ex8/data/` |

---

→ Next: [06-ensembles.md](06-ensembles.md) — combine many trees: bagging, random forests, gradient boosting.
