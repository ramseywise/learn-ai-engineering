# Gate Contract — `<suite name>`

> Generic version of the case study's [gate contract](../notes/case-study/gate-contract.md). One section per gate, in pipeline order. See [notes/10](../notes/10-evals-in-ci.md#the-gate-ladder).

**Suite:** `<name>` · **Dataset version:** `vN` · **Baseline:** `<run ID / release>` · **Owner:** `<name>`

---

## Row pools

| Pool | Definition | Produced by gate |
|---|---|---|
| `all` | Every row in the dataset | — |
| `<stage>_eligible` | | |
| `quality_sample` | Deterministic sample of `<pool>`, max `N` rows, seed `S` | — |

Rule: a gate scores only its own pool. Ineligible rows are reported as a diagnostic slice, never silently scored.

---

## Gate: `<name>` (repeat per gate)

| Field | Value |
|---|---|
| Runs on pool | |
| Graders (name · version · state) | `<grader> · v1 · heuristic` |
| Metrics | |
| **Fails when** (absolute) | e.g. `schema_valid < 0.99` |
| **Fails when** (vs baseline) | e.g. upper bound of paired Δ grounding < −0.03 |
| **Fails when** (per slice) | e.g. any slice with n ≥ 20 drops > 10 points |
| Efficiency budget | cost per success ≤ 1.2 × baseline; p95 latency ≤ `__` s |
| Blocks | merge / release / nothing (alert only) |

**Emits:**

```json
{
  "gate": "<name>",
  "passed": true,
  "metrics": {"<metric>": {"value": 0.0, "ci": [0.0, 0.0], "baseline": 0.0}},
  "rows_scored": 0,
  "rows_ineligible": 0,
  "infra_errors": 0,
  "top_failure_labels": {},
  "worst_slices": [],
  "next_action": ""
}
```

---

## Gate order

```
data_quality → <stage> → <stage> → grader_calibration → release
```

## Grader calibration gate

- [ ] Every grader used by a blocking gate is `heuristic` or `calibrated`
- [ ] Every calibrated judge has a sheet ([judge-calibration.md](judge-calibration.md)) newer than its last prompt / model change

## Changing this contract

Threshold or pool changes need: a reason, the criteria owner's sign-off, and a re-run of the baseline under the new contract.
