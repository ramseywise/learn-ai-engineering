---
origin: internet-search-agent-main
sources:
  - https://github.com/omidreza-amrollahi/internet-search-agent (Omidreza Amrollahi, 2025; MIT)
  - https://docs.langchain.com/langgraph (StateGraph, MessagesState, checkpointers)
confidence: high
cleaned: 2026-10-31
---
# 1 — An internet search agent in LangGraph

> Two small LangGraph graphs behind one FastAPI service. A router decides whether to search. A quick agent answers from three snippets; a workflow agent plans an outline and loops search → draft over its sections, then compiles a cited report.

---

## Where this sits

This is the pillar's first worked project. It is small enough to read in an hour and it uses every primitive from [04-agentic-frameworks](../../04-agentic-frameworks/README.md) and [05-graph 02–04](../../../ai-engineering/05-graph-engineering/README.md): typed state, a conditional edge, a counter loop, structured output and a checkpointer. The local snapshot was removed on 2026-10-31. This note keeps the graphs, the prompts that matter and the review. The code is [upstream](https://github.com/omidreza-amrollahi/internet-search-agent) (MIT).

| Part | File upstream | What it does |
|---|---|---|
| Simple agent | `src/graphs/simple_search_agent.py` | decide → (search) → answer, for chat |
| Workflow agent | `src/graphs/workflow_agent.py` | decide → outline → per-section search/draft loop → compile |
| Clients | `src/clients/llm_client.py`, `search_client.py` | Azure OpenAI at `temperature=0`; Bing via `langchain_community`, `num_results=3` |
| Persistence | `src/persistence.py` | `AsyncSqliteSaver` if `SQLITE_DB_LOCAL_PATH` is set; Postgres is a `NotImplementedError` stub |
| API | `src/main.py`, `src/routes/` | `/api/v1/chat`, `/chat/wait`, `/history`, `/state_history`, `/threads`, `/info`, `/health` |
| Studio | `langgraph.json` | Registers both graphs for `langgraph dev` |

The domain is fixed by prompt: a *sustainability* research assistant that politely declines anything else.

---

## Design choice: a router node, not a search tool

The usual LangGraph search agent binds a `search` tool and lets the model call it inside a ReAct loop ([03-agentic-foundations 02](../../03-agentic-foundations/notes/02-tool-use-and-react.md)). This project splits that into two nodes on purpose. The author's comment in `decide_search` gives the reason: a separate node can write the search query with its own prompt, while a tool forces the query-writing instructions into the main prompt.

| | Tool-calling agent | Router + search node (this project) |
|---|---|---|
| Who decides to search | The model, mid-turn | A classifier node with a one-field schema |
| Who writes the query | The model, as tool arguments | A dedicated LLM call with its own system prompt |
| Number of searches | 0..n, model-chosen | 0 or 1 (simple), 1 + ≤2 retries per section (workflow) |
| Debuggability | One long trace | One node per step; state is inspectable per node |
| Cost | Fewer calls when no search | Always one extra classifier call |

Pick the router when you want a fixed, auditable path. Pick tools when the number of searches should depend on what comes back. This is the "spend agency per node" rule from [05-graph 02](../../../ai-engineering/05-graph-engineering/notes/02-graph-primitives.md).

---

## The simple agent

```
START → decide_search ──should_search──▶ run_search ─▶ generate_answer → END
                     └──────── else ────────────────▶ generate_answer
```

```python
from langgraph.graph import MessagesState, StateGraph, START, END
from pydantic import BaseModel, Field

class SearchDecision(BaseModel):
    """Structured output for the decision LLM."""
    should_search: bool = Field(description="True if the agent should perform a web search for this query.")

class CustomState(MessagesState):           # messages: list with the add_messages reducer
    should_search: bool                      # router decision
    search_results: list[BingSearchResult]   # written by run_search, cleared by generate_answer

def decide_search(state):
    # A one-field schema makes the router's output impossible to misparse
    structured_llm = llm.with_structured_output(SearchDecision)
    d = structured_llm.invoke([
        SystemMessage(content="You are a classifier that must decide whether the user's question requires a live web search."),
        HumanMessage(content=f"Conversation history: {state['messages']}"),
    ])
    return {"should_search": d.should_search}

def run_search(state):
    # Separate LLM call to turn the conversation into a search-engine query
    q = llm.invoke([SystemMessage(content="You are a search assistant. Formulate a search query for Bing based on the conversation history."),
                    HumanMessage(content=f"Conversation history: {state['messages']}")])
    results = json.loads(bing_search.invoke(q.content).replace("'", '"'))   # see review: brittle
    return {"search_results": [
        BingSearchResult(body=r.get("snippet", ""), href=r.get("link", ""),
                         title=r.get("name", ""), index=i + 1)          # 1-based index for citations
        for i, r in enumerate(results)]}

builder = StateGraph(CustomState)
builder.add_node("decide_search", decide_search)
builder.add_node("run_search", run_search)
builder.add_node("generate_answer", generate_answer)
builder.add_edge(START, "decide_search")
builder.add_conditional_edges("decide_search",
    lambda s: "run_search" if s["should_search"] else "generate_answer",
    ["run_search", "generate_answer"])
builder.add_edge("run_search", "generate_answer")
builder.add_edge("generate_answer", END)
graph = builder.compile()        # the checkpointer is attached later, in FastAPI's lifespan
```

`generate_answer` puts the results into the system prompt as JSON and asks for inline URL citations. Then it **clears `search_results`** so the next turn on the same thread starts clean. The prompt does three jobs: scope (sustainability only), refusal style (two few-shot refusals) and citation format.

```text
When answering using the search results, cite the claims that require a citation
with [href] at the end of the claim. For example:
"According to the search results, the sky is blue [https://example.com]."
```

---

## The workflow agent: plan, then loop over sections

```
START → decide_search ─▶ plan_outline ─▶ search_section ─▶ draft_section ─┬─ more? ─▶ advance_index ─┐
              │                              ▲                            │                         │
              │                              └────────────────────────────┼─────────────────────────┘
              │                                                           └─ done ─▶ compile_report → END
              └──── no search ─▶ generate_answer → END
```

```python
class WorkflowState(MessagesState):
    outline: list[str]          # section titles from plan_outline
    current_idx: int = 0        # loop counter
    search_results: list[BingSearchResult]
    section_drafts: list[str]   # appended by draft_section; no reducer, so the node concatenates
    should_search: bool

class OutlinePlan(BaseModel):
    outline: list[str] = Field(description="A list of section titles for the report outline.")

def plan_outline(state):
    topic = state["messages"][-1].content
    plan = llm.with_structured_output(OutlinePlan).invoke(
        "You are a senior sustainability analyst. "
        f"Write a 3 bullet point high-level outline for an in-depth report on:\n«{topic}»\n"
        "Return ONLY a JSON array of section titles.")
    return {"outline": plan.outline, "current_idx": 0}

def search_section(state):
    title = state["outline"][state["current_idx"]]
    q = llm.invoke([SystemMessage(content=f"... The search query must be focused on {title}."), ...])
    results = ast.literal_eval(bing_search.invoke(q.content))
    retries = 0
    while retries < 2 and not results:           # query-reformulation retry, max 2
        q = llm.invoke([SystemMessage(content=f"The previous search query for '{title}' returned no good results. "
                                              "Create a more specific and detailed search query ..."),
                        HumanMessage(content=f"Previous failed query: {q.content}\nSection title: {title}")])
        results = ast.literal_eval(bing_search.invoke(q.content))
        retries += 1
    if not results:                              # degrade explicitly, don't fail the run
        return {"search_results": [BingSearchResult(body="No search results found after retry", href="",
                    title="No Results", index=1,
                    content="No content could be found for this section. The section will be drafted using general knowledge.")]}
    return {"search_results": _sync_crawl_urls(results)}   # crawl4ai /md for each URL → full page markdown

def should_continue(state):
    return "continue" if state["current_idx"] + 1 < len(state["outline"]) else "finish"

builder.add_conditional_edges("draft_section", should_continue,
                              {"continue": "advance_index", "finish": "compile_report"})
builder.add_edge("advance_index", "search_section")    # the loop edge
```

| Node | Prompt contract | Output |
|---|---|---|
| `plan_outline` | 3 section titles, JSON only | `outline`, `current_idx=0` |
| `search_section` | Query focused on the current title; ≤2 reformulations | 3 results, each with crawled `content` |
| `draft_section` | "Write a 200-300 word section… Use ONLY the sources provided below and cite each claim inline with [href]" | one more entry in `section_drafts` |
| `advance_index` | none (pure function) | `current_idx + 1`, clear `search_results` |
| `compile_report` | "Write a 2-3 sentence introduction… then append the compiled sections unchanged" | the report as one AI message; all work fields reset |

**Crawling.** `_crawl_single_url` POSTs `{"url": url, "f": "fit"}` to a crawl4ai server's `/md` endpoint and returns the page as markdown. Errors come back as a string ("Failed to crawl content: …") instead of an exception, so one dead link can't kill the section. The cost is that the error text lands in the drafting prompt.

**Fixed topology, bounded cost.** The run always costs 1 router + 1 planner + 3 × (1 query + ≤2 retries + 1 draft) + 1 compile LLM calls, i.e. 9–15. Nothing in the graph can make it run longer. That is the main thing a hand-built loop buys over a free-running research agent like the one in [02](02-deep-research-bot.md).

---

## Serving it: FastAPI around compiled graphs

| Endpoint | Behaviour |
|---|---|
| `POST /api/v1/chat/wait` | `ainvoke(..., stream_mode=["updates","values"])`; returns the last message, or the interrupt value if the run paused |
| `POST /api/v1/chat` | Schedules `ainvoke` as a FastAPI `BackgroundTask`; returns `run_id` immediately |
| `POST /api/v1/history` | `aget_state(thread_id)` → messages |
| `POST /api/v1/state_history` | `aget_state_history` → per-step node name, outline, index, drafts (for a UI timeline) |

```python
@asynccontextmanager
async def lifespan(app):
    async with get_checkpointer() as saver:      # AsyncSqliteSaver.from_conn_string(path)
        await saver.setup()
        for a in get_all_agent_info():
            get_agent(a.key).checkpointer = saver  # attach one saver to both compiled graphs
        yield
```

`_handle_input` checks `aget_state(...).tasks` for pending interrupts. If one exists, it sends `Command(resume=message)` instead of a new human message. Neither graph calls `interrupt()` yet, so this is plumbing for a future human-in-the-loop step ([05-graph 04](../../../ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts.md)).

---

## Review: what to fix before reusing it

| Issue | Where | Fix |
|---|---|---|
| **Bing Search API is retired** (Microsoft shut it down in August 2025) | `search_client.py` | Swap in Tavily, Exa, Brave or SerpAPI; keep the `{snippet, link, title}` normalisation |
| `json.loads(text.replace("'", '"'))` breaks on any apostrophe in a snippet | simple `run_search` | Call the wrapper's `.results(q, n)`, which returns dicts; or `ast.literal_eval` as the workflow does |
| Title read from `name` in one graph and `title` in the other | `run_search` vs. `_sync_crawl_urls` | One normaliser shared by both graphs |
| Retry condition checks for a dict key on a list | `search_section` | Test `not results` only, or the wrapper's sentinel string |
| `async with get_checkpointer()` when it returns `None` (no SQLite path) | `lifespan` | Use `contextlib.nullcontext()` for the no-persistence case |
| Router sees the full history as one f-string | both `decide_search` | Pass messages as messages; trim to the last k turns |
| Draft prompt says "use ONLY the sources", but the no-results fallback says "use general knowledge" | `search_section` / `draft_section` | Mark the section as unsourced in the report |
| Crawled pages go into the prompt untrimmed | `draft_section` | Truncate or chunk-and-rank per page ([02-rag 05](../../02-rag-retrieval/notes/05-chunking-query-parsing-and-reranking.md)) |
| No evaluation beyond `tests/qna.md` (expected behaviours written in prose) | `tests/` | Turn the six conversations into an LLM-judge set ([06-observability](../../06-observability/README.md)) |

The unit tests (`tests/test_graphs.py`, `test_models.py`, `test_routes.py`) mock the LLM and Bing. `conftest.py` sets dummy Azure and Bing variables because `src/config.py` raises at import without them.

---

## Rules of thumb

| Rule | Why |
|---|---|
| Use a structured-output router when search should be the exception | One cheap call; output can't be misparsed |
| Write the search query in its own node | The query prompt stays separate from the answer prompt |
| Clear per-turn scratch fields (`search_results`) at the end of the turn | Stale results leak into the next answer on the same thread |
| Loop with an explicit index and a `should_continue` edge | Cost is bounded by the outline length |
| Return errors as data from flaky I/O (crawl, search) | One dead URL shouldn't kill a 15-call run |
| Keep the citation format in the prompt as an example | Models copy examples more reliably than rules |

---

## Labs

| Project | Label |
|---|---|
| [internet-search-agent](https://github.com/omidreza-amrollahi/internet-search-agent) (upstream, MIT; not copied) | needs API key (Azure OpenAI) + needs Bing Search (retired, so swap the client) + optionally needs crawl4ai server on :11235; Python 3.11, `uv sync`, `langgraph dev`. Unit tests run offline with mocks |

→ Next: [02-deep-research-bot.md](02-deep-research-bot.md) — the same job without a fixed graph: one agent loop with search tools, traced with Weave and scored on a benchmark.
