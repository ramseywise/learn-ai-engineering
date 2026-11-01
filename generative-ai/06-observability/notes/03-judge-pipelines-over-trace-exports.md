---
origin: langfuse-evaluation-main
sources:
  - https://github.com/gustavobrieva1/langfuse-evaluation (README.md, src/orchestrator.py, src/etl/, src/evaluators/, AB_TEST_GUIDE.md); upstream README says "Internal use only", so only the generic design is condensed here
  - https://langfuse.com/docs/api-and-data-platform/features/export-from-ui
  - https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge
  - https://platform.claude.com/docs/en/about-claude/pricing
  - ../practice/support_agent/judges.py
confidence: medium
cleaned: 2026-11-01
---
# 3 — Judge Pipelines over Trace Exports

> When one judge prompt is not enough: export production traces from Langfuse, flatten them into conversations, and run specialised judges (relevance, hallucination, completeness, escalation) in parallel, with a stronger second judge that verifies only the expensive findings.

By the end of chapter 2, Acme Books had a release gate that passed the billing category while billing answers were going wrong in production. A golden set can only test what someone thought to write down. To learn what is actually going wrong, and how often, you have to read production, and at 100 turns a day nobody reads everything. So you build something that does: a pipeline of judges that goes through the export each week and tells a person which turns to look at. The design question is how to make that trustworthy and affordable, since a judge that cries wolf on a third of the traffic gets switched off.

The source is a hallucination-analysis pipeline built for a bank's RAG support assistant (gustavobrieva1/langfuse-evaluation). Its README marks it **"Internal use only"**, so this note keeps only the architecture and schemas, written generically. The client's prompts, data and results aren't reproduced. Judge theory (rubrics, calibration, bias) is in [ai-engineering/06-eval 05 — LLM-as-judge](../../../ai-engineering/06-eval/notes/05-llm-as-judge.md) and grounding metrics in [07 — evaluating RAG and grounding](../../../ai-engineering/06-eval/notes/07-evaluating-rag-and-grounding.md).

The offline judges in [`judges.py`](../practice/support_agent/judges.py) are deterministic rules that behave the way a first-pass and a verifying model plausibly would. They let us measure the *pipeline design* against planted failures. They say nothing about how well any real model judges, which you must measure on your own traces.

---

## Where this sits

| | [Chapter 2](02-scoring-datasets-experiments.md) | This chapter |
|---|---|---|
| Input | A golden dataset you wrote | Real production traces, exported |
| Ground truth | `expected_output` per item | None; the retrieved documents are the reference |
| Judge | One rubric prompt | Specialised judges, one per failure mode |
| Question answered | Is version B better than A? | What is going wrong in production, and how often? |
| Output | Scores in Langfuse | A flat table for analysis, written back as scores |

```text
Langfuse export ──> ETL ──> ConversationData ──┬─> relevance judge     (fast, every turn)
                                               ├─> completeness judge  (fast, every turn)
                                               ├─> escalation judge    (fast, every turn)
                                               └─> grounding, first pass (fast, every turn)
                                                        │ only if flagged
                                                        v
                                                   verifier (strong, a small fraction)
                                                        │
                       flat table, one row per turn  <──┘──> scores on the trace ──> review queue
```

---

## Stage 0: ETL from trace exports

Trace JSON is whatever the app logged, and it changes shape between app versions. Here are two turns from the same agent, either side of the release that restructured its output.

```python
from support_agent import generate_traces
from support_agent.judges import raw_export

traces = generate_traces()
for release in ["v1", "v2.0"]:
    row = raw_export(next(t for t in traces if t.release == release and t.seeded_failure is None))
    print(release, "input :", row["input"][:90])
    print(release, "output:", row["output"][:120], "...")
```

```text
v1 input : {"user_question": "What is the default payment term?"}
v1 output: {"lastMessage": "The default payment term is 14 days. Change it under Invoice settings.", "sources": ["https://help.acme ...
v2.0 input : {"structured_response": {"advisor_query": "Hvor mange brugere er der på Standard planen?"}
v2.0 output: {"structured_response": {"answer": "Standard planen har 5 users. Du tilføjer brugere under Indstillinger og Team.", "sou ...
```

A parser written for the first shape returns nothing for the second, and doesn't complain. So the ETL tries several paths per field. The pattern comes from the upstream extractor.

```python
from support_agent import generate_traces
from support_agent.judges import first_path, raw_export, safe_json_parse, to_conversation

rows = [raw_export(t) for t in generate_traces()]

naive = sum(bool(safe_json_parse(r["output"]).get("lastMessage")) for r in rows)
robust = [to_conversation(r) for r in rows]
print(f"answer recovered by the v1-only parser: {naive} of {len(rows)}")
print(f"answer recovered with fallback paths:   {sum(bool(c.answer) for c in robust)} of {len(rows)}")

print(first_path({"structured_response": {"answer": "14 days"}}, [("lastMessage",), ("structured_response", "answer")]))
c = robust[0]
print(c.trace_id, c.escalated, c.metadata["route"], len(c.documents), "documents")
```

```text
answer recovered by the v1-only parser: 900 of 1400
answer recovered with fallback paths:   1400 of 1400
14 days
t00022 False billing 2 documents
```

A weekly report built on the first parser would silently cover less and less of production, and would show the failure rate falling as coverage fell.

| ETL step | Purpose |
|---|---|
| Parse input/output JSON per trace | Traces store payloads as strings |
| Extract question, answer, sources, escalation flags | Fields the judges need |
| Explode sources (one row per document) | Join to the document store for full text |
| Merge trace export + documents + session metadata | One row per conversation turn |
| Attach the previous turn's question and answer | "What about the other one?" is unjudgeable without it |

**Instrumentation lesson.** Half this ETL exists because the app didn't log a stable schema. Logging `question`, `answer`, `retrieved_doc_ids` and `escalated` as fixed trace fields ([chapter 5](05-support-agent-observability.md)) deletes most of it.

---

## Stage 1: judges in parallel

Each judge answers one question, because each answer maps to a different fix. Splitting retrieval relevance from hallucination is the important move. A wrong answer from irrelevant documents is a **retrieval** bug, and a wrong answer from relevant documents is a **generation** bug. One judge can't tell you which to fix.

| Judge | Model tier | Question | Output fields |
|---|---|---|---|
| Document relevance | Fast | Did retrieval return documents that answer the question? | `relevance_score` 1–5, `has_answer`, `missing_information`, relevant/irrelevant doc ids |
| Hallucination detector | Strong upstream; first pass fast here | Is every claim in the answer supported by the documents? | `hallucination_detected`, `severity`, `hallucination_type`, `evidence[]`, `confidence` |
| Completeness | Fast | Did the answer use the relevant information it had? | `completeness_score` 1–5, `missing_information`, `unnecessary_clarification` |
| Escalation validator | Fast | Was handing off to a human right? | `escalation_appropriate`, `should_have_escalated`, `alternative_action` |

The orchestrator's shape is short. Run judges in a thread pool, since they spend their time waiting on the network, and let one judge fail without losing the others. The stub judge here raises, as a real one will when an API call times out.

```python
import concurrent.futures
from support_agent import generate_traces
from support_agent.judges import escalation_judge, fast_hallucination, raw_export, relevance_judge, to_conversation

def completeness_judge(conv):
    raise TimeoutError("judge call timed out after 120 s")

JUDGES = {"relevance": relevance_judge, "hallucination": fast_hallucination,
          "completeness": completeness_judge, "escalation": escalation_judge}

def evaluate(conv):
    results, failures = {}, {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(JUDGES)) as pool:
        futures = {name: pool.submit(judge, conv) for name, judge in JUDGES.items()}
        for name, future in futures.items():
            try:
                results[name] = future.result(timeout=120)
            except Exception as error:   # a failed judge is logged, not fatal
                failures[name] = repr(error)
    return results, failures

conv = to_conversation(raw_export(generate_traces()[0]))
results, failures = evaluate(conv)
print(sorted(results))
print(failures)
print(results["relevance"])
```

```text
['escalation', 'hallucination', 'relevance']
{'completeness': "TimeoutError('judge call timed out after 120 s')"}
{'relevance_score': 4, 'has_answer': True}
```

Record the failures as a separate count. A judge that times out on long conversations is biased towards scoring the short ones, and you'll only see that if you keep the denominator.

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

**Consistency override.** After parsing, the code recomputes `grounding_ratio = grounded / total claims` and, if the claim list disagrees with the top-level boolean, flips `hallucination_detected` to match the evidence. Models often write a correct evidence list and a wrong summary flag, and the structured part is the one to trust.

```python
def override(data):
    claims = data.get("evidence", [])
    n_bad = sum(c["status"] == "hallucination" for c in claims)
    # Upstream defaults to 0.0 with no claims; 1.0 is arguably saner, since nothing was unsupported.
    data["grounding_ratio"] = (len(claims) - n_bad) / len(claims) if claims else 1.0
    data["hallucination_detected"] = n_bad > 0
    return data

verdict = {"hallucination_detected": False,   # the summary flag the model wrote
           "evidence": [{"claim": "Credit notes within 90 days", "status": "hallucination"},
                        {"claim": "From the invoice page", "status": "grounded"}]}
print(override(verdict))
```

```text
{'hallucination_detected': True, 'evidence': [{'claim': 'Credit notes within 90 days', 'status': 'hallucination'}, {'claim': 'From the invoice page', 'status': 'grounded'}], 'grounding_ratio': 0.5}
```

---

## Stage 2: verify only what is expensive

The strong model is many times the price of the fast one, so it should only look at what the fast one flagged. Hallucinations are a minority of turns, and false positives are what erodes trust in the report, so a second opinion aimed at exactly those gets the most from its budget. Upstream reports the strong second judge running on about 15% of traffic.

```python
# verification fields upstream: verified, severity_adjustment (none|increase|decrease),
# new_severity, explanation, final_recommendation (approve|reject|review)
from support_agent import generate_traces
from support_agent.judges import fast_hallucination, raw_export, to_conversation, verify_hallucination

trace = next(t for t in generate_traces() if t.seeded_failure == "distorted_claim")
conv = to_conversation(raw_export(trace))
print("Q:", conv.question)
print("A:", conv.answer)
print("Cited:", conv.sources)
first = fast_hallucination(conv)
print("first pass:", first["evidence"])
print("verifier  :", verify_hallucination(conv))
```

```text
Q: How many users are on the Standard plan?
A: The Standard plan includes 10 users. Add users under Settings, then Team.
Cited: ['https://help.acmebooks.example/account/add-user']
first pass: [{'claim': '10', 'status': 'hallucination', 'document_support': 'NOT FOUND'}]
verifier  : {'verified': True, 'type': 'distortion', 'severity': 'critical'}
```

`final_recommendation: review` is worth copying: it routes a disagreement to a human queue instead of guessing.

Now run the whole pipeline over the fortnight and score it against the planted labels, which is the measurement you rarely get in production.

```python
from support_agent import generate_traces
from support_agent.judges import flagged, pipeline_cost, precision_recall, raw_export, run_pipeline, to_conversation

traces = generate_traces()
convs = [to_conversation(raw_export(t)) for t in traces]
results = [run_pipeline(c) for c in convs]

truth = [t.seeded_failure in {"hallucinated_citation", "distorted_claim"} for t in traces]
first_pass = [r["hallucination"]["hallucination_detected"] for r in results]
print("first pass:", precision_recall(first_pass, truth))
print("verified  :", precision_recall([flagged(r) for r in results], truth))
print("verifier ran on", sum("verification" in r for r in results), "of", len(results), "turns")
print({k: round(v, 2) for k, v in pipeline_cost(results).items()})
```

```text
first pass: {'tp': 39, 'fp': 3, 'fn': 3, 'precision': 0.9285714285714286, 'recall': 0.9285714285714286}
verified  : {'tp': 39, 'fp': 3, 'fn': 3, 'precision': 0.9285714285714286, 'recall': 0.9285714285714286}
verifier ran on 42 of 1400 turns
{'fast_usd': 0.76, 'strong_usd': 0.72, 'total_usd': 1.48}
```

The rule-based first pass is already decent on this data, so the verifier doesn't improve the numbers here. Its three false alarms are refund escalations on turns where retrieval went wrong, whose citation points at a policy page that was never retrieved, and a human reviewer might well side with the judge. A real fast model is noisier than a number check, and that's the case verification exists for. The next section shows it. Notice the cost too: the prices are the dated rates in [`pricing.py`](../practice/support_agent/pricing.py), with token counts that are assumptions (900 in and 180 out per fast call, 1,800 and 500 per strong call), so the figures show relative size only.

The turns the pipeline misses deserve as much attention as the ones it finds. This is a number that does appear in the retrieved documents, only not in the cited one.

```python
from support_agent import generate_traces
from support_agent.judges import fast_hallucination, raw_export, to_conversation

traces = generate_traces()
missed = [t for t in traces if t.seeded_failure == "distorted_claim"
          and not fast_hallucination(to_conversation(raw_export(t)))["hallucination_detected"]]
print(len(missed), "distortions passed the first pass")
t = missed[0]
print("A:", t.answer)
for d in t.documents:
    print("  ", d["url"].rsplit("/", 1)[-1], "::", d["text"][:80])
```

```text
3 distortions passed the first pass
A: The default payment term is 30 days. Change it under Invoice settings.
   payment-terms :: The default payment term is 14 days and can be changed under Invoice settings.
   credit-notes :: Issue a credit note from the Invoices page within 30 days of the invoice date.
```

The gate means the second judge never sees these. That's the price of gating on positives: **recall can only go down at the second stage**. Measure it by sending a small random sample of first-pass negatives to the strong judge too. Without that sample, you can't know what you're missing.

---

## Which judge do you trust? Lenient against strict

The upstream project kept two prompt versions and compared them on the same conversations before choosing.

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

We can run the same A/B here. The lenient stance adds one rule: flag anything with low word overlap with the documents. That sounds cautious, and it's what a model told "when in doubt, flag it" tends to do.

```python
import pandas as pd
from support_agent import generate_traces
from support_agent.judges import flagged, pipeline_cost, precision_recall, raw_export, run_pipeline, to_conversation

traces = generate_traces()
convs = [to_conversation(raw_export(t)) for t in traces]
truth = [t.seeded_failure in {"hallucinated_citation", "distorted_claim"} for t in traces]

rows = []
for stance in ["strict", "lenient"]:
    results = [run_pipeline(c, stance) for c in convs]
    first = precision_recall([r["hallucination"]["hallucination_detected"] for r in results], truth)
    final = precision_recall([flagged(r) for r in results], truth)
    rows.append({"stance": stance, "first_precision": round(first["precision"], 3), "first_recall": round(first["recall"], 3),
                 "verifications": sum("verification" in r for r in results), "final_precision": round(final["precision"], 3),
                 "final_recall": round(final["recall"], 3), "cost_usd": round(pipeline_cost(results)["total_usd"], 2)})
print(pd.DataFrame(rows).to_string(index=False))

lenient = [run_pipeline(c, "lenient") for c in convs]
false_alarms = [t for t, r, y in zip(traces, lenient, truth) if r["hallucination"]["hallucination_detected"] and not y]
print("lenient false alarms by language:", pd.Series([t.language for t in false_alarms]).value_counts().to_dict())
```

```text
 stance  first_precision  first_recall  verifications  final_precision  final_recall  cost_usd
 strict            0.929         0.929             42            0.929         0.929      1.48
lenient            0.086         0.929            454            0.929         0.929      8.56
lenient false alarms by language: {'da': 389, 'en': 26}
```

The lenient judge arrives at the same final answer at about six times the cost, because the verifier cleans up after it. Without the verifier its precision would make the report useless. Almost all the false alarms are Danish turns, whose answers share few words with English help articles. That's the general lesson: a judge's false alarm rate is rarely uniform, and an A/B on an aggregate would miss where it fails. If you change the judge, you also change the trend line, so A/B the judge prompt before you trust a month-on-month chart.

---

## What the pipeline found

The table the team needed in October: flagged turns by route and release, split into what each one would have you fix.

```python
import pandas as pd
from support_agent import generate_traces
from support_agent.judges import flagged, raw_export, run_pipeline, to_conversation

traces = generate_traces()
rows = []
for t in traces:
    r = run_pipeline(to_conversation(raw_export(t)))
    rows.append({"release": t.release, "route": t.route,
                 "generation_bug": flagged(r) and r["relevance"]["has_answer"],
                 "retrieval_bug": not r["relevance"]["has_answer"],
                 "escalation_bug": r["escalation"]["should_have_escalated"] and not r["escalation"]["escalation_appropriate"]})
df = pd.DataFrame(rows)
print((df.pivot_table(index="route", columns="release", values="generation_bug", aggfunc="mean") * 100).round(1).to_string())
print()
print((df.groupby("release")[["generation_bug", "retrieval_bug", "escalation_bug"]].mean() * 100).round(1).to_string())
```

```text
release     v1  v2.0  v2.1
route
account    1.4   2.4   0.0
billing    1.6   7.6  12.5
refund     0.0   7.8   3.2
technical  1.8   0.0   6.1

         generation_bug  retrieval_bug  escalation_bug
release
v1                  1.3            5.6             0.4
v2.0                4.7            5.0             1.3
v2.1                6.5            8.0             2.5
```

Billing's generation failures rose after `v2.0` and did not recover in `v2.1`, the release everyone took as the fix. Its golden category went up by a point over the same change. The bill recovered on 17 October, and the answers didn't. Only a check over production could have said so, and this is what this pipeline is for.

The same figures carry a warning for small routes. Each cell rests on a few hundred turns or fewer, so a difference of a couple of points between cells may be chance, and the release-over-release jump on billing is what's worth acting on.

---

## With real models

A real implementation of the two tiers on Claude looks like this. Haiku 5.5 runs the first pass on every turn, and Opus 5.5 verifies the flagged ones. It needs an `ANTHROPIC_API_KEY`. Here it runs against a local fake that enforces the API's request rules, so it tests the call's shape and the control flow but not judgement.

```python
# illustrative: needs ANTHROPIC_API_KEY (runs here against a local fake)
import json
import anthropic

client = anthropic.Anthropic()
EVIDENCE = {"type": "object", "additionalProperties": False, "required": ["hallucination_detected", "evidence"],
            "properties": {"hallucination_detected": {"type": "boolean"},
                           "evidence": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                        "required": ["claim", "status", "document_support"],
                                        "properties": {"claim": {"type": "string"},
                                                       "status": {"type": "string", "enum": ["grounded", "hallucination"]},
                                                       "document_support": {"type": "string"}}}}}}
FIRST_PASS = """List each factual claim in the answer, and quote the document that supports it, or write NOT FOUND.
Not a hallucination: clarifying questions, "I don't have this information", greetings, restating the question."""
VERIFY = FIRST_PASS + "\nA first-pass reviewer flagged this answer. Check each flagged claim against the cited documents only."

def judge(model, system, conv_text, effort=None):
    config = {"format": {"type": "json_schema", "schema": EVIDENCE}}
    if effort:
        config["effort"] = effort
    response = client.messages.create(model=model, max_tokens=4000, output_config=config,
                                      # A cached system prompt keeps a weekly run cheap.
                                      system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
                                      messages=[{"role": "user", "content": conv_text}])
    if response.stop_reason != "end_turn":
        return None  # refused or cut off: count as unjudged, not as clean
    return json.loads(next(b.text for b in response.content if b.type == "text"))

conv_text = "Question: How long is a reset link valid?\nAnswer: 60 minutes.\nDocuments: Reset links last 60 minutes."
first = judge("claude-haiku-5-5", FIRST_PASS, conv_text)
if first and first["hallucination_detected"]:
    second = judge("claude-opus-5-5", VERIFY, conv_text, effort="high")
assert first is not None and "evidence" in first
```

Three notes on using this in earnest. The upstream `temperature: 0.1` has no equivalent on Opus 5.5, whose API rejects sampling parameters, so stability has to come from the fixed procedure in the rubric. A weekly job has no user waiting, so send it through the Batches API at 50% off input and output, which stacks with cache discounts. And for the strong judge you may want server-side fallback (`client.beta.messages.create(betas=["server-side-fallback-2026-07-01"], fallbacks="default", ...)`), though it isn't accepted on batches, so choose one per job.

---

## Base classes and config

The upstream shape separates the model provider from the judge, so that each judge is only a prompt and a parser, and a failure comes back as a value rather than an exception.

```python
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class EvaluationResult:
    success: bool
    data: dict | None = None
    error: str | None = None

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt, model): ...

    def generate_json(self, prompt, model):
        text = self.generate(prompt, model).strip()
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```")
        return json.loads(text)

class BaseAgent(ABC):
    def __init__(self, llm, model):
        self.llm, self.model = llm, model

    @abstractmethod
    def get_prompt(self, **kw): ...

    def parse_response(self, data):
        return EvaluationResult(success=True, data=data)

    def evaluate(self, **kw):
        try:
            return self.parse_response(self.llm.generate_json(self.get_prompt(**kw), self.model))
        except Exception as e:
            return EvaluationResult(success=False, error=str(e))

class FencedProvider(BaseLLMProvider):
    def generate(self, prompt, model):
        return '```json\n{"has_answer": true}\n```' if "credit" in prompt else "Sorry, I can't return JSON."

class RelevanceAgent(BaseAgent):
    def get_prompt(self, question):
        return f"Do the documents answer: {question}"

agent = RelevanceAgent(FencedProvider(), "stub")
print(agent.evaluate(question="How long for a credit note?"))
print(agent.evaluate(question="What is the VAT rate?").success)
```

```text
EvaluationResult(success=True, data={'has_answer': True}, error=None)
False
```

Fence stripping is a workaround for text output. With structured output, as in the previous section, you don't need it.

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

The upstream project stops at a DataFrame. To make the results visible next to the traces, write them back as scores, and send the disagreements to people. Because the pipeline computes the trace id from the same seed as the agent did ([chapter 1](01-tracing-with-langfuse.md)), it needs no lookup.

```python
from langfuse import Langfuse
from support_agent import generate_traces
from support_agent.fakes import offline_langfuse
from support_agent.judges import raw_export, run_pipeline, to_conversation

lf, capture = offline_langfuse()
queue = lf.api.annotation_queues.create_queue(name="grounding-disagreements", score_config_ids=[])
queued = 0
for t in generate_traces():
    r = run_pipeline(to_conversation(raw_export(t)))
    trace_id = Langfuse.create_trace_id(seed=t.trace_id)
    lf.create_score(trace_id=trace_id, name="retrieval_relevance", value=r["relevance"]["relevance_score"], data_type="NUMERIC")
    if "verification" in r:
        verdict = r["verification"]
        lf.create_score(trace_id=trace_id, name="hallucination", value=int(verdict["verified"]), data_type="BOOLEAN",
                        comment=f"{verdict['type']}, {verdict['severity']}")
        # A person confirms critical findings, and decides when the two judges disagree.
        if verdict["severity"] == "critical" or not verdict["verified"]:
            lf.api.annotation_queues.create_queue_item(queue.id, object_id=trace_id, object_type="TRACE")
            queued += 1
lf.flush()
print("scores written:", len(capture.api.scores))
print("sent to a person:", queued)
```

```text
scores written: 1442
sent to a person: 42
```

That closes the circle from chapter 1: a person's label on a flagged turn becomes a regression fixture, and the golden set gets a question it was missing. Include the judge's version in the score `comment` or metadata, so a later change of judge isn't mistaken for a change in the product.

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

## Pitfalls

| Pitfall | What happens | Instead |
|---|---|---|
| A parser that handles only the current shape | Coverage falls silently after a release, and the failure rate seems to fall with it | Use fallback paths, and report the share of rows parsed |
| Gating with no audit of the negatives | Second-stage recall loses what the first stage missed, and you can't see it | Send a random sample of negatives to the strong judge |
| Treating a lenient judge's rate as a metric | Most of its flags may be one segment's false alarms | Measure precision per segment, including language |
| Dropping failed or refused judge calls | Long or difficult turns fall out of the denominator | Record unjudged counts next to the results |
| Comparing months across a judge change | The change in the judge looks like a change in the product | Keep the judge version on the score, and rerun old data when it changes |
| Reading a verdict flag while the evidence disagrees | The summary and the list contradict each other | Recompute the verdict from the evidence |

---

## Try it

1. Extend the pipeline with a `completeness_judge` that flags answers with no number when the top document contains one. On which seeded failures does it fire, and what does it find that the others don't?

   <details><summary>Answer</summary>

   With that rule it fires on 38 turns, of which 35 have no planted failure and 3 are `retrieval_miss` or `wrong_route`. So in this data it mostly finds answers that are merely short, and you'd have to read a sample to find out whether any are real omissions. That's a useful finding in itself: a new judge should earn its cost by catching something the others don't.

   </details>

2. The strict gate never verifies its negatives. Sample 5% of them at random and run `verify_hallucination`, then estimate how many distortions the first pass misses. Is the verifier able to catch them?

   <details><summary>Answer</summary>

   Yes, for those it sees: `verify_hallucination` reads only the cited documents, so the number that appears in another document no longer rescues the answer. A 5% sample of about 1,360 negatives costs 68 strong calls and on average surfaces far less than one of the three missed turns. So one sample tells you little, and you need to accumulate them across weeks to size a rare miss.

   </details>

3. Estimate the cost of the strict run through the Batches API, using `pipeline_cost` and the 50% discount, and compare it with the upstream figure of about $3.70 per 1,000 conversations. Why shouldn't you compare them directly?

   <details><summary>Answer</summary>

   The strict run costs about $1.48 for 1,400 turns, so about $0.53 per 1,000 after halving. But the token counts here are assumptions, the upstream run used different models, and it ran its strong model on every turn. The comparison shows only that the design choices can move the bill several times over.

   </details>

---

## Interview checklist

| Question | A good answer |
|---|---|
| Why several judges and not one? | Each failure has a different fix. A wrong answer from irrelevant documents is a retrieval bug, and from relevant documents a generation bug. One score can't separate them |
| What does gating verification on positives cost? | It lowers cost, but recall can only fall at the second stage. Sample the negatives to measure what is lost |
| Why make the judge list evidence first? | Models often write a right list and a wrong flag. Recompute the verdict from the list |
| How do you decide between a lenient and a strict judge? | Run both over the same turns, and compare precision, recall and cost per segment. A lenient judge's false alarms often concentrate in one language or route |
| What breaks a trend line of judge scores? | A change to the judge, and schema drift in the export. Keep the judge version on the score and report parse coverage |
| How do you run this cheaply on Claude? | A small model on every turn, a stronger one only on flagged turns, a cached system prompt, and the Batches API at 50% off since nobody is waiting |
| Why not record a refused judge reply as a zero? | It would turn the judge's failure into a false finding about the product. Count unjudged turns separately |

---

## Next

→ [04-langfuse-mcp-server.md](04-langfuse-mcp-server.md): instead of exporting traces to a pipeline, let an agent query Langfuse directly through MCP.
