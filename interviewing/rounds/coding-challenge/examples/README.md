# Worked Examples

Eight full walkthroughs with narration annotations — the text in `[NARRATE: ...]` blocks is what you say out loud while typing.

For the syntax underneath these — the patterns you should be able to produce without reference — see [code-from-heart.md](../code-from-heart.md).

## General engineering

| File | Format | What it demonstrates |
|------|--------|---------------------|
| `lru-cache.md` | Live coding | Plan → code → test cycle; data structure justification; edge case handling |
| `debugging-dedup.md` | Debugging | Reproduce → bisect → root cause → fix → regression prevention |
| `retry-decorator.md` | Live coding (project-style) | Tests-first; production-readiness signals; `functools.wraps`; jitter |

## Practicals — offline, stdlib only

These five assume the **browser-editor, no-network, no-AI** constraint: no `pip install`, no API key, no `numpy`/`pandas`/`pydantic`. Everything runs on the standard library, so the drill is never blocked by the environment. Each is sized to its stated timebox.

| File | Time | What it demonstrates |
|------|------|---------------------|
| `rag-pipeline-offline.md` | 45 min | Retrieval → prompt construction → schema validation → grounding check; the full pipeline in one arc |
| `workflow-orchestration.md` | 40 min | Deterministic workflow over agent loop; step gating; failure taxonomy; containment |
| `transaction-aggregation.md` | 35 min | Structured aggregation, `Decimal` money handling, defensive parsing, MAD-based anomaly detection |
| `sqlite-pipeline-scaling.md` | 40 min | SQL pipeline + the scaling trap: single-writer lock, OLTP/OLAP split, `EXPLAIN QUERY PLAN` |
| `auth-api-endpoint.md` | 40 min | HMAC tokens, constant-time compare, password hashing, scopes, 401 vs 403, IDOR |

**Two of these are trap-shaped.** `sqlite-pipeline-scaling.md` and `auth-api-endpoint.md` are graded less on whether the code runs than on whether you name the specific failure — the single-writer lock in one, the timing attack and `alg=none` in the other. Build correctly, then critique.

**Why offline matters**: the case-study track's [1-hour code test](../../case-study/examples/aie-track/one-hour-code-test.md) covers similar ground but assumes an API key, network access, and `pip install` — it is a take-home compression drill, not a browser-assessment drill. These five are the browser-assessment version: same concepts, zero setup.

**The concept map** — if the MCQ bank tested it, one of these implements it:

| Concept | Example |
|---|---|
| Few-shot / CoT / prompt formatting | `rag-pipeline-offline.md` — prompt construction section |
| Structured outputs / Pydantic schemas | `rag-pipeline-offline.md` — validation section (stdlib dataclass + the pydantic equivalent named) |
| RAG vs fine-tuning, retrieval mechanics | `rag-pipeline-offline.md` — retrieval section |
| Workflow vs ReAct agents | `workflow-orchestration.md` — the opening architecture call |
| Circuit breakers / retries | `workflow-orchestration.md` — the retry-scoping discussion |
| SQL vs RAG for structured data | `transaction-aggregation.md` — the framing statement |
| OLTP vs OLAP, columnar stores, database choice | `sqlite-pipeline-scaling.md` — the scaling follow-up |
| SQL injection, parameterized queries, transactions | `sqlite-pipeline-scaling.md` — the ingest path |
| Auth, hashing, tokens, HTTP status codes | `auth-api-endpoint.md` — throughout |
| GIL / threads vs processes | [code-from-heart.md](../code-from-heart.md) §12 |

Read these as rehearsal scripts, not reference implementations. The narration is as important as the code.
