"""Shared core of the research-agent lab: corpus, tools and a scripted brain.

Nothing here imports a framework. The tools are plain functions and the "model"
is a deterministic function from (question, observations) to the next step, so
the same behaviour runs through a hand-written loop, LangGraph and Google ADK
without an API key. Each framework file only adapts its own message format to
`decide()`.
"""
import json
import re
from dataclasses import dataclass

SYSTEM_PROMPT = (
    "You are a research assistant. Search the corpus, read at most two sources, "
    "then answer in two sentences and cite each source id in square brackets."
)

# Six short summaries of this pillar's sources. The sentences paraphrase the
# papers; see references.md for the full citations.
CORPUS = {
    "wang-2025": {
        "title": "Agent developer practices: framework failure study",
        "text": (
            "Logic control caused more than a third of the agent failures studied, "
            "with task termination alone at 21.63 percent of them. "
            "Recursive tool or agent calls that never stop show up as a named failure pattern."
        ),
    },
    "furgale-2026": {
        "title": "NOOA: agents as Python objects, validated termination",
        "text": (
            "Requiring a validated typed result before an agent may stop prevents unsupported "
            "declarations of completion. "
            "A harness that stops on any reply without a tool call ended 77 percent of its failed "
            "Terminal-Bench trials within ten steps."
        ),
    },
    "zhou-2023": {
        "title": "Agents: symbolic plans as state graphs",
        "text": (
            "Writing the plan as a graph of states with transition rules makes an agent more "
            "stable than a prompt alone. "
            "A control loop runs until the plan reaches its finished state."
        ),
    },
    "liu-2026": {
        "title": "Development and issues across eight agent frameworks",
        "text": (
            "Perfective changes lead agent framework commits at 40.83 percent, ahead of corrective "
            "and adaptive work. "
            "Median issue resolution ranged from about a day to more than ten days by project."
        ),
    },
    "dibia-2024": {
        "title": "AutoGen Studio: declarative agents and a profiler",
        "text": (
            "A declarative JSON specification lets teams compose and export multi-agent workflows. "
            "A profiler that reports messages, tokens, cost and tool success supports debugging."
        ),
    },
    "phoenix-2024": {
        "title": "Prompt Engineering for Generative AI: testing a cheaper model",
        "text": (
            "Test a cheaper model by labelling a sample with the expensive model and scoring the "
            "cheap one against those labels. "
            "Mixtral matched GPT-4 labels 77.5 percent of the time in the book's sentiment test."
        ),
    },
}

STOPWORDS = set("a an and are at by do does for from how in is it of on or that the to what when which why with".split())
PUBLISHED: list[dict] = []
QUESTION = "Why do framework agents get stuck in loops, and what stops them?"


def _terms(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS}


def search(query: str) -> str:
    """Search the research corpus and return the best source ids, one per line.

    Args:
        query: Keywords or a question to look up.
    """
    terms = _terms(query)
    scored = []
    for source_id, doc in CORPUS.items():
        score = len(terms & _terms(doc["title"] + " " + doc["text"]))
        if score:
            scored.append((score, source_id, doc["title"]))
    scored.sort(key=lambda row: (-row[0], row[1]))
    return "\n".join(f"{sid} | {title}" for _, sid, title in scored[:3]) or "no results"


def read_source(source_id: str) -> str:
    """Return the full text of one source from the research corpus.

    Args:
        source_id: An id returned by search, such as wang-2025.
    """
    if source_id not in CORPUS:
        return f"ERROR: unknown source {source_id}"
    return CORPUS[source_id]["text"]


def publish_report(title: str, body: str) -> str:
    """Publish the finished report. This is a side effect a human should approve.

    Args:
        title: Report title.
        body: Report text with citations.
    """
    PUBLISHED.append({"title": title, "body": body})
    return f"published: {title}"


TOOLS = {"search": search, "read_source": read_source, "publish_report": publish_report}


@dataclass
class Observation:
    """One tool result the model has seen."""
    tool: str
    args: dict
    result: str


@dataclass
class ToolStep:
    """The model asks for a tool."""
    name: str
    args: dict
    thought: str


@dataclass
class Final:
    """The model answers."""
    text: str


def _hits(search_result: str) -> list[str]:
    return [line.split(" | ")[0] for line in search_result.splitlines() if " | " in line]


def _first_sentence(text: str) -> str:
    return text.split(". ")[0].rstrip(".") + "."


def parse_known(system_text: str) -> dict[str, str]:
    """Read `KNOWN id: finding` lines, which the memory lab puts in the system prompt."""
    return dict(re.findall(r"^KNOWN ([\w-]+): (.+)$", system_text, flags=re.M))


def decide(question: str, observations: list[Observation], behavior: str = "normal",
           known: dict[str, str] | None = None) -> ToolStep | Final:
    """The scripted model. A real model would make these choices from the same inputs.

    behavior="stubborn" never stops searching, the loop-control failure in Wang et al.
    """
    known = known or {}
    searches = [o for o in observations if o.tool == "search"]
    reads = [o for o in observations if o.tool == "read_source"]
    if behavior == "stubborn":
        return ToolStep("search", {"query": f"{question} attempt {len(searches) + 1}"},
                        "The results might improve if I search once more.")
    good = {o.args["source_id"]: o.result for o in reads if not o.result.startswith("ERROR")}
    findings = {**known, **{sid: _first_sentence(text) for sid, text in good.items()}}
    if len(findings) < 2:
        if not searches:
            return ToolStep("search", {"query": question}, "I need sources before I can answer.")
        tried = {o.args["source_id"] for o in reads} | set(known)
        unread = [sid for sid in _hits(searches[-1].result) if sid not in tried]
        if unread:
            return ToolStep("read_source", {"source_id": unread[0]}, f"{unread[0]} looks relevant.")
    answer = " ".join(f"{sentence.rstrip('.')} [{sid}]." for sid, sentence in findings.items())
    answer = answer or "I found no sources that answer this."
    if "publish" in question.lower() and not any(o.tool == "publish_report" for o in observations):
        return ToolStep("publish_report", {"title": "Why agents loop", "body": answer},
                        "The report is ready to publish.")
    return Final(answer)


def count_tokens(text: str) -> int:
    """A stand-in for a tokenizer: four characters per token. Good enough to compare runs."""
    return max(1, len(text) // 4)


def as_json(payload) -> str:
    return json.dumps(payload, sort_keys=True)
