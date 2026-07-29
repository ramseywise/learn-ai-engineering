# Notion image review — staging area

Candidate images pulled from Dropbox for the `*(missing diagram — not exported from Notion)*`
markers in `ai-engineering/`. **Nothing here is referenced by any note yet.** Review, then
either promote to `ai-engineering/images/` with a descriptive name, or delete.

Staged 2026-07-29.

## Bottom line

The 9 screenshots the notes name by filename **do not exist anywhere on disk**. Searched all of
Dropbox plus Desktop/Downloads/Documents/Pictures by exact timestamp — zero hits. They are still
only in Notion, or on another machine.

The images below are the *closest available* candidates, from `~/Dropbox/docs/AI-LLM-Architecture/`
(320 screenshots, 2026-03-13 → 2026-04-21). That folder turned out to be a **work inbox for the
Ageras / Billy.dk engagement**, not a curated set of course diagrams — so most of it is
client-specific rather than the generic concept art the notes call for.

Note the source folder stops at **April 21**. The six July-dated references
(`2026-07-12`, `2026-07-13`) have **no candidate pool at all**.

## Source of truth

`~/Dropbox/docs/AI-LLM-Architecture/` — left untouched; these are copies.

## Candidates

| File | What it actually shows | Verdict |
|---|---|---|
| `Screenshot 2026-04-13 at 15.02.50.png` | AWS Bedrock Knowledge Base process diagram, Billy.dk Support Assistant — ingestion → semantic chunking → vector DB → hybrid search → generation | **Best candidate.** Genuine architecture diagram, but Billy.dk-branded. Fine as a worked example if labelled as such; wrong for a generic RAG slot. |
| `Screenshot 2026-04-13 at 15.06.45.png` | Three-tier parser comparison — data parsed vs parser output (text / +audio+video / visually rich docs) | **Most reusable.** Fully generic, no client branding. Good fit for an ingestion or parsing section. |
| `Screenshot 2026-04-13 at 15.16.35.png` | Browser screenshot — Ledger entries UI with Shine Assistant chat panel | Reject. Product UI, not a diagram. |
| `Screenshot 2026-04-13 at 16.11.24.png` | VS Code file tree — `src/agents/tools/*.ts` | Possible fit for an agent tool-layout illustration, but it's a work repo. Weak. |
| `Screenshot 2026-04-14 at 14.59.06.png` | "RAG Data Source Task List" — Danish market scope, Intercom/SKAT ingestion | Reject. Project planning doc. |
| `Screenshot 2026-04-14 at 14.59.14.png` | "RAG System Implementation Task List" — Bedrock deploy, monitoring, DataDog | Reject. Project planning doc. |
| `Screenshot 2026-04-14 at 21.37.58.png` | VS Code tree — `cs_agent_assist_with_rag` infra (terraform, lambda, opensearch) | Reject. Client infra layout. |
| `Screenshot 2026-04-14 at 22.35.19.png` | CI tooling comparison table — npm/pixi vs uv, Node 22 vs Python 3.12 | Reject. Unrelated to AI-engineering notes. |

**Net: 1 clear keeper (`15.06.45`), 1 conditional (`15.02.50`), 6 rejects.**

## Where they could be inserted

Insertion points below are **suggestions only — no note files were edited.**

### `Screenshot 2026-04-13 at 15.06.45.png` (parser tiers)
Not a match for either named marker in `05-graph/memory.md`. Better suited to an ingestion
or multimodal-parsing section. Closest unnamed markers:
- `06-eval/eval-harness.md:15` / `:19` — opening diagram slots

Suggested promoted name: `parser-tiers-by-modality.png`

### `Screenshot 2026-04-13 at 15.02.50.png` (Bedrock KB pipeline)
Only if you want a concrete worked example. Candidate slot:
- `05-graph/memory.md:48` — the `Memory-augmented RAG` heading, where
  `Screenshot 2026-04-13 at 15.43.25.png` is missing

Caveat: the note there is about *memory-augmented* RAG (recall policy, what to retrieve
when). This diagram is a standard ingest+retrieve pipeline with no memory layer — it does
not illustrate the point the prose is making. Recommend **not** using it here.

Suggested promoted name: `bedrock-kb-pipeline-billydk.png`

## The 9 named-but-missing screenshots

None recoverable from disk. Listed so you can pull them from Notion directly.

| Filename | Referenced at |
|---|---|
| `Screenshot 2026-04-13 at 15.43.25.png` | `05-graph/memory.md:48` |
| `Screenshot 2026-04-14 at 08.45.14.png` | `05-graph/memory.md:78` |
| `Screenshot 2026-07-12 at 18.30.18.png` | `03-harness/agents-design.md:108` |
| `Screenshot 2026-07-12 at 18.31.54.png` | `03-harness/agents-design.md:143` |
| `Screenshot 2026-07-13 at 15.10.42.png` | `06-eval/eval-harness.md:76` |
| `Screenshot 2026-07-13 at 15.11.43.png` | `06-eval/eval-harness.md:80` |
| `Screenshot 2026-07-13 at 15.11.54.png` | `06-eval/eval-harness.md:84` |
| `Screenshot 2026-07-13 at 15.36.07.png` | `06-eval/eval-harness.md:222` |
| `Screenshot 2026-07-13 at 15.36.19.png` | `06-eval/eval-harness.md:224` |

## Marker totals

48 markers across 7 files; only 9 name a file. The other 39 are bare
`*(missing diagram — not exported from Notion)*` and can only be matched by reading the
surrounding prose against image content.

| File | Markers |
|---|---|
| `06-eval/eval-harness.md` | 10 |
| `05-graph/memory.md` | 10 |
| `03-harness/agents-design.md` | 10 |
| `04-loop/loop-engineering.md` | 8 |
| `03-harness/agent-harness.md` | 5 |
| `03-harness/agents-guardrails.md` | 4 |
| `06-eval/observability.md` | 1 |

Counted on the working tree of branch `LAE-105-context-notes`, where
`02-context/context-management.md` (7 markers) has been split into `02-context/notes/`.
Those markers did not survive the split — re-check `02-context/` after that branch settles.

## Convention, once you promote something

Existing notes have no image convention — the single inline image in the hand-written docs
points sideways at `../../interviewing/images/` (`06-eval/eval-harness.md:233`), which isn't
worth extending.

Proposed: promote to `ai-engineering/images/` with descriptive kebab-case names, referenced
by relative path, e.g. from `05-graph/memory.md`:

```markdown
![Parser tiers by input modality](../images/parser-tiers-by-modality.png)
```

## Re-running the search

```sh
# markers with a named file
grep -rn "missing diagram — \`" ai-engineering/

# all markers, per file
grep -rc "missing diagram" ai-engineering/ | grep -v ":0"
```
