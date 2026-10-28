---
origin: web-authored
sources:
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://www.promptingguide.ai/guides/context-engineering-guide
  - https://github.com/davidkimai/Context-Engineering (00_COURSE/05_memory_systems/00–04, 00_COURSE/03_context_management/02_memory_hierarchies.md) — snapshot 2026-08-14)
  - https://arxiv.org/abs/2610.29823
  - "Bojie Li, AI Agents in Depth (2026), ch. 3 — https://github.com/bojieli/ai-agent-book"
confidence: high
cleaned: 2026-10-28
---
# 6 — Memory as a Context Sub-Component

> Memory is not a sibling pillar of context engineering. It is the mechanism by which context outlives a window.

---

## Framing

Every source that enumerates the foundations treats memory as a context primitive, not a top-level discipline. The reason is structural: memory has no effect on a model except by **entering a context window**. A memory store the agent never reads is inert. So every memory design decision is really a context decision — what gets written, what gets selected back in, at what size.

This reframes the design question from "what should the agent remember?" to **"what should occupy the window three sessions from now, and how does it get there?"**

---

## Memory types

![Comparison of Four Memory Strategies](../images/ai-agent-book/fig3-2.svg)
*Figure 3-2, Comparison of Four Memory Strategies. From Li, [*AI Agents in Depth*](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter3.md) (Apache-2.0).*

| Type | Scope | Lifetime | Example |
|---|---|---|---|
| **In-context / working** | Current window | The session | The conversation so far |
| **Short-term** | Session or workflow | Hours | Task state, prior revisions in a multi-shot refinement |
| **Long-term** | Cross-session | Indefinite | User preferences, project decisions, known failure patterns |
| **Episodic** | Specific past events | Indefinite | "Last Tuesday's deploy failed because of X" |
| **Semantic** | Distilled facts | Indefinite | "This project uses pnpm, not npm" |

Episodic vs. semantic is the distinction that matters in practice. Episodic memory accumulates linearly with time and rots — most of what happened is not worth carrying. Semantic memory is *distilled from* episodes and stays roughly constant in size. A memory system that only stores episodes grows without bound; one that distills episodes into semantic facts converges.

The distillation step is the whole design. "The user corrected me about commit format three times" (episodic, ×3) becomes "commit format is `type(scope): desc (#num)`" (semantic, ×1).

**The trajectory is a log; long-term memory is an archive.** The trajectory is append-only and never rewritten. Long-term memory is rewritten, merged and pruned. Working memory is neither: it is the *filtered, activated subset* of both that is in the window right now. A third store, **business state** ("awaiting payment"), records the task's stage for event-driven agents ([harness 07](../../03-harness-engineering/notes/07-orchestration.md)).

Extraction after a session should be **selective** (skip "the search returned 3 options"), **abstract** ("prefers window seats", not tied to this flight) and **typed** (preference, restriction, account number).

### Three questions, three axes

Li separates three independent design choices:

| Axis | Question | Options |
|---|---|---|
| Hierarchy | *Where* is it stored? | Trajectory · long-term memory · business state |
| Format | *How* is it stored? | Simple notes · enhanced notes · JSON cards · advanced JSON cards |
| Cognitive type | *What* is stored? | Episodic · semantic · procedural |

The axes combine freely. A procedural memory ("search direct flights → confirm seat → apply frequent-flyer number → order meal") can live in a JSON card in long-term memory.

### Storage formats

| Format | Shape | Wins | Loses |
|---|---|---|---|
| **Simple notes** | One atomic fact per entry | Cheapest; passes most basic recall | Links between facts ("Senior Engineer at TechCorp, leads recsys" becomes three unrelated facts) |
| **Enhanced notes** | A narrative paragraph per topic | Nuance ("suggest a project from my background") | Redundant; one change means rewriting several paragraphs; long text weakens the embedding |
| **JSON cards** | `category.subcategory.key` | Partial updates; predictable | Rigid: "Python side projects on weekends" fits three categories at once |
| **Advanced JSON cards** | Facts plus `backstory`, `person`, `relationship`, timestamp | Disambiguation: "Dr. Zhang" the user's dentist vs. their father's cardiologist | Expensive to generate and maintain |

Mix them: **advanced cards for critical, low-volume facts** (preferences, key relationships); **simple notes for high-volume, low-stakes ones**.

**Beyond text.** *User as Code* (Li, [arXiv:2606.16707](https://arxiv.org/abs/2606.16707)) keeps an append-only fact log and periodically regenerates **typed Python state** from it: write-ahead log plus checkpoint. Aggregations ("international trips in 2025") become one expression instead of mental arithmetic: about 99% accuracy, vs. 6–43% for retrieval-based memory. Conflict checks (drug class × allergy) and constraints (passport expires < 180 days after an international departure) run as code on every update. A `notes: list[str]` field holds what won't type. Further inward, facts can be written into the model's own parameters (*User as Engram*: hash N-gram slots, no gradient updates) or kept as perceptual vectors (faces, voices). Those are research directions, previewing [gen-AI 05](../../../generative-ai/05-RL/README.md).

---

## Structured note-taking

Anthropic's term for the pattern: the agent **writes notes to persistent storage outside the context window**, and retrieves them later.

This is agentic memory in its simplest usable form — no vector store, no embedding, just files the agent maintains. A `NOTES.md` or `progress.md` the agent updates as it works survives compaction, crashes, and session boundaries, because it never depended on the window.

Why it works so well relative to its complexity:

- **Write is cheap, read is selective.** Writing costs one tool call; the note only re-enters context when needed.
- **It is the state extraction from compaction, done eagerly.** An agent already keeping structured notes is trivially compactable — the state is on disk.
- **It is auditable.** A human can read the notes, correct them, delete wrong entries.
- **It doubles as crash recovery.** See [05-compression-compaction.md](05-compression-compaction.md).

The discipline: write the note **when the decision is made**, not when the window fills. Notes written under compaction pressure are reconstructions; notes written in the moment are records.

---

## Index-plus-detail

The core architecture for long-term memory. Never load the full memory store; load an **index** and fetch detail on demand.

```text
MEMORY.md (index)                      memory/*.md (detail)
- [Topic A](a.md) — one-line hook  -->  full content, loaded only when relevant
- [Topic B](b.md) — one-line hook
- [Topic C](c.md) — one-line hook
```

Claude Code's auto-memory is exactly this: `MEMORY.md` (first 200 lines / 25 KB) loads at session start; topic files are read only when a hook line signals relevance.

This is **progressive disclosure applied to memory** — the same pattern as skills in layer 2, and the same pattern as lightweight identifiers in retrieval. One idea, three applications: keep a cheap pointer resident, load the payload on demand.

Design consequence: **the one-line hook is the highest-leverage text in the system.** It is the only thing that decides whether the detail ever loads. A vague hook makes a correct memory unreachable — the memory is present and useless, which is worse than absent because it creates false confidence that the fact is available.

---

## Memory hygiene

![Mem0 Memory Management Architecture](../images/ai-agent-book/fig3-3.svg)
*Figure 3-3, Mem0 Memory Management Architecture. From Li, [*AI Agents in Depth*](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter3.md) (Apache-2.0).*

Memory must be **editable and auditable**. Wrong, outdated, and contradictory entries have to be removable rather than accumulating indefinitely. Append-only memory is a slow-motion failure: contradictions accumulate, and the model gets two conflicting facts with no basis to choose — **context poisoning** (see [11-failure-modes.md](11-failure-modes.md)).

Practices:

- **Update over append.** Before writing, check whether an existing entry covers it. Revise that one.
- **Delete what proved wrong.** A memory falsified by later evidence is worse than no memory.
- **One fact per file.** Granular files can be individually revised or deleted; a monolith cannot.
- **Absolute dates, not relative.** "Last week" written six months ago is now false. Timestamps must resolve independently of read time.
- **Don't store what's derivable.** Code structure, git history, and file layout are already in the repo. Memory holds what the artifacts *don't* record — decisions, preferences, corrections, and the reasons behind them.
- **Verify before relying.** A memory naming a file, function, or flag reflects what was true when written. Check that it still exists before acting on it.

The last two are the difference between memory that compounds and memory that decays. Memory should hold what cannot be re-derived; anything re-derivable should be re-derived, because the source of truth stays current and the memory does not.

**Production reconciliation: Mem0's write path.** After each conversation segment, an LLM extracts candidate facts. Each one is vector-matched against existing memories, and the LLM chooses one of four operations: **ADD** (new), **UPDATE** (refines or corrects), **DELETE** (contradicted) or **NOOP** (duplicate). "I moved to Shanghai" finds "lives in Beijing" and UPDATEs it, rather than storing two contradictory facts. This is update-over-append, automated. **Memobase** takes a different design: configurable profile slots (`basic_info.name`, `work.title`) plus a timeline of events. It extracts in **buffered batches**, triggered by size or time, so LLM cost is amortized and reads stay fast. Labs: upstream [mem0](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/mem0) · [memobase](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/memobase).

**Compaction for the store** works in tiers:

1. Score importance (access frequency, age decay, emotional weight, uniqueness) and archive what falls below the threshold.
2. Cluster similar entries into one representative summary ("often asks about weather, especially rain").
3. Generalize episodes into semantic or procedural rules ("prefers value-for-money products and reads reviews").

Keep version history for conflicts. Some fields keep only the latest value (current address); others keep the whole history (job history).

**Sanitize logs locally.** Memory and logs collect PII. Li's lab runs a 0.6B local model (Ollama Qwen3) that returns JSON spans of type, location and confidence. It catches PII written in natural language ("my password is abc123") that regex misses, with recall above 95%. For high throughput, run regex first and send the remainder to the LLM. Don't send logs to a cloud API to be cleaned; that defeats the purpose. Lab: upstream [3-3 log-sanitization](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/log-sanitization).

---

## Short-term memory: state and history

Within a session, prior states and agent outputs are a memory tier too. **Multi-shot refinement** — where an agent revises its own earlier output — depends on having those prior states available.

The tension: prior revisions are exactly the content that fills a window fastest, and superseded drafts are prime pruning candidates. The resolution is usually to keep the *latest* state verbatim plus a compact record of what changed and why, rather than the full revision chain. The rejected drafts rarely matter; the reason for rejection often does.

---

## Conversational memory: the corpus includes the conversation

In multi-turn RAG the retrieval corpus is no longer only a knowledge base. It also holds prior user turns, assistant outputs, tool results and memories distilled from them. That changes the hard problem from relevance to **continuity and intent resolution**: follow-ups carry pronouns, ellipsis ("what about the second one?") and topic drift.

Three controls matter more than the choice of retriever:

| Control | Options | Trade-off |
|---|---|---|
| **Query construction** | Concatenate recent turns; rewrite into a standalone question (CONQRR trains the rewriter against retrieval quality); decompose into parallel subqueries from the whole thread (agentic retrieval) | Concatenation is cheap but drags irrelevant history into the query. A single rewrite loses context in long dialogues, which is why systems move to summaries or structured memory objects. |
| **When to retrieve** | Every turn; only if needed; reuse the previous turn's evidence; ask a clarifying question first | Retrieving every turn is wasteful and can displace evidence that is still valid. |
| **Recency vs. relevance** | Weight retrieved memories by age, e.g. Memoria's exponential decay `wᵢ = e^(−α·xᵢ)` over normalised age | Newer facts win contradictions automatically ("changed jobs"). The risk is that a stable old fact gets down-weighted below a recent, trivial one. |

Recency weighting is a cheap partial answer to **memory hygiene**. It does not replace update-over-append, because both conflicting facts still occupy the window.

---

## Memory architectures

### Episodic, semantic, procedural

The upstream course adds a third long-term type to the table above:

- **Procedural memory:** *how* to do things. Learned workflows, successful tool sequences, prompts that worked. In practice this is a skills or playbook library that the agent retrieves by task type.

### MemOS-style management

Treating memory as an operating-system concern means each memory item has **metadata and a lifecycle**, not just content:

| Field | Why |
|---|---|
| Source and timestamp | Resolve conflicts; expire stale items |
| Confidence | Down-weight inferences relative to stated facts |
| Access count / last used | Promote hot items, archive cold ones |
| Scope (user, project, global) | Prevent one user's facts leaking into another's context |

### MEM1: constant-size memory

Zhou et al. (2506.15841) train agents to keep a single **internal state that is overwritten every turn**, merging new observations with what's worth keeping and discarding the rest. On long multi-hop QA it matches or beats larger models while using a near-constant amount of memory. The engineering takeaway doesn't need training: a fixed-size, rewritten state block outperforms an ever-growing log ([07](07-structured-context.md#2-state-schemas--what-carries-across-turns)).

### Reconstructive memory

Store **fragments** (facts, events, procedures) with source pointers, and assemble a task-specific memory at retrieval time rather than replaying stored transcripts. The risk is confabulated connections between fragments ([13](13-putting-it-together.md#a-note-on-reconstructive-memory)).

### Designed memory vs. searching the raw record

Extraction-based memory (Mem0's fact store, Zep's temporal graph) decides what to keep *before any question arrives*. [arXiv:2610.29823](https://arxiv.org/abs/2610.29823) (Peng, 2026-10) asks whether that still pays once the model can search the raw history with its own tools. On one LoCoMo conversation (419 turns, 152 questions), **Mem0 beats full context only with the weakest model** (GPT-4o-mini, 78% vs. 74%). With GPT-6 Luna and Claude Opus 5.5 it ties or loses, and its build alone costs more than a whole full-context run. Two findings travel as design rules:

- **The writer caps every reader.** A stronger reader on a store a weaker model wrote barely helps: on Zep's GPT-4o-mini graph, Opus 5.5 scores 45% against GPT-4o-mini's 43%. Extraction loses information for good; a verbatim record doesn't.
- **With a strong model, keep the raw record and give it search tools.** A coding agent (Pi) reading the raw history as one file scored 99% at under half full context's cost.

The paper's own caveats: one conversation, one run per cell, a GPT-4o-mini judge, and most of the agents' lead came from photo captions only they could read — on questions without photo evidence, Pi and full context differ by one answer. Read it as a direction, not a benchmark result. It points the same way as [index-plus-detail](#index-plus-detail): keep the source, make it searchable, and let the model decide what to load.

### Two-tier memory: overview plus details

Li's chapter ends with an architecture that combines the two threads:

- **Resident tier.** A few critical facts as advanced JSON cards, always in context ("passport expires 2025-02-18").
- **Retrieved tier.** Raw conversation chunks with **contextual-retrieval prefixes** ("[Husband James is modifying the earlier wire transfer]"), searched on demand ([04](04-retrieval.md#contextual-retrieval)).

Either tier alone fails. Resident context can't hold the details. Retrieval alone misses cross-session connections because it has no overall view. Without prefixes, three chunks recording a transfer set by one spouse, changed by the other, then changed back look like three contradictory instructions. With the who, when and intent in each prefix, the latest valid one is clear. The combination enables proactive service: the agent sees "Tokyo flight in January" next to "passport expires February", retrieves the original conversations to confirm, and warns the user without being asked. Labs: upstream [3-10 agentic-rag-for-user-memory](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/agentic-rag-for-user-memory) · [3-12 contextual-retrieval-for-user-memory](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/contextual-retrieval-for-user-memory).

### Evaluating memory

**Grade it in three levels** (Li's framework, used in [user-memory-evaluation](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/user-memory-evaluation)):

1. **Basic recall.** "My membership number is 12345" comes back exact.
2. **Multi-session retrieval.** Find *all* the relevant records across entities and channels. Two cars means asking "which one?", not guessing. Use the active contract, not a quote that never took effect. Cancelling a trip means finding every linked booking.
3. **Proactive service.** Connect old, unrelated-looking memories without being asked: the expiring passport, every warranty and insurance that covers a broken phone, a year's tax documents.

The protocol: the agent writes memory from session 1, revises it after each later session *seeing only memory, not the raw transcript*, then answers a new question; an LLM judge scores the answer against a reference. LoCoMo (about 300 turns over up to 35 sessions) is the public benchmark in this space. Lab: upstream [3-1/3-2 user-memory](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/user-memory) compares the four formats on this framework.

Memory failures are slow and silent. Test recall across sessions, update correctness and stale-memory rate ([12](12-evaluating-context.md#write-memory)). In production, also track **memory hit rate** (the share of queries where a retrieved memory was actually relevant) and log which memory entries went into each answer, so a bad answer can be traced back to the memory that caused it.

Public multi-turn benchmarks stress later turns, questions that aren't standalone, topic switches and unanswerable questions: **CAsT** (query understanding, with a large gap between automatic and oracle rewrites), **QReCC** (rewrite, retrieve, read), **TopiOCQA** (topic switching), **CORAL** (retrieval, generation and citation) and **mtRAG** (human-written, multi-domain). Mixed-initiative sets such as **InSCIt** test the decision to ask a clarifying question instead of answering.

Source notes with more detail (Memoria internals, production concerns): [memory-augmented-rag-notion-export.md](../sources/memory-augmented-rag-notion-export.md).

---

## Working reference

`~/.claude/refs/agent-memory.md` — memory tier conventions, what belongs in each, and retention rules.
`~/.claude/refs/agent-context.md` — the Write lever (writing context out of the window) and memory summaries as stable, cache-friendly content.

---

→ Next: [07-structured-context.md](07-structured-context.md) — giving context a shape.
