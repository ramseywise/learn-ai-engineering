---
origin: synthesis
sources:
  - https://github.com/davidkimai/Context-Engineering (NOCODE/README.md, NOCODE/00_foundations/03_protocol_shells.md, 04_pareto_lang.md, NOCODE/20_practical_protocols/01–09 — snapshot 2026-08-14)
confidence: medium
cleaned: 2026-10-28
---
# 9 — Protocols: Context Engineering Without Code

> A protocol shell is a structured prompt written in pseudo-code: an intent, the inputs, an ordered process and a declared output. The model doesn't execute it. The structure is useful because it is explicit, reusable and easy to share.

---

## What a protocol shell is

The upstream NOCODE track brings the discipline of [prompt programs](08-cognitive-tools.md#prompt-programs) to people who don't write code. Every shell has the same four parts:

```
/protocol.name{
    intent="Clear statement of purpose",
    input={ param1="value1", param2="value2" },
    process=[
        /step1{action="do something"},
        /step2{action="do something else"}
    ],
    output={ result1="expected output 1", result2="expected output 2" }
}
```

| Part | Job | Common mistake |
|---|---|---|
| **Name** (`/research.literature`) | Category and variant; makes it findable and reusable | Generic names like `/do.task` |
| **Intent** | One sentence on what success looks like | A list of activities instead of a goal |
| **Input** | Everything the task depends on, as named fields | Hiding constraints inside the process steps |
| **Process** | Ordered steps, each with one action | Steps that each do three things |
| **Output** | The shape of the deliverable | "A good summary", with no structure |

This maps directly onto the input schema in [07](07-structured-context.md#1-input-schemas--how-a-task-is-presented). A protocol shell is the same idea with the process made explicit.

---

## Pareto-lang: the operation vocabulary

Process steps use a small, consistent grammar, `/operation.modifier{parameters}`:

```
/compress.summary{target="history", method="key_points", max_tokens=200}
```

The upstream reference groups operations into families. Only the vocabulary needs learning, not the exact syntax:

| Family | Operations | Context lever |
|---|---|---|
| **Information management** | `/extract`, `/filter`, `/prioritize`, `/group` | Select |
| **Transformation** | `/compress`, `/expand`, `/restructure`, `/format` | Compress |
| **Analysis** | `/analyze`, `/evaluate`, `/compare`, `/synthesize` | (reasoning) |

Operations nest and sequence:

```
process=[
    /filter.relevance{threshold=0.7, against="key_questions"},
    /extract.key_points{focus=["claims", "evidence"], max_points=7},
    /synthesize.themes{min_sources_per_theme=2}
]
```

The model has no parser for this. It reads `/filter.relevance{threshold=0.7}` as a compact, unambiguous instruction ("keep only what's clearly relevant"), and the brevity is the point: it is denser than the equivalent prose.

---

## A complete example

Trimmed from the upstream research protocols:

```
/research.literature{
    intent="Develop a structured understanding of existing work on a topic",
    input={
        research_topic="Context compaction for long-running agents (2024–2026)",
        key_questions=[
            "What compaction strategies are used in production agents?",
            "What is lost under each, and how is it measured?"
        ],
        scope_boundaries={
            include: "papers, engineering blogs from model providers",
            exclude: "tutorials, pre-2024 work"
        }
    },
    process=[
        /map{action="Build a conceptual map: foundations, research streams, terminology"},
        /explore{action="For each stream: key works, methods, results, limitations"},
        /synthesize{action="Patterns, competing approaches, consensus, open questions"},
        /evaluate{action="Rate evidence quality: rigour, empirical support"}
    ],
    output={
        map="Themed outline of the field",
        findings="Per-question answer with citations",
        gaps="Open questions worth investigating",
        confidence="High/medium/low per finding, with reason"
    }
}
```

Compare it with the prose version of the same request. The shell makes the scope, the steps and the deliverable impossible to leave out.

---

## The protocol catalogue

The upstream `20_practical_protocols/` holds about 50 ready-made shells in nine families. These are the ones worth knowing exist:

| Family | Protocols | Use for |
|---|---|---|
| **Conversation** | `/extract.information`, `/decision.analyze`, `/debate.structured`, `/feedback.progressive`, `/align.mutual` | Structuring a dialogue |
| **Document** | `/document.executive_brief`, `/document.article`, `/document.instructional`, `/document.persuasive` | Producing written artefacts |
| **Research** | `/research.literature`, `/research.analyze`, `/research.compare`, `/research.problem`, `/research.foresight` | Investigations |
| **Knowledge** | `/knowledge.extract`, `/knowledge.base`, `/knowledge.decision`, `/knowledge.learning` | Building and querying a knowledge store |
| **Creative** | `/creative.concept`, `/creative.adapt`, `/creative.remix`, `/creative.collaborate` | Ideation |
| **Meta-recursive** | `/meta.correct`, `/meta.improve`, `/meta.goal` | Self-critique and refinement ([08](08-cognitive-tools.md#the-self-correction-loop)) |
| **Interpretability** | `/interpret.confidence`, `/interpret.attribution`, `/interpret.process` | Asking the model to expose its reasoning and certainty |
| **Collaborative** | `/collaborate.human_loop`, `/collaborate.complement` | Human-in-the-loop work division |
| **Cross-modal** | `/cross.synthesize`, `/cross.augment` | Combining text, image and data inputs |

---

## Design principles

The upstream list of seven, condensed to the tests that matter:

- **One action per step.** If a step needs "and", split it.
- **Inputs, not assumptions.** Anything the task depends on is a named input field.
- **Declared output.** Name every field of the deliverable.
- **Modular.** A step that's useful elsewhere should be its own protocol you can call.
- **Proportionate.** A three-line request doesn't need a shell. The structure has to pay for its tokens ([03](03-budgeting-the-window.md)).

---

## Honest assessment

**What's real:** explicit intent, inputs, steps and output measurably improve consistency. That is ordinary prompt engineering ([02-prompt-anatomy](../../01-prompt-engineering/notes/02-prompt-anatomy.md)), and the shell is a disciplined way to make sure you do it. It works well for repeatable workflows, prompt libraries and handing a procedure to a non-engineer.

**What's oversold:** the syntax has no special power. A well-structured markdown prompt with the same four sections performs about the same. The upstream claims about "field operations" (`/attractor.*`, `/resonance.*`) belong to the speculative track ([99](99-speculative-field-track.md)).

**Use it when** you want a reusable, shareable procedure and the people using it don't write code. If they do write code, the same structure belongs in a prompt template with variables ([08 — prompt programs](08-cognitive-tools.md#prompt-programs)).

---

→ Next: [10-tools-and-multi-agent.md](10-tools-and-multi-agent.md) — isolating context across agents.
