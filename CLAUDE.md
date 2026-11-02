# Learn AI Engineering

Course repo: curriculum notes, lecture decks, practice drills and the pipeline that feeds them. Librarian
(`../librarian`) imports this content with `make import-courses`. [CURRICULUM.md](CURRICULUM.md) describes the program.

## Layout

- `ai-engineering/`, `generative-ai/`, `data-analytics/`, `data-science/`, `data-engineering/`: pillars of
  `README.md`, `notes/`, `references.md`, `slides/`, `sources/`. Standard:
  [pillar-layout.md](.claude/skills/pillar/references/pillar-layout.md).
- `programming/`: modules with their own notes and decks.
- `practice/`: drills and interview guides. `practice/.gitignore` is a per-file allowlist, so nothing new is tracked
  until it is listed there. Add a line only after clearing the licence and checking for anything personal.
- `scripts/`: deterministic checks and pipelines. `scripts/papers/ledger.jsonl` tracks readings.
  `scripts/review/findings.jsonl` tracks reviewer decisions.

## How work is split

- **Scripts do what can be computed.** Run them through `make`; `make help` lists the targets.
- **Agents (`.claude/agents/`) read and report.** They never edit. Don't give a reviewer the author's reasoning.
- **Skills (`.claude/skills/`) orchestrate, decide and edit.** Use `/papers`, `/chapter`, `/write-chapter`, `/slides`,
  `/pillar`, `/curriculum`, `/readings` and `/review`.
- A fault that keeps recurring becomes a script check or a spec change, not a longer reviewer prompt.
- Learner and reviewer signals produce proposals for the user. Nothing rewrites content or agent definitions on its own.

## Rules that are easy to break

- Notes are the source of truth. Decks are built from `deck.yaml` with `make slides`; never hand-edit a `.pptx`.
- A source that repeats what a note says is **sharpens**: add the citation and the references row. Never drop it silently.
- Every number carries the setup it holds under. `unverifiable` is not a pass. Never cite what was not read.
- Personal history (drill logs, flashcard results, signal reports) stays out of tracked files.
- The working tree can be shared with other sessions. Stage by explicit path, and don't touch changes you didn't make.
- Run `make test` before handing work over, and report any failure you leave behind.
