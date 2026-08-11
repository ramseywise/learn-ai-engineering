# Worked Example: Transaction Aggregation & Anomaly Detection (35 min, offline)

> **Constraint note:** pure stdlib — no pandas. If pandas is available, say what you'd do with it (`groupby().agg()`) and then ask whether they want it; some graders specifically want to see the stdlib version because it shows you know what `groupby` is doing.

**Format:** 35 min, browser editor.
**Prompt:** *"Given a list of transaction records, compute per-user monthly totals, flag anomalous transactions, and return a summary. Some records are malformed."*

This is the conventional-Python end of an AIE loop, and it pairs with the **OLTP vs OLAP / SQL-vs-RAG** MCQs. The hidden question is whether you know that *this* problem — aggregation over structured records — is a SQL problem, and that routing it through a vector store would be an architectural error. Say so.

---

## 0–4 min — clarify and frame

[NARRATE: "Three questions. What defines anomalous — is there a rule, or should I pick one? Should malformed records be skipped or should the whole batch fail? And is this in-memory batch, or a stream I can't hold at once?"]

Typical: pick a reasonable rule, skip-and-report, fits in memory.

Then the framing sentence that earns the round:

[NARRATE: "One architectural note before I start — this is structured aggregation over records with a fixed schema, so in production this is a `GROUP BY` in the warehouse, not something you'd put through an LLM or a vector store. Embeddings are for semantic similarity over unstructured text; asking a retrieval system to sum a column is both more expensive and less correct than SQL. I'm implementing it in Python because that's the exercise, but I'd push this to the database given the choice."]

That is precisely the SQL-vs-RAG discrimination the MCQ bank tests, delivered unprompted.

---

## 4–12 min — parse defensively

Malformed records are stated in the prompt, which means the validation path *is* the exercise.

```python
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import logging

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Transaction:
    user_id: str
    amount: Decimal
    timestamp: datetime

    @property
    def month(self) -> str:
        return self.timestamp.strftime("%Y-%m")


def parse(record: dict) -> Transaction | None:
    """Parse one record; return None if malformed.

    Returns rather than raises: one bad record in a batch of 10,000 should not
    abort the run. The caller counts rejections.
    """
    try:
        amount = Decimal(str(record["amount"]))
    except (KeyError, InvalidOperation, TypeError):
        log.warning("bad amount: %r", record.get("amount"))
        return None

    if not amount.is_finite():
        log.warning("non-finite amount: %r", amount)
        return None

    try:
        ts = datetime.fromisoformat(record["timestamp"])
    except (KeyError, ValueError, TypeError):
        log.warning("bad timestamp: %r", record.get("timestamp"))
        return None

    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)      # assume UTC, don't silently compare naive

    user_id = record.get("user_id")
    if not isinstance(user_id, str) or not user_id:
        log.warning("bad user_id: %r", user_id)
        return None

    return Transaction(user_id=user_id, amount=amount, timestamp=ts)
```

[NARRATE: "Two choices worth flagging. `Decimal`, not float — this is money, and float addition on currency accumulates representation error; 0.1 + 0.2 isn't 0.3 and in a financial context that eventually shows up in a reconciliation report. And I'm normalizing naive timestamps to UTC explicitly rather than letting them through, because comparing a naive datetime with an aware one raises, and mixing them silently produces wrong month boundaries."]

Those are two of the highest-signal details available in this problem and each costs one line. Interviewers for finance-adjacent roles listen specifically for `Decimal`.

---

## 12–22 min — aggregate

```python
def aggregate(records: list[dict]) -> tuple[dict[tuple[str, str], Decimal], int]:
    """Sum amounts per (user_id, month). Returns totals and a rejection count."""
    totals: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    rejected = 0

    for record in records:
        txn = parse(record)
        if txn is None:
            rejected += 1
            continue
        totals[(txn.user_id, txn.month)] += txn.amount

    return dict(totals), rejected
```

[NARRATE: "`defaultdict(Decimal)` gives a zero default, so there's no key-existence check in the loop. And I'm returning the rejection count alongside the totals rather than just logging it — if 4,000 of 10,000 records failed to parse, the totals are meaningless and the caller has to be able to know that. Silently returning a partial sum that looks plausible is the dangerous outcome here."]

That is the ETL instinct the existing `questions.md` #4 describes, applied concretely.

**On the pandas question, if it comes up:**

[NARRATE: "With pandas this is `df.groupby(['user_id', df.timestamp.dt.to_period('M')]).amount.sum()`. I'd want `errors='coerce'` on the numeric conversion and then an explicit count of the resulting NaNs, because the failure mode of the pandas version is that coercion turns bad records into NaN and they vanish from the sum without anyone noticing."]

---

## 22–30 min — anomaly detection

Pick a rule, state its weakness before being asked.

```python
def flag_anomalies(
    txns: list[Transaction], threshold: Decimal = Decimal("3")
) -> list[tuple[Transaction, str]]:
    """Flag transactions more than `threshold` MADs from that user's median.

    Median absolute deviation rather than standard deviation: with a handful of
    transactions per user, one large outlier inflates the standard deviation
    enough to mask itself. MAD is resistant to that.
    """
    by_user: dict[str, list[Transaction]] = defaultdict(list)
    for t in txns:
        by_user[t.user_id].append(t)

    flagged = []
    for user_id, user_txns in by_user.items():
        if len(user_txns) < MIN_HISTORY:
            continue                       # not enough history to judge
        amounts = sorted(t.amount for t in user_txns)
        med = _median(amounts)
        mad = _median(sorted(abs(a - med) for a in amounts))
        if mad == 0:
            continue                       # all identical — no dispersion to measure
        for t in user_txns:
            if abs(t.amount - med) / mad > threshold:
                flagged.append((t, f"{abs(t.amount - med) / mad:.1f} MADs from median {med}"))
    return flagged


def _median(sorted_vals: list[Decimal]) -> Decimal:
    n = len(sorted_vals)
    mid = n // 2
    return sorted_vals[mid] if n % 2 else (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
```

[NARRATE: "I'm using median absolute deviation rather than standard deviation deliberately. With ten transactions and one fraudulent charge, that charge drags the mean toward itself and inflates the standard deviation — so the outlier partly hides in the statistic meant to catch it. MAD uses medians throughout, so a single extreme value barely moves it."]

[NARRATE: "Two guards worth naming. `MIN_HISTORY` because flagging a user's second-ever transaction as anomalous is just noise. And the `mad == 0` check because identical amounts give zero dispersion, and without that guard this divides by zero — that's the bug I'd expect in a first draft."]

[NARRATE: "The honest weakness: this is per-user and purely amount-based, so it won't catch a novel-merchant pattern, a velocity attack of many small charges, or anything seasonal. A real system would add velocity features and time-of-day. I'm picking the rule I can defend in the timebox."]

Naming the limitation before being asked converts a simple heuristic into evidence of judgment.

---

## 30–35 min — summarize and close

```python
def summarize(records: list[dict]) -> dict:
    totals, rejected = aggregate(records)
    txns = [t for t in (parse(r) for r in records) if t is not None]
    anomalies = flag_anomalies(txns)
    return {
        "users": len({u for u, _ in totals}),
        "months": len({m for _, m in totals}),
        "total_volume": sum(totals.values(), Decimal(0)),
        "rejected_records": rejected,
        "anomaly_count": len(anomalies),
    }
```

[NARRATE: "One inefficiency I want to flag rather than hide: I'm parsing twice, once in aggregate and once here. At a few thousand records that's irrelevant, but I'd restructure to parse once into a list and pass it to both functions if this were hot. I'm leaving it because the clearer structure is worth more right now than the constant factor — but I'd rather say that than have you assume I didn't see it."]

Naming a known-suboptimal choice with its justification is far stronger than either hiding it or prematurely optimizing.

[NARRATE: "Next steps: push the aggregation into SQL where it belongs, add velocity features to the anomaly rule, and emit rejected records to a dead-letter file with the reason attached rather than only counting them — a count tells you something broke, the records tell you what."]

---

## What the interviewer is grading

| Signal | Where it appeared |
|---|---|
| Knows where this belongs | Named it a `GROUP BY` problem, not a RAG problem, unprompted |
| Money handling | `Decimal` over float, with the reconciliation-error reason |
| Time handling | Naive timestamps normalized to UTC explicitly, not silently compared |
| Batch resilience | Bad records skipped and *counted*, not fatal, not silent |
| Statistical judgment | MAD over stddev, with the masking explanation |
| Guards the first draft misses | `MIN_HISTORY`, `mad == 0` divide-by-zero |
| Honest about limits | Named the anomaly rule's blind spots and the double-parse before being asked |

The weakest version uses floats for currency, lets a malformed record raise and kill the batch, flags on mean ± 3σ without noticing the outlier inflates σ, and divides by zero on a user whose transactions are all the same amount.
