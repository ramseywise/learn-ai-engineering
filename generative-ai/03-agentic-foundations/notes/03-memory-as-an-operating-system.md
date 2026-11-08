---
origin: synthesis  # was: course-synthesis
sources:
  - "DeepLearning.AI, LLMs as Operating Systems: Agent Memory (Charles Packer, Sarah Wooders), Labs 1–6 and slides — https://www.deeplearning.ai/short-courses/llms-as-operating-systems-agent-memory/ ; snapshot upstream https://github.com/frankwwu/LLMs-as-Operating-Systems--Agent-Memory"
  - "Packer et al. 2023, MemGPT: Towards LLMs as Operating Systems — https://arxiv.org/abs/2310.08560"
  - Lakshmanan & Hapke, Generative AI Design Patterns (O'Reilly 2025), ch 8 P28 Long-Term Memory
  - "Chhikara et al. 2025, Mem0 — https://arxiv.org/abs/2504.19413"
  - "adv-11/AgenticAIFrameworks: Letta/self-editing memory from scratch, LangGraph/langMem — https://github.com/adv-11/AgenticAIFrameworks"
  - https://arxiv.org/abs/2304.03442
  - https://arxiv.org/abs/2505.22101
  - https://arxiv.org/abs/2607.26637
  - https://github.com/firstbatchxyz/mem-agent/blob/main/main.pdf
  - "James Phoenix & Mike Taylor, Prompt Engineering for Generative AI (O'Reilly, 2024), ch. 6"
  - https://arxiv.org/abs/2409.07429
  - https://arxiv.org/abs/2502.12110
  - https://arxiv.org/abs/2508.09736
  - https://arxiv.org/abs/2601.01885
  - https://arxiv.org/abs/2601.03192
  - "Zhou et al. 2025, Memento — https://arxiv.org/abs/2508.16153"
  - "Agashe et al. 2024, Agent S — https://arxiv.org/abs/2410.08164"
  - "Wang et al. 2023, JARVIS-1 — https://arxiv.org/abs/2311.05997"
  - "Salama et al. 2025, MemInsight — https://arxiv.org/abs/2503.21760"
  - "Hu et al. 2023, ChatDB — https://arxiv.org/abs/2306.03901"
  - "Wang et al. 2026, Memex(RL) — https://arxiv.org/abs/2603.04257"
  - "Xu et al. 2026, Contextual Agentic Memory is a Memo — https://arxiv.org/abs/2604.27707"
  - "Zhou et al. 2026, Are We Ready For An Agent-Native Memory System — https://arxiv.org/abs/2606.24775"
  - https://arxiv.org/abs/2602.02007
  - https://arxiv.org/abs/2609.23986
  - https://arxiv.org/abs/2602.07755
confidence: high
cleaned: 2026-11-01
  - Schuurmans 2023, Memory Augmented Large Language Models are Computationally Universal — https://arxiv.org/abs/2301.04589
  - Liu et al. 2024, From LLM to Conversational Agent: A Memory Enhanced Architecture with Fine-Tuning of Large Language Models (RAISE) — https://arxiv.org/abs/2401.02777
---

# 3 — Memory as an operating system

> MemGPT treats the context window as RAM and external stores as disk, and makes the agent its own memory manager: every memory edit, search and eviction is a tool call.

On Monday the restock agent learns that a supplier's delivery time has doubled, and next Monday, in a new session, it knows nothing about that. A model has no state between calls: everything it appears to remember was put into the prompt by someone. So the real question is who decides what goes in, what comes out and what happens when there is no more room. MemGPT's answer is that the agent can do that work itself with tools, which turns a storage problem into a behavior you have to design and test.

---

## What this note adds

Memory theory (types, hygiene, the memory loop, production designs) lives in [context engineering 06 — memory](../../../ai-engineering/02-context-engineering/notes/06-memory.md). Read that first. This note covers only what MemGPT and its successor Letta add on top:

- the **operating-system framing**: tiers, paging, and an agent that pages for itself;
- **self-editing memory** through tools;
- **heartbeats**, which let one user message drive many LLM calls;
- the **Letta API** as a concrete implementation, from the DeepLearning.AI course.

---

## The OS analogy

An LLM has a fixed context window, the way a CPU has fixed RAM. MemGPT (Packer et al. 2023) borrows the answer operating systems use: a memory hierarchy with paging. The difference is that the LLM decides what to page in and out.

The paper's evidence is about recall across sessions. In **deep memory retrieval**, the agent is asked about a detail from one of five earlier chat sessions. GPT-4 alone scored **32.1%** and GPT-4 with MemGPT **92.5%**. The setup favours MemGPT, though: the baseline saw only a lossy summary of the earlier sessions, while MemGPT could page through the full history with search. On document QA (NaturalQuestions-Open, with the same retriever for both), the fixed-context models were capped by however many retrieved documents fit in the window. MemGPT could keep querying archival storage, so its accuracy didn't fall as the document set grew. The limits matter as much as the wins. MemGPT often **stopped paging before it reached the gold document**, and with GPT-3.5 it degraded badly because that model's function calling was weak. The design only works as well as the model's tool use ([arXiv:2310.08560](https://arxiv.org/abs/2310.08560) (Packer et al., 2023-10)).

| OS concept | MemGPT equivalent |
|---|---|
| RAM | the context window |
| Disk | archival memory and recall memory (databases) |
| Page in | a search tool call returns results into context |
| Page out | summarize old messages and evict them to recall memory |
| Kernel | the agent loop that compiles state into a prompt each step |
| Interrupt | a heartbeat request that schedules another step |

![MemGPT key ideas: self-editing memory, inner thoughts, every output is a tool call, looping via heartbeats](../sources/images/packer-wooders-agent-memory-fig1.png)

*Figure: the four ideas behind MemGPT (Letta course, L2).*

The four ideas:

1. **Self-editing memory.** The agent writes to its own memory with tools.
2. **Inner thoughts.** The agent reasons privately; the user sees only what it sends.
3. **Every output is a tool call.** Even replying to the user is a tool (`send_message`).
4. **Looping via heartbeats.** A tool call can set `request_heartbeat=True` to get another turn without waiting for the user.

The analogy has a formal floor. Schuurmans ([arXiv:2301.04589](https://arxiv.org/abs/2301.04589) (Schuurmans, 2023-01, preprint)) shows a model that conditions on a bounded context is a finite automaton, and that giving it a read/write associative memory plus a regex loop removes the limit: Flan-U-PaLM 540B with a dictionary as memory simulated a universal Turing machine (15 states, 2 symbols) with all 29 state-symbol prompts answered correctly in one greedy call each. The model is the CPU, the dictionary the RAM, and one key holds the next prompt. This is a proof of capability, not a memory design: it checked one model once with no failure rates, and the author reports it was brittle (other LLMs failed, prompts had to be terse, if-then-else was not reliable).

---

## Context compilation

Agent state lives in a database, not in the prompt. Each step, the server **compiles** that state into a prompt:

| Context section | Content | Who writes it |
|---|---|---|
| System prompt | instructions, tool rules | developer |
| Core memory | labelled blocks (persona, human, ...) | the agent, through tools |
| External memory stats | counts of archival and recall entries | the server |
| Recursive summary | summary of evicted messages | the server, on overflow |
| Chat history | recent messages | the loop |

The memory stats line matters: it tells the agent that there is more it does not currently see, so it knows when to search.

Each core-memory block has a label, a character limit and a value. Blocks are rows in a database with unique IDs. The compiled prompt renders each one with its label and fill level; schematically:

```text
<persona characters="52/2000">
You are a helpful assistant and you always use emojis
</persona>
<human characters="18/10000">
My name is Charles
</human>
```

![Memory compilation: blocks with label, limit and value rendered into the prompt](../sources/images/packer-wooders-agent-memory-fig6.png)

*Figure: compiling blocks into the context window (Letta course, L4).*

---

## Two tiers, three stores

| Tier | Store | In context? | Size | Tools |
|---|---|---|---|---|
| 1 | Core memory | always | small (e.g. 2,000 chars per block) | `core_memory_append`, `core_memory_replace` |
| 2 | Recall memory | no | all past messages | `conversation_search` |
| 2 | Archival memory | no | unbounded, vector-indexed | `archival_memory_insert`, `archival_memory_search` |

![Two tiers: core memory in context, archival and recall memory outside](../sources/images/packer-wooders-agent-memory-fig5.png)

*Figure: memory tiers in MemGPT (Letta course, L2).*

When the context fills up, the server summarizes the oldest messages and moves them to recall memory. The messages are still searchable; they just cost nothing until the agent asks for them.

![Summarize and evict to recall memory](../sources/images/packer-wooders-agent-memory-fig3.png)

*Figure: overflow handling (Letta course, L2).*

Archival memory is general purpose: facts the agent chose to keep, plus documents a developer loaded. Because core memory has a hard limit, the agent has to decide what earns a place there and what goes to archival.

![Archival memory as the second tier, with the core memory limit](../sources/images/packer-wooders-agent-memory-fig4.png)

*Figure: why a second tier is needed (Letta course, L2).*

---

## Heartbeats: one message, many steps

Every tool in MemGPT takes a `request_heartbeat` argument. If the agent sets it, the server calls the model again with the tool result, without waiting for the user. That is how an agent chains a memory search, a memory edit and a reply from one user message.

![Heartbeats chain LLM calls](../sources/images/packer-wooders-agent-memory-fig2.png)

*Figure: heartbeats (Letta course, L2).*

The task-queue system prompt from Lab 4 makes the rules explicit: heartbeats keep the loop alive, inner monologue stays at 50 words or fewer, and `send_message` is the only action the user sees.

---

## Building it from scratch

Lab 1 builds self-editing memory with raw OpenAI calls: a dict for memory, one tool to write to it, and the memory serialized into a system message on every call. The full loop is in [02 — the raw loop](02-tool-use-and-react.md#the-raw-loop-no-framework). The memory-specific part is small:

```python
import json

agent_memory = {"human": "", "agent": ""}

def core_memory_save(section: str, memory: str):
    agent_memory[section] += "\n" + memory     # the agent edits its own context

# rebuilt on every call: this is context compilation in one line
memory_message = {"role": "system", "content": "[MEMORY]\n" + json.dumps(agent_memory)}
```

The system prompt ends with "When you learn new information, make sure to always call the core_memory_save tool." Without that instruction the model rarely saves anything.

### Two tiers for the restock agent

Add a size limit and a second store and the whole design appears. The block below has no LLM in it; the calls at the bottom are the ones a model would choose to make, so you can see what each one changes:

```python
# Self-editing memory for the restock agent: a small core that is always in context,
# and an archive that is only reached by a tool call. No LLM needed to see the mechanics.
CORE_LIMIT = 100
core = {"policy": "Order just in time. Keep two weeks of peak sales."}
archive = []

def core_append(label, text):
    new = core.get(label, "") + " " + text
    if sum(map(len, core.values())) - len(core.get(label, "")) + len(new) > CORE_LIMIT:
        return f"Error: core is full (limit {CORE_LIMIT}). Move detail to the archive."
    core[label] = new.strip()
    return "ok"

def archive_insert(text):
    archive.append(text)
    return f"ok, {len(archive)} passages in archive"

def archive_search(query):
    return [p for p in archive if query.lower() in p.lower()] or "no match"

def compile_context(trajectory):
    """Rebuilt for every model call. This is all the model will ever know."""
    blocks = "\n".join(f"<{k}>{v}</{k}>" for k, v in core.items())
    stats = f"[{len(archive)} passages in archive, not shown]"
    return f"{blocks}\n{stats}\n" + "\n".join(trajectory)

# What a model would choose to do across two Mondays, scripted.
print(core_append("supplier", "Acme delivers itemB."))
print(core_append("supplier", "On 3 March Acme said lead time rose to 4 weeks after a port strike."))
print(archive_insert("3 March: Acme lead time for itemB rose to 4 weeks, port strike."))
print(core_append("supplier", "See archive: lead time."))

print("\n--- next Monday, new session ---")
print(compile_context(["user: Should we reorder itemB?"]))
print("\nsearch 'lead time' ->", archive_search("lead time"))
print("search 'delay'     ->", archive_search("delay"))
```

```text
ok
Error: core is full (limit 100). Move detail to the archive.
ok, 1 passages in archive
ok

--- next Monday, new session ---
<policy>Order just in time. Keep two weeks of peak sales.</policy>
<supplier>Acme delivers itemB. See archive: lead time.</supplier>
[1 passages in archive, not shown]
user: Should we reorder itemB?

search 'lead time' -> ['3 March: Acme lead time for itemB rose to 4 weeks, port strike.']
search 'delay'     -> no match
```

Read the output from the model's side. The second `core_append` is refused, and the error tells the model what to do next, so the size limit becomes a behavior rather than a crash. The archive's contents never appear in the compiled context, only a count, which is how the model knows there is something worth searching for. And the last line shows the weak point: the fact is stored, but the query "delay" misses it, because this search is literal. A real archive uses embeddings for that reason. Even so, the agent has to decide to search at all, and that is the failure the [stale-memory pitfall](#pitfalls) describes.

---

## The Letta API

Letta is the MemGPT authors' server. The course pins `letta==0.6.50` and runs the server at `http://localhost:8283`. Agents are persistent server objects, not Python objects in your process.

**Create an agent with memory blocks (Lab 3):**

```python
# illustrative: needs `letta==0.6.50`, a Letta server on localhost:8283 and an OpenAI key
from letta_client import Letta
client = Letta(base_url="http://localhost:8283")

agent_state = client.agents.create(
    name="simple_agent",
    memory_blocks=[
        {"label": "human",   "value": "My name is Charles", "limit": 10000},
        {"label": "persona", "value": "You are a helpful assistant and you always use emojis"},
    ],
    model="openai/gpt-4o-mini-2024-07-18",
    embedding="openai/text-embedding-3-small",
)

response = client.agents.messages.create(
    agent_id=agent_state.id,
    messages=[{"role": "user", "content": "my name actually Sarah"}],
)
# the agent calls core_memory_replace; the block now says Sarah
client.agents.blocks.retrieve(agent_id=agent_state.id, block_label="human").value
```

**Archival memory directly (Lab 3):** `client.agents.passages.list(agent_id=...)` reads it and `client.agents.passages.create(agent_id=..., text="Bob loves boston terriers")` writes to it from outside the agent.

**Custom memory tools (Lab 4).** A tool that takes `agent_state: "AgentState"` gets the calling agent injected, so it can edit that agent's blocks. The lab builds a task queue in a core-memory block:

```python
# illustrative: needs a Letta server, an OpenAI key, `client`, `pop_tool` and the lab's system prompt file
def task_queue_push(agent_state: "AgentState", task_description: str):
    """Push to a task queue stored in core memory.

    Args:
        task_description (str): A description of the next task you must accomplish.
    """
    from letta_client import Letta          # tools run server-side: import inside
    import json
    client = Letta(base_url="http://localhost:8283")
    block = client.agents.blocks.retrieve(agent_id=agent_state.id, block_label="tasks")
    tasks = json.loads(block.value) + [task_description]
    client.agents.blocks.modify(agent_id=agent_state.id, block_label="tasks",
                                value=json.dumps(tasks))

push_tool = client.tools.upsert_from_function(func=task_queue_push)

task_agent = client.agents.create(
    system=open("task_queue_system_prompt.txt").read(),
    memory_blocks=[{"label": "tasks", "value": "[]"}],
    model="openai/gpt-4o-mini-2024-07-18",
    embedding="openai/text-embedding-3-small",
    tool_ids=[pop_tool.id, push_tool.id],
    include_base_tools=False,               # drop the default memory tools
    tools=["send_message"],
)
```

The docstring is the tool description: Letta builds the JSON schema from the signature and the `Args:` section.

**Agentic RAG over a document (Lab 5).** A *source* is a document collection; attaching it copies its passages into the agent's archival memory, where `archival_memory_search` finds them. The course uses an employee handbook, kept here as [packer-wooders-agent-memory-handbook.pdf](../sources/packer-wooders-agent-memory-handbook.pdf).

```python
# illustrative: needs a Letta server, an OpenAI key, `agent_state`, and a `handbook.pdf`
source = client.sources.create(name="employee_handbook",
                               embedding="openai/text-embedding-3-small")
job = client.sources.files.upload(source_id=source.id, file=open("handbook.pdf", "rb"))
while job.status != "completed":            # chunking and embedding run as a job
    job = client.jobs.retrieve(job.id); time.sleep(1)

client.agents.sources.attach(agent_id=agent_state.id, source_id=source.id)
# "Search archival for our company's vacation policies" -> archival_memory_search
```

This is agentic RAG: the agent decides whether to retrieve, what query to send and whether to search again. Compare the fixed retrieve-then-generate pipeline in [02-rag-retrieval](../../02-rag-retrieval/README.md). The lab also shows a plain tool (`query_birthday_db`) as the other route to external data.

---

## Memory types in other frameworks

Lakshmanan and Hapke (*Generative AI Design Patterns*, ch. 8, Pattern 28) and LangMem use a cognitive-science vocabulary. It maps onto MemGPT's stores like this:

| P28 type | Meaning | MemGPT/Letta | LangMem / Mem0 |
|---|---|---|---|
| Working | current session messages, trimmed to fit | chat history + summary | message list in graph state |
| Episodic | past interactions, searchable with metadata | recall memory | `Episode` schema; Mem0 `run_id` |
| Procedural | instructions, user profile, how to behave | persona block, system prompt | `create_prompt_optimizer` rewrites the prompt |
| Semantic | facts extracted from conversations | human block, archival memory | `create_memory_manager` with schemas; Mem0 graph + vectors |

The book's working-memory rule: trim to the token limit but keep the system prompt, and keep the trimmed list valid (never drop a tool call while keeping its result). Mem0's `memory.add(messages, user_id=...)` uses an LLM to extract facts, resolve contradictions with what is stored, and drop small talk and general knowledge; `memory.search(query, user_id=...)` returns ranked memories across types. The book's Mem0 example configures ChromaDB as the vector store, gpt-4o-mini at temperature 0.1 for extraction and text-embedding-3-small (1,536 dimensions) for embeddings, and recommends writing memories in a background thread and running Mem0 as a microservice. Its design advice, to prefer semantic over episodic memory because retrieving raw messages adds latency and cache-miss errors are hard to debug, is covered in [context engineering 06](../../../ai-engineering/02-context-engineering/notes/06-memory.md#memory-types) (*Generative AI Design Patterns*, ch. 8, Pattern 28).

"Trimmed to fit" covers four strategies. LangChain's legacy memory classes, as Phoenix and Taylor present them, give each one a name (*Prompt Engineering for Generative AI*, ch. 6):

| Strategy | Legacy class | Keeps | Trade-off |
|---|---|---|---|
| Full buffer | `ConversationBufferMemory` | Every message | No limit, so it eventually overflows the window |
| Last-k window | `ConversationBufferWindowMemory` | The last k exchanges | Silently forgets anything older than k |
| Token buffer | `ConversationTokenBufferMemory` | Recent messages up to a token limit | Predictable size; same blind spot as the window |
| Running summary | `ConversationSummaryMemory` | An LLM-written summary | Costs a model call per update; summaries lose detail |
| Summary + buffer | `ConversationSummaryBufferMemory` | Recent messages verbatim; older ones folded into a summary once a token limit is passed | The usual default: recency kept exactly, history kept roughly |

By default these live in process memory and disappear with the session; persistence needs a database-backed history. The classes are deprecated: current LangChain keeps the message list in LangGraph state with a checkpointer and trims or summarizes it in a node. The strategies are unchanged. In MemGPT terms, the summary-plus-buffer row is the recursive summary plus recent chat history from the context-compilation table above. MemGPT adds what these classes lack: the evicted messages stay searchable in recall memory.

The Mem0 paper ([arXiv:2504.19413](https://arxiv.org/abs/2504.19413), Chhikara et al., 2025-04) shows what extraction costs. On LOCOMO's long multi-session conversations, graded by an LLM judge, Mem0 scored 66.9% and the graph variant 68.4%. Passing the whole 26k-token conversation scored **72.9%**. Memory wins on cost: about 1.8k tokens per query instead of 26k, and p95 latency of 1.4 s instead of 17 s. Mem0 also beat its other memory baselines: OpenAI's memory at 52.9%, LangMem at 58.1%, and Zep at 66.0% (Zep also took hours to make new memories searchable). When the history still fits in the window and latency doesn't matter, full context is the more accurate baseline.

The retrieval score most of these systems descend from is from *Generative Agents* ([arXiv:2304.03442](https://arxiv.org/abs/2304.03442), Park et al., 2023-04). It ran 25 simulated characters, each with a **memory stream** of timestamped observations. Each memory gets three scores, each min-max scaled to [0, 1]:

- recency: exponential decay, factor 0.995 per game hour since the memory was last *retrieved*
- importance: the LLM rates the memory 1–10 when it is stored, e.g. 2 for "cleaning up the room" and 8 for "asking your crush out"
- relevance: cosine similarity to the current query ([dot product and cosine](../../01-llm-fundamentals/notes/01-tokens-and-embeddings.md#vectors-dot-products-and-cosine-similarity))

The three are summed with equal weight. **Reflection** runs when the importance of recent events adds up past 150, which works out to two or three times a game day. It writes higher-level conclusions back into the stream as memories. In a believability ranking (TrueSkill), the full architecture scored μ = 29.9, without reflection 26.9, and without memory, reflection or planning 21.2. Human crowdworkers role-playing the agents scored 23.0. Memory errors persisted: agents missed facts they had observed, retrieved fragments, and embellished details.

MemOS ([arXiv:2505.22101](https://arxiv.org/abs/2505.22101), Li et al., 2025-05) takes the OS analogy further than MemGPT. Its taxonomy is by where memory lives rather than what it is about: **parametric** (the weights), **activation** (the KV cache and hidden states), and **plaintext** (retrievable documents, which is everything in the table above). It also defines paths for moving memory between them, such as caching hot plaintext as KV or distilling stable knowledge into weights. Every unit is a **MemCube**: a payload plus a metadata header that records provenance, a time-to-live or decay policy, access control, version lineage and access frequency. That header is the governance layer most frameworks leave out, but MemOS is an architecture paper with no experiments, so treat it as a checklist of fields to store, not as evidence that the design works.

The LangGraph + LangMem course version, with semantic, episodic and procedural memory in an email assistant, is [04-agentic-frameworks 03](../../04-agentic-frameworks/notes/03-long-term-memory-with-langgraph.md).

LangMem's procedural memory is the one idea MemGPT does not have: a prompt optimizer that rewrites the agent's own instructions from feedback.

```python
# illustrative: needs `langmem` and an API key for the named model; the model ID is from the course
from langmem import create_prompt_optimizer

optimizer = create_prompt_optimizer(
    "anthropic:claude-3-5-sonnet-latest",
    kind="metaprompt",
    config={"max_reflection_steps": 3},
)
conversation = [
    {"role": "user", "content": "Explain inheritance in Python."},
    {"role": "assistant", "content": "Inheritance allows classes to inherit features from other classes."},
    {"role": "user", "content": "Can you give me a concrete code example?"},
]
feedback = {"user_score": 0.3, "feedback": "Too vague, no practical detail."}

better_prompt = optimizer.invoke({
    "trajectories": [(conversation, feedback)],   # (messages, feedback) pairs
    "prompt": "You are a helpful assistant.",
})
```

RAISE ([arXiv:2401.02777](https://arxiv.org/abs/2401.02777) (Liu et al., 2024-01, preprint)) is a small worked case of prompt-assembled memory rather than paging. It extends ReAct with a scratchpad (dialogue-level, short-term) and retrieved examples (turn-level, long-term). In the fine-tuned Qwen-14B-Chat block, quality rose step by step as each was added: ReAct 7.52, plus scratchpad 7.61, plus examples 7.66, RAISE 7.71 (100 held-out real-estate chat scenes, human-scored, 848 training scenes). Under GPT-4 prompting RAISE (7.69) did not beat ReAct plus examples (7.72), so the memory gain is small and shows mainly after fine-tuning; one in-house dataset, no significance test, and no long-conversation test.

---

## Shared memory across agents

Blocks are database rows, so two agents can attach the same block. Lab 6 gives an evaluator agent and an outreach agent a shared `company` block; when one agent learns "the company has rebranded to Letta" and edits the block, the other sees the change on its next step.

![Blocks shared across agents](../sources/images/packer-wooders-agent-memory-fig7.png)

*Figure: shared blocks (Letta course, L4).*

The multi-agent side of Lab 6 is in [04 — multi-agent design patterns](04c-planning-architectures-and-failure.md#letta-agents-as-services-with-shared-memory).

---

## Designing a memory agent

From the course conclusion, the four things you control:

| Lever | Question |
|---|---|
| Prompts | What does the system prompt say about when to save and search? |
| Tools | Which memory tools exist, and do any have side effects outside memory? |
| Memory management | Block sizes, eviction policy, what gets summarized |
| Memory content | Initial persona and human blocks, preloaded archival documents |

How much should the memory agent curate? A controlled comparison of filesystem memory stores ([arXiv:2607.26637](https://arxiv.org/abs/2607.26637), Zhou et al., 2026-07) says less than you'd think. With gpt-5.4-mini building and searching the store, a verbatim dump of the conversations or one file per session matched or beat an agent-curated store on all four conversational benchmarks; on PersonaMem at 32k tokens, curation scored 37.5% against 78.1% for the dump, because the curator left superseded preferences standing as current (the right fact was still in the store for all 13 misses). Asking the agent to reorganize a store silently condensed it unless told to keep every fact: on REALTALK, a condensing reorganization dropped correctness from 77.6% to 41.2%, while a fact-preserving one held at 77.6%. Two budget rules follow. Spend model strength on the reader, not the writer: a stronger searcher raised mean correctness from about 62% (gpt-5.4-nano) to 79% (gpt-5.4), while a stronger builder "buys a more elaborate store, not a more useful one." And match stored experience to the executor: on ALFWorld, raw episode logs helped a gpt-4.1 executor most (87.1% vs. 73.6% with no store), but a gpt-4.1-mini executor did better with distilled task guidance (76.4% vs. 66.4% with logs). The study uses single build runs and 32–158 questions per benchmark tier, so read differences of a few points as ties.

The safe kind of curation edits the index, not the facts. A-MEM ([arXiv:2502.12110](https://arxiv.org/abs/2502.12110) (Xu et al., NeurIPS 2025)) stores each interaction as a Zettelkasten-style note: the raw content plus LLM-written keywords, tags and a one-line context, linked to related notes. When a new note arrives, the agent may rewrite its neighbours' keywords, tags and context, but never their content. On LoCoMo with GPT-4o-mini, scored by token F1, removing the linking and rewriting steps cut multi-hop F1 from 27.0 to 9.7. Against the whole conversation in context, the result looks like Mem0's. With GPT-4o, A-MEM won on temporal questions (39.4 vs. 9.1 F1) using about 1.2k tokens per question instead of 16.9k. It lost on single-hop questions (48.4 vs. 61.6) and on adversarial ones (36.4 vs. 52.6).

The verbatim result assumes there is a verbatim record to keep. For a video or audio stream there isn't one, so the writer has to extract something. M3-Agent ([arXiv:2508.09736](https://arxiv.org/abs/2508.09736) (Long et al., 2025-08, preprint)) turns each 30-second clip into episodic memory (what happened) and semantic memory (what it implies, such as "Alice likes coffee in the morning"), keyed to face and voice identities. With the reader held fixed, **dropping the semantic memories cut VideoMME-long accuracy from 61.8% to 48.7%**, and dropping the face–voice identity links cut it to 52.1%. On the authors' robot-view benchmark, dropping semantic memory cut accuracy from 30.7% to 13.6%. Here the writer mattered too. A Qwen2.5-Omni-7B fine-tuned to write memories beat prompted Gemini-1.5-Pro in the same role (61.8% vs. 52.7% on VideoMME-long), so the "spend on the reader" rule applies to text conversations, where the raw record can be stored as it is.

Memory of *how to do a task* raises the same choice between keeping the trajectory and keeping a distilled routine. Agent Workflow Memory ([arXiv:2409.07429](https://arxiv.org/abs/2409.07429) (Wang et al., ICML 2025)) turns successful trajectories into reusable workflows and adds them to the prompt. Example-specific values become placeholders such as `{product-name}`. In the online setting it learns from its own test-time runs, keeping those an LLM evaluator judges successful. With GPT-4 on WebArena, success rose from 15.0% (BrowserGym with the same accessibility-tree input) to 35.5%. The paper's own ablation agrees with Zhou et al., though. **Deduplicated raw trajectories did as well as LM-abstracted workflows on WebArena (35.6% vs. 35.5%)**, and on Mind2Web abstraction added 1.7 points of step success (43.4% to 45.1%). Wrapping workflows as callable tools changed little, because the agent called them in only 18.5% of tasks.

Retrieval is the other half. When stored experiences look alike, similarity is a poor proxy for usefulness. MemRL ([arXiv:2601.03192](https://arxiv.org/abs/2601.03192) (Zhang et al., 2026-01, preprint)) gives each stored experience a utility score. Each time the experience is used, task reward updates the score with a Monte Carlo rule, Q ← Q + α(r − Q). Candidates are first recalled by similarity, then re-ranked by an equal mix of similarity and utility. This is Generative Agents' importance score learned from outcomes instead of rated once at write time, and the idea goes back to episodic control in RL (Pritzel et al., ICML 2017). The model stays frozen. With GPT-4o-mini on Lifelong Agent Bench OS tasks, MemRL reached 78.8% success after 10 epochs, against 69.0% for similarity-only RAG and 73.6% for MemP. With GPT-5-mini on ALFWorld it reached 94.9%, against 88.7% for RAG. It needs a reward for every task, and the gain needs tasks that resemble each other. On HLE, where questions share little, cross-task retrieval tied reflecting on the same task alone (60.6% vs. 61.0%).

Memento ([arXiv:2508.16153](https://arxiv.org/abs/2508.16153) (Zhou et al., 2025-08, preprint)) is the same idea with a trained scorer: a frozen LLM planner (GPT-4.1) reads from a bank of (state, action, reward) cases, written once per finished task, successes and failures alike. Retrieval is by embedding similarity, or by a two-layer MLP trained as a success classifier. On DeepResearcher data over five passes, accuracy ended at 85.44 with the learned retriever, 84.85 with similarity and 84.47 with no case memory, so the retriever matters less than having cases at all (no seeds reported). Retrieving 4 cases was best (64.5 F1 across seven datasets, against 59.9 with none and 63.9 with 32), which the authors put down to noise from irrelevant cases.

Agent S ([arXiv:2410.08164](https://arxiv.org/abs/2410.08164) (Agashe et al., 2024-10, preprint)) splits experience by who uses it. A planner reads *narrative* memory, abstract summaries of whole tasks with the actions removed, and the executor reads *episodic* memory, grounded plans for subtasks that succeeded, both written by a self-evaluator without ground truth. On a 65-task subset of OSWorld with GPT-4o, the full system scored 26.15%; removing episodic memory gave 18.46, narrative memory 21.41, web knowledge 16.80 and all three 13.85. Storing full trajectories instead of evaluated summaries gave 18.46, and skipping the self-supervised exploration that seeds the memory gave 15.38. On all 369 OSWorld tasks it reached 20.58% against 11.21% for the best GPT-4o baseline. With 65 tasks, single-point gaps are noisy, and the exploration tasks come from the same environments as the test.

MemInsight ([arXiv:2503.21760](https://arxiv.org/abs/2503.21760) (Salama et al., 2025-03, preprint)) puts the structure in an annotation layer instead of the store. A zero-shot LLM mines attributes and values for each memory (turn-level or session-level) and, in its *priority* mode, orders them by relevance. The query is annotated the same way, and retrieval matches attributes or embeds the annotations. On LoCoMo question answering, with embedding retrieval at k=5 and Claude-3-Sonnet as annotator, **recall@5 was 60.5 overall against 26.5 for a DPR baseline**, and priority beat unordered annotation (48.8). The gain does not carry through to answers: F1 was 30.1 against 28.7 for DPR, and DPR won the adversarial questions (89.9 vs 75.3). On movie recommendation (LLM-REDIAL, 200 conversations) attribute filtering retrieved about 90% less memory than the baseline at comparable recall, and recall and NDCG did not improve. The authors name no cost or latency of annotating, run a single time, and compare against none of MemGPT, Mem0 or A-Mem. Annotation quality depends on the annotating model: they report 99.14% of Claude-3-Sonnet annotations grounded in the dialogue, with visible hallucinated attributes from Llama and Mistral.

ChatDB ([arXiv:2306.03901](https://arxiv.org/abs/2306.03901) (Hu et al., 2023-06, preprint)) goes further and makes the store symbolic: an LLM controller turns a request into a chain of SQL operations (insert, update, delete, select) on a database, rewriting later steps from earlier results, so state is current and arithmetic is done by the database. On a synthetic shop dataset (70 records, about 3.3k tokens, 50 questions) with GPT-3.5 Turbo at temperature 0, **ChatDB answered 41 of 50 (82%) against 11 of 50 (22%)** for the same model with the records in its prompt; on the 35 hard questions the gap was 28 against 1. It is one run on one synthetic set, the baseline is full-context prompting rather than RAG or MemGPT, and the claim that vector memory fails on multi-hop questions is argued, not measured.

JARVIS-1 ([arXiv:2311.05997](https://arxiv.org/abs/2311.05997) (Wang et al., 2023-11, preprint)) shows the lifelong version in Minecraft. Memory is a key-value store of tasks and observations mapped to plans that worked, and only successes are kept. An LLM first generates the sub-goals to look up, then candidates are ranked by visual similarity to the current state. Against DEPS, a memory-less planner baseline, the diamond-task group averaged 8.99% against 2.42%, with 2 to 3 re-planning rounds instead of more than 6. It had gathered 425 successful trajectories over four epochs, with no weight updates. The memory is filled on the same task pool it is tested on, never evicts, and the game was run in an easier mode (peaceful, permanent daytime), so the transfer claim is partly overlap.

The memory manager can also be a small model trained for the job. mem-agent from Dria ([mem-agent](https://github.com/firstbatchxyz/mem-agent/blob/main/main.pdf) (Tekparmak & Kaya, 2025-10)) trained Qwen3-4B-Thinking with GSPO to retrieve, update and ask for clarification over an Obsidian-style folder of markdown files, using Python file tools. On the authors' 56-sample md-memory-bench, scored by an LLM judge, the overall score rose from 0.39 to 0.75. That put it second of 11 models, behind Qwen3-235B-Thinking at 0.79 and ahead of GPT-5 at 0.63 and Claude Opus 4.1 at 0.55. The engineering lessons travel better than the leaderboard:
- **Format rewards get farmed.** Paying per well-formed turn taught the model to use all 8 turns. The fix was rewards that shrink each turn until halfway, then turn negative, plus double the reward for success.
- **Diffs are hard for small models.** A diff-based update tool failed, and they switched to `update_file(path, old_content, new_content)`.
- **Quantization costs judgment first.** The 4- and 8-bit builds sometimes invent facts instead of asking the user for clarification.

The benchmark is small and handmade, and the training data is synthetic from the same team, so treat 0.75 as an existence proof, not a ranking.

Two larger studies make the same point: tools let the agent manage memory, but they don't teach it when to. AgeMem ([arXiv:2601.01885](https://arxiv.org/abs/2601.01885) (Yu et al., 2026-01, preprint)) gives the agent MemGPT-style tools for both tiers: add, update and delete for the long-term store, and retrieve, summarize and filter for the context. It trains them with GRPO on HotpotQA only. When Qwen2.5-7B-Instruct was only prompted to use these tools, it never updated or deleted a memory (0.00 calls per episode). It averaged 33.4% across ALFWorld, SciWorld, PDDL, BabyAI and HotpotQA, against 28.1% with no memory and 37.1% with Mem0. **After RL it averaged 42.0%**, and Qwen3-4B went from 45.6% to 54.3%. The context tools saved only 3–5% of prompt tokens over plain RAG. M3-Agent's controller makes the same point for search. After RL, its 32B controller, which searches memory for up to five rounds, scored 61.8% on VideoMME-long, against 52.5% for the same model prompted. This is MemGPT's weak-function-calling limit again: a memory design works only as well as the model's tool use.

Three 2026 preprints attack the same problem from the structure, the control plane and the design process. All three are LoCoMo-style or game-world results from the authors' own reruns, with no variance reported for xMemory and Jev-Mem (ALMA reports standard error over three deployment runs).

- **Structure: split before you summarize.** xMemory ([arXiv:2602.02007](https://arxiv.org/abs/2602.02007) (Hu et al., 2026-02, preprint)) keeps four levels (messages, segments, extracted memory components, groups of components) and retrieves top-down, adding finer levels only while they lower the reader's answer uncertainty. Groups are split and merged as new components arrive. On LoCoMo with Qwen3-8B (greedy decoding, same model builds and answers), it scored **34.48 BLEU / 43.98 F1 at 4,711 tokens per query, against 31.44 / 40.88 at 7,755 for Nemori** and 27.95 / 36.48 at 8,633 for top-20 chunk RAG. Freezing the structure (no split, no merge) cut F1 to 38.59, and compressing the RAG chunks with LLMLingua-2 lowered F1 to 34.58 from 36.48. Construction is not free: 421.9k tokens against Nemori's 381.3k, so the saving is at query time, and the authors note that with few queries after construction a simpler retriever may be preferable. Tested on LoCoMo and PerLTQA only, at about 18k to 25k tokens of context, with answers capped at a few words.
- **Control: keep the model off the hot path.** Jev-Mem ([arXiv:2609.23986](https://arxiv.org/abs/2609.23986) (Jiang et al., 2026-09, preprint)) lets a small typed-output controller do the frequent bounded decisions (typing a new memory, scoring candidate links, routing a query, deciding when evidence is sufficient) and calls the LLM only to write the answer. On LoCoMo with gpt-4o-mini as the answerer and an LLM judge, it scored 0.777 against 0.700 for the best baseline (MAGMA), built memory in 158 s against 1,044 s for the fastest rival (Nemori), and answered in 0.93 s per query against 1.47 s. There is no ablation of controller against LLM control, the controller is a vendor product (TypeSafe AI's Jev), the run is single, and the authors share a first author with the strongest baseline, so the speed numbers show a configuration, not the principle.
- **Process: let the agent design the memory.** ALMA ([arXiv:2602.07755](https://arxiv.org/abs/2602.07755) (Xiong et al., 2026-02, preprint)) has a meta-agent write memory designs as code (update, storage and retrieval), score them on a learning set, and keep an archive it samples parents from. With a GPT-5-nano agent on four game-world benchmarks (ALFWorld, TextWorld, Baba Is AI, MiniHack), learned designs averaged **12.3% against 6.1% with no memory and 8.6% for the best of four hand-built designs**; moved unchanged to a GPT-5-mini agent they averaged 53.9% against 41.1% and 48.6%. Some hand-built designs hurt: on TextWorld, trajectory retrieval fell from 5.4% to 2.7%. On ALFWorld, archive sampling beat always expanding the best design (87.1% against 77.1% with GPT-5-mini). Designs are learned offline on a fixed set of tasks, three deployment runs, OpenAI models only, and none of the benchmarks is conversational memory.

Memex(RL) ([arXiv:2603.04257](https://arxiv.org/abs/2603.04257) (Wang et al., 2026-03, preprint)) makes the write and read decisions learned. `CompressExperience` replaces the working context with a short summary holding an index map and archives the full text under those indices in a key-value store, and `ReadExperience(index)` restores exactly that span, an exact lookup rather than a similarity match. Trained with GRPO on task reward minus penalties for context overflow, redundant calls and malformed calls, a Qwen3-30B-A3B-Thinking agent went from **24.22% to 85.61% success** on a modified ALFWorld and from 16,934 to 9,634 tokens of peak working context, still above the 8,000-token penalty threshold. Compress calls fell from about 6.5 to 3 per episode and reads rose from about 1 to 6 or 7. The comparison is the same agent before and after RL, with no other memory system as baseline; the environment was changed to force reads (one `look` per episode, summaries capped at 300 tokens), and it is one model with no seeds.

Xu et al. ([arXiv:2604.27707](https://arxiv.org/abs/2604.27707) (2026-04, position paper)) argue that MemGPT-style stores, RAG and Reflexion change only the context, never the model, so competence disappears when the stored trace is not supplied: a memo, not learning. Their theorem is conditional. If a frozen model stays below the target accuracy on held-out combinations of k concepts, retrieval needs on the order of k² stored examples where a parametric learner of complexity d needs about d. It is shown on modular arithmetic as an existence proof, and the authors say they provide no compute-matched frontier-model experiment. The security point is relayed from other papers: persistent writes carry an injection across sessions (MINJA, 98.2% injection success; PoisonedRAG, 90% with five texts per query). Their proposal keeps scoped, deletable episodic retrieval as the default and adds a separate asynchronous consolidation channel into adapters, with provenance, versioned checkpoints and regression guards.

A benchmark of agent memory systems ([arXiv:2606.24775](https://arxiv.org/abs/2606.24775) (Zhou et al., 2026-06, preprint)) compares a dozen of them with long-context and embedding-RAG baselines on LoCoMo, LongMemEval, DB-Bench and LongBench (GPT-5.4 judges LongMemEval). **No design won everywhere**: Zep led LongMemEval judge accuracy (48.0), MemOS led LoCoMo exact match (11.5) and plain long context led DB-Bench (48.20 EM). Keeping original text beat summarising it (LightMem on LoCoMo, 24.2 EM raw against 8.5 summarised), and heavier write-time extraction hurt (MemOS fine against fast memorize on LoCoMo, 2.5 against 25.5 EM). Letta scored 0.0 EM on LoCoMo. Single runs, no variance, many ablation gaps are a few tenths of a point, and the authors are affiliated with MemOS, one of the systems tested.

---

## Pitfalls

From the course's conclusion, with the fixes that go with them:

| Pitfall | Fix |
|---|---|
| Agent never saves | Say so in the system prompt; check the tool description |
| Core memory fills with trivia | Smaller block limits; a rule for what belongs in core vs archival |
| Agent answers from stale core memory | Memory stats in context; instruct it to search before answering |
| Shared block edited by two agents at once | One writer per block, or a tool that serializes writes |

Four more follow from the rest of this chapter:

- **Treating memory as trusted.** Anything saved from a tool result or user message comes back later as if it were context, so an injected instruction can persist across sessions. Mark where each memory came from.
- **Overwriting facts with summaries.** A summary loses detail for good. Keep the verbatim record and curate the index on top of it.
- **Storing what you should look up.** A delivery time held in memory goes stale. Keep the source of truth in a tool, and store what the system of record does not hold, such as why a decision was made.
- **Testing storage and not behavior.** A passing insert test says nothing about whether the agent saves the right things. Replay real conversations and check what it wrote and what it later retrieved.

---

## Try it

1. Run the two-tier block with `CORE_LIMIT = 40`. What does the first `core_append` return, and what does the context look like next Monday?
2. Change `archive_search` to match any word in the query. Does `"lead time delay"` now find the passage? What would it wrongly match in a larger archive?
3. Add a `core_replace(label, old, new)` tool. Why might it suit a small model better than a diff-based edit?
4. Which tier should hold each of these: the agent's ordering policy, a 40-page supplier contract, last Monday's conversation, today's stock level?

<details>
<summary>Answers</summary>

1. The policy alone is 49 characters, so every `core_append` is refused and even the short pointer to the archive is lost. Next Monday, the context shows the policy and a count of one archived passage, with no hint of what it holds. A limit set too low silently costs you the index.
2. Yes, it finds the passage through "lead" and "time". It would also match any passage containing "time", which is why keyword matching needs ranking, and why archives usually use embeddings or hybrid search.
3. It only has to quote the old text and supply the new text. The mem-agent team reports that a diff-based tool failed for their small model and that they moved to a tool of this form.
4. Policy: core. Contract: archival, with retrieval. Last Monday's conversation: recall. Stock level: none of them, since it should come from a tool on each run.

</details>

---

## Interview checklist

| Question | Short answer |
|---|---|
| What is the MemGPT analogy? | Context = RAM, databases = disk, the LLM pages for itself with tools |
| Core vs archival vs recall? | Always in context and small; vector store of facts and documents; full message history |
| What is a heartbeat? | A flag on a tool call asking for another LLM step without user input |
| Why is "every output a tool call" useful? | One uniform loop; replying is just another action the agent chooses |
| What does agentic RAG change? | The agent decides when and what to retrieve, and can retrieve again |
| Why give core memory a hard size limit? | It is always in context, so it costs tokens on every call. An error at the limit makes the agent decide what to keep |
| Should a memory agent summarize what it stores? | Often not: curate the index and keep the facts. Zhou et al. found that verbatim stores hold up well against curated ones |
| Why does the agent not search when it should? | Tools let it manage memory but do not teach it when. Put memory stats in context, instruct it, and test that behavior |

---

## Next

→ [03b — learning from experience](03b-learning-from-experience.md): what to keep from past runs, whether it transfers, and how to tell if the store helps.
