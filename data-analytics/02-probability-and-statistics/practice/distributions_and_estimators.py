# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scipy"]
# ///
"""Bernoulli, Binomial, Poisson and Normal: how they connect, and what bias and variance of an estimator mean.

Four checks, each printed as a small table:
1. moments of each distribution against the formulas;
2. Binomial approximated by Poisson (small p) and by Normal (large np);
3. the Central Limit Theorem on a skewed distribution;
4. a biased and an unbiased variance estimator, and which has the lower mean squared error.

Run from this folder with: uv run distributions_and_estimators.py
"""
import numpy as np
from scipy import stats

rng = np.random.default_rng(11)

# %% 1. Moments: formula against a large sample
print("1. Mean and variance: formula against 500,000 draws")
print(f"{'distribution':<22}{'mean':>9}{'sample':>9}{'variance':>10}{'sample':>9}")
cases = {
    "Bernoulli(0.3)": (stats.bernoulli(0.3), 0.3, 0.3 * 0.7),
    "Binomial(20, 0.3)": (stats.binom(20, 0.3), 20 * 0.3, 20 * 0.3 * 0.7),
    "Poisson(4)": (stats.poisson(4), 4.0, 4.0),
    "Normal(10, sd 2)": (stats.norm(10, 2), 10.0, 4.0),
    "Geometric(0.2)": (stats.geom(0.2), 1 / 0.2, 0.8 / 0.2**2),
    "Exponential(rate 2)": (stats.expon(scale=1 / 2), 0.5, 0.25),
}
for name, (dist, mean, var) in cases.items():
    x = dist.rvs(size=500_000, random_state=rng)
    print(f"{name:<22}{mean:>9.3f}{x.mean():>9.3f}{var:>10.3f}{x.var():>9.3f}")
    assert abs(x.mean() - mean) < 0.02 * max(mean, 1) and abs(x.var() - var) < 0.03 * max(var, 1)

# %% 2. Approximating the Binomial
# Poisson works when n is large and p small (lambda = np). Normal works when np and n(1-p) are both large.
print("\n2. Largest gap in P(X = k) between Binomial(n, p) and its approximations")
print(f"{'n':>6}{'p':>7}{'np':>7}{'Poisson gap':>13}{'Normal gap':>12}")
for n, p in [(20, 0.5), (100, 0.5), (100, 0.03), (1000, 0.003), (1000, 0.3)]:
    k = np.arange(n + 1)
    exact = stats.binom.pmf(k, n, p)
    pois = stats.poisson.pmf(k, n * p)
    sd = np.sqrt(n * p * (1 - p))
    normal = stats.norm.cdf(k + 0.5, n * p, sd) - stats.norm.cdf(k - 0.5, n * p, sd)  # continuity correction
    print(f"{n:>6}{p:>7.3f}{n * p:>7.1f}{np.abs(exact - pois).max():>13.4f}{np.abs(exact - normal).max():>12.4f}")

# %% 3. Central Limit Theorem on a skewed population
# Exponential(1) has mean 1, sd 1 and a long right tail. The mean of n draws should be close to Normal(1, 1/n).
print("\n3. CLT: means of n Exponential(1) draws (20,000 means each)")
print(f"{'n':>5}{'sd of means':>13}{'1/sqrt(n)':>11}{'skewness':>10}{'within 1.96 SE':>16}")
for n in (2, 10, 30, 200):
    means = rng.exponential(1.0, size=(20_000, n)).mean(axis=1)
    se = 1 / np.sqrt(n)
    inside = (np.abs(means - 1) < 1.96 * se).mean()
    print(f"{n:>5}{means.std():>13.4f}{se:>11.4f}{stats.skew(means):>10.2f}{inside:>16.1%}")
# The sd of the mean falls as 1/sqrt(n): four times the data halves the error.
# Skewness shrinks towards 0 and coverage towards 95%, but the raw data stays as skewed as ever.

# %% 4. Bias and variance of an estimator
# Estimate the variance of Normal(0, sd 2), true value 4, from samples of size n = 5.
# Divide the sum of squares by n (the MLE), by n - 1 (Bessel) or by n + 1.
print("\n4. Three variance estimators, true variance 4, n = 5, 200,000 samples")
print(f"{'divisor':<10}{'mean':>8}{'bias':>8}{'variance':>10}{'MSE':>8}")
n, true_var = 5, 4.0
x = rng.normal(0, 2, size=(200_000, n))
ss = ((x - x.mean(axis=1, keepdims=True)) ** 2).sum(axis=1)
mse = {}
for label, d in (("n", n), ("n - 1", n - 1), ("n + 1", n + 1)):
    est = ss / d
    bias = est.mean() - true_var
    mse[label] = bias**2 + est.var()
    print(f"{label:<10}{est.mean():>8.3f}{bias:>8.3f}{est.var():>10.3f}{mse[label]:>8.3f}")
assert mse["n + 1"] < mse["n"] < mse["n - 1"]
# Dividing by n - 1 is unbiased. Dividing by n is biased low by the factor (n - 1)/n, here 0.8.
# The biased estimators have the lower MSE: MSE = bias^2 + variance, and shrinking cuts variance
# by more than it adds in bias^2. Unbiased is not the same as best.

# %% Try it
# 1. Rerun part 4 with n = 50. How much of the bias is left, and does the MSE ranking still matter?
# 2. In part 3, swap the exponential for a Pareto with shape 1.5 (infinite variance). What breaks?
# 3. Generate counts with variance well above the mean (rng.negative_binomial) and overlay a Poisson pmf
#    with the same mean. Which tail does the Poisson miss?
