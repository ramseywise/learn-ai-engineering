"""Export, ETL and deterministic judges over the synthetic traces.

Every judge here is a stand-in for a model call, with the same inputs and outputs a
model judge would have, so the pipeline around it can run and be measured offline.
"""

import json
import re
from dataclasses import dataclass, field

from .pricing import llm_cost

FAST_MODEL = "claude-haiku-5-5"
STRONG_MODEL = "claude-opus-5-5"
# Token estimates per judged turn, used only to price a batch.
FAST_TOKENS = {"input_tokens": 900, "output_tokens": 180}
STRONG_TOKENS = {"input_tokens": 1800, "output_tokens": 500}


def raw_export(trace):
    """A trace as an export gives it: payloads are strings, and v2 changed the shape."""
    if trace.release == "v1":
        output = {"lastMessage": trace.answer, "sources": trace.citations, "need_expert": trace.escalated}
        inp = {"user_question": trace.question}
    else:
        output = {"structured_response": {"answer": trace.answer, "sources": trace.citations}, "need_expert": trace.escalated}
        inp = {"structured_response": {"advisor_query": trace.question}}
    search = [s for s in trace.spans if s.name == "kb_search"][-1]
    return {"id": trace.trace_id, "input": json.dumps(inp, ensure_ascii=False), "output": json.dumps(output, ensure_ascii=False),
            "documents": trace.documents, "language": trace.language,
            "metadata": {"route": trace.route, "top_score": search.tool_result["top_score"],
                         "amount_eur": trace.amount_eur, "release": trace.release}}


def safe_json_parse(value):
    if isinstance(value, dict):
        return value
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return {}


def first_path(obj, paths):
    """Return the first non-empty value among candidate key paths."""
    for path in paths:
        cur = obj
        for key in path:
            cur = cur.get(key) if isinstance(cur, dict) else None
        if cur:
            return cur
    return None


@dataclass
class ConversationData:
    trace_id: str
    question: str
    answer: str
    sources: list
    documents: list
    escalated: bool = False
    metadata: dict = field(default_factory=dict)


def to_conversation(row):
    out, inp = safe_json_parse(row["output"]), safe_json_parse(row["input"])
    return ConversationData(
        trace_id=row["id"],
        question=first_path(inp, [("user_question",), ("structured_response", "advisor_query")]),
        answer=first_path(out, [("lastMessage",), ("structured_response", "answer")]),
        sources=first_path(out, [("sources",), ("structured_response", "sources")]) or [],
        documents=row["documents"], escalated=bool(first_path(out, [("need_expert",)])),
        metadata={**row["metadata"], "language": row["language"]},
    )


def _numbers(text):
    return set(re.findall(r"\d+", text))


def _overlap(answer, documents):
    words = {w.strip(".,").lower() for w in answer.split()}
    doc_words = {w.strip(".,").lower() for d in documents for w in d["text"].split()}
    return len(words & doc_words) / max(len(words), 1)


def relevance_judge(conv):
    """Did retrieval return documents that can answer? Fast tier."""
    score = conv.metadata["top_score"]
    return {"relevance_score": 1 + round(score * 4), "has_answer": score >= 0.5}


def escalation_judge(conv):
    """Was a refund above the 500 EUR limit handed to a human? Fast tier."""
    amount = conv.metadata["amount_eur"]
    should = amount is not None and amount > 500
    return {"should_have_escalated": should, "escalation_appropriate": conv.escalated or not should}


def fast_hallucination(conv, stance="strict"):
    """First-pass grounding check. Fast tier, runs on every turn.

    strict: a fixed procedure, checking numbers and citations against the documents.
    lenient: when in doubt, flag. Also flags low word overlap with the documents,
    which is what a Danish answer over English documents always has.
    """
    retrieved = {d["url"] for d in conv.documents}
    doc_numbers = set().union(*(_numbers(d["text"]) for d in conv.documents)) if conv.documents else set()
    evidence = []
    for url in conv.sources:
        if url not in retrieved:
            evidence.append({"claim": url, "status": "hallucination", "document_support": "NOT FOUND"})
    for n in sorted(_numbers(conv.answer) - doc_numbers):
        evidence.append({"claim": n, "status": "hallucination", "document_support": "NOT FOUND"})
    if stance == "lenient" and _overlap(conv.answer, conv.documents) < 0.5:
        evidence.append({"claim": "low overlap", "status": "hallucination", "document_support": "NOT FOUND"})
    return {"hallucination_detected": bool(evidence), "evidence": evidence}


def verify_hallucination(conv):
    """Second opinion on a flagged turn. Strong tier, reads only the cited documents."""
    cited = [d for d in conv.documents if d["url"] in conv.sources]
    if conv.sources and not cited:
        return {"verified": True, "type": "fabrication", "severity": "critical"}
    cited_numbers = set().union(*(_numbers(d["text"]) for d in cited)) if cited else set()
    if _numbers(conv.answer) - cited_numbers:
        return {"verified": True, "type": "distortion", "severity": "critical"}
    return {"verified": False, "type": "none", "severity": "none"}


def run_pipeline(conv, stance="strict"):
    """All judges for one turn, with verification gated on the first pass."""
    result = {"trace_id": conv.trace_id, "relevance": relevance_judge(conv), "escalation": escalation_judge(conv),
              "hallucination": fast_hallucination(conv, stance)}
    if result["hallucination"]["hallucination_detected"]:
        result["verification"] = verify_hallucination(conv)
    return result


def flagged(result):
    """A turn counts as hallucinated only when the second judge agrees."""
    return bool(result.get("verification", {}).get("verified"))


def pipeline_cost(results, n_fast_judges=3):
    """Priced at the dated rates in pricing.py from the token estimates above."""
    fast = len(results) * n_fast_judges * llm_cost(FAST_MODEL, **FAST_TOKENS)
    strong = sum("verification" in r for r in results) * llm_cost(STRONG_MODEL, **STRONG_TOKENS)
    return {"fast_usd": fast, "strong_usd": strong, "total_usd": fast + strong}


def precision_recall(flags, truth):
    """Measure a check against the seeded labels."""
    tp = sum(f and t for f, t in zip(flags, truth))
    fp = sum(f and not t for f, t in zip(flags, truth))
    fn = sum(t and not f for f, t in zip(flags, truth))
    return {"tp": tp, "fp": fp, "fn": fn, "precision": tp / (tp + fp) if tp + fp else 0.0, "recall": tp / (tp + fn) if tp + fn else 0.0}
