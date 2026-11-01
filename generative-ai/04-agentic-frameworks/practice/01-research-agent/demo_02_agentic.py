"""Code from notes/02-agentic-search-persistence-streaming.md, in order. Run from this folder; see README.md."""
from research_lab import CORPUS, QUESTION, count_tokens, read_source, search

BOILERPLATE = "Home | Products | Pricing | Sign in | Accept all cookies | Subscribe to our newsletter\n" * 12

def scrape_page(source_id):
    return f"{BOILERPLATE}<h1>{CORPUS[source_id]['title']}</h1>\n{CORPUS[source_id]['text']}\n{BOILERPLATE}"

print("scraped page:", count_tokens(scrape_page("wang-2025")), "tokens")
print("agent tool:  ", count_tokens(read_source("wang-2025")), "tokens")
print("search hits: ", count_tokens(search(QUESTION)), "tokens for three candidate sources")

from langgraph.checkpoint.memory import InMemorySaver
from agent_langgraph import StubChatModel, build_agent, show

agent = build_agent(checkpointer=InMemorySaver())

def tool_calls(messages):
    return [c["name"] for m in messages if m.type == "ai" for c in m.tool_calls]

thread_1 = {"configurable": {"thread_id": "1"}}
first = agent.invoke({"messages": [("user", QUESTION)]}, thread_1)
print("thread 1, first ask: ", tool_calls(first["messages"]))

second = agent.invoke({"messages": [("user", "Summarise that in one line.")]}, thread_1)
print("thread 1, follow-up: ", tool_calls(second["messages"][len(first["messages"]):]), "new tool calls")

other = agent.invoke({"messages": [("user", QUESTION)]}, {"configurable": {"thread_id": "2"}})
print("thread 2, same words:", tool_calls(other["messages"]))
print("messages held:", len(second["messages"]), "in thread 1,", len(other["messages"]), "in thread 2")

history = list(agent.get_state_history({"configurable": {"thread_id": "2"}}))
for snapshot in reversed(history):
    print(f"step {snapshot.metadata['step']:>2}  next={str(snapshot.next):<16} messages={len(snapshot.values.get('messages', []))}")

import sqlite3, tempfile, os
from langgraph.checkpoint.sqlite import SqliteSaver

path = os.path.join(tempfile.mkdtemp(), "threads.db")
config = {"configurable": {"thread_id": "report-7"}}

with sqlite3.connect(path, check_same_thread=False) as connection:
    build_agent(checkpointer=SqliteSaver(connection)).invoke({"messages": [("user", QUESTION)]}, config)

with sqlite3.connect(path, check_same_thread=False) as connection:     # a new "process"
    restored = build_agent(checkpointer=SqliteSaver(connection)).get_state(config)
    print(len(restored.values["messages"]), "messages restored; last:", restored.values["messages"][-1].content[:48])

agent = build_agent()
for update in agent.stream({"messages": [("user", QUESTION)]}, stream_mode="updates"):
    for node, change in update.items():
        last = change["messages"][-1]
        print(f"{node:<6}", last.tool_calls[0]["name"] if getattr(last, "tool_calls", None) else last.content[:50])

words = []
for chunk, meta in agent.stream({"messages": [("user", QUESTION)]}, stream_mode="messages"):
    if meta["langgraph_node"] == "model" and chunk.content:
        words.append(chunk.content)
print(len(words), "chunks. First six:", words[:6])

from research_lab import PUBLISHED

agent = build_agent(checkpointer=InMemorySaver(), interrupt_before=["tools"])
config = {"configurable": {"thread_id": "review"}}
agent.invoke({"messages": [("user", QUESTION + " Then publish a report.")]}, config)

while agent.get_state(config).values["messages"][-1].tool_calls[0]["name"] != "publish_report":
    agent.invoke(None, config)                     # approve the read-only steps

state = agent.get_state(config)
pending = state.values["messages"][-1]
print("paused before:", state.next, "| wants:", pending.tool_calls[0]["name"], "| published so far:", len(PUBLISHED))

pending.tool_calls[0]["args"]["title"] = "Why agents loop, reviewed"
agent.update_state(config, {"messages": [pending]})   # same id, so add_messages replaces it
print("messages after edit:", len(agent.get_state(config).values["messages"]), "(replaced, not appended)")

agent.invoke(None, config)
print("published:", PUBLISHED[-1]["title"])

from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from agent_langgraph import TOOLS, AgentState
from research_lab import SYSTEM_PROMPT

def build_gated_agent(checkpointer):
    model = StubChatModel().bind_tools(list(TOOLS.values()))

    def call_model(state: AgentState):
        return {"messages": [model.invoke([SystemMessage(SYSTEM_PROMPT), *state["messages"]])]}

    def call_tools(state: AgentState):
        return {"messages": [ToolMessage(TOOLS[c["name"]].invoke(c["args"]), tool_call_id=c["id"])
                             for c in state["messages"][-1].tool_calls]}

    def gate(state: AgentState):
        print("  gate node runs")                  # printed twice per approval: see Pitfalls
        call = state["messages"][-1].tool_calls[0]
        decision = interrupt({"action": call["name"], "title": call["args"]["title"]})
        if decision == "approve":
            return Command(goto="tools")
        refusal = ToolMessage(f"REJECTED by reviewer: {decision}", tool_call_id=call["id"])
        return Command(goto="model", update={"messages": [refusal]})

    def route(state: AgentState):
        calls = state["messages"][-1].tool_calls
        if not calls:
            return END
        return "gate" if calls[0]["name"] == "publish_report" else "tools"

    graph = StateGraph(AgentState)
    graph.add_node("model", call_model)
    graph.add_node("tools", call_tools)
    graph.add_node("gate", gate, destinations=("tools", "model"))
    graph.add_edge(START, "model")
    graph.add_conditional_edges("model", route, ["tools", "gate", END])
    graph.add_edge("tools", "model")
    return graph.compile(checkpointer=checkpointer)

gated = build_gated_agent(InMemorySaver())
PUBLISHED.clear()
for thread, decision in (("yes", "approve"), ("no", "cites only two sources, widen it")):
    config = {"configurable": {"thread_id": thread}}
    paused = gated.invoke({"messages": [("user", QUESTION + " Then publish a report.")]}, config)
    print("paused on:", paused["__interrupt__"][0].value["action"], "| next:", gated.get_state(config).next)
    done = gated.invoke(Command(resume=decision), config)
    print(f"reviewer said {decision!r}: published={len(PUBLISHED)}; last tool result: {done['messages'][-2].content[:50]}")

config = {"configurable": {"thread_id": "yes"}}
history = list(gated.get_state_history(config))
print("checkpoints on the thread:", len(history), "| at the end, next =", history[0].next)
before_gate = next(s for s in history if s.next == ("gate",))
print("rewound to step", before_gate.metadata["step"], "next =", before_gate.next)
replay = gated.invoke(None, before_gate.config)     # runs forward from that checkpoint
print("paused again:", "__interrupt__" in replay, "| checkpoints now:", len(list(gated.get_state_history(config))))

import operator
from typing import Annotated, TypedDict

class ReportState(TypedDict):
    task: str
    plan: str
    content: Annotated[list[str], operator.add]   # accumulates across research rounds
    draft: str
    critique: str
    revision_number: int
    max_revisions: int

def plan(state):
    return {"plan": f"Answer: {state['task']}"}

def research(state):
    query = state["critique"] or state["task"]
    ids = [line.split(" | ")[0] for line in search(query).splitlines()][:1 + state["revision_number"]]
    return {"content": [i for i in ids if i not in state["content"]]}

def generate(state):
    return {"draft": " ".join(f"[{source}]" for source in state["content"]),
            "revision_number": state["revision_number"] + 1}

def should_continue(state):
    return END if state["revision_number"] > state["max_revisions"] else "reflect"

def reflect(state):
    return {"critique": f"only {len(state['content'])} sources, find more about termination loops"}

writer = StateGraph(ReportState)
for node in (plan, research, generate, reflect):
    writer.add_node(node.__name__, node)
writer.add_edge(START, "plan")
writer.add_edge("plan", "research")
writer.add_edge("research", "generate")
writer.add_conditional_edges("generate", should_continue, {END: END, "reflect": "reflect"})
writer.add_edge("reflect", "research")

result = writer.compile().invoke({"task": QUESTION, "plan": "", "content": [], "draft": "", "critique": "",
                                  "revision_number": 0, "max_revisions": 2})
print(result["revision_number"], "drafts ->", result["draft"])
