---
origin: curated
confidence: high
cleaned: 2026-11-01
---

# References: data analytics

> The shared book library for all six pillars, with free courses and videos. **★** means read first. Each pillar's own `references.md` maps books and papers to chapters; this file maps them to pillars. PDFs are in [sources/](sources/), figures in [sources/images/](sources/images/).

---

## Books

| | Book | PDF or site | Pillars |
|---|---|---|---|
| ★ | McKinney, *Python for Data Analysis*, 1st and 2nd eds. (O'Reilly); 3rd ed. free online | [2nd ed.](sources/Python%20for%20Data%20Analysis%202nd%20edition.pdf) · [1st ed.](sources/Python%20for%20Data%20Analysis.pdf) · [3rd ed.](https://wesmckinney.com/book/) | 01, 05 |
| | VanderPlas, *Python Data Science Handbook* (O'Reilly) | [PDF](sources/Python_Datascience.pdf) · [online](https://jakevdp.github.io/PythonDataScienceHandbook/) | 01, 05 |
| ★ | Bruce & Bruce, *Practical Statistics for Data Scientists* (O'Reilly, 2017) | [PDF](sources/Practical_Statistics_for_Data_Scientist.pdf) | 02, 03 |
| ★ | Reinhart, *Statistics Done Wrong* (No Starch, 2015) | [PDF](sources/Alex_Reinhart-Statistics_Done_Wrong-EN.pdf) | 02, 03 |
| | Downey, *Think Stats* and *Think Bayes* (Green Tea Press; CC BY-NC) | [Think Stats](sources/thinkstats.pdf) · [3rd ed. online](https://allendowney.github.io/ThinkStats/) · [Think Bayes](sources/think_bayes.pdf) | 02, 04 |
| | James, Witten, Hastie, Tibshirani & Taylor, *An Introduction to Statistical Learning with Applications in Python* (Springer, 2023) | [PDF](sources/An-Introduction-to-Statistical-Learning-with-Applications-in-Python.pdf) · [site](https://www.statlearning.com/) | 02, 03 |
| | Efron & Hastie, *Computer Age Statistical Inference* (Cambridge, 2016) | [PDF](sources/computer%20age%20statistical%20inference.pdf) | 02, 04 |
| | Blitzstein & Hwang, *Introduction to Probability* (2nd ed., 2019); free PDF, not held here | [probabilitybook.net](http://probabilitybook.net/) | 02 |
| | Gelman, Hill & Vehtari, *Regression and Other Stories* (Cambridge, 2020); not held here | [site](https://avehtari.github.io/ROS-Examples/) | 02 |
| | Kohavi, Tang & Xu, *Trustworthy Online Controlled Experiments* (Cambridge, 2020); not held here | [site](https://experimentguide.com/) | 03 |
| | Cunningham, *Causal Inference: The Mixtape*; free online | [site](https://mixtape.scunning.com/) | 03 |
| ★ | Davidson-Pilon, *Probabilistic Programming and Bayesian Methods for Hackers* (MIT licence; PyMC 5 port upstream) | [print sample](sources/bayes_for_hackers.pdf) · [repo](https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers) | 02, 04 |
| | McElreath, *Statistical Rethinking* (draft) | [PDF](sources/RM-StatRethink-Bayes.pdf) | 04 |
| ★ | Knaflic, *Storytelling with Data* (Wiley, 2015) | [PDF](sources/Knaflic-storytelling-data.pdf) · [site](https://www.storytellingwithdata.com/books) | 05 |
| | Wilke, *Fundamentals of Data Visualization* (O'Reilly, 2019); free online | [site](https://clauswilke.com/dataviz/) | 05 |
| | Healy, *Data Visualization: A Practical Introduction* (Princeton, 2018); free online | [site](https://socviz.co/) | 05 |
| | Munzner, *Visualization Analysis and Design* (CRC Press, 2014); not held here | [site](https://www.cs.ubc.ca/~tmm/vadbook/) | 05 |
| | Murray, *Interactive Data Visualization for the Web*, 2nd ed. (O'Reilly, 2017); not held here | [site](https://alignedleft.com/work/d3-book-2e) | 05 |
| | Meeks & Dufour, *D3.js in Action*, 3rd ed. (Manning, 2024); not held here | [site](https://www.manning.com/books/d3js-in-action-third-edition) | 05 |
| | Cairo, *The Truthful Art* (New Riders, 2016); not held here. Details are in [pillar 05's references](05-visualisation-and-storytelling/references.md) | | 05 |
| | Hyndman & Athanasopoulos, *Forecasting: Principles and Practice*, 3rd ed.; free online | [site](https://otexts.com/fpp3/) | 06 |

## Core papers

| | Paper | PDF | Pillars |
|---|---|---|---|
| ★ | Dmitriev, Gupta, Kim & Vaz, *A Dirty Dozen: Twelve Common Metric Interpretation Pitfalls in Online Controlled Experiments* (KDD 2017) | [PDF](sources/2017-08-kddmetricinterpretationpitfalls.pdf) | 03 |
| | Kohavi et al., *Controlled experiments on the web: survey and practical guide* ([Data Mining and Knowledge Discovery](https://doi.org/10.1007/s10618-008-0114-1)) | [PDF](sources/kohavi-2008-controlled-experiments-web.pdf) | 02, 03 |
| | Gelman et al., *A weakly informative default prior distribution for logistic and other regression models* ([Annals of Applied Statistics](https://doi.org/10.1214/08-aoas191)) | [PDF](sources/gelman-2009-weakly-informative-default-prior-distribution.pdf) | 02, 04 |
| | Hoffman & Gelman, [*The No-U-Turn Sampler*](https://arxiv.org/abs/1111.4246) | [PDF](sources/hoffman-2011-no-u-turn-sampler.pdf) | 04 |
| | Blei et al., [*Variational Inference: A Review for Statisticians*](https://arxiv.org/abs/1601.00670) (JASA) | [PDF](sources/blei-2016-variational-inference.pdf) | 04 |
| | Kaufmann, Cappé & Garivier, [*On Bayesian upper confidence bounds for bandit problems*](https://proceedings.mlr.press/v22/kaufmann12.html) (AISTATS 2012) | | 04 |

## Courses and videos

Everything here is free unless the row says otherwise.

| Course or channel | What to use it for | Link | Pillars |
|---|---|---|---|
| Kaggle Learn | Short pandas, data cleaning, visualisation and time-series exercises in the browser | [Pandas](https://www.kaggle.com/learn/pandas) · [Data cleaning](https://www.kaggle.com/learn/data-cleaning) · [Visualisation](https://www.kaggle.com/learn/data-visualization) · [Time series](https://www.kaggle.com/learn/time-series) | 01, 05, 06 |
| StatQuest (Josh Starmer) | Slow, clear video explanations of tests, regression and ML | [Channel](https://www.youtube.com/@statquest) · [Index](https://statquest.org/video-index/) · [Statistics fundamentals](https://www.youtube.com/playlist?list=PLblh5JKOoLUK0FLuzwntyYI10UQFUhsY9) · [Machine learning](https://www.youtube.com/playlist?list=PLblh5JKOoLUICTaGLRoHQDuF_7q2GfuJF) | 02, 03 |
| 3Blue1Brown | Visual intuition for probability and for the linear algebra behind regression | [Probability](https://www.3blue1brown.com/topics/probability) · [Probabilities of probabilities](https://www.youtube.com/playlist?list=PLZHQObOWTQDOjmo3Y6ADm0ScWAlEXf-fp) · [Linear algebra](https://www.3blue1brown.com/topics/linear-algebra) · [Essence of linear algebra](https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab) | 02, 04 |
| Khan Academy, Statistics and Probability | Exercises if the foundations are rusty | [Course](https://www.khanacademy.org/math/statistics-probability) | 02 |
| MIT 18.650, Statistics for Applications (Fall 2016) | The mathematical treatment, with lectures | [OCW](https://ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/) · [Lectures](https://www.youtube.com/playlist?list=PLUl4u3cNGP60uVBMaoNERc6knT_MgPKS0) | 02 |
| Google Data Analytics Certificate | Paid (about $49 a month in the US when checked, after a 7-day trial). Use the nine-course syllabus as a checklist of what employers expect: ask, prepare, process, analyse, share, Python, capstone | [Coursera](https://www.coursera.org/professional-certificates/google-data-analytics) | 01, 02, 05, 06 |
| Mode SQL tutorial | SQL for analysts, from basics to window functions | [Tutorial](https://mode.com/sql-tutorial/) | 06 |
| Hyndman, FPP3 lectures | Lectures that go with the forecasting textbook | [Playlist](https://www.youtube.com/playlist?list=PLyCNZ_xXGzpm7W9jLqbIyBAiSO5jDwJeE) · [Announcement](https://robjhyndman.com/hyndsight/fpp3_videos.html) | 06 |
| Cassie Kozyrkov, *Making Friends with Machine Learning* | Applied ML explained for people who decide, not only build | [About](https://cloud.google.com/blog/topics/developers-practitioners/ai-all-humans-course-delight-and-inspire) · Parts [1](https://bit.ly/mfml_part1), [2](https://bit.ly/mfml_part2), [3](https://bit.ly/mfml_part3), [4](https://bit.ly/mfml_part4) | 02, 06 |
| Michigan, *Applied Data Science with Python* | Paid on Coursera. The source of the `umich_*` coursework scripts | [Coursera](https://www.coursera.org/specializations/data-science-python) | 01, 02 |
| Wesleyan, *Data Analysis and Interpretation* | Paid on Coursera. The source of the `wesleyan_*` scripts | [Coursera](https://www.coursera.org/specializations/data-analysis) | 02 |
| HSE, *Bayesian Methods for Machine Learning* | Source of the coursework in [`practice/BayesianML`](04-bayesian-analysis/practice/BayesianML). Its old Coursera page returned 404 on 2026-11-02, so no link is given | | 04 |

## Talks, docs and posts

| | Source | Pillars |
|---|---|---|
| ★ | prasoon2211, [*Introduction to Bayesian Inference for Parameter Estimation*](https://github.com/prasoon2211/bayesian_inference_talk) (DataTalks.Club talk; notebooks updated to PyMC 5) | 04 |
| ★ | [PyMC docs](https://www.pymc.io/) and [ArviZ](https://python.arviz.org/) | 04 |
| | [scipy.stats](https://docs.scipy.org/doc/scipy/reference/stats.html), [statsmodels](https://www.statsmodels.org/stable/stats.html) | 02, 03 |
| | E. Miller, [*Formulas for Bayesian A/B testing*](https://www.evanmiller.org/bayesian-ab-testing.html) | 04 |
| | C. Stucchio, [*Easy evaluation of decision rules in Bayesian A/B testing*](https://www.chrisstucchio.com/blog/2014/bayesian_ab_decision_rule.html) | 04 |
| | [DoWhy](https://www.pywhy.org/dowhy/) | 03 |
| | E. Adan, *The German tank problem*: the code behind the talk's notebook. Site unreachable on 2026-11-02, so no link is given | 04 |
| | T. Salimans, winning solution to Observing Dark Worlds, as retold in Davidson-Pilon ch. 5. Site unreachable on 2026-11-02, so no link is given | 04 |
| | Kaggle `ab_data.csv` (`zhangluyuan/ab-testing`): data for the AB notebook, not included. Kaggle returned a bot check, so the page was not confirmed and no link is given | 03 |

## Files in sources/

The downloader can add PDFs here. Files not listed below have arrived since this table was written.

| File | What it is | Status |
|---|---|---|
| `intro_stats_learning.pdf` | ISLP again (613 pp, not the R edition) | **Duplicate**; candidate to delete |
| `Python for Data Analysis.pdf` | McKinney, 1st ed. | Superseded by the 2nd ed. |
| `bayes_for_hackers.pdf` | Davidson-Pilon, print sample (63 pp) | Partial |
| `blei-2016-variational-inference.pdf`, `hoffman-2011-no-u-turn-sampler.pdf` | Downloaded papers | Filed; no chapter cites either yet, so the pillar shown under Core papers is where they fit |

Every other PDF is listed under Books or Core papers.

## Removed snapshots

| Directory | Upstream | Removed | Kept |
|---|---|---|---|
| `data-analytics/Bayes/CamDavidsonPilon-Probabilistic-Programming-and-Bayesian-Methods-for-Hackers-5b33f77` | https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers | 2026-10-31 | ch. 1–7 condensed into pillars 02 and 04; two figures in `sources/images/davidson-pilon-bmh-*` |
| `data-analytics/Bayes/bayesian_inference_talk-main` | https://github.com/prasoon2211/bayesian_inference_talk | 2026-10-31 | three notebooks condensed into pillar 04; the 33-slide deck was not kept |

## PyMC version audit

The PyMC3 → PyMC 5 map is in [the MCMC chapter](04-bayesian-analysis/notes/02-mcmc-and-pymc.md#pymc3-to-pymc-5-migration-map). State of the code here:

| Material | PyMC version | Decision |
|---|---|---|
| BMH snapshot (removed) | ported to PyMC 5 upstream | snippets in pillar 04 use PyMC 5 |
| Talk notebooks (removed) | updated to PyMC 5 | snippets in pillar 04's first chapter use PyMC 5 |
| [practice/BayesianML/week_4](04-bayesian-analysis/practice/BayesianML/week_4) | PyMC3 + Theano | pinned at `pymc3==3.11.4 theano-pymc==1.1.2`; archival banner in the notebook |
| [practice/BayesianML/](04-bayesian-analysis/practice/BayesianML) (all weeks) | TF 1.15, Keras 2.3.1, Python 3.7 | legacy; `bayesian.yml` |

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
