"""Code from notes/01-react-from-scratch-to-langgraph.md, in order. Run from this folder; see README.md."""
from research_lab import QUESTION, search, read_source

print(QUESTION)
print(search(QUESTION))
print(read_source("wang-2025"))

def calculate(what):
    return eval(what)          # course code: never eval model output outside a sandbox

def average_dog_weight(name):
    if name in "Scottish Terrier": return "Scottish Terriers average 20 lbs"
    elif name in "Border Collie":  return "a Border Collies average weight is 37 lbs"
    elif name in "Toy Poodle":     return "a toy poodles average weight is 7 lbs"
    else:                          return "An average dog weights 50 lbs"

known_actions = {"calculate": calculate, "average_dog_weight": average_dog_weight}
print(known_actions["average_dog_weight"]("Border Collie"), "|", known_actions["calculate"]("37 + 20"))

import re
from agent_scratch import PROMPT, KNOWN_ACTIONS, text_model

action_re = re.compile(r"^Action: (\w+): (.*)$")

def query(question, max_turns=6, model=text_model):
    messages = [{"role": "system", "content": PROMPT}, {"role": "user", "content": question}]
    for turn in range(max_turns):
        reply = model(messages)
        messages.append({"role": "assistant", "content": reply})
        actions = [m for m in map(action_re.match, reply.split("\n")) if m]
        if not actions:                        # no Action line: the model answered
            return reply
        name, arg = actions[0].groups()
        if name not in KNOWN_ACTIONS:
            observation = f"ERROR: no action named {name}"
        else:
            observation = KNOWN_ACTIONS[name](arg)
        print(f"turn {turn}: {name}({arg[:32]}...)")
        messages.append({"role": "user", "content": f"Observation: {observation}"})
    return None                                # out of turns: tell the caller, don't pretend

print(query(QUESTION))

stubborn = lambda messages: text_model(messages, behavior="stubborn")
print("result:", query(QUESTION, max_turns=3, model=stubborn))

from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.tools import tool as as_tool
from langgraph.graph import END, START, StateGraph
from agent_langgraph import StubChatModel, show
from research_lab import SYSTEM_PROMPT, publish_report

TOOLS = {f.__name__: as_tool(f) for f in (search, read_source, publish_report)}

def build_agent(model=None):
    model = (model or StubChatModel()).bind_tools(list(TOOLS.values()))

    def call_model(state: AgentState):
        return {"messages": [model.invoke([SystemMessage(SYSTEM_PROMPT), *state["messages"]])]}

    def call_tools(state: AgentState):
        results = []
        for call in state["messages"][-1].tool_calls:
            if call["name"] not in TOOLS:          # let the model recover instead of crashing
                results.append(ToolMessage(f"ERROR: no tool named {call['name']}", tool_call_id=call["id"]))
                continue
            results.append(ToolMessage(TOOLS[call["name"]].invoke(call["args"]), tool_call_id=call["id"]))
        return {"messages": results}

    def route(state: AgentState):
        return "tools" if state["messages"][-1].tool_calls else END

    graph = StateGraph(AgentState)
    graph.add_node("model", call_model)
    graph.add_node("tools", call_tools)
    graph.add_edge(START, "model")
    graph.add_conditional_edges("model", route, ["tools", END])
    graph.add_edge("tools", "model")
    return graph.compile()

agent = build_agent()
show(agent.invoke({"messages": [("user", QUESTION)]})["messages"])

from langgraph.errors import GraphRecursionError

stubborn_agent = build_agent(StubChatModel(behavior="stubborn"))
try:
    stubborn_agent.invoke({"messages": [("user", QUESTION)]}, {"recursion_limit": 9})
except GraphRecursionError as error:
    print(type(error).__name__, "->", str(error).split(".")[0])
