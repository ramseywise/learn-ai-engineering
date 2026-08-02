# Worked Example: 1-Hour Timed Code Test (AIE track)

> **Format note:** the 1h timed code test is **emerging, not canonical** — it appears in CoderPad/CodeSignal pilots, not as a confirmed standard round at major AIE employers. Practice it as a compression drill for take-homes; do not assume your loop contains one.

**Format:** 1 hour, timed, shared editor or your own machine. Async — no interviewer to ask.
**Prompt:** "Here's a corpus of 200 support docs. Build a system that answers questions with citations. Deliverable: running Python + a README."

This example walks the [60-minute clock](../../study-guide.md) end to end. The point is not the code — it's the sequence of decisions, and specifically **what gets deliberately skipped**.

---

## 0–10 min — triage

No interviewer to clarify with, so the protocol is the async one: **state your interpretation, write it down, proceed.** Waiting is not an option; the clock is the constraint.

**Decisions made in this window:**

| Question | Call | Why |
|---|---|---|
| RAG-in-a-box or agent-in-a-box? | RAG | The prompt says "answers questions with citations." No multi-hop, no tool use, no state. An agent here is over-scoping. |
| Retrieval approach? | Embeddings + cosine, in-memory | 200 docs is small. No vector DB — numpy array and `argsort` is enough and has no setup cost. |
| Embedding model? | `text-embedding-3-small`, same model for docs and queries | Cheapest, fastest. One constant, used both places — a mismatch here silently destroys similarity scores. |
| Chunking? | 512 tokens, ~10% overlap | Fixed-size with overlap. Semantic chunking is the right answer and the wrong use of 60 minutes. |
| Token budget? | 8K context; assert headroom before every call | Top-5 × 512 = 2.5K + system + question. Fits, but assert rather than assume. |

**Assumption block written into the README immediately** (not at the end — at minute 8, while it's cheap):

> Assumes docs are plain text/Markdown and fit in memory. Assumes single-hop questions — "what is X" / "how do I Y", not "compare X and Y across docs." Assumes an `OPENAI_API_KEY` in the environment.

---

## 10–40 min — execution

End-to-end first. No refactoring, no tuning.

### 10–15 — ingest

Walk the corpus directory, read files, chunk at 512 with 50-token overlap.

```python
CHUNK, OVERLAP = 512, 50
chunks, meta = [], []
for path in sorted(Path(corpus).rglob("*.md")):
    text = path.read_text()
    for i in range(0, len(text), CHUNK - OVERLAP):
        chunks.append(text[i:i + CHUNK])
        meta.append({"doc": path.name, "offset": i})

print(f"{len(chunks)} chunks, ~{sum(map(len, chunks)) // 4} tokens")
```

That last `print` is the cost instrumentation. Adding it now costs nothing; retrofitting observability at minute 55 is how it ends up missing.

### 15–25 — retrieval

Batch-embed all chunks, cache to a local `.npy` so a re-run doesn't re-pay the embedding cost. Embed the query, cosine against the matrix, take top-5.

```python
EMBED_MODEL = "text-embedding-3-small"   # one constant — docs AND queries

def retrieve(query, k=5):
    qv = embed([query])[0]
    scores = (matrix @ qv) / (norms * np.linalg.norm(qv))
    return scores.argsort()[-k:][::-1]
```

Then **manually inspect one query's top-3 chunks.** This is the highest-value 90 seconds in the whole window: if the top-3 are irrelevant, every minute spent downstream is decorating a broken retriever. Cheap to check, fatal to skip.

Isolating retrieval behind one function is also what makes the "swap to pgvector" line in the README credible rather than aspirational.

### 25–35 — LLM call

The prompt assembles the 5 chunks with explicit `[chunk_id]` markers and instructs the model to cite them.

```python
@retry_with_backoff(attempts=3)          # sleep(2**attempt) — backoff, not bare retry
def answer(query, ids):
    ctx = "\n\n".join(f"[{i}] {chunks[i]}" for i in ids)
    return client.chat.completions.create(
        model="gpt-4o-mini",
        timeout=30,                       # written now, not retrofitted
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": f"{ctx}\n\nQ: {query}"}],
    )
```

Two details that are graded and take one line each: `timeout=30` (without it a stalled stream hangs until the clock runs out) and exponential backoff (retry *without* backoff is a named anti-pattern — it hammers a rate-limited endpoint and reads as not knowing why retries exist).

### 35–40 — connect and run

One real query, end to end, output captured and eyeballed. Working system at minute 40 — unpolished, but real. Everything after this point is improvement to something that already runs, which means the clock can expire at any moment from here and there is still a submission.

**Deliberately not done in this window:** no prompt tuning, no reranker, no hyperparameter sweep on chunk size, no CLI argument parsing. Every one of these is defensible engineering and all of them lose to a finished pipeline.

---

## 40–60 min — hardening + docs

**40–45 — the minimal fixes**, in ROI order:

```python
# 1. Context budget assertion (1 min)
available = CTX - len(system_tokens) - MAX_HISTORY - int(0.2 * CTX)
assert available >= 2000, f"Context over-budget: {available} left; reduce top_k"

# 2. Grounding check (2 min) — the highest-signal three lines in the file
if not any(f"[{cid}]" in answer for cid in retrieved_ids):
    return "I couldn't find an answer in the documents."

# 3. Structured output, enumerated not open (3 min)
#    "confidence must be one of: low, medium, high"  — not a float the model invents
try:
    parsed = json.loads(raw)
    assert {"answer", "citations", "confidence"} == set(parsed)
except (json.JSONDecodeError, AssertionError) as e:
    log.warning("JSON drift: %s", e)      # visible failure, not a swallowed one
    return FALLBACK

# 4. Chunk boundary test (30 sec)
assert all(len(c) >= MIN_CHUNK for c in chunks[:-1])
```

No bare `except: pass` anywhere. A system that fails silently is worse than one that fails loudly — every handler either logs and re-raises or returns an explicit error value.

**45–50 — README** (~200 words, below).

**50–55 — three targeted tests.** Not a suite — one happy path, one boundary (empty retrieval), one failure (malformed JSON from the model, mocked). One-command run: `pytest -q`. At a 3–6h Work Trial this bar rises to a full suite; at 60 minutes, three tests that actually run beat twenty that don't.

**55–60 — self-review.** Missing imports, typos, an off-by-one in the overlap arithmetic, any swallowed exception. Read it as a stranger would.

**Deliberately not done:** multi-turn conversation, web UI, caching layer, custom embedding model, Faiss. Named in the README rather than silently omitted — an acknowledged gap reads as judgment; an unacknowledged one reads as an oversight.

---

## The README submitted

> # Doc QA — retrieval with citations
>
> **Run:** `pip install -r requirements.txt && export OPENAI_API_KEY=... && python qa.py "how do I reset a password?"`
> **Test:** `pytest -q` (3 tests: happy path, empty retrieval, malformed model output)
>
> **What it does.** Chunks 200 support docs at 512 tokens with 50-token overlap, embeds with `text-embedding-3-small`, retrieves top-5 by cosine similarity, and answers with `[chunk_id]` citations. If the answer cites nothing retrieved, it declines instead of guessing.
>
> **Assumptions.** Plain-text/Markdown docs that fit in memory. Single-hop questions. Embedding cache in `.npy`; delete it to re-index.
>
> **Cost/latency.** 200 docs → 1,847 chunks, ~=0.4M tokens, ~$0.008 to index (cached after first run). Query path: ~1.2s, ~3K tokens, ~$0.002.
>
> **What breaks.**
> 1. **Multi-hop questions** — "compare the refund policy with the exchange policy" needs two retrievals and a synthesis step. Single-shot retrieval returns chunks from one policy and answers confidently from half the picture. *Fix: query decomposition, or an agent loop with a retrieval tool.*
> 2. **Corpus growth past ~10K chunks** — the in-memory cosine scan is O(n) per query and the `.npy` stops fitting comfortably. *Fix: pgvector or FAISS with an ANN index; the retrieval interface is already isolated in `retrieve()`, so this is a one-function swap.*
> 3. **Changing the embedding model** — the cache is keyed by path only, so a model swap silently compares vectors from two different spaces. *Fix: version the cache key on the model name.*
>
> **Not done, deliberately.** No reranker (adds ~300ms and a second model for maybe 5–10 points of precision — worth it in production, not in the timebox). No multi-turn state. No caching of completions. Chunking is fixed-size; semantic chunking would likely be the highest-value next change, based on inspecting where the top-3 results are weakest.

---

## What the grader sees

The submission is read like a pull request from a new engineer — holistically, attentive to what was chosen and what was omitted. Against that lens:

| Signal | Where it lands |
|---|---|
| Scoped correctly | Chose RAG over an agent in minute 3, and said why |
| Ships | Working end-to-end at minute 40, hardened by 60 |
| API-safe | Timeout, backoff, context assertion, grounding check — all present |
| Fails loudly | No swallowed exceptions; JSON drift logs and falls back |
| Tested proportionally | Three targeted tests, one-command run — right for 1h |
| Observable | Cost and latency printed, not guessed |
| Honest | "What breaks" is specific and has fixes; "not done" is deliberate, with reasoning |

The weakest submission at this timebox is not the one that built least — it's the one that built a reranker and a Streamlit UI and has no grounding check, no timeout, and a README that says "a RAG system."
