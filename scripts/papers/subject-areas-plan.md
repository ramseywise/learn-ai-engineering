# Plan — readings, source map and stats gap for the four subject areas

Status: 2026-10-31, not started. Companion to [citation-graph-plan.md](citation-graph-plan.md), which
built the same machinery for ai-engineering and generative-ai.

## Why

The readings pipeline (ledger, triage, `/papers`, citation graph) was built for the AI pillars.
The four subject areas sit outside it:

| Area | Notes | Papers cited | Ledger home | What's wrong |
|---|---|---|---|---|
| data-analytics | 10 | ~1 | none | No home, so nothing can be triaged or routed there. No probability, estimation or regression note. |
| data-engineering | 8 | 0 ("Papers: None") | `ml-systems` | Six paper PDFs in `sources/` that no note cites. One home key covers both MLOps and data systems. |
| data-science | 17 | ~10 | `classical-ml` | ~38 `classical-ml` rows not integrated. Gaps already listed in its CURRICULUM.md. |
| programming | 63 | 0 | none | Books and docs are the right sources. A few primary papers belong in SQL and types. |

Two bugs make it worse:

1. `potw.note_inventory()` treats any folder without a `/` as "no notes; file the PDF only", so
   triage has never been allowed to map a paper to a data-science or data-engineering note.
2. `citegraph.homes()` defaults to the ai-engineering and generative-ai homes only, so these
   areas have no reports, no `primary.md` entries and no "Where the ideas come from" tables.

The citation graph alone can't fill these areas either. It expands outward from papers we
already hold, and data-analytics holds almost none. These areas need a **discovery** step first:
search by topic, ranked by citations, then triage, then the graph.

## Phase 1 — Homes and triage (potw.py)

1. **New and changed homes** in `HOMES`:

   | Key | Folder | Scope |
   |---|---|---|
   | `analytics` (new) | `data-analytics` | probability, estimation, hypothesis testing, regression, experimentation (A/B, CUPED, sequential tests, SRM), causal inference, Bayesian inference and MCMC, bandits, decision theory |
   | `data-systems` (new) | `data-engineering` | distributed storage and compute (MapReduce, Spark), warehouses and column stores, streaming (Kafka, Dataflow), table formats and lakehouse, orchestration, data modelling, data mesh |
   | `ml-systems` (narrowed) | `data-engineering` | MLOps: ML technical debt, SE for ML, data validation, drift and monitoring, feature stores, model registries, maturity |
   | `classical-ml` (broadened) | `data-science` | + tree ensembles and boosting, tabular DL vs trees, optimisers, regularisation, model evaluation and leakage, clustering and dimensionality reduction, sentence embeddings as features |
   | `programming` (new) | `programming` | relational model and query processing, indexing, type systems (incl. TypeScript), concurrency models, software design. Not language tutorials |

   Two keys can share a folder: `PILLARS` is a plain map, and both route to `data-engineering/sources/`.

2. **Fix `note_inventory()`**: glob `**/notes/*.md` under every home folder, so subject folders
   and programming's nested tracks (`python/0N-*/notes/`, `sql/notes/`, `typescript/notes/`) are listed.

3. **Audience per home.** The interest score asks how much "an AI engineer" should know a reading.
   Add an `AUDIENCE` map (`analytics`: "a data analyst running experiments"; `data-systems`: "a data
   engineer"; `programming`: "a working programmer"; default unchanged). Group triage batches by
   home so the prompt can name the audience.

4. **`source_role` in triage.** Triage returns `primary` (the paper that introduced the method,
   system or result), `secondary` (textbook, survey, tutorial, position paper, applied study) or
   `docs`. This is a first guess; Phase 4 checks it against the graph.

5. Re-triage what's already there: `triage --status filed queued parked skipped --home classical-ml ml-systems`
   so existing rows get real note targets and the split key.

Done when: `potw.py status` lists rows for all five keys with notes set, and a dry-run triage
prompt shows data-science notes in the inventory.

## Phase 2 — Discovery (new `potw.py discover`)

1. **Queries per note.** One Haiku call per home reads each note's H1 and H2 headings and writes
   2–4 search queries per note to `scripts/papers/discover/queries-<home>.json`. **Review
   gate:** you edit this file before anything is searched.
2. **Search.**
   - OpenAlex `works?search=<query>&sort=cited_by_count:desc`, types article,
     proceedings-article, book, book-chapter; top 10 per query.
   - Semantic Scholar `/recommendations` seeded with the papers we hold in that home, for
     neighbours that keyword search misses.
3. **Dedupe** against the ledger by DOI, arXiv id and normalised title. Append the new works as
   rows with `source: "openalex"`, `discovered_by: <query>`, `global_citations`, `doi` and
   `oa_pdf_url`.
4. **Curated rows.** The appendix list goes in as `source: "curated"`, resolved by title in
   OpenAlex. Anything that doesn't resolve is printed for a manual check, not dropped.
5. Then the normal `triage` (Phase 1 audience and role) and `download` (free copies only; the
   rest get `link-only`).

Scope limits: programming runs discovery only on `sql/` and the concurrency and types notes.
Expected volume is about 50 notes × 3 queries × 10 results, around 1,500 hits and roughly 800
after dedupe. That's about 32 Haiku triage batches.

Done when: each new home has queued rows whose `note` is set, and the queries file is committed.

## Phase 3 — Stats gap in data-analytics

Before searching, add the missing notes so discovery and triage have targets. Proposed order,
renumbered with `git mv`, with links fixed until `make link-check` passes:

| New | Note | Source |
|---|---|---|
| 01 | **Probability foundations** (new): sample spaces, conditional probability, Bayes' rule, independence, random variables, expectation and variance, joint and marginal | Blitzstein & Hwang, *Introduction to Probability* (free from the Stat 110 site); Downey, *Think Stats* (held) |
| 02 | Distributions and sampling (old 01) | — |
| 03 | **Estimation** (new): MLE, standard error, confidence intervals, bootstrap, power | Bruce & Bruce ch. 2 (held); Efron & Hastie (held); Efron 1979 |
| 04 | Hypothesis testing (old 02) | — |
| 05 | **Regression and GLMs** (new): OLS, reading coefficients, diagnostics, logistic and Poisson GLMs | Gelman, Hill & Vehtari, *Regression and Other Stories* (free PDF); ISLP ch. 3–4 (held); Bruce & Bruce ch. 4 |
| 06 | A/B testing (old 03) | — |
| 07 | **Experimentation at scale** (new): CUPED, sequential and always-valid tests, SRM, metric pitfalls | Kohavi, Tang & Xu; papers in the appendix; KDD 2017 pitfalls PDF (move it here from data-engineering) |
| 08 | Correlation and causation (old 04) | — |
| 09–14 | Bayesian track (old 05–10) | — |

The skeletons come first. Then `/chapter` folds in the book chapters and `/papers` the papers.
data-science note 01 ("Probability as ML uses it") gets a link to the new note 01.

Later and optional: data visualisation (Knaflic, currently uncited), time series (Hyndman,
*FPP3*, free). Out of scope for this plan.

## Phase 4 — Source map (citegraph.py)

1. `homes()` default covers every home. `--subject` limits it to the five subject keys.
2. **Seed rule for thin homes.** The AI homes seed only from what we've read (`integrated`,
   `filed`, `downloaded`). In these homes that's almost nothing. `fetch --include-queued`
   also seeds from queued discovery and curated rows. Reports built that way carry a
   "provisional: seeded from unread candidates" banner until the rows are integrated.
3. **Primary vs secondary.** The local rule (cited by at least 3 of our papers, at least 2 for
   the method) stays. Add `role_check`: compare triage's `source_role` with the graph. A work
   counts as primary when the rule fires, or when triage says primary and the work is the
   earliest in its cluster that our seeds cite. Disagreements go in a table in the report for
   you to settle (Phase 5).
4. **`bridges` (new command).** It lists works cited from both a subject home and an AI home,
   for example analytics A/B testing ↔ `ai-engineering/06-eval` online evaluation,
   `classical-ml` calibration ↔ eval, `ml-systems` monitoring ↔ `generative-ai/06-observability`,
   and `data-systems` storage ↔ RAG vector stores. The output is `reports/bridges.md` plus
   cross-links to add to the notes.
5. Run `fetch → dblp → intents → report → export --html` per home, then `primary` and `refs --write`.
   These areas are mostly journal, SIGMOD, VLDB and KDD papers, so the DBLP and OpenAlex review
   status is mostly peer-reviewed already. The point here is lineage, not upgrading preprints.

Outputs: `reports/citegraph-{analytics,data-systems,ml-systems,classical-ml,programming}.md`,
`reports/bridges.md`, an updated `reports/primary.md`, and graph HTML per home.

## Phase 5 — Your triage pass

A per-home review file, `scripts/papers/discover/review-<home>.md`, generated from the
ledger: one table per note with title, year, citations, triage's role and the graph's role,
plus a keep/drop column. You mark it up. `potw.py review --apply <file>` writes the decisions
back (keep stays `queued` with `role` fixed; drop becomes `skipped`, reason "manual").

## Phase 6 — Integrate

`/papers analytics`, `/papers data-systems`, `/papers ml-systems`, `/papers classical-ml`,
`/papers programming`. They can run as separate sessions at the same time; the ledger lock
handles that. Primary sources go first, as `/papers` already does for `primary.md` rows. After
that come the remaining missing notes (data-science note 18, the boosting/SHAP notebook,
programming testing and profiling).

## Skills and agents

| Item | Change |
|---|---|
| `/readings` | Add a `discover` mode (run Phase 2, point to the queries file) and a `review` mode (generate or apply the Phase 5 files). Know the five subject keys. |
| `/papers` | The description and the grep line say ai-engineering and generative-ai only. Add the subject folders and `programming`. Subject folders keep `references.md` at the folder root, not per pillar. |
| `/chapter` | No change. It is used for the stats books in Phase 3. |
| `/pillar` | No change. Subject folders aren't pillars. |
| New skill | None. New notes follow the existing note shape in each folder. |
| Agents | None needed. Triage already uses `claude -p` with Haiku. Phase 6 can be parallel sessions, or a Workflow if you ask for one. |

## Order and checkpoints

```
Phase 1 homes + triage fixes ──▶ Phase 3 stats note skeletons ──▶ Phase 2 discover
   (code)                          (so triage has targets)          ├─ ✋ review queries
                                                                    ▼
                         Phase 4 source map ◀──────────── triage + download
                                │
                                ▼
                    ✋ Phase 5 your triage pass ──▶ Phase 6 /papers per home
```

✋ marks a step where the work stops for your review.

## Open questions

- Renumbering data-analytics notes 01–10 changes every link to them, including links from
  other subjects. The alternative is new notes numbered 11–14 with the order set only in
  CURRICULUM.md. The default is to renumber.
- Should `programming` get a full home, or only curated rows with no discovery? The default is a
  full home with discovery limited as above.
- Is an S2 API key available? Without one, `intents` and `/recommendations` are slow (429s).

## Appendix — curated candidates

These are a starting set for Phase 2 step 4, from memory. Discovery resolves and verifies
each one. Role is a first guess: P = primary, S = secondary.

**analytics**

| Work | Role | Note |
|---|---|---|
| Kohavi, Tang & Xu, *Trustworthy Online Controlled Experiments* (2020) | S | 06, 07 |
| Kohavi et al., *Controlled experiments on the web: survey and practical guide* (DMKD 2009) | P | 06 |
| Deng, Xu, Kohavi & Walker, CUPED (WSDM 2013) | P | 07 |
| Johari, Koomen, Pekelis & Walsh, *Peeking at A/B Tests* (KDD 2017) | P | 06, 07 |
| Fabijan et al., *Diagnosing Sample Ratio Mismatch* (KDD 2019) | P | 07 |
| Dmitriev et al., *A Dirty Dozen: Metric Interpretation Pitfalls* (KDD 2017), held | P | 07 |
| Benjamini & Hochberg, false discovery rate (JRSS-B 1995) | P | 04 |
| Ioannidis, *Why Most Published Research Findings Are False* (2005) | P | 04 |
| Wasserstein & Lazar, ASA statement on p-values (2016) | S | 04 |
| Efron, *Bootstrap Methods* (Ann. Stat. 1979) | P | 03 |
| Rosenbaum & Rubin, propensity score (Biometrika 1983) | P | 08 |
| Pearl, *Causal inference in statistics: an overview* (2009) | S | 08 |
| Chapelle & Li, *An Empirical Evaluation of Thompson Sampling* (NeurIPS 2011) | P | 11 |
| Gelman et al., weakly informative default prior for logistic regression (AoAS 2008) | P | 11 |
| Hoffman & Gelman, NUTS (JMLR 2014) | P | 10 |
| Vehtari et al., rank-normalised R-hat (Bayesian Analysis 2021) | P | 10 |
| Dempster, Laird & Rubin, EM (JRSS-B 1977) | P | 14 |
| Blei, Kucukelbir & McAuliffe, *Variational Inference: A Review for Statisticians* (JASA 2017) | S | 14 |
| Blitzstein & Hwang; Gelman, Hill & Vehtari (books) | S | 01, 05 |

**data-systems**

| Work | Role | Note |
|---|---|---|
| Ghemawat et al., GFS (SOSP 2003) | P | 04 |
| Dean & Ghemawat, MapReduce (OSDI 2004) | P | 04 |
| Chang et al., Bigtable (OSDI 2006); DeCandia et al., Dynamo (SOSP 2007) | P | 04 |
| Stonebraker et al., C-Store (VLDB 2005); Abadi et al., *Column-Stores vs. Row-Stores* (SIGMOD 2008) | P | 04 |
| Melnik et al., Dremel (VLDB 2010) | P | 04 (BigQuery) |
| Zaharia et al., RDDs (NSDI 2012); Armbrust et al., Spark SQL (SIGMOD 2015) | P | 04 |
| Kreps, Narkhede & Rao, Kafka (NetDB 2011) | P | 01 |
| Akidau et al., the Dataflow model (VLDB 2015) | P | 01, 03 |
| Armbrust et al., Delta Lake (VLDB 2020); Lakehouse (CIDR 2021) | P | 04, 07 |
| Raasveldt & Mühleisen, DuckDB (SIGMOD 2019) | P | 04 |
| Kimball & Ross, *The Data Warehouse Toolkit*, held, filed | S | 02, 04 |

**ml-systems**

| Work | Role | Note |
|---|---|---|
| Sculley et al., *Hidden Technical Debt in ML Systems* (NeurIPS 2015), held | P | 08 |
| Amershi et al., *Software Engineering for ML* (ICSE-SEIP 2019), held | P | 08 |
| Breck et al., *The ML Test Score* (IEEE BigData 2017) | P | 08 |
| Breck et al., *Data Validation for ML* (SysML 2019) | P | 05 |
| Baylor et al., TFX (KDD 2017) | P | 06, 08 |
| Zaharia et al., MLflow (IEEE Data Eng. Bull. 2018) | P | 06 |
| Rabanser et al., *Failing Loudly* (NeurIPS 2019), held | P | 05 |
| Gama et al., *A Survey on Concept Drift Adaptation* (CSUR 2014) | S | 05 |
| Paleyes et al., *Challenges in Deploying ML* (CSUR 2022) | S | 08 |
| Kreuzberger et al., *MLOps: Overview, Definition, and Architecture* (IEEE Access 2023) | S | 08 |
| Shankar et al., *Operationalizing ML: An Interview Study* (2022) | S | 08 |

**classical-ml**

| Work | Role | Note |
|---|---|---|
| Breiman, *Random Forests* (2001); *Statistical Modeling: The Two Cultures* (2001) | P / S | 06, 01 |
| Friedman, *Greedy Function Approximation* (Ann. Stat. 2001) | P | 06 |
| Chen & Guestrin, XGBoost (KDD 2016); Ke et al., LightGBM (NeurIPS 2017); Prokhorenkova et al., CatBoost (NeurIPS 2018) | P | 06 |
| Grinsztajn et al., *Why do tree-based models still outperform deep learning on tabular data?* (NeurIPS 2022) | P | 06 |
| Tibshirani, lasso (JRSS-B 1996); Cortes & Vapnik, SVM (1995) | P | 02 |
| Kaufman et al., *Leakage in Data Mining* (TKDD 2012); Varma & Simon, CV bias (2006) | P | 03, 04 |
| Niculescu-Mizil & Caruana, *Predicting Good Probabilities* (ICML 2005); Davis & Goadrich, PR vs ROC (ICML 2006) | P | 04 |
| Arthur & Vassilvitskii, k-means++ (SODA 2007); Ester et al., DBSCAN (KDD 1996); Liu et al., Isolation Forest (ICDM 2008) | P | 05 |
| van der Maaten & Hinton, t-SNE (JMLR 2008); McInnes et al., UMAP (2018) | P | 05 |
| Rumelhart, Hinton & Williams, backprop (Nature 1986); Glorot & Bengio (AISTATS 2010) | P | 07, 15 |
| Kingma & Ba, Adam (ICLR 2015); Srivastava et al., Dropout (JMLR 2014); He et al., ResNet (CVPR 2016) | P | 07 |
| Pedregosa et al., scikit-learn (JMLR 2011) | S | 01–06 |
| Reimers & Gurevych, Sentence-BERT (EMNLP 2019); Grootendorst, BERTopic (2022) | P | 18 (planned) |

**programming**

| Work | Role | Note |
|---|---|---|
| Codd, *A Relational Model of Data* (CACM 1970) | P | sql 01, 07 |
| Bayer & McCreight, B-trees (Acta Inf. 1972); Comer, *The Ubiquitous B-Tree* (CSUR 1979) | P / S | sql 08 |
| Selinger et al., *Access Path Selection* (SIGMOD 1979) | P | sql 08 |
| Graefe, *Query Evaluation Techniques* (CSUR 1993) | S | sql 08 |
| Bierman, Abadi & Torgersen, *Understanding TypeScript* (ECOOP 2014) | P | typescript 02–05 |
| Cardelli & Wegner, *On Understanding Types* (CSUR 1985) | S | python 03·05, typescript |
| Hoare, CSP (CACM 1978) | P | python 03·07, typescript 06 |
| Parnas, *On the Criteria for Decomposing Systems into Modules* (CACM 1972) | P | python 03·06 |
| Moseley & Marks, *Out of the Tar Pit* (2006) | S | python 03 |
| Knuth, *Structured Programming with go to Statements* (CSUR 1974) | P | profiling (planned) |
