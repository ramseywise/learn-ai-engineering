---
origin: web-authored
sources:
  - https://arxiv.org/abs/2510.27246
  - https://arxiv.org/abs/2602.16173
  - "Chip Huyen, AI Engineering (O'Reilly, 2025), ch. 6"
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://www.promptingguide.ai/guides/context-engineering-guide
  - https://github.com/davidkimai/Context-Engineering (00_COURSE/05_memory_systems/00–04, 00_COURSE/03_context_management/02_memory_hierarchies.md) — snapshot 2026-08-14)
  - https://arxiv.org/abs/2610.29823
  - "Bojie Li, AI Agents in Depth (2026), ch. 3 — https://github.com/bojieli/ai-agent-book"
  - https://arxiv.org/abs/2506.15841
  - https://arxiv.org/abs/2507.02259
  - https://arxiv.org/abs/2508.19828
  - "Mayo Oshin & Nuno Campos, Learning LangChain (O'Reilly, 2025), ch. 4 — generative-ai/01-llm-fundamentals/sources/learning-langchain/"
  - "Michael Albada, Building Applications with AI Agents (O'Reilly, 2025), ch. 6, 13 — sources/building-applications-with-ai-agents/"
  - https://arxiv.org/abs/2606.16707
  - https://arxiv.org/abs/1410.5401
  - https://arxiv.org/abs/1503.08895
  - https://arxiv.org/abs/2306.07174
  - https://arxiv.org/abs/2603.02473
  - https://arxiv.org/abs/2607.20064
  - https://arxiv.org/abs/2607.14611
  - https://arxiv.org/abs/2610.12668
  - https://arxiv.org/abs/2609.26891
  - https://arxiv.org/abs/2602.02704
  - https://arxiv.org/abs/2605.12357
  - https://arxiv.org/abs/2603.29493
  - https://arxiv.org/abs/2605.26099
  - https://arxiv.org/abs/2510.07318
  - https://arxiv.org/abs/2502.06049
confidence: high
cleaned: 2026-11-01
---
# 6 — Memory as a Context Sub-Component

> Memory is not a sibling pillar of context engineering. It is the mechanism by which context outlives a window.

An agent that forgets between sessions makes the user repeat themselves, and an agent that remembers badly is worse, because it acts on the old address or the rule from last quarter with full confidence. Memory only ever helps by entering a window, so every stored fact competes for the same budget as everything else. This chapter covers what to distil, how to store and update it, and how to measure it, using systems from Mem0 and ChatGPT's four layers to a plain `MEMORY.md` file.

---

## Framing

Every source that enumerates the foundations treats memory as a context primitive, not a top-level discipline. The reason is structural: memory has no effect on a model except by **entering a context window**. A memory store the agent never reads is inert. So every memory design decision is really a context decision — what gets written, what gets selected back in, at what size.

This reframes the design question from "what should the agent remember?" to **"what should occupy the window three sessions from now, and how does it get there?"**

---

## Memory types

![Comparison of Four Memory Strategies](../sources/images/li-ai-agents-in-depth-fig3-2.svg)
*Image Source: Li, [AI Agents in Depth](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter3.md) (2026), Figure 3-2: Comparison of Four Memory Strategies (Apache-2.0)*

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

### A survey taxonomy: forms, functions, dynamics

The survey *Memory in the Age of AI Agents* organises the field along three different axes, useful when reading papers that each use their own vocabulary:

| Axis | Question | Categories |
|---|---|---|
| **Forms** | What carries the memory? | **Token-level**, as text in an external buffer: *flat* (logs, rolling windows, retrieved snippets), *planar* (graphs such as Zep or A-Mem), *hierarchical* (summaries at several levels). **Parametric**, in the weights: pretraining knowledge, or fine-tuning / LoRA adapters on accumulated experience. **Latent**, as activations: generated, reused (cached KV states) or transformed |
| **Functions** | Why does the agent need it? | **Factual** (user facts such as preferences and identity; environment facts such as world and task state). **Experiential** (case-based, strategy-based, skill-based, or a mix). **Working** (single-turn scratchpads; multi-turn dialogue state and partial plans) |
| **Dynamics** | How does it operate over time? | **Formation** (summarise, distil, build triples or schemas, encode, fine-tune). **Evolution** (consolidate, update, forget). **Retrieval** (timing, query construction, strategy — sparse, dense, graph, hybrid — and post-processing before injection) |

Almost everything in this note is token-level memory. Parametric and latent memory are where the research is heading ([gen-AI 05](../../../generative-ai/05-RL/README.md)); the KV-cache reuse in [02](02-context-anatomy.md#ordering-stable-before-dynamic) is the one latent form already in production.

The idea of a model reading an external store by attention is older than LLMs. **Neural Turing Machines** coupled a neural controller to a memory matrix that it read and wrote with soft attention. The controller found a slot either by matching a key against the contents or by shifting from the slot it used last. Trained on copy sequences of up to 20 random 8-bit vectors, it still copied sequences of length 120 nearly correctly (a few errors, one a duplicated vector), while an LSTM degraded past 20. The authors name the 128-slot memory as the limiting factor: past it, writes wrap around and overwrite earlier ones ([arXiv:1410.5401](https://arxiv.org/abs/1410.5401) (Graves et al., 2014-10, preprint)). **End-To-End Memory Networks** kept only the content read: a softmax of the query against every memory slot, a weighted sum, repeated over several hops. They trained it from question–answer pairs alone. On the synthetic bAbI tasks with 1k training examples, for the jointly trained model, **going from one hop to three cut mean error from 25.8% to 13.3%**. The best variant (12.6% in the text, 12.4% in Table 1) still trailed a Memory Network that was told which facts to read (6.7%) ([arXiv:1503.08895](https://arxiv.org/abs/1503.08895) (Sukhbaatar et al., NeurIPS 2015)). Both papers use toy tasks with memories of 128 slots or 50 sentences, and the MemN2N authors warn that smooth lookups "may not scale well" to larger memories. Two lessons carry over to token-level memory. The store sits outside the model, read by similarity to the query. And the store's size, not the reader, is often what breaks first. Infini-attention's compressive memory ([01](01-why-context-is-finite.md#context-rot)) puts the same idea inside a transformer layer.

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

![Mem0 Memory Management Architecture](../sources/images/li-ai-agents-in-depth-fig3-3.svg)
*Image Source: Li, [AI Agents in Depth](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter3.md) (2026), Figure 3-3: Mem0 Memory Management Architecture (Apache-2.0)*

Memory must be **editable and auditable**. Wrong, outdated, and contradictory entries have to be removable rather than accumulating indefinitely. Append-only memory is a slow-motion failure: contradictions accumulate, and the model gets two conflicting facts with no basis to choose — **context poisoning** (see [11-failure-modes.md](11-failure-modes.md)).

Practices:

- **Update over append.** Before writing, check whether an existing entry covers it. Revise that one.
- **Delete what proved wrong.** A memory falsified by later evidence is worse than no memory.
- **Pick a contradiction policy on purpose.** Keep the newer fact, have a model judge, or keep both as perspectives. Which is right depends on the use case. Liu et al. (2023) have the agent reflect after each action and choose to insert, merge or replace; Bae et al. (2022) merge a summary back into the memory with a sentence-level classifier (*AI Engineering*, ch. 6).
- **One fact per file.** Granular files can be individually revised or deleted; a monolith cannot.
- **Absolute dates, not relative.** "Last week" written six months ago is now false. Timestamps must resolve independently of read time.
- **Don't store what's derivable.** Code structure, git history, and file layout are already in the repo. Memory holds what the artifacts *don't* record — decisions, preferences, corrections, and the reasons behind them.
- **Verify before relying.** A memory naming a file, function, or flag reflects what was true when written. Check that it still exists before acting on it.
- **Scope memory to the agent's audience.** A team agent that recalls something said in a private one-to-one chat is a breach. Personal agents default to isolated memory and share only when explicitly allowed. Team agents use shared, access-controlled spaces. Org-wide agents run under retention rules, logging and audit. At every scope, users can see what the agent remembers, and why, and can delete it or turn memory off (*Building Applications with AI Agents*, ch. 13).

The last two are the difference between memory that compounds and memory that decays. Memory should hold what cannot be re-derived; anything re-derivable should be re-derived, because the source of truth stays current and the memory does not.

**Production reconciliation: Mem0's write path.** After each conversation segment, an LLM extracts candidate facts. Each one is vector-matched against existing memories, and the LLM chooses one of four operations: **ADD** (new), **UPDATE** (refines or corrects), **DELETE** (contradicted) or **NOOP** (duplicate). "I moved to Shanghai" finds "lives in Beijing" and UPDATEs it, rather than storing two contradictory facts. This is update-over-append, automated. **Memobase** takes a different design: configurable profile slots (`basic_info.name`, `work.title`) plus a timeline of events. It extracts in **buffered batches**, triggered by size or time, so LLM cost is amortized and reads stay fast. Labs: upstream [mem0](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/mem0) · [memobase](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/memobase).

**Compaction for the store** works in tiers:

1. Score importance (access frequency, age decay, emotional weight, uniqueness) and archive what falls below the threshold.
2. Cluster similar entries into one representative summary ("often asks about weather, especially rain").
3. Generalize episodes into semantic or procedural rules ("prefers value-for-money products and reads reviews").

Keep version history for conflicts. Some fields keep only the latest value (current address); others keep the whole history (job history).

**Make consolidation rollback-friendly.** Once memory is tiered, the question is no longer whether to store but when to consolidate, and what happens when consolidation fails. OpenClaw's answer: consolidation only **moves a pointer** to mark which messages have been folded into the curated store; it never deletes the originals. If the summarising call fails, the original messages are written to `archive/`, so nothing is lost and the next run starts from the archive. How elegant the summary is matters less than this property.

**Memory is an injection surface that persists.** A payload in a memory file is read as the user's own instruction in every later session, the way stored XSS outlives reflected XSS. Gadgil et al. planted one payload per trial in a synthetic workspace (10 trials per cell; Claude Code with Haiku 4.5 and Opus 4.7, Codex with GPT-5.2 and GPT-5.5). Mean attack success ran from 23.3% (GPT-5.2) to 63.3% (Haiku 4.5). Refusing the attack didn't remove it: **Opus 4.7 never exfiltrated the SSH key, yet left the instruction in memory in all ten sequences**, and its mean persistence across goals was 96.7%. A later session on a weaker model would then read it ([arXiv:2607.14611](https://arxiv.org/abs/2607.14611) (Gadgil et al., 2026-07, preprint)). The payload was planted by hand. The authors could not reliably get an agent to write one into its own memory from untrusted content. The study used one workspace and three payloads, each tied to one file, and tested no defences. Its proposals match the hygiene list above: treat memory files as unequally trusted, review edits to the auto-loaded ones, and validate them at session start.

**Sanitize logs locally.** Memory and logs collect PII. Li's lab runs a 0.6B local model (Ollama Qwen3) that returns JSON spans of type, location and confidence. It catches PII written in natural language ("my password is abc123") that regex misses, with recall above 95%. For high throughput, run regex first and send the remainder to the LLM. Don't send logs to a cloud API to be cleaned; that defeats the purpose. Lab: upstream [3-3 log-sanitization](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/log-sanitization).

---

## Short-term memory: state and history

Within a session, prior states and agent outputs are a memory tier too. **Multi-shot refinement** — where an agent revises its own earlier output — depends on having those prior states available.

The tension: prior revisions are exactly the content that fills a window fastest, and superseded drafts are prime pruning candidates. The resolution is usually to keep the *latest* state verbatim plus a compact record of what changed and why, rather than the full revision chain. The rejected drafts rarely matter; the reason for rejection often does.

Frameworks draw the same line. LangGraph's [memory docs](https://docs.langchain.com/oss/javascript/langgraph/memory) split **thread-scoped** state (message history and working state, persisted per thread by a checkpointer) from **long-term** memory in a store, organised by **namespaces** (per user, per org) and shared across threads. The docs carry the warning this pillar is built on: long histories distract the model, raise cost and latency, and degrade quality, so short-term memory needs its own forgetting and compression ([05](05-compression-compaction.md)).

Oshin and Campos list what a production chat history needs beyond "append the messages" (*Learning LangChain*, ch. 4):

- **Atomic updates.** Record the question and the answer together, so a failure doesn't leave half a turn.
- **Durable storage.** A checkpointer backed by SQLite or Postgres, keyed by `thread_id`.
- **Control** over what is stored and what is sent.
- **State you can inspect and edit outside a model call** (`get_state` / `update_state`).

The trimming defaults that keep a cut history valid:

```python
trim_messages(messages, max_tokens=N, strategy="last",  # keep the newest
              token_counter=model,      # count with the target model's tokenizer
              include_system=True,      # never trim the system message
              allow_partial=False,      # drop a message whole rather than cut it
              start_on="human")         # never keep an answer without its question
```

Two related helpers clean the list before it is sent. `filter_messages` keeps messages by type, name or id. `merge_message_runs` joins consecutive messages of the same type, which some providers (Anthropic among them) reject.

`strategy="last"` is FIFO eviction, and FIFO assumes early turns matter least. Huyen calls that assumption "fatally wrong" in long conversations, where the first turns often hold the task definition. Pin those turns (the system message, the original request) or summarize them; don't let them age out. She also frames the budget as a split. If 30% of the window is reserved for what is retrieved from long-term memory, short-term history gets at most 70%, and overflow moves to the store (*AI Engineering*, ch. 6). The 30% is her illustration, not a recommendation.

---

## The memory loop

Memory touches every call twice: once before the model runs (read) and once after (write). A memory-augmented agent adds a **policy step** in front of retrieval, because in multi-turn settings retrieving every turn is wasteful and can displace evidence that is still valid:

```mermaid
flowchart TD
    Q[User query] --> U[Query understanding<br/>resolve references, rewrite]
    U --> P{Policy decision}
    P -->|retrieve docs?| R[Retrieval layer<br/>knowledge base · memory store · tools · other DBs]
    P -->|recall memory?| R
    P -->|ask to clarify| C[Clarifying question]
    R --> B[Context builder<br/>summary + selected memories + retrieved docs]
    B --> L[LLM]
    L --> W[Memory update<br/>store event · update profile · compress history]
    W -.next turn.-> Q
```
*Image Source: memory-augmented agent architecture, after the author's Notion notes and the Azure / LangGraph memory docs*

The loop is **dual retrieval**: one path reads static knowledge (the RAG index), the other reads history and user memory, and a reasoning step merges the two before generation. Albada names the two paths:

- **Knowledge** is external, verifiable content, fetched at generation time.
- **Memory** is the agent's own history: prior exchanges, tool outputs and state updates.

His "semantic experience memory" embeds each new user input and searches all past interactions with it. A **fixed slice of the window is reserved** for the top matches, and the rest goes to the system message, the latest input and the most recent turns. The reservation is the useful part: experience memory gets a budget line of its own ([03](03-budgeting-the-window.md)), rather than competing with recent turns for whatever room is left (*Building Applications with AI Agents*, ch. 6). After the answer, the memory store is updated with the new interaction (session summary, extracted facts, feedback).

Read as a lifecycle, every memory system makes five decisions, and most failures trace to one of them:

| Step | Decision | Options |
|---|---|---|
| **A. Represent** | What form is a memory? | Raw history, summaries, structured objects (facts, triples, cards) |
| **B. Store** | Where does it live? | Vector DB, structured store (SQL, NoSQL, graph), files |
| **C. Retrieve** | How is it selected? | Query rewriting, history-aware retrieval, recency weighting |
| **D. Use** | How does it enter the call? | Prompt construction, tool choice, planning |
| **E. Update / forget** | How does it change? | Summarise, compress, filter, consolidate, expire |

Microsoft's Foundry agent memory service implements A–E as three managed stages: **extraction** (an LLM pulls preferences and facts such as "allergic to dairy" from the conversation), **consolidation** (an LLM merges duplicates and resolves conflicts, e.g. a new allergy), and **retrieval** (search the store for the most relevant memories; load the stable user profile early in the conversation so personalisation starts on turn one).

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

The four common strategies, from cheapest to most engineered:

| Strategy | How | Wins | Loses |
|---|---|---|---|
| **History-based** | All history, or the last N turns, in the prompt | Trivial; low latency (NVIDIA's RAG blueprint still ships it as "simple multi-turn" mode) | Irrelevant history drifts the retrieval query; grows without bound |
| **Compression** | Rolling summary updated each turn, or structured extraction (preferences, key facts, task state); LangChain summary memory, LangGraph compression | Bounded tokens; better relevance | Lossy; summary quality depends on the model |
| **Retrieval-based** | Store user messages, replies, tool outputs and extracted memories in a vector store; retrieve by semantic, hybrid, or recency + relevance search | Scales; crosses sessions | Retrieval noise; **embedding drift** when the embedding model changes; added latency |
| **Query rewriting** | Use memory to rewrite the turn into a standalone query ("what about the second one?" → "what about the second product you mentioned earlier?") rather than injecting memory directly | Better retrieval for multi-turn RAG (NVIDIA's recommended mode for accuracy); datasets CANARD, QReCC | Can drop context; rewrites are unstable |

The retrieval side of these (history-aware retrieval, CONQRR, agentic retrieval) is in [rag.md — conversational RAG](../../../generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md#conversational-multi-turn-rag).

---

## Production memory designs

Four shipped designs, from simplest to most engineered. Note how little machinery the most widely used one needs.

**ChatGPT: four layers, no vector database.** Viewed from outside, ChatGPT's memory does no RAG at all:

| Layer | Content | Persistent? |
|---|---|---|
| Session metadata | Device, location, usage patterns | No |
| User memory | About 33 key preference facts, **injected every time** | Yes |
| Conversation summary | Lightweight summaries of about 15 recent conversations | Yes |
| Current session | A sliding window over the current conversation | No |

It works because the resident tier is tiny and curated. That's the resident half of [two-tier memory](#two-tier-memory-overview-plus-details), without the retrieved half.

**OpenClaw: logs plus curated facts plus hybrid search.** Three pieces: `memory/YYYY-MM-DD.md`, append-only daily logs that keep the original detail; `MEMORY.md`, curated facts the agent maintains itself; and `memory_search`, a hybrid search weighted **70% vector similarity + 30% keyword**. That's the same split Bayer found by experiment for document retrieval (0.7/0.3, [rag.md](../../../generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md#a-tuned-pipeline-bayers-prince)). Its rollback-friendly consolidation is described under [hygiene](#memory-hygiene).

**Memoria: a summary plus a decayed user graph.** Memoria (Sarmah, Sarin et al., BlackRock; Python package announced as forthcoming) wraps an existing chat app with four modules:

1. **Structured logging.** Every message goes to SQLite with timestamp, session ID, the raw user and assistant messages, extracted triples, the session summary and token usage. A queryable, time-indexed record that survives sessions.
2. **Session summary (short-term).** After each exchange, the user message and reply go to an LLM that *updates* the session's running summary (creates it the first time). Retrieval is a deterministic lookup by session ID.
3. **Knowledge-graph user model (long-term).** After every user message, an LLM extracts `(subject, predicate, object)` triples such as `(user, prefers, equity stocks)`. **Only user messages** are mined, so the graph reflects the user's intent and identity, not the assistant's words. Each triple is stored twice: as text in SQL for traceability, and as an embedding in ChromaDB with timestamp, source message and username.
4. **Weighted retrieval.** The query is embedded, the top-20 triples for that username are retrieved, and each gets an exponential-decay weight by age.

The weighting is the distinctive part:

```text
x_norm = (x − x_min) / (x_max − x_min)     # x = minutes since the triple was created; normalise first
wᵢ     = e^(−α · xᵢ)                        # α = 0.02 (their setting)
w̃ᵢ     = wᵢ / Σⱼ wⱼ                         # weights sum to 1
```

Normalising the ages first stops very old triples decaying to zero, so they still contribute softly. Recent triples dominate, and a contradicted fact (a new job, a changed preference) loses to the newer one with no explicit conflict resolution. **Tuning α**: higher means steeper decay, good for fast-changing preferences; lower keeps old context relevant, good for stable traits like profession or long-term goals.

The prompt is `system + session summary + weighted triples + user message`; afterwards new triples are extracted and the summary updated. With `text-embedding-ada-002` and GPT-4.1-mini, top-20 kept the memory context **under 400 tokens on average, against about 115K for full context**. A sketch of the wrapper pattern (the package isn't released, so the names are illustrative):

```python
mem = Memoria(user_id="alice", session_id="s001")          # illustrative API
summary  = mem.get_session_summary()                         # SQL lookup by session id
triples  = mem.get_weighted_triplets(query=msg, top_k=20)    # vector search + decay weights
reply    = llm(build_prompt(system, summary, triples, msg))  # your existing call
mem.update_summary(msg, reply)                               # update, don't replace
mem.extract_and_store_triplets(msg)                          # user message only
```

The core is small enough to replicate: SQLite, ChromaDB, one extraction call and the decay formula.

**Microsoft Foundry:** a managed extraction → consolidation → retrieval service ([above](#the-memory-loop)).

### Operating a memory store

The production concerns are the ones of any datastore, plus a few specific to memory:

- **Performance.** Cache hot entries (recent session data) with write-through or write-back updates. Index metadata fields (`user_id`, `session_id`). Update vector indexes asynchronously. Use async I/O for lookups; precompute embeddings and summaries so the context builder isn't waiting on them.
- **Observability.** Track **memory hit rate** (share of queries that used a relevant memory), latency per stage (memory lookup, fusion, generation) and update frequency. Log which memory entries went into each answer and trace the request end to end (e.g. OpenTelemetry).
- **Maintenance.** Scheduled pruning of stale entries; store deltas rather than full copies; re-embed when the embedding model changes, or retrieval drifts.
- **Security and compliance.** RBAC/ABAC on read and write; encryption at rest (AES-256) and in transit (TLS); anonymise or tokenise sensitive fields; support **deletion and consent** (GDPR, CCPA), which an index without per-user scope makes very hard.
- **Common failures.** *Overload*: summarise or relevance-score to keep memory concise. *Stale context*: TTL and decay policies, archiving with version history rather than deleting. *Conflicts*: newer supersedes older, or higher-confidence sources beat ambiguous ones.

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

ReAct-style agents append every thought, action and observation, so context grows without bound. Zhou et al. (2506.15841) instead train agents to keep a single **internal state that is overwritten every turn**, merging new observations with what's worth keeping and discarding the rest. On a 16-question multi-hop QA task, MEM1-7B answered **3.5× more questions than Qwen2.5-14B while using 3.7× less peak memory**, and its memory stayed nearly flat as the number of questions grew ([arXiv:2506.15841](https://arxiv.org/abs/2506.15841)). The paper also tests the prompt without the training. Given MEM1's rewrite-the-state prompt, an untrained Qwen2.5-7B scored 0.40 exact matches against 0.17 with the full log, at a third of the peak tokens. So a fixed-size, rewritten state block beats an ever-growing log even without training ([07](07-structured-context.md#2-state-schemas--what-carries-across-turns)). Most of the gain still came from RL: the trained model scored 1.97, and fine-tuning on GPT-4o trajectories did much worse than RL.

![ReAct-style agents append every thought, action and observation; MEM1 replaces its internal state each step](../sources/images/zhou-mem1-fig1.png)
*Image Source: Zhou et al. (2025)*

### MemAgent: overwrite a memory while reading a long document

MEM1 overwrites state across a trajectory; [arXiv:2507.02259](https://arxiv.org/abs/2507.02259) (Yu et al., ICLR 2026) does the same across a long *document*. It reads 5,000-token chunks and rewrites a 1,024-token memory after each, so the window stays at 8K and compute grows linearly. Trained with RL on Qwen2.5-7B and 14B over documents up to 60K tokens, on RULER-HQA (128 synthetic multi-hop questions per length) the 14B scores **80.47 at 7K tokens and 71.09 at 3.5M**, while Qwen2.5-14B-Instruct-1M falls from 60.16 at 7K to 0.00 at 896K. **The RL is the point:** without it, needle retrieval at 512K averages 40.10 against 98.18 with it. The memory is lossy and single-pass: a fact can be overwritten, and a first hop that looks irrelevant is dropped before the second appears. Tests are mostly synthetic, one model family; this is working memory inside one task, not across sessions.

InfMem targets that single-pass weakness. MemAgent pushes every chunk through the same overwrite and cannot look back or stop early. InfMem adds a control step that looks only at the question and the memory and decides to stop or search. If it searches, it runs BM25 over the same document, earlier or later parts, and then writes memory, chunk and retrieved text back into the same 1K budget ([arXiv:2602.02704](https://arxiv.org/abs/2602.02704) (Wang et al., 2026-02, preprint)). At 1M tokens with Qwen3-4B after RL, it scored **56.86 vs. 35.91 on padded MuSiQue and 66.39 vs. 35.18 on padded 2Wiki** (128 samples per task). Across three backbones the average gain was 8–12 points, and latency fell 3.9× on average because it stops once the memory suffices. The comparison isn't budget-matched: InfMem gets up to 4K extra retrieved tokens per step and a document index that MemAgent lacks, and the authors turned off MemAgent's thinking mode. The long tests are synthetic, and on LongBench, the one natural set, untrained MemAgent beats untrained InfMem at 7B. So the evidence supports **control over when to read and when to stop**, not a larger memory.

### Memory in the attention layers

The memory above is text the harness stores and re-reads. LongMem ([arXiv:2306.07174](https://arxiv.org/abs/2306.07174) (Wang et al., 2023-06, preprint)) puts it inside the model instead: a frozen backbone caches the attention keys and values of past segments in a first-in-first-out bank (65K tokens), and a small trainable side network retrieves from it. On a 407M GPT-2 backbone (558M with the side network) it reaches 40.5% on ChapterBreak suffix identification at 8K tokens of prefix (GPT-3 28%, a figure cited from another paper), and with 2,000 extra demonstrations in memory it gains 8.0 points on average over five classification sets at 20 shots (66.7 vs. 58.7; per-task standard deviation up to about 14). The memory is vectors, so it cannot be read or edited, it needs a white-box model and 26B tokens of adapter training, and the evidence is one small model, so treat it as the architectural end of the spectrum rather than something to deploy. LM2 builds the memory into pretraining. Every decoder block gets a 2,048-slot memory bank that tokens read by cross-attention and that input, forget and output gates update ([arXiv:2502.06049](https://arxiv.org/abs/2502.06049) (Kang et al., Convergence Labs, 2025-02, preprint)). At 1.7B parameters it averaged 92.5% on bAbI with no haystack, against 76.4% for a recurrent-memory baseline. From 8K to 128K tokens of BABILong padding it averaged only 39.9% against 35.5%, and about 85% of that lead came from two tasks, counting (qa7, +19.5 points) and qa5 (+18.5), while RMT led on qa9 by 8.7. The baselines were trained differently, the MMLU check sits near chance (29.4%), and there is one model size and one run per setting.

δ-mem shrinks the in-model store to an **8×8 matrix per layer**. A frozen backbone gets a state that a gated delta rule updates, and the state's readout becomes a low-rank correction to attention's query and output. The read cost doesn't grow with the history ([arXiv:2605.12357](https://arxiv.org/abs/2605.12357) (Lei et al., NeurIPS 2026)). On Qwen3-4B-Instruct, with 4.9M trainable parameters trained for one epoch on 2,219 QASPER samples, the average over five benchmarks rose from 46.79 to 51.66, and LoCoMo from 40.79 to 49.12 (best variant per metric: the average is the TSW variant, LoCoMo the MSW variant, whose own average is 50.74). Every text-memory baseline in the same table (BM25 RAG, LLMLingua-2, MemoryBank) scored *below* the bare backbone. The state is not a substitute for the history. With the history removed and only the state left, HotpotQA exact match goes from 0.08 to 6.48. The gains shrink on Qwen3-8B (+3.7), the tests use one seed and models of 8B or smaller, and decoding slows because the state updates every step. *Do Language Models Need Sleep?* asks when that consolidation should happen. Before clearing the KV cache, a hybrid SSM–attention model makes N extra passes over the context it is about to drop, folding it into the SSM blocks' fast-weight state. It then answers in one pass with no looping ([arXiv:2605.26099](https://arxiv.org/abs/2605.26099) (Lee et al., CMU, UMD, 2026-06, preprint)). On GSM-Infinite problems longer than the window (Ouro 1.4B with six added layers, 1,600 held-out problems, no chain of thought), four sleep passes lifted 6-operation accuracy from 0.419 to 0.615. Easy problems were saturated either way. The authors' reading is that **the bottleneck is the compute spent turning context into state, not memory capacity**. All tasks are synthetic and the models are 2B or smaller. Training cost grows with N and is unstable, and nothing tests forgetting across repeated consolidations.

The limit all of these share is **exact recall**. Artificial Hippocampus Networks keep a 32K sliding window as lossless memory and fold every key–value pair that leaves it into a fixed-size recurrent state ([arXiv:2510.07318](https://arxiv.org/abs/2510.07318) (Fang et al., ByteDance Seed, 2025-10, preprint)). On Qwen2.5-3B at 128K, that cut FLOPs by 40.5% and the cache by 74%, and the LV-Eval average rose from 4.41 to 5.88, though full attention scores very low there. On RULER needle retrieval (NIAH single_1) at 128K (Qwen2.5-7B), **the compressed memory scored 26.8% against 98.6% for full attention, the same as dropping the old tokens outright (26.8%)**. The authors say so: fixed-size memory "may impair performance on tasks that require exact recall". A compressed state helps with gist and hurts with needles, and the needle is the case that text memory with search handles well.

### Reconstructive memory

Store **fragments** (facts, events, procedures) with source pointers, and assemble a task-specific memory at retrieval time rather than replaying stored transcripts. The risk is confabulated connections between fragments ([13](13-putting-it-together.md#a-note-on-reconstructive-memory)).

### Designed memory vs. searching the raw record

Extraction-based memory (Mem0's fact store, Zep's temporal graph) decides what to keep *before any question arrives*. [arXiv:2610.29823](https://arxiv.org/abs/2610.29823) (Peng, 2026-10) asks whether that still pays once the model can search the raw history with its own tools. On one LoCoMo conversation (419 turns, 152 questions), **Mem0 beats full context only with the weakest model** (GPT-4o-mini, 78% vs. 74%). With GPT-6 Luna and Claude Opus 5.5 it ties or loses, and its build alone costs more than a whole full-context run. Two findings travel as design rules:

- **The writer caps every reader.** A stronger reader on a store a weaker model wrote barely helps: on Zep's GPT-4o-mini graph, Opus 5.5 scores 45% against GPT-4o-mini's 43%. Extraction loses information for good; a verbatim record doesn't.
- **With a strong model, keep the raw record and give it search tools.** A coding agent (Pi) reading the raw history as one file scored 99% at under half full context's cost.

![Correct rate vs. cost per rollout for each model and memory method on LoCoMo; the frontier runs BM25 → full context → Pi](../sources/images/peng-memorytax-fig1.png)
*Image Source: Peng (2026)*

The paper's own caveats: one conversation, one run per cell, a GPT-4o-mini judge, and most of the agents' lead came from photo captions only they could read — on questions without photo evidence, Pi and full context differ by one answer. Read it as a direction, not a benchmark result. It points the same way as [index-plus-detail](#index-plus-detail): keep the source, make it searchable, and let the model decide what to load.

A controlled grid points the same way at larger scale. Yuan et al. crossed three write strategies (raw 3-turn chunks, Mem0-style extracted facts, MemGPT-style summaries) with three retrievers on all ten LoCoMo conversations (1,540 questions, GPT-5-mini, top-5). **The retriever moved average accuracy by 20 points (BM25 57.1%, cosine 73.4%, hybrid with rerank 77.2%). The write strategy moved it by 3–8 points.** Raw chunks, which need no LLM call to write, scored highest with hybrid retrieval (81.1%, against 77.3% for extracted facts and 73.3% for summaries). Retrieval failures accounted for 11–46% of all questions and failures to use a retrieved memory for 4–8% ([arXiv:2603.02473](https://arxiv.org/abs/2603.02473) (Yuan et al., ICLR 2026)). The write strategies are prompt reimplementations, not the shipped systems. The grid uses one model and one benchmark, reports no variance, and has an LLM judge assign the failure labels. Write-time information loss isn't measured on its own, so a fact that was never stored in enough detail can also show up as a retrieval failure. So invest in retrieval before write-time cleverness. The authors expect the raw-chunk advantage to shrink when the budget forces compression.

Over a long task rather than a long conversation, the same choice shows up as **fidelity versus tractability**. Summarizing at write time makes reading easy but "can discard details whose relevance is evident only in hindsight". PRO-LONG gives the agent an append-only `log.txt` of every observation, action and outcome, and has it read the log with grep and Python instead of loading it ([arXiv:2607.20064](https://arxiv.org/abs/2607.20064) (Fox et al., 2026-10, preprint)). On 25 public ARC-AGI-3 games (500-action cap, five runs or fewer per model), the log lifted pass@1 by **15.7–21.0 points over the same coding agent without it**, across three frontier models (GPT-5.5: 41.2% vs. 24.0%). Each step up the tool ladder added accuracy: read-only 23.1%, plus grep 27.2%, plus Python 38.3%, plus write and edit 41.2%. Cutting the loaded context from 244K to 64K tokens left PRO-LONG unchanged (44.3%, within its interval), while the no-log agent fell steadily. The evidence is two game benchmarks with small samples and wide run-to-run variance (best@5 60.1% against pass@1 41.2%). Each log covers one task, so this is history within a task, not memory across users or sessions, and no Mem0-style store was run against it. The design is the coding-agent long-context result from [04](04-retrieval.md#the-shift) applied to the agent's own trajectory. JAZ makes the same case against a shipped memory system ([arXiv:2609.26891](https://arxiv.org/abs/2609.26891) (Li et al., MIT, 2026-09, preprint)). Its agent keeps every input and its own history as REPL variables. When the window fills, it hands the whole history by reference to a subagent, which searches it with code. On the far-recall subset of StuLife (207 graded tasks in a 1,284-task sequence, GPT-5.4 nano, three runs), this passed **69.9% against 61.8% for Letta (MemGPT), at $18.3 per run against $42.1**. Over all 939 graded tasks the gap shrinks to 72.6% vs. 70.9%. The case behind the gap is exact recall. Letta's semantic `conversation_search` returned near-misses where an exact substring match was needed. The authors configured Letta themselves: its default search backend returned mostly empty results, and only one of their prompts avoided infinite loops. The history is lossless within one long episode, so nothing is distilled, updated or forgotten.

### Learning the memory operations with RL

Mem0-style stores decide with a prompt when to ADD, UPDATE, DELETE or ignore an entry. [arXiv:2508.19828](https://arxiv.org/abs/2508.19828) (Yan et al., 2025, preprint) trains that decision instead. A Memory Manager picks the operation and is rewarded only by whether a frozen Answer Agent then gets the question exactly right, so no operation labels are needed; **152 training questions** from LoCoMo were enough. With LLaMA-3.1-8B-Instruct on 1,307 LoCoMo test questions (adversarial subset excluded, baselines re-implemented by the authors), the GRPO-trained system reaches **F1 45.02 against 35.04 for the strongest baseline, MemoryOS**. It beats supervised imitation of GPT-5 trajectories (judge score 62.74 vs. 58.76), though on Qwen-2.5-7B the two nearly tie (61.51 vs. 61.13). The paper reports no seeds or variance, and the abstract names Mem0 as the baseline while Table 1 shows MemoryOS ahead of it, so cite the table. Readers are 8B-class only. To try this, MemFactory packages extractor, updater and retriever modules with a GRPO trainer and ships re-implementations of Memory-R1, MemAgent and RMM ([arXiv:2603.29493](https://arxiv.org/abs/2603.29493) (Guo et al., MemTensor, 2026-04, preprint)). The paper tests only the MemAgent agent, against its own untrained checkpoint. On the authors' shortened in-distribution sets, the average rose 14.8% relative (0.31 to 0.36) at Qwen3-1.7B and 7.3% at Qwen3-4B, with four trials per question and no variance reported. The 1.7B score on the out-of-distribution set fell. Treat it as a scaffold, not as evidence that the earlier results reproduce.

**Learning from the user's corrections.** PAHF asks before acting when a preference is ambiguous and corrects memory after a wrong action, with notes merged by similarity ([arXiv:2602.16173](https://arxiv.org/abs/2602.16173) (Liang et al., 2026-02, preprint)). With simulated users and GPT-4o on an embodied task, using both channels gave 70.5% success after learning and 68.8% after the preferences flipped; asking-only memory fell to 35.7% after the flip, below no memory (44.8%), because confident notes stopped it asking. Correction-only was close behind (68.3%, within noise). Simulated users only.

**Revising stored lessons against later outcomes.** Reflection memories are usually written once and never corrected, so an overgeneralised lesson ("put larger numbers first") keeps being retrieved after it starts doing harm. ReHarness adds a backward step. After each task, a revision agent rewrites the reflections it retrieved for that task, using the new trajectory as feedback, and each revision has to stay grounded in the reflection's own source trajectory ([arXiv:2610.12668](https://arxiv.org/abs/2610.12668) (Xiao et al., 2026-10, preprint)). Over three continual-learning benchmarks, three frontier backbones and three stream orderings, it reached a **normalized gain of 0.240, against 0.168 for top-5 raw trajectories, 0.164 for the full raw history and 0.131 for Mem0**. Turning revision off on one benchmark dropped it from 0.217 to 0.144. The lead over raw history is modest: the adjusted p-values were 0.039 and 0.043, and full raw history tied it in some cells. The method needs a reward that says what went wrong; it did poorly on noisy-reward poker. It also keeps raw trajectories for later revision, and one CL-Bench stream with Claude cost about $254 against $85 for top-5 raw (with prompt caching). This is update-over-append ([hygiene](#memory-hygiene)) driven by later outcomes rather than by new statements.

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

**Memory over a million tokens.** BEAM builds synthetic dialogues of 100K to 10M tokens with probes for ten memory abilities, and its LIGHT scheme adds a running scratchpad of facts and a working-memory buffer to top-5 retrieval ([arXiv:2510.27246](https://arxiv.org/abs/2510.27246) (Tavakoli et al., ICLR 2026)). Whole-history models fall from 0.24 to 0.28 average score at 100K to 0.104 to 0.133 at 10M (four backbones; at 10M, the latest window that fits). LIGHT beats plain RAG by only a few points (Qwen2.5-32B: 0.238 vs 0.211 at 10M) and loses to it with Gemini-2.0-flash (0.192 vs 0.216). Contradiction resolution stays near zero for every system. One run, small 2025 models.

Memory failures are slow and silent. Test recall across sessions, update correctness and stale-memory rate ([12](12-evaluating-context.md#write-memory)). In production, also track **memory hit rate** (the share of queries where a retrieved memory was actually relevant) and log which memory entries went into each answer, so a bad answer can be traced back to the memory that caused it.

Public multi-turn benchmarks stress later turns, questions that aren't standalone, topic switches and unanswerable questions: **CAsT** (query understanding, with a large gap between automatic and oracle rewrites), **QReCC** (rewrite, retrieve, read), **TopiOCQA** (topic switching), **CORAL** (retrieval, generation and citation) and **mtRAG** (human-written, multi-domain). Mixed-initiative sets such as **InSCIt** and **OR-ShARC** test the decision to ask a clarifying question instead of answering.

---

## Pitfalls

- **Append-only memory.** Symptom: "lives in Beijing" and "I moved to Shanghai" are both retrieved, and the agent picks one. Fix: use Mem0's ADD, UPDATE, DELETE, NOOP decision, and update rather than append.
- **Relative dates.** Symptom: "last week" means nothing a month later, and the agent acts on it. Fix: store absolute dates.
- **Storing what can be derived.** Symptom: memory says a function lives in one file after it has moved. Fix: don't store what the code or the tools can answer, and verify any remembered fact before relying on it.
- **FIFO as a memory policy.** Symptom: the agent forgets the task after a long conversation, because the first turns often hold its definition. Huyen calls FIFO's assumption "fatally wrong" for this reason. Fix: pin the system message and the original request, or summarize them.
- **An oversized index.** Symptom: the memory file itself eats the budget, or lines past its limit are never loaded. `MEMORY.md` is capped at 200 lines or 25 KB. Fix: one-line hooks in an index, with the detail in files fetched on demand.
- **Memory that crosses audiences.** Symptom: one user's fact shows up in another user's session. Fix: scope each entry to its audience and sanitize logs before they become memory.
- **Consolidation with no way back.** Symptom: a bad nightly merge corrupts everything. Fix: keep a pointer to the old version so you can roll back, as OpenClaw does, and keep the trajectory log.
- **Reading a benchmark as a verdict.** Symptom: picking a memory system from one table. Peng's LoCoMo result rests on 419 turns and 152 questions, one conversation and one run. Fix: run your own three-level eval, including memory hit rate.

## Try it

1. `MEMORY.md` allows 200 lines or 25 KB. What average line length uses both limits at once, and what does this say about how to write an index line?

   <details><summary>Answer</summary>

   25,000 / 200 = 125 bytes per line. An index line is a one-line hook and a pointer, not the memory itself.

   </details>

2. Choose a Mem0 operation for each new message, given stored facts "lives in Beijing" and "prefers pnpm": "I moved to Shanghai", "I still use pnpm", "I started learning Rust", "Please forget my package preference".

   <details><summary>Answer</summary>

   UPDATE, NOOP, ADD, DELETE.

   </details>

3. Memoria reports top-20 triples under 400 tokens against about 115K of full history. What's the rough compression ratio, and what do you still need to check?

   <details><summary>Answer</summary>

   More than 115,000 / 400 ≈ 288×. Ratio alone says nothing about usefulness, so check retention and answer quality, as in [12](12-evaluating-context.md).

   </details>

4. Rewrite this as a good memory entry: "Yesterday we decided the deploy script is in `scripts/deploy.sh` and the team prefers small PRs."

   <details><summary>Answer</summary>

   Drop the script location, which the repo can answer. Keep the preference with an absolute date, its scope and the reason, if known: "Team prefers small PRs (decided 2026-11-01, applies to this repo)." The date here stands in for whatever day "yesterday" was.

   </details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| Episodic or semantic memory? | Episodic records what happened, semantic records what's true, and the useful step distils the first into the second, such as three commit-format corrections into one rule. |
| Does a good memory system need a vector database? | Not always. ChatGPT's memory, as analysed here, has four layers with about 33 facts and about 15 summaries and no vector DB, and Peng found a coding agent searching raw history hit 99% at under half full context's cost, on one conversation and one run. |
| How would you handle "I moved to Shanghai" when "lives in Beijing" is stored? | Run a write-time decision between ADD, UPDATE, DELETE and NOOP, then UPDATE. Append-only leaves two contradictory facts for retrieval to choose between. |
| How do you structure user facts for reliability? | When questions aggregate, use typed state: User as Code regenerates typed Python from a fact log and reached about 99% on aggregation against 6-43% for retrieval-based memory, because a count becomes one expression. |
| What's the highest-leverage part of an index-plus-detail memory? | The one-line hook, because it decides whether the detail file ever gets opened. |
| Do you evaluate a memory system on overall answer accuracy only? | No. Evaluate at three levels, including hit rate. In Peng's test Opus 5.5 reading Zep's GPT-4o-mini graph scored 45% against GPT-4o-mini's 43%, so a stronger reader can't recover what a weak writer never stored. |
| How do short-term and long-term memory differ? | The trajectory is an append-only log that is never rewritten, while long-term memory is an archive that gets rewritten, merged and pruned. Working memory is the filtered subset of both that is in the window right now. |

## Next

[07-structured-context.md](07-structured-context.md): memory keeps facts between windows, and next comes giving the context a shape that the model and your code can both rely on.
