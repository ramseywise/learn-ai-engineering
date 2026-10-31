---
origin: langfuse-evaluation-main
sources:
  - https://github.com/gustavobrieva1/langfuse-evaluation (README.md, src/orchestrator.py, src/etl/, src/evaluators/, AB_TEST_GUIDE.md) — upstream README says "Internal use only"; only the generic design is condensed here
  - https://langfuse.com/docs/api-and-data-platform/features/export-from-ui
  - https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge
confidence: medium
cleaned: 2026-10-31
---
# 3 — Judge Pipelines over Trace Exports

> When one judge prompt is not enough: export production traces from Langfuse, flatten them into conversations, and run a pipeline of specialised judges (relevance, hallucination, completeness, escalation) in parallel, with a stronger second judge that verifies only the expensive findings.

Source: a hallucination-analysis pipeline built for a bank's RAG support assistant (gustavobrieva1/langfuse-evaluation). Its README marks it **"Internal use only"**, so this note keeps only the architecture and schemas, written generically; the client's prompts, data and results are not reproduced. Judge theory (rubrics, calibration, bias) is in [ai-engineering/06-eval 05 — LLM-as-judge](../../../ai-engineering/06-eval/notes/05-llm-as-judge.md) and grounding metrics in [07 — evaluating RAG and grounding](../../../ai-engineering/06-eval/notes/07-evaluating-rag-and-grounding.md).

---

## Where this sits

| | Note 02 | This note |
|---|---|---|
| Input | A golden dataset you wrote | Real production traces, exported |
| Ground truth | `expected_output` per item | None; the retrieved documents are the reference |
| Judge | One rubric prompt | Five specialised judge agents |
| Question answered | Is version B better than A? | What is going wrong in production, and how often? |
| Output | Scores in Langfuse | A flat table for analysis (could be written back as scores) |

---

## Stage 0 — ETL from trace exports

Trace JSON is whatever the app logged, and it changes shape between app versions. The ETL tries several paths per field and records which one hit.

```python
# Generic extractor pattern (adapted from src/etl/json_extractor.py)
import json

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

out = safe_json_parse(trace["output"])
sources  = first_path(out, [("sources",), ("structured_response", "sources")])
question = first_path(safe_json_parse(trace["input"]),
                      [("user_question",), ("structured_response", "advisor_query")])
answer   = first_path(out, [("lastMessage",), ("structured_response", "answer")])
escalated = bool(first_path(out, [("need_expert",)]))
```

| ETL step | Purpose |
|---|---|
| Parse input/output JSON per trace | Traces store payloads as strings |
| Extract question, answer, sources, escalation flags | Fields the judges need |
| Explode sources (one row per document) | Join to the document store for full text |
| Merge trace export + documents + session metadata | One row per conversation turn |
| Attach the previous turn's question and answer | "What about the other one?" is unjudgeable without it |

**Instrumentation lesson.** Half this ETL exists because the app didn't log a stable schema. Logging `question`, `answer`, `retrieved_doc_ids` and `escalated` as fixed trace fields ([note 05](05-support-agent-observability.md)) deletes most of it.

---

## Stage 1 — four judges in parallel

```python
# Shape of the orchestrator (adapted from src/orchestrator.py)
from dataclasses import dataclass, field
import concurrent.futures

@dataclass
class ConversationData:
    session_id: str
    user_question: str
    ai_response: str
    documents: list
    escalated: bool = False
    escalation_reason: str | None = None
    prev_user_question: str | None = None
    prev_ai_response: str | None = None
    turn_number: int = 1
    total_turns: int = 1
    metadata: dict = field(default_factory=dict)

def evaluate(conv: ConversationData, agents) -> dict:
    kw = dict(user_question=conv.user_question, ai_response=conv.ai_response,
              documents=conv.documents, prev_user_question=conv.prev_user_question,
              prev_ai_response=conv.prev_ai_response)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futures = {
            "hallucination": ex.submit(agents["hallucination"].evaluate, **kw),
            "relevance":     ex.submit(agents["relevance"].evaluate,
                                       user_question=conv.user_question, documents=conv.documents),
            "completeness":  ex.submit(agents["completeness"].evaluate, **kw),
            "escalation":    ex.submit(agents["escalation"].evaluate, **kw,
                                       escalated=conv.escalated,
                                       escalation_reason=conv.escalation_reason),
        }
        results = {}
        for name, f in futures.items():
            r = f.result(timeout=120)
            if r.success:                      # a failed judge is logged, not fatal
                results[name] = r.data
    return results
```

| Judge | Model tier | Question | Output fields |
|---|---|---|---|
| Document relevance | Fast | Did retrieval return documents that answer the question? | `relevance_score` 1–5, `has_answer`, `missing_information`, relevant/irrelevant doc ids |
| Hallucination detector | Strong | Is every claim in the answer supported by the documents? | `hallucination_detected`, `severity`, `hallucination_type`, `evidence[]`, `confidence` |
| Completeness | Fast | Did the answer use the relevant information it had? | `completeness_score` 1–5, `missing_information`, `unnecessary_clarification` |
| Escalation validator | Fast | Was handing off to a human right? | `escalation_appropriate`, `should_have_escalated`, `alternative_action` |

Splitting retrieval relevance from hallucination is the important move: a wrong answer from irrelevant documents is a **retrieval** bug; a wrong answer from relevant documents is a **generation** bug. One judge can't tell you which to fix.

---

## Stage 2 — verify only what is expensive

```python
# Verification runs only on positives, with a stronger model
if results.get("hallucination", {}).get("hallucination_detected"):
    results["verification"] = agents["verification"].verify_hallucination(
        hallucination_result=results["hallucination"],
        user_question=conv.user_question, ai_response=conv.ai_response,
        documents=conv.documents).data
# verification fields: verified, severity_adjustment (none|increase|decrease),
# new_severity, explanation, final_recommendation (approve|reject|review)
```

| Why gate on positives | Effect |
|---|---|
| Hallucinations are a minority of turns | The strong second judge runs on a fraction of traffic (upstream: ~15%) |
| False positives are what erodes trust in the report | A second opinion targets exactly those |
| `final_recommendation: review` | Routes disagreements to a human queue instead of guessing |

---

## The hallucination judge, in detail

Evidence-first output: the judge must list each claim and its support before it gives a verdict.

```json
{
  "hallucination_detected": true,
  "severity": "critical | major | minor | none",
  "hallucination_type": "fabrication | distortion | mixing | contradiction | none",
  "evidence": [
    {"claim": "exact text from the answer",
     "status": "hallucination | grounded",
     "document_support": "quote, or NOT FOUND",
     "explanation": "why"}
  ],
  "overall_assessment": "...",
  "confidence": 0.0
}
```

| Type | Meaning |
|---|---|
| Fabrication | Claim appears in no document |
| Distortion | Document says X, answer says a changed X (amount, condition, step) |
| Mixing | Facts about product A applied to product B |
| Contradiction | Answer contradicts a document |

| Not a hallucination (stated in the prompt) | Why it matters |
|---|---|
| Asking a clarifying question | Otherwise every clarification is flagged |
| "I don't have this information" | An honest abstention is the desired behaviour |
| Greetings and politeness | No factual content |
| Reformulating the user's question | Not a claim about the world |

**Consistency override.** After parsing, the code recomputes `grounding_ratio = grounded / total claims` and, if the claim list disagrees with the top-level boolean, flips `hallucination_detected` to match the evidence. Models often write a correct evidence list and a wrong summary flag; trust the structured part.

```python
# Consistency override (pattern from hallucination_detector.py)
claims = data.get("evidence", [])
n_bad = sum(c["status"] == "hallucination" for c in claims)
data["grounding_ratio"] = (len(claims) - n_bad) / len(claims) if claims else 0.0  # upstream default; 1.0 is arguably saner
data["hallucination_detected"] = n_bad > 0
```

---

## Prompt A/B: lenient vs strict judge

The project kept two prompt versions and compared them on the same conversations before choosing.

| | v1 (lenient) | v2 (strict) |
|---|---|---|
| Stance | "When in doubt, flag it" | Zero tolerance, but via a fixed decision procedure |
| Procedure | Free-form judgement | 1. Exact match in a document? 2. Same entity (same product)? 3. Is the inference valid? |
| Valid inference | Unspecified | Combining facts about the **same** entity is fine; carrying facts across entities is not |
| Severity | Judge's opinion | Objective categories (below) |
| Extra types | — | `entity_substitution`, `invalid_inference`; `step_failed` records which check failed |

| Severity (v2) | Claims about |
|---|---|
| Critical | Amounts, contact details, legal procedures, deadlines, identifiers |
| Major | Misrepresented features, process steps, invented requirements |
| Minor | Name variants, formatting |

Objective severity is what makes the metric stable across judge runs and comparable across months. "How bad does the judge feel" is not.

---

## Base classes and config

```python
# Shape of src/evaluators/base.py
@dataclass
class EvaluationResult:
    success: bool
    data: dict | None = None
    error: str | None = None
    raw_response: str | None = None

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, model: str) -> str: ...
    def generate_json(self, prompt, model):
        text = self.generate(prompt, model).strip()
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```")
        return json.loads(text)

class BaseAgent(ABC):
    def get_prompt(self, **kw) -> str: ...
    def parse_response(self, data: dict) -> EvaluationResult: ...
    def evaluate(self, **kw) -> EvaluationResult:
        try:
            return self.parse_response(self.llm.generate_json(self.get_prompt(**kw), self.model))
        except Exception as e:
            return EvaluationResult(success=False, error=str(e))
```

| Config | Value upstream | Why |
|---|---|---|
| Fast tier | Gemini Flash for relevance, completeness, escalation | Cheap checks, high volume |
| Strong tier | Gemini Pro for hallucination and verification | The metric that matters most |
| Temperature | 0.1 | Judge stability |
| Rate limit / retries / timeout | 60 rpm, 3 retries, 120 s | Batch runs over thousands of traces |
| `prompt_version` | `v1` / `v2` | A/B the judge itself |
| Cost (upstream estimate) | ~$3.70 per 1,000 conversations, ~$2.00 of it the hallucination judge | Budget for a weekly batch |

`EvaluationResults.to_dict()` flattens each judge's fields with a prefix (`hall_`, `doc_`, `comp_`, `esc_`, `ver_`) into one row per conversation, ready for pandas.

---

## Closing the loop with Langfuse

The upstream project stops at a DataFrame. To make the results visible next to the traces:

```python
# Write pipeline results back as Langfuse scores (not in upstream)
langfuse.create_score(trace_id=row.trace_id, name="hallucination",
                      value=float(row.hall_hallucination_detected),
                      comment=row.hall_overall_assessment)
langfuse.create_score(trace_id=row.trace_id, name="retrieval_relevance",
                      value=row.doc_relevance_score)
```

Then annotation queues ([note 01](01-tracing-with-langfuse.md)) can pull every `verification.final_recommendation == "review"` trace for a human.

---

## Rules of thumb

| Rule | Why |
|---|---|
| One judge per failure mode | Each output maps to one fix (retrieval vs generation vs routing) |
| Evidence list before verdict; recompute the verdict from the evidence | Structured parts are more reliable than summary flags |
| Tell the judge what is *not* a failure | Abstentions and clarifications otherwise inflate the rate |
| Strong model on the metric that matters; verify only positives | Cost goes where precision matters |
| A/B the judge prompt before trusting its trend line | A judge change looks like a product change |
| Log a stable schema so ETL stays trivial | Every fallback path is a past schema drift |

---

→ Next: [04-langfuse-mcp-server.md](04-langfuse-mcp-server.md) — instead of exporting traces to a pipeline, let an agent query Langfuse directly through MCP.
