# Unused-image assessment (2026-10-31)

This file lists the images under `ai-engineering/*/sources/images/` that no note or deck uses, and
says for each group whether it should be **used**, **kept** or could be **deleted**. Nothing has
been deleted. Every deletion is a separate decision.

A file counts as unused when its filename appears in no `.md` or `.yaml` file under
`ai-engineering/` or `generative-ai/`. Pillars 02, 03 and 04 have no unused images.

Verdicts:

- **Use**: worth putting into the named note. Rename it to `<author>-<short-title>-fig<N>` and move it to the destination pillar when you do.
- **Keep**: not needed now, but the information is real and hard to recover.
- **Redundant**: an identical or superseded copy of an image already in use. Safe to delete.
- **Low value**: product screenshots or launch marketing that date fast. Delete unless you want the history.

## 01 Prompt engineering (about 150 unused files, mostly from the DAIR guide)

These are left over from the DAIR prompt-engineering guide import. They still sit in its subfolders
and have not been renamed to the flat convention.

### Use: belongs in another pillar's notes

| Files | Content | Where it would go |
|---|---|---|
| `rag/` (10: rag-paradigms, rag-process, rag-taxonomy, rag-vs-finetuning, rag-evolution, rag-framework, rag-augmentation, rag-optimization, rag-metrics, rag-ecosystem) | Gao et al. 2023 RAG-survey figures | `generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md`. **rag-paradigms** and **rag-vs-finetuning** are the strongest |
| `research/rag-faith.png` | RAG faithfulness vs. prior strength (Wu et al. 2024) | `02-context-engineering/notes/04-retrieval.md` |
| `research/haystack-performance.png` | needle-in-a-haystack results | `02-context-engineering/notes/01-why-context-is-finite.md` |
| `research/infini-attention.png` | Infini-attention architecture | 02 note 01, as an aside |
| `context-engineering-guide/` (2: workflow, diagram) | DAIR context-engineering overview | `02-context-engineering/README.md` or note 01 |
| `agents/` (15: agent-components, agent-framework, cs-planning, cs-subagents, cs-verification-agent, cs-persistent-storage, customer-support-deep-agent, simple-dr-agent, parallelization, prompt-chaining, hugginggpt, autogen, chemcrow, agentbench, one unnamed screenshot) | agent architecture diagrams and a worked customer-support deep-agent | `03-harness-engineering` notes 01 and 07. The **cs-*** set illustrates sub-agents and persistent storage well. agentbench → `06-eval` |
| `research/structured_outputs.png` | structured-output reliability | `01-prompt-engineering` structured-output note |
| `research/reasoning-taxonomy.png`, `reasoning-techniques.png`, `reasoning-tasks.png` | reasoning-method taxonomies | 01 reasoning note, if it needs a map |
| `llms/` (3: trustllm, trust-dimensions, truthfulness-leaderboard) | TrustLLM benchmark | `06-eval`, if the pillar covers trust dimensions |

### Keep: real content, no current home

- `gpt-simulator.jpeg`, `gpt4-game-simulator.png`: the "LLM as simulator" framing.
- `flan-11.png`: the instruction-tuning scaling summary.
- `research/guided-cot.png`, `research/thoughtsculpt.png`: two less-known reasoning methods.

### Redundant: the notes already show the same result

- `research/reflexion-examples.png`, `reflexion-hotpotqa.png`, `reflexion-alfworld.png`: the 01 notes already use a Reflexion figure.
- `flan-2` to `flan-10` (9 files): the FLAN figures. One renamed FLAN figure is in use.
- `react/alfworld.png`: covered by the ReAct figure in use.
- `chatgpt-1.png`, `introduction.png`, `introduction/sky.png`, `prompt_chaining/prompt-chaining-1.png`: generic DAIR intro and example images. `agents/prompt-chaining.png` is the better copy of the chaining diagram.
- `synthetic_diversity/textbooks_2.png`, `synthetic_rag/synthetic_rag_1.png`, `_3.png`: siblings of `gunasekar-textbooks-are-all-you-need-sample.png` and the `dai-promptagator-*` figures in use.
- `rag.png` (root): duplicates `rag/rag-process.png`.
- `ART2.png`: a second ART pipeline figure. `paranjape-art-overview.png` is in use.

### Low value: model-launch screenshots and benchmark tables

These are dated and easy to find again on the vendors' sites:

- `gemini/` (23), `gemini-advanced/` (7), `mixtral/` (12), `llama3/` (3), `gemma/` (5), `phi-2/` (5), `grok/` (2), `claude/` (2), `olmo/` (3), `mistral-l/` (4)
- root `gpt4-1`…`gpt4-8`, `llama-1.png`, `mistral-7B-1.png`, `mistral-7B-2.png`
- `4o-image-generation/` (7), `deep-research/` (7)
- `research/groq.png`

That is about 90 files. Deleting them loses nothing the course teaches.

### Mixed

- `claude-code/` (10): Claude Code UI screenshots. They relate to `03-harness-engineering`, but they are UI captures that go out of date. Low value unless a note walks through the UI.

## 05 Graph engineering: `sources/images/unreferenced/notebooks/knowledge-graphs-for-rag/images/` (12 files)

- **Redundant:**
  - `1_0`, `1_2`, `5_1`, `7_3`, `7_5` are byte-identical to the renamed copies that are in use.
  - `7_0`, `7_1`, `7_2` are superseded, because `7_3` combines them.
- **Low value:** `1_1`, `2_0`, `2_1`, `2_2`, `6_1` are Neo4j Browser UI screenshots.

All 12 can go. The whole folder is safe to delete.

## 06 Eval: `sources/images/unreferenced/notebooks/evaluating-ai-agents/` (10 files)

- **Redundant:**
  - `lab-1/images/agent.png` is identical to the copy in use.
  - `lab-2/spans_agent`, `lab-3/router_skill_eval`, `lab-4/experiment1`, `lab-5/experiments` and `traces` are the WebP originals of PNGs that are in use.
  - `lab-5/agent_evaluators` is superseded by the figure in use.
- **Low value:** `lab-1/images/tool1`, `tool2`, `tool3` are crops of the lab's tool-definition code. The note shows that code as text.

The whole folder is safe to delete.

## Suggested order

1. Delete the 05 and 06 `unreferenced/` folders (22 files, all redundant or low value).
2. Delete the 01 low-value launch screenshots (about 90 files).
3. Move the 01 **Use** images into their destination pillars, renamed, as those notes are next revised. Then delete the 01 **Redundant** files.
4. Leave the **Keep** files where they are.
