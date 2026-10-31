---
origin: Long-Term-Agentic-Memory-With-LangGraph-main
sources:
  - https://github.com/YunghuiHsu/Long-Term-Agentic-Memory-With-LangGraph (Lesson 2–5 notebooks, prompts.py)
  - https://www.deeplearning.ai/short-courses/long-term-agentic-memory-with-langgraph/ (L2 Baseline, L3 Semantic, L4 Episodic, L5 Procedural)
  - https://langchain-ai.github.io/langmem/
  - https://docs.langchain.com/oss/python/langgraph/memory
confidence: high
cleaned: 2026-10-31
---
# 3 — Long-Term Memory with LangGraph

> An email assistant gains three kinds of memory, one lesson at a time: **semantic** (facts about people), **episodic** (labelled past examples used as few-shot), and **procedural** (its own prompts, rewritten from feedback). All three live in one LangGraph store, separated by namespace.

Course: DeepLearning.AI × LangChain, *Long-Term Agentic Memory with LangGraph* (Harrison Chase). Pinned stack: `langgraph==1.2.18`, `langmem==0.0.30`, `langchain==1.3.9`, Python 3.11. The memory taxonomy and design trade-offs are in [ai-engineering/02-context-engineering 06 — memory](../../../ai-engineering/02-context-engineering/notes/06-memory.md); this note is how LangGraph and `langmem` implement it.

---

## The three memory types

| Type | Human analogy | What the agent stores | How it is used | Lesson |
|---|---|---|---|---|
| Semantic | Facts you know | "Jim is my friend", contact details, project facts | Agent calls `search_memory` as a tool | L3 |
| Episodic | Things that happened | Past emails with the correct triage label | Retrieved by similarity, injected as few-shot examples | L4 |
| Procedural | How to do things | The system prompts themselves | Read at the start of each node; rewritten by an optimizer | L5 |

| Short-term (note 02) | Long-term (this note) |
|---|---|
| Checkpointer | Store (`BaseStore`) |
| Scoped to one `thread_id` | Scoped to a namespace tuple, e.g. per user |
| Whole graph state, every step | Explicit `put` / `search` / `get` of JSON items |
| Lost when the thread ends | Survives across threads and sessions |

---

## L2 — the baseline graph

Two nodes: a structured-output triage router and a ReAct response agent.

| Rule bucket | Default contents |
|---|---|
| ignore | Marketing newsletters, spam emails, mass company announcements |
| notify | Team member out sick, build system notifications, project status updates |
| respond | Direct questions from team members, meeting requests, critical bug reports |

```python
# L2 — the router: structured output, so the edge logic never parses prose (needs OPENAI_API_KEY)
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Literal, Annotated
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.types import Command

class Router(BaseModel):
    reasoning: str = Field(description="Step-by-step reasoning behind the classification.")
    classification: Literal["ignore", "respond", "notify"]

llm_router = init_chat_model("openai:gpt-4o-mini").with_structured_output(Router)

class State(TypedDict):
    email_input: dict
    messages: Annotated[list, add_messages]

def triage_router(state: State) -> Command[Literal["response_agent", "__end__"]]:
    result = llm_router.invoke([{"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}])
    if result.classification == "respond":
        return Command(goto="response_agent",
                       update={"messages": [{"role": "user",
                               "content": f"Respond to the email {state['email_input']}"}]})
    return Command(goto=END)      # ignore / notify (notify would alert the user in a real app)
```

`Command(goto=..., update=...)` lets a node choose its successor and write state in one return, instead of a separate conditional-edge function.

```python
# L2 — mock tools and a prebuilt ReAct agent as the second node
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

@tool
def write_email(to: str, subject: str, content: str) -> str:
    """Write and send an email."""
    return f"Email sent to {to} with subject '{subject}'"
# schedule_meeting(attendees, subject, duration_minutes, preferred_day), check_calendar_availability(day)

agent = create_react_agent("openai:gpt-4o", tools=tools, prompt=create_prompt)

email_agent = (StateGraph(State)
               .add_node(triage_router)
               .add_node("response_agent", agent)
               .add_edge(START, "triage_router")
               .compile())
```

The prompts are XML-ish sections (`< Role >`, `< Tools >`, `< Instructions >`, `< Rules >`, `< Few shot examples >`) filled from a `profile` dict (John Doe, senior engineer leading five developers) and the rule buckets above. Lessons 3–5 change what fills those slots.

---

## L3 — semantic memory: a store plus two tools

```python
# L3 — an embedding-indexed store and langmem's memory tools
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool, create_search_memory_tool

store = InMemoryStore(index={"embed": "openai:text-embedding-3-small"})

ns = ("email_assistant", "{langgraph_user_id}", "collection")   # template, filled from config
manage_memory_tool = create_manage_memory_tool(namespace=ns)    # create / update / delete
search_memory_tool = create_search_memory_tool(namespace=ns)    # semantic search

response_agent = create_react_agent(
    "anthropic:claude-3-5-sonnet-latest",
    tools=[write_email, schedule_meeting, check_calendar_availability,
           manage_memory_tool, search_memory_tool],
    prompt=create_prompt,
    store=store,                      # the tools reach the store through the runtime
)
config = {"configurable": {"langgraph_user_id": "lance"}}
response_agent.invoke({"messages": [{"role": "user", "content": "Jim is my friend"}]}, config=config)
response_agent.invoke({"messages": [{"role": "user", "content": "who is jim?"}]}, config=config)
```

```python
# L3 — inspect what the agent chose to remember
store.list_namespaces()                                    # [('email_assistant', 'lance', 'collection')]
store.search(("email_assistant", "lance", "collection"), query="jim")
email_agent = StateGraph(State)...compile(store=store)     # the whole graph shares the store
```

| Design choice | Effect |
|---|---|
| Memory as **tools** | The model decides when to write and search ("hot path"). Cheap to build; writes are only as good as the model's judgement |
| `{langgraph_user_id}` in the namespace | One store, isolated per user; the id comes from the run config, not the prompt |
| Embedding index on the store | `search(query=...)` is semantic, not key lookup |

The payoff demo: a follow-up email ("Any update on my previous ask?") gets a reply that uses what the first email stored.

---

## L4 — episodic memory: labelled examples as few-shot

Instead of editing rules, store *examples* of correct decisions and retrieve the most similar ones into the triage prompt.

```python
# L4 — write an example: the email plus the label the user wants
import uuid
store.put(("email_assistant", "lance", "examples"), str(uuid.uuid4()),
          {"email": email, "label": "ignore"})

template = """Email Subject: {subject}
Email From: {from_email}
Email To: {to_email}
Email Content:
{content}
> Triage Result: {result}"""

def format_few_shot_examples(examples):
    strs = ["Here are some previous examples:"]
    for eg in examples:
        e = eg.value["email"]
        strs.append(template.format(subject=e["subject"], from_email=e["author"],
                                    to_email=e["to"], content=e["email_thread"][:400],
                                    result=eg.value["label"]))
    return "\n\n------------\n\n".join(strs)
```

```python
# L4 — the router now takes config and store, and retrieves examples by similarity
def triage_router(state: State, config, store) -> Command[Literal["response_agent", "__end__"]]:
    namespace = ("email_assistant", config["configurable"]["langgraph_user_id"], "examples")
    examples = store.search(namespace, query=str({"email": state["email_input"]}))
    system_prompt = triage_system_prompt.format(..., examples=format_few_shot_examples(examples))
    ...
```

The triage prompt's last section reads: *"Here are some examples of previous emails, and how they should be handled. Follow these examples more than any instructions above."*

| Run | Result |
|---|---|
| Run as `langgraph_user_id="harrison"`, no matching example | respond |
| Store the same email labelled `ignore`, rerun | ignore |
| Slightly reworded email | still ignore (similarity search) |
| Same email, different `langgraph_user_id` (`"andrew"` instead of `"harrison"`) | respond: the new user has no examples |

Episodic memory changes behaviour without touching the rules, and per-user namespaces keep one user's corrections from leaking to another.

---

## L5 — procedural memory: prompts in the store

The prompts move out of code and into the store, and an optimizer rewrites them from feedback.

```python
# L5 — read each prompt from the store, seeding a default on first use
def triage_router(state, config, store):
    user_id = config["configurable"]["langgraph_user_id"]
    namespace = (user_id,)
    result = store.get(namespace, "triage_ignore")
    if result is None:
        store.put(namespace, "triage_ignore", {"prompt": prompt_instructions["triage_rules"]["ignore"]})
        ignore_prompt = prompt_instructions["triage_rules"]["ignore"]
    else:
        ignore_prompt = result.value["prompt"]
    # ... same for "triage_notify", "triage_respond"; create_prompt() reads "agent_instructions"
```

```python
# L5 — langmem rewrites prompts from a trajectory and a piece of feedback
from langmem import create_multi_prompt_optimizer

conversations = [(response["messages"], "Always sign your emails `John Doe`")]
prompts = [
    {"name": "main_agent", "prompt": store.get(("lance",), "agent_instructions").value["prompt"],
     "update_instructions": "keep the instructions short and to the point",
     "when_to_update": "Update this prompt whenever there is feedback on how the agent should write emails or schedule events"},
    {"name": "triage-ignore", "prompt": ..., "update_instructions": ...,
     "when_to_update": "Update this prompt whenever there is feedback on which emails should be ignored"},
    # triage-notify, triage-respond
]
optimizer = create_multi_prompt_optimizer("anthropic:claude-3-5-sonnet-latest", kind="prompt_memory")
updated = optimizer.invoke({"trajectories": conversations, "prompts": prompts})

for i, p in enumerate(updated):
    if p["prompt"] != prompts[i]["prompt"]:
        key = {"main_agent": "agent_instructions", "triage-ignore": "triage_ignore",
               "triage-notify": "triage_notify", "triage-respond": "triage_respond"}[p["name"]]
        store.put(("lance",), key, {"prompt": p["prompt"]})
# the course notebook uses if/if/else here, so its "else" warning prints even after a valid update
```

| Feedback | Prompt the optimizer changed |
|---|---|
| "Always sign your emails `John Doe`" | `agent_instructions` |
| "Ignore any emails from Alice Jones" | `triage_ignore` |

`when_to_update` is the routing signal: the optimizer only rewrites prompts whose description matches the feedback. `kind="prompt_memory"` is the cheapest optimizer; langmem also has `metaprompt` and `gradient` kinds that reflect more and cost more.

---

## Namespace map

| Namespace | Key | Value | Written by | Read by |
|---|---|---|---|---|
| `("email_assistant", user, "collection")` | uuid | free-text memory | agent via `manage_memory` | agent via `search_memory` |
| `("email_assistant", user, "examples")` | uuid | `{"email": ..., "label": ...}` | the user (feedback UI) | `triage_router` |
| `(user,)` | `agent_instructions`, `triage_ignore`, `triage_notify`, `triage_respond` | `{"prompt": ...}` | seed default, then optimizer | `triage_router`, `create_prompt` |

| Rule | Why |
|---|---|
| Namespace by user from the run config, never from model output | Isolation can't be prompt-injected |
| One writer per namespace | `collection` is the agent's; `examples` and prompts are the user's and optimizer's |
| `InMemoryStore` is for notebooks | Use a persistent store (`PostgresStore`) in anything that restarts |
| Log every procedural update | A rewritten prompt is a deploy; you need diffs and rollback |

---

## Labs

| Lab | Where | Runs |
|---|---|---|
| L2 baseline | [upstream Lesson 2](https://github.com/YunghuiHsu/Long-Term-Agentic-Memory-With-LangGraph) | Needs `OPENAI_API_KEY` |
| L3 semantic, L4 episodic | same repo, Lesson 3–4 folders | Needs `OPENAI_API_KEY` (gpt-4o, embeddings); L3 also `ANTHROPIC_API_KEY` |
| L5 procedural | same repo, Lesson 5 folder | Needs `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` |

---

→ Next: [04-google-adk.md](04-google-adk.md) — the same agent ideas (tools, state, sessions, workflow agents) in Google's framework, and how ADK's eval harness differs.
