"""Code from notes/07-lcel-composition-in-practice.md, in order. Run from this folder; see README.md."""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from agent_lcel import RuleModel
from research_lab import CORPUS, QUESTION


def rule(prompt: str) -> str:
    """Stands in for a model. Each step's reply depends only on how its prompt begins."""
    if prompt.startswith("Findings"):
        return "Termination causes 21.63% of failures [wang-2025]."
    if prompt.startswith("Gaps"):
        return "No study measures the cost of a stuck run."
    return "REPORT\n" + prompt


model = RuleModel(rule=rule)
to_text = StrOutputParser()
findings_prompt = ChatPromptTemplate.from_template("Findings for: {question}")
gaps_prompt = ChatPromptTemplate.from_template("Gaps in: {findings}")
report_prompt = ChatPromptTemplate.from_template("Report.\nQ: {question}\nF: {findings}\nG: {gaps}")

pipeline = (
    RunnablePassthrough.assign(findings=findings_prompt | model | to_text)   # {question} + findings
    | RunnablePassthrough.assign(gaps=gaps_prompt | model | to_text)         # ... + gaps
    | RunnablePassthrough.assign(report=report_prompt | model | to_text)     # ... + report
)
result = pipeline.invoke({"question": QUESTION})
print(list(result))
print(result["report"])

for label, build in [("string first", lambda: "some text" | model),
                     ("plain dict first", lambda: {"age": 18} | model)]:
    try:
        build()
        print(label, "composed")
    except TypeError as error:
        print(label, "-> TypeError")

backwards = model | findings_prompt     # composes and runs, and no model sees this prompt
print("model | prompt returns a", type(backwards.invoke("Findings for: anything")).__name__)

import threading
import time

in_flight, peak, lock = 0, 0, threading.Lock()


def slow_rule(prompt: str) -> str:
    """Sleeps like a network call and tracks the most calls running at once."""
    global in_flight, peak
    with lock:
        in_flight += 1
        peak = max(peak, in_flight)
    time.sleep(0.02)
    with lock:
        in_flight -= 1
    return prompt.split("about ")[-1]


slow_chain = ChatPromptTemplate.from_template("Summarise: about {source}") | RuleModel(rule=slow_rule) | to_text
inputs = [{"source": source_id} for source_id in CORPUS]
for cap in (1, 2, 6):
    peak = 0
    start = time.perf_counter()
    answers = slow_chain.batch(inputs, config={"max_concurrency": cap})
    print(f"cap {cap}: peak {peak}, {time.perf_counter() - start:.2f}s, in input order: {answers == list(CORPUS)}")

import json

from langchain_core.output_parsers import PydanticOutputParser, PydanticToolsParser
from pydantic import BaseModel, Field, ValidationError


class Finding(BaseModel):
    source_id: str
    claim: str
    percent: float | None = Field(default=None, description="The number the claim rests on, if any")


reply = json.dumps({"source_id": "wang-2025", "claim": "Termination causes failures", "percent": 21.63})
stub = RuleModel(rule=lambda prompt: reply)

parser = PydanticOutputParser(pydantic_object=Finding)
print("parser:", (stub | parser).invoke("Extract one finding.").percent)
print("instructions it adds:", parser.get_format_instructions()[:48] + "...")

tools = stub.bind_tools([Finding]) | PydanticToolsParser(tools=[Finding])
print("tools: ", tools.invoke("Extract one finding.")[0].percent)

print("schema:", stub.with_structured_output(Finding).invoke("Extract one finding.").percent)

bad = RuleModel(rule=lambda prompt: json.dumps({"source_id": "wang-2025", "percent": "about a fifth"}))
try:
    bad.with_structured_output(Finding).invoke("Extract one finding.")
except ValidationError as error:
    print("validation:", error.error_count(), "errors:", [e["loc"][0] for e in error.errors()])

from graphlib import TopologicalSorter, CycleError


class Query(BaseModel):
    id: int
    question: str
    dependencies: list[int] = Field(default_factory=list,
                                    description="ids of queries whose answers this one needs")


class QueryPlan(BaseModel):
    query_graph: list[Query]


plan_reply = json.dumps({"query_graph": [
    {"id": 1, "question": "How often do agents fail to terminate?"},
    {"id": 2, "question": "What validates completion?"},
    {"id": 3, "question": "Does validation address the failure rate?", "dependencies": [1, 2]},
]})
user_request = "Why do agents get stuck, and would validated termination fix it?"
planner = RuleModel(rule=lambda prompt: plan_reply).with_structured_output(QueryPlan)
plan = planner.invoke(user_request)
print([(q.id, q.dependencies) for q in plan.query_graph])

def run_plan(plan: QueryPlan, answer_one) -> dict[int, str]:
    by_id = {q.id: q for q in plan.query_graph}
    missing = {d for q in plan.query_graph for d in q.dependencies} - by_id.keys()
    if missing:
        raise ValueError(f"plan references unknown ids {missing}")
    ts = TopologicalSorter({q.id: q.dependencies for q in plan.query_graph})
    ts.prepare()                                   # raises CycleError on a cyclic plan
    answers: dict[int, str] = {}
    while ts.is_active():
        ready = ts.get_ready()                     # every query whose dependencies are answered
        for qid in ready:                          # independent: could be one .batch() call
            q = by_id[qid]
            answers[qid] = answer_one(q.question, {d: answers[d] for d in q.dependencies})
        ts.done(*ready)
    return answers


def answer_one(question: str, context: dict[int, str]) -> str:
    return f"[{question[:22]} | using {sorted(context)}]"


for qid, answer in run_plan(plan, answer_one).items():
    print(qid, answer)

for label, graph in [("unknown id", [Query(id=1, question="a", dependencies=[9])]),
                     ("cycle", [Query(id=1, question="a", dependencies=[2]),
                                Query(id=2, question="b", dependencies=[1])])]:
    try:
        run_plan(QueryPlan(query_graph=graph), answer_one)
    except (ValueError, CycleError) as error:
        print(label, "->", type(error).__name__)

def map_reduce_rule(prompt: str) -> str:
    if prompt.startswith("Extract"):
        source_id, text = prompt.removeprefix("Extract one claim from ").split(": ", 1)
        return f"{text.split('. ')[0].rstrip('.')} [{source_id}]"
    claims = prompt.splitlines()[1:]
    return f"{len(claims)} claims. First: {claims[0]}"


stub = RuleModel(rule=map_reduce_rule)
map_chain = ChatPromptTemplate.from_template("Extract one claim from {source_id}: {text}") | stub | to_text
reduce_chain = ChatPromptTemplate.from_template("Combine these claims:\n{claims}") | stub | to_text

partials = map_chain.batch([{"source_id": sid, "text": doc["text"]} for sid, doc in CORPUS.items()],
                           config={"max_concurrency": 5})
print(reduce_chain.invoke({"claims": "\n".join(partials)}))
