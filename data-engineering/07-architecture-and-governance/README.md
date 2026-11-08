# 07 Architecture and Governance

**What.** How data is arranged and owned across a company: the modern data warehouse, data fabric, lakehouse and data mesh, then access control, personal data and GDPR basics for the engineers who hold it, and the catalog, semantic layer and contracts that tell a team what a change will break.

**Why.** Earlier pillars each build one stage and ask what it trusts about the stage before. At company scale the failures sit between teams, and the rules of a regulator apply to every copy. Both need a decision on who owns what, and enforcement that can fail a build. And a rule only helps if people can find the data, read one definition of a number, and learn who a change breaks.

**The story.** A finance team joins trips to tax rates and files a figure less than half the truth, with no error, because one domain writes `CA` and another `California`. Both tables are correct by their owners' rules, so we build the global rule and the publish gate that catch it, and we size the architecture by measuring it. Then the riders behind those trips arrive: a contractor reads 5,000 of them, hashed phone numbers come back in seconds, and one rider asks to be deleted from immutable files, a backup and a forgotten feature table. Last, the same company's analysts ask what a column means and get two revenue figures: we measure a catalog by staleness and use, run a real semantic layer that refuses a fan-out join, and watch a same-name unit change pass every contract and multiply a metric by 100.

## Reading order

| # | Chapter | Question it answers |
|---|---|---|
| 01 | [Data architectures: MDW, fabric, mesh](notes/01-data-architectures-mesh-fabric-mdw.md) | Where should the data live, and who should own each part of it? |
| 02 | [Access control, PII and GDPR](notes/02-access-control-pii-gdpr.md) | Who may see it, what counts as anonymous, and how do you delete one person from an immutable lake? |
| 03 | [Catalog, semantic layer and data contracts](notes/03-catalog-semantic-layer-and-contracts.md) | What does this column mean, how is a metric computed the same way everywhere, and who breaks when it changes? |

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [DE 02/04 Data contracts](../02-ingest-and-modelling/notes/04-data-contracts.md) | Chapter 03 takes contract mechanics as read |
| [DE 05/06 DataOps](../05-quality-and-observability/notes/06-dataops.md) | Chapter 03 starts from its metric compiler, exposures and manifest catalog |
| [DA 06/11 Metric trees](../../data-analytics/06-applied-analyses/notes/11-metric-trees.md) | Recommended, not required: what a metric definition must state |
| [Programming](../../programming/README.md) | Python and SQL fluency, which the zoomcamps assume |

**Feeds into**

| Chapter | Why |
|---|---|
| [GA 07/05 Data-analysis agent](../../generative-ai/07-agentic-applications/notes/05-data-analysis-agent.md) | The agent's required metric definitions are a small semantic layer; chapter 03 is the production version |
| [GA 02/08 Agentic RAG in production](../../generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince.md) | Text-to-SQL schema subsetting needs the table and column meaning a catalog holds; separates PRINCE's few-shot "semantic layer" from the metric kind |

## Rules of thumb

- Measure first. Run a representative query on one machine before buying a cluster, and remember that it tests volume and not concurrency.
- A mesh is an ownership model, not a storage choice. Each domain still runs an MDW, a fabric or a lakehouse.
- Contracts before decentralisation: ownership without contracts moves the breakage around.
- Start with a shared platform and domain ownership of data (Serra's Type 1, close to Strengholt's topology 2; the pairing and the advice are ours). Decentralise technology last, if ever.
- A standard takes effect only where a step can fail it, with the failure routed to a named owner.
- A control the user can alter is no control. Attack your own masking as the user.
- Hashed is not anonymous. Pseudonymised data stays personal data, so use a keyed hash with the key outside the lake.
- A delete in a table format isn't finished until vacuum runs, and erasure isn't finished until every store is clean.
- Measure a catalog by stale descriptions and by reads on certified tables, not by coverage.
- Recompute a ratio from its parts at the grain asked for. Never average a stored ratio.
- A new unit gets a new column name, so the failure is loud.
- These chapters are engineering guidance and not legal advice. Take real cases to your data protection officer.

## Deck and practice

**Deck:** [slides/architecture-and-governance.pptx](slides/architecture-and-governance.pptx) ([PDF](slides/architecture-and-governance.pdf)), covering chapters 01 and 02; chapter 03 has no slide yet. Build it with `make slides PILLAR=data-engineering/07-architecture-and-governance STRICT=1 PREVIEW=1`.

**Practice:** this pillar has no practice folder. The discussion version is the [scenario prompts handout](../sources/data-mesh-scenario-prompts-handout.pdf), and [chapter 01](notes/01-data-architectures-mesh-fabric-mdw.md#scenario-prompts-mapped-to-mechanisms) maps each prompt to a mechanism.

**Chapter code:** every block runs top to bottom on synthetic data. Each chapter gives its `uv run --with ...` line near the start, and none needs a server or a paid service. The SQL for Postgres in chapter 02 is marked illustrative because it needs a server.

## Primary texts

- Serra, *Deciphering Data Architectures*, excerpts: attribution inferred from content
- Kleppmann, *Designing Data-Intensive Applications*, ch. 12
- Dehghani, *Data Mesh Principles and Logical Architecture*
- The GDPR
- Halevy et al., *Goods: Organizing Google's Datasets*
- MetricFlow docs and the Open Data Contract Standard

Everything else: [references.md](references.md).
