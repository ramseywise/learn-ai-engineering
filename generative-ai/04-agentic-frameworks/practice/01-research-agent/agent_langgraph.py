"""Note 01: the research agent as a real LangGraph StateGraph with a stub chat model."""
from itertools import count
from typing import Annotated, TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AnyMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import tool as as_tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from research_lab import SYSTEM_PROMPT, Final, Observation, count_tokens, decide, parse_known, publish_report, read_source, search

_ids = count(1)


class StubChatModel(BaseChatModel):
    """A chat model LangGraph cannot tell from a real one, driven by `decide()`."""
    behavior: str = "normal"

    @property
    def _llm_type(self) -> str:
        return "research-stub"

    def bind_tools(self, tools, **kwargs):
        return self  # a real model would send these schemas with each request

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        question = next(m.content for m in messages if m.type == "human")
        system = "\n".join(m.content for m in messages if m.type == "system")
        asked = {c["id"]: c for m in messages if m.type == "ai" for c in m.tool_calls}
        observations = [Observation(asked[m.tool_call_id]["name"], asked[m.tool_call_id]["args"], m.content)
                        for m in messages if m.type == "tool"]
        step = decide(question, observations, self.behavior, parse_known(system))
        if isinstance(step, Final):
            reply = AIMessage(content=step.text)
        else:
            call = {"name": step.name, "args": step.args, "id": f"call_{next(_ids)}", "type": "tool_call"}
            reply = AIMessage(content=step.thought, tool_calls=[call])
        prompt = sum(count_tokens(str(m.content)) for m in messages)
        completion = count_tokens(str(reply.content))
        reply.usage_metadata = {"input_tokens": prompt, "output_tokens": completion,
                                "total_tokens": prompt + completion}
        return ChatResult(generations=[ChatGeneration(message=reply)])


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


TOOLS = {f.__name__: as_tool(f) for f in (search, read_source, publish_report)}


def build_agent(model=None, checkpointer=None, interrupt_before=None):
    """Two nodes and one conditional edge: the whole ReAct loop."""
    model = (model or StubChatModel()).bind_tools(list(TOOLS.values()))

    def call_model(state: AgentState):
        return {"messages": [model.invoke([SystemMessage(SYSTEM_PROMPT), *state["messages"]])]}

    def call_tools(state: AgentState):
        results = []
        for call in state["messages"][-1].tool_calls:
            if call["name"] not in TOOLS:
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
    return graph.compile(checkpointer=checkpointer, interrupt_before=interrupt_before)


def show(messages) -> None:
    """Print a run one message per line."""
    for m in messages:
        if m.type == "ai" and m.tool_calls:
            for c in m.tool_calls:
                print(f"model  -> {c['name']}({c['args']})")
        elif m.type == "ai":
            print(f"model  => {m.content}")
        elif m.type == "tool":
            print(f"tool   <- {m.content[:70].replace(chr(10), ' ; ')}")


if __name__ == "__main__":
    from research_lab import QUESTION
    result = build_agent().invoke({"messages": [("user", QUESTION)]})
    show(result["messages"])
