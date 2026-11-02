# Practice

Drills and interview prep that test the curriculum. The curriculum teaches; this folder is for
reps and recall. Dependency runs one way: practice links to chapters, and no chapter depends on
practice.

| Folder | What it is | Start here |
|---|---|---|
| `drills/` | Reps by language and topic | [drills/README.md](drills/README.md) |
| `interviewing/` | Twelve pillars, each a recall sheet, plus prep for each interview round | [interviewing/README.md](interviewing/README.md) |

[CROSSWALK.md](CROSSWALK.md) maps each curriculum unit to the guides and drills that test it, and
[interviewing/README.md](interviewing/README.md) has the role × topic matrix for choosing what to
work on.

Labs stay in their pillars: a pillar's `practice/` folder belongs to that chapter.

## How it fits with the curriculum

- Work a chapter, then drill it, then self-test with the pillar's `interview-guide.md`.
- Guides and drills name the curriculum units they test in a `units:` frontmatter field. Leave the
  field out rather than guess.
- `make crosswalk` checks those paths and the links in this folder, then regenerates `CROSSWALK.md`.

## What is tracked

`practice/.gitignore` is a per-file allowlist, so everything here is ignored until it is listed.
A new file needs a line there, after checking its licence. Personal attempts, solutions to site
problems and third-party material without a licence stay local. Upstreams are recorded in
[`THIRD_PARTY.md`](../THIRD_PARTY.md).
