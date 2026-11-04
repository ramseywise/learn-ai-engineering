# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "scipy"]
# ///
"""Chapter 12: what share of Fernhill's customers are satisfied, and how sure can a survey make us?

Run from this folder with: uv run ch12_surveys.py
"""
import numpy as np
import pandas as pd
from scipy import optimize, stats

from retail import load_survey_frame

pd.set_option("display.width", 130)
RNG = np.random.default_rng(12)

# %% load
frame = load_survey_frame()
N = len(frame)
truth = frame.true_satisfied.mean()
print(N, "customers; true share satisfied", round(truth, 3), "(a survey never sees this)")
print(frame.groupby("segment").agg(customers=("spend", "size"), spend=("spend", "mean"), spend_sd=("spend", "std"),
                                   satisfied=("true_satisfied", "mean"), active=("active", "mean")).round(2).to_string())


# %% blanket
def half_width(p, n):
    """The simple-random-sample 95% half-width: what a dashboard prints as a margin of error."""
    return 1.96 * np.sqrt(p * (1 - p) / n)


sent = frame[frame.emailable]
replied = sent[RNG.random(len(sent)) < sent.true_p_email]
raw = replied.true_satisfied.mean()
print(f"customers {N}; emailable {len(sent)} ({len(sent) / N:.0%}); replies {len(replied)} ({len(replied) / len(sent):.1%} of those sent)")
print(f"answers say {raw:.3f}, plus or minus {half_width(raw, len(replied)):.3f} by the textbook formula")
print(f"true share: everyone {truth:.3f}; emailable {sent.true_satisfied.mean():.3f}; replies {raw:.3f}")
print(f"coverage error {sent.true_satisfied.mean() - truth:+.3f}; nonresponse error {raw - sent.true_satisfied.mean():+.3f}")

# %% allocate
strata = frame.groupby("segment").agg(N_h=("spend", "size"), S_spend=("spend", "std"), S_sat=("true_satisfied", "std"))
n = 1000
plans = pd.DataFrame({"proportional": n * strata.N_h / N,
                      "neyman_spend": n * strata.N_h * strata.S_spend / (strata.N_h * strata.S_spend).sum(),
                      "neyman_satisfied": n * strata.N_h * strata.S_sat / (strata.N_h * strata.S_sat).sum()}).round().astype(int)
print(plans.to_string())


def stratified_se(alloc, S):
    """The stratified estimator's standard error, with the finite population correction in each stratum."""
    W = strata.N_h / N
    return np.sqrt((W**2 * (1 - alloc / strata.N_h) * S**2 / alloc).sum())


fpc = np.sqrt(1 - n / N)  # the finite population correction, explained in the next section
rows = {"simple random": {"spend": fpc * frame.spend.std() / np.sqrt(n), "satisfied": fpc * frame.true_satisfied.std() / np.sqrt(n)}}
for plan in plans:
    rows[plan] = {"spend": stratified_se(plans[plan], strata.S_spend), "satisfied": stratified_se(plans[plan], strata.S_sat)}
print(pd.DataFrame(rows).T.round(4).to_string())

groups = {s: g[["spend", "true_satisfied"]].to_numpy(float) for s, g in frame.groupby("segment")}
reps = []
for _ in range(2000):
    est = np.zeros(2)
    for s, values in groups.items():
        take = values[RNG.choice(len(values), plans.neyman_spend[s], replace=False)]
        est += strata.N_h[s] / N * take.mean(axis=0)
    reps.append(est)
print("Neyman for spend, standard deviation over 2,000 draws:", np.round(np.std(reps, axis=0), 4), "(spend, satisfied)")

# %% fpc
for label, small_n, big_n in [("this survey", 1000, N), ("B2B accounts", 150, 400)]:
    f = small_n / big_n
    print(f"{label}: f = {f:.3f}; standard error multiplied by sqrt(1 - f) = {np.sqrt(1 - f):.3f}")


# %% cluster
def icc(data, group, y):
    """One-way ANOVA estimate of the intra-cluster correlation."""
    by = data.groupby(group)[y]
    k, m = by.ngroups, len(data) / by.ngroups
    between = (by.size() * (by.mean() - data[y].mean())**2).sum() / (k - 1)
    within = ((data[y] - by.transform("mean"))**2).sum() / (len(data) - k)
    return (between - within) / (between + (m - 1) * within)


frame["y"] = frame.true_satisfied.astype(float)
rho = icc(frame, "area", "y")
budget, per_area, per_interview = 12_000, 60, 8
values_by_area = [g.y.to_numpy() for _, g in frame.groupby("area")]
print(f"intra-cluster correlation {rho:.3f}; budget {budget}, {per_area} per area visited, {per_interview} per interview")
rows = []
for m in [5, 10, 15, 20, 40]:
    areas = min(budget // (per_area + per_interview * m), len(values_by_area))
    total = areas * m
    deff = 1 + (m - 1) * rho
    draws = [np.concatenate([values_by_area[a][RNG.choice(len(values_by_area[a]), m, replace=False)]
                             for a in RNG.choice(len(values_by_area), areas, replace=False)]).mean() for _ in range(1500)]
    rows.append({"per_area": m, "areas": areas, "interviews": total, "deff": deff, "effective_n": total / deff,
                 "formula_se": np.sqrt(deff * truth * (1 - truth) / total), "simulated_se": np.std(draws)})
print(pd.DataFrame(rows).round(4).to_string(index=False))


# %% dispositions
def field_survey(rng, size=2000):
    """A proportional stratified sample of the whole frame, chased by email, post and phone."""
    picked = []
    for _, g in frame.groupby("segment"):
        picked.append(g.sample(int(round(size * len(g) / N)), random_state=int(rng.integers(1 << 31))))
    sample = pd.concat(picked)
    return sample, rng.random(len(sample)) < sample.true_p_followup.to_numpy()


sample, answered = field_survey(RNG)
u = RNG.random(len(sample))
complete = answered & (u < .94)
partial = answered & ~complete
refused = ~answered & (u < .25)
no_contact = ~answered & (u >= .25) & (u < .85)
unknown = ~answered & (u >= .85)
I, P, R, NC, UN = complete.sum(), partial.sum(), refused.sum(), no_contact.sum(), unknown.sum()
e = .8
print(f"sampled {len(sample)}: complete {I}, partial {P}, refused {R}, no contact {NC}, unknown eligibility {UN}")
print(f"RR1 {I / (I + P + R + NC + UN):.3f}; RR3 with e = {e}: {I / (I + P + R + NC + e * UN):.3f}; RR6 {(I + P) / (I + P + R + NC):.3f}")

# %% rate_vs_bias
y = frame.true_satisfied.to_numpy(float)


def nonresponse_bias(p):
    """Respondent mean minus population mean: the covariance of the chance of answering with y, over the mean chance."""
    return np.cov(p, y, bias=True)[0, 1] / p.mean()


mailings = {"flat 8%": np.full(N, .08),
            "'tell us what you loved', 42%": .30 + .25 * y,
            "blanket email, all customers": frame.true_p_email.to_numpy(),
            "designed, with reminders": frame.true_p_followup.to_numpy()}
for name, p in mailings.items():
    print(f"{name:32s} response {p.mean():.3f}; bias {nonresponse_bias(p):+.3f}; check {np.average(y, weights=p) - y.mean():+.3f}")


# %% weighting
def rake(data, margins, iterations=500, tolerance=1e-6):
    """Iterative proportional fitting: scale the weights to one margin at a time until all of them hold."""
    w = np.ones(len(data))
    for step in range(iterations):
        start = w.copy()
        for column, target in margins.items():
            codes = data[column].to_numpy()
            for level, share in target.items():
                mask = codes == level
                w[mask] *= share * w.sum() / w[mask].sum()
        if np.abs(w / start - 1).max() < tolerance:
            return w * N / w.sum(), step + 1
    raise RuntimeError("raking did not converge")


def poststratify(data, cells):
    """Weight each cell up to its population count; a population cell with no respondents is simply lost."""
    population = frame.groupby(cells).size().rename("pop")
    held = data.groupby(cells).size().rename("got")
    joined = data[cells].merge(pd.concat([population, held], axis=1).reset_index(), on=cells, how="left")
    missing = population[~population.index.isin(held.index)]
    return (joined["pop"] / joined["got"]).to_numpy(), len(missing), missing.sum()


def kish(w):
    """Kish's 1 + L: the variance inflation from unequal weights alone."""
    return len(w) * (w**2).sum() / w.sum()**2


frame["band"] = pd.qcut(frame.spend, 4, labels=False)
margins = {c: frame[c].value_counts(normalize=True).to_dict() for c in ["channel", "segment", "active", "band"]}
sets = {"channel only": ["channel"], "channel, segment, active": ["channel", "segment", "active"],
        "plus spend band": ["channel", "segment", "active", "band"]}
sent = frame[frame.emailable]
samples = {"blanket email": sent[RNG.random(len(sent)) < sent.true_p_email], "designed": field_survey(RNG)[0]}
samples["designed"] = samples["designed"][RNG.random(len(samples["designed"])) < samples["designed"].true_p_followup]
rows = []
for name, data in samples.items():
    rows.append({"survey": name, "method": "unweighted", "estimate": data.y.mean(), "1+L": 1.0, "effective_n": len(data)})
    for label, columns in sets.items():
        w, steps = rake(data, {c: margins[c] for c in columns})
        rows.append({"survey": name, "method": "rake: " + label, "estimate": np.average(data.y, weights=w), "1+L": kish(w), "effective_n": len(w) / kish(w)})
    w, lost, lost_units = poststratify(data, ["channel", "segment", "active", "band"])
    rows.append({"survey": name, "method": f"cells, {lost} empty, {lost_units} customers lost", "estimate": np.average(data.y, weights=w), "1+L": kish(w), "effective_n": len(w) / kish(w)})
print(f"truth {truth:.3f}")
print(pd.DataFrame(rows).round(3).to_string(index=False))
print("raking steps to converge, designed survey:", rake(samples["designed"], {c: margins[c] for c in sets["plus spend band"]})[1])

# %% trim
data = samples["blanket email"]
w, _ = rake(data, {c: margins[c] for c in sets["plus spend band"]})
rows = []
for cap in [np.inf, 5, 3, 2]:
    v = np.minimum(w, cap * w.mean())
    v = v * N / v.sum()
    rows.append({"cap_times_mean": cap, "largest": v.max() / v.mean(), "1+L": kish(v), "effective_n": len(v) / kish(v), "estimate": np.average(data.y, weights=v)})
print(pd.DataFrame(rows).round(3).to_string(index=False))

# %% margin
columns = sets["plus spend band"]
use = {c: margins[c] for c in columns}
sent = frame[frame.emailable]
results = {"designed": [], "blanket email": []}
draws = np.random.default_rng(2012)
for _ in range(400):
    pick, got = field_survey(draws)
    designed = pick[got]
    blanket = sent[draws.random(len(sent)) < sent.true_p_email]
    for name, data in [("designed", designed), ("blanket email", blanket)]:
        w, _ = rake(data, use)
        results[name].append((len(data), data.y.mean(), np.average(data.y, weights=w), kish(w)))
rows = []
for name, values in results.items():
    a = np.array(values)
    n_, raw_, est, inflate = a.T
    plain = half_width(est, n_)
    adjusted = plain * np.sqrt(inflate)
    rows.append({"survey": name, "respondents": n_.mean(), "mean_raw": raw_.mean(), "mean_raked": est.mean(), "true_sd": est.std(),
                 "plain_margin": plain.mean(), "kish_margin": adjusted.mean(), "covers_plain": (np.abs(est - truth) < plain).mean(),
                 "covers_kish": (np.abs(est - truth) < adjusted).mean()})
print(f"truth {truth:.3f}; 400 repeated surveys")
print(pd.DataFrame(rows).round(3).T.to_string(header=False))

# %% report
data = samples["designed"]
w, _ = rake(data, use)
est, deff = np.average(data.y, weights=w), kish(w)
plain, margin = half_width(est, len(data)), half_width(est, len(data)) * np.sqrt(deff)
print(f"n {len(data)}, weighted {est:.3f}, deff (1+L) {deff:.2f}, deft {np.sqrt(deff):.2f}, margin {margin:.3f} (plain formula {plain:.3f})")
rate = len(data) / 2000
for gap in [0, .05, .10]:
    print(f"if non-respondents are {gap * 100:.0f} points less satisfied than the weighted answers: {rate * est + (1 - rate) * (est - gap):.3f}")
for group, sub in data.groupby("channel"):
    v = w[data.channel.to_numpy() == group]
    p = np.average(sub.y, weights=v)
    print(f"  {group:12s} n {len(sub):4d}  {p:.3f}  margin {half_width(p, len(sub)) * np.sqrt(kish(v)):.3f}")

# %% split_ballot
ballot = frame.sample(4000, random_state=12)
form_b = RNG.random(len(ballot)) < .5
acquiesce = RNG.random(len(ballot)) < .12    # planted in this script: 12% of people agree with whatever is put to them
says_yes = np.where(form_b, ballot.true_satisfied | acquiesce, ballot.true_satisfied)
a, b = says_yes[~form_b].mean(), says_yes[form_b].mean()
se = np.sqrt(a * (1 - a) / (~form_b).sum() + b * (1 - b) / form_b.sum())
print(f"form A, 'how satisfied, 1 to 5?': {a:.3f}; form B, 'I am satisfied: agree or disagree?': {b:.3f}")
print(f"difference {b - a:+.3f}, 95% interval {b - a - 1.96 * se:+.3f} to {b - a + 1.96 * se:+.3f}")
print(f"margin on either form alone about {half_width(a, (~form_b).sum()):.3f}; the margin says nothing about which form is right")

# %% likert
cuts = np.array([1.5, 2.5, 3.5, 4.5])


def answers(mu, sigma, size, rng):
    return np.searchsorted(cuts, rng.normal(mu, sigma, size)) + 1


def fit_probit(scores):
    """Ordered probit with the thresholds pinned at 1.5 to 4.5, so the mean and spread are on the 1-5 scale."""
    counts = np.bincount(scores, minlength=6)[1:]

    def nll(theta):
        mu, log_sigma = theta
        edges = np.concatenate([[-np.inf], cuts, [np.inf]])
        p = np.diff(stats.norm.cdf(edges, mu, np.exp(log_sigma)))
        return -(counts * np.log(np.clip(p, 1e-12, 1))).sum()

    best = optimize.minimize(nll, [scores.mean(), 0.0], method="Nelder-Mead")
    return best.x[0], np.exp(best.x[1])


make = np.random.default_rng(7)
packaging = answers(4.6, 1.0, 500, make)    # consistent answers
delivery = answers(5.4, 2.5, 500, make)     # a higher underlying mean, and a much wider spread
for name, s in [("packaging", packaging), ("delivery", delivery)]:
    shares = np.bincount(s, minlength=6)[1:] / len(s)
    print(f"{name:10s} shares 1-5 {np.round(shares, 2)}  mean {s.mean():.2f}  bottom two {np.mean(s <= 2):.3f}  top box {np.mean(s == 5):.2f}  probit mean, sd {np.round(fit_probit(s), 2)}")
print(f"t test on the means: p = {stats.ttest_ind(packaging, delivery, equal_var=False).pvalue:.3f}; true underlying means are 4.6 and 5.4")
