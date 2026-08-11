# Worked Example: Retrieval → Prompt → Structured Answer (45 min, offline)

> **Constraint note:** written for the **browser-editor, no-AI, no-network** variant — CoderPad/CodeSignal style. Pure stdlib: no `numpy`, no `pydantic`, no API key. If the real assessment offers those libraries, say so and use them; the point of drilling it offline is that you are never blocked by what isn't installed.

**Format:** 45 min, shared browser editor, interviewer watching.
**Prompt:** *"Given a list of documents and a user query, retrieve the most relevant documents, build a prompt from them, and return a validated structured answer. The LLM call is stubbed — we've given you `fake_llm(prompt) -> str`. Handle missing and malformed results gracefully."*

This is the highest-probability shape for an AIE practical: it touches retrieval, prompt construction, schema validation, and error handling in one 45-minute arc, and none of it needs a network.

The trap is that it *looks* like four features. It is really one pipeline with four failure points, and the grade is mostly about the failure points.

---

## 0–5 min — clarify, then commit

Three questions, then stop asking. In a 45-minute round, a fourth question costs more than a stated assumption.

[NARRATE: "Before I write anything — three quick questions. First, can I assume no external libraries, so no numpy or pydantic? Second, is `fake_llm` deterministic, and can it return malformed JSON — do I need to handle that path? Third, roughly how many documents: tens, or tens of thousands? That decides whether a linear scan is acceptable."]

Typical answers: stdlib only, yes it can return junk, a few hundred docs.

That third answer is the one that matters and candidates skip it. A few hundred documents means **a linear scan is correct** and an inverted index is over-engineering. Say that out loud — it converts a shortcut into a deliberate choice:

[NARRATE: "A few hundred docs means I'll score every document on every query — that's O(n·m) and completely fine at this scale. I'm noting that the scoring function is the seam I'd swap for an ANN index if this grew past ~10K docs. I'd rather spend the time on the validation path, which is where this kind of pipeline actually breaks."]

Then write the interface before the implementation:

```python
def retrieve(query: str, documents: list[dict], k: int = 3) -> list[dict]: ...
def build_prompt(question: str, context: list[dict]) -> str: ...
def parse_answer(raw: str, valid_ids: set[str]) -> "Answer": ...
def retrieve_and_answer(query: str, documents: list[dict], k: int = 3) -> "Answer": ...
```

[NARRATE: "Four functions, each independently testable. I'm writing the signatures first so we agree on the shape before I fill them in — if you'd rather the whole thing be one function, tell me now."]

This is a cheap seniority signal: contracts before logic.

---

## 5–15 min — retrieval

Without embeddings, the honest move is lexical overlap. Name it as a deliberate downgrade, not a limitation you didn't notice.

[NARRATE: "No embedding API, so I'll do token-overlap scoring. I want to be explicit that this is a keyword proxy for semantic similarity — it'll miss synonyms entirely. In production this is the one component I'd replace first, with cosine over embeddings."]

```python
import re
from collections import Counter

STOPWORDS = {"the", "a", "an", "is", "are", "was", "of", "to", "in", "and", "for", "on", "what"}


def tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric tokens, stopwords removed."""
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]


def score(query_tokens: Counter, doc_tokens: Counter) -> float:
    """Overlap normalized by document length — a cheap TF proxy.

    Normalizing matters: without it, long documents win every query purely by
    having more tokens.
    """
    if not doc_tokens:
        return 0.0
    overlap = sum(min(count, doc_tokens[term]) for term, count in query_tokens.items())
    return overlap / (len(doc_tokens) ** 0.5)
```

[NARRATE: "I'm dividing by the square root of document length rather than the raw length. Raw length over-penalizes long documents; no normalization at all lets them dominate. Square root is the middle ground — it's the same intuition behind the length normalization in BM25."]

That single sentence is worth more than the rest of the function. It shows you know *why* the normalization exists rather than having copied a formula.

```python
def retrieve(query: str, documents: list[dict], k: int = 3) -> list[dict]:
    """Return the top-k documents by lexical overlap, best first.

    Documents scoring zero are excluded — returning irrelevant filler is worse
    than returning fewer results.
    """
    if not query or not query.strip():
        raise ValueError("query must be non-empty")
    if not documents:
        return []

    q = Counter(tokenize(query))
    if not q:                      # query was all stopwords
        return []

    scored = []
    for doc in documents:
        s = score(q, Counter(tokenize(doc.get("text", ""))))
        if s > 0:
            scored.append((s, doc))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [doc for _, doc in scored[:k]]
```

[NARRATE: "Two decisions to flag. I'm dropping zero-score documents rather than padding to k — if only one document matches, returning three means two are noise, and noise in the context window is what causes the model to hallucinate. And an all-stopword query returns empty rather than raising, because that's a legitimate user input, not a programmer error. Contrast with an empty query string, which I do raise on — that's a caller bug."]

That distinction — *user input returns empty, caller bug raises* — is a genuine senior signal and takes one sentence.

**Edge cases handled, said aloud:** empty corpus, empty query, all-stopword query, fewer than k matches, missing `text` key (via `.get`).

---

## 15–25 min — prompt construction

The single most-graded line in this whole exercise is the instruction that tells the model what to do when the context doesn't contain the answer.

```python
SYSTEM = """You answer questions using ONLY the provided context.

Rules:
- Cite the document id for every claim, in the form [doc_id].
- If the context does not contain the answer, set "answer" to the exact string
  "insufficient context" and return an empty sources list. Do not guess.
- Respond with JSON only, no prose before or after:
  {"answer": str, "confidence": "low"|"medium"|"high", "sources": [str]}"""


def build_prompt(question: str, context: list[dict]) -> str:
    """Assemble the system instruction, labeled context blocks, and the question."""
    if not context:
        # No retrieval hits — still ask, but the model is instructed to decline.
        blocks = "(no relevant documents found)"
    else:
        blocks = "\n\n".join(f"[{doc['id']}] {doc['text']}" for doc in context)

    return f"{SYSTEM}\n\nContext:\n{blocks}\n\nQuestion: {question}"
```

[NARRATE: "Three things I'm doing deliberately here. The id goes in square brackets inline with each block, so the model has a concrete token to copy when citing — asking for citations without giving it a citation format is the usual reason citations come back malformed. Confidence is an *enumerated* string, not a float; if you ask a model for a 0-to-1 confidence it will invent 0.87 with no calibration behind it, whereas three buckets are something it can actually apply. And I'm giving it an explicit escape hatch — 'insufficient context' — because a model with no permitted way to say 'I don't know' will fabricate one."]

Those three points map directly onto real production failure modes, and each is one line of code. This is the part of the exercise where knowing the domain shows.

**If asked "why not f-string the whole thing in one line?"** — because the system instruction is a constant that belongs outside the function, so it can be tested and versioned independently of the assembly logic.

---

## 25–37 min — structured output and validation

Without pydantic, a frozen dataclass plus explicit validation. Say what you'd use in production.

[NARRATE: "With pydantic available this is a `BaseModel` with a field validator and I'd get the error messages for free. Stdlib-only, I'll use a frozen dataclass and validate in `__post_init__` — same contract, more typing."]

```python
from dataclasses import dataclass, field
import json


@dataclass(frozen=True)
class Answer:
    answer: str
    confidence: str
    sources: list[str] = field(default_factory=list)

    VALID_CONFIDENCE = ("low", "medium", "high")

    def __post_init__(self):
        if not isinstance(self.answer, str) or not self.answer.strip():
            raise ValueError("answer must be a non-empty string")
        if self.confidence not in self.VALID_CONFIDENCE:
            raise ValueError(f"confidence must be one of {self.VALID_CONFIDENCE}, got {self.confidence!r}")
        if not isinstance(self.sources, list) or not all(isinstance(s, str) for s in self.sources):
            raise ValueError("sources must be a list of strings")
```

Now the parser — and this is where the grading concentrates, because it is the only place where an adversarial input reaches your code:

```python
FALLBACK = Answer(answer="insufficient context", confidence="low", sources=[])


def parse_answer(raw: str, valid_ids: set[str]) -> Answer:
    """Parse and validate a model response, falling back rather than raising.

    Every failure path is logged and returns FALLBACK — a bad model response is
    an expected runtime condition, not an exception.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        log.warning("model returned non-JSON: %s", e)
        return FALLBACK

    if not isinstance(data, dict):
        log.warning("model returned %s, expected object", type(data).__name__)
        return FALLBACK

    missing = {"answer", "confidence", "sources"} - data.keys()
    if missing:
        log.warning("model response missing keys: %s", sorted(missing))
        return FALLBACK

    # Grounding check: drop citations the model invented.
    claimed = data["sources"] if isinstance(data["sources"], list) else []
    grounded = [s for s in claimed if s in valid_ids]
    if len(grounded) != len(claimed):
        log.warning("dropped %d hallucinated citation(s)", len(claimed) - len(grounded))

    try:
        return Answer(answer=data["answer"], confidence=data["confidence"], sources=grounded)
    except ValueError as e:
        log.warning("schema validation failed: %s", e)
        return FALLBACK
```

[NARRATE: "The grounding check is the part I'd defend hardest. The model can return a perfectly well-formed JSON object citing a document id that was never in its context — that's the failure mode that survives every syntactic check and reaches the user as a confident, sourced, false answer. So I intersect the claimed sources against the ids I actually retrieved, and drop the rest."]

[NARRATE: "Note that everything here logs and falls back rather than raising. A malformed model response is an expected runtime condition — models do this — so it's control flow, not an exception. What I'm not doing anywhere is a bare `except: pass`; every path leaves a trace, because a pipeline that fails silently is worse than one that fails loudly."]

**If the interviewer pushes: "should a hallucinated citation invalidate the whole answer?"** — a genuinely good question with no single right answer. Say the tradeoff: dropping citations preserves a possibly-correct answer with weaker attribution; rejecting outright is safer in a regulated domain. State that you'd make it a policy flag, and that in finance or medicine you'd default to rejecting.

---

## 37–43 min — wire it up and test

```python
def retrieve_and_answer(query: str, documents: list[dict], k: int = 3) -> Answer:
    hits = retrieve(query, documents, k)
    if not hits:
        return FALLBACK                     # short-circuit: don't pay for an LLM call
    prompt = build_prompt(query, hits)
    raw = fake_llm(prompt)
    return parse_answer(raw, valid_ids={doc["id"] for doc in hits})
```

[NARRATE: "The short-circuit on empty retrieval is a cost decision as much as a correctness one — if nothing was retrieved there's nothing to ground an answer in, so calling the model is spending money to get a guess."]

Then tests, chosen to cover each failure point rather than to be numerous:

```python
DOCS = [
    {"id": "d1", "text": "Password reset is available from the account settings page."},
    {"id": "d2", "text": "Refunds are processed within 5 business days."},
]

def test_retrieval_ranks_relevant_first():
    assert retrieve("how do I reset my password", DOCS)[0]["id"] == "d1"

def test_no_match_returns_empty():
    assert retrieve("quantum chromodynamics", DOCS) == []

def test_malformed_json_falls_back():
    assert parse_answer("not json at all", {"d1"}) == FALLBACK

def test_hallucinated_citation_dropped():
    raw = '{"answer": "See settings.", "confidence": "high", "sources": ["d1", "d99"]}'
    assert parse_answer(raw, {"d1"}).sources == ["d1"]

def test_bad_confidence_falls_back():
    raw = '{"answer": "x", "confidence": 0.9, "sources": []}'
    assert parse_answer(raw, {"d1"}) == FALLBACK
```

[NARRATE: "Five tests, one per failure point: ranking, empty retrieval, malformed JSON, hallucinated citation, schema violation. I'd rather have five that each cover a distinct path than twenty on the happy path."]

---

## 43–45 min — close

Do not go silent at the end. State what you'd do next, in priority order:

[NARRATE: "If I had another hour: first, swap lexical scoring for embeddings and cosine — that's the biggest quality win and the interface is already isolated in `score`. Second, add a token budget check before the LLM call, because right now top-k of unbounded-length documents can overflow the context window. Third, make the hallucinated-citation policy configurable rather than always-drop. What I deliberately skipped: chunking, since the docs are short enough to use whole, and any caching layer."]

---

## What the interviewer is grading

| Signal | Where it appeared |
|---|---|
| Scoped before coding | Asked corpus size, chose linear scan deliberately, named the swap point |
| Contracts first | Four signatures written before any implementation |
| Knows retrieval | Length normalization, and *why* — not a copied formula |
| Knows prompting | Inline citation format, enumerated confidence, explicit escape hatch |
| Knows the real failure mode | Grounding check against retrieved ids — the bug that survives syntactic validation |
| Errors as control flow | Logs and falls back; no bare except; distinguishes user input from caller bug |
| Tests by failure path | Five tests, five distinct paths, no happy-path padding |
| Narrated throughout | Never silent; every tradeoff stated as a tradeoff |

The weakest version of this submission retrieves with a bare `in` substring check, f-strings the prompt inline, `json.loads` without a try block, and has no grounding check — it "works" on the happy path and fails on every input the interviewer actually cares about.
