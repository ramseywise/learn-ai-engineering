# Reciprocal Rank Fusion for multi-query KB retrieval

> **Scope:** This document covers the **TypeScript `va-agents`** implementation (`support-knowledge-v2.ts`). It is not galactus Python code. Kept here as a design reference for porting RRF to the Python pipeline — see `docs/rag/retrieval-improvements.md` for the Python roadmap.

## Problem

`fetch_support_knowledge` fires 2–4 Bedrock queries in parallel and merges the results in `getUniqueResults()`. The current merge is a score-descending sort over the flat union, with a fingerprint-based dedup that keeps the highest-scored copy of each chunk:

```
query A results: [C1(0.78), C2(0.61), C3(0.55), C4(0.50), C5(0.44)]
query B results: [C1(0.81), C6(0.72), C7(0.63), C2(0.59), C8(0.48)]

merged + sorted: [C1(0.81), C6(0.72), C7(0.63), C2(0.61), C3(0.55), ...]
```

C1 appears in both queries and is ranked first by both — but its score is `0.81` because that is the max of its two raw scores. The fact that two independent query phrasings both retrieved it is not recorded. C2 also appears in both queries; it goes into position 4 with score `0.61`. C6 appears in only one query but slots in at position 2 ahead of C2.

The current scheme treats cross-query agreement as noise to be collapsed rather than signal to be amplified. Reciprocal Rank Fusion (RRF) fixes this.

---

## Algorithm

RRF assigns each chunk a score equal to the sum of its reciprocal rank across all query result lists that returned it:

```
rrf(chunk) = Σ  1 / (k + rank_i + 1)
             i ∈ {lists that contain chunk}
```

- `rank_i` is the zero-based position of the chunk in query `i`'s result list (rank 0 = top result).
- `k = 60` is the standard smoothing constant. It limits the maximum contribution of the top rank to `1/61 ≈ 0.016`, preventing a single rank-1 hit from dominating chunks that consistently appear at rank 2–5 across all queries.

### Worked example

Using the same two queries from above:

```
k = 60

C1: rank 0 in A  → 1/(60+0+1) = 0.01639
    rank 0 in B  → 1/(60+0+1) = 0.01639
    rrf(C1) = 0.03279

C2: rank 1 in A  → 1/(60+1+1) = 0.01613
    rank 3 in B  → 1/(60+3+1) = 0.01563
    rrf(C2) = 0.03175

C6: rank 1 in B  → 1/(60+1+1) = 0.01613
    rrf(C6) = 0.01613

C7: rank 2 in B  → 1/(60+2+1) = 0.01587
    rrf(C7) = 0.01587
```

Final order: `[C1, C2, C6, C7, ...]`

C2 moves ahead of C6 because two queries agreed it was relevant. C6, despite its raw score of `0.72` (the second highest in the merged pool), falls to third place because only one query retrieved it. This is the intended behaviour.

---

## Scope

### What changes

One function in [support-knowledge-v2.ts](tools/support-knowledge-v2.ts):

- `getUniqueResults(results: KnowledgeBaseRetrievalResult[])` — the flat-merge dedup — is replaced by `rankByRrf(queryResultLists: KnowledgeBaseRetrievalResult[][])`, which accepts the per-query result lists before they are flattened.
- The call site in `createExecute` preserves the per-query structure after `Promise.allSettled` and passes it to `rankByRrf` instead of flatMapping into `getUniqueResults`.

### What does not change

| Component | Reason unchanged |
| --- | --- |
| `scoreThreshold` (0.4 cosine / 0.05 reranker) | Raw cosine score is preserved on each `KnowledgeBaseRetrievalResult` — filtering in `toPassages` continues to use `result.score`, which is the max raw score across the queries that returned that chunk. |
| `_kbTopScore` retry threshold (0.45) | Derived from `passage.score`, which stores the raw cosine score. No recalibration needed. |
| `ic._kbScores` score bar chart | Stores `p.score` (raw cosine). RRF score is an ordering mechanism, not a grounding confidence signal. |
| Cross-call dedup | Fingerprint-based, runs after `rankByRrf`, unchanged. |
| SSE dup cache | Keyed by sorted query strings, unchanged. |
| Reranking path (`fetchSupportKnowledgeReranking`) | See Reranking path section below. |

---

## Implementation

### New function: `rankByRrf`

```typescript
const RRF_K = 60;

function rankByRrf(queryResultLists: KnowledgeBaseRetrievalResult[][]): KnowledgeBaseRetrievalResult[] {
  type Entry = { result: KnowledgeBaseRetrievalResult; rrfScore: number; maxRawScore: number };
  const seen = new Map<string, Entry>();

  for (const results of queryResultLists) {
    results.forEach((result, rank) => {
      const url = (result.location ? extractUrl(result.location) : undefined) ?? "no-url";
      const content = result.content?.text ?? "";
      const fingerprint = `${url}|${contentFingerprint(content)}`;
      const contribution = 1 / (RRF_K + rank + 1);
      const rawScore = result.score ?? 0;

      const existing = seen.get(fingerprint);
      if (existing) {
        existing.rrfScore += contribution;
        if (rawScore > existing.maxRawScore) {
          existing.maxRawScore = rawScore;
          existing.result = result;   // keep the higher-scored copy for its metadata
        }
      } else {
        seen.set(fingerprint, { result, rrfScore: contribution, maxRawScore: rawScore });
      }
    });
  }

  return [...seen.values()]
    .sort((a, b) => b.rrfScore - a.rrfScore)
    .map(({ result, maxRawScore }) => ({ ...result, score: maxRawScore }));
}
```

The return type is still `KnowledgeBaseRetrievalResult[]`. Callers do not change. Each returned entry carries `score = maxRawScore` (not the RRF score), so `toPassages`, `_kbTopScore`, and the score bar chart continue to operate on the raw cosine scale without recalibration.

### Call site change in `createExecute`

```typescript
// Before
const allResults = settled
  .filter((r): r is PromiseFulfilledResult<KnowledgeBaseRetrievalResult[]> => r.status === "fulfilled")
  .flatMap(r => r.value);
const uniqueResults = getUniqueResults(allResults);

// After
const queryResultLists = settled
  .filter((r): r is PromiseFulfilledResult<KnowledgeBaseRetrievalResult[]> => r.status === "fulfilled")
  .map(r => r.value);
const uniqueResults = rankByRrf(queryResultLists);
```

The rest of `createExecute` — score threshold, `maxUniqueResults` slice, cross-call dedup, `appendPassagesToContext` — is unchanged.

### Logging

Add a debug log line in `rankByRrf` for chunks that appear in more than one query list, so the signal can be observed in production:

```typescript
const multiHit = [...seen.values()].filter(e => e.rrfScore > 1 / (RRF_K + 1));
if (multiHit.length > 0) {
  log.debug({ count: multiHit.length, ids: multiHit.map(e => ...) }, "rrf multi-query hits");
}
```

Alternatively, extend the existing `[kb-timing]` log line with a `rrfMultiHits` field.

---

## Reranking path

`fetchSupportKnowledgeReranking` uses the Amazon reranker, which already produces a cross-query relevance score for each chunk. Applying RRF on top of reranker scores would double-count relevance signal — the reranker's job is precisely to reconcile multi-concept evidence.

**Recommendation:** apply RRF only in the non-reranking path (`rerank: false`). Keep the flat-merge sort for the reranking path, or apply RRF before the reranker call (using raw cosine ranks to select candidates for reranking, then sort by reranker score for the final list).

Since `fetchSupportKnowledgeReranking` is not currently wired to the live agent (only `fetchSupportKnowledge` is used), this can be deferred.

---

## Edge cases

**Single query.** `rankByRrf` with one list degrades to sort-by-rank, which is identical to sort-by-score since Bedrock returns results ranked by cosine similarity. No behavior change.

**All queries time out except one.** `queryResultLists` contains one fulfilled list. Equivalent to single-query case above.

**Same chunk ranked differently across queries.** RRF handles this naturally — contributions from each rank are summed, so the chunk's final score reflects the union of evidence. The raw max score stored on the result picks up the highest cosine score observed for threshold purposes.

**Chunk ranked at position 0 in all four queries.** Maximum possible RRF score: `4 × 1/61 ≈ 0.066`. This is well above the score of any chunk that appears in only one query at rank 0 (`1/61 ≈ 0.016`). The spread is meaningful with 5 results per query.

**Chunk fingerprint collision.** `contentFingerprint` uses the first 200 characters after whitespace-collapsing. Two chunks from different articles with identical 200-char prefixes would be incorrectly collapsed. This is the same risk as the existing `getUniqueResults` dedup and is not introduced by this change.

---

## Testing

`support-knowledge-v2.test.ts` should add the following cases for `rankByRrf`:

1. **Consensus promotion:** a chunk ranked #2 in both queries scores higher than a chunk ranked #1 in only one query.
2. **Single-query parity:** a single result list produces the same order as sort-by-score.
3. **All-timeouts input:** an empty `queryResultLists` returns an empty array without throwing.
4. **Fingerprint dedup:** the same chunk from two queries appears once in the output with `score = maxRawScore`.
5. **Raw score preserved:** the `.score` on each returned result is the max raw cosine score, not the RRF score.

Existing tests for `toPassages`, `appendPassagesToContext`, and the cross-call dedup should pass without modification since those functions are unchanged.

---

## What RRF does not fix

- **Below-threshold chunks.** A chunk consistently ranked at position 4 with raw score `0.35` is filtered by `scoreThreshold: 0.4` before RRF ordering matters. RRF only re-orders the chunks that survive the threshold.
- **Semantically redundant queries.** If the model submits four phrasings of the same question and all four return the same top chunk, RRF amplifies that one chunk's score but cannot surface new content — the retrieval diversity problem is upstream in the instruction prompt.
- **Reranking precision.** RRF improves ordering within the vector-retrieval path. Highly ambiguous queries where the top-5 cosine results are mostly irrelevant require either better query generation or the reranker.
