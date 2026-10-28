# Failure Taxonomy — `<system name>`

> Copy and fill in from your own error analysis ([notes/02](../notes/02-defining-correct.md#find-failure-modes-by-reading-error-analysis)). Don't pre-fill labels you haven't seen in traces.

**Owner:** `<one named person>` · **Version:** `v1` · **Last reviewed:** `YYYY-MM-DD` · **Traces coded:** `<n>`

## Rules

- Label the **first** failure in a trace only.
- One label → one fix. If a label could be fixed two different ways, split it.
- Names are `snake_case` and stable. Rename = new version + migration note.
- Eval-infrastructure failures get labels too, so they're never counted as system failures.

## Labels

Ordered by pipeline stage. Upstream failures mask downstream ones.

| Stage | Label | Definition (what you see in the trace) | Likely fix | Grader | Count | Cost |
|---|---|---|---|---|---|---|
| Input / data | `<label>` | | | | | |
| Retrieval | `<label>` | | | | | |
| Tool use | `<label>` | | | | | |
| Generation | `<label>` | | | | | |
| Behavior / policy | `<label>` | | | | | |
| Eval infrastructure | `context_missing` | Grader received no passage text | Fix trace capture | Code | | — |
| Eval infrastructure | `infra_error` | Timeout, rate limit, crash before output | Retry / capacity | Code | | — |

**Count** from the latest coding pass. **Cost**: low / medium / high, from the cost-of-error answer in your success criteria.

## Priority

Rank by count × cost. The top 3 get graders first.

1. `<label>` —
2. `<label>` —
3. `<label>` —

## Change log

| Version | Date | Change | Reason |
|---|---|---|---|
| v1 | | Initial, from `<n>` traces | |

## Example (RAG support agent)

| Stage | Labels |
|---|---|
| Corpus | `source_missing`, `url_unmapped`, `topic_proxy` |
| Index | `index_lag`, `chunk_fragmented` |
| Retrieval | `rank_miss`, `query_rewrite_miss`, `reranker_regression` |
| Eval infrastructure | `context_missing` |
| Generation | `citation_hallucination`, `unsupported_claim`, `incomplete_answer` |
| Behavior | `wrong_escalation`, `refusal`, `schema_violation` |
