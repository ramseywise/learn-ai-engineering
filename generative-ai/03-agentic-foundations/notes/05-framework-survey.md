---
origin: course-synthesis
sources:
  - "adv-11/AgenticAIFrameworks (AutoGen, CrewAI, LangGraph, LangMem, Google ADK, OpenAI Agents SDK, smolagents, Letta, MCP, A2A, MLflow examples) — https://github.com/adv-11/AgenticAIFrameworks"
  - "DeepLearning.AI CrewAI notebooks bundled in that repo (CrewAI/Notebooks) — https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/"
  - "Lakshmanan & Hapke, Generative AI Design Patterns (O'Reilly 2025), ch 10 Composable Agentic Workflows — ../sources/lakshmanan-hapke-genai-design-patterns-ch10-composable-agentic-workflows.pdf"
  - "generative-ai/resources.md, section 03/04 Agents and frameworks"
confidence: medium
cleaned: 2026-10-31
---

# 5 — Framework survey

> Every agent framework is a different answer to one question: what is the unit you program — a conversation, a crew, a graph, an agent object, a server, or a piece of code?

---

## Scope

This note is the map. The two frameworks this course uses in depth, LangGraph and Google ADK, have full notes in [04-agentic-frameworks](../../04-agentic-frameworks/README.md), including [04 — framework selection](../../04-agentic-frameworks/notes/06-framework-selection.md). The examples here come from the AgenticAIFrameworks repo, a set of small proof-of-concept scripts, one or two per framework. Versions in that repo date from early to mid 2025; APIs have moved since, so read the snippets for shape, not for exact signatures.

---

## The comparison

| Framework | Unit you program | Control flow | Memory | Best for |
|---|---|---|---|---|
| AutoGen 0.2 | conversable agents | conversation; group chat manager picks speakers | chat history | prototyping multi-agent dialogue |
| CrewAI | role/goal/backstory agents + tasks | sequential or hierarchical process; Flows for DAGs | short/long-term, entity | role-based pipelines, business workflows |
| LangGraph | nodes and edges over typed state | explicit state machine, `Command` routing | checkpointer + store | production control, human-in-the-loop |
| Google ADK | `Agent` with tools and sub-agents | LLM-driven delegation; workflow agents | session state, memory service | Gemini/Vertex deployments |
| OpenAI Agents SDK | `Agent` + `Runner` | handoffs between agents | sessions | small OpenAI-native agents |
| smolagents | `CodeAgent` | the model writes Python as its action | step log | code-as-action, open models |
| Letta | persistent agent server | MemGPT loop with heartbeats | core/archival/recall | stateful long-lived agents |
| Pydantic AI | typed agent with dependencies | plain Python | user-managed | typed outputs, testability |
| MCP | tool server | n/a (protocol) | n/a | sharing tools across clients |
| A2A | agent server | task protocol between agents | per task | agents from different vendors |

AutoGen's own maintainers now point new work at the **Microsoft Agent Framework**, which merges AutoGen and Semantic Kernel. The AutoGen patterns in [04](04-multi-agent-design-patterns.md) still apply.

---

## AutoGen

Two agents and a registered function; see [02](02-tool-use-and-react.md) and [04](04-multi-agent-design-patterns.md) for the details. The ReAct example in the repo runs the same code against Gemini or Mistral through an OpenAI-compatible `config_list`, and caches LLM calls on disk so reruns cost nothing:

```python
from autogen import AssistantAgent, UserProxyAgent, register_function
from autogen.cache import Cache

assistant = AssistantAgent(
    "Assistant",
    system_message="Only use the tools you have access to. Reply TERMINATE when task is done",
    llm_config={"config_list": config_list},           # Gemini or Mistral entries
)
user_proxy = UserProxyAgent(
    "User",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: (x.get("content") or "").rstrip().endswith("TERMINATE"),
)
register_function(search_tool, caller=assistant, executor=user_proxy,
                  name="search_tool", description="Search the web for a given query")

with Cache.disk(cache_seed=43) as cache:               # replay identical calls from disk
    user_proxy.initiate_chat(
        assistant,
        message=react_prompt_message,                  # fills {input} in the ReAct template
        question="What is the weather and Air quality in New Delhi today?",
        cache=cache,
    )
```

The repo also has a RAG group chat built on `RetrieveUserProxyAgent`, which retrieves from a document folder before the conversation starts.

---

## CrewAI

CrewAI separates *who* (agents with a role, goal and backstory) from *what* (tasks with an expected output), both usually in YAML:

```yaml
# config/agents.yaml
researcher:
  role: "{topic} Senior Data Researcher"
  goal: "Uncover cutting-edge developments in {topic}"
  backstory: "You're a seasoned researcher with a knack for uncovering the latest developments in {topic}."
```

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

@CrewBase
class LatestAiDevelopmentCrew:
    @agent
    def researcher(self) -> Agent:
        return Agent(config=self.agents_config["researcher"], tools=[SerperDevTool()])

    @task
    def reporting_task(self) -> Task:
        return Task(config=self.tasks_config["reporting_task"], output_file="output/report.md")

    @crew
    def crew(self) -> Crew:
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential)

LatestAiDevelopmentCrew().crew().kickoff(inputs={"topic": "AI Agents"})
```

The bundled DeepLearning.AI notebooks add the production features:

| Notebook | Feature |
|---|---|
| Sales pipeline | `output_pydantic` for typed task output; `Flow` with `@start()` / `@listen()` to chain crews; `kickoff_for_each` over leads |
| Project planning | a Pydantic `ProjectPlan` output; usage metrics and cost per run |
| Project report | a custom `BaseTool` subclass wrapping the Trello API |
| Support analysis | `FileReadTool`; training a crew from human feedback |

CrewAI's strength is how little code a role-based pipeline needs. Its weakness is the same: control flow is implicit in the process type, so debugging a hierarchical crew means reading traces.

---

## LangGraph

The repo's deep-research agent follows the LangChain *open deep research* layout: scope, research, write.

![Deep research: scope, research, write](../sources/images/langchain-deep-research-fig1.png)

*Figure: the three phases of a deep-research agent (LangChain open deep research).*

| Phase | What happens | Pattern |
|---|---|---|
| Scope | clarify with the user, then write a research brief | human-in-the-loop, structured output |
| Research | a supervisor fans out to research sub-agents | hierarchical multi-agent, parallel |
| Write | one-shot report from the gathered notes | prompt chaining |

Only the scope phase is implemented in the repo. Its key move is a node that returns a `Command` to route itself:

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

class ClarifyWithUser(BaseModel):
    need_clarification: bool
    question: str
    verification: str

def clarify_with_user(state: AgentState) -> Command[Literal["write_research_brief", "__end__"]]:
    response = model.with_structured_output(ClarifyWithUser).invoke(...)
    if response.need_clarification:
        return Command(goto=END, update={"messages": [AIMessage(content=response.question)]})
    return Command(goto="write_research_brief",
                   update={"messages": [AIMessage(content=response.verification)]})

builder = StateGraph(AgentState, input_schema=AgentInputState)
builder.add_node("clarify_with_user", clarify_with_user)
builder.add_node("write_research_brief", write_research_brief)
builder.add_edge(START, "clarify_with_user")
builder.add_edge("write_research_brief", END)
```

The repo's email agent is the textbook LangGraph loop (agent node, `ToolNode`, a `should_continue` router), and its LangMem examples are covered in [03](03-memory-as-an-operating-system.md#memory-types-in-other-frameworks). For LangGraph itself start with [04-agentic-frameworks 01](../../04-agentic-frameworks/notes/01-react-from-scratch-to-langgraph.md).

---

## Google ADK

An ADK agent is a declaration: model, instruction, tools. Tools are plain functions whose docstrings become descriptions. Returning a `status` field lets the model tell success from failure.

```python
from google.adk.agents import Agent

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city."""
    if city.lower() == "new york":
        return {"status": "success", "report": "Sunny, 25 degrees Celsius."}
    return {"status": "error", "error_message": f"Weather for '{city}' is not available."}

root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions about the time and weather in a city.",
    instruction="You are a helpful agent who can answer user questions about the time and weather in a city.",
    tools=[get_weather, get_current_time],
)
```

The repo's second example generates slide decks with python-pptx tools. The full ADK reference is [04-agentic-frameworks 04](../../04-agentic-frameworks/notes/04-google-adk.md); course notes from Google's five-day intensive are in [06](06-google-adk-intensive.md).

---

## OpenAI Agents SDK and smolagents

The smallest possible agents:

```python
from agents import Agent, Runner
agent = Agent(name="Assistant", instructions="You are a helpful assistant.", model="gpt-4o-mini")
print(Runner.run_sync(agent, "Write a Fibonacci function in C++.").final_output)
```

```python
from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel
model = LiteLLMModel(model_id="anthropic/claude-3-5-sonnet-latest", temperature=0.2)
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)   # actions are Python snippets
agent.run("How many seconds would it take for a leopard at full speed to run through Pont des Arts?")
```

smolagents' `CodeAgent` is P22 Code Execution as the default action format: instead of one JSON tool call per step, the model writes a short program that may call several tools and compute on the results. Hugging Face's docs claim this takes fewer steps than JSON tool calling. The cost is a sandbox requirement.

---

## Protocols: MCP and A2A

| | MCP | A2A |
|---|---|---|
| Connects | a model client to tools and data | an agent to another agent |
| Server exposes | tools, resources, prompts | an agent card and tasks |
| Interaction | request/response tool calls | long-running tasks with status, streaming, push notifications |
| Example in repo | `FastMCP("research")` arXiv server ([02](02-tool-use-and-react.md#mcp-tools-served-over-a-protocol)) | AutoGen currency agent served over A2A |

The A2A example wraps an AutoGen agent in an A2A task manager (`on_send_task`, `on_send_task_subscribe` for streaming) and has the agent report a typed status, so the calling agent knows whether to wait, answer a question or give up:

```python
class ResponseFormat(BaseModel):
    """Respond to the user in this format."""
    status: Literal["input_required", "completed", "error"] = "input_required"
    message: str
```

Protocol shells as a context-engineering idea are in [context 09 — protocols](../../../ai-engineering/02-context-engineering/notes/09-protocols.md).

---

## Evaluating agents: MLflow GenAI

The repo's MLflow script logs runs and scores answers with built-in LLM judges (`answer_relevance`, `faithfulness`) plus a custom judge built with `make_genai_metric` (a privacy check). Evaluation proper lives in [06-observability](../../06-observability/README.md) and [ai-engineering 06 — eval](../../../ai-engineering/06-eval/README.md).

---

## Composing patterns (book ch 10)

Lakshmanan and Hapke close the book by building one agentic workflow from earlier patterns. The useful lesson for picking a framework: you need typed outputs (P2 Grammar), tool calls (P21), a reviewer step (P17 LLM-as-Judge or P18 Reflection), guardrails (P32) and long-term memory (P28). Any of the frameworks above can host all five; they differ in which ones come built in.

| If you need | Lean toward |
|---|---|
| Explicit control flow, checkpoints, human approval mid-run | LangGraph |
| Gemini and Vertex AI deployment | Google ADK |
| A role-based pipeline with little code | CrewAI |
| Agents that remember users for months | Letta, or LangGraph + LangMem/Mem0 |
| Typed Python with tests | Pydantic AI |
| A quick OpenAI-only prototype | OpenAI Agents SDK |
| Code-as-action with open models | smolagents |

---

## Interview questions

| Question | Short answer |
|---|---|
| CrewAI vs LangGraph? | Roles and tasks with implicit flow vs an explicit state graph |
| What is code-as-action? | The model writes Python that calls tools, instead of one JSON call per step |
| MCP vs A2A? | Tools for a model vs tasks between agents |
| Why does AutoGen 0.2 code look different from current AutoGen? | 0.4 rewrote it as event-driven; Microsoft Agent Framework is the successor |
| What should a tool return on failure? | A status and a readable error, so the model can recover |

→ Next: [06 — Google ADK intensive](06-google-adk-intensive.md) — course notes on context types, the agentic SDLC, protocols and skills.
