# 05 Quality and observability

**What.** How you find out that data is wrong: tests that judge each batch against written rules, monitors that judge it against history, lineage that shows what a bad table touched, and the playbooks that repair it.

**Why.** Pipelines fail when code fails, and nothing in the code reads what the data says. Each stage silently trusts the one before it, so without these checks the first alarm is a stakeholder holding a wrong number.

**The story.** One quarter of taxi trips runs through all three chapters, with five faults planted in March: a null spike, a dropped day, a late partition, duplicate keys and a silent switch from miles to kilometres. Rule tests, Great Expectations and dbt catch two of the five and stay quiet about the rest, because those three are visible only against time. So we build freshness, volume and distribution monitors, find that an age alert clears while the hole remains, and that the common three-sigma volume check misses a quarter of the data. Lineage names the five datasets and 20 runs that the unit change touched. Then we contain it, repair it with a backfill that is safe to run twice, and write the postmortem that adds the next check.

## Reading order

| # | Chapter | Question it answers |
|---|---|---|
| 1 | [Quality dimensions and tests](notes/01-quality-dimensions-and-tests.md) | What does "good" mean, and how do you test it with SQL, Great Expectations and dbt? |
| 2 | [Monitors and lineage](notes/02-monitors-and-lineage.md) | How do you catch what no rule anticipated, and what did the bad table touch? |
| 3 | [Incident playbooks](notes/03-incident-playbooks.md) | Who does what, how do you stop the spread, and how do you repair it safely? |

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [DA 01/02 Loading and cleaning](../../data-analytics/01-python-for-data-analysis/notes/02-loading-and-cleaning.md) | The assertions an analyst runs by hand |
| [DA 02/01 Descriptive statistics and EDA](../../data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda.md) | Looking for what is impossible |

**Feeds into**

| Chapter | Why |
|---|---|
| [GA 08/11 Production and the maturity ladder](../../generative-ai/08-eval/notes/11-production-and-the-maturity-ladder.md) | Monitoring input mix, the same idea for LLM traffic |

## Rules of thumb

- A test is a query that should return nothing. Its rows are the evidence.
- State a tolerance. A hard rule on a soft fact gets muted within a week.
- Accuracy needs an outside account, such as a producer's control total.
- A test asks about a batch. A monitor asks about a batch against time. You need both.
- Pair `max(loaded_at)` with a date spine, or the alert clears while the hole stays.
- Compare the same weekday, using median and MAD. Validate a threshold by injecting losses.
- At scale, threshold on an effect size rather than a p-value.
- Key every metric by logical date, so a backfill replaces rather than adds.
- Contain before you diagnose. Never fix raw in place.
- Prove that a backfill can run twice before you need it.
- Every postmortem adds a check, and no postmortem names a person as the cause.

## Deck and practice

- **Deck:** [slides/quality-and-observability.pptx](slides/quality-and-observability.pptx). Build with `make slides PILLAR=data-engineering/05-quality-and-observability STRICT=1 PREVIEW=1`.
- **Practice:** this pillar has no folder of its own. The monitoring coursework is [06-ml-platform/practice/datatalks-mlops/05-monitoring](../06-ml-platform/practice/datatalks-mlops/05-monitoring): the baseline notebook needs Python and `evidently<0.7`; the stack needs Docker (`docker-compose up`, then `evidently_metrics_calculation.py`). dbt tests are exercised in [03-transform-and-orchestrate/practice](../03-transform-and-orchestrate/practice).
- **Chapter code:** every block without an `# illustrative` label runs locally on synthetic data. Each chapter gives its `uv run --with ...` line. No cloud account is required.

## Primary texts

- Beyer et al., *Site Reliability Engineering*
- Schelter et al., *Automating Large-Scale Data Quality Verification*
- Breck et al., *Data Validation for Machine Learning* and *The ML Test Score*
- Kleppmann, *Designing Data-Intensive Applications*, ch. 12

Everything else: [references.md](references.md).
