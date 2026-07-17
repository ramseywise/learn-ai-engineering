# Interview KB Consolidation — learn-ai-engineering/interviewing × librarian wiki
Date: 2026-07-17
Status: IN PROGRESS

## Research

### Summary
The `interviewing/` folder is an uncommitted raw Notion dump (17+ files, ~5,900 lines and still growing mid-research, one exact duplicate pair) whose topics overlap ~70% with the librarian wiki — which is deeper on every shared topic. The unique value in `interviewing/` is (a) interview-process framing (case/system-design interview technique), (b) 3–4 topic gaps in the wiki (prompt injection depth, RL/MARL, agent self-training, harness/loop engineering), and (c) a curated reading list. **Direction (agreed 2026-07-17): the interviewing KB lives in this repo** as compiled study guides that summarize both the repo's own learning folders and librarian wiki knowledge, with references to all sources; librarian consumes it back via its existing repo scraper (already configured for this repo, but its globs miss `interviewing/`). External research confirms the 2026 ML/AI/DS/FDE loop is well-mapped and the original interview-type list was missing ~5 round types.

### Scope
Investigated: all 17 files in `interviewing/` (headings + full read of `table_of_contents.md`, `case_interview.md`); librarian wiki structure (117 pages, `_index.md`, `CLAUDE.md` schema); external sources on 2026 interview loops for ML/AI/DS/FDE roles. Out of scope: implementation of the consolidation, ingest mechanics, per-page content migration decisions.

### Findings

#### F1 — `interviewing/` is raw material, not a KB (High)
- Untracked in git (`?? interviewing/` — never committed).
- Notion-export artifacts throughout: broken `!image.png` refs, affiliate links, `?utm_source=chatgpt.com` URLs, mixed Chinese/English (`rl.md`), free-associative structure (`table_of_contents.md` is a link dump + misc notes, not a TOC).
- `eval_harness.md` and `agents/evals.md` are **byte-identical duplicates** (verified by diff).
- Provenance flag: `table_of_contents.md:57` says "Sth to read (but Yan haven't)" — at least some content appears copied from a third party's notes. Treat as `confidence: low/medium` source per librarian's source-confidence scheme.
- Quality maps exactly onto librarian's mental model: this folder is `raw/`, not `wiki/`.

#### F2 — Librarian already scaffolded the destination (High)
- `librarian/CLAUDE.md` defines `wiki/foundations/` ("ML/DS/data-engineering fundamentals") and `wiki/interview/` ("Coding-interview patterns, system design, prep references") with matching domain tags `foundations` and `interview`.
- Both directories **exist and are empty** — declared intent, never populated.
- The wiki already contains 4 interview-format pages: `eval/system-design-eval-harness.md`, `adk/system-design-serverless-agents.md`, `infra/system-design-shared-indexer.md`, `meta/code-review-drill-sanyi.md` — i.e., the "system design interview writeup" and "code review drill" genres already have precedent pages.
- Librarian's ingest protocol (dedup, conflict flagging, wikilinks, tombstones) solves exactly the consolidation problem this task poses.

#### F3 — Topic parity (High for topic-level; Medium for claim-level, files not read line-by-line)

| Topic | interviewing/ file(s) | librarian coverage | Verdict |
|---|---|---|---|
| RAG | `rag.md` (212 ln, 9 architectures, prod checklist) | `wiki/rag/` — 16 pages, far deeper | **Wiki wins**; rag.md adds interview-answer framing only |
| Evals | `eval_harness.md` ≡ `agents/evals.md` (same Anthropic source) | `wiki/eval/` — 16 pages incl. `anthropic-eval-taxonomy.md` from the same article | **Wiki wins**; near-total overlap |
| Deep agents | `deep_agents.md` (630 ln — LangChain docs copy) | `wiki/deep-agents/` — 3 compiled pages | **Wiki wins** |
| Context mgmt / caching | `context_management.md`, `context_engineering.md`, prompt-caching notes in `table_of_contents.md` | `infra/prefix-caching.md`, `adk/adk-context-engineering.md`, `langgraph/summarization-node.md` | **Wiki wins**, minor deltas (compaction-instruction notes) |
| Memory | `memory.md` (671 ln — memory-augmented RAG, **Memoria framework**) | `wiki/memory/` — 3 pages | **Partial gap**: Memoria + memory-augmented-RAG flow not in wiki |
| Guardrails | `agents/guardrails.md` | `infra/input-guardrails-pipeline.md` | Overlap; small deltas (bad deployment patterns list) |
| Security / prompt injection | `security.md` (939 ln), `prompt_injection.md` (592 ln) | Only `input-guardrails-pipeline.md`, `mcp-server-security-patterns.md`, PII pages | **Gap**: no dedicated prompt-injection or agent-security-threat-model page; interviewing/ + OWASP links are the stronger source |
| RL / RLHF / DPO / MARL | `rl.md` (317 ln, partly Chinese) | `eval/direct-preference-optimization.md` only | **Gap**: RL-in-RAG, MARL, RLHF overview absent |
| Self-training agents | `agents/self_training.md` (Agent-Lightning) | `memory/self-learning-agents.md` (4-level stack, no tooling) | **Partial gap**: Agent-Lightning / training-agent disaggregation not in wiki |
| Harness / loop engineering | `agent_harness.md`, `loop_engineering.md`, `reliable_agents.md`, OpenClaw + protocol-driven multi-agent notes in `table_of_contents.md` | Scattered: `patterns/agentic-workflow-patterns.md`, `aci`, deep-agents pages | **Partial gap**: "harness engineering" as a named concept + protocol/task-graph/isolation triad not compiled |
| Multi-agent design | `agents/design.md` (79 ln) | `adk/multi-agent-orchestration-patterns.md` + A2A | **Wiki wins** |
| Google ADK | `agents/google_adk.md` (209 ln, added 2026-07-17 mid-research — folder still growing) | `wiki/adk/` — 19 pages | **Wiki wins** (presumed; not read line-by-line) |
| Interview technique | `case_interview.md` (436 ln — case + system-design interview process, trade-off narration, bottleneck/failure tables) | Nothing equivalent (only the 4 drill/writeup pages) | **interviewing/ wins** — this is the seed for `wiki/interview/` |
| Reading list / job tracker | `table_of_contents.md` links (roadmap.sh, OWASP cheatsheets, LLM-interview-Q hub, books) | None | **interviewing/ wins** — becomes a `reference` page |

Net: ~9 of 13 topic areas are already better covered by the wiki; unique value concentrates in interview technique, security/prompt-injection, RL, self-training, harness engineering, and the reference list.

#### F4 — What the 2026 interview loop actually tests (Medium-High, external sources)
- **AI/ML engineer loop**: recruiter screen → coding (increasingly project-style/debugging, AI assistant often allowed) → ML/LLM breadth round (front-loads transformer/LLM-era questions) → **(ML/LLM/agent) system design** (the highest-weight round; RAG, agents, eval, cost/latency trade-offs) → project deep-dive → behavioral. In-person rounds returning (~38% in 2025) to counter AI-assisted cheating.
- **FDE / Applied AI Engineer loop** (Palantir/OpenAI/Anthropic pattern): 5–8 stages; ~50% of evaluation is **non-coding** — ambiguous customer case study (lowest pass rate ~40%, highest weight ~30%), customer-conversation simulation (Anthropic's hidden filter, ~60% of coding-passers fail it), business judgment/ROI reasoning.
- **DS loop**: recruiter → SQL/technical screen → statistics & experimentation (A/B) → product-sense case → behavioral; take-home data challenge with presentation common (24–48h).
- **Cross-cutting signal** every source repeats: trade-off narration (cost vs latency, RAG vs fine-tuning, interpretability vs accuracy), measuring success (evals/metrics stated unprompted), thinking aloud, structured clarify→design→iterate process, business framing. This matches `case_interview.md`'s emphasis — that file is aligned with current practice.

#### F5 — Interview-type taxonomy: user's list + gaps (High)
User listed: CTO, head of product, code review, system design, coding challenge, behavioral, technical questions, case study (online/offline). Missing round types found in research:
1. **Recruiter/HR screen** (narrative + logistics — deserves a 1-pager)
2. **Project deep-dive / experience review** (walk through a past system; standard senior round)
3. **Customer/stakeholder simulation** (FDE signature round — distinct from behavioral)
4. **Debugging round** (2026 trend: fix unfamiliar broken code > write new code)
5. **Take-home presentation / defense** (the follow-up to offline case studies)
6. **Reverse interview** (questions to ask CTO/founder/HoP — sources treat it as evaluated signal, and it doubles as startup due-diligence: runway, culture, growth)
7. (Optional) pair-programming and values/bar-raiser rounds — variants of coding/behavioral, may not need own files.
Note: "CTO interview" and "head of product interview" are interviewer-centric names; research suggests organizing by **what is tested** (vision/judgment alignment, product sense) with a per-interviewer prep angle, since a CTO round at a startup mixes system design + judgment + reverse-interview.

#### F5b — Notion images now exported (High)
`interviewing/images/` holds 10 screenshots (agent patterns, prompt-caching diagrams, etc.) matching the broken `!image.png` refs in the MDs. Filenames are Notion defaults (`image (1).png`, `Screenshot 2026-06-15 at …`) with no mapping back to which MD referenced them — re-linking requires opening each image and matching it to its context (feasible: only 10 images, and `case_interview.md:14` names one screenshot by date). Cleanup should rename them descriptively and restore inline refs.

#### F6 — Governance fit and the scrape-back loop (High)
- `~/.claude/rules/docs.md`: learn-ai-engineering is a human-consumed learning repo; librarian wiki is the compiled KB with an established writer (ingest pipeline). Study guides here are *compiled artifacts for a human reader* — copying knowledge into them is the point of compilation, not state duplication; drift is guarded by librarian's conflict-flagging ingest, provided the loop below is closed.
- **The scrape-back loop already exists but has a hole**: `librarian/raw/repos/repos.txt` already lists `/Users/wiseer/workspace/learn-ai-engineering`, but `etl/scrape_repos.py` only extracts `CLAUDE.md`, `README.md`, `SANYI.md`, `.claude/skills|docs/**`, `docs/**`, `.agents/**` — **`interviewing/` content would never be scraped**. Closing the loop requires either extending the scrape globs or placing the KB under a scraped path.
- Librarian ingest of Notion sources goes through `raw/notion/` (append-only) — precedent exists for exactly this kind of Notion-dump ingestion (16 files already there). Agreed: `interviewing/` gets cleaned up (duplicate removal, dead links, image re-linking, provenance tagging) **before** librarian ingests it.

#### F7 — Repo-internal source map: the KB's other input (High)
The interviewing KB is a summary layer over the repo's existing learning folders, not just over librarian. Current source inventory in this repo:

| Folder | Content | Feeds which prep area |
|---|---|---|
| `data-science/` | Ng Deep Learning notebooks (incl. two ML-strategy **case-study quizzes**), Intro-to-ML, Bayes | ML breadth/theory, case study |
| `data-engineering/` | DataTalks Data Engineering (6 modules) + DataTalks MLOps (7 modules) | DE/MLOps questions, system design substrate |
| `data-analytics/` | Text Analytics with Python, SimpleHacks | SQL/analytics screen, NLP basics |
| `generative-ai/` | nn-zero-to-hero (nanogpt), intro-to-nlp, chatbot projects (deep-research-bot), coursera-references (LangGraph, memory, RAG, evals, context engineering — 15+ course repos), **`readings/`** (new: paper PDFs organized `0.rag`, `1.prompt engineering`, `2.knowledge graphs` + classic papers: attention-is-all-you-need, wavenet, batch-norm, RAGAS…) | LLM internals, RAG, agents — technical depth + "explain the paper" questions |
| `programming/` | README only | Coding-challenge prep — **empty, confirmed gap** |
| `interviewing/` | this consolidation's subject | technique + question banks |

`generative-ai/readings/` is being actively populated (user copying additional texts now) — it scaffolds the "primary sources" tier of the KB. Numbered-folder convention (`0.rag`, `1.prompt engineering`, …) suggests an intended topic ordering the KB structure should align with.

#### F8 — Role × topic syllabus (what must be known, per role) (Medium-High)
Synthesis of F4 external research + librarian domains + repo folders — the topic scaffold the study guides must cover. Roles: **AIE** (AI/agent engineer), **MLE**, **DS**, **FDE** (applied/forward-deployed). Weight: ● core / ◐ secondary / ○ awareness.

| Topic area | AIE | MLE | DS | FDE | Primary sources today |
|---|---|---|---|---|---|
| LLM fundamentals (transformers, tokenization, attention, fine-tuning/LoRA, RLHF) | ● | ● | ◐ | ● | readings/, nn-zero-to-hero, wiki gaps (RL) |
| RAG (architectures, chunking, reranking, eval) | ● | ◐ | ○ | ● | wiki/rag (16 pp), readings/0.rag, interviewing/rag.md |
| Agents (orchestration, memory, tools/MCP, harness, deep agents) | ● | ◐ | ○ | ● | wiki/adk+langgraph+memory+mcp+deep-agents+patterns (~50 pp), interviewing/agents/ |
| Evals & observability | ● | ● | ◐ | ● | wiki/eval+infra (~20 pp), interviewing/eval_harness.md, langfuse course refs |
| Safety/security (prompt injection, guardrails, PII, compliance) | ● | ◐ | ○ | ● | interviewing/security.md + prompt_injection.md (wiki gap), OWASP links |
| Context engineering & cost/latency (caching, compaction) | ● | ◐ | ○ | ◐ | wiki infra/adk pages, interviewing context files |
| Classical ML + DL theory (bias/variance, metrics, calibration) | ◐ | ● | ● | ○ | data-science/, wiki/foundations (empty) |
| Stats & experimentation (A/B, causal, product metrics) | ○ | ◐ | ● | ○ | **gap everywhere** — no source in either repo |
| SQL & analytics | ○ | ◐ | ● | ◐ | data-analytics/ (thin) |
| Data eng & MLOps (pipelines, deployment, monitoring) | ◐ | ● | ◐ | ◐ | data-engineering/ (strong) |
| Coding patterns (DS&A, debugging drills) | ◐ | ◐ | ◐ | ◐ | **gap everywhere** — programming/ empty |
| System design (classic + ML + LLM/agent) | ● | ● | ◐ | ● | case_interview.md + wiki's 3 system-design writeups |
| Product/business sense, ROI, customer judgment | ◐ | ○ | ● | ● | case_interview.md fragments only — thin |
| Interview technique (trade-off narration, STAR, reverse interview) | ● | ● | ● | ● | case_interview.md + external sources in this doc |

Notable: the two topics with **no source material anywhere** (stats/experimentation, coding patterns) are both DS/loop staples — acquiring or writing those is net-new work, not consolidation.

### Assumptions
- **Assumption:** The Notion pages behind `interviewing/` are fully captured in these MD files (no images/tables lost that matter). — **Evidence:** broken `!image.png` refs show images were dropped. — **If wrong:** some content (architecture diagrams, the 5-agent-patterns images) must be re-exported from Notion before ingest. — **Confidence:** Medium.
- **Assumption:** `wiki/interview/` + `wiki/foundations/` being empty means "planned, not started" rather than "abandoned". — **Evidence:** CLAUDE.md defines both domains + tags; dirs exist. — **If wrong:** a different destination decision was already made somewhere; none found in `projects/librarian-kb-plan.md` index summary. — **Confidence:** High.
- **Assumption:** Target roles are ML/AI engineer, DS, and FDE-type hybrid roles (per request), with startup-weighted loops (CTO/HoP rounds imply small-company processes). — **If wrong:** big-tech loops add LC-style algorithmic depth that this KB currently de-prioritizes. — **Confidence:** Medium.

### Disconfirming Evidence
- **"Wiki is deeper on shared topics"** — checked by grepping wiki for each interviewing/ topic and comparing page counts/summaries; claim-level diffs (e.g., whether `security.md`'s circuit-breaker pattern appears in any wiki page) were **not** exhaustively verified — some "wiki wins" rows may hide small unique deltas. Mitigation: librarian's ingest protocol is delta-preserving by design, so misjudging a row costs nothing if the folder is ingested as raw source.
- **"interviewing/ is third-party/low-confidence"** — the "Yan" reference could denote a colleague whose notes were shared intentionally; content could still be accurate. I did not find contradictions with wiki claims in the sections read.
- **"System design is the highest-weight round"** — FDE sources contradict this for FDE roles specifically (case study + customer simulation outweigh it). Reflected in F4.
- **"Empty dirs = intent"** — looked for a librarian plan doc scoping wiki/interview population; `librarian-kb-plan.md` phases were not read in full. If Phase 9–15 already scopes this, the plan phase should align with it.

### Open Questions for /plan
1. **Pointer mechanism** — how study guides reference librarian wiki knowledge:
   - **(A) Compile + cite (recommended):** guides carry compiled summaries and end with a `Sources:` section listing repo-relative paths (this repo) and librarian wiki page titles. Self-contained for studying, GitHub-readable; drift guarded by librarian's scrape→ingest conflict flagging once the scrape hole (F6) is closed.
   - **(B) Cross-repo relative links** (`../../librarian/wiki/...`): live links locally/Obsidian, broken on GitHub; couples repo layouts.
   - **(C) Pure pointers, no content:** zero drift but defeats the purpose — a study guide you can't study from.
2. **Scrape-hole fix** — extend `scrape_repos.py` globs to include `interviewing/**` vs. move the KB under an already-scraped path (`docs/`). Glob extension is the smaller change and keeps the repo's human-facing layout.
3. **Notion export completeness** — TOC lists topics with no corresponding file (Knowledge Graph, Recovery/rollback, Tool Calling & Evals); folder still receiving files mid-research (`agents/google_adk.md`, `observability.md.m` — note the typo'd extension). Cleanup should wait for the dump to finish.
4. **Images** — 10 exported screenshots need renaming + re-linking (F5b); decide insert-where-applicable (cheap, recommended first pass) vs. expand into annotated diagram pages.
5. **Net-new topics** (stats/experimentation, coding patterns) — acquire external material, write from scratch, or defer to a later milestone.
6. Whether `wiki/foundations/`+`wiki/interview/` population in librarian happens in the same effort (via scrape+ingest) or is deferred — affects librarian's phase plan, not this repo's.

Resolved since first draft: KB lives in this repo (decided); cleanup before librarian ingest (decided); images exist (exported); focus is roles not companies (AIE/MLE/DS/FDE weighting in F8).

### Recommendation
Build the interviewing KB **in this repo** as a three-layer structure, then let librarian consume it: **(1) Study guides** — one per F8 topic area, compiled summaries drawing on the repo's own folders (F7), the cleaned interviewing/ notes, and librarian wiki knowledge, each ending with a full `Sources:` section (pointer mechanism A); **(2) Interview-round guides** — one per round type (the 8 originally listed + recruiter screen, project deep-dive, customer simulation, debugging, take-home presentation, reverse interview), containing process, technique, question banks, and the F8 per-role weighting; **(3) Sources tier** — the existing folders plus `generative-ai/readings/`, cleaned `interviewing/` raw notes, and `images/`, left in place and referenced. `case_interview.md` seeds layer 2; librarian's four interview-format writeups seed a "my systems as interview answers" drill set. Consolidation order matters: finish the Notion dump → clean (dedupe, dead links, image re-linking, provenance tags) → build the study-guide layer → close the scrape hole so librarian's `wiki/interview/`+`wiki/foundations/` populate from it. The two net-new topic areas (stats/experimentation, coding patterns) should be scoped as a separate milestone since they are authorship, not consolidation.

## Sources (external)
- [Grokking — The Modern ML Interview formats](https://grokkingml.com/ml-interview-formats.html)
- [Exponent — ML System Design Interview 2026](https://www.tryexponent.com/blog/machine-learning-system-design-interview-guide)
- [Exponent — AI Engineer Interview Questions 2026](https://www.tryexponent.com/blog/ai-engineer-interview-questions)
- [KORE1 — AI Engineer Interview Questions 2026](https://www.kore1.com/ai-engineer-interview-questions-2026/)
- [Exponent — FDE Interview: Definitive 2026 Guide](https://www.tryexponent.com/blog/forward-deployed-engineer-interview-the-definitive-2026-guide-fde)
- [Perspective AI — Anthropic Applied AI Engineer process](https://getperspective.ai/blog/anthropic-applied-ai-engineer-interview-process-frontier-lab-2026)
- [Perspective AI — FDE interview questions 2026](https://getperspective.ai/blog/forward-deployed-engineer-interview-questions-2026-prep-guide)
- [Sundeep Teki — FDE interview guide 2026](https://www.sundeepteki.org/advice/the-definitive-guide-to-forward-deployed-engineer-interviews-in-2026)
- [Hacking the Case Interview — DS case interviews](https://www.hackingthecaseinterview.com/pages/data-science-case-interview)
- [DataInterview — Product DS prep 2026](https://www.datainterview.com/blog/product-data-scientist-interview-prep)
- [Clément Bataille — Questions to ask in startup interviews](https://medium.com/@clementb/questions-to-ask-as-a-software-engineer-candidate-in-startup-interviews-263e4698e17c)

## Plan
Date: 2026-07-17
Based on: ## Research above + direct repo inspection (baseline 2026-07-17: repo clean on main except untracked `.claude/`, `interviewing/`, `generative-ai/readings/`; no test suite — content repo)

### Goal
Build the interviewing KB inside this repo — cleaned raw notes → compiled study guides → interview-round guides, with full source references — and close the librarian scrape loop so `wiki/interview/` + `wiki/foundations/` can later populate from it.

### Open Questions
Decisions for Ramsey, each with the plan's assumed default:

1. **⚠ Public-repo exposure (gates Step 1, blocks all commits).** — **RESOLVED 2026-07-17:** copyrighted book PDFs stay local + gitignored (personal license ≠ redistribution right; public GitHub = redistribution). Personal/internal files (`PhD_Exposé.docx`, `marco_thesis.pdf`, `oraion_interview_prep.docx`, `DATA-TxMatch…`, `DATA-DSML…`, `AAAAAAA~@@@@@@.pdf`) are **deleted** (Ramsey decision 2026-07-17; all untracked, never committed — presumed copies of originals held elsewhere). Gitignore `generative-ai/readings/**` with `!README.md`; index README lists books by title + publisher link, no binaries committed.
2. **Dump completeness.** — **RESOLVED 2026-07-17: Notion export confirmed complete.** TOC topics with no file (Knowledge Graph, Recovery/rollback, Tool Calling & Evals) are genuinely unwritten → **filled during guide compilation** from librarian + repo sources (Ramsey decision 2026-07-17): Knowledge Graph → rag/agents guides (readings/`2.knowledge graphs`, coursera `Knowledge_Graphs_for_RAG-main`, wiki GraphRAG in [[Agentic RAG — Advanced Patterns]]); Recovery/rollback → agents guide harness/reliability section (notes on OpenClaw crash recovery, wiki HITL/checkpointer pages); Tool Calling & Evals → agents + evals-observability guides (wiki ACI, ADK eval pages).
3. **Guide granularity.** — **RESOLVED 2026-07-17: 10 study guides** (Ramsey deferred to recommendation): files stay 150–300 lines, groupings follow F8 merges; split later if any guide exceeds ~400 lines.
4. **Rounds granularity.** — **RESOLVED 2026-07-17: 10 round files** (coding+debugging+pairing → one; case-study+take-home-presentation → one; CTO+HoP+reverse-interview → `leadership-rounds.md`).
5. **Cleaned-notes location.** — **RESOLVED 2026-07-17: raw MDs move to `interviewing/notes/`** (flattening `agents/` into it), keeping guides/ and rounds/ as the readable surface.
6. **Scrape fix.** — **RESOLVED 2026-07-17: extend `librarian/etl/scrape_repos.py` globs** with `interviewing/**/*.md`.
7. **Librarian private content.** Guides compile from **public wiki domains only** — never `wiki/private/`, no client names (legacy-scrub rule). Non-negotiable given public repo; listed here for visibility, not really a question.

### Approach
Three phases matching the research's consolidation order: (A) hygiene + cleanup of the raw dump, (B) build the KB scaffold and compile study guides using pointer mechanism A (compile + cite), (C) round guides + librarian scrape integration. Key tradeoff: guides duplicate knowledge that lives in librarian — accepted deliberately because study guides must be self-contained; drift is guarded by the closed scrape→ingest loop (librarian flags conflicts on re-ingest). All commits are made by Ramsey; sessions only stage.

### Out of Scope
- Authoring net-new **stats/experimentation** and **coding-patterns (DS&A)** guides — separate milestone; note `readings/stats_recs/` (ISLR, Practical Stats, Think Stats/Bayes) now seeds the stats one.
- Librarian-side wiki ingest/population of `wiki/interview/` + `wiki/foundations/` (a librarian session, after scrape works).
- Re-exporting anything from Notion; editing files in `librarian/raw/`.
- Summarizing/annotating the readings PDFs themselves (index only).
- `PORTFOLIO.md`, root `README.md` restructuring beyond the interviewing pointer.
- Linear tickets (repo not wired to Linear).

### Steps

#### Step 1: Repo hygiene gate
**Files**: `.gitignore` (repo root), `generative-ai/readings/README.md` (new), `interviewing/observability.md.m` → rename
**What**: Add `generative-ai/readings/**` (with `!README.md` exception) to `.gitignore` per Open Q1. Delete the personal/internal files (exact Q1 list, echoed in the step output for the commit-gate review). Write `readings/README.md` indexing the collection (folders `0.rag`…`3.reinforcement_learning`, `ai_engineering/`, `general/`, `stats_recs/`, `data mesh/` + loose classics) with title + one-line relevance each; books listed by title + publisher link only. Rename `observability.md.m` → `observability.md`.
**Snippet** (.gitignore):
```
# readings library: copyrighted books + personal/internal docs stay local
generative-ai/readings/**
!generative-ai/readings/README.md
```
**Test**: `git -C ~/workspace/learn-ai-engineering status --porcelain | grep readings` → only `readings/README.md` appears; `git check-ignore -q "generative-ai/readings/wavenet.pdf" && echo IGNORED`
**Done when**: `git status` shows no readings binaries as untracked; `observability.md` exists; README index covers every subfolder.

#### Step 2: Clean the raw notes → `interviewing/notes/`
**Files**: all 17 `interviewing/*.md` + `interviewing/agents/*.md` → `interviewing/notes/*.md` (flattened; `agents/` prefix kept in filenames where needed, e.g. `agents-design.md`)
**What**: Per file: (a) add provenance frontmatter (`source:` original URL(s) when identifiable, `confidence: low|medium` per librarian's scheme, `origin: notion-export`, third-party-notes flag where the "Yan" provenance applies); (b) strip `utm_source` params and affiliate links; (c) delete `agents/evals.md` (byte-identical to `eval_harness.md`, verified in research); (d) split `table_of_contents.md` into `notes/reading-list.md` (curated links + book list, cleaned) and distribute its orphan knowledge chunks (prompt-caching, protocol-driven multi-agent, OpenClaw tips, skills-design tips) into the matching notes files; (e) translate or flag the Chinese sections in `rl.md`.
**Snippet** (frontmatter added to each note):
```markdown
---
origin: notion-export
source: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
confidence: medium
cleaned: 2026-07-17
---
```
**Test**: `grep -rL "^origin:" interviewing/notes/*.md | wc -l` → 0; `grep -rc "utm_source" interviewing/notes/ | grep -v ':0' | wc -l` → 0; `test ! -f interviewing/agents/evals.md && echo GONE`
**Done when**: every notes file has frontmatter; no duplicates; `table_of_contents.md` no longer exists as such; old top-level MDs moved.

#### Step 3: Re-link images
**Files**: `interviewing/images/*` (10 files, renamed), image refs inside `interviewing/notes/*.md`
**What**: Open each image, identify its subject, rename descriptively (`prompt-caching-prefill.png`, `agent-patterns-5.png`, …), and replace the broken `!image.png` / `!Screenshot …` lines in the notes with real markdown refs. `case_interview.md:14` names its screenshot by date — anchor from there. Unmatchable images get listed in `notes/reading-list.md` under "unplaced diagrams".
**Snippet**: `!Screenshot 2025-12-20 at 14.54.34.png` → `![Case interview evaluation dimensions](../images/case-interview-dimensions.png)`
**Test**: `grep -rn '^!\[' interviewing/notes/ | wc -l` ≥ 8; `grep -rn '^!image\|^!Screenshot' interviewing/notes/ | wc -l` → 0
**Done when**: no broken image refs remain; every image renamed and either placed or listed as unplaced.

--- *Phase A review boundary: Ramsey commits cleanup before compilation begins* ---

#### Step 4: KB scaffold + index
**Files**: `interviewing/README.md` (new), `interviewing/guides/` + `interviewing/rounds/` (new dirs), root `README.md` (update the existing interview-prep note, ~lines 6-11)
**What**: Write the KB index: how the three layers work (guides ← notes ← readings; rounds for process), the F8 role × topic weighting matrix (AIE/MLE/DS/FDE), links to all planned guide/round files, and the librarian relationship (public-wiki compile + scrape-back). Update root README's interview-prep note to point at `interviewing/README.md` first.
**Snippet** (index structure):
```markdown
# Interviewing KB
## How to use   (role → weighted topic list → guides → rounds)
## Role × topic matrix   (from research F8)
## Study guides   (guides/*.md)
## Interview rounds   (rounds/*.md)
## Sources   (notes/, images/, ../generative-ai/readings/, librarian wiki)
```
**Test**: `test -d interviewing/guides && test -d interviewing/rounds && grep -q "Role × topic" interviewing/README.md && echo OK`
**Done when**: README renders with matrix + working relative links to notes/.

#### Step 5: Study guides — agent-era batch (5 guides)
**Files**: `interviewing/guides/{rag,agents,evals-observability,security-safety,context-engineering-cost}.md`
**What**: Compile each from: librarian **public** wiki pages (read in full per librarian's query protocol; never `wiki/private/`; scrub any client references), cleaned notes, and readings index entries. This batch also fills the three unwritten Notion topics per the Q2 mapping (Knowledge Graph → rag+agents; Recovery/rollback → agents; Tool Calling & Evals → agents+evals-observability). Structure per guide: core concepts → design trade-offs (interview framing) → common questions with answer sketches → `Sources:` section (mechanism A: repo paths + librarian wiki page titles). ~150–300 lines each.
**Snippet** (sources footer):
```markdown
## Sources
- notes/rag.md, notes/prompt_injection.md (this repo)
- ../generative-ai/readings/0.rag/ — RAGAS, Self-RAG papers
- librarian wiki: [[RAG Retrieval Strategies]], [[RAG Evaluation]], [[Agentic RAG — Advanced Patterns]]
```
**Test**: `for f in interviewing/guides/{rag,agents,evals-observability,security-safety,context-engineering-cost}.md; do grep -q "## Sources" $f || echo MISSING:$f; done` → no output; `grep -rl "wiki/private\|project-g\|va-" interviewing/guides/ | wc -l` → 0
**Done when**: 5 guides exist, each with Sources; zero private/client references.

#### Step 6: Study guides — foundations batch (5 guides)
**Files**: `interviewing/guides/{llm-fundamentals,ml-foundations,data-engineering-mlops,system-design,product-business}.md`
**What**: Same recipe. `llm-fundamentals` pulls readings/general classics (attention, BERT, InstructGPT, Constitutional AI, ReAct, CoT/ToT) + nn-zero-to-hero; `ml-foundations` pulls data-science/ (Ng case-study quizzes!) + folds in SQL/analytics pointers; `data-engineering-mlops` summarizes the DataTalks module structure as an interview checklist; `system-design` compiles case_interview.md's handbook section + librarian's three system-design writeups (as drill references, scrubbed); `product-business` compiles the case/ROI/trade-off framing from notes + F4 research.
**Test**: same Sources/private-scrub checks as Step 5 over the batch.
**Done when**: all 10 guides exist and README links resolve (`grep -o 'guides/[a-z-]*\.md' interviewing/README.md | while read f; do test -f interviewing/$f || echo DEAD:$f; done` → empty).

--- *Phase B review boundary: Ramsey reviews guide quality on 1–2 samples before rounds* ---

#### Step 7: Interview-round guides (10 files)
**Files**: `interviewing/rounds/{recruiter-screen,coding-challenge,technical-questions,system-design-round,code-review-round,case-study,project-deep-dive,behavioral,customer-simulation,leadership-rounds}.md`
**What**: One per round type (groupings per Open Q4). Structure: what's tested → format & 2026 trends (from research F4/F5, cited) → prep checklist → question bank → per-role weighting → links to the relevant study guides. `case-study.md` absorbs the online/offline split + take-home presentation; `leadership-rounds.md` covers CTO/HoP rounds + reverse-interview question bank; `code-review-round.md` references librarian's SANYI drill pattern (scrubbed).
**Test**: `ls interviewing/rounds/*.md | wc -l` → 10; every file `grep -q "Per-role weighting"`.
**Done when**: 10 round guides exist, each linking ≥1 study guide and listed in README.

#### Step 8: Close the librarian scrape loop
**Files**: `librarian/etl/scrape_repos.py` (`EXTRACT_GLOBS`, lines 32-39; docstring lines 4-5), `librarian/raw/repos/repos.txt` (comment block, lines 4-9)
**What**: Add `interviewing/**/*.md` to the per-repo extraction globs; update the repos.txt header comment to document it. Run the scraper; verify the KB lands in `librarian/raw/repos/`. Do **not** run wiki ingest (out of scope). Note: librarian repo has its own SANYI.md — check the change against its contract before staging.
**Snippet** (after line 39):
```python
EXTRACT_GLOBS = [
    ...
    ".agents/**/*.md",
    "interviewing/**/*.md",   # learn-ai-engineering interview KB
]
```
**Test**: `cd ~/workspace/librarian && uv run python etl/scrape_repos.py && ls raw/repos/ | grep -i learn` then confirm interviewing files present in the scrape output.
**Done when**: scraped copies of `interviewing/README.md` + guides exist under `librarian/raw/repos/`; librarian `git status` shows only intended changes, staged for Ramsey.

### Test Plan
No test suite (content repo). Per-step shell checks above, plus final sweep before each Ramsey commit:
- `grep -rl "utm_source\|project-g\|wiki/private" interviewing/` → empty
- `git -C ~/workspace/learn-ai-engineering status --porcelain | grep -c readings` → 1 (README only)
- All README links resolve (Step 6 dead-link loop, extended to rounds/)
- Librarian scrape run completes and picks up the KB (Step 8)

### Risks & Rollback
- **Public-repo leak (highest)**: readings binaries or client-flavored wiki content reaching GitHub. Mitigated by Step 1 gitignore gate + private-scrub greps in Steps 5–7; commits are manual (Ramsey), providing a second gate. Rollback pre-push: `git reset`; post-push would require history purge (avoid — hence the gates).
- **Dump still growing**: new Notion files after Step 2 miss the cleanup pass. Mitigated by Open Q2 confirmation; late arrivals get the Step 2 recipe applied individually.
- **Guide drift vs librarian**: accepted by design; guarded by scrape→ingest conflict flagging. If a guide is later contradicted, librarian's `_conflicts.md` surfaces it.
- **Scraper change breaks librarian etl**: small glob addition; verify with the Step 8 run; rollback = revert the two-line diff. SANYI check before staging.
- **Rollback general**: all work is additive files on main (no history rewrites); `git clean`/`git checkout` restores any step.

## Execution Log

### Step 1 ✓ DONE — 2026-07-17
- Deleted 7 personal/internal files from readings/ (Q1 list + `B Test Analysis-090326-112852.pdf`).
- Appended readings ignore rules to `.gitignore`; wrote `generative-ai/readings/README.md` index; renamed `observability.md.m` → `observability.md`.
- Checks: readings shows only README as untracked ✓; rename ✓.
- **Deviations:** (1) also deleted `B Test Analysis-090326-112852.pdf` — not in the Q1 list but same internal Notion-export naming pattern (`-090326-`) as the DATA-* docs; flagged for Ramsey. (2) 8 readings PDFs were **already tracked** pre-plan (arXiv/research papers: attention, wavenet, batch-norm ×2, bengio LM, conversational-ai, Rasa ×2) — left tracked (papers, not books; already public; gitignore doesn't affect tracked files). Untrack with `git rm --cached` if preferred.

### Step 2 ✓ DONE — 2026-07-17
- 19 files now in `interviewing/notes/` (17 renamed kebab-case + flattened `agents-*` + new `reading-list.md`); `agents/evals.md` duplicate deleted; `table_of_contents.md` split (5 knowledge chunks appended to matching notes under "Salvaged from…" headers; head/tail → `reading-list.md`).
- All notes carry provenance frontmatter (origin/confidence/sources/cleaned); `rl.md` tagged `confidence: low` + mixed-language flag, Chinese headers translated inline.
- Checks: 0 files missing frontmatter; 0 utm_source refs; duplicate + TOC gone ✓.
- Deviations: none.

### Step 3 ✓ DONE — 2026-07-17
- All 10 images renamed descriptively; 8 placed inline (6 filename-matched screenshots, 9-RAG-architectures → rag.md, two-layer eval diagram → eval-harness.md anchor), 2 unplaced (trends infographic, lifecycle diagram) listed in `notes/reading-list.md`.
- Remaining refs to never-exported Notion images (≈70 incl. 6 dated screenshots that aren't in images/) converted to explicit `*(missing diagram …)*` placeholders.
- Checks: 0 broken `!image`/`!Screenshot` lines; 10 inline image refs ✓.
- Deviations: plan expected most refs to be restorable; in fact only 10 images were exported — the placeholder convention covers the rest (research F5b assumption "If wrong" case).

--- Phase A complete — awaiting Ramsey commit ---
