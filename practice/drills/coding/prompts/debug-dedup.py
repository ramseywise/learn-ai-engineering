"""Broken deduplication script — debugging, 20-25 min.

PROMPT
    "This script should deduplicate records by ID, but the output still
    contains duplicates. Fix it."

BUG REPORT
    "The first run produces correct output. The second run produces an
    empty output."

Do not start by reading the code top to bottom. Reproduce first with a
minimal input you control, state your hypothesis, then check it.

Run this file to see the failure.
"""

import json


def load_records(path):
    with open(path) as f:
        return json.load(f)


def dedup(records, seen=set()):
    result = []
    for r in records:
        if r["id"] not in seen:
            seen.add(r["id"])
            result.append(r)
    return result


def save_records(records, path):
    with open(path, "w") as f:
        json.dump(records, f)


if __name__ == "__main__":
    # Minimal reproducer -- no files needed.
    batch1 = [{"id": 1, "val": "a"}, {"id": 2, "val": "b"}, {"id": 1, "val": "c"}]
    batch2 = [{"id": 3, "val": "d"}]

    print("Run 1:", dedup(batch1))
    print("Run 2:", dedup(batch2))

    # This is what the caller expects. It currently fails -- that is the bug.
    assert dedup([{"id": 3, "val": "d"}]) == [{"id": 3, "val": "d"}], "run 2 lost records"
    print("smoke test passed")

    # your regression test here -- it should fail before your fix and pass after
