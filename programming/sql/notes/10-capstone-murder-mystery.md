---
origin: curated
sources:
  - "Knight Lab, SQL Murder Mystery — https://github.com/NUKnightLab/sql-mysteries (MIT)"
concepts: [sql-joins, sql-subqueries, sql-like, sql-investigation]
cleaned: 2026-10-29
---
# 10 — Capstone: The SQL Murder Mystery

> A crime happened in SQL City on 15 January 2018. The police lost the report, but the database still has everything. Find the murderer with nothing but queries.

---

`bash practice/setup.sh` downloads `sql-murder-mystery.db` (3.6 MB, MIT, from Knight Lab) into `practice/data/`. Then:

```bash
sqlite3 -header -column practice/data/sql-murder-mystery.db
sqlite> .tables
sqlite> SELECT sql FROM sqlite_master WHERE name = 'crime_scene_report';
```

Start from what you know: **a murder, on 2018-01-15, in SQL City.** Read the crime-scene report and follow the leads.

It uses everything from notes 01–05:

| Step | Skill |
|---|---|
| Find the report | Filtering on several columns ([01](01-select-and-filter.md)) |
| Find the witnesses | `LIKE`, `ORDER BY … DESC LIMIT 1` ([01](01-select-and-filter.md), [02](02-nulls-and-expressions.md)) |
| Cross-reference gym check-ins, licence plates and event attendance | Multi-table joins ([04](04-joins.md)) |
| Narrow down the suspects | Subqueries, `GROUP BY … HAVING count(*) = 3` ([03](03-aggregation.md), [05](05-subqueries-and-ctes.md)) |

**Checking your answer.** The game ships with a `solution` table that checks your guess:

```sql
INSERT INTO solution VALUES (1, 'Your Suspect');
SELECT value FROM solution;
```

There is a second twist after the first answer. Keep going until the message says you've found the person really behind it.

No solutions are written down here on purpose. Knight Lab's [walkthrough](https://mystery.knightlab.com/walkthrough.html) teaches the first steps if you get stuck.
