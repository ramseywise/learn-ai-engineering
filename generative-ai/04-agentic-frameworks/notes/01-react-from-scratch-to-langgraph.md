---
origin: AI-Agents-in-LangGraph-main
sources:
  - https://github.com/ksm26/AI-Agents-in-LangGraph (Lesson_1_Student.ipynb, Lesson_2_Student.ipynb)
  - https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/ (L1 Build an Agent from Scratch, L2 LangGraph Components)
  - https://til.simonwillison.net/llms/python-react-pattern
  - https://arxiv.org/abs/2210.03629
confidence: high
cleaned: 2026-10-31
---
# 1 — ReAct from Scratch, then in LangGraph

> Build the same tool-using agent twice: first as a 40-line Python loop around a chat model, then as a two-node LangGraph `StateGraph`. The point is to see exactly which lines the framework takes over.

Course: DeepLearning.AI, *AI Agents in LangGraph* (Harrison Chase, Rotem Weiss), lessons L1 and L2. The theory of why an agent is a cyclic graph is in [ai-engineering/05-graph-engineering 02 — graph primitives](../../../ai-engineering/05-graph-engineering/notes/02-graph-primitives.md) and [03 — state and reducers](../../../ai-engineering/05-graph-engineering/notes/03-state-and-reducers.md). This note is the mechanics.

---

## The split of work

![ReAct loop: the LLM proposes, the code around it acts](../sources/images/ksm26-ai-agents-in-langgraph-fig1.png)

*Figure: the ReAct loop from L1. The LLM decides; the surrounding code runs the action and feeds back the observation. Source: ksm26/AI-Agents-in-LangGraph, `images/l1_1.png`.*

| Who | Does what |
|---|---|
| LLM | Reads the transcript, writes a `Thought`, picks an `Action` and its input, or writes the `Answer` |
| Your code | Parses the action, looks it up in a registry, runs it, appends `Observation: ...`, calls the LLM again |
| Loop guard | Caps turns (`max_turns`) so a model that never answers can't spin forever |

ReAct ([Yao et al., 2022](https://arxiv.org/abs/2210.03629)) is the name for interleaving reasoning and acting in one transcript. Everything else in this pillar is a framework that owns some part of the right-hand column.

---

## L1 — the agent as a plain class

The agent is a message list plus a call. Nothing else.

```python
# L1 — Agent: keeps the transcript, calls the model, appends the reply
from openai import OpenAI
client = OpenAI()                     # needs OPENAI_API_KEY

class Agent:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = client.chat.completions.create(
            model="gpt-4o", temperature=0, messages=self.messages)
        return completion.choices[0].message.content
```

### The prompt is the protocol

Before native tool calling, the "API" between model and code was a text format the prompt teaches by example.

```text
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:
calculate:
e.g. calculate: 4 * 7 / 3
average_dog_weight:
e.g. average_dog_weight: Collie

Example session:
Question: How much does a Bulldog weigh?
Thought: I should look the dogs weight using average_dog_weight
Action: average_dog_weight: Bulldog
PAUSE
Observation: A Bulldog weights 51 lbs
Answer: A bulldog weights 51 lbs
```

| Token | Who writes it | Purpose |
|---|---|---|
| `Thought:` | model | Scratchpad; makes the next action conditional on stated reasoning |
| `Action: name: input` | model | The tool call, in a parseable line |
| `PAUSE` | model | "Stop generating, run the tool" |
| `Observation:` | code | The tool result, fed back as the next user turn |
| `Answer:` | model | Termination signal |

### Tools and the registry

```python
# L1 — tools are plain functions; the registry maps the name the model writes to the callable
def calculate(what):
    return eval(what)          # course code: never eval model output outside a sandbox

def average_dog_weight(name):
    if name in "Scottish Terrier": return "Scottish Terriers average 20 lbs"
    elif name in "Border Collie":  return "a Border Collies average weight is 37 lbs"
    elif name in "Toy Poodle":     return "a toy poodles average weight is 7 lbs"
    else:                          return "An average dog weights 50 lbs"

known_actions = {"calculate": calculate, "average_dog_weight": average_dog_weight}
```

The course first drives this by hand (call the agent, run the tool yourself, paste `Observation: ...` back) for "I have 2 dogs, a border collie and a scottish terrier. What is their combined weight": three tool rounds (two weights, one sum) before the answer. Doing it by hand once is the fastest way to see what the loop automates.

### The loop

```python
# L1 — query(): parse "Action:" lines, dispatch, feed back the observation
import re
action_re = re.compile(r'^Action: (\w+): (.*)$')

def query(question, max_turns=5):
    bot = Agent(prompt)
    next_prompt = question
    for _ in range(max_turns):
        result = bot(next_prompt)
        actions = [action_re.match(a) for a in result.split('\n') if action_re.match(a)]
        if not actions:
            return result                        # no Action line → the model answered
        action, action_input = actions[0].groups()
        if action not in known_actions:
            raise Exception(f"Unknown action: {action}: {action_input}")
        observation = known_actions[action](action_input)
        next_prompt = f"Observation: {observation}"
```

| Weakness of the hand-rolled loop | What replaces it in L2 |
|---|---|
| Regex parsing of free text; a stray format breaks it | Native tool calling (`bind_tools`), structured `tool_calls` |
| One action per turn (`actions[0]`) | The model can emit several tool calls in one message |
| Unknown tool raises and kills the run | Return "bad tool name, retry" as the observation |
| State is a private list on one object | Typed graph state with a reducer |
| No pause, resume, or inspection | Checkpointer + threads (note 02) |

---

## L2 — the same agent as a graph

![LangGraph adds cyclic graphs, persistence and human-in-the-loop](../sources/images/ksm26-ai-agents-in-langgraph-fig3.png)

*Figure: what LangGraph adds over a LangChain chain: cycles, persistence, human-in-the-loop. Source: ksm26/AI-Agents-in-LangGraph, `images/l2_2.png`.*

![LangChain building blocks used inside the graph](../sources/images/ksm26-ai-agents-in-langgraph-fig2.png)

*Figure: the LangChain pieces (prompt templates, tools, chat model) the graph nodes call. Source: ksm26/AI-Agents-in-LangGraph, `images/l2_1.png`.*

| LangGraph component | Role in this agent |
|---|---|
| State (`TypedDict`) | The shared object every node reads and returns updates to |
| Reducer (`Annotated[..., operator.add]`) | How a node's update merges into state: append, not overwrite |
| Node | A Python function `state -> partial update` |
| Edge | Fixed transition (`action → llm`) |
| Conditional edge | A function of state that picks the next node (`llm → action` or `END`) |
| Entry point | Where a run starts (`llm`) |
| `compile()` | Freezes the graph into a runnable with `invoke` / `stream` |

### State and reducer

```python
# L2 — the whole state is one message list; operator.add makes updates append
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
```

Without the reducer, each node's `{'messages': [msg]}` would replace the list. With it, the transcript accumulates. This is the one line that carries the conversation; reducers in general are in [graph-engineering 03](../../../ai-engineering/05-graph-engineering/notes/03-state-and-reducers.md).

### The graph

```python
# L2 — two nodes, one conditional edge, one loop-back edge
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, ToolMessage

class Agent:
    def __init__(self, model, tools, system=""):
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges("llm", self.exists_action, {True: "action", False: END})
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile()
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)       # tool schemas go to the model API

    def exists_action(self, state: AgentState):
        return len(state['messages'][-1].tool_calls) > 0

    def call_openai(self, state: AgentState):
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        return {'messages': [self.model.invoke(messages)]}

    def take_action(self, state: AgentState):
        results = []
        for t in state['messages'][-1].tool_calls:
            if t['name'] not in self.tools:
                result = "bad tool name, retry"    # let the model recover instead of crashing
            else:
                result = self.tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        return {'messages': results}
```

| L1 line | L2 equivalent |
|---|---|
| `self.messages.append(...)` | Node returns `{'messages': [...]}`; the reducer appends |
| `action_re.match` | `message.tool_calls` (structured, from the API) |
| `if actions: ... else: return` | `exists_action` + conditional edge to `END` |
| `while i < max_turns` | The `action → llm` edge; cap with `recursion_limit` in the run config |
| `"Observation: ..."` | `ToolMessage(tool_call_id=...)` matched to the call |

`tool_call_id` matters: the provider rejects a transcript where a tool result does not answer a tool call in the preceding assistant message.

### Running it

```python
# L2 — a search tool and three queries (needs OPENAI_API_KEY and TAVILY_API_KEY)
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

tool = TavilySearchResults(max_results=4)
prompt = ("You are a smart research assistant. Use the search engine to look up information. "
          "You are allowed to make multiple calls (either together or in sequence). "
          "Only look up information when you are sure of what you want. ...")
abot = Agent(ChatOpenAI(model="gpt-4o"), [tool], system=prompt)

abot.graph.invoke({"messages": [HumanMessage(content="What is the weather in sf?")]})
abot.graph.invoke({"messages": [HumanMessage(content="What is the weather in SF and LA?")]})
# multi-hop: who won the 2024 Super Bowl → HQ state → that state's GDP
abot.graph.get_graph().draw_png()          # renders llm ⇄ action, llm → __end__
```

| Query | What it shows |
|---|---|
| Weather in SF | One tool call, one loop back, answer |
| Weather in SF **and** LA | Two `tool_calls` in one assistant message, run in one `action` step |
| Super Bowl → state → GDP | Sequential dependency: each search needs the last answer. The course swaps to gpt-4o here because gpt-3.5 dropped hops |

---

## API drift since the course

The course pins 2024-era packages. The ideas hold; some names moved.

| Course code | Current equivalent |
|---|---|
| `graph.set_entry_point("llm")` | `graph.add_edge(START, "llm")` (both still work) |
| `langchain_community...TavilySearchResults` | `langchain_tavily.TavilySearch` |
| Hand-written `Agent` class | `langgraph.prebuilt.create_react_agent(model, tools)`, used in [note 03](03-long-term-memory-with-langgraph.md) |
| `ChatOpenAI(model=...)` | `init_chat_model("openai:gpt-4o")` for provider-agnostic code |

Check the current [LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview) before copying any import.

---

## Labs

| Lab | Where | Runs |
|---|---|---|
| L1 ReAct from scratch | [upstream Lesson_1_Student.ipynb](https://github.com/ksm26/AI-Agents-in-LangGraph/blob/main/Lesson_1_Student.ipynb) | Needs `OPENAI_API_KEY` |
| L2 LangGraph components | [upstream Lesson_2_Student.ipynb](https://github.com/ksm26/AI-Agents-in-LangGraph/blob/main/Lesson_2_Student.ipynb) | Needs `OPENAI_API_KEY`, `TAVILY_API_KEY`; `draw_png` needs graphviz |

---

→ Next: [02-agentic-search-persistence-streaming.md](02-agentic-search-persistence-streaming.md) — swap the generic search tool for an agent-shaped one, then give this graph a checkpointer so it remembers threads and streams tokens.
