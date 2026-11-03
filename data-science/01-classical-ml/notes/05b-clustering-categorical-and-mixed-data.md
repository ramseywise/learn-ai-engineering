---
origin: synthesis
sources:
  - ../practice/mixed_clustering.py
  - https://www.numdam.org/item/RSA_2004__52_4_93_0.pdf
  - https://arxiv.org/abs/1301.4797
  - https://personal.utdallas.edu/~herve/Abdi-MCA2007-pretty.pdf
  - https://helios2.mi.parisdescartes.fr/~lerb/rouanet/publications/MCABREVIARY.pdf
  - https://personal.utdallas.edu/~herve/abdi-WiresCS-mfa-2013.pdf
  - https://www.jstatsoft.org/article/view/v091i10
  - https://repub.eur.nl/pub/77010/EI2014-24.pdf
  - https://repub.eur.nl/pub/93479
  - https://ideas.repec.org/a/bla/jorssc/v32y1983i3p267-275.html
  - https://doi.org/10.2307/2528823
  - https://arxiv.org/abs/2008.05171
  - https://python-kmedoids.readthedocs.io/en/latest/
  - https://cse.hkust.edu.hk/~qyang/537/Papers/huang98extensions.pdf
  - https://raw.githubusercontent.com/nicodv/kmodes/master/kmodes/kprototypes.py
  - https://www.osti.gov/biblio/1459931
  - https://www.jstatsoft.org/article/view/v083i13
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC7892576/
  - https://arxiv.org/abs/2203.16287
  - https://www.statmodel.com/download/LCA_tech11_nylund_v83.pdf
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC12494633/
  - https://maxhalford.github.io/prince/mca/
  - https://github.com/Labo-Lacourse/stepmix
  - https://scikit-learn.org/stable/modules/generated/sklearn.cluster.HDBSCAN.html
  - https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html
  - https://scikit-learn.org/stable/modules/generated/sklearn.metrics.calinski_harabasz_score.html
  - https://scikit-learn.org/stable/modules/generated/sklearn.metrics.davies_bouldin_score.html
  - https://github.com/husson/FactoMineR/blob/master/man/MCA.Rd
  - https://pypi.org/project/kmedoids/
  - https://allisonhorst.github.io/palmerpenguins/
  - https://doi.org/10.1016/j.patcog.2012.07.021
  - https://arxiv.org/abs/2104.00629
  - https://arxiv.org/abs/1604.06737
  - https://arxiv.org/abs/0902.2206
  - https://arxiv.org/abs/1706.09516
  - https://arxiv.org/abs/1705.07874
  - https://arxiv.org/abs/2012.02936
  - https://arxiv.org/abs/2103.01281
  - https://arxiv.org/abs/2308.01475
  - https://arxiv.org/abs/2605.08242
confidence: medium
cleaned: 2026-11-02
---
# Clustering categorical and mixed data

Tallybook's marketing lead wants customer segments. The table has invoice counts and revenue, and also plan, sign-up channel, industry, company size and two yes-or-no columns. An analyst one-hot encodes the lot, runs k-means, gets four tidy groups and a decent silhouette. Is it a good answer? On the generated tables below, that recipe finds the groups when numbers and categories both separate them (adjusted Rand index, ARI, of 0.879). When only the categories hold the groups, it scores 0.003, which is nothing. It returned four tidy groups all the same.

Tallybook is the course's fictional invoicing company. This chapter picks up where [note 05](05-unsupervised-learning.md#clustering) stops: k-means, agglomerative clustering, DBSCAN, ARI and silhouette are taught there. Here the question is what to feed them when columns aren't all numbers, and how to tell if the result means anything.

**In plain words.** Clustering needs a sense of "how far apart are these two customers?" For numbers that's simple. "Retail versus construction" has no natural distance, so every method here invents one, and that invented distance decides whose columns get heard. You get three families: turn the table into numbers (MCA, FAMD), define a distance directly (Gower), or assume each group is a recipe that generates customers (latent class).

Blocks run top to bottom from this `notes/` folder, and they need the packages at the top of [`mixed_clustering.py`](../practice/mixed_clustering.py). Every customer table is generated with a fixed seed, so no number here measures a real market. `uv run mixed_clustering.py` from `practice/` reprints them all in a few minutes.

---

## The test bench

The generator makes four groups of 40%, 30%, 20% and 10%, across 1,200 customers, with 5 numeric and 6 categorical columns. It has the same table in several worlds, so we can ask which method hears which columns:

| World | Where the groups live |
|---|---|
| `both` | Numbers and categories |
| `categorical` | Only categories; numbers are noise |
| `numeric` | Only numbers; categories are noise |
| `control` | Each column shuffled alone, so there are no groups |
| `correlated` | `both`, plus a business-size factor inside every group that moves three numbers and `size` together |

```python
import sys
sys.path.insert(0, "../practice")
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import mixed_clustering as lab
from sklearn.metrics import adjusted_rand_score as ari

df, y = lab.make_customers("both", seed=0)
num, cat = lab.split(df)
print(df.iloc[:3, [0, 3, 5, 6, 7]].round(2).to_string())
```

```text
   log_invoices  logins    plan    channel    industry
0         -0.30   -2.69  plan_1  channel_4  industry_4
1          0.94    2.90  plan_3  channel_3  industry_4
2          0.11    2.39  plan_3  channel_3  industry_8
```

## Why one-hot goes deaf

K-means minimises squared distance, so a column's say is roughly its variance. A z-scored number has variance 1. A dummy column for a category with share $p$ has variance $p(1-p)$, at most 0.25.

```python
blocks, n_dummies = lab.block_variance(df)
for name, (numeric, categorical) in blocks.items():
    print(f"{name:8} total variance: numbers {numeric:.1f}, {n_dummies} category dummies {categorical:.1f}")
```

```text
one-hot  total variance: numbers 5.0, 26 category dummies 3.4
FAMD     total variance: numbers 5.0, 26 category dummies 20.0
```

Six categorical columns with 26 levels between them hold 3.4 of variance against 5.0 for five numbers. In `categorical` all of that 5.0 is noise, which is what buries the groups: k-means on the dummies alone scores 0.319 there (mean of 5 seeds), and adding the numbers takes it to 0.003. Pagès, whose paper the next section uses, rejects even a normed principal component analysis (PCA) on dummies for a related reason: it [favours high-count levels](https://www.numdam.org/item/RSA_2004__52_4_93_0.pdf).

## FAMD and MCA: turn categories into coordinates

**Factor analysis of mixed data (FAMD)** is a PCA after one change of coding: z-score the numbers, and divide each centred dummy by $\sqrt{p}$. Rare levels are stretched and common ones are not. In [Pagès's 2004 paper](https://www.numdam.org/item/RSA_2004__52_4_93_0.pdf) (*Revue de statistique appliquée*), which credits the method to Escofier in 1979, the balance this buys is specific: a numeric column and a categorical column can each contribute at most 1 of inertia (variance, for our purposes) to any one axis. The total isn't balanced, because a category with $m$ levels holds $m-1$ in all. Each axis maximises the sum of squared correlations with the numbers and correlation ratios $\eta^2$ with the categories. A correlation ratio is the share of an axis coordinate's variance explained by the mean coordinate of each level.

An axis's eigenvalue is the inertia it captures, the raw quantity behind note 05's `explained_variance_ratio_`. That criterion gives us a check: eigenvalues from our own coding should equal it, and they should match the [`prince`](https://maxhalford.github.io/prince/mca/) package:

```python
import prince

Z, eigenvalues = lab.famd(df)
model = prince.FAMD(n_components=8, random_state=0, categorical_columns=cat).fit(df)
R = model.row_coordinates(df).to_numpy()
print("lab eigenvalues", eigenvalues[:3].round(3))
print("criterion      ", np.round([lab.famd_criterion(Z[:, i], df) for i in range(3)], 3))
print("prince         ", np.round(model.eigenvalues_[:3], 3))
print("ARI lab", round(ari(y, lab.km(Z)), 3), "prince", round(ari(y, lab.km(R)), 3))
```

```text
lab eigenvalues [3.271 2.127 1.467]
criterion       [3.271 2.127 1.467]
prince          [3.271 2.126 1.466]
ARI lab 0.88 prince 0.877
```

Two `prince` 0.23.1 traps cost real time. Without `categorical_columns`, every non-float column counts as categorical, so an integer `age` becomes 60 levels. And `row_coordinates` recomputes the category shares from whatever rows you hand it, so a small batch of new customers lands somewhere else:

```python
five = model.row_coordinates(df.iloc[:5]).to_numpy()
print("row 2 in the full table", R[2, :2].round(3))
print("row 2 in a batch of 5  ", five[2, :2].round(3))
```

```text
row 2 in the full table [-0.673 -0.819]
row 2 in a batch of 5   [-0.612 -0.445]
```

Score new customers with shares saved at fit time, or score them inside the full table.

How many axes? I found no rule worth quoting, so try several and see whether the groups move. The 8 used below is a round number, not a result:

```python
for axes in (2, 4, 8, 12, 20):
    print(f"{axes:2} axes  ARI {ari(y, lab.km(lab.famd(df, axes)[0])):.3f}")
```

```text
 2 axes  ARI 0.786
 4 axes  ARI 0.888
 8 axes  ARI 0.880
12 axes  ARI 0.880
20 axes  ARI 0.752
```

Four to twelve axes barely differ at seed 0; 2 and 20 lose ground. That's one table, so run the sweep on yours.

**Multiple correspondence analysis (MCA)** is the version for categories alone. It runs correspondence analysis on the dummy table: an SVD like PCA's, on a table of counts, after weighting rows and columns by their totals. Its raw percentages mislead. Coding one column as several dummies inflates the total, so [the first axis is understated](https://personal.utdallas.edu/~herve/Abdi-MCA2007-pretty.pdf) (Abdi and Valentin, encyclopedia chapter, 2007). Axes with eigenvalue at or below $1/J$, for $J$ columns, only code those extra dimensions. Benzécri's correction drops them and replaces each remaining eigenvalue $\lambda$ with $\left[\frac{J}{J-1}(\lambda - \frac{1}{J})\right]^2$. The same source calls its percentages optimistic and gives Greenacre's alternative, which `prince` also offers.

```python
c = df[cat]
eig, *_ = lab.mca_eigenvalues(c)
corrected = lab.benzecri(eig, c.shape[1])
print("eigenvalues ", eig[:4].round(3), " 1/J =", round(1 / c.shape[1], 3))
print("raw %       ", (100 * eig / eig.sum())[:4].round(1))
print("Benzecri %  ", (100 * corrected / corrected.sum())[:4].round(1))
```

```text
eigenvalues  [0.324 0.234 0.224 0.193]  1/J = 0.167
raw %        [9.7 7.  6.7 5.8]
Benzecri %   [73.4 13.6  9.7  2. ]
```

A scree plot, which draws eigenvalue against axis number, made from the raw column says the first axis holds a tenth of the table. The corrected one says about three quarters of the real structure. Don't choose how many axes to keep from the raw column.

**Rare levels pull hard.** Dividing by $\sqrt{p}$ makes a level count $1/p$ in squared distance, and that's deliberate. [Audigier, Husson and Josse](https://arxiv.org/abs/1301.4797) (*Advances in Data Analysis and Classification*) note that the same weighting in FAMD gives rare categories more influence, and MCA behaves likewise here. Give 8 of the 1,200 customers a new channel and a new plan, and those two levels each supply 48.1% of axis 1's inertia. The new axis 1 correlates at 0.134 with the old one. The k-means ARI on six MCA axes (categories of `both`, seed 0) barely moves (0.501 from 0.520), so the damage shows up in the plot and in the story you'd tell about axis 1. [A note among Rouanet's publications](https://helios2.mi.parisdescartes.fr/~lerb/rouanet/publications/MCABREVIARY.pdf) says that levels under, "say", 5% need pooling or making passive (left out of the fit, then placed on the finished axes). It gives no evidence for the figure. In R, [FactoMineR's `level.ventil`](https://github.com/husson/FactoMineR/blob/master/man/MCA.Rd) does the pooling automatically, though it's off by default.

**Grouped columns.** If some of your columns form blocks, say 20 product-usage columns beside 3 billing ones, [multiple factor analysis (MFA)](https://personal.utdallas.edu/~herve/abdi-WiresCS-mfa-2013.pdf) (Abdi, Williams and Valentin, *WIREs Computational Statistics*, 2013) divides each block by its first singular value, so that no block dominates just by being large. FAMD is the [special case where each column is its own block](https://www.numdam.org/item/RSA_2004__52_4_93_0.pdf).

## Reducing first can hide the groups

Running a reduction and then clustering its output is called **tandem analysis**. Chang [proved in 1983](https://ideas.repec.org/a/bla/jorssc/v32y1983i3p267-275.html) (*JRSS Series C*, abstract read) that for a mixture of two normals the top components need not hold the separation. The reason is simple: PCA ranks by variance and has no idea what you're looking for. Three loud correlated columns beside two quiet columns holding three groups, with the ARI of k-means on each input, mean of 5 seeds:

```python
table, ratios = lab.tandem_table()
print(table.to_string())
print("variance ratios", ratios)
```

```text
all 5 columns          0.230
the 2 quiet columns    0.964
PCA 1                  0.002
PCA 2                  0.142
PCA 4                  0.234
variance ratios [0.562 0.201 0.198 0.02  0.019]
```

Picking axes by the elbow, the point where the scree plot flattens, keeps one, at 56% of the variance, and that axis has no groups in it at all. Keep four and you only tie with the raw columns (0.23), where the loud block also drowns the groups. Only the two quiet columns on their own do well (0.964). Column choice beat the reduction here, and no reduction method can make that choice for you.

The evidence for categorical data is more mixed than the warning suggests. Joint methods that fit the reduction and the clusters together exist: reduced k-means, factorial k-means, MCA k-means and cluster correspondence analysis, [all in R's `clustrd`](https://www.jstatsoft.org/article/view/v091i10) (Markos and colleagues, *Journal of Statistical Software*, 2019). That paper's review reports that reduced and factorial k-means, on continuous data, recover well-separated clusters masked by random variables where tandem fails, on evidence I know only through this summary. [A 2014 working paper](https://repub.eur.nl/pub/77010/EI2014-24.pdf) with uniform noise columns found tandem about level with the joint methods (ARI 0.85 against 0.82 to 0.86, for 20 variables of 5 categories plus 8 noise columns, 4 balanced groups, n = 1,000). [Its published 2017 abstract](https://repub.eur.nl/pub/93479) (*Psychometrika*) reports tandem doing worse once unrelated variables are added; I couldn't read those tables, so don't treat one as settling the other. In practice: keep more axes than the elbow says, and rerun with a joint method if the columns may include noise.

## Gower: define the distance directly

[Gower's 1971 coefficient](https://doi.org/10.2307/2528823) (*Biometrics*) skips coordinates. For each pair of customers, each number scores absolute difference over the column's range, each category scores 0 for a match and 1 otherwise, and the distance is the average. A column missing for either customer just drops out of that pair's average, which is the method's most useful property and one the coordinate methods don't have. Adding weights is easy, Gower writes, but "how to decide on a rational set of weights is more difficult".

There are no coordinates, so k-means is out. You need a method that takes a distance matrix: **PAM** (k-medoids), whose centres are real customers, or agglomerative clustering with average link. HDBSCAN [also accepts precomputed distances](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.HDBSCAN.html), but I found no benchmark of the pairing.

Equal weights don't mean equal say:

```python
print(lab.column_spread(df).round(3).to_string())
print("Gower, PAM, seed 0, ARI", round(ari(y, lab.pam(lab.gower(df))), 3))
```

```text
log_invoices     0.148
log_revenue      0.131
tenure           0.144
logins           0.164
overdue_share    0.152
plan             0.474
channel          0.446
industry         0.341
size             0.484
payroll          0.445
mobile           0.500
Gower, PAM, seed 0, ARI 0.263
```

That's the standard deviation of each column's term over all pairs. A mismatch is 0 or 1, while a range-scaled difference mostly sits near 0.2, so the categories move the distance about three times as much as the numbers. Scores follow. Over 5 seeds, Gower with PAM gets 0.289 in `both` and 0.024 in `numeric`. Using the numeric columns alone it gets 0.608 in `both`, so those columns held plenty that the mix drowned out. Weighting numbers by 5 lifts `both` to 0.713. At seed 0, `numeric` rises from 0.018 to 0.466 while `categorical` slips from 0.184 to 0.141. Nothing tells you the weight in advance. Replacing each number with its rank before computing Gower gets 0.387 in `both`.

Medoids are practical to explain ("segment 2 looks like this customer"), but the matrix is the bill:

| Customers | Gower matrix | PAM | FAMD + k-means, all in | Matrix memory |
|---:|---:|---:|---:|---:|
| 1,000 | 0.012 s | 0.005 s | 0.021 s | 0.008 GB |
| 2,000 | 0.061 s | 0.032 s | 0.036 s | 0.032 GB |
| 4,000 | 0.192 s | 0.204 s | 0.051 s | 0.128 GB |
| 8,000 | 0.954 s | 0.637 s | 0.060 s | 0.512 GB |

That's one run on one laptop, on `float64`. Memory is $8n^2$ bytes, so 100,000 customers would need 80 GB (my arithmetic). [Schubert and Rousseeuw](https://arxiv.org/abs/2008.05171) (*Information Systems*, 2021), who made PAM far faster with FasterPAM, reach the same view: the distance matrix is the main remaining scaling problem. Their CLARA variant clusters samples, and they say it usually gives worse results. Without it, cluster a sample and assign the rest to the nearest medoid. The [`kmedoids` package](https://python-kmedoids.readthedocs.io/en/latest/) used here is GPL-3.0-or-later ([PyPI](https://pypi.org/project/kmedoids/), read 2026-11-02), which matters if you copy it into a product. scikit-learn has no Gower distance, so the lab writes its own in a dozen lines.

For a picture of a Gower matrix, scikit-learn's multidimensional scaling (MDS) takes precomputed distances. Treat it as a picture, under the [warnings in note 05](05-unsupervised-learning.md#manifold-learning-t-sne).

## k-modes and k-prototypes: a shared loss

**k-modes** is k-means with the mean replaced by the most common level and squared distance replaced by a count of mismatches. **k-prototypes** adds the two up: $\sum (x_j - q_j)^2 + \gamma \sum \mathbb{1}[x_j \neq q_j]$ for customer $x$ and cluster centre $q$, where the first sum runs over numeric columns and the second over categorical ones, with a single weight $\gamma$ [meant to stop either type being favoured](https://cse.hkust.edu.hk/~qyang/537/Papers/huang98extensions.pdf) (Huang, *Data Mining and Knowledge Discovery*, 1998). Huang suggests the average numeric standard deviation as a guide and immediately says it's too early to call that a rule. The `kmodes` package's default [is half that](https://raw.githubusercontent.com/nicodv/kmodes/master/kmodes/kprototypes.py), a choice I can't find in Huang.

```python
labels, gamma = lab.kproto(df)
print("default gamma", round(gamma, 3), "ARI", round(ari(y, labels), 3))
```

```text
default gamma 0.5 ARI 0.75
```

Here is the same fit across values of $\gamma$ and across worlds:

| $\gamma$ | `both` | `categorical` | `numeric` |
|---:|---:|---:|---:|
| 0.5 (package default on z-scores) | 0.750 | 0.004 | 0.700 |
| 1 | 0.752 | 0.024 | 0.662 |
| 2 | 0.675 | 0.165 | 0.511 |
| 4 | 0.535 | 0.271 | 0.215 |
| 8 | 0.357 | 0.220 | 0.037 |

Seed 0. Each world wants a different $\gamma$, and you don't know which world you're in. Treat it as a sensitivity check and report how much the groups move. [Foss, Markatou and Ray](https://www.osti.gov/biblio/1459931) (*International Statistical Review*) make this the central failure of the field, saying that fixed weights, dummy coding and Gower can't reliably balance the two types. They also propose a competing semiparametric method, KAMILA ([R package `kamila`](https://www.jstatsoft.org/article/view/v083i13)), so read it with that in mind.

## Latent class: a model of how customers arise

Every method so far minimises a distance. **Latent class analysis (LCA)** instead assumes a recipe: each customer belongs to a hidden class, each class has its own mean for each number and its own level shares for each category, and within a class the columns are independent. That last assumption is called **local independence**.

The fit is expectation-maximisation (EM), the same loop as the [Gaussian mixture in note 05](05-unsupervised-learning.md#clustering), and easy to say in words. Start with guessed recipes. **E step:** for each customer, compute the probability of each class given their row. **M step:** re-estimate each recipe using those probabilities as weights. Repeat until it settles, from several random starts because it can stop at a poor optimum.

Because it's a likelihood model, you can compare numbers of classes with the Bayesian information criterion (BIC), including one class, which means no groups:

```python
def lca_bic(d, k):
    model, _, data = lab.lca(d, k)
    return round(model.bic(data))

for world in ("both", "control", "correlated"):
    d, _ = lab.make_customers(world, seed=0)
    bic = [lca_bic(d, k) for k in range(1, 8)]
    print(f"{world:11}", bic, " lowest at k =", int(np.argmin(bic)) + 1)
```

```text
both        [33095, 30979, 29779, 29254, 29416, 29586, 29746]  lowest at k = 4
control     [33095, 33255, 33241, 33417, 33568, 33739, 33905]  lowest at k = 1
correlated  [34071, 32525, 31642, 31266, 30939, 30799, 30632]  lowest at k = 7
```

This is the only method here where "there are no groups" is a possible answer, and it gave that answer on the control. Don't over-read that. This control is built from normal numbers, the model's home ground, and [note 05](05-unsupervised-learning.md#choosing-k-the-criteria-disagree) saw a Gaussian mixture's BIC pick $k=7$ on shuffled skewed columns. I didn't run latent class on skewed columns. On `correlated` it fails the way you'd predict. A size factor inside each group breaks local independence, so the model invents classes to explain the correlation, and BIC keeps falling past 7. A class count from BIC is only as good as that assumption. [Nylund and colleagues](https://www.statmodel.com/download/LCA_tech11_nylund_v83.pdf) (*Structural Equation Modeling*, 2007) found BIC the best information criterion across their simulations and a bootstrap likelihood ratio test more consistent still, while stating that mixed continuous and categorical outcomes need further study. [A 2025 review of latent class analysis in psychology](https://pmc.ncbi.nlm.nih.gov/articles/PMC12494633/) (*Behavior Research Methods*) reports BIC underestimating classes below about 300 cases, and common guidance asking for 300 to 500. The code here uses [StepMix](https://github.com/Labo-Lacourse/stepmix), a Python package that follows the scikit-learn API.

## The benchmark

![Grouped bars of ARI for seven methods in three worlds. Latent class is highest in each. FAMD with k-means is second in the both and categorical worlds and the only distance method that hears categories. One-hot and k-prototypes score near zero in the categorical world. Gower with PAM stays below 0.3 everywhere.](../../sources/images/classical-mixed-benchmark.png)

| ARI, 1,200 customers, mean (sd) of 5 seeds | `both` | `categorical` | `numeric` | `correlated` |
|---|---:|---:|---:|---:|
| One-hot, k-means | 0.879 (0.026) | 0.003 (0.002) | 0.726 (0.014) | 0.336 |
| One-hot, PCA 8, k-means | 0.869 (0.025) | 0.003 (0.002) | 0.724 (0.007) | 0.334 |
| FAMD 8, k-means | 0.890 (0.014) | 0.542 (0.040) | 0.572 (0.060) | 0.448 |
| Gower, PAM | 0.289 (0.052) | 0.190 (0.053) | 0.024 (0.011) | 0.220 |
| Gower, average link | 0.455 (0.034) | 0.166 (0.120) | -0.003 (0.006) | 0.425 |
| k-prototypes | 0.796 (0.040) | 0.004 (0.001) | 0.721 (0.013) | 0.315 |
| Latent class | 0.957 (0.006) | 0.659 (0.026) | 0.791 (0.024) | 0.351 |

Latent class wins three columns because I gave it home advantage: the generator *is* its model, with normal numbers and categories independent within a group. Break that, in `correlated`, and FAMD leads. Don't read this table as "use LCA". Read the shape of it. One-hot and k-prototypes can't hear categories alone. FAMD hears both at some cost when categories are noise (0.572 against 0.726). Gower with equal weights is weak here for the reason the spread table showed.

Two published simulations agree on Gower's place and differ on the rest. [Preud'homme and colleagues](https://pmc.ncbi.nlm.nih.gov/articles/PMC7892576/) (*Scientific Reports*, 2021; 1,000 generated datasets per design over 7 scenarios, R tools) have k-prototypes, KAMILA and latent class on top and Gower worst. [Costa and colleagues](https://arxiv.org/abs/2203.16287) (*Advances in Data Analysis and Classification*; 81,000 generated tables, true $k$ supplied) have mean ARI of 0.366 for KAMILA, 0.340 for FAMD with k-means, 0.336 for k-prototypes and 0.136 for Gower with PAM, which stays poor even on well-separated clusters (about 0.27 to 0.31 at the lowest overlap). Both draw numbers from normals, and Costa's authors suggest that may favour squared-loss methods. So this is no general verdict on medoids, and neither study compares latent class with FAMD. None of the three uses real customers.

The one real table I ran is [Palmer penguins](https://allisonhorst.github.io/palmerpenguins/) (333 complete rows, CC0), with $k=3$ scored against species, and the rank order moves. "Numbers only" is k-means on the four z-scored body measurements; every other method also gets `island` and `sex`. One run, seed 0:

| Numbers only | k-prototypes | FAMD 4 | One-hot | Gower, average | Latent class | Gower, PAM |
|---:|---:|---:|---:|---:|---:|---:|
| 0.799 | 0.734 | 0.563 | 0.553 | 0.543 | 0.506 | 0.496 |

Every mixed method lands below k-means on the numbers alone. Which column does the damage? Add them one at a time:

```python
P, species = lab.penguins()
numbers = list(P.columns[:4])
for name, cols in [("numbers", numbers), ("+ island", numbers + ["island"]), ("+ sex", numbers + ["sex"]), ("+ both", list(P.columns))]:
    t = P[cols]
    famd = ari(species, lab.km(lab.famd(t, min(4, t.shape[1]))[0], 3))
    gower = ari(species, lab.pam(lab.gower(t), 3))
    print(f"{name:9} FAMD {famd:.3f}  Gower PAM {gower:.3f}")
```

```text
numbers   FAMD 0.799  Gower PAM 0.631
+ island  FAMD 0.563  Gower PAM 0.559
+ sex     FAMD 0.543  Gower PAM 0.181
+ both    FAMD 0.563  Gower PAM 0.496
```

Either column alone costs FAMD about a third of its score (0.799 to 0.563 or 0.543). Gower with PAM falls furthest with `sex` alone (0.181). Every species has both sexes, so a column that splits each species in two competes with the groups we are scoring against; that reading is mine, and `island` also hurts. "Use all the columns" is a choice too. A mixed method faithfully clusters what you give it.

## Encodings: which ones need a label?

The advice to use target or CatBoost encoding comes from supervised learning. [Pargent and colleagues](https://arxiv.org/abs/2104.00629) (*Computational Statistics*, 2022) split encoders into target-agnostic and target-based, noting that only the first can be used without a target. Their finding that regularised target encoding wins comes from a supervised benchmark, so it doesn't transfer. With no label there's nothing to compute it from. [CatBoost's target statistics](https://arxiv.org/abs/1706.09516) ([note 07](07-boosting-in-practice.md)) are the same story, and so are [entity embeddings](https://arxiv.org/abs/1604.06737) (a preprint), which are learned during supervised training even though the authors say the result could then be used for clustering. Train one on a stand-in label and your distances reflect that stand-in (my reasoning). An autoencoder needs no label, but I read no evidence on it for customer tables.

High-cardinality columns are where this bites. Frequency encoding replaces a level with its share of rows. Hashing sends each level to one of a fixed number of columns through a hash function, with a sign of +1 or -1, so different levels can collide. Binary encoding numbers the levels and gives each bit of the number its own column.

Here are 1,500 customers with 3 columns of 200 levels each. Each level leans towards one of four groups, and 80% of a customer's values follow their group, so the signal lives in which levels occur together:

| Encoding | Columns | Needs a target? | ARI, mean of 3 seeds | What goes wrong |
|---|---:|---|---:|---|
| One-hot, SVD to 8 (MCA-like) | 8 | No | 0.491 | The only one that keeps co-occurrence |
| One-hot | 600 | No | 0.053 | Every pair of different levels is equally far apart |
| Frequency | 3 | No | 0.039 | Levels of equal size collapse together |
| Hashing | 32 | No | 0.012 | [Signed collisions cancel in expectation](https://arxiv.org/abs/0902.2206) (Weinberger and colleagues, ICML 2009), not for one customer |
| Binary | 24 | No | 0.004 | Bits are arbitrary: codes 001 and 011 sit at squared distance 1, 001 and 110 at 3 |
| Gower, PAM | none | No | 0.008 | Matching can't see that two levels are related |
| Target, CatBoost, embeddings | | **Yes** | | Not available |

The world is built so that co-occurrence is the signal, so this isn't a general ranking, and I found no published benchmark of these encoders for clustering customers. The binary row's reasoning is mine; no source I read states it.

## Validating without a label

The silhouette and the two other common internal indices take different inputs. **Calinski-Harabasz (CH)** is between-group spread over within-group spread, adjusted for $k$; higher is better. **Davies-Bouldin (DB)** averages each group's worst similarity to another group; lower is better. In scikit-learn only the [silhouette](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html) accepts a precomputed matrix. [CH](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.calinski_harabasz_score.html) and [DB](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.davies_bouldin_score.html) need features, so on Gower they're off the table.

| $k$ | Silhouette `both` | Control | CH `both` | Control | DB `both` | Control | Gower silhouette `both` | Control |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 0.216 | 0.121 | 329 | 125 | 1.653 | 2.919 | 0.194 | 0.118 |
| 3 | 0.233 | 0.102 | 308 | 117 | 1.705 | 2.553 | 0.206 | 0.084 |
| **4** | 0.243 | 0.110 | 277 | 117 | 1.534 | 2.264 | 0.185 | 0.090 |
| 5 | 0.249 | 0.120 | 249 | 118 | 1.471 | 2.039 | 0.153 | 0.089 |
| 6 | 0.254 | 0.129 | 232 | 120 | 1.472 | 1.866 | 0.151 | 0.087 |
| 7 | 0.227 | 0.139 | 219 | 120 | 1.557 | 1.725 | 0.160 | 0.086 |

FAMD coordinates with k-means, except the last two columns; seed 0; truth is $k=4$. No index picks 4. Silhouette says 6, CH says 2, DB says 5. On the control, DB improves steadily as $k$ grows, with nothing there to find. [Arbelaitz and colleagues](https://doi.org/10.1016/j.patcog.2012.07.021) (*Pattern Recognition*, 2013) compared 30 indices over 6,480 configurations of numeric data and found silhouette best overall, the only one above a 50% success rate, with no index winning in every context; that wasn't mixed data. Use these to compare against a control. The gap between the `both` and control columns carries the message: silhouette 0.243 against 0.110. The peak doesn't.

The shuffled-column control from [note 05](05-unsupervised-learning.md#choosing-k-the-criteria-disagree) works here, and so does stability, which needs a control too. Fit on two 80% subsamples and compare labels on the customers they share:

| ARI between overlapping 80% subsamples | `both` | Control |
|---|---:|---:|
| FAMD, k-means | 0.963 | 0.257 |
| Gower, PAM | 0.802 | 0.304 |

Gower with PAM is *stable* at 0.802 while recovering the truth at 0.263 on that same table (seed 0; the five-seed mean is 0.289). Stability says you'd get the same answer again, which isn't the same as the right answer.

## Explaining segments: useful, but not proof

Fitting CatBoost, a gradient-boosted tree classifier ([note 07](07-boosting-in-practice.md), still ahead), to predict the cluster labels and reading SHAP values ([note 08](08-model-interpretability.md)) is a good way to describe segments. [SHAP assigns each feature an importance for a prediction](https://arxiv.org/abs/1705.07874) (Lundberg and Lee, NIPS 2017), and here the prediction is your own label. So high accuracy can't validate anything:

```python
for world in ("both", "control"):
    accuracy, shap = lab.surrogate(world)
    print(f"{world:8} 3-fold accuracy {accuracy:.3f}  top columns", shap.head(3).round(2).to_dict())
```

```text
both     3-fold accuracy 0.958  top columns {'logins': 0.94, 'plan': 0.89, 'channel': 0.7}
control  3-fold accuracy 0.913  top columns {'industry': 1.5, 'payroll': 0.56, 'mobile': 0.52}
```

With no groups in the data, the classifier still predicts the labels at 91% and gives a confident ranking of columns. K-means carved regions out of the space, so the columns do predict them. [A 2026 preprint on UK dietary data](https://arxiv.org/abs/2605.08242) (Yu and Chiu, accepted at FICTA) comes closest to saying this outright, treating such accuracy as evidence of reproducibility and explanation, not of clinical or external predictive validity. If you want a real test, [split the data first](https://arxiv.org/abs/2308.01475) (Allen, Gan and Zheng, *Annual Review of Statistics and Its Application*, 2024): cluster the training part, transfer labels to held-out rows with a classifier, cluster the held-out rows independently, and compare the two, [as Ullmann and colleagues set out](https://arxiv.org/abs/2103.01281) (*WIREs Data Mining and Knowledge Discovery*).

The same trap catches significance tests. "The segments differ on revenue, p < 0.001" is close to guaranteed, because the clustering made them differ. [Gao, Bien and Witten](https://arxiv.org/abs/2012.02936) (*JASA*) show classical tests between estimated clusters have an extremely inflated false-positive rate, and they call the cause double use of the data. Their correction covers hierarchical clustering of normal data. It doesn't cover the methods here, so report those differences as description.

The check that matters most comes from outside the data, as in [DA 06/05](../../../data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm.md): do the segments predict something later, on customers or periods not used to fit them, better than a one-line rule?

## Which to reach for

| Situation | Start with | Then check |
|---|---|---|
| Mixed columns, whatever the size | FAMD with generous axes, then k-means | One-hot and numeric-only versions; control |
| Only categories | MCA, then k-means | Benzécri percentages; rare levels |
| You want "no groups" as a possible answer, or probabilities per customer | Latent class with BIC | Correlated columns within class |
| Many missing values, or a bespoke notion of similar | Gower with chosen weights, then PAM or average link | Sensitivity to the weights; a sample if $n$ is large |
| You want each centre stated as a mean and a mode per column | k-prototypes | Sweep $\gamma$ |
| Hundreds of levels | Pool rare levels, or MCA-like SVD | Never binary or hashing on trust |
| A strong reason to think some columns are noise | Drop them first | A joint method such as `clustrd` |

In every row, run the control, and rerun on a numeric-only and a category-only version to find out which columns your answer depends on.

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| One-hot beside z-scored numbers | ARI of 0.003 when only categories hold the groups, with tidy clusters anyway | FAMD coding, or test on each column block alone |
| Reading raw MCA percentages | First axis looks like 10% | Benzécri or Greenacre correction |
| A rare level taking over an axis | 8 customers in 1,200 took 96% of axis 1's contribution | Pool, or make passive, then replot |
| Elbow-picking axes before clustering | One axis at 56% of variance and ARI of 0.002 | Keep more axes; check columns on their own |
| Assuming Gower's equal weights are fair | Categories move the distance about three times as much | Inspect the per-column spread and set weights on purpose |
| Reading a steady Gower score as robustness | In `both` at seed 0, setting one value to 500 in each numeric column left Gower with PAM at 0.264 (0.263 clean), because numeric spread fell from about 0.15 to 0.04: numbers had stopped counting | Check the spread, not just the score |
| Ignoring outliers before z-scoring | The same five values took FAMD with k-means from 0.880 to 0.413; clipping at 1% and 99% restored 0.879 | Clip or fix before any scale-based method |
| Trusting the $\gamma$ default | 0.700 in one world, 0.004 in another | Sweep it |
| LCA with correlated columns | BIC keeps falling and finds too many classes | Check residual correlation; drop or merge columns |
| Treating stability as validity | 0.802 stable, 0.263 correct | Stability against a control, plus an outside check |
| SHAP accuracy as validation | 0.913 with no groups | Describe with it; validate on held-out outcomes |
| Scoring new rows with `prince` FAMD in a small batch | Coordinates differ from the full-table ones | Save category shares; score against them |

## Try it

1. By hand, apply Benzécri's correction to an MCA eigenvalue of 0.324 with 6 columns. Does an eigenvalue of 0.160 survive?
2. A column's Gower term is 0 or 1. What share of matching pairs gives it the largest spread, and what is that spread?
3. Rerun the k-prototypes table in your head: if you had to choose one $\gamma$ without knowing the world, which would you choose, and what would it cost?
4. Your colleague's CatBoost predicts their segments at 96% and they call the segments validated. What single run would you ask for?
5. Run `lab.gower(df, numeric_weight=5)` with PAM in `both`, `categorical` and `numeric`. Then argue whether you'd ship the weight.

<details>
<summary>Answers</summary>

1. $(\frac{6}{5}(0.324 - 0.1667))^2 = 0.1888^2 = 0.0356$. An eigenvalue of 0.160 is below $1/6 = 0.167$, so it's dropped.
2. A 50% share of matches, giving a standard deviation of 0.5. `mobile` shows exactly that. A column where almost every pair matches or mismatches has a small spread and says little.
3. $\gamma = 2$ is the most even (0.675, 0.165, 0.511), but it gives up about a tenth in `both` and more in `numeric`, and it still mostly misses `categorical`. No value wins, which is why FAMD or a sweep is the better plan.
4. The same pipeline on a table with each column shuffled alone. Here that gave 0.913 accuracy with no groups present, so 96% alone shows nothing.
5. Over five seeds in `both` it lifts ARI from 0.289 to 0.713. At seed 0, `numeric` rises from 0.018 to 0.466 and `categorical` falls from 0.184 to 0.141. You only chose 5 because the truth was known here. On real data, choose weights from what the segments are for and report the sensitivity.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| Why does one-hot plus k-means struggle? | Dummies have small variance beside z-scores, so categories get little say. Here ARI was 0.003 when only they held the groups |
| What does FAMD change? | Numbers are z-scored and dummies are divided by $\sqrt{p}$, then PCA. Each column can contribute at most 1 to any axis |
| What is balanced in FAMD, and what isn't? | Maximum inertia per axis is balanced. Total isn't: a category with $m$ levels holds $m-1$ |
| What does MCA's Benzécri correction do? | Drops axes at or below $1/J$ and rescales the rest, since the dummy coding inflates raw inertia |
| What is the tandem warning? | Top components rank by variance, so reducing first can discard the groups. Evidence on categorical data is less settled |
| How does Gower handle a missing value? | That column drops out of that pair's average |
| What's the main cost of Gower with PAM? | The $n \times n$ matrix: $8n^2$ bytes, 80 GB at 100,000 customers |
| What does $\gamma$ do in k-prototypes? | Trades numeric against categorical cost. No value suited all worlds here, and its author calls the guidance premature |
| What does LCA assume, and what breaks it? | Columns are independent within a class. A hidden factor breaks it, and BIC over-extracts |
| What does LCA offer that k-means can't? | A likelihood, so BIC can compare against one class: "no groups" is an answer |
| Why not target encoding for clustering? | There is no target to compute it from. Same for CatBoost statistics and supervised embeddings |
| Can you use Calinski-Harabasz on Gower? | Not in scikit-learn: it needs features. Silhouette takes a precomputed matrix |
| What can CatBoost and SHAP do for clusters? | Describe them. Accuracy was 0.913 with no groups, so they can't validate them |
| Why not test differences between clusters? | The clustering created them; classical tests are badly inflated |
| Which method is best? | It depends on the columns and what the segments are for. Benchmark on your table against a control |

## Next

[Ensembles](06-ensembles.md): back to labels, where trees handle categories and interactions without any of this.
