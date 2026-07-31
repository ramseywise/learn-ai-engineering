# Recurring Sources

Sources swept periodically for material that belongs in the six pillars. Update the
**Last swept** date when you do a pass, and note what landed.

A source earns a row here if it publishes on a cadence *and* has produced at least one
note. One-off citations belong in a note's `sources:` frontmatter, not here.

---

## Tier 1 — primary

Original research or first-party engineering writing. Cite directly.

| Source | Cadence | Scope | Last swept |
|---|---|---|---|
| [Anthropic Engineering](https://www.anthropic.com/engineering) | irregular | harness, context, eval | 2026-07-29 |
| [LangChain blog](https://www.langchain.com/blog) | weekly | loop, graph, harness | 2026-07-29 |
| [Addy Osmani](https://addyosmani.com/blog/) | irregular | loop, harness | 2026-07-29 |
| arXiv (via librarian `cartographer`) | daily cron | all — see `librarian/` | automated |

## Tier 2 — secondary / aggregator

Synthesises Tier 1. **Use as a gap-detector, not a citation of record** — when a post is
good, prefer citing the primary source it draws on. Value is coverage and cadence.

| Source | Cadence | Scope | Last swept |
|---|---|---|---|
| [AI Builder Club](https://www.aibuilderclub.com/blog) | weekly | all six pillars; ~86 posts as of 2026-07 | 2026-07-30 |
| [MarkTechPost](https://www.marktechpost.com/) | daily | loop, graph, papers | 2026-07-31 |
| [dair.ai](https://github.com/dair-ai) | weekly | prompt, papers | vendored snapshot — see below |

---

## Notes on individual sources

### AI Builder Club

Added 2026-07-30. Post taxonomy maps almost exactly onto the six pillars (it uses a
five-layer stack: prompt → context → harness → loop → graph, **omitting eval as a layer** —
our six-pillar model treats eval as a peer foundation and is the better frame).

Landed in the 2026-07-30 sweep:
- [04-loop/loop-autonomy-ladder.md](04-loop/loop-autonomy-ladder.md)
- [04-loop/evolve-loop.md](04-loop/evolve-loop.md)
- [06-eval/eval-maturity-ladder.md](06-eval/eval-maturity-ladder.md)
- [05-graph/graph-engineering.md](05-graph/graph-engineering.md) §11 — escalation framing + decision tree
- [03-harness/notes/04-execution-boundaries.md](03-harness/notes/04-execution-boundaries.md) — role-label/canary section

Assessed and **skipped** as already covered at equal or greater depth: harness 6 components,
the 5 layers of AI engineering, episodic/semantic/procedural memory, context engineering
guide, prompt engineering 2026, and the Claude Code fundamentals track (that is
`~/.claude` config material, not notes material).

### MarkTechPost

Added 2026-07-31. High volume, low signal-per-post — most of its loop-engineering guide
duplicated material already in [04-loop/loop-engineering.md](04-loop/loop-engineering.md)
(three components, five building blocks, the loop skeleton). Its value was one thing: the
`autoresearch` case study, which pointed at two primary sources worth citing directly.

**Fact-check its numbers before using them.** The 2026-07-12 loop-engineering guide had two
errors caught on verification: it dated `autoresearch` to 2026-03-07 (actually 03-06) and
claimed ~90,000 GitHub stars (~48,000 two weeks post-release). The load-bearing figures
(630 lines, 700 experiments, 20 improvements, 2.02→1.80h, 5× val_bpb) all held up.

Landed in the 2026-07-31 sweep:
- [04-loop/loop-engineering.md](04-loop/loop-engineering.md) §8 — the `autoresearch`
  worked example and bilevel autoresearch, cited to
  [karpathy/autoresearch](https://github.com/karpathy/autoresearch) and
  [arXiv:2603.23420](https://arxiv.org/abs/2603.23420) rather than to MarkTechPost.

### dair.ai

**Not automated** — vendored git snapshots, refreshed by hand:
- [01-prompt/Prompt-Engineering-Guide-main/](01-prompt/Prompt-Engineering-Guide-main/)
- [readings/AI-Papers-of-the-Week/](readings/AI-Papers-of-the-Week/)

### librarian / cartographer

The only genuinely automated source. Fetches arXiv on a cron into a queue; `/learn`
processes it. Run from `~/workspace/librarian`, or `make learn` here for the pointer.

Extending cartographer to non-arXiv feeds (RSS) would automate the Tier 1/2 sweeps above —
tracked as a separate `LIB-` concern, not done.
