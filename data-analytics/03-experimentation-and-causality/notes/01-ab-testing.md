---
origin: own coursework
sources:
  - ../practice/AB-Bayes/AB_Testing_with_Python.ipynb
  - ../../02-probability-and-statistics/practice/5_Statistical_Analysis.ipynb
  - https://www.kaggle.com/datasets/zhangluyuan/ab-testing (ab_data.csv, not included)
  - https://www.statsmodels.org/stable/stats.html#power-and-sample-size-calculations
  - ../../sources/kohavi-2008-controlled-experiments-web.pdf (Kohavi et al., DMKD, 2009)
  - ../../sources/Alex_Reinhart-Statistics_Done_Wrong-EN.pdf
  - ../../sources/Practical_Statistics_for_Data_Scientist.pdf (ch. 3)
confidence: high
cleaned: 2026-11-01
---
# 1 — A/B Testing

Larkspur's designers have rebuilt the checkout, and everyone who has seen it thinks it is better. A shop that once "upgraded" its checkout in just this way lost 90% of its revenue, because a new coupon-code box made shoppers wonder whether they were overpaying, and removing the box from the new design put conversion 6.5% above the old one ([Kohavi et al., DMKD, 2009](https://doi.org/10.1007/s10618-008-0114-1)). An A/B test exists because opinion and before/after charts cannot separate your change from everything else happening that month. This chapter runs one properly: decide what you would act on, size it, assign users, check the assignment, then read the answer once.

Randomisation is what makes this different from everything in the [statistics pillar](../../02-probability-and-statistics/README.md). There, we could only say what was true of the data. Here, a coin decides who gets the treatment, so nothing about a user can cause both their arm and their outcome, measured or not. Any systematic difference between the arms has one explanation left besides chance. That is why a two-sample test, which proves nothing about causes in an observational table, is enough here. The test is the easy part, and nearly all the ways to fail come before and after it.

## The pipeline

```mermaid
flowchart LR
    M[Choose the metric] --> E[Set the MDE]
    E --> N[Compute N and duration]
    N --> R[Randomise by user]
    R --> S[Check the sample ratio]
    S --> T[Test once at N]
    T --> D[Decide from the interval]
```

| Step | Decision | Failure if skipped |
|---|---|---|
| 1. Metric | one primary metric (conversion, revenue per user), plus guardrails | twenty metrics, one "wins" by chance |
| 2. Minimum detectable effect (MDE) | the smallest lift worth shipping | test runs forever or is underpowered |
| 3. Sample size | power analysis from baseline, MDE, α, power | peeking, or stopping too early |
| 4. Randomisation unit | user, not session or pageview | the same user sees both arms |
| 5. Run to N | no decisions before N | inflated false-positive rate |
| 6. Test | two-proportion z (or Welch t for means) | |
| 7. Report | lift, 95% CI, p-value, sample ratio check | "significant" with no effect size |

The metric step gets [its own chapter](02-metrics-and-kpi-design.md). Here the metric is simple: did this user buy during the test? Kohavi and colleagues insist that the evaluation criterion is agreed before the test, and the reason is practical as well as statistical. Once a result is in, the argument about what the metric should have been tends to follow whichever result each person wanted.

## How many users

The minimum detectable effect is a business number. Larkspur's conversion is 5%. The redesign has an engineering cost and ongoing risk, and the team agrees that anything under half a point is not worth shipping. That turns "does it work?" into "can we detect 5.0% against 5.5%?". Power is the chance of detecting that effect if it exists. Convention is 80%, so a real effect of exactly the MDE is missed one time in five.

For two proportions with equal arms, each arm needs

```text
n = (z_{1-α/2} + z_{1-β})² · [p₁(1-p₁) + p₂(1-p₂)] / (p₂ - p₁)²
```

The sum in the bracket is why this is a two-sample calculation: the difference between two means carries noise from both.

```python
import hashlib
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.stats.api as sms
from statsmodels.stats.proportion import proportions_ztest, proportion_confint

def n_per_arm(p1, p2, alpha=0.05, power=0.80):
    """Users per arm to detect p1 vs p2 with a two-sided two-proportion z-test."""
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    return z ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p2 - p1) ** 2

print(f"per arm, 5.0% to 5.5%: {n_per_arm(0.05, 0.055):,.0f}")
```

```text
per arm, 5.0% to 5.5%: 31,231
```

There are several routes to the same number, and the agreement is worth seeing once. Kohavi's rule of thumb is n ≈ 16σ²/δ² per arm at 5% significance and 80% power, and `statsmodels` uses Cohen's h, an arcsine transformation of the two rates:

```python
p, q = 0.05, 0.055
h = sms.proportion_effectsize(q, p)
by_h = sms.NormalIndPower().solve_power(h, power=0.8, alpha=0.05, ratio=1)
var = p * (1 - p)
print(f"formula with both variances   {n_per_arm(p, q):>8,.0f}")
print(f"statsmodels, Cohen's h        {by_h:>8,.0f}")
print(f"Kohavi's 16 sigma^2 / delta^2 {16 * var / (q - p) ** 2:>8,.0f}")
```

```text
formula with both variances     31,231
statsmodels, Cohen's h          31,217
Kohavi's 16 sigma^2 / delta^2   30,400
```

Use any of them. They agree within a few percent, and your baseline estimate is rarely better than that.

The two practice notebooks do this calculation too, and it is worth checking them, because one of them has a bug in a form you will see elsewhere:

```python
pooled = (0.05 + 0.06) / 2
effect = 0.01 / np.sqrt(pooled * (1 - pooled))
z_sum = stats.norm.ppf(0.975) + stats.norm.ppf(0.80)
print(f"practice 5, Part 3 (5% to 6%), its formula: {np.ceil((z_sum / effect) ** 2):,.0f}")
print(f"same test, standard two-arm formula:        {n_per_arm(0.05, 0.06):,.0f}")
h2 = sms.proportion_effectsize(0.13, 0.15)
print(f"AB notebook (13% to 15%):                   "
      f"{sms.NormalIndPower().solve_power(h2, power=0.8, alpha=0.05, ratio=1):,.0f}")
```

```text
practice 5, Part 3 (5% to 6%), its formula: 4,080
same test, standard two-arm formula:        8,155
AB notebook (13% to 15%):                   4,719
```

The formula in `5_Statistical_Analysis.ipynb` computes (z/d)², which is the one-sample formula. It leaves out the factor of 2 from having noise in both arms, so its 4,080 per group is about half of what the test needs and gives far less than the promised 80% power. The AB notebook's `solve_power` call is right, and returns about 4,720 per group. A check against the 16σ²/δ² rule catches this kind of error in seconds: 16 × 0.052 / 0.01² is about 8,300.

### What moves N

```python
base = n_per_arm(0.05, 0.055)
rows = {
    "baseline plan (5.0 to 5.5, 80% power, alpha .05)": base,
    "halve the MDE (5.0 to 5.25)": n_per_arm(0.05, 0.0525),
    "double the MDE (5.0 to 6.0)": n_per_arm(0.05, 0.06),
    "power 0.90": n_per_arm(0.05, 0.055, power=0.9),
    "alpha 0.01": n_per_arm(0.05, 0.055, alpha=0.01),
    "same absolute lift at 20% baseline": n_per_arm(0.20, 0.205),
}
for k, v in rows.items():
    print(f"{k:<50}{v:>9,.0f}  x{v / base:.2f}")
```

```text
baseline plan (5.0 to 5.5, 80% power, alpha .05)     31,231  x1.00
halve the MDE (5.0 to 5.25)                         122,121  x3.91
double the MDE (5.0 to 6.0)                           8,155  x0.26
power 0.90                                           41,809  x1.34
alpha 0.01                                           46,471  x1.49
same absolute lift at 20% baseline                  101,400  x3.25
```

| Change | Effect on N | Why |
|---|---|---|
| halve the MDE | about ×4 | N grows with the inverse square of the effect |
| power 0.8 → 0.9 | ×1.34 | |
| α 0.05 → 0.01 | ×1.49 | |
| higher baseline, same absolute lift | larger | variance p(1−p) peaks at 0.5 |
| unequal split | larger total | see below |

The inverse square is the law from [estimation](../../02-probability-and-statistics/notes/04-estimation.md): precision costs data quadratically. Most sizing arguments end here. If the plan needs 122,000 per arm and you can get 40,000, either accept that you can only detect bigger effects, or find a less noisy metric or [a variance-reduction method](03-experimentation-at-scale.md), or do not run the test. An underpowered test does not just risk missing the effect. When it does reach significance, the estimate is inflated, as the [winner's curse](../../02-probability-and-statistics/notes/05-hypothesis-testing.md) showed.

### From users to days

```python
daily_users = 4_000
needed = 2 * n_per_arm(0.05, 0.055)
days = needed / daily_users
print(f"users needed {needed:,.0f}, at {daily_users:,}/day = {days:.1f} days, "
      f"run {int(np.ceil(days / 7)) * 7} days")
for share in (0.5, 0.1, 0.01):
    mult = 1 / (4 * share * (1 - share))
    print(f"treatment share {share:>4.0%}: variance multiplier {mult:5.1f}")
```

```text
users needed 62,461, at 4,000/day = 15.6 days, run 21 days
treatment share  50%: variance multiplier   1.0
treatment share  10%: variance multiplier   2.8
treatment share   1%: variance multiplier  25.3
```

Two rules turn this into a calendar. Run whole weeks, because weekend shoppers differ from weekday ones, and because some users only arrive at certain points in the cycle. Kohavi and colleagues recommend at least one to two weeks for this reason. And split 50/50 once you have checked for damage. The variance multiplier 1/(4p(1−p)) shows that a 99/1 split needs about 25 times the running time of 50/50 for the same power, which is why the [ramp](03-experimentation-at-scale.md) spends as little time as possible at low percentages.

Larkspur books 21 days, which yields about 84,000 users, more than the 62,461 the calculation needs. Selling those spare weeks as "more power" is honest. Stopping at day 16 because the number was reached is also fine, if that was the rule beforehand. Deciding after seeing results is not.

## Assigning users

Assignment must be random, stable for a user, and independent of every other test running. The usual way is to hash the user ID with a salt unique to the experiment:

```python
def bucket(user_id, salt="checkout-redesign-v1", arms=("A", "B")):
    h = hashlib.sha256(f"{salt}:{user_id}".encode()).hexdigest()
    return arms[int(h, 16) % len(arms)]

ids = [f"u{i}" for i in range(84_000)]
arm = np.array([bucket(u) for u in ids])
print("u17 twice:", bucket("u17"), bucket("u17"))
counts = pd.Series(arm).value_counts().sort_index()
print(counts.to_dict())
print("chi-square p:", round(stats.chisquare(counts).pvalue, 3))
```

```text
u17 twice: A A
{'A': 42141, 'B': 41859}
chi-square p: 0.331
```

There is no assignment table to keep and nothing to look up, and a returning user always lands in the same arm. Changing the salt gives a fresh independent split for the next test, and that independence is what lets many tests overlap. Do not skimp on the hash. Kohavi and colleagues tested several and found that only a cryptographic one passed their tests, with poor ones causing correlations between experiments.

The unit of randomisation should also be your unit of analysis. If you randomise by user and analyse by pageview, you repeat the mistake from [regression](../../02-probability-and-statistics/notes/06-regression-and-glms.md): pageviews from the same person are not independent, and the test is overconfident. This simulation of an A/A test, with no treatment at all, shows the size of the problem:

```python
rng = np.random.default_rng(12)
fp_user = fp_view = 0
reps = 2_000
for _ in range(reps):
    users = 800
    views = rng.integers(1, 11, users)             # 1 to 10 pageviews each
    u_rate = rng.beta(0.5, 9.5, users)             # users differ a lot, mean 5%
    arm_u = rng.random(users) < 0.5
    clicks = rng.binomial(views, u_rate)
    # by pageview, as if each view were independent
    va, vb = views[~arm_u].sum(), views[arm_u].sum()
    ca, cb = clicks[~arm_u].sum(), clicks[arm_u].sum()
    fp_view += proportions_ztest([ca, cb], [va, vb])[1] < 0.05
    # by user: per-user click rate, Welch
    r = clicks / views
    fp_user += stats.ttest_ind(r[arm_u], r[~arm_u], equal_var=False).pvalue < 0.05
print(f"A/A false positives: analysed by pageview {fp_view / reps:.3f}, by user {fp_user / reps:.3f}")
```

```text
A/A false positives: analysed by pageview 0.108, by user 0.046
```

The pageview analysis produces twice the false positives, with at most ten views per user. Heavier users make it worse.

## Checking the assignment

Here is Larkspur's experiment, with a true lift of 0.6 points that we know only because we simulated it:

```python
rng = np.random.default_rng(301)
n = 84_000
df = pd.DataFrame({"user_id": ids, "group": arm})
df["device"] = rng.choice(["mobile", "desktop"], n, p=[0.62, 0.38])
base_rate = np.where(df["device"] == "mobile", 0.038, 0.070)
lift = np.where(df["group"] == "B", 0.006, 0.0)
df["converted"] = (rng.random(n) < base_rate + lift).astype(int)
summary = df.groupby("group")["converted"].agg(["sum", "count", "mean"])
print(summary.round(4))
```

```text
        sum  count    mean
group
A      2079  42141  0.0493
B      2335  41859  0.0558
```

Before you look at any outcome, check that the arms have the sizes you designed. This is the sample ratio mismatch (SRM) check, a chi-square goodness-of-fit test on the counts:

```python
def srm_p(counts, expected=(0.5, 0.5)):
    counts = np.asarray(counts, float)
    return stats.chisquare(counts, counts.sum() * np.asarray(expected)).pvalue

print(f"our split {summary['count'].tolist()}: p = {srm_p(summary['count']):.3f}")
print(f"50.4/49.6 on 2M users:     p = {srm_p([1_008_000, 992_000]):.1e}")
print(f"42,400 vs 41,600:          p = {srm_p([42_400, 41_600]):.4f}")
```

```text
our split [42141, 41859]: p = 0.331
50.4/49.6 on 2M users:     p = 1.1e-29
42,400 vs 41,600:          p = 0.0058
```

The result for 50.4/49.6 on two million users should stop you, even though the split looks close to fair. On that many users, a random deviation of that size essentially never happens, so something is removing or adding users in one arm: a redirect that loses mobile traffic, a bot filter that fires differently, a logging bug. The cost of a false alarm is low and the cost of trusting a broken experiment is high, so teams use a strict threshold such as p < 0.001 and treat a failure as disqualifying. An SRM result is not repaired by reweighting, because you do not know which users went missing. You find the cause, fix it and rerun. [Experimentation at scale](03-experimentation-at-scale.md) goes through the causes.

The real dataset behind the AB notebook (`ab_data.csv`, about 290,000 rows, not included in this repo) has a different defect: some users appear in both arms, or on the wrong page for their group. Here is the check against a synthetic table of the same shape, since the notebook's data is not in the repo. Cross-tabulate before anything else:

```python
rng = np.random.default_rng(5)
users = np.arange(290_000)
repeats = rng.choice(users, 3_900, replace=False)
raw = pd.DataFrame({"user_id": np.concatenate([users, repeats])})
raw["group"] = np.where(rng.random(len(raw)) < 0.5, "control", "treatment")
page = np.where(raw["group"] == "control", "old_page", "new_page")
flip = rng.random(len(raw)) < 0.013
raw["landing_page"] = np.where(flip, np.where(page == "old_page", "new_page", "old_page"), page)
print(pd.crosstab(raw["group"], raw["landing_page"]))
seen = raw["user_id"].value_counts()
clean = raw[raw["user_id"].isin(seen[seen == 1].index)]
print(f"rows {len(raw):,}, users seen twice {(seen > 1).sum():,}, rows kept {len(clean):,}")
```

```text
landing_page  new_page  old_page
group
control           1907    145062
treatment       144994      1937
rows 293,900, users seen twice 3,900, rows kept 286,100
```

The off-diagonal cells are mis-assigned rows. Drop every user seen more than once, since you cannot know which exposure they responded to, but ask why it happened first. If the off-diagonal is lopsided, or the duplicates differ between arms, dropping them can introduce bias of its own. The notebook then samples exactly `required_n` from each arm, which is fine for a tutorial, but with a live test you would use everyone.

## Running the test

The test comes last, reporting the lift and its interval before the p-value:

```python
x = summary["sum"].to_numpy()[::-1]
nobs = summary["count"].to_numpy()[::-1]
z, p_val = proportions_ztest(x, nobs)
rb, ra = x / nobs
se = np.sqrt(ra * (1 - ra) / nobs[1] + rb * (1 - rb) / nobs[0])
diff = rb - ra
print(f"A {ra:.4f}  B {rb:.4f}  lift {diff * 100:+.2f} pp")
print(f"95% CI [{(diff - 1.96 * se) * 100:+.2f}, {(diff + 1.96 * se) * 100:+.2f}] pp")
print(f"z = {z:.3f}, p = {p_val:.5f}")
```

```text
A 0.0493  B 0.0558  lift +0.64 pp
95% CI [+0.34, +0.95] pp
z = 4.188, p = 0.00003
```

The notebook also runs `ttest_ind` on the 0/1 outcomes and computes a chi-square by hand. On large samples these all give the same answer. That agreement is a sanity check, but they are not three independent pieces of evidence:

```python
table = np.array([x, nobs - x])
chi2 = stats.chi2_contingency(table, correction=False)
welch = stats.ttest_ind(df.loc[df.group == "B", "converted"], df.loc[df.group == "A", "converted"], equal_var=False)
fisher = stats.fisher_exact(table)
print(f"z^2 = {z ** 2:.3f}, chi-square = {chi2.statistic:.3f}")
print(f"p: z {p_val:.5f}, chi-square {chi2.pvalue:.5f}, Welch {welch.pvalue:.5f}, Fisher {fisher.pvalue:.5f}")
```

```text
z^2 = 17.538, chi-square = 17.538
p: z 0.00003, chi-square 0.00003, Welch 0.00003, Fisher 0.00003
```

| Test on conversion data | When it is the right one |
|---|---|
| two-proportion z | the default for large N |
| chi-square on the 2×2 | identical to z (χ² = z²); generalises to more than two arms |
| Fisher's exact | small N, any expected count < 5 |
| Welch t on 0/1 outcomes | fine at large N; mostly useful when the metric is a mean, not a rate |

Stakeholders usually ask for a relative lift. A relative lift is a ratio, so the interval needs a little care. Kohavi and colleagues point out that you cannot get it by dividing the absolute interval by the control mean, because the control mean is an estimate as well, and they recommend Fieller's method. A log-ratio interval does the same job and takes two lines:

```python
log_ratio = np.log(rb / ra)
se_log = np.sqrt((1 - rb) / (rb * nobs[0]) + (1 - ra) / (ra * nobs[1]))
lo, hi = np.exp(log_ratio - 1.96 * se_log), np.exp(log_ratio + 1.96 * se_log)
print(f"relative lift {rb / ra - 1:+.1%}, 95% CI [{lo - 1:+.1%}, {hi - 1:+.1%}]")
```

```text
relative lift +13.1%, 95% CI [+6.7%, +19.8%]
```

### Deciding from the interval

Compare the interval with the MDE and with zero. The p-value alone cannot distinguish the middle cases, and those are where most tests land:

```python
def read(lo, hi, mde):
    if lo > mde: return "ship: clears the bar"
    if lo > 0:   return "real, maybe below the bar: weigh the cost"
    if hi < 0:   return "harmful: stop"
    if hi < mde: return "flat: no effect worth shipping"
    return "inconclusive: cannot rule out a worthwhile effect"

mde = 0.5
for lo_, hi_ in [(0.6, 1.4), (0.2, 1.0), (-0.1, 0.3), (-0.4, 1.0), (-0.9, -0.2)]:
    print(f"CI [{lo_:+.1f}, {hi_:+.1f}] pp -> {read(lo_, hi_, mde)}")
```

```text
CI [+0.6, +1.4] pp -> ship: clears the bar
CI [+0.2, +1.0] pp -> real, maybe below the bar: weigh the cost
CI [-0.1, +0.3] pp -> flat: no effect worth shipping
CI [-0.4, +1.0] pp -> inconclusive: cannot rule out a worthwhile effect
CI [-0.9, -0.2] pp -> harmful: stop
```

```text
                      0         MDE (+0.5 pp)
                      |           |
ship                  |           |   [=====]
weigh the cost        |      [====|===]
flat                [=|===]       |
inconclusive      [===|===========|==]
harmful     [=====]   |           |
```

Larkspur's interval of [+0.34, +0.95] sits in the second row. The lift is real, and it may or may not clear the bar. "Significant, ship it" would have skipped a real conversation about whether a lift near 0.34 pays for the work. The fourth row is the one that gets misreported. "No significant difference" there means you could not rule out a worthwhile effect, and teams regularly report it as "no effect". Kohavi and colleagues warn that "does not hurt" launches can actually be negative and merely underpowered, and that a migration where you want to retain the null needs a power calculation of its own.

A good report reads: "Treatment converts at 5.58% against 4.93%, a lift of +0.64 points, 95% CI [+0.34, +0.95], p < 0.001. Sample ratio check passes (p = 0.33)."

## What calibration looks like

A/A tests prove the machinery works. Split users with no change at all, and p-values should be uniform, with 5% below 0.05:

```python
rng = np.random.default_rng(11)
reps, nA = 4_000, 5_000
a = rng.binomial(nA, 0.05, reps)
b = rng.binomial(nA, 0.05, reps)
pooled_rate = (a + b) / (2 * nA)
zs = (b - a) / nA / np.sqrt(pooled_rate * (1 - pooled_rate) * 2 / nA)
ps = 2 * stats.norm.sf(np.abs(zs))
print(f"false positive rate at p<.05: {np.mean(ps < 0.05):.3f}")
print("share of p-values per decile:", np.round(np.histogram(ps, bins=10, range=(0, 1))[0] / reps, 3))
```

```text
false positive rate at p<.05: 0.046
share of p-values per decile: [0.1   0.096 0.098 0.108 0.101 0.093 0.099 0.108 0.098 0.098]
```

Run A/A tests continuously on your platform. Each decile holding about a tenth of the p-values is the signature of a test that means what it says. Kohavi and colleagues recommend A/A testing to validate data collection and variance assumptions.

Now break it. The p-value is valid only at the sample size you planned. Check it repeatedly, and stop the first time it dips below 0.05, and the false-positive rate climbs:

```python
rng = np.random.default_rng(7)
reps, n_max, looks = 4_000, 2_000, np.arange(100, 2_001, 100)
a = rng.binomial(1, 0.10, (reps, n_max)).cumsum(axis=1)[:, looks - 1]
b = rng.binomial(1, 0.10, (reps, n_max)).cumsum(axis=1)[:, looks - 1]
pooled_rate = (a + b) / (2 * looks)
z_paths = (b - a) / looks / np.sqrt(pooled_rate * (1 - pooled_rate) * 2 / looks)
print(f"both arms 10%, tested once at the end:  {np.mean(np.abs(z_paths[:, -1]) > 1.96):.3f}")
print(f"both arms 10%, stop at first of 20 looks: {np.mean((np.abs(z_paths) > 1.96).any(axis=1)):.3f}")
```

```text
both arms 10%, tested once at the end:  0.055
both arms 10%, stop at first of 20 looks: 0.250
```

A one-in-four false-positive rate from twenty looks is more than enough to make "we stopped when it hit significance" worthless. The practice notebook shows this with one path crossing the line. This table lists what to do if you cannot wait. The methods are worked through in [experimentation at scale](03-experimentation-at-scale.md):

| If you need to look early | Method |
|---|---|
| a few planned interim looks | group-sequential design with O'Brien-Fleming or Pocock boundaries |
| continuous monitoring | always-valid p-values / mSPRT |
| you want a probability, not a test | [Bayesian A/B](../../04-bayesian-analysis/notes/04-bayesian-ab-testing.md) (peeking is less damaging, not free) |
| you want to stop sending traffic to losers | a [bandit](../../04-bayesian-analysis/notes/03-priors-and-bandits.md) |

## What a test cannot tell you

Kohavi and colleagues list limits that are worth repeating. A test tells you which version won, and not why, so log enough to diagnose. It measures the effect during the test window, so a change whose value builds slowly, or whose novelty fades, is misread. And it can test only what you can build. The same paper also shows the discipline at its most useful, which is killing ideas. MSN ran a test of ads on its home page on 5% of users for 12 days, found click-through down 0.38% in relative terms (p = 0.02), and scrapped an idea people had been sure of. Effects that small are invisible without randomisation.

---

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Novelty or primacy effect | lift fades or grows after week one | run at least one full business cycle; look at lift by days since exposure |
| Network effects | treatment users affect control users (marketplaces, social) | cluster randomisation by region or graph component |
| Multiple metrics | a secondary metric "wins" | one primary metric, correct the rest |
| Segment fishing | "it worked on iOS" | pre-register segments; treat others as hypotheses for the next test |
| Simpson's paradox | arm mix differs across segments | [stratify](04-correlation-and-causation.md) |
| Variance too high | revenue tests never conclude | [CUPED](03-experimentation-at-scale.md): regress out a pre-period covariate |
| Analysing by pageview | noise looks significant | analyse at the unit of randomisation |
| Ignoring SRM | a real-looking result from a broken split | check before reading outcomes, and do not reweight |
| Reading "not significant" as "no effect" | a harmful change launches as harmless | compare the interval with the MDE |
| Stopping at first significance | one in four A/A tests "wins" at 20 looks | fix N, or use a sequential method |

---

## Try it

1. Larkspur's revenue per user has mean 3.30 and SD 40. Use 16σ²/δ² to find users per arm for a 5% change. How does that compare with conversion?
2. An experiment reports 51,000 and 49,000 users. Run the SRM check. What do you do next?
3. Change `unit_bug` so that every user has exactly one pageview. What happens to the pageview false-positive rate, and why?
4. A test has a 95% CI of [−0.2, +0.7] points against an MDE of +0.5. Your PM says "no effect, close it". Reply.

<details>
<summary>Answers</summary>

1. δ = 0.165, so n = 16 × 1600 / 0.165² ≈ 940,000 per arm, about 30 times the conversion plan. That gap is why [metric choice](02-metrics-and-kpi-design.md) matters.
2. `stats.chisquare([51000, 49000])` gives χ² = 40, p about 2.5e-10. Treat the test as broken and do not read its outcomes. Look for the cause by segment, by day and in the funnel, fix it, and rerun.
3. It falls to about 5%, because each user is one row, and the rows are independent. The inflation came entirely from correlated rows within a user.
4. The test could not rule out a lift above the bar, nor a small harm. It is inconclusive. Either accept that and move on for cost reasons, or run longer. "No effect" is not what it found.

</details>

---

## Interview checklist

| Prompt | Answer |
|---|---|
| Why does randomisation allow causal claims? | The coin decides the arm, so no user characteristic, measured or not, can drive both arm and outcome. |
| How do you pick the MDE? | The smallest lift worth the cost of shipping, a business decision, and not a statistical one. |
| What sets sample size? | Baseline variance, the MDE squared, α and power. Rule of thumb: 16σ²/δ² per arm. |
| Conversion or revenue: which needs more users? | Revenue, usually by a lot, because its variance is larger relative to its mean. |
| What is a sample ratio mismatch? | Arm counts differ from the design more than chance allows. Treat the experiment as broken until the cause is found. |
| A test is "not significant". What do you report? | The interval. If it includes the MDE, the test is inconclusive and did not show no effect. |
| Why randomise by user? | One person's rows are correlated, and users should get a consistent experience. Analyse at the same level. |
| Why run whole weeks? | Behaviour varies across the week, and short tests over-represent frequent users. |
| What is an A/A test for? | To confirm the pipeline yields uniform p-values and 5% false positives. |
| Can you stop when it reaches significance? | Not with a fixed-horizon test. Twenty looks gave a false-positive rate of 25% in the simulation. Use a sequential method. |

---

## Further reading

Kohavi et al.'s [survey](https://doi.org/10.1007/s10618-008-0114-1) is the best single paper on this topic. Bruce and Bruce ch. 3 cover experiments from first principles. Reinhart's *Statistics Done Wrong* ch. 2 explains why underpowered results mislead. Everything is listed in [references](../references.md).

---

## Next

[Chapter 2: Metrics and KPI Design](02-metrics-and-kpi-design.md) deals with the choice this chapter made too easily: what to measure. It covers north stars and guardrails, and how a ratio metric can fall while the business improves.
