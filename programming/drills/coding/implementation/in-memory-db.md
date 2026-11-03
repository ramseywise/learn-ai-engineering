---
title: "In-memory database"
track: coding
topic: implementation
difficulty: hard
timebox_min: 40
concepts: [implementation]
source: https://leetcode.com/discuss/interview-question/949850/in-memory-sql-like-database-ood-machine-coding/
---
## Prompt

Design an in-memory SQL-like database (cf. LeetCode 2408, "Design SQL"). Support
creating tables with a fixed number of columns, inserting rows with auto-increment
ids, deleting rows by id, selecting a single cell, and exporting a table as CSV.
Then extend it under follow-ups (filtering, indexing).

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Store rows in a dict keyed by id, not a list. The spec requires ids to auto-increment forever. Deleting a row must not reuse or shift ids.

</details>

<details><summary>Hint 2</summary>

The id counter increments on every insert and is never rolled back by a delete. A dict keyed by id keeps delete and select-cell O(1) and ids stable.

</details>

<details><summary>Hint 3</summary>

For CSV export, iterate rows in id order. For fast WHERE lookups under follow-ups, add a secondary index (column value -> set of ids) maintained on insert/delete.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

A machine-coding / multi-level OOP round: they judge data-model choices and how cleanly you extend, not clever algorithms. Model each table as an object holding its column count, a rows container, and a next-id counter. The spec detail people miss: ids auto-increment and never reuse. Deleting a row doesn't decrement the counter, and the next insert still gets last_id + 1 even if that row was deleted. So store rows in a dict keyed by id (not a list), which makes delete O(1) and keeps ids stable and sparse. Keep a top-level dict of table_name -> Table. Validate inputs (right number of columns, table exists, 1-based column index) and decide error behavior explicitly. Talk through the model before coding. Clarify whether column types/names matter or columns are positional.

**L1 — schema + insert with auto-increment** — create_table(name, n_columns) makes a Table with rows = {} and next_id = 1. insert_row(name, values) asserts len(values) == n_columns, stores rows[next_id] = values, then increments next_id. The counter increments on every insert regardless of later deletes — that stable, monotonic id is the property the problem is really testing.

**L2 — delete + select cell** — delete_row(name, id) pops the id from the dict (O(1)); next_id is untouched, so ids never get reused. select_cell(name, id, column) returns `rows[id][column-1]` (columns are 1-indexed in the problem). Using a dict keyed by id makes both O(1) and correct after arbitrary deletes, where a plain list would misalign indices.

**L3 — CSV export + query extensions** — export_csv(name) iterates rows in id order, joining each row's cells, optionally with a header. For richer follow-ups: filtering (WHERE) is a linear scan with a predicate; to make repeated equality lookups fast, add a secondary index — a dict column_value -> set(ids) maintained on insert/delete — which is exactly how a real DB index turns an O(n) scan into O(1). Order-by is a sort of the selected ids.

**Complexity** — time O(1) insert/delete/select-cell; O(n) export or full-table scan; O(1) indexed equality lookup; space O(rows * columns), plus O(rows) per secondary index

</details>

## Notes

Follow-ups an interviewer may push on:

- How would you add WHERE filtering, and when is a full scan acceptable vs. needing an index?
- How do you keep a secondary index consistent across inserts and deletes?
- How would you support a simple JOIN between two tables?
- How would you add transactions with rollback?
- What changes if a single table grows too large to hold in memory?

Sources:

- [Hello Interview — LeetCode 2408 Design SQL](https://www.hellointerview.com/community/questions/design-sql-2408/cm5eguhah03va838ozuanzsde)
- [algo.monster — 2408. Design SQL In-Depth Explanation](https://algo.monster/liteproblems/2408)
- [LeetCode Discuss — In-memory SQL-like Database (OOD / Machine Coding)](https://leetcode.com/discuss/interview-question/949850/in-memory-sql-like-database-ood-machine-coding/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/aieng-in-memory-db.yaml`.
