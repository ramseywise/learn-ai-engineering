# Grader Interface Contract

The grader interface is documented in the canonical source: **`evals/graders/README.md`**

That file covers:
- `BaseGrader` abstract class and `grade()` signature
- `GraderOutput` schema (`score`, `is_correct`, `reasoning`, `dimensions`, `labels`)
- Registry (`get_graders_for_tier`, `TierName`)
- How to add a new grader
- Tier definitions (`heuristic`, `calibrated`, `experimental`)
