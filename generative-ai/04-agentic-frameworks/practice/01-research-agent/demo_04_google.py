"""Code from notes/04-google-adk.md, in order. Run from this folder; see README.md."""
import asyncio
from google.adk.agents import LlmAgent
from agent_adk import StubLlm, ask, show
from research_lab import QUESTION, SYSTEM_PROMPT, publish_report, read_source, search

agent = LlmAgent(name="research_agent", model=StubLlm(), instruction=SYSTEM_PROMPT,
                 tools=[search, read_source, publish_report])

events = asyncio.run(ask(agent, QUESTION))
show(events)

for event in events:
    kinds = [("call " + p.function_call.name) if p.function_call else ("result " + p.function_response.name)
             if p.function_response else "text" for p in event.content.parts]
    print(f"{event.author:<15} {kinds}", event.usage_metadata.total_token_count if event.usage_metadata else "")

from google.adk.agents.run_config import RunConfig

stubborn = LlmAgent(name="stubborn", model=StubLlm(behavior="stubborn"), instruction=SYSTEM_PROMPT, tools=[search])
try:
    asyncio.run(ask(stubborn, QUESTION, run_config=RunConfig(max_llm_calls=5)))
except Exception as error:
    print(type(error).__name__, "->", error)

from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
import research_lab

def read_source(source_id: str, tool_context: ToolContext) -> str:
    """Return the full text of one source and record that it was read.

    Args:
        source_id: An id returned by search.
    """
    tool_context.state["sources_read"] = tool_context.state.get("sources_read", []) + [source_id]
    tool_context.state["user:reads_ever"] = tool_context.state.get("user:reads_ever", 0) + 1
    tool_context.state["temp:last_id"] = source_id
    return research_lab.read_source(source_id)

agent = LlmAgent(name="research_agent", model=StubLlm(), tools=[search, read_source],
                 instruction=SYSTEM_PROMPT + " Audience: {audience?}", output_key="last_answer")

async def run_twice():
    service = InMemorySessionService()
    await service.create_session(app_name="lab", user_id="u1", session_id="one", state={"audience": "engineers"})
    await ask(agent, QUESTION, service, "one")
    await ask(agent, QUESTION, service, "two")
    for session_id in ("one", "two"):
        state = (await service.get_session(app_name="lab", user_id="u1", session_id=session_id)).state
        print(session_id, {k: (v[:28] if k == "last_answer" else v) for k, v in state.items()})

asyncio.run(run_twice())

from google.adk.runners import Runner
from google.adk.tools import FunctionTool
from google.genai import types
from research_lab import PUBLISHED

agent = LlmAgent(name="research_agent", model=StubLlm(), instruction=SYSTEM_PROMPT,
                 tools=[search, read_source, FunctionTool(publish_report, require_confirmation=True)])

async def review(confirmed):
    service = InMemorySessionService()
    PUBLISHED.clear()
    events = await ask(agent, QUESTION + " Then publish a report.", service, "review")
    request = next(p.function_call for e in events for p in e.content.parts
                   if p.function_call and p.function_call.name == "adk_request_confirmation")
    print("paused on:", request.name, "| published:", len(PUBLISHED))

    answer = types.Part(function_response=types.FunctionResponse(
        id=request.id, name=request.name, response={"confirmed": confirmed}))
    runner = Runner(app_name="lab", agent=agent, session_service=service)
    async for event in runner.run_async(user_id="u1", session_id="review",
                                        new_message=types.Content(role="user", parts=[answer])):
        pass
    print(f"confirmed={confirmed}: published={len(PUBLISHED)}")

asyncio.run(review(True))
asyncio.run(review(False))

from google.adk.plugins.base_plugin import BasePlugin

class BlockUnknownSources(BasePlugin):
    def __init__(self):
        super().__init__(name="block_unknown_sources")

    async def before_tool_callback(self, *, tool, tool_args, tool_context):
        if tool.name == "read_source" and tool_args["source_id"] == "wang-2025":
            return {"result": "ERROR: this source is under review"}
        return None

agent = LlmAgent(name="research_agent", model=StubLlm(), instruction=SYSTEM_PROMPT, tools=[search, research_lab.read_source])
show(asyncio.run(ask(agent, QUESTION, plugins=[BlockUnknownSources()])))

from typing import AsyncGenerator
from google.adk.models import BaseLlm, LlmResponse

class AlwaysTransfer(BaseLlm):
    model: str = "router-stub"
    async def generate_content_async(self, llm_request, stream=False) -> AsyncGenerator[LlmResponse, None]:
        call = types.FunctionCall(id="t1", name="transfer_to_agent", args={"agent_name": "research_agent"})
        yield LlmResponse(content=types.Content(role="model", parts=[types.Part(function_call=call)]))

specialist = LlmAgent(name="research_agent", model=StubLlm(), instruction=SYSTEM_PROMPT, tools=[search, research_lab.read_source],
                      description="Answers research questions from the corpus.")
coordinator = LlmAgent(name="coordinator", model=AlwaysTransfer(), instruction="Route to a specialist.", sub_agents=[specialist])
events = asyncio.run(ask(coordinator, QUESTION))
print([e.author for e in events])

from google.adk.workflow import START, Workflow

def find_sources(node_input):
    return search(QUESTION).splitlines()[0].split(" | ")[0]

def read_top(node_input):
    return {"id": node_input, "text": research_lab.read_source(node_input)}

def format_answer(node_input):
    return f"{node_input['text'].split('. ')[0]}. [{node_input['id']}]"

pipeline = Workflow(name="research_pipeline", edges=[(START, find_sources, read_top, format_answer)])

async def run_pipeline():
    service = InMemorySessionService()
    await service.create_session(app_name="lab", user_id="u1", session_id="wf")
    runner = Runner(app_name="lab", node=pipeline, session_service=service)
    message = types.Content(role="user", parts=[types.Part(text=QUESTION)])
    async for event in runner.run_async(user_id="u1", session_id="wf", new_message=message):
        if event.output is not None:
            print(event.author, "->", str(event.output)[:66])

asyncio.run(run_pipeline())

from google.adk.memory import InMemoryMemoryService

async def remember_and_search():
    sessions, memory = InMemorySessionService(), InMemoryMemoryService()
    agent = LlmAgent(name="research_agent", model=StubLlm(), instruction=SYSTEM_PROMPT, tools=[search, research_lab.read_source])
    await ask(agent, QUESTION, sessions, "past")
    await memory.add_session_to_memory(await sessions.get_session(app_name="lab", user_id="u1", session_id="past"))
    found = await memory.search_memory(app_name="lab", user_id="u1", query="loops termination")
    other = await memory.search_memory(app_name="lab", user_id="someone-else", query="loops termination")
    print(len(found.memories), "events found for u1;", len(other.memories), "for someone else")

asyncio.run(remember_and_search())

from google.adk.evaluation import AgentEvaluator

asyncio.run(AgentEvaluator.evaluate("research_eval", "eval/loops.test.json", num_runs=1, print_detailed_results=False))
print("trajectory matched")

import json, shutil, tempfile, os
case = json.load(open("eval/loops.test.json"))
case["eval_cases"][0]["conversation"][0]["intermediate_data"]["tool_uses"].pop()
folder = tempfile.mkdtemp()
shutil.copy("eval/test_config.json", folder)
json.dump(case, open(os.path.join(folder, "wrong.test.json"), "w"))
try:
    asyncio.run(AgentEvaluator.evaluate("research_eval", os.path.join(folder, "wrong.test.json"), num_runs=1, print_detailed_results=False))
except AssertionError as error:
    print("wrong expectation fails:", str(error).strip().splitlines()[0][:70])
