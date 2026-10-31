# References — Data Analytics

> Every source the notes cite, mapped to notes. **★** = read first. Local PDFs live in [sources/](sources/); figures in [sources/images/](sources/images/). Licence and quality flags are in [Source quality](#source-quality).

---

## Books and courses

| | Source | Notes |
|---|---|---|
| ★ | Davidson-Pilon, [*Probabilistic Programming and Bayesian Methods for Hackers*](https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers) (BMH; MIT licence; PyMC 5 port by Kurisu Chan). Folded in as: ch. 1–2 → [09](notes/09-bayesian-inference.md) and [12](notes/12-bayesian-ab-testing.md); ch. 3 → [10](notes/10-mcmc-and-pymc.md); ch. 4 → [02](notes/02-distributions-and-sampling.md) and [12](notes/12-bayesian-ab-testing.md); ch. 5 → [13](notes/13-loss-functions-and-decisions.md); ch. 6 → [11](notes/11-priors-and-bandits.md); ch. 7 (unfinished outline) → [14](notes/14-bayesian-machine-learning.md). Figures as `davidson-pilon-bmh-*`. Print sample: [sources/bayes_for_hackers.pdf](sources/bayes_for_hackers.pdf) | 02, 09–14 |
| ★ | Bruce & Bruce, *Practical Statistics for Data Scientists* (O'Reilly, 2017), [sources/](sources/Practical_Statistics_for_Data_Scientist.pdf). The working reference for distributions, testing and A/B design | 02–07 |
| ★ | Reinhart, *Statistics Done Wrong* (No Starch, 2015), [sources/](sources/Alex_Reinhart-Statistics_Done_Wrong-EN.pdf). P-value misreadings, multiple comparisons, peeking | 04, 06 |
| | Downey, *Think Stats* and *Think Bayes* (Green Tea Press, CC BY-NC 3.0), [sources/thinkstats.pdf](sources/thinkstats.pdf), [sources/think_bayes.pdf](sources/think_bayes.pdf). Plain-Python alternatives to notes 02 and 09 | 01, 02, 09 |
| | McElreath, *Statistical Rethinking* (draft), [sources/](sources/RM-StatRethink-Bayes.pdf). The next step after BMH; weakly informative priors | 09, 11, 14 |
| | James, Witten, Hastie, Tibshirani & Taylor, *An Introduction to Statistical Learning with Applications in Python* (ISLP, 2023), [sources/](sources/An-Introduction-to-Statistical-Learning-with-Applications-in-Python.pdf). Regression and resampling; bridge to data-science | 05, 08, 14 |
| | Efron & Hastie, *Computer Age Statistical Inference* (2016), [sources/](sources/computer%20age%20statistical%20inference.pdf). Frequentist, Bayesian and ML methods side by side | 03, 14 |
| | Knaflic, *Storytelling with Data* (Wiley, 2015), [sources/](sources/Knaflic-storytelling-data.pdf). Presenting results; pairs with the Michigan visualisation scripts | none yet |
| | McKinney, *Python for Data Analysis*, 1st and 2nd ed., [sources/](sources/Python%20for%20Data%20Analysis%202nd%20edition.pdf). The pandas layer, taught in [programming/python/04-python-for-data/](../programming/python/04-python-for-data/README.md) | prerequisite |
| | VanderPlas, *Python Data Science Handbook*, [sources/](sources/Python_Datascience.pdf) | prerequisite |
| | HSE, [*Bayesian Methods for Machine Learning*](https://www.coursera.org/learn/bayesian-methods-in-machine-learning) (Coursera). Own coursework in [practice/BayesianML/](practice/BayesianML/) | 10, 14 |
| | Michigan, *Applied Data Science with Python* and Wesleyan, *Data Analysis and Interpretation* (Coursera). Own scripts in [practice/courses/](practice/courses/) | 04 |
| | Cunningham, [*Causal Inference: The Mixtape*](https://mixtape.scunning.com/) (free online). The next step for the causal-methods map | 08 |
| | Blitzstein & Hwang, [*Introduction to Probability*](https://projects.iq.harvard.edu/stat110) (2nd ed., 2019; free PDF from the Stat 110 site). Planned source for the probability skeleton; not yet held | 01 |
| | Gelman, Hill & Vehtari, [*Regression and Other Stories*](https://avehtari.github.io/ROS-Examples/) (Cambridge, 2020; free PDF). Planned source for the regression skeleton; not yet held | 05 |
| | Kohavi, Tang & Xu, *Trustworthy Online Controlled Experiments* (Cambridge, 2020). The practitioner reference for experimentation platforms; not yet held | 06, 07 |

## Talks, docs and posts

| | Source | Notes |
|---|---|---|
| ★ | prasoon2211, [*Introduction to Bayesian Inference for Parameter Estimation*](https://github.com/prasoon2211/bayesian_inference_talk) (DataTalks.Club talk; notebooks updated to PyMC 5). Coin toss, Beta-Binomial in closed form and PyMC, German tank | 09 |
| | E. Adan, [*The German tank problem*](https://www.eadan.net/blog/german-tank-problem/): code the talk's notebook is built on | 09 |
| ★ | [PyMC docs](https://www.pymc.io/) and [ArviZ](https://python.arviz.org/) | 09, 10 |
| | [scipy.stats](https://docs.scipy.org/doc/scipy/reference/stats.html), [statsmodels power and proportions](https://www.statsmodels.org/stable/stats.html) | 02, 04, 06 |
| | E. Miller, [*Formulas for Bayesian A/B testing*](https://www.evanmiller.org/bayesian-ab-testing.html) | 12 |
| | C. Stucchio, [*Easy evaluation of decision rules in Bayesian A/B testing*](https://www.chrisstucchio.com/blog/2014/bayesian_ab_decision_rule.html): the expected-loss stopping rule | 12 |
| | Kaufmann, Cappé & Garivier, [*On Bayesian upper confidence bounds for bandit problems*](http://jmlr.csail.mit.edu/proceedings/papers/v22/kaufmann12/kaufmann12.pdf) (Bayes-UCB) | 11 |
| | T. Salimans, [Observing Dark Worlds](http://timsalimans.com/) winning solution, as retold in BMH ch. 5 | 13 |
| | [DoWhy](https://www.pywhy.org/dowhy/) | 08 |
| | Kaggle [`ab_data.csv`](https://www.kaggle.com/datasets/zhangluyuan/ab-testing): data for the AB notebook (not included) | 06 |

## Papers

Papers for notes 01–08 are being gathered with `scripts/papers/discover.py` (see `scripts/papers/subject-areas-plan.md`); rows land here as `/papers analytics` integrates them.

| | Paper | Notes |
|---|---|---|
| ★ | Dmitriev, Gupta, Kim & Vaz, *A Dirty Dozen: Twelve Common Metric Interpretation Pitfalls in Online Controlled Experiments* (KDD 2017), [sources/](sources/2017-08-kddmetricinterpretationpitfalls.pdf). Moved here from data-engineering 2026-10-31; queued for `/papers` | 07 |

## Readings in sources/

| File | Book | Size | Status |
|---|---|---|---|
| `Alex_Reinhart-Statistics_Done_Wrong-EN.pdf` | Reinhart, *Statistics Done Wrong* | 3.6 MB | cited |
| `An-Introduction-to-Statistical-Learning-with-Applications-in-Python.pdf` | ISLP | 13 MB | cited |
| `intro_stats_learning.pdf` | ISLP again (613 pp, not the R edition) | 20 MB | **duplicate**; candidate to delete |
| `bayes_for_hackers.pdf` | BMH print sample (Addison-Wesley, 63 pp) | 1.8 MB | cited |
| `computer age statistical inference.pdf` | Efron & Hastie | 8.5 MB | cited |
| `Knaflic-storytelling-data.pdf` | Knaflic | 13 MB | uncited |
| `Practical_Statistics_for_Data_Scientist.pdf` | Bruce & Bruce | 14 MB | cited |
| `Python for Data Analysis.pdf` | McKinney, 1st ed. | 8.0 MB | superseded by 2nd ed. |
| `Python for Data Analysis 2nd edition.pdf` | McKinney, 2nd ed. | 10.6 MB | prerequisite |
| `Python_Datascience.pdf` | VanderPlas | 22 MB | prerequisite |
| `RM-StatRethink-Bayes.pdf` | McElreath draft | 24 MB | cited |
| `think_bayes.pdf`, `thinkstats.pdf` | Downey | 3.9 MB | cited |
| `2017-08-kddmetricinterpretationpitfalls.pdf` | Dmitriev et al., *A Dirty Dozen* (KDD 2017) | 1.2 MB | queued for note 07 |

## Removed snapshots

| Directory | Upstream | Removed | Kept |
|---|---|---|---|
| `data-analytics/Bayes/CamDavidsonPilon-Probabilistic-Programming-and-Bayesian-Methods-for-Hackers-5b33f77` | https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers | 2026-10-31 | ch. 1–7 condensed into notes 02, 09–14; two figures in `sources/images/davidson-pilon-bmh-*` |
| `data-analytics/Bayes/bayesian_inference_talk-main` | https://github.com/prasoon2211/bayesian_inference_talk | 2026-10-31 | three notebooks condensed into note 09; the 33-slide deck was not kept |

## PyMC version audit

The PyMC3 → PyMC 5 map is in [note 10](notes/10-mcmc-and-pymc.md#pymc3-to-pymc-5-migration-map). State of the code here:

| Material | PyMC version | Decision |
|---|---|---|
| BMH snapshot (removed) | ported to PyMC 5 upstream | snippets in notes 09–13 use PyMC 5 |
| Talk notebooks (removed) | updated to PyMC 5 | snippets in note 09 use PyMC 5 |
| [practice/BayesianML/week_4](practice/BayesianML/week_4/) | PyMC3 + Theano | pinned at `pymc3==3.11.4 theano-pymc==1.1.2`; archival banner in the notebook |
| [practice/BayesianML/](practice/BayesianML/) (all weeks) | TF 1.15, Keras 2.3.1, Python 3.7 | legacy; `bayesian.yml` |

## Jupyter quick hacks

Folded from `SimpleHacks.md`, a copy of the first five of Parul Pandey's *10 Simple Hacks to Speed up Your Data Analysis in Python* (Towards Data Science, 2019). Updated for 2026.

| Hack | Command | 2026 status |
|---|---|---|
| One-line EDA report | `from ydata_profiling import ProfileReport; ProfileReport(df).to_file("report.html")` | `pandas-profiling` was renamed `ydata-profiling` |
| Interactive pandas plots | `pd.options.plotting.backend = "plotly"; df.plot()` | replaces `cufflinks` / `df.iplot()`, which is unmaintained |
| List magics | `%lsmagic` | current |
| Interactive plots in the notebook | `%matplotlib widget` (needs `ipympl`) | replaces `%matplotlib notebook`, which JupyterLab does not support |
| Run a script / write a cell to a file | `%run file.py`, `%%writefile foo.py` | current |
| Render LaTeX | `%%latex` | current |
| Post-mortem debugger | `%debug` in the next cell after an exception | current |
| Readable nested dicts and JSON | `from pprint import pprint` | current; `rich.print` is the modern alternative |
| Share a snippet | `%pastebin` | uploads to a public paste service; avoid for anything private |

## Source quality

| Source | Quality | Flag |
|---|---|---|
| BMH | high on concepts; dated in places | some PyMC idioms in the upstream text predate the port; notes use PyMC 5 forms |
| Talk notebooks | medium | a conference talk; small, correct examples |
| Own notebook `5_Statistical_Analysis.ipynb` | high | synthetic data, so effects are known by construction |
| AB notebook | medium | missing imports (`statsmodels.stats.api as sms`, `ceil`), no outputs, data not included |
| Kaggle `ab_data.csv` | medium | a teaching dataset with deliberate assignment errors |
| Stucchio, Miller blog posts | medium-high | practitioner posts; the formulas are standard |
| SimpleHacks article | low | tool tips, partly obsolete; kept only as the table above |
