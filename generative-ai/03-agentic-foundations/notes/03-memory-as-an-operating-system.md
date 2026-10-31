---
origin: course-synthesis
sources:
  - "DeepLearning.AI, LLMs as Operating Systems: Agent Memory (Charles Packer, Sarah Wooders), Labs 1–6 and slides — https://www.deeplearning.ai/short-courses/llms-as-operating-systems-agent-memory/ ; snapshot upstream https://github.com/frankwwu/LLMs-as-Operating-Systems--Agent-Memory"
  - "Packer et al. 2023, MemGPT: Towards LLMs as Operating Systems — https://arxiv.org/abs/2310.08560"
  - "Lakshmanan & Hapke, Generative AI Design Patterns (O'Reilly 2025), ch 8 P28 Long-Term Memory — ../sources/lakshmanan-hapke-genai-design-patterns-ch08-addressing-constraints.pdf"
  - "Chhikara et al. 2025, Mem0 — https://arxiv.org/abs/2504.19413"
  - "adv-11/AgenticAIFrameworks: Letta/self-editing memory from scratch, LangGraph/langMem — https://github.com/adv-11/AgenticAIFrameworks"
confidence: high
cleaned: 2026-10-31
---

# 3 — Memory as an operating system

> MemGPT treats the context window as RAM and external stores as disk, and makes the agent its own memory manager: every memory edit, search and eviction is a tool call.

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
agent_memory = {"human": "", "agent": ""}

def core_memory_save(section: str, memory: str):
    agent_memory[section] += "\n" + memory     # the agent edits its own context

# rebuilt on every call: this is context compilation in one line
memory_message = {"role": "system", "content": "[MEMORY]\n" + json.dumps(agent_memory)}
```

The system prompt ends with "When you learn new information, make sure to always call the core_memory_save tool." Without that instruction the model rarely saves anything.

---

## The Letta API

Letta is the MemGPT authors' server. The course pins `letta==0.6.50` and runs the server at `http://localhost:8283`. Agents are persistent server objects, not Python objects in your process.

**Create an agent with memory blocks (Lab 3):**

```python
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

Lakshmanan and Hapke (P28 Long-Term Memory) and LangMem use a cognitive-science vocabulary. It maps onto MemGPT's stores like this:

| P28 type | Meaning | MemGPT/Letta | LangMem / Mem0 |
|---|---|---|---|
| Working | current session messages, trimmed to fit | chat history + summary | message list in graph state |
| Episodic | past interactions, searchable with metadata | recall memory | `Episode` schema; Mem0 `run_id` |
| Procedural | instructions, user profile, how to behave | persona block, system prompt | `create_prompt_optimizer` rewrites the prompt |
| Semantic | facts extracted from conversations | human block, archival memory | `create_memory_manager` with schemas; Mem0 graph + vectors |

The book's working-memory rule: trim to the token limit but keep the system prompt, and keep the trimmed list valid (never drop a tool call while keeping its result). Mem0's `memory.add(messages, user_id=...)` uses an LLM to extract facts, resolve contradictions with what is stored, and drop small talk and general knowledge; `memory.search(query, user_id=...)` returns ranked memories across types.

The LangGraph + LangMem course version, with semantic, episodic and procedural memory in an email assistant, is [04-agentic-frameworks 03](../../04-agentic-frameworks/notes/03-long-term-memory-with-langgraph.md).

LangMem's procedural memory is the one idea MemGPT does not have: a prompt optimizer that rewrites the agent's own instructions from feedback.

```python
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

---

## Shared memory across agents

Blocks are database rows, so two agents can attach the same block. Lab 6 gives an evaluator agent and an outreach agent a shared `company` block; when one agent learns "the company has rebranded to Letta" and edits the block, the other sees the change on its next step.

![Blocks shared across agents](../sources/images/packer-wooders-agent-memory-fig7.png)

*Figure: shared blocks (Letta course, L4).*

The multi-agent side of Lab 6 is in [04 — multi-agent design patterns](04-multi-agent-design-patterns.md#letta-agents-as-services-with-shared-memory).

---

## Designing a memory agent

From the course conclusion, the four things you control:

| Lever | Question |
|---|---|
| Prompts | What does the system prompt say about when to save and search? |
| Tools | Which memory tools exist, and do any have side effects outside memory? |
| Memory management | Block sizes, eviction policy, what gets summarized |
| Memory content | Initial persona and human blocks, preloaded archival documents |

| Pitfall | Fix |
|---|---|
| Agent never saves | Say so in the system prompt; check the tool description |
| Core memory fills with trivia | Smaller block limits; a rule for what belongs in core vs archival |
| Agent answers from stale core memory | Memory stats in context; instruct it to search before answering |
| Shared block edited by two agents at once | One writer per block, or a tool that serializes writes |

---

## Interview questions

| Question | Short answer |
|---|---|
| What is the MemGPT analogy? | Context = RAM, databases = disk, the LLM pages for itself with tools |
| Core vs archival vs recall? | Always in context and small; vector store of facts and documents; full message history |
| What is a heartbeat? | A flag on a tool call asking for another LLM step without user input |
| Why is "every output a tool call" useful? | One uniform loop; replying is just another action the agent chooses |
| What does agentic RAG change? | The agent decides when and what to retrieve, and can retrieve again |

→ Next: [04 — multi-agent design patterns](04-multi-agent-design-patterns.md) — reflection, tool use, planning and collaboration built from conversations between agents.
