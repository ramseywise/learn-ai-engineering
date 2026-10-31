# Lab 2 — A three-layer trajectory verifier

> Adapted from Bojie Li, *AI Agents in Depth*, Experiment 9-1 ([upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/trajectory-verifier), Apache-2.0). The README and sample data have been translated to English. Concepts: [note 08 — Verify before you learn](../../notes/08-self-improving-loops.md#verify-before-you-learn).

The lab turns a customer-service trajectory into a structured diagnosis that a later evolve step can learn from. User satisfaction is not used as the signal, and neither is a single overall score. The verifier checks three layers in order, and every failing dimension keeps the turns that prove it:

| Layer | Question | Judged by |
|---|---|---|
| Outcome | Was the task actually completed? | Final order state (code) |
| Process | Was it done in an allowed way? This covers rules, privacy, factual support and promise–action consistency. | Action log and policy rules (code) |
| Quality | Was it handled well? This covers expression quality and compliant alternatives. | A rubric judge (heuristic or LLM) |

`verifier.py` implements the three layers. The quality layer uses the deterministic `HeuristicQualityJudge` by default, so no API key is needed. `llm_judge.py` is a real LLM judge behind the same `QualityJudge` interface. The outcome and process layers always use environment ground truth and code rules, never the model.

`sample_trajectories.json` holds four expert-labelled trajectories:

- a normal refund;
- a false promise ("I have completed your refund", with no tool call);
- a privacy and policy violation;
- an over-refusal that ignores the user's rebooking alternative.

`calibration.py` reports per-dimension precision, recall and agreement with the expert labels. `demo.py` contrasts a single overall score with the multi-dimension diagnosis.

## Run

```bash
python demo.py
python -m unittest -v test_verifier.py
```

That is the deterministic calibration path. To have a real LLM judge expression quality and compliant flexibility:

```bash
pip install -r requirements.txt
cp env.example .env
export OPENAI_API_KEY=your_api_key_here
python demo.py --judge llm --model gpt-5.6
```

In LLM mode the model must return, for each dimension, a verdict, the evidence turns and a confidence score, all in the same schema. Code still decides the outcome and process layers. This mode costs real API money, and its output can change with the model version. Keep checking each dimension against the expert labels; don't watch only the total.

## What to notice

- The overall score hides what went wrong. The false promise and the privacy leak both score 0.571, yet they need entirely different fixes: a harness consistency check for the first, an identity gate and output redaction for the second. The over-refusal scores 0.714 and lands in `review_or_accept`. Only the per-dimension failures say what to change.
- `quality_facts` in the sample data spells out what an LLM judge would infer, which keeps the offline demo reproducible. A production system does not get these fields in advance.
- A real system would grow the expert calibration set. It would also send low-confidence or high-risk trajectories to a second verifier or a human, rather than letting them become learning signals automatically.
