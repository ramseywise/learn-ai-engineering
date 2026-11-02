"""Code from notes/06-framework-selection.md, in order. Run from this folder; see README.md."""
import compare

compare.main()

import asyncio
import logging

from langgraph.errors import GraphRecursionError

import agent_adk
import agent_langgraph
import agent_scratch
from research_lab import QUESTION

logging.disable(logging.ERROR)   # ADK logs the limit error with a full traceback before raising it


class CountingChat(agent_langgraph.StubChatModel):
    calls: list = []

    def _generate(self, *args, **kwargs):
        self.calls.append(1)
        return super()._generate(*args, **kwargs)


class CountingLlm(agent_adk.StubLlm):
    calls: list = []

    async def generate_content_async(self, *args, **kwargs):
        self.calls.append(1)
        async for response in super().generate_content_async(*args, **kwargs):
            yield response


scratch_calls = []


def stuck_text_model(messages):
    scratch_calls.append(1)
    return agent_scratch.text_model(messages, behavior="stubborn")


print("no framework returned", agent_scratch.query(QUESTION, model=stuck_text_model, verbose=False),
      "after", len(scratch_calls), "calls")

graph_model = CountingChat(behavior="stubborn")
try:
    agent_langgraph.build_agent(graph_model).invoke({"messages": [("user", QUESTION)]})
except GraphRecursionError as error:
    print("langgraph raised", type(error).__name__, "after", len(graph_model.calls), "calls")

adk_model = CountingLlm(behavior="stubborn")
try:
    asyncio.run(agent_adk.ask(agent_adk.build_agent(adk_model), QUESTION))
except Exception as error:
    print("google-adk raised", type(error).__name__, "after", len(adk_model.calls), "calls")

import agent_adk
import agent_langgraph
import agent_scratch
from research_lab import read_source, search

print("scratch uses the shared search:", agent_scratch.KNOWN_ACTIONS["search"] is search)
print("langgraph wraps it:", agent_langgraph.TOOLS["search"].func is search)
print("adk takes it as is:", search in agent_adk.build_agent().tools)

answers = {
    "no framework": agent_scratch.query(QUESTION, verbose=False).removeprefix("Answer: "),
    "langgraph": agent_langgraph.build_agent().invoke({"messages": [("user", QUESTION)]})["messages"][-1].content,
    "google-adk": asyncio.run(agent_adk.ask(agent_adk.build_agent(), QUESTION))[-1].content.parts[0].text,
}
print("all three give the same answer:", len(set(answers.values())) == 1)
print(answers["langgraph"])

def graph_export(result):
    """LangGraph messages to neutral rows."""
    rows = []
    for m in result["messages"]:
        calls = [c["name"] for c in getattr(m, "tool_calls", [])]
        rows.append({"role": m.type, "tools": calls, "text": str(m.content)[:30]})
    return rows


def adk_export(events):
    """ADK events to the same rows. Results arrive as function_response parts."""
    rows = []
    for event in events:
        for part in event.content.parts:
            if part.function_call:
                rows.append({"role": "ai", "tools": [part.function_call.name], "text": ""})
            elif part.function_response:
                rows.append({"role": "tool", "tools": [], "text": str(part.function_response.response)[:30]})
            else:
                rows.append({"role": "ai", "tools": [], "text": part.text[:30]})
    return rows


graph_rows = graph_export(agent_langgraph.build_agent().invoke({"messages": [("user", QUESTION)]}))
adk_rows = adk_export(asyncio.run(agent_adk.ask(agent_adk.build_agent(), QUESTION)))
tool_order = lambda rows: [t for r in rows for t in r["tools"]]
print("langgraph tools:", tool_order(graph_rows))
print("adk tools:      ", tool_order(adk_rows))
print("same route:", tool_order(graph_rows) == tool_order(adk_rows))
