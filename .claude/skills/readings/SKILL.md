---
name: readings
description: "Work the readings backlog: show what is in the scripts/readings/ inbox and the ledger (queued, downloaded, integrated by home), route triaged PDFs to their home's sources/, triage anything new, and recommend the next /chapter or /papers run. Usage: /readings, /readings route, /readings triage. Run from the learn-ai-engineering repo."
---

You are keeping the reading backlog moving. `scripts/readings/README.md` describes
the system. In short, every reading (DAIR AI Papers of the Week and every PDF dropped into
the repo) is one row in `scripts/readings/ledger.jsonl`. Triage gives each row a
home, a note and a relevance score. Route moves its PDF to the home's `sources/`. Then
`/papers` (single papers) or `/chapter` (book chapters) fold it into the notes.

Nothing leaves the repo. A reading with no home stays in the ledger as `parked` (worth
knowing: interest 2–3) or `skipped` (not for this course). If `status --list parked` shows a
body of sources with no home, propose a new pillar (see the
decision note in `CURRICULUM.md`). Do not create one without the user.

---

## Step 1 — Status

```bash
python3 scripts/papers/potw.py status
python3 scripts/papers/potw.py status --list queued | python3 -c "import sys,json,collections; c=collections.Counter((r['pillar'], 'chapter' if '/ch' in (r.get('pdf') or '') or '/appendix-' in (r.get('pdf') or '') else 'paper') for r in map(json.loads,sys.stdin)); [print(f'{n:4} {h:18} {k}') for (h,k),n in sorted(c.items())]"
find scripts/readings -name '*.pdf' -newer scripts/readings/ledger.jsonl
```

The last command lists PDFs added since the ledger was last written. They need a scan and
a triage.

## Step 2 — Scan, triage, route (when asked, or when step 1 shows work)

```bash
python3 scripts/papers/potw.py scan                          # new inbox PDFs into the ledger
python3 scripts/papers/potw.py triage --source repo --backlog  # homes + notes for new rows
python3 scripts/papers/potw.py triage --local --backlog      # DAIR rows whose PDF is already here
python3 scripts/papers/potw.py route                         # dry run: where each PDF goes
python3 scripts/papers/potw.py route --apply
```

Read the dry run before applying. Check that book chapters land together under one
`sources/<book-slug>/` and that nothing obviously off-topic is going to a pillar. To fix a
wrong home, edit that row's `topic`, `pillar` and `note` in the ledger (one JSON object
per line), then rerun the dry run. Skipped rows stay where they are. Route removes an
inbox copy only when the same file already sits in the right home. A copy filed in the
wrong home stays in the row's `copies` list; mention those so `/pillar` can clear them.

## Step 3 — Recommend the next run

Recommend one concrete next command, then one or two alternatives:
- Finish a half-integrated book before starting another: `/chapter <book-slug>`.
- Otherwise prefer the home with the most queued relevance-3 rows: `/papers <home>`.
- Prefer homes whose notes are thin (few notes, or no references.md) over well-covered ones.
- When a pillar's notes changed a lot since its deck was built, suggest `/slides <pillar>`.

Report the counts as a short table, what you routed, and the recommendation. Do not commit.
