# Conventions & Tunables

## Example 1: Hardcoded tunable in agent logic (the SANYI BN-1 pattern)

Based on the real SANYI drill from the librarian wiki.

**The diff**
```python
# src/agents/rag_agent/confidence.py
         if self.crag_delta is None:
             return True
+        if self.ensemble_top_score < 0.42:
+            return False
         return self.crag_delta >= min_improvement
```

**Surface read**: Two lines. Type-checks, lints clean, tests pass. Behavior is sensible — stop CRAG iteration on hopeless retrieval scores.

**Model review**

> **[Info / BN-1]** `confidence.py:3` — `0.42` is a policy threshold living in business logic. The file's own convention ten lines up is env-driven module constants (`_SCORE_DELTA_MIN = float(os.getenv(...))`). This threshold now requires a code change to adjust.
>
> Fix is mechanical — hoist to a named, env-overridable constant:
> ```python
> _HOPELESS_SCORE_THRESHOLD = float(os.getenv("CRAG_HOPELESS_THRESHOLD", "0.42"))
> ```
>
> **[Notice / UN-1]** — `confidence.py` matched no entry in the contract registry. The layer decision for the confidence router was never made.

**What this teaches**: The canonical code review drill. Line-by-line reading approves it; convention-diffing catches it. Severity is info (not blocker) because the behavior is correct — it's the *changeability* that's wrong. See the [Code Review Drill — SANYI](../sources.md) wiki page for the full walkthrough.

---

## Example 2: Prompt hardcoded in agent code instead of config

**The diff**
```python
# agents/summarizer.py
  class SummarizerAgent:
      def __init__(self, llm: LLM):
          self.llm = llm
+         self.system_prompt = """You are a summarization expert. Follow these rules:
+ 1. Always output exactly 3 bullet points
+ 2. Never include numbers or statistics
+ 3. Keep each bullet under 20 words
+ 4. Use present tense only"""

      async def summarize(self, text: str) -> str:
-         return await self.llm.generate(
-             system=load_prompt("summarizer_system"),
-             messages=[{"role": "user", "content": text}],
-         )
+         return await self.llm.generate(
+             system=self.system_prompt,
+             messages=[{"role": "user", "content": text}],
+         )
```

**Surface read**: Prompt moved inline. Clearer to read — no need to look up a separate file.

**Model review**

> **[Warning]** `summarizer.py:5-8` — The system prompt was moved from `load_prompt("summarizer_system")` (configurable, swappable, versionable) into a hardcoded class attribute. This means:
> - Changing the prompt requires a code change, review, and deploy
> - A/B testing prompt variants now requires code branches, not config changes
> - The prompt can't be overridden per-environment (staging might need different behavior)
> - Prompt version history is now buried in git diffs instead of a dedicated prompt registry
>
> The original `load_prompt()` pattern was correct — prompts are Bianyi (ever-changing tunables that should be modifiable without deploy).
>
> **[Info]** `summarizer.py:6` — "Never include numbers or statistics" is a policy decision embedded in code with no documentation. Is this a product requirement? If the business need changes, someone will have to find this buried in agent source code.

**What this teaches**: Prompts are the quintessential Bianyi component — they change constantly during development and tuning. Hardcoding them in application code is the AI engineering equivalent of hardcoding a config value. The convention is to keep them in a loadable/swappable layer. See SANYI Bianyi layer; [agents guide §4](../../../guides/4-agents/interview-guide.md) on harness engineering — "prompt strings are tunables, not code."

---

## Example 3: Eval threshold changed without updating documentation or alerts

**The diff**
```python
# evals/graders.py
  class QualityGrader:
-     PASS_THRESHOLD = 0.7
+     PASS_THRESHOLD = 0.4
      RUBRIC_VERSION = "v2.1"

      def grade(self, response: str, reference: str) -> GradeResult:
          score = self.compute_similarity(response, reference)
          return GradeResult(
              passed=score >= self.PASS_THRESHOLD,
              score=score,
          )
```

**Surface read**: Threshold adjusted. Single constant change.

**Model review**

> **[Warning]** `graders.py:2` — Pass threshold dropped from 0.7 to 0.4 — nearly halved. This changes what the eval system considers "good enough." Questions:
> - Was this calibrated against human-labeled examples, or is it vibes-based?
> - Does the alerting/monitoring system reference this threshold? A 0.4 pass rate will look healthy under old 0.7-based dashboards.
> - Is this meant to be temporary (relaxed during development) or permanent?
>
> **[Info]** — `RUBRIC_VERSION` is still `"v2.1"`. If the threshold change reflects a meaningful change in what "passing" means, the rubric version should be bumped so historical comparisons are valid.
>
> **[Info]** — Like example 1, this threshold should probably be env-configurable. Different environments (dev vs staging vs prod) may need different pass criteria.

**What this teaches**: Eval thresholds are high-consequence tunables in AI systems. Lowering a quality bar looks like a one-line change but affects what ships. The right review question isn't "is 0.4 correct?" but "how was 0.4 chosen, and what else depends on this number?" See [evals guide §2-3](../../../guides/6-evals-observability/interview-guide.md) on grader calibration.
