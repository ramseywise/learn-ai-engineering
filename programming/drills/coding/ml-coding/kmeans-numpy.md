---
title: "K-means in NumPy"
track: coding
topic: ml-coding
difficulty: medium
timebox_min: 25
concepts: [ml-coding]
source: https://github.com/alexeygrigorev/ai-engineering-gym
---
## Prompt

Implement k-means clustering from scratch in NumPy (Lloyd's algorithm). Given a
data matrix X and k, return cluster assignments and centroids.

## Starter

Blank file in `programming/drills/coding/scratch/`. NumPy allowed unless the prompt says otherwise.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

It's two alternating steps: assign each point to its nearest centroid, then recompute each centroid as the mean of its members. Repeat until assignments stabilize.

</details>

<details><summary>Hint 2</summary>

Vectorize the assignment by building an (n_points, k) squared-distance matrix and taking argmin along axis 1. Avoid a Python loop over points.

</details>

<details><summary>Hint 3</summary>

K-means only finds a local optimum, so seeding matters. Mention k-means++ and multiple restarts, and handle the empty-cluster case by reseeding a centroid.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

K-means (Lloyd's algorithm) alternates two steps until convergence. Assignment: put each point in the cluster whose centroid is nearest by squared Euclidean distance. Update: move each centroid to the mean of the points assigned to it. Repeat until assignments stop changing (or centroids move less than a tolerance, or you hit max_iter). The vectorized assignment computes an (n_points, k) distance matrix and takes argmin along the centroid axis, with no per-point loop. Interviewers probe several details here. Initialization: random points as centroids is fine to start, though k-means++ gives better seeds and fewer bad local minima. The objective it minimizes is the within-cluster sum of squares (inertia). It only reaches a local optimum, so you run several restarts and keep the best. The empty-cluster edge case: reseed a centroid to the farthest point if a cluster loses all members.

```python
def kmeans(X, k, max_iter=100, tol=1e-4):
    centroids = X[random_choice(len(X), k, replace=False)]   # k-means++ is better
    for _ in range(max_iter):
        # assignment: (n, k) squared distances, then argmin
        d = ((X[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
        labels = d.argmin(axis=1)
        # update: mean of assigned points (reseed empty clusters)
        new_centroids = stack([X[labels == j].mean(axis=0) if any(labels == j)
                                else X[random_index()] for j in range(k)])
        if norm(new_centroids - centroids) < tol: break
        centroids = new_centroids
    return labels, centroids
```

**Complexity** — time `O(iters * n * k * d)` for n points, k clusters, d dimensions; space `O(n*k)` for the distance matrix (or `O(n)` if you loop over clusters)

</details>

## Notes

Follow-ups an interviewer may push on:

- How does k-means++ initialization work and why does it help?
- How would you choose k (elbow method, silhouette score)?
- Why does k-means assume roughly spherical, equal-size clusters, and when does that break?
- How would you scale this to data that doesn't fit in memory (minibatch k-means)?

Sources:

- [Mustafa Murat ARAT — Implementing K-means Clustering from Scratch in Python](https://mmuratarat.github.io/2019-07-23/kmeans_from_scratch)
- [Towards AI — K-Means Clustering from Scratch](https://medium.com/towards-artificial-intelligence/k-means-clustering-from-scratch-4e357ac4716f)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/aieng-kmeans-numpy.yaml`.
