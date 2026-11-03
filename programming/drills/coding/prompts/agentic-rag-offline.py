"""Retrieval -> prompt -> structured answer — practical, 45 min, stdlib only.

PROMPT
    "Given a list of documents and a user query, retrieve the most relevant
    documents, build a prompt from them, and return a validated structured
    answer. The LLM call is stubbed -- we've given you `fake_llm(prompt) -> str`.
    Handle missing and malformed results gracefully."

Constraint: pure stdlib. No numpy, no pydantic, no API key.

The interviewer answered:
    - Stdlib only.
    - Yes, `fake_llm` can return junk. Handle it.
    - A few hundred documents.

That third answer decides your retrieval approach. Say what it implies.

This looks like four features. It is one pipeline with four failure points.
"""

import json

DOCUMENTS = [
    {"id": "d1", "text": "Refunds are issued within 5 business days of approval."},
    {"id": "d2", "text": "To cancel a subscription, open Settings and choose Cancel Plan."},
    {"id": "d3", "text": "Our support hours are 9am to 6pm CET, Monday through Friday."},
    {"id": "d4", "text": "Refund requests must be filed within 30 days of purchase."},
    {"id": "d5", "text": "Password resets are sent to the email address on file."},
]

_CANNED = [
    '{"answer": "Refunds take 5 business days.", "citations": ["d1"], "confidence": "high"}',
    "Sorry, I could not find that.",  # not JSON at all
    '{"answer": "Refunds take 5 days.", "citations": ["d9"]}',
    '{"answer": "See settings.", "citations": ["d2"], "confidence": "banana"}',
]
_calls = {"n": 0}


def fake_llm(prompt: str) -> str:
    """Interviewer-supplied stub. Deterministic, and NOT always well-formed."""
    out = _CANNED[_calls["n"] % len(_CANNED)]
    _calls["n"] += 1
    return out


def retrieve(query: str, documents: list[dict], k: int = 3) -> list[dict]:
    raise NotImplementedError


def build_prompt(question: str, context: list[dict]) -> str:
    raise NotImplementedError


def parse_answer(raw: str, valid_ids: set[str]):
    raise NotImplementedError


def retrieve_and_answer(query: str, documents: list[dict], k: int = 3):
    raise NotImplementedError


if __name__ == "__main__":
    hits = retrieve("how long do refunds take", DOCUMENTS, k=3)
    assert hits, "expected at least one hit"
    assert hits[0]["id"] in {"d1", "d4"}, f"unexpected top hit: {hits[0]['id']}"
    top = retrieve("how do I cancel my subscription", DOCUMENTS, k=1)
    assert top[0]["id"] == "d2", f"unexpected top hit: {top[0]['id']}"

    result = retrieve_and_answer("how long do refunds take", DOCUMENTS)
    assert result is not None, "pipeline should degrade, not return None"

    print("smoke test passed")

    # your edge cases here -- call the pipeline 4 times in one process so every
    # canned response is exercised (the counter starts over on each run of this file)
