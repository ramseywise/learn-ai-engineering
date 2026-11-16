# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scipy"]
# ///
"""An A/B test on a conversion rate, by hand: the z-test, the sample size, and what breaks it.

1. the two-proportion z-test, written out and checked against a worked example;
2. sample size for a minimum detectable effect, and the 16 p(1-p)/delta^2 shortcut;
3. A/A tests: the false positive rate is alpha when you look once;
4. power: at the planned sample size a true effect is found about 80% of the time;
5. peeking: stopping at the first significant look inflates the false positive rate;
6. sample ratio mismatch as a chi-square test.

Run from this folder with: uv run ab_test_from_scratch.py
"""
import numpy as np
from scipy import stats

rng = np.random.default_rng(3)


def z_test(x_c: int, n_c: int, x_t: int, n_t: int) -> dict[str, float]:
    """Two-sided two-proportion z-test. Pooled SE for the test, unpooled SE for the interval."""
    p_c, p_t = x_c / n_c, x_t / n_t
    pooled = (x_c + x_t) / (n_c + n_t)
    se_test = np.sqrt(pooled * (1 - pooled) * (1 / n_c + 1 / n_t))
    z = (p_t - p_c) / se_test
    se_ci = np.sqrt(p_c * (1 - p_c) / n_c + p_t * (1 - p_t) / n_t)
    return {
        "diff": p_t - p_c,
        "z": z,
        "p": 2 * stats.norm.sf(abs(z)),
        "lo": p_t - p_c - 1.96 * se_ci,
        "hi": p_t - p_c + 1.96 * se_ci,
    }


def p_values(x_c, n_c, x_t, n_t):
    """Vectorised p-values for many simulated experiments at once."""
    pooled = (x_c + x_t) / (n_c + n_t)
    se = np.sqrt(pooled * (1 - pooled) * (1 / n_c + 1 / n_t))
    return 2 * stats.norm.sf(np.abs((x_t / n_t - x_c / n_c) / se))


def sample_size(p: float, delta: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Users per arm to detect an absolute lift `delta` on a baseline rate `p`."""
    z_a, z_b = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    p2 = p + delta
    return int(np.ceil((z_a + z_b) ** 2 * (p * (1 - p) + p2 * (1 - p2)) / delta**2))


# %% 1. The worked example: 1,000 of 10,000 convert in control, 1,100 of 10,000 in treatment
r = z_test(1000, 10_000, 1100, 10_000)
print("1. Control 10.0%, treatment 11.0%, 10,000 users each")
print(f"   lift {r['diff']:.3f}, z = {r['z']:.2f}, p = {r['p']:.3f}, 95% CI [{r['lo']:.4f}, {r['hi']:.4f}]")
assert abs(r["z"] - 2.31) < 0.01 and abs(r["p"] - 0.021) < 0.001
# Significant at 5%. The interval runs from about 0.15 to 1.85 points: the lift is real but its size is not pinned down.

# %% 2. Sample size
print("\n2. Users per arm, alpha 0.05 two-sided, power 80%")
print(f"{'baseline':>10}{'lift':>8}{'exact':>10}{'16p(1-p)/d^2':>15}")
for p, d in [(0.10, 0.02), (0.10, 0.01), (0.10, 0.005), (0.02, 0.002)]:
    print(f"{p:>10.0%}{d:>8.3f}{sample_size(p, d):>10,}{16 * p * (1 - p) / d**2:>15,.0f}")
# Halving the lift you want to detect multiplies the sample by four.

# %% 3. A/A tests: no true difference, one look at the end
SIMS, n, base = 20_000, 14_750, 0.10
x_c, x_t = rng.binomial(n, base, SIMS), rng.binomial(n, base, SIMS)
fpr = (p_values(x_c, n, x_t, n) < 0.05).mean()
print(f"\n3. A/A, one look: {fpr:.1%} of {SIMS:,} tests are 'significant' (expected 5%)")
assert 0.04 < fpr < 0.06

# %% 4. Power at the planned sample size
n_plan = sample_size(0.10, 0.01)
x_c, x_t = rng.binomial(n_plan, 0.10, SIMS), rng.binomial(n_plan, 0.11, SIMS)
power = (p_values(x_c, n_plan, x_t, n_plan) < 0.05).mean()
print(f"4. True lift of 1 point, n = {n_plan:,} per arm: detected in {power:.1%} of tests (planned 80%)")
assert 0.77 < power < 0.83
# With a quarter of the sample the same lift is usually missed:
x_c, x_t = rng.binomial(n_plan // 4, 0.10, SIMS), rng.binomial(n_plan // 4, 0.11, SIMS)
print(f"   with n = {n_plan // 4:,} per arm: {(p_values(x_c, n_plan // 4, x_t, n_plan // 4) < 0.05).mean():.1%}")

# %% 5. Peeking: check after every batch and stop at the first p < 0.05
print("\n5. A/A with peeking: share of tests that are ever 'significant'")
batch = 1_000
for looks in (1, 5, 10, 20):
    c = rng.binomial(batch, base, size=(SIMS, looks)).cumsum(axis=1)
    t = rng.binomial(batch, base, size=(SIMS, looks)).cumsum(axis=1)
    seen = batch * np.arange(1, looks + 1)
    ever = (p_values(c, seen, t, seen) < 0.05).any(axis=1).mean()
    print(f"   {looks:>2} looks: {ever:.1%}")
# The fix is a fixed horizon (look once), or a sequential design that spends alpha across the looks.

# %% 6. Sample ratio mismatch
# A 50/50 design that logged 10,000 and 10,500 users. Is that chance?
obs = np.array([10_000, 10_500])
chi2, p = stats.chisquare(obs, f_exp=[obs.sum() / 2] * 2)
print(f"\n6. SRM: 10,000 vs 10,500 under a 50/50 design: chi2 = {chi2:.2f}, p = {p:.4f}")
print("   p < 0.001 is the usual alarm: fix the assignment or logging before reading any metric.")

# %% Try it
# 1. Rerun part 1 with 100 of 1,000 against 110 of 1,000. Same rates, a tenth of the data. What changed?
# 2. In part 5, replace the 0.05 threshold with 0.05 / looks (Bonferroni). What is the false positive rate now?
# 3. Give each user a random number of sessions and analyse sessions as if independent. Watch the A/A rate.
