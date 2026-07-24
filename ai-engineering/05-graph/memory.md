---
origin: notion-export
confidence: medium
sources:
  - https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-overview
  - https://docs.langchain.com/oss/javascript/langgraph/memory
  - Memoria framework writeup (Notion copy, package forthcoming)
cleaned: 2026-07-17
---

4 memory types:

*(missing diagram — not exported from Notion)*

some products’ memory design:

**ChatGPT:**

four-layer memory architecture, viewed as a product implementation, doesn't use vector databases or introduce RAG retrieval enhancements. Its overall structure is simpler than many expect:

1. Session Metadata: Device, location, usage patterns; not persistent.
2. User Memory: Approximately 33 key preference facts; persistent, injected each time.
3. Conversation Summary: Lightweight summaries of approximately 15 recent conversations; persistent.
4. Current Session: A sliding window of the current conversation; not persistent.

**OpenClaw Hybrid Search**

1. memory/YYYY-MM-DD.md: Appends to logs, preserving original details.
2. MEMORY.md: Selected facts, actively maintained by the agent.
3. memory_search: Hybrid search using 70% vector similarity + 30% keyword weight.

How is memory consolidation triggered and rolled back?

*(missing diagram — not exported from Notion)*

With memory stratification, the next step isn't "whether to store," but rather "when to consolidate, and what to do if consolidation fails."

The failed path writes the original messages to `archive/`, preserving the complete history and preventing context loss in case of consolidation failure.

The most crucial aspect isn't how elegant the summary is, but that the process itself must be rollback-friendly. The system only moves the pointer, without deleting the original messages, so even if consolidation fails, it can return to the original archive and continue working.

---

haven’t been organized:

# Memory-augmented RAG

*(missing diagram — `Screenshot 2026-04-13 at 15.43.25.png` not exported from Notion)*

agent needs to decide when to recall, what to recall and how to use it for tool choice and response generation.

includes:

1. **Conversational RAG / multi-turn RAG**
2. **History-aware retrieval / conversational query understanding:** using dialogue history to rewrite, expand, disambiguate, or plan retrieval queries.
3. **Long-term memory for LLM agents**: persistent storage and retrieval of user preferences and agent experiences beyond a single context window.
4. **Mixed-initiative information-seeking dialogue**: the agent chooses when to answer vs ask clarifying questions when the user request is underspecified or unanswerable.

A useful modern taxonomy is the “mixed memory” framing (conversational + long-term user + episodic + working memory layers)

Memory-augmentation in multi-turn agents changes the “augmentation target” and the “control problem”:

1. **The retrieval corpus includes the conversation itself (and derived memories).**

    Instead of only retrieving from a knowledge base, systems store and retrieve prior **user messages, assistant outputs, tool results, and “distilled” memory objects**.

2. **The main challenge is not just relevance, but continuity and intent resolution.**

    Follow-up queries contain pronouns, ellipsis, references (“what about the second one?”), and topic drift. This makes *query rewriting and memory selection* central—often more than retrieval model choice.

3. **The agent must decide when to retrieve (and from where).**

    In multi-turn settings, retrieving new passages every turn can be wasteful or harmful; systems increasingly learn or implement policies like “reuse previous evidence,” “retrieve only if needed,” or “ask a clarifying question first.”


*(missing diagram — not exported from Notion)*

*(missing diagram — `Screenshot 2026-04-14 at 08.45.14.png` not exported from Notion)*

#### **Key benchmarks and what they measure**

- **CAsT (TREC Conversational Assistance Track)**: emphasizes conversational query understanding and retrieval/reranking; the overview reports large headroom for automatic systems vs manually resolved “oracle” rewrites, quantifying how crucial context resolution is.
- **QReCC**: open-domain conversational QA over a large web corpus, designed to allow training/evaluating question rewriting, passage retrieval, and reading comprehension components.
- **TopiOCQA**: open-domain convQA explicitly with topic switching; stresses multi-topic memory and efficient retrieval across turns.
- **CORAL**: benchmark for conversational RAG including passage retrieval, response generation, and citation labeling under multi-turn settings and topic shifts.
- **mtRAG**: end-to-end, human-generated multi-turn RAG benchmark emphasizing later turns, non-standalone questions, unanswerable questions, and multiple domains.
- **Mixed-initiative benchmarks/datasets (e.g., InSCIt; OR-ShARC)**: stress the *decision* to ask clarifying questions (“inquire”) vs answer, which is a key “context-driven action” capability.

### **Core methodologies for memory-augmentation**

A coherent technical taxonomy for memory-augmented conversational RAG/agents can be framed as: **(A) represent memory, (B) store it, (C) retrieve/select it, (D) integrate it into decisions and prompts, (E) update/forget it**.

*(missing diagram — not exported from Notion)*

*(missing diagram — not exported from Notion)*

1. **passed: Query rewriting and standalone question generation:  transform a context-dependent utterance into a standalone query that can drive retrieval reliably.**

    A key limitation (increasingly emphasized since 2023–2024) is that “rewrite into one question” can lose important context in long dialogues; hence t**he move toward summaries or structured memory objects, rather than a single rewritten query**

2. **History-aware retrieval: use chat history + user turn to build a retrieval plan**.

    2 approaches:

    1. **R pipeline line (CAsT / ORConvQA / CORAL / mtRAG):**

        ORConvQA explicitly shows that enabling history modeling across system components improves open-retrieval conversational QA performance, reinforcing the idea that history is not just a prompt trick but a retrieval and ranking signal.

    2. **Agentic retrieval line (industrial):**

        In Azure AI Search agentic retrieval, an LLM reads the entire chat thread, decomposes into focused subqueries (which can include chat history), runs subqueries in parallel with semantic reranking, and returns grounding data plus a query plan for downstream agent use. https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-overview?tabs=quickstarts


**Memory mechanisms: short-term vs long-term**

- **Short-term memory** (“thread/session scoped”): message history and immediate state used for continuity inside an active conversation.
- **Long-term memory** (“cross-session”): persistent memory stores for user preferences, profiles, episodic events, agent notes—retrieved when relevant.

https://docs.langchain.com/oss/javascript/langgraph/memory

LangChain’s LangGraph memory documentation (thread-scoped state + checkpointer; long-term memory via stores and namespaces), including the practical warning that long histories can cause distraction, cost/latency increases, and degrade model performance—so you need forgetting/compression strategies.

**Clarification and mixed-initiative interaction**

**Selective memory and context compression (beyond naive history stuffing)**

https://docs.langchain.com/oss/javascript/langgraph/memory

**History-Aware and Agentic Retrieval**: Systems now use the entire chat thread to build complex retrieval plans. In "agentic retrieval," an LLM analyzes the chat history, breaks down questions into subqueries, runs them in parallel, and returns grounding data alongside an activity plan

conversational information seeking (CIS)

**CONQRR: Conversational Query Rewriting for Retrieval with Reinforcement Learning**

a query rewriting model CONQRR that rewrites a conversational question in the context into a standalone question.  It is trained with a novel reward function to directly optimize towards retrieval using reinforcement learning and can be adapted to any off-the-shelf retriever.

把 conversational query rewriting 明确做成一个 retrieval 优化问题

**mt RAG: A Multi-Turn Conversational Benchmark for Evaluating Retrieval-Augmented Generation Systems**

**Multi-Turn Conversation Strategies:**

https://docs.nvidia.com/rag/latest/multiturn.html

**Strategy 1: Query Rewriting (Recommended for Best Accuracy)**

最主流的几种方法

1. History concatenation

把最近几轮对话直接拼进 prompt 或检索 query。实现便宜、延迟低，但一旦对话变长，很容易把无关历史也带进去，造成检索偏移。NVIDIA 现在也仍然保留这种 simple multi-turn mode，说明它在工业里还很常见。
****

## **Memory-Augmented Conversational RAG — Continuity under limited context window**

- Not just retrieving documents
- But **retrieving and managing conversation + agent memory**

Challenges:

- Multi-turn queries are **not standalone**
- History becomes **long + noisy**
- System must decide:
    - What to remember
    - When to recall
    - How to use memory

3.1 Memory Types  — Modern systems = **multi-layer memory system**

*(missing diagram — not exported from Notion)*

### **Data Flow**

1. **Incoming Query**: A user query hits the Orchestration Layer.
2. **Dual Retrieval**: The system queries both the **Retrieval Module** (for static knowledge) and the **Memory Module** (for historical/contextual data).
3. **Combine Results**: The **Reasoning Module** merges static knowledge and memory-based data to form a rich context.
4. **Contextual Generation**: The **Generation Module** produces an output guided by both retrieved documents and memory context.
5. **Memory Update**: After producing a response, the system updates the **Memory Module** with new interaction details (session summaries, user feedback, etc.).
6. **Response Delivery**: The final, context-enriched answer is returned to the user.

*(missing diagram — not exported from Notion)*

1. Short-term/session memory — Conversation history (session-level)—  in-memory DB

2. Long-term memory — **NoSQL Datastores / GraphDB**

Stored in vector databases.

Used for knowledge recall across sessions.

User preferences, past events, profiles

1. **Episodic Memory**

    Stores key events, decisions, or failures.

    Useful for autonomous workflows and multi-day tasks.

2. **Semantic Memory**

    Stores general world knowledge or domain-specific expertise.

3. **Tool Memory**

    Agents retrieve knowledge from tools:

    - Web search
    - APIs
    - SQL queries
    - Cloud file systems

3. Agentic memory

**Agentic retrieval / agentic memory**: model-assisted planning that uses the **entire chat thread** (and sometimes stored memories) to decide retrieval strategy, tool calls, and whether to reuse prior evidence.

- Memory used for:
    - Planning
    - Retrieval decisions
    - Tool usage

From 2024–2026 specifically, the sharpest trend is moving from “include chat history” to **selective, structured, and controllable memory**: summarize or compress history, store “distilled” memories, retrieve only the most relevant past turns, and add safety/governance controls (scope, ACLs, injection defenses). 

Memory-Augmented Agent Architecture

```python
User Query
   ↓
[1] Query Understanding
   ↓
[2] Policy Decision
   ├── retrieve docs?
   ├── recall memory?
   ├── ask clarification?
   ↓
[3] Retrieval Layer
   ├── Vector DB (memory)
   ├── Knowledge base
   ├── Tools (API)
   ├── other DBs
   ↓
[4] Context Builder
   ├── summary
   ├── selected memory
   ├── retrieved docs
   ↓
[5] LLM
   ↓
[6] Memory Update
   ├── store event
   ├── update profile
   ├── compress history
```

methodology: memory lifecycle

*(missing diagram — not exported from Notion)*

The paper gives a **5-step memory pipeline**:

(A) Represent memory

- Raw history, summaries, structured memory

(B) Store memory

- Vector DB
- Structured stores

(C) Retrieve/select memory

- Query rewriting
- History-aware retrieval

(D) Use memory

- Prompt construction
- Tool decisions
- Planning

(E) Update/forget memory

- Summarization
- Compression
- Filtering

some method / strategies from different companies/ libraries:

1. MCSF: https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-memory?tabs=conversational-agent
    1. **Extraction:** When a user interacts with an agent, the system actively extracts key information from the conversation, such as user preferences, facts, and relevant context. For example, preferences like "allergic to dairy" and summaries of recent activities are identified and stored.
    2. **Consolidation:** Extracted memories are consolidated to keep the memory store efficient and relevant. The system uses LLMs to merge similar or duplicate topics so that the agent doesn't store redundant information. Conflicting facts, such as a new allergy, are resolved to maintain an accurate memory.
    3. **Retrieval:** When the agent needs to recall information, it searches the memory store for the most relevant memories. This allows the agent to quickly surface the right context, making conversations feel natural and informed. For best results, retrieve stable user profile information early in the conversation so the agent can personalize responses.

1. History-based - add all `chat history` / latest N history into prompt
2. **Memory/context Compression:**  summarize/extract/ distilled memory
    1. tools
        - LangChain summary memory
        - LangGraph memory compression
        - “distilled memory”
    2. Conversation summarization —- into a paragraph
    3. Structured memory extraction — user preference, key fact, task state
    4. Rolling summary — update summary every turn
    5. 优点
        - 控制 token
        - 提升 relevance
    6.  问题
        - 信息损失（lossy）
        - summary quality 依赖模型
3. Retrieval-based Memory: 把 memory 存到 vector DB，然后检索
    1. store:
        - user message
        - assistant response
        - tool output
        - extracted memory（结构化）
    2. retrieval method:
        1. Semantic search

        ```
        query → embedding → top-k memory
        ```

        2. Hybrid search: keyword + semantic

        3. Recency + relevance

        ✅ 优点

        - scalable
        - 可跨 session（long-term memory）

        ❌ 问题

        - retrieval noise
        - embedding drift —
        - latency

    tools:

    - LangGraph memory store
    - Microsoft ChatHistoryMemoryProvider
4. Query Rewriting / Context Understanding
    1. rewrite user’s query into complete one
        1. User: what about the second one?
        → rewrite → what about the second product you mentioned earlier?
        2. don’t use memory directly, but use memory to rewrite better query
        3. 优点
        - 提升 retrieval 质量
        - 适合 multi-turn RAG

            问题

        - 丢 context
        - rewrite 不稳定

        database:

        - CANARD
        - QReCC

### Memory Architecture

Multi-layer memory

| 层级 | 内容 |
| --- | --- |
| Working memory | 当前上下文 |
| Short-term | 当前对话 |
| Long-term | 用户信息 |
| Episodic | 事件记录 |

# some tools/ studies:

## 1. Memoria: A Scalable Agentic Memory Framework  — **Python package is *forthcoming***

Memoria- A Scalable Agentic Memory Framework for Personalized Conversational AI.pdf

**1. Session-Level Summarization (Short-term memory) — compression :**

Dynamically compresses ongoing dialogue into a running summary stored per session ID in SQL. Keeps the LLM coherent within and across turns without flooding the context window.

**2. Knowledge Graph (KG) User Modeling (Long-term memory) —** Extracts structured triplets (subject → predicate → object) from user messages and stores them in both SQL and a vector database. These triplets build an evolving user persona capturing preferences, topics, and behavioral patterns.

A key innovation is **exponential decay weighting** — more recent triplets get higher priority, resolving contradictions and keeping the model aligned with the user's current state.

## How Memoria Actually Works (In Detail)

### 1. The Four Core Modules

**Structured Conversation Logging (the foundation)**
Every message gets stored in SQLite with: timestamp, session ID, raw user + assistant messages, extracted KG triplets, session summary, and token usage. This creates a queryable, time-indexed memory bank that survives across sessions.

**Dynamic KG Construction**
After every user message, an LLM call extracts structured triplets in the form:

> `(subject, predicate, object)`
e.g. `(user, prefers, equity stocks)` or `(user, works_as, financial analyst)`
>

These triplets are stored two ways simultaneously:

- **SQL** — raw text for traceability
- **ChromaDB (vector DB)** — as dense embeddings alongside metadata (timestamp, source message, username)

Crucially, only *user messages* go into the KG — not assistant responses — so it purely reflects the user's intent and identity.

**Session Summarization**
After each exchange, Memoria sends both the user message and assistant response to the LLM with a summarization prompt. If a summary already exists for that session ID, it gets *updated* (not replaced). If not, a fresh one is created. Retrieval is deterministic — just a direct session ID lookup.

**Semantic Retrieval**
When context is needed, the incoming query is converted to an embedding and used to pull the top-K most semantically similar triplets from ChromaDB, filtered by username. These triplets then get weighted before being injected into the prompt.

### 2. The Weighting Mechanism (The Key Innovation)

This is what separates Memoria from competitors. Before triplets hit the prompt, each one gets an **exponential decay weight** based on how old it is:

```
wᵢ = e^(−α · xᵢ)
```

Where `xᵢ` = minutes since that triplet was created, and `α` = decay rate (they use 0.02).

To prevent very old triplets from becoming zero (and being effectively ignored), they apply **min-max normalization** first:

```
x_norm = (x − x_min) / (x_max − x_min)
```

Then weights are normalized so they all sum to 1:

```
w̃ᵢ = wᵢ / Σwⱼ
```

The result: recent triplets dominate the prompt context, older ones still contribute softly, and if a user contradicts something they said before (e.g. changed their job or preference), the newer triplet wins automatically — no manual conflict resolution needed.

---

### 3. Full Flow for a Returning User

```
User sends message
        ↓
1. Embed the query
2. Search ChromaDB for top-20 similar triplets (filtered by username)
3. Apply exponential decay weights to each triplet
4. Fetch session summary from SQL (by session ID)
5. Build prompt = system prompt + session summary + weighted triplets + user message
6. LLM generates response
        ↓
Post-response:
7. Extract new triplets from user message → store in SQL + ChromaDB
8. Update session summary in SQL
```

---

## How You Can Use It

The paper says the open-source Python package is *forthcoming*, but based on everything described, here's how you'd integrate it practically:

### Setup (based on their stack)

```python
# Their confirmed stack:
# - SQLite3 (local, no setup needed)
# - ChromaDB (local vector DB)
# - OpenAI text-embedding-ada-002 (embeddings)
# - Any LLM via API (they used GPT-4.1-mini)

pip install chromadb openai sqlite3
```

### The Integration Pattern They Describe

Memoria is designed as a **wrapper around your existing chat app**, not a replacement. The pattern is:

```python
# Pseudocode reflecting their described API

from memoria import Memoria

memory = Memoria(user_id="alice", session_id="session_001")

# Before sending to LLM — retrieve context
session_summary = memory.get_session_summary()
relevant_triplets = memory.get_weighted_triplets(query=user_message, top_k=20)

# Build your prompt
prompt = build_prompt(
    system="You are a helpful assistant.",
    summary=session_summary,
    triplets=relevant_triplets,
    user_message=user_message
)

# Your LLM call (unchanged)
response = llm.chat(prompt)

# After response — update memory
memory.update_summary(user_message, response)
memory.extract_and_store_triplets(user_message)
```

### Key Configuration Knobs

| Parameter | Their Value | What it controls |
| --- | --- | --- |
| `top_k` | 20 | How many triplets retrieved per query |
| `decay_rate (α)` | 0.02 | How fast old triplets lose influence |
| Embedding model | `text-embedding-ada-002` | Retrieval quality |
| LLM | `GPT-4.1-mini` | Triplet extraction + summarization |

**Tuning tips from their results:**

- Higher `α` = steeper decay = model almost ignores anything older than a few sessions. Good for fast-changing preferences.
- Lower `α` = gentler decay = older context stays relevant longer. Good for stable traits like profession or long-term goals.
- `K=20` hit the sweet spot between context richness and token efficiency (they got under 400 avg tokens vs 115K for full context).

---

### Where to Watch for the Release

Since the library isn't public yet, your best options right now are:

1. **Watch the paper authors on GitHub** — Bhaskarjit Sarmah, Samarth Sarin (BlackRock team)
2. **Search PyPI for `memoria-memory`** once released
3. **Replicate it yourself** — the paper gives enough detail. The core is: SQLite + ChromaDB + an LLM call for triplet extraction + the decay formula above. Probably ~300–400 lines of Python to build a working version.

Want me to sketch out a working prototype implementation based on the paper's specs?

1. Memory in the Age of AI Agents: A Survey

    **Forms → Functions → Dynamics**.

    ### 1. Forms — *What carries the memory?*

    **Token-level memory** — stored as text/tokens in an external buffer:

    - *Flat (1D)* — plain conversation logs, rolling windows, retrieved snippets
    - *Planar (2D)* — graph-structured memory (knowledge graphs, memory graphs like Zep, A-Mem)
    - *Hierarchical (3D)* — layered structures with summaries at multiple levels of abstraction

    **Parametric memory** — knowledge baked into model weights:

    - *Internal* — what the LLM already "knows" from pretraining
    - *External* — continual fine-tuning or LoRA adapters trained on accumulated experience

    **Latent memory** — stored as neural activations or hidden states:

    - *Generate* — synthesizing new latent representations from experience
    - *Reuse* — caching and replaying KV states
    - *Transform* — compressing or restructuring latent representations

    ### 2. Functions — *Why do agents need memory?*

    **Factual Memory** — records knowledge from agent-environment interactions:

    - *User factual* — preferences, identity, history (what Memoria does)
    - *Environment factual* — world state, task context, domain facts

    **Experiential Memory** — accumulates problem-solving capability over time:

    - *Case-based* — storing past solved examples to reuse
    - *Strategy-based* — distilling generalizable approaches
    - *Skill-based* — extracting reusable tools or code from experience
    - *Hybrid* — combining the above

    **Working Memory** — manages active information during a task:

    - *Single-turn* — reasoning traces, scratchpads, intermediate outputs
    - *Multi-turn* — dialogue state, partial plans carried across turns

    ### **3. Dynamics — *How does memory operate over time?***

    **Memory Formation** (how memories are created):

    - Semantic summarization — compress conversations into summaries
    - Knowledge distillation — extract reusable patterns
    - Structured construction — build KG triplets, schemas
    - Latent representation — encode into vectors or hidden states
    - Parametric internalization — fine-tune the model itself

    **Memory Evolution** (how memories change):

    - *Consolidation* — merging redundant or related memories
    - *Updating* — revising outdated facts (conflict resolution)
    - *Forgetting* — pruning low-utility or stale memories

    **Memory Retrieval** (how memories are accessed):

    - *Timing* — when to retrieve (at start, on demand, continuously)
    - *Query construction* — how to form the retrieval query
    - *Strategies* — sparse (keyword), dense (semantic), graph traversal, hybrid
    - *Post-retrieval processing* — reranking, filtering, compression before injection

### **5. Benchmarks (What is Evaluated)**

Focus shifts from **single QA → multi-turn reasoning**

Key aspects:

- Later-turn performance
- Non-standalone questions
- Topic switching
- Unanswerable queries
- Clarification ability

👉 Important benchmarks:

- CAsT
- QReCC
- CORAL
- mtRAG

# **Performance and Scalability**

**Caching**:

- Cache frequently accessed memory entries (e.g., recent session data) to reduce retrieval latency.
- Use a write-through or write-back strategy when updating memory stores.

**Indexing**:

- Maintain efficient indexes on metadata fields (e.g., user_id, session_id) in NoSQL stores.
- Update vector indexes periodically or asynchronously for memory embeddings.

**Load Balancing**:

- Deploy multiple instances of the Memory Module behind a load balancer.
- Auto-scale based on query volume and memory write operations.

**Latency Considerations**:

- Use asynchronous I/O for memory lookups and retrieval operations.
- Consider precomputing embeddings or summaries of memory entries to speed up contextual fusion.

# **Monitoring, Observability, and Maintenance**

**Metrics**:

- **Memory Hit Rate**: Ratio of queries that leverage relevant memory entries.
- **Latency Metrics**: Time spent in memory retrieval, reasoning fusion, and generation steps.
- **Update Frequency**: How often memory is appended or pruned.

**Logging and Tracing**:

- Log each query and the memory entries used to provide transparency and auditability.
- Use distributed tracing (e.g., OpenTelemetry) to visualize end-to-end request flow, including memory lookups.

**Automated Maintenance**:

- Schedule periodic memory pruning tasks to remove stale data.
- Implement differential storage: store only deltas to reduce memory bloat.
- Regularly retrain or update embedding models to ensure semantic relevance over time.

# **Security and Compliance**

**Access Controls**:

- Enforce RBAC/ABAC on memory endpoints to restrict who can read or modify memory.

**Encryption**:

- Encrypt memory data at rest (AES-256) and in transit (TLS).

**Compliance**:

- Anonymize or tokenize sensitive user data.
- Comply with regulations (GDPR, CCPA) by supporting data deletion and user consent mechanisms.

# **Common Challenges and Solutions**

**Memory Overload**:

- Use summarization techniques or vector-based relevance scoring to keep memory concise. e.g. Summarize past content performance while retaining key insights

**Stale Context**:

- Implement time-to-live (TTL) and decay policies to discard old, irrelevant entries. e.g. Archive outdated brand guidelines while maintaining version history

**Conflicting Information**:

- Apply conflict resolution strategies: recent memory entries supersede older ones, or trust high-confidence sources over ambiguous ones. e.g. Resolve conflicts between different campaign messaging
