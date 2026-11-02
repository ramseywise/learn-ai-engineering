---
origin: synthesis
sources:
  - notes/
confidence: high
cleaned: 2026-11-01
---
# 02 — Ingest and modelling

How data enters a platform you control, and what shape it takes once it is there. Ingest is the first hand-off between teams, and the model is the set of agreements that lets two people get one answer from it.

**Why it comes here.** Pillar 1 gave the physical facts. This pillar sets up everything that later stages will trust: raw data that is complete for a known window and can be re-pulled, a model that says what a row means and how it changes, and a written promise from whoever produces it. Transforms and orchestration ([pillar 3](../03-transform-and-orchestrate/README.md)) only move these guarantees downstream; they cannot create them.

**The story.** A load retries and doubles the day's rows, so we make it repeatable. A watermark misses a delete and a late write, so we read the change log. With the data in hand we design a star on a million taxi trips, watch a join inflate revenue by 8%, and a boundary change rewrite last month's figures until Type 2 keeps both versions. Then we try the two alternatives: a vault with three joins per attribute, and a single wide table that needs 29,249 rows rewritten for one label. Finally a producer switches dollars to cents, every schema check passes, and only a written contract notices.

## Reading order

| # | Chapter | Question it answers |
|---|---|---|
| 1 | [Ingest](notes/01-ingest.md) | How do you copy data without loading it twice or losing it once? |
| 2 | [Dimensional modelling](notes/02-dimensional-modelling.md) | What does a row mean, what adds up, and what did a label mean that day? |
| 3 | [Data Vault and One Big Table](notes/03-data-vault-and-obt.md) | When is the star wrong, in either direction? |
| 4 | [Data contracts](notes/04-data-contracts.md) | How do you turn "the source keeps sending this" into a promise a machine checks? |

Then go to [03, transform and orchestrate](../03-transform-and-orchestrate/README.md). The sequenced path across all seven pillars is in the [curriculum](../CURRICULUM.md).

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [Programming](../../programming/README.md) | Python and SQL fluency, which the zoomcamps assume |

**Feeds into**

| Chapter | Why |
|---|---|
| None in other subjects | Nothing outside this subject links here yet |

## Rules of thumb

| Situation | Rule | Why |
|---|---|---|
| Any load | Assume it will run twice | Schedulers retry. Delete and insert a window in one transaction, or merge on a key |
| Need deletes or every change | Read the log, not a watermark | A watermark cannot see a deleted row |
| Starting a model | Write the grain sentence first | Nearly every wrong number is a grain violation |
| Dimension key has no match | Point at an Unknown row | Inner joins lose rows silently, and totals stop reconciling |
| Numbers per unit | Store numerator and denominator | Ratios get summed. Use the ratio of the sums |
| A label changes | Choose Type 1 or 2 per attribute, with the readers | Overwriting rewrites published history |
| Two facts in one report | Drill across | Fact-to-fact joins multiply both sides |
| Many changing sources, audit duty | Consider a vault, with marts on top | Otherwise it is a star with extra steps |
| One consumer, one grain, stable labels | A wide table on top of the star | Faster reads, but a label change touches each row |
| Someone else's data matters to you | Write the contract and check it at the door | Types cannot see a change of units |

## Deck and practice

- **Deck:** [slides/ingest-and-modelling.pptx](slides/ingest-and-modelling.pptx), built from [slides/deck.yaml](slides/deck.yaml). Rebuild with `make slides PILLAR=data-engineering/02-ingest-and-modelling STRICT=1 PREVIEW=1`.
- **Practice:** [practice/](practice/) has one script per chapter holding that chapter's code. Each prints its output and writes only to a temporary folder. Run from `practice/`:

```bash
uv run --with duckdb --with pyarrow --with numpy --with 'dlt[duckdb]' python 01_ingest.py
uv run --with duckdb --with pyarrow --with numpy python 02_dimensional_modelling.py
uv run --with duckdb --with pyarrow --with numpy python 03_data_vault_and_obt.py
uv run --with duckdb --with pyarrow --with numpy --with pyyaml --with jsonschema python 04_data_contracts.py   # one step fetches the ODCS schema
```

- **Zoomcamp:** [practice/datatalks-de/](practice/datatalks-de/) holds the DataTalks.Club course [README](practice/datatalks-de/README.md), its [Docker and Terraform module](practice/datatalks-de/01-docker-terraform/) and its [project brief](practice/datatalks-de/projects/README.md). The Docker part runs offline after a CSV download; Terraform needs a GCP account. It is a snapshot, so its module numbers differ from the [current course](https://github.com/DataTalksClub/data-engineering-zoomcamp).

Sources: [references.md](references.md).
