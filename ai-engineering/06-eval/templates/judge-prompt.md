# Judge Prompt — `<criterion name>`

> One criterion per judge. Binary verdict. Reasoning before verdict. See [notes/05](../notes/05-llm-as-judge.md#writing-the-judge-prompt).

**Judge version:** `<criterion>-v1` · **Judge model:** `<pinned model ID, different family from the SUT>` · **State:** experimental | calibrated

---

```text
You are reviewing a response written by a customer-support assistant. Your job is to check
one thing only: <CRITERION, one sentence>.

## Definitions
PASS: <precise condition, e.g. "every specific fact (menu path, number, date, price) in the
response appears in the SOURCES">.
FAIL: <precise condition, e.g. "any specific fact is absent from or contradicts the SOURCES">.
Ignore everything else: length, tone and formatting do not affect this verdict.
CANNOT_GRADE: the SOURCES are empty, or the question is outside <domain>.

## Examples
<example>
<question>…</question>
<sources>…</sources>
<response>…</response>
<critique>…</critique>
<verdict>PASS</verdict>
</example>

<example>   <!-- tricky FAIL: looks right, one invented detail -->
…
<verdict>FAIL</verdict>
</example>

<example>   <!-- short but correct: guards against verbosity bias -->
…
<verdict>PASS</verdict>
</example>

## Task
<question>{{question}}</question>
<sources>{{retrieved_context_text}}</sources>
<response>{{response}}</response>

First write a short critique in <critique> tags: list each relevant claim and whether it
meets the PASS definition. Then give your verdict in <verdict> tags: PASS, FAIL or
CANNOT_GRADE.
```

---

## Notes for the author

- Few-shot examples come from the **train** split of your human labels, never dev or test.
- Include at least one tricky FAIL near the boundary and one short correct PASS.
- Parse `<verdict>` strictly. Anything else counts as a grader error, not a FAIL.
- For pairwise variants, run both orders and count a win only if it holds in both.
- Changing this prompt resets the state to **experimental** until re-calibrated ([judge-calibration.md](judge-calibration.md)).
