---
origin: synthesis  # split from 12-surveys-and-sampling-design.md (2026-11-08) so each part stays under the chapter length cap
sources:
  - https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/methods-for-design-effects.pdf (Kish, JOS 1995, full)
  - https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/weighting-methods.pdf (Kalton and Flores-Cervantes, JOS 2003, full)
  - https://aapor.org/wp-content/uploads/2022/11/NPS_TF_Report_Final_7_revised_FNL_6_22_13-2.pdf (AAPOR, 2013, part read)
  - https://aapor.org/standards-and-ethics/disclosure-standards/
  - https://aapor.org/wp-content/uploads/2023/01/Margin-of-Sampling-Error-508.pdf
  - https://www.surveypractice.org/article/2953-practical-considerations-in-raking-survey-data (Battaglia et al., 2009, part read)
  - https://www.pewresearch.org/methods/2018/01/26/for-weighting-online-opt-in-samples-what-matters-most/ (Mercer et al., 2018, main page)
  - https://arxiv.org/abs/2107.08075 (Hartman et al., JRSS A 2024, arXiv version, part read)
  - https://www.nature.com/articles/s41586-021-04198-4 (Bradley et al., Nature 2021, targeted)
  - https://sites.stat.columbia.edu/gelman/research/unpublished/forecasting-with-nonrepresentative-polls.pdf (Wang et al., author's preprint, part read)
  - https://www.pewresearch.org/writing-survey-questions/
  - https://www.pewresearch.org/short-reads/2015/05/14/where-web-surveys-produce-different-results-than-phone-interviews/
  - https://www.pewresearch.org/short-reads/2016/09/08/understanding-the-margin-of-error-in-election-polls/
  - https://ojs.ub.uni-konstanz.de/srm/article/view/2682 (Saris et al., SRM 2010, part read)
  - https://pure.uva.nl/ws/files/2653460/169196_506179.pdf (Lelkes and Weiss, 2015, part read)
  - https://link.springer.com/article/10.1007/s11135-017-0533-4 (DeCastellarnau, 2018, excerpts)
  - https://osf.io/9h3et/ (Liddell and Kruschke, 2018, authors' draft, part read)
  - https://link.springer.com/article/10.1007/s10459-010-9222-y (Norman, 2010, abstract only)
  - https://link.springer.com/article/10.1007/s11135-022-01489-4 (Lenzner et al., 2023)
  - https://census.gov/about/policies/quality/standards/appendixa2.html
  - practice/retail.py (Fernhill synthetic tables, run against this chapter's script)
confidence: medium
cleaned: 2026-11-08
---

# 12b — Weighting, the margin and the question

Fernhill's email blast said 73% satisfied with a margin of plus or minus 1.7 points, against a truth of 49.6%. [Part one](12-surveys-and-sampling-design.md) drew a designed sample and chased its nonresponse, but the people who answered still differ from the customer list, and the questions they answered may not mean what the report says. This part repairs the first with weights, states the margin the design actually earns, and examines the second: question wording, and what a mean of a five-point scale hides.

> The second half of surveys and sampling design. [12](12-surveys-and-sampling-design.md) covered the frame, strata, clusters and nonresponse. Here: post-stratification and raking, design effects, measurement error and Likert scales, then the recommendation for the whole chapter. It continues the same `practice/ch12_surveys.py` script and the same `load_survey_frame()` table.

---

## Weighting: post-stratification, raking and their limit

Weighting makes respondents add up to known population totals. An analyst has an advantage over a pollster here: those totals come from the CRM exactly, not from a census estimate.

**Post-stratification** cross-classifies the **auxiliary variables**, the columns you know for both respondents and the whole population, then weights each cell up to its population count. It's clean until cells run out. **Raking**, or iterative proportional fitting, matches each variable's population shares in turn (its **margin**, nothing to do with a margin of error) and repeats until all of them hold, so it needs only the margins and no cross-classification. [Kalton and Flores-Cervantes](https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/weighting-methods.pdf) (*Journal of Official Statistics*, 2003) give the trade: raking assumes response probabilities multiply across the variables, which is an additional assumption and "leads to less variability in the weights". They suggest cells when there are few and they're well filled, and raking when there are many. They count the variance cost as 1 plus the squared coefficient of variation of the weights, the same quantity as [Kish](https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/methods-for-design-effects.pdf)'s factor for unequal weights, $1 + L = n\sum w^2 / (\sum w)^2$, where $L$ is the relative variance of the weights. They warn it "does not apply for weighting adjustments that benchmark survey estimates to population values", and Kish offers it as an assumption for haphazard weights, so treat it here as a rough measure of cost. Effective sample then follows as $n / (1 + L)$, a form neither prints, [the same quantity](../../03-experimentation-and-causality/notes/05-matching-and-weighting.md#judging-the-designs) the matching chapter uses.

```python
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
```

```text
truth 0.496
       survey                              method  estimate   1+L  effective_n
blanket email                          unweighted     0.725 1.000     2648.000
blanket email                  rake: channel only     0.699 1.140     2323.607
blanket email      rake: channel, segment, active     0.667 1.755     1508.861
blanket email               rake: plus spend band     0.666 1.763     1502.006
blanket email   cells, 5 empty, 62 customers lost     0.666 1.907     1388.247
     designed                          unweighted     0.514 1.000      966.000
     designed                  rake: channel only     0.511 1.005      961.185
     designed      rake: channel, segment, active     0.499 1.033      935.207
     designed               rake: plus spend band     0.499 1.034      934.125
     designed cells, 11 empty, 325 customers lost     0.498 1.095      882.164
raking steps to converge, designed survey: 29
```

Variables matter more than method: raking on channel alone moves the email figure 2.6 points, adding segment and active moves it about 6, and raking, then cells, land on the same number. Kalton and Flores-Cervantes say this too: the choice of auxiliaries, and of how they're used, "may be of more significance than the choice of a particular method". Weights cost precision: the email's effective sample fell from 2,648 to about 1,500. And cells lose people: 62 and 325 customers sat in cells where nobody answered, so those estimates no longer cover them.

The designed survey's 49.9% looks nearly perfect. Be suspicious of that, since the repeat runs below show it's a lucky draw. The email's 66.6% is still 17 points out. Most of what's left is the part where satisfaction itself drives replying, and no CRM column holds it. [Pew's study of opt-in panels](https://www.pewresearch.org/methods/2018/01/26/for-weighting-online-opt-in-samples-what-matters-most/) (Mercer, Lau and Kennedy, 2018; not peer-reviewed) found the same on real data: across 24 benchmarks and over 30,000 interviews, the best adjustment "was only able to remove about 30% of the original bias", and complex methods never beat simpler ones by more than 0.3 points on average. Bradley et al. reach the same conclusion: "Weighting on observed covariates alone cannot explain or correct the discrepancies we observe."

The counterexample is [the Xbox poll](https://sites.stat.columbia.edu/gelman/research/unpublished/forecasting-with-nonrepresentative-polls.pdf) (Wang, Rothschild, Goel and Gelman; author's preprint, published in *International Journal of Forecasting*, 2015). Men were 93% of the Xbox sample (750,148 interviews) against 47% of the electorate, and yet the day-before estimate of voter intent was 0.6 points from the result. It used [partial pooling](../../04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling.md) over 176,256 cells, and those cells included party identification and past vote. The variables held the selection. Raking should also look familiar: its distance is the one [entropy balancing](../../03-experimentation-and-causality/notes/05-matching-and-weighting.md#entropy-balancing) uses ([Hartman, Hazlett and Sterbenz](https://arxiv.org/abs/2107.08075), *J. R. Stat. Soc. A*, 2024; arXiv version read).

Extreme weights invite **trimming**, which caps them and spreads the excess over everyone else:

```python
data = samples["blanket email"]
w, _ = rake(data, {c: margins[c] for c in sets["plus spend band"]})
rows = []
for cap in [np.inf, 5, 3, 2]:
    v = np.minimum(w, cap * w.mean())
    v = v * N / v.sum()
    rows.append({"cap_times_mean": cap, "largest": v.max() / v.mean(), "1+L": kish(v), "effective_n": len(v) / kish(v), "estimate": np.average(data.y, weights=v)})
print(pd.DataFrame(rows).round(3).to_string(index=False))
```

```text
 cap_times_mean  largest   1+L  effective_n  estimate
            inf    4.997 1.763     1502.006     0.666
            5.0    4.997 1.763     1502.006     0.666
            3.0    3.135 1.564     1692.665     0.673
            2.0    2.254 1.401     1889.719     0.681
```

A cap of 2 raises the email's effective sample by about 26% and moves the estimate 1.5 points further from the truth. Kalton and Flores-Cervantes describe that bargain: "accepting some possible loss in bias reduction". [Battaglia, Hoaglin and Frankel](https://www.surveypractice.org/article/2953-practical-considerations-in-raking-survey-data) (*Survey Practice*, 2009) say raking generally converges in 3 to 10 iterations and give no numeric rule for the bounds. Our run took 29, since segment and spend band overlap heavily and the tolerance is tight.

## Reporting a margin that reflects the design

This frame can check itself. Run the whole thing 400 times, weight each one, and mark the intervals:

```python
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
```

```text
truth 0.496; 400 repeated surveys
survey        designed  blanket email
respondents    917.928        2601.93
mean_raw         0.542          0.733
mean_raked       0.528          0.678
true_sd          0.016          0.012
plain_margin     0.032          0.018
kish_margin      0.033          0.023
covers_plain     0.525            0.0
covers_kish      0.548            0.0
```

The margin is right about what it measures. For the designed survey the raked estimates have a standard deviation of 0.016, so 1.96 of those is 0.031, close to the 0.033 reported. But those intervals cover the truth only about 55% of the time, since they're centred on 52.8% rather than 49.6%: the bias left after weighting is as large as the margin. The email's intervals never cover it. Raking took out about 30% of the designed survey's bias and 23% of the email's (my arithmetic on the rows above). So the margin answers "how much would this wobble?". It says nothing about "how far off is it?".

Adjust the margin for the design all the same. **Deff** is the ratio of the actual variance to a simple random sample's, and **deft** is its square root, near enough (Kish keeps a finite population factor in deff only, and calls the difference "commonly trivial"). Kish prefers deft first because it's "in the same units as the factors in the intervals", and his warning shows why it matters: a deft of 3 turns a claimed $t = 2$ at $\alpha = .05$ into $t = 2/3$ at $\alpha = 0.50$. So the margin is $1.96 \times \text{deft} \times \sqrt{p(1-p)/n}$, or the plain formula with $n$ replaced by the effective sample. For weighting alone, this chapter lets 1 + L stand in for deff. It's an approximation that ignores clustering: Kish reserves it for haphazard weights, says deliberate oversampling needs other treatment, and has no simple answer for post-stratification.

```python
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
```

```text
n 966, weighted 0.499, deff (1+L) 1.03, deft 1.02, margin 0.032 (plain formula 0.032)
if non-respondents are 0 points less satisfied than the weighted answers: 0.499
if non-respondents are 5 points less satisfied than the weighted answers: 0.473
if non-respondents are 10 points less satisfied than the weighted answers: 0.447
  email        n  144  0.654  margin 0.079
  organic      n  351  0.535  margin 0.053
  paid_social  n  354  0.401  margin 0.052
  referral     n  117  0.526  margin 0.092
```

Subgroups get wide fast: the referral margin is 9.2 points on 117 people. A gap between groups needs its own margin. Paid social against organic is 13.4 points, with a margin of about 7.4 (my arithmetic: the root of the two squared margins, for independent groups). Between two candidates' shares on the same question, [Pew](https://www.pewresearch.org/short-reads/2016/09/08/understanding-the-margin-of-error-in-election-polls/) says it's "about twice" a single candidate's.

The three "if non-respondents" lines are a sensitivity check. In this frame the real gap works out at about 6 points (my arithmetic, from a mean raked estimate of 52.8% against 49.6% at a 46% response rate), and the second line is close to that.

[AAPOR's code](https://aapor.org/standards-and-ethics/disclosure-standards/) (revised 2021) requires disclosure of "whether or not the reported sampling error or statistical analyses have been adjusted for the design effect", how weights were calculated, and the unweighted sample sizes behind subgroups. It allows precision measures for non-probability samples only with a description of the underlying model.

## The question itself: measurement error

Everything above assumes the answer means what you think. Wording alone moved a real result by 25 points. [Pew's methods page](https://www.pewresearch.org/writing-survey-questions/) reports a January 2003 survey: 68% favoured military action against Iraq when asked plainly, and 43% when the question added "even if it meant that U.S. forces might suffer thousands of casualties". Order moves answers too: dissatisfaction with the country was 88% straight after a question on presidential approval, 78% without it.

The usual faults follow. **Acquiescence** is the tendency to agree with whatever is put to you.

| Fault | Example | Fix |
|---|---|---|
| Double-barrelled | "How happy were you with the speed and care of delivery?" | Ask one thing per question |
| Acquiescence | "Delivery was on time: agree or disagree?" | Offer a choice between statements |
| Social desirability | An interviewer asks whether the driver was rude | Self-administer, or use [randomised response](../../04-bayesian-analysis/notes/01-bayesian-inference.md#the-survey-nobody-answers-honestly) |
| Order | Overall rating asked after a list of complaints | Overall first; rotate the items |

Acquiescence has the best evidence against it. [Saris, Revilla, Krosnick and Shaeffer](https://ojs.ub.uni-konstanz.de/srm/article/view/2682) (*Survey Research Methods*, 2010) ran split-ballot experiments in the European Social Survey and found agree/disagree items "had much lower quality" than item-specific versions, which offer answers specific to the thing asked: on one immigration item (23-country means), .85 in the main questionnaire and .76 in the supplement against .48 (5-point; .44 at 7 points), where quality is a model-based product of reliability and validity. [Lelkes and Weiss](https://pure.uva.nl/ws/files/2653460/169196_506179.pdf) (*Research & Politics*, 2015) qualify that: on one US political efficacy battery they found the two formats equally valid. On scale length, [DeCastellarnau](https://link.springer.com/article/10.1007/s11135-017-0533-4) (*Quality & Quantity*, 2018) concludes from the literature, in line with Cox (1980), that no single number is best, and that labelling every point generally helps reliability, though it raises acquiescence.

Mode matters too. [Keeter at Pew](https://www.pewresearch.org/short-reads/2015/05/14/where-web-surveys-produce-different-results-than-phone-interviews/) (2015) reports randomly assigned phone and web groups differing by 5.5 points on average across 60 questions.

The tool for all of this is the **split ballot**: randomise which version each person gets, and it becomes an experiment on the question.

```python
ballot = frame.sample(4000, random_state=12)
form_b = RNG.random(len(ballot)) < .5
acquiesce = RNG.random(len(ballot)) < .12    # planted in this script: 12% of people agree with whatever is put to them
says_yes = np.where(form_b, ballot.true_satisfied | acquiesce, ballot.true_satisfied)
a, b = says_yes[~form_b].mean(), says_yes[form_b].mean()
se = np.sqrt(a * (1 - a) / (~form_b).sum() + b * (1 - b) / form_b.sum())
print(f"form A, 'how satisfied, 1 to 5?': {a:.3f}; form B, 'I am satisfied: agree or disagree?': {b:.3f}")
print(f"difference {b - a:+.3f}, 95% interval {b - a - 1.96 * se:+.3f} to {b - a + 1.96 * se:+.3f}")
print(f"margin on either form alone about {half_width(a, (~form_b).sum()):.3f}; the margin says nothing about which form is right")
```

```text
form A, 'how satisfied, 1 to 5?': 0.517; form B, 'I am satisfied: agree or disagree?': 0.563
difference +0.046, 95% interval +0.015 to +0.077
margin on either form alone about 0.022; the margin says nothing about which form is right
```

The 12% acquiescence is planted in the script. Form B reads 4.6 points higher, and both forms come with a tidy margin of 2.2 points. Only the comparison shows the problem.

Before any of this, pretest. The [US Census Bureau's quality standards](https://census.gov/about/policies/quality/standards/appendixa2.html) accept cognitive interviews, where a respondent talks through how they understand and answer each question, and note that "as few as fifteen" can reveal major problems if respondents keep flagging the same questions. Expert review alone is allowed only as a last resort. [Lenzner, Hadler and Neuert](https://link.springer.com/article/10.1007/s11135-022-01489-4) (*Quality & Quantity*, 2023) tested one question this way: ten interviews found a real ambiguity, but the rewritten version didn't improve criterion validity and improved content validity only in part, so split-ballot the fix.

## Reading a five-point scale

A 1-to-5 answer is [ordinal](../../02-probability-and-statistics/notes/01-descriptive-statistics-and-eda.md), and averaging it assumes the gap from 4 to 5 equals the gap from 1 to 2. [Liddell and Kruschke](https://osf.io/9h3et/) (*Journal of Experimental Social Psychology*, 2018; authors' draft read) checked 68 psychology articles using Likert outcomes (ratings on an ordered scale) and found every one treated them as metric: plain numbers with equal gaps. In their worked examples, with settings they picked to show the problem, the metric model reported a standardised effect of 0.49 where none existed and of −0.01 where the true effect was 0.66. An **ordered probit** recovered both: it assumes a hidden continuous score, cut at thresholds into the answers, so gaps needn't be equal and the hidden mean can sit above 5. Averaging several items didn't help. [Norman](https://link.springer.com/article/10.1007/s10459-010-9222-y) (*Advances in Health Sciences Education*, 2010; abstract read only) argues parametric methods are robust on such data. Liddell and Kruschke answer that such earlier work didn't test unequal variability or means near one end of the scale, the cases where they find inflated false alarms, so look at the shares.

```python
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
```

```text
packaging  shares 1-5 [0.   0.01 0.14 0.34 0.5 ]  mean 4.33  bottom two 0.014  top box 0.50  probit mean, sd [4.5  0.96]
delivery   shares 1-5 [0.06 0.05 0.09 0.15 0.65]  mean 4.29  bottom two 0.106  top box 0.65  probit mean, sd [5.48 2.44]
t test on the means: p = 0.567; true underlying means are 4.6 and 5.4
```

Delivery and packaging tie on the mean (4.29, 4.33; $p = 0.57$). They aren't alike. Delivery has more top scores, 65% against 50%, and about seven and a half times the bottom-two share, 10.6% against 1.4%. An ordered probit with its thresholds pinned sees delivery's underlying mean as about a point higher and its spread two and a half times as wide, which is near what we planted. "Average 4.3 on both" would have hidden a delivery problem affecting one customer in nine. Report the shares, and use [rank tests](../../02-probability-and-statistics/notes/05-hypothesis-testing.md) or an ordinal model if you need a test.

## Recommendation

Stop publishing 73%. Run the designed survey: a proportional stratified sample of the whole customer list by order segment, a questionnaire that was split-ballot tested, with reminders across email, post and phone. Rake to channel, segment and activity from the CRM. Report it as **about 50% satisfied, plus or minus 3 points of sampling error, on 966 answers from 2,000 sampled (a 48% completed share), weighted to CRM totals, with a further unmeasured risk: if non-respondents are 5 points less satisfied, the figure is 47%.** Add shares by channel, with paid social's 40.1% flagged and its own margin of 5.2.

What would change this: a follow-up with a random subsample of non-respondents, the only way to measure the gap directly, and a repeat of the survey to track it over time. A change of mode or wording breaks the series.

## Practice

Run `uv run ch12_surveys.py` from `practice/`, which takes under a minute. It needs numpy, pandas and scipy. `latent` in `SURVEY_DGP` in `retail.py` sets how much satisfaction itself drives replying. Change it in `followup_logit` to move the designed survey's rows, and in `email_logit` to move the email's. At 0 in `email_logit`, the email's fully raked figure falls from 66.6% to 49.3%.

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Plain margin after weighting or clustering | Intervals too narrow | Multiply by deft; say that you did |
| Taking a weighted number as debiased | Rows agree with each other, and all miss the truth | State the unmeasured risk; follow up a sample of non-respondents |

## Try it

1. Rake the blanket email on channel and segment only, without `active`. How much does it lose?

<details><summary>Answer</summary>

69.1% with 1 + L of 1.20, against 66.7% and 1.76 when `active` is included. Dropping a variable that predicts answering costs 2.4 points of repair and saves variance.
</details>

2. Five respondents have weights 1, 1, 1, 1 and 4. What are 1 + L and the effective sample?

<details><summary>Answer</summary>

$1 + L = 5 \times 20 / 8^2 = 1.5625$, and the effective sample is $5 / 1.5625 = 3.2$.
</details>

## Interview checklist

| Question | Answer |
|---|---|
| Post-stratification or raking? | Cells when few and well filled; raking for many variables or only margins. Raking assumes no interaction in response |
| What can't weighting fix? | Selection on anything the auxiliaries don't hold, including the answer itself. Pew's best adjustment removed about 30% of opt-in bias |
| What's Kish's 1 + L? | Variance inflation from unequal weights, assuming they're haphazard. Effective sample then follows as n / (1 + L) |
| Deff or deft? | Deff is the variance ratio; deft its root, on the scale of the standard error. Multiply the margin by deft |
| Mean of a Likert item? | It assumes equal gaps and can hide a tail, so report the shares and use an ordinal model or a rank test |
| How do you test a question? | Cognitive interviews to find problems, then a split ballot to measure the fix |

## Next

That's the last of the applied analyses. Go on to [data science](../../../data-science/README.md), which takes up the models behind these analyses in depth.
