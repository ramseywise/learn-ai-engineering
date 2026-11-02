"""Code from notes/05-langsmith.md, in order. Run from this folder; see README.md."""
import asyncio
from langsmith import traceable, tracing_context
from langsmith.utils import tracing_is_enabled
from research_lab import QUESTION, read_source, search
from trace_capture import CaptureClient, print_tree


@traceable(name="find_and_read", run_type="chain")
def find_and_read(query: str) -> str:
    hits = traced_search(query)
    return traced_read(hits.split(" | ")[0])


@traceable(name="search", run_type="tool")
def traced_search(query: str) -> str:
    return search(query)


@traceable(name="read_source", run_type="tool")
def traced_read(source_id: str) -> str:
    return read_source(source_id)


print("tracing on with no env vars:", tracing_is_enabled())
print("still returns:", find_and_read("loops")[:44])

client = CaptureClient()
with tracing_context(enabled=True, client=client, project_name="lab"):
    find_and_read("loops")
print_tree(client)

run = next(r for r in client.captured.values() if r["name"] == "search")
for field in ("name", "run_type", "inputs", "outputs", "session_name", "dotted_order"):
    print(f"{field:13}", str(run.get(field))[:74])
print("parent set:   ", run["parent_run_id"] is not None, "| same trace:", run["trace_id"] != run["id"])

from langchain_core.tracers.langchain import LangChainTracer
from agent_langgraph import StubChatModel, build_agent


def trace_graph(agent, question, **config):
    """Invoke the graph with a tracer on a fresh capture client."""
    client = CaptureClient()
    tracer = LangChainTracer(client=client, project_name="lab")
    config = {"callbacks": [tracer], "run_name": "research_agent", "tags": ["lab"],
              "metadata": {"framework": "langgraph", "prompt_version": "v1"}, **config}
    error = None
    try:
        agent.invoke({"messages": [("user", question)]}, config)
    except Exception as exc:
        error = exc
    tracer.wait_for_futures()
    return client, error


graph_client, _ = trace_graph(build_agent(), QUESTION)
print(len(graph_client.captured), "runs")
print_tree(graph_client)

def usage(client):
    """Sum what the llm runs report, the number a trace view shows at its root."""
    llm_runs = [r for r in client.captured.values() if r["run_type"] == "llm"]
    tokens = 0
    for run in llm_runs:
        message = run["outputs"]["generations"][0][0]["message"]["kwargs"]
        tokens += message["usage_metadata"]["total_tokens"]
    return len(llm_runs), tokens


calls, tokens = usage(graph_client)
print(f"model calls: {calls}, stub tokens: {tokens}")
root = next(r for r in graph_client.captured.values() if r["name"] == "research_agent")
print("metadata:", {k: v for k, v in root["extra"]["metadata"].items() if k in ("framework", "prompt_version")})
print("tags:", root["tags"])

from langsmith.integrations.google_adk import configure_google_adk
from agent_adk import ask, build_agent as build_adk_agent

print("patched:", configure_google_adk(name="research_agent", project_name="lab",
                                        metadata={"framework": "google-adk"}, tags=["lab"]))


async def trace_adk():
    client = CaptureClient()
    with tracing_context(enabled=True, client=client, project_name="lab"):
        await ask(build_adk_agent(), QUESTION)
    return client

adk_client = asyncio.run(trace_adk())
print(len(adk_client.captured), "runs")
print_tree(adk_client)

from google.adk.plugins import BasePlugin
from langsmith.run_trees import RunTree


class ToolTracer(BasePlugin):
    def __init__(self, client):
        super().__init__(name="tool_tracer")
        self.client, self.root, self.open = client, None, {}

    async def before_run_callback(self, *, invocation_context):
        question = invocation_context.user_content.parts[0].text
        self.root = RunTree(name="research_agent", run_type="chain", inputs={"question": question},
                            client=self.client, project_name="lab")
        self.root.post()

    async def before_tool_callback(self, *, tool, tool_args, tool_context):
        run = self.root.create_child(name=tool.name, run_type="tool", inputs=tool_args)
        run.post()
        self.open[tool_context.function_call_id] = run

    async def after_tool_callback(self, *, tool, tool_args, tool_context, result):
        run = self.open.pop(tool_context.function_call_id)
        run.end(outputs={"result": str(result)[:40]})
        run.patch()

    async def after_run_callback(self, *, invocation_context):
        self.root.end(outputs={})
        self.root.patch()


plugin_client = CaptureClient()
asyncio.run(ask(build_adk_agent(), QUESTION, plugins=[ToolTracer(plugin_client)]))
print_tree(plugin_client)

from collections import Counter

stuck_client, error = trace_graph(build_agent(StubChatModel(behavior="stubborn")), QUESTION,
                                  recursion_limit=9)
print("raised:", type(error).__name__)
root = next(r for r in stuck_client.captured.values() if r["name"] == "research_agent")
print("root error:", root["error"].splitlines()[0][:70])

tool_runs = sorted((r for r in stuck_client.captured.values() if r["run_type"] == "tool"),
                   key=lambda r: r["dotted_order"])
for run in tool_runs:
    print(run["name"], "|", run["inputs"]["query"][-22:], "|", str(run["outputs"]["output"])[:32]
          if run.get("outputs") else None)
print("tools used:", Counter(r["name"] for r in tool_runs), "| read_source calls:",
      sum(r["name"] == "read_source" for r in tool_runs))
print("model calls, tokens:", usage(stuck_client))

def looks_stuck(client, max_same_tool=3):
    """Flag a trace where one tool ran repeatedly with no other tool in between."""
    names = [r["name"] for r in sorted(client.captured.values(), key=lambda r: r["dotted_order"])
             if r["run_type"] == "tool"]
    longest = run_length = 0
    for previous, current in zip([None, *names], names):
        run_length = run_length + 1 if previous == current else 1
        longest = max(longest, run_length)
    return longest > max_same_tool


print("healthy run flagged:", looks_stuck(graph_client))
print("stubborn run flagged:", looks_stuck(stuck_client))

import uuid
from datetime import datetime, timezone
from langsmith.evaluation import evaluate
from langsmith.schemas import Example


def run_research(inputs, model=None):
    """The target: question in, the answer and its route out."""
    result = build_agent(model).invoke({"messages": [("user", inputs["question"])]},
                                       {"recursion_limit": 9})
    calls = [c["name"] for m in result["messages"] if m.type == "ai" for c in m.tool_calls]
    return {"answer": result["messages"][-1].content, "tools": calls}


def cites_expected(run, example):
    """Every source the example expects appears as a citation, and nothing else does."""
    cited = set(re.findall(r"\[([\w-]+)\]", run.outputs["answer"]))
    return {"key": "cites_expected", "score": float(cited == set(example.outputs["sources"]))}


def read_before_answering(run, example):
    """Route check: if the answer cites anything, a read_source call must have happened."""
    needs_read = bool(example.outputs["sources"])
    return {"key": "read_before_answering",
            "score": float(not needs_read or "read_source" in run.outputs["tools"])}


def example(question, sources):
    return Example(id=uuid.uuid4(), dataset_id=DATASET_ID, created_at=datetime.now(timezone.utc),
                   inputs={"question": question}, outputs={"sources": sources})


import re
DATASET_ID = uuid.uuid4()
EXAMPLES = [example(QUESTION, ["furgale-2026", "wang-2025"]),
            example("How do no-code tools help people debug multi-agent systems?", ["dibia-2024", "furgale-2026"]),
            example("What do commit histories show about maintaining agent frameworks?", ["liu-2026"]),
            example("What is the pricing of hosted vector databases?", [])]


def experiment(target, prefix):
    rows = list(evaluate(target, data=EXAMPLES, evaluators=[cites_expected, read_before_answering],
                         upload_results=False, client=CaptureClient(), experiment_prefix=prefix,
                         max_concurrency=0))
    scores = {}
    for row in rows:
        question = row["example"].inputs["question"]
        scores[question] = {r.key: r.score for r in row["evaluation_results"]["results"]}
    return scores


baseline = experiment(run_research, "baseline")
for question, score in baseline.items():
    print(f"{question[:44]:46}", score)

def stubborn_target(inputs):
    try:
        return run_research(inputs, model=StubChatModel(behavior="stubborn"))
    except Exception as exc:
        return {"answer": f"FAILED: {type(exc).__name__}", "tools": []}


variant = experiment(stubborn_target, "stubborn")
for name, scores in (("baseline", baseline), ("stubborn", variant)):
    for key in ("cites_expected", "read_before_answering"):
        print(f"{name:9}{key:24}{sum(s[key] for s in scores.values()) / len(scores):.2f}")
