---
origin: synthesis
sources:
  - "Statistics Canada, Survey Methods and Practices, cat. 12-587-X, 2003 (sections on sampling, allocation and the finite population correction read)"
  - https://www150.statcan.gc.ca/n1/en/pub/12-587-x/12-587-x2003001-eng.pdf
  - "Kish, Methods for Design Effects, Journal of Official Statistics 11(1), 1995 (read in full)"
  - https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/methods-for-design-effects.pdf
  - "Kalton and Flores-Cervantes, Weighting Methods, Journal of Official Statistics 19(2), 2003 (body read)"
  - https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/weighting-methods.pdf
  - "United Nations, Designing Household Survey Samples, Series F No. 98, 2008 (sections on clusters and design effects read)"
  - https://unstats.un.org/unsd/publication/seriesf/seriesf_98e.pdf
  - "AAPOR Task Force on Non-Probability Sampling, report, 2013 (executive summary and section 7 read)"
  - https://aapor.org/wp-content/uploads/2022/11/NPS_TF_Report_Final_7_revised_FNL_6_22_13-2.pdf
  - "AAPOR, Standard Definitions, 10th edition, 2023 (response rate pages read)"
  - https://aapor.org/wp-content/uploads/2023/05/Standards-Definitions-10th-edition.pdf
  - https://aapor.org/standards-and-ethics/disclosure-standards/
  - https://aapor.org/wp-content/uploads/2023/01/Margin-of-Sampling-Error-508.pdf
  - "Biemer, Total Survey Error, Public Opinion Quarterly 74(5) (part read)"
  - https://academic.oup.com/poq/article-lookup/doi/10.1093/poq/nfq058
  - "Groves, Nonresponse Rates and Nonresponse Bias in Household Surveys, Public Opinion Quarterly 70(5), 2006 (part read)"
  - https://academic.oup.com/poq/article/70/5/646/4084443
  - "Brick and Tourangeau, Responsive Survey Designs for Reducing Nonresponse Bias, Journal of Official Statistics 33(3), 2017 (part read; source of the Groves and Peytcheva 2008 figure, whose full text was not read)"
  - https://reference-global.com/download/article/10.1515/jos-2017-0034.pdf
  - "Brick, Unit Nonresponse and Weighting Adjustments, Journal of Official Statistics 29(3), 2013 (part read)"
  - https://reference-global.com/download/article/10.2478/jos-2013-0026.pdf
  - "Battaglia, Hoaglin and Frankel, Practical Considerations in Raking Survey Data, Survey Practice 2(5), 2009 (part read)"
  - https://www.surveypractice.org/article/2953-practical-considerations-in-raking-survey-data
  - "Mercer, Lau and Kennedy, For Weighting Online Opt-In Samples, What Matters Most?, Pew Research Center, 2018 (main page read)"
  - https://www.pewresearch.org/methods/2018/01/26/for-weighting-online-opt-in-samples-what-matters-most/
  - "Hartman, Hazlett and Sterbenz, arXiv:2107.08075 (preprint, part read)"
  - https://arxiv.org/abs/2107.08075
  - "Bradley et al., Unrepresentative big surveys significantly overestimated US vaccine uptake, Nature 600, 2021 (targeted read)"
  - https://www.nature.com/articles/s41586-021-04198-4
  - "Wang, Rothschild, Goel and Gelman, Forecasting elections with non-representative polls (author-hosted preprint read; published in International Journal of Forecasting 31, 2015, not read)"
  - https://sites.stat.columbia.edu/gelman/research/unpublished/forecasting-with-nonrepresentative-polls.pdf
  - "Pew Research Center, Writing Survey Questions (methods page)"
  - https://www.pewresearch.org/writing-survey-questions/
  - https://www.pewresearch.org/short-reads/2015/05/14/where-web-surveys-produce-different-results-than-phone-interviews/
  - https://www.pewresearch.org/short-reads/2016/09/08/understanding-the-margin-of-error-in-election-polls/
  - https://www.pewresearch.org/race-and-ethnicity/2025/11/03/census-measuring-race-methodology/
  - "Saris, Revilla, Krosnick and Shaeffer, Comparing Questions with Agree/Disagree Response Options to Questions with Item-Specific Response Options, Survey Research Methods 4(1), 2010 (part read)"
  - https://ojs.ub.uni-konstanz.de/srm/article/view/2682
  - "Lelkes and Weiss, Research & Politics 2(3), 2015 (part read)"
  - https://pure.uva.nl/ws/files/2653460/169196_506179.pdf
  - "DeCastellarnau, A classification of response scale characteristics that affect data quality, Quality & Quantity 52, 2018 (excerpts read)"
  - https://link.springer.com/article/10.1007/s11135-017-0533-4
  - "Liddell and Kruschke, Analyzing ordinal data with metric models, Journal of Experimental Social Psychology 79, 2018 (authors' draft read, published text not compared)"
  - https://osf.io/9h3et/
  - "Norman, Likert scales, levels of measurement and the laws of statistics, Advances in Health Sciences Education 15, 2010 (abstract only)"
  - https://link.springer.com/article/10.1007/s10459-010-9222-y
  - "Lenzner, Hadler and Neuert, Quality & Quantity 57, 2023"
  - https://link.springer.com/article/10.1007/s11135-022-01489-4
  - https://census.gov/about/policies/quality/standards/appendixa2.html
  - practice/retail.py (Fernhill synthetic tables, run against this chapter's script)
confidence: medium
cleaned: 2026-11-03
---

# Surveys and sampling design: who you ask, what you ask, and what the answer is worth

Fernhill emailed everyone it could about their last delivery, and 2,573 people replied. 73.0% said they were satisfied, and the dashboard printed a margin of plus or minus 1.7 points. Fernhill's customers are synthetic, so we can look up the truth: 49.6%. That error is more than 13 times the margin, and no amount of extra replies would have shrunk it. It also isn't a flaw in the formula, which answered exactly the question it was given: how far would a random sample of this size wander? This wasn't a random sample. This chapter is about building one that is, repairing what goes wrong in the field, stating honestly what's left, and writing questions whose answers mean what you think they mean.

## The question and the data

The business question is **what share of Fernhill's customers are satisfied with delivery, and how sure can a survey make us?** It's an estimate of a population number, not a causal claim, so it sits apart from [experiments](../../03-experimentation-and-causality/README.md), and it borrows a lot from earlier chapters. [Why a big sample doesn't help](../../02-probability-and-statistics/notes/07-data-generating-process.md#big-is-not-the-same-as-representative) is Meng's result and stays there. [The half-width of an interval on a proportion](../../02-probability-and-statistics/notes/04-estimation.md) is what a survey calls its margin of error. [Propensity weights and effective sample size](../../03-experimentation-and-causality/notes/05-matching-and-weighting.md#judging-the-designs) carry over. What's new is the design before the data exists, and the repair after it comes back short.

One table is used, **`load_survey_frame()`** from `practice/retail.py`: one row per customer who has ordered, with what the CRM knows (channel, order count, spend, whether they ordered in 2025, whether they can be emailed, a postcode area) and, in `true_` columns, the answer they'd give and their chance of giving it. All of it is synthetic, and the answers lean on the CRM columns and also, a little, on satisfaction itself. A real survey has no `true_` columns, which is why having them here is useful: every method gets marked.

The code blocks are the sections of `practice/ch12_surveys.py` in order, each relying on those before it. Run them with `uv run ch12_surveys.py` from the practice folder.

```python
frame = load_survey_frame()
N = len(frame)
truth = frame.true_satisfied.mean()
print(N, "customers; true share satisfied", round(truth, 3), "(a survey never sees this)")
print(frame.groupby("segment").agg(customers=("spend", "size"), spend=("spend", "mean"), spend_sd=("spend", "std"),
                                   satisfied=("true_satisfied", "mean"), active=("active", "mean")).round(2).to_string())
```

```text
26342 customers; true share satisfied 0.496 (a survey never sees this)
         customers   spend  spend_sd  satisfied  active
segment
few           6274  120.93     70.64       0.49    0.51
many          4043  438.56    383.69       0.65    0.67
one          16025   51.97     37.98       0.46    0.49
```

Few customers order often, and those few spend far more and are happier. Keep the three segments in mind: they drive everything below.

## Frame, coverage and the errors a margin can't see

A survey has three populations. The **target** is who you want to know about: every customer. The **frame** is the list you can draw from: the emailable ones. The **sample** is who you select from the frame, and the **respondents** are who answer. Each gap has a name.

```mermaid
flowchart LR
    T[Target: every customer] -->|coverage error| F[Frame: the list you can reach]
    F -->|sampling error| S[Sample: who you select]
    S -->|nonresponse error| R[Respondents: who answer]
    R -->|measurement error| A[Answers: what they say]
```

Biemer defines [total survey error](https://academic.oup.com/poq/article-lookup/doi/10.1093/poq/nfq058) (*Public Opinion Quarterly*) as "the accumulation of all errors that may arise in the design, collection, processing, and analysis of survey data". The [AAPOR task force on non-probability sampling](https://aapor.org/wp-content/uploads/2022/11/NPS_TF_Report_Final_7_revised_FNL_6_22_13-2.pdf) (2013) groups the first three gaps as errors of non-observation. A margin of error measures only one of them, the sampling step. [AAPOR's fact sheet](https://aapor.org/wp-content/uploads/2023/01/Margin-of-Sampling-Error-508.pdf) says it flatly: "There is no such thing as a measurable overall margin of error for a poll".

The blanket email splits its error across the gaps:

```python
def half_width(p, n):
    """The simple-random-sample 95% half-width: what a dashboard prints as a margin of error."""
    return 1.96 * np.sqrt(p * (1 - p) / n)


sent = frame[frame.emailable]
replied = sent[RNG.random(len(sent)) < sent.true_p_email]
raw = replied.true_satisfied.mean()
print(f"frame {N}; emailable {len(sent)} ({len(sent) / N:.0%}); replies {len(replied)} ({len(replied) / len(sent):.1%} of those sent)")
print(f"answers say {raw:.3f}, plus or minus {half_width(raw, len(replied)):.3f} by the textbook formula")
print(f"true share: everyone {truth:.3f}; emailable {sent.true_satisfied.mean():.3f}; replies {raw:.3f}")
print(f"coverage error {sent.true_satisfied.mean() - truth:+.3f}; nonresponse error {raw - sent.true_satisfied.mean():+.3f}")
```

```text
frame 26342; emailable 15981 (61%); replies 2573 (16.1% of those sent)
answers say 0.730, plus or minus 0.017 by the textbook formula
true share: everyone 0.496; emailable 0.521; replies 0.730
coverage error +0.025; nonresponse error +0.209
```

Coverage cost 2.5 points and nonresponse 20.9. Neither shrinks if you send more email. That's the AAPOR report's point too: bias "is not a function of the sample size".

A **probability sample** is what makes the sampling step measurable. [Statistics Canada's *Survey Methods and Practices*](https://www150.statcan.gc.ca/n1/en/pub/12-587-x/12-587-x2003001-eng.pdf) requires that "all units in the survey population have a non-zero inclusion probability in the sample and that these probabilities can be calculated". It adds: "It is not necessary for all units to have the same inclusion probability". Our email fails that test twice. Nobody chose who replied, and 39% of customers had no chance at all. For samples like that, the AAPOR report suggests "exclusion bias" as the better name than coverage bias, and AAPOR's fact sheet says a margin of sampling error "does not apply to opt-in online surveys and other non-probability based polls".

The evidence that size doesn't rescue this is large-scale. [Bradley et al.](https://www.nature.com/articles/s41586-021-04198-4) (*Nature*, 2021) compared US COVID-19 first-dose estimates with the CDC benchmark. Delphi-Facebook, with about 250,000 responses a week, overestimated uptake by 17 points in May 2021. Axios-Ipsos, with about 1,000 a week and careful panel recruitment, overestimated it by 4.2. By their reckoning Delphi-Facebook's effective sample in April 2021 was under 10.

## Strata and allocation: where to spend a fixed sample

Fernhill can do better. It has the whole customer list, so it can draw from it directly and chase people by email, post and phone. Budget buys 1,000 interviews before nonresponse. A simple random sample would work, but we already know which customers differ, so we can **stratify**: split the frame into groups and sample each one separately. No draw can then come up short on heavy buyers.

The remaining choice is how many from each stratum. **Proportional allocation** gives each stratum its population share, so every customer has the same chance. Statistics Canada says it's "never worse than simple random sampling". **Neyman allocation** gives more to the strata that vary more: $n_h = n \cdot N_h S_h / \sum_k N_k S_k$, where $N_h$ is the stratum's size and $S_h$ its standard deviation. Statistics Canada describes it as the special case of optimum allocation for equal interview costs, and as minimising the overall variance. Its catch is that $S_h$ is for one statistic:

```python
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


rows = {"simple random": {"spend": frame.spend.std() / np.sqrt(n), "satisfied": frame.true_satisfied.std() / np.sqrt(n)}}
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
```

```text
         proportional  neyman_spend  neyman_satisfied
segment
few               238           170               240
many              153           596               148
one               608           234               612
                   spend  satisfied
simple random     6.5566     0.0158
proportional      4.8783     0.0154
neyman_spend      2.9714     0.0218
neyman_satisfied  4.9546     0.0154
Neyman for spend, standard deviation over 2,000 draws: [3.0459 0.0213] (spend, satisfied)
```

Stratifying proportionally cut the standard error on spend from 6.56 to 4.88 and barely moved satisfaction, from 0.0158 to 0.0154, since satisfaction differs little between segments. Neyman for spend cut spend's further, to 2.97, by putting 596 of the 1,000 interviews on heavy buyers. It also raised satisfaction's standard error by about 42%, to 0.0218. [Kish](https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/methods-for-design-effects.pdf) (*Journal of Official Statistics*, 1995) reports the same thing on real data: "an 'optimal allocation' for mean incomes resulted in losses for median incomes". For a share near one half, $S_h$ barely varies, so Neyman lands on nearly proportional, which the table shows too. The 2,000 repeated draws sit close to the formula, at 3.05 and 0.0213.

A survey asks many questions, so we take proportional here. Disproportionate allocation earns its keep when one number matters most, or when a small stratum needs its own estimate.

The formula has a factor we can usually ignore. The **finite population correction** multiplies the variance by $1 - f$, where $f = n/N$, because a sample that uses up the population leaves less to be uncertain about:

```python
for label, small_n, big_n in [("this survey", 1000, N), ("B2B accounts", 150, 400)]:
    f = small_n / big_n
    print(f"{label}: f = {f:.3f}; standard error multiplied by sqrt(1 - f) = {np.sqrt(1 - f):.3f}")
```

```text
this survey: f = 0.038; standard error multiplied by sqrt(1 - f) = 0.981
B2B accounts: f = 0.375; standard error multiplied by sqrt(1 - f) = 0.791
```

For 1,000 of 26,342 it's a 2% change. For 150 of 400 B2B accounts it's a 21% cut, and leaving it out overstates the margin. Statistics Canada relays Cochran's rule that it can be ignored up to 5%, and for many purposes 10%. I read that rule second-hand, and the source's wording says the factor where it plainly means the sampling fraction.

## Clusters: paying precision to save money

Now suppose the research team wants home visits, because a sofa's delivery is hard to judge by email. Reaching a postcode area costs £60 in travel, and each interview there costs £8 (both invented for this example). Visiting one customer per area spends the money on travel. **Cluster sampling** picks some areas and takes several people in each. It's cheaper, but neighbours resemble each other, so each extra interview in an area tells you less. [The design effect](../../03-experimentation-and-causality/notes/03-experimentation-at-scale.md) $1 + (m-1)\rho$ from the experiments pillar measures the loss. Compare designs by **effective sample size**, interviews divided by design effect:

```python
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
```

```text
intra-cluster correlation 0.026; budget 12000, 60 per area visited, 8 per interview
 per_area  areas  interviews   deff  effective_n  formula_se  simulated_se
        5    120         600 1.1050     543.0019      0.0215        0.0198
       10     85         850 1.2362     687.6025      0.0191        0.0176
       15     66         990 1.3674     724.0070      0.0186        0.0173
       20     54        1080 1.4986     720.6722      0.0186        0.0171
       40     31        1240 2.0234     612.8166      0.0202        0.0193
```

More people per area buys more interviews but not more information past a point. At 12,000 pounds the effective sample peaks around 15 to 20 per area, and 40 per area gives more interviews (1,240) and less information (613 against 724). The correlation is only 0.026, and it still matters. The formula's standard errors run a little above the simulated ones, because the formula treats the areas as drawn from an endless supply and here 85 of the 120 are visited.

The [UN's household survey handbook](https://unstats.un.org/unsd/publication/seriesf/seriesf_98e.pdf) (2008) puts the trade-off in one line: the sampler "can exercise no control over the intra-class correlation" but "can still adjust the cluster size". Its worked example has a correlation of 0.03: 50 people per cluster gives a design effect of 2.5, 100 gives 4.0, and it calls effects "much larger than 2.5-3.0" undesirable for key indicators. Kish adds that clustering falls in subgroups that cut across clusters, while the cost of unequal weights stays about the same.

## Nonresponse: a low rate is not the same as high bias

Fernhill's designed survey goes into the field. Report what happened to every case, not just the rate. [AAPOR's *Standard Definitions*](https://aapor.org/wp-content/uploads/2023/05/Standards-Definitions-10th-edition.pdf) (10th edition, 2023) defines six response rates, which differ on partial interviews and on cases of unknown eligibility. RR1 counts completes over everyone who might be eligible. RR3 discounts the unknowns by $e$, the estimated eligible share, and AAPOR calls it "the most-common" in reporting, adding "One must not select a proportion to boost the response rate". RR6 counts partials and drops the unknowns, which makes it "the maximum". The same fieldwork gives three figures:

```python
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
```

```text
sampled 2000: complete 853, partial 55, refused 284, no contact 661, unknown eligibility 147
RR1 0.426; RR3 with e = 0.8: 0.433; RR6 0.490
```

(The dispositions are generated in the script, and $e = 0.8$ is our assumption.) Always say which rate you quote. AAPOR also says response rates "make little sense" for non-probability samples, where selection probabilities are unknowable. An opt-in panel's "participation rate" isn't a quality measure.

Does a low rate matter? Less than you'd expect, and not in the way people assume. The bias of the respondents' mean is driven by the covariance between someone's chance of answering, $p$, and their answer, $y$: $\text{bias} \approx \text{cov}(p, y) / \bar{p}$. Response rate appears only in the denominator. So:

```python
y = frame.true_satisfied.to_numpy(float)


def nonresponse_bias(p):
    """Respondent mean minus population mean: the covariance of the chance of answering with y, over the mean chance."""
    return np.cov(p, y, bias=True)[0, 1] / p.mean()


mailings = {"flat 8%": np.full(N, .08),
            "'tell us what you loved', 45%": .30 + .25 * y,
            "blanket email, all customers": frame.true_p_email.to_numpy(),
            "designed, with reminders": frame.true_p_followup.to_numpy()}
for name, p in mailings.items():
    print(f"{name:32s} response {p.mean():.3f}; bias {nonresponse_bias(p):+.3f}; check {np.average(y, weights=p) - y.mean():+.3f}")
```

```text
flat 8%                          response 0.080; bias -0.000; check +0.000
'tell us what you loved', 45%    response 0.424; bias +0.147; check +0.147
blanket email, all customers     response 0.147; bias +0.217; check +0.217
designed, with reminders         response 0.460; bias +0.047; check +0.047
```

A flat 8% has no bias at all, and a 42% mailing that invites people to say what they loved has 14.7 points. The covariance formula and the direct calculation agree to three decimals because here we hold the true $p$.

[Groves](https://academic.oup.com/poq/article/70/5/646/4084443) (*Public Opinion Quarterly*, 2006) calls the nonresponse rate "a weak predictor of nonresponse bias components": across 30 studies it gives an $r^2$ of 0.11 with absolute relative bias, and "the vast majority of the variation" lies within surveys. Don't over-read that. Groves and Peytcheva's 2008 regression on 959 estimates from 59 studies has an $R^2$ of 0.04, but I know that only through [Brick and Tourangeau](https://reference-global.com/download/article/10.1515/jos-2017-0034.pdf) (*Journal of Official Statistics*, 2017). Their reanalysis of the same data finds study-level correlations of about −0.36 to −0.50 and concludes that response rates "may not be very good predictors of nonresponse bias, but they are far from irrelevant". A low rate gives bias more room. It doesn't tell you how much of the room got used, and any one estimate can differ widely from another in the same survey.

Groves also maps the causes onto [the missing-data vocabulary](../../02-probability-and-statistics/notes/01-descriptive-statistics-and-eda.md). If something else drives both answering and the answer, such as being a heavy buyer, that's consistent with **missing at random**, and a variable holding that cause can repair it. If the answer itself drives answering, because the unhappy don't reply, that's **not missing at random**. And as [Brick](https://reference-global.com/download/article/10.2478/jos-2013-0026.pdf) (*Journal of Official Statistics*, 2013) notes, you can't tell the two apart "without obtaining additional data for the nonrespondents".

## Weighting: post-stratification, raking and their limit

Weighting makes respondents add up to known population totals. An analyst has an advantage over a pollster here: margins come from the CRM exactly, not from a census estimate.

**Post-stratification** cross-classifies the auxiliary variables, then weights each cell up to its population count. It's the same move as [reweighting an effect to population shares](../../02-probability-and-statistics/notes/07-data-generating-process.md), and it's clean until cells run out. **Raking**, or iterative proportional fitting, matches each margin in turn and repeats until all of them hold, so it needs only the margins and no cross-classification. [Kalton and Flores-Cervantes](https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/weighting-methods.pdf) (*Journal of Official Statistics*, 2003) give the trade: raking assumes response probabilities multiply across the variables, which is a stronger assumption and "leads to less variability in the weights". They suggest cells when there are few and they're well filled, and raking when there are many. Both count the variance cost with [Kish](https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/methods-for-design-effects.pdf)'s factor for unequal weights, $1 + L = n\sum w^2 / (\sum w)^2$, where $L$ is the relative variance of the weights. Effective sample is $n / (1 + L)$, [the same quantity](../../03-experimentation-and-causality/notes/05-matching-and-weighting.md#judging-the-designs) the matching chapter uses.

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

Read it in three steps. Variables matter more than method: raking on channel alone moves the email figure 2.6 points, adding segment and active moves it 5.9, and raking, then cells, land on the same number. Kalton and Flores-Cervantes say this too: the choice of auxiliaries "may be of more significance than the choice of a particular method". Weights cost precision: the email's effective sample fell from 2,648 to about 1,500. And cells lose people: 62 and 325 customers sat in cells where nobody answered, so those estimates no longer cover them.

The designed survey's 49.9% looks nearly perfect. Be suspicious of that, since the repeat runs below show it's a lucky draw. The email's 66.6% is still 17 points out. Most of what's left is the part where satisfaction itself drives replying, and no CRM column holds it. [Pew's study of opt-in panels](https://www.pewresearch.org/methods/2018/01/26/for-weighting-online-opt-in-samples-what-matters-most/) (Mercer, Lau and Kennedy, 2018; not peer-reviewed) found the same on real data: across 24 benchmarks and over 30,000 interviews, the best adjustment "was only able to remove about 30% of the original bias", and complex methods never beat simpler ones by more than 0.3 points on average. Bradley et al. reach the same conclusion: "Weighting on observed covariates alone cannot explain or correct the discrepancies we observe."

Weighting isn't hopeless. The richest counterexample is [the Xbox poll](https://sites.stat.columbia.edu/gelman/research/unpublished/forecasting-with-nonrepresentative-polls.pdf) (Wang, Rothschild, Goel and Gelman; author's preprint, published in *International Journal of Forecasting*, 2015). Men were 93% of 750,148 interviews against 47% of the electorate, and yet the day-before estimate of voter intent was 0.6 points from the result. It used [partial pooling](../../04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling.md) over 176,256 cells, and those cells included party identification and past vote. The method helped because the variables held the selection. On raking's relatives: [Hartman, Hazlett and Sterbenz](https://arxiv.org/abs/2107.08075) (preprint) describe the distance raking uses as the one also known as [entropy balancing](../../03-experimentation-and-causality/notes/05-matching-and-weighting.md#entropy-balancing). So raking should look familiar.

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

A cap of 2 raises the email's effective sample by about 26% and moves the estimate 1.5 points further from the truth. (The largest weight ends above the cap because the weights are rescaled afterwards.) That's the bargain as Kalton and Flores-Cervantes describe it: better precision, "while accepting some possible loss in bias reduction". [Battaglia, Hoaglin and Frankel](https://www.surveypractice.org/article/2953-practical-considerations-in-raking-survey-data) (*Survey Practice*, 2009) say raking generally converges in 3 to 10 iterations and give no numeric rule for the bounds. Our run took 29, since segment and spend band overlap heavily and the tolerance is tight. If raking takes far longer than that or fails to converge, look for a nearly empty category.

## Reporting a margin that reflects the design

A single survey can't check itself, but this frame can. Run the whole thing 400 times, weight each one, and mark the intervals:

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

Adjust the margin for the design all the same. **Deff** is the ratio of the actual variance to a simple random sample's, and **deft** is its square root. Kish prefers deft because it's "in the same units as the factors in the intervals", and his warning shows why it matters: a deft of 3 turns a claimed $t = 2$ at $\alpha = .05$ into $t = 2/3$ at $\alpha = 0.50$. So the margin is $1.96 \times \text{deft} \times \sqrt{p(1-p)/n}$, or the plain formula with $n$ replaced by the effective sample. For weighting alone, 1 + L stands in for deff. It's only an approximation, since it ignores any variance that the weights remove and treats weights as fixed. Kish reserves it for haphazard weights and says deliberate oversampling needs other treatment.

Real designs are often heavier than this one. A [2025 Pew methodology statement](https://www.pewresearch.org/race-and-ethnicity/2025/11/03/census-measuring-race-methodology/) gives plus or minus 2.1 points on 6,871 interviews. A simple random sample at 95% would give about 1.18, so the implied design effect is about 3.2 (my arithmetic, assuming 95%, which the page I read doesn't state).

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

Subgroups get wide fast: the referral margin is 9.2 points on 117 people. A gap between groups needs its own margin. Paid social against organic is 13.4 points, with a margin of about 7.4 (my arithmetic: the root of the two squared margins, for independent groups). Between two answers in the same poll, [Pew](https://www.pewresearch.org/short-reads/2016/09/08/understanding-the-margin-of-error-in-election-polls/) says it's "about twice" a single answer's.

The three "if non-respondents" lines are a sensitivity check, and the honest way to state what the margin omits. In this frame the real gap works out at about 6 points (my arithmetic, from a mean raked estimate of 52.8% against 49.6% at a 46% response rate), and the second line is close to that.

[AAPOR's code](https://aapor.org/standards-and-ethics/disclosure-standards/) (revised 2021) requires disclosure of "whether or not the reported sampling error or statistical analyses have been adjusted for the design effect", how weights were calculated, and the unweighted sample sizes behind subgroups. It allows precision measures for non-probability samples only with a description of the underlying model. So don't print plus or minus 1.7 on that email.

## The question itself: measurement error

Everything above assumes the answer means what you think. Wording alone moved a real result by 25 points. [Pew's methods page](https://www.pewresearch.org/writing-survey-questions/) reports a January 2003 split: 68% favoured military action against Iraq when asked plainly, and 43% when the question added "even if it meant that U.S. forces might suffer thousands of casualties". Offering the economy as a listed answer drew 58%, while 35% volunteered it in an open question. Order moves answers too: dissatisfaction with the country was 88% straight after a question on presidential approval, 78% without it.

The usual faults, and what to do about them:

| Fault | Example | Fix |
|---|---|---|
| Double-barrelled | "How happy were you with the speed and care of delivery?" | Ask one thing per question |
| Acquiescence | "Delivery was on time: agree or disagree?" | Offer a choice between statements |
| Social desirability | An interviewer asks whether the driver was rude | Self-administer, or use [randomised response](../../04-bayesian-analysis/notes/01-bayesian-inference.md) |
| Order | Overall rating asked after a list of complaints | Overall first; rotate the items |
| Response order | The best option always comes first | Rotate. Pew: phone favours later items, self-administered the top |

Acquiescence has the best evidence against it. [Saris, Revilla, Krosnick and Shaeffer](https://ojs.ub.uni-konstanz.de/srm/article/view/2682) (*Survey Research Methods*, 2010) ran split-ballot experiments in the European Social Survey and found agree/disagree items "had much lower quality" than item-specific versions, for example .85 against .48 on one immigration item, where quality is a model-based product of reliability and validity. [Lelkes and Weiss](https://pure.uva.nl/ws/files/2653460/169196_506179.pdf) (*Research & Politics*, 2015) qualify that: on one US political efficacy battery they found the two formats equally valid. Neither study used customers. On scale length, [DeCastellarnau](https://link.springer.com/article/10.1007/s11135-017-0533-4) (*Quality & Quantity*, 2018) finds no single best number, and that labelling every point generally helps reliability, though it raises acquiescence.

Measurement also changes with who's asking. [Keeter at Pew](https://www.pewresearch.org/short-reads/2015/05/14/where-web-surveys-produce-different-results-than-phone-interviews/) (2015) reports randomly assigned phone and web groups differing by 5.5 points on average across 60 questions: 62% "very satisfied" with family life by phone, 44% on the web.

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

The 12% acquiescence is planted in the script. Form B reads 4.6 points higher, and both forms come with a tidy margin of 2.2 points. Only the comparison shows the problem, and neither margin says which number is right.

Before any of this, pretest. The [US Census Bureau's quality standards](https://census.gov/about/policies/quality/standards/appendixa2.html) accept cognitive interviews, and note that "as few as fifteen" can reveal major problems. Expert review alone doesn't count. [Lenzner, Hadler and Neuert](https://link.springer.com/article/10.1007/s11135-022-01489-4) (*Quality & Quantity*, 2023) tested one question this way: ten interviews found a real ambiguity (in a later web test 26.2% read it one way, 37.8% another, 33.9% both), but the rewritten version didn't improve validity. Finding a problem doesn't guarantee the fix works, so split-ballot the fix.

## Reading a five-point scale

A 1-to-5 answer is [ordinal](../../02-probability-and-statistics/notes/01-descriptive-statistics-and-eda.md), and averaging it assumes the gap from 4 to 5 equals the gap from 1 to 2. [Liddell and Kruschke](https://osf.io/9h3et/) (*Journal of Experimental Social Psychology*, 2018; authors' draft read) checked 68 psychology articles using Likert outcomes and found every one treated them as metric. In their simulations, with deliberately chosen settings, the metric model reported an effect of 0.49 where none existed and of −0.01 where the true effect was 0.66. An ordered-probit model recovered both. Averaging several items didn't help. On the other side, [Norman](https://link.springer.com/article/10.1007/s10459-010-9222-y) (*Advances in Health Sciences Education*, 2010; abstract read only) argues parametric methods are robust on such data. The two needn't conflict: a typical case may be fine, and a floor, ceiling or unequal spread is where it breaks. So look at the shares.

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
    print(f"{name:10s} shares 1-5 {np.round(shares, 2)}  mean {s.mean():.2f}  bottom two {np.mean(s <= 2):.2f}  top box {np.mean(s == 5):.2f}  probit mean, sd {np.round(fit_probit(s), 2)}")
print(f"t test on the means: p = {stats.ttest_ind(packaging, delivery, equal_var=False).pvalue:.3f}; true underlying means are 4.6 and 5.4")
```

```text
packaging  shares 1-5 [0.   0.01 0.14 0.34 0.5 ]  mean 4.33  bottom two 0.01  top box 0.50  probit mean, sd [4.5  0.96]
delivery   shares 1-5 [0.06 0.05 0.09 0.15 0.65]  mean 4.29  bottom two 0.11  top box 0.65  probit mean, sd [5.48 2.44]
t test on the means: p = 0.567; true underlying means are 4.6 and 5.4
```

Delivery and packaging tie on the mean (4.29, 4.33; $p = 0.57$). They aren't alike. Delivery has more top scores, 65% against 50%, and eleven times the bottom-two share, 11% against 1%. An ordered probit with its thresholds pinned sees delivery's underlying mean as about a point higher and its spread two and a half times as wide, which is near what we planted. (That latent scale is the model's, so treat it as a description.) "Average 4.3 on both" would have hidden a delivery problem affecting one customer in nine. Report the shares first, and use [rank tests](../../02-probability-and-statistics/notes/05-hypothesis-testing.md) or an ordinal model if you need a test.

## Recommendation

Stop publishing 73%. Run the designed survey: a proportional stratified sample of the whole customer list by order segment, a questionnaire that was split-ballot tested, with reminders across email, post and phone. Rake to channel, segment and activity from the CRM. Report it as **about 50% satisfied, plus or minus 3 points of sampling error, on 966 answers from 2,000 sampled (a 48% completed share), weighted to CRM totals, with a further unmeasured risk: if non-respondents are 5 points less satisfied, the figure is 47%.** Add shares by channel, with paid social's 40.1% flagged and its own margin of 5.2.

What would change this: a follow-up with a random subsample of non-respondents, the only way to measure the gap directly, and a repeat of the survey to track it over time. Compare like with like, since a change of mode or wording breaks the series.

This survey estimates a level. Whether a new carrier raises it is a question for [an experiment](../../03-experimentation-and-causality/README.md).

## Practice

Run `uv run ch12_surveys.py` from `practice/`, which takes under a minute. It needs numpy, pandas and scipy. Change `followup_logit` in `SURVEY_DGP` in `retail.py` to see how far the latent coefficient alone moves every row above.

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Printing a margin on a self-selected sample | A tight plus or minus on a poll anyone could join | Report it as non-probability, and describe the model if you give a precision measure |
| Treating the response rate as the quality measure | A 45% survey trusted over an 8% one with no check | Compare respondents with the frame on known columns first |
| Quoting a response rate without naming it | Two vendors' "response rates" that can't be compared | Name RR1, RR3 or RR6, and $e$ |
| Optimising allocation for one number | Fine on spend, and the satisfaction margin is 40% wider | Use proportional unless one statistic dominates |
| Plain margin after weighting or clustering | Intervals too narrow | Multiply by deft; say that you did |
| Taking a weighted number as debiased | Rows agree with each other, and all miss the truth | State the unmeasured risk; follow up a sample of non-respondents |
| Post-stratifying on too many cells | Respondent-free cells, with customers silently dropped | Rake, or collapse the cells |
| Trimming as a default | Effective sample up, estimate moves away from the benchmark | Trim with a reason; report both |
| Averaging a five-point item only | Two items tie on the mean and one hides a tail | Report the shares |
| Changing mode or wording mid-series | A jump in the tracker at the switch | Run both for a wave as a split ballot |

## Try it

1. Rerun the cluster table with an area costing £120, then £240. What happens to the best number of interviews per area, and why?

<details><summary>Answer</summary>

Using the formula's effective sample on a grid of 5 to 60 per area: £60 peaks at 15 (724), £120 at 25 (568) and £240 at 30 (426). Dearer travel pushes you to fewer areas with more people in each, and the same money buys less information.
</details>

2. Rake the blanket email on channel and segment only, without `active`. How much does it lose?

<details><summary>Answer</summary>

69.1% with 1 + L of 1.20, against 66.7% and 1.76 when `active` is included. Dropping a variable that predicts answering costs 2.4 points of repair and saves variance. It's the same trade every time, and the truth is 49.6%.
</details>

3. You have 400 B2B accounts and want plus or minus 5 points at 95%. How many completed interviews, ignoring and then using the finite population correction?

<details><summary>Answer</summary>

Ignoring it, $1.96^2 \times 0.25 / 0.05^2 = 384$, nearly every account. With it, $384 / (1 + 384/400) = 196$. That's my arithmetic, at the worst case $p = 0.5$. Then divide by the expected response rate to get how many to approach.
</details>

4. Five respondents have weights 1, 1, 1, 1 and 4. What are 1 + L and the effective sample?

<details><summary>Answer</summary>

$1 + L = 5 \times 20 / 8^2 = 1.5625$, and the effective sample is $5 / 1.5625 = 3.2$. One heavy weight costs more than a third of the sample.
</details>

## Interview checklist

| Question | Answer |
|---|---|
| Why does a margin of error fail on an email blast? | It measures sampling error from a probability sample. An email blast has no known selection probabilities, and its bias doesn't shrink with n |
| Target, frame, sample, respondents? | Each gap has its own error: coverage, sampling, nonresponse. Measurement error sits on top |
| What makes a sample a probability sample? | Random selection with a known, non-zero chance for every unit. The chances needn't be equal |
| Stratified or cluster? | Stratify to gain precision: every group is sampled. Cluster to save money: some groups are sampled, and precision falls |
| Proportional or Neyman allocation? | Proportional is never worse than simple random and suits many questions. Neyman minimises variance for one statistic, at others' expense |
| When does the finite population correction matter? | When the sampling fraction is large; a common rule of thumb is above about 5%. It reduces the variance by 1 − f |
| How many interviews per cluster? | Trade per-cluster cost against the intra-cluster correlation: compare by effective sample within the budget |
| Does a low response rate mean high bias? | Not by itself: bias comes from the covariance of response propensity and the answer. It's a weak predictor for any one estimate, though not irrelevant at study level |
| Which response rate do you quote? | Name it. RR3 is the most common: it estimates the eligible share of unknown cases |
| Post-stratification or raking? | Cells when few and well filled; raking when there are many variables or you hold only margins. Raking assumes no interaction in response |
| What can't weighting fix? | Selection on anything the auxiliaries don't hold, including the answer itself. Pew's best adjustment removed about 30% of opt-in bias |
| What's Kish's 1 + L? | The variance inflation from unequal weights, 1 plus the relative variance of the weights. Effective sample is n / (1 + L) |
| Deff or deft? | Deff is the variance ratio; deft its root, on the scale of the standard error. Multiply the margin by deft |
| Why trim weights? | To cut variance, accepting some bias. Report before and after |
| Mean of a Likert item? | It assumes equal gaps. It can hide a tail or reverse an order, so report the shares and use an ordinal model or a rank test |
| How do you test a question? | Cognitive interviews to find problems, then a split ballot to measure the fix |

## Next

That's the last of the applied analyses. Each ended with a decision and a check against something known, and this one asked what a number is worth when you must ask people for it. Go on to [data science](../../../data-science/README.md), which takes up the models behind these analyses in depth.
