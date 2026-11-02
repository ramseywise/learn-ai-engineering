# 07 Architecture and Governance

**What.** How data is arranged and owned across a company: the modern data warehouse, data fabric, lakehouse and data mesh, then access control, personal data and GDPR basics for the engineers who hold it.

**Why.** Earlier pillars each build one stage and ask what it trusts about the stage before. At company scale the failures sit between teams, and the rules of a regulator apply to every copy. Both need a decision on who owns what, and enforcement that can fail a build.

**The story.** A finance team joins trips to tax rates and files a figure less than half the truth, with no error, because one domain writes `CA` and another `California`. Both tables are correct by their owners' rules, so we build the global rule and the publish gate that catch it, and we size the architecture by measuring it. Then the riders behind those trips arrive: a contractor reads 5,000 of them, hashed phone numbers come back in seconds, and one rider asks to be deleted from immutable files, a backup and a forgotten feature table.

## Reading order

| # | Chapter | Question it answers |
|---|---|---|
| 01 | [Data architectures: MDW, fabric, mesh](notes/01-data-architectures-mesh-fabric-mdw.md) | Where should the data live, and who should own each part of it? |
| 02 | [Access control, PII and GDPR](notes/02-access-control-pii-gdpr.md) | Who may see it, what counts as anonymous, and how do you delete one person from an immutable lake? |

## Rules of thumb

- Measure first. Run a representative query on one machine before buying a cluster, and remember that it tests volume and not concurrency.
- A mesh is an ownership model, not a storage choice. Each domain still runs an MDW, a fabric or a lakehouse.
- Contracts before decentralisation: ownership without contracts moves the breakage around.
- Start with a shared platform and domain ownership of data (Serra's Type 1, Strengholt's topology 2). Decentralise technology last, if ever.
- A standard takes effect only where a step can fail it, with the failure routed to a named owner.
- A control the user can alter is no control. Attack your own masking as the user.
- Hashed is not anonymous. Pseudonymised data stays personal data, so use a keyed hash with the key outside the lake.
- A delete in a table format isn't finished until vacuum runs, and erasure isn't finished until every store is clean.
- These chapters are engineering guidance and not legal advice. Take real cases to your data protection officer.

## Deck and practice

**Deck:** [slides/architecture-and-governance.pptx](slides/architecture-and-governance.pptx) ([PDF](slides/architecture-and-governance.pdf)). Build it with `make slides PILLAR=data-engineering/07-architecture-and-governance STRICT=1 PREVIEW=1`.

**Practice:** this pillar has no practice folder. The discussion version is the [scenario prompts handout](../sources/data-mesh-scenario-prompts-handout.pdf), and [chapter 01](notes/01-data-architectures-mesh-fabric-mdw.md#scenario-prompts-mapped-to-mechanisms) maps each prompt to a mechanism.

**Chapter code:** every block runs top to bottom on synthetic data. Each chapter gives its `uv run --with ...` line near the start, and neither needs a server or a paid service. The SQL for Postgres in chapter 02 is marked illustrative because it needs a server.

[References](references.md)
