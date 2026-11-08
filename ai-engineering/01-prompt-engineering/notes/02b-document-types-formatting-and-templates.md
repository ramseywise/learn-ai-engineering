---
origin: synthesis
sources:
  - "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly 2024) — Ch 4–6"
  - "Bojie Li, AI Agents in Depth (2026), ch. 2 — https://github.com/bojieli/ai-agent-book"
  - https://arxiv.org/abs/2411.10541
confidence: high
cleaned: 2026-11-01
---
# 2b — Document types, formatting and templates

> The second half of [prompt anatomy](02-prompt-anatomy.md): which document type to write the prompt as, how to format injected content, how to write agent system prompts, and prompt templates.

---

## Choosing the document type

| Archetype | Good for | Notes |
|---|---|---|
| **Advice conversation** | Chat, multi-turn, tool use | The default for chat models. Can include synthetic prior turns the model treats as its own: let the assistant "ask" for each piece of context and the user "answer" with it, and the completion starts with the answer rather than another clarifying question. On a completion model the same document sidesteps unwanted RLHF habits (stylistic habits, content policing) |
| **Analytic report** (markdown) | Analysis, reasoning-then-decision | The safest default: there's a lot of markdown in training data and it's easy to parse. A `Scope` section ("This report focuses solely on novels, excluding self-help books") sets boundaries more reliably than conversational exclusions. Reports also spare the model from simulating a social exchange, but they drift: mark the switch from analysis to decision clearly. A table of contents with `# Analysis` before `# Conclusion` gives a scratchpad; a trailing `# Appendix` or `# Further Reading` heading makes a clean stop sequence |
| **Structured document** (XML / YAML / JSON) | Parseable output, complex prompts | Lets the app route parts of the output — e.g. hide a `<thinking>` block, render an `<artifact>` |

A completion model needs a transcript format as well. The book's four, each fixing the previous one's weakness: **freeform** prose with quoted speech (flexible, but hard to assemble on the fly), **script** (`Me:` / `Husband:`, easy to assemble but awkward for long or indented content such as code), **markerless** alternating paragraphs (good for long pasted text, but the model loses track of speakers and the app can't tell where the reply ends), and **structured** tags (`<me>…</me>`, which mark both speaker and end) (book, Ch 6, Table 6-2).

Trade-offs within structured formats (book, Ch 6): **XML** suits short elements where indentation doesn't matter, and the closing tag is a natural stop. Free text inside it has to escape the five entities (`&quot; &apos; &lt; &gt; &amp;`), and `<!-- comments -->` give a place for editorial hints to the model. **YAML** makes you get indentation right, which is a chore, but that precision is what you want for code: a `field: |2` block scalar preserves indentation and needs no escaping. **JSON** is escape-heavy and less readable, and the authors once advised against it. They changed their view for OpenAI models, which are trained hard on JSON because it carries their tools API, and a missing brace still breaks the whole thing.

**Case study: Claude's Artifacts prompt.** Anthropic's system prompt for Artifacts is a structured document. An `<artifacts_info>` block plays the system message and explains in prose when to create an artifact and when not to. Each worked example is an `<example>` with a `<user_query>` and an `<assistant_response>`. Inside each response, an `<antThinking>` block has the model decide whether this request deserves an artifact, and then an `<antArtifact identifier="…" type="…" language="…" title="…">` block holds the content. The app strips `antThinking` so the user never sees it and renders `antArtifact` in a side panel under its title — the transform-back step done with markup (book, Ch 6; the prompt was extracted by a user, not published by Anthropic).

**XML tags inside prompts** are the most robust way to separate parts of a complex prompt:

```xml
<instructions>Summarize the document for an executive audience.</instructions>
<document index="1">
  <source>q3-report.pdf</source>
  <document_content>{{DOCUMENT}}</document_content>
</document>
<constraints>Max 3 sentences. Plain prose.</constraints>
```

Use consistent, descriptive tag names and nest for hierarchy. Plain delimiters (`###`, `"""`) also work for simple prompts.

---

## Formatting injected content

How a piece of data (say, a weather API result) enters the prompt should match the document type:

- **Conversation:** `Assistant: It'll be sunny and 75 degrees.`
- **Report:** a `#### Weather` heading followed by a prose sentence.
- **Structured:** `<weather><description>sunny</description><temperature>75</temperature></weather>`

Whole-prompt format matters too, and the best one is model-specific. He et al. wrote the same five parts (persona, instructions, examples, output format, user ask) as plain text, Markdown, YAML and JSON. On gpt-35-turbo-0613, JSON beat Markdown on MMLU 59.7% to 50.0% (14,079 questions), and JSON beat plain text on HumanEval pass@1 59.8% to 40.2%. GPT-4-1106-preview varied far less (dispersion below 0.036 on every benchmark), and GPT-4-32k fell to 21.95% on HumanEval with JSON against 76.22% with plain text because it wrote its reasoning and skipped the code (the authors' reading of the outputs). The top formats overlapped little across model families, so a format tuned on one model should be re-tested before you move it. Structure and layout were changed together, only OpenAI models from 2023 were tested, and some of the paper's headline percentages do not match its own tables ([arXiv:2411.10541](https://arxiv.org/abs/2411.10541) (He et al., 2024-11, preprint)).

Content that doesn't fit the main flow can go in an **aside** — a clearly marked digression (a blockquote, a `Note:` paragraph, a code comment) that the document's genre already allows. An aside hints strongly without obliging the model to use it. Copilot's code completions pull in code from other files this way (book, Ch 6):

```go
// <consider this snippet from ../skill.go>
// type Skill interface {
//     Execute(data []byte) (refs, error)
// }
// </end snippet>
```

Snippet checklist: **modular** (insert or drop like list items), **natural** (reads as part of the document), **brief**, and **inert** (its token count doesn't change with its neighbors). Inertness matters because tokenization isn't additive. With OpenAI's GPT-3.5-and-later tokenizer, `"be"` + `"am"` is one token plus one token but `"beam"` is a single token, while `"cat"` + `"tail"` becomes three tokens (`c`, `att`, `ail`) as `"cattail"` (book, Ch 6, Table 6-4). Separate elements with whitespace so they can't merge. GPT tokenizers have many tokens that *start* with a space and few that end with one, so put the space at the start of a snippet, not the end. They also merge runs of newlines, so a snippet should either never start or never end with a newline. Never starting with one is usually easier, and ending every element with a newline also simplifies string handling and token counting.

**Assembly** is a packing problem: choose the elements that maximize the prompt's value within a budget of the context window minus the tokens reserved for the response. With a very large window, set a softer budget anyway, for compute and to keep out loosely relevant context. The book compares it to a 0-1 knapsack with dependencies and notes there is no standard solver, so you write your own (Ch 6).

Each element carries a **position**, an **importance** and its **dependencies**. Beginners conflate position and importance because recent content is often important, but the introduction outranks most of the middle. The book distinguishes **priorities**, a few integer tiers where every higher tier is used before dipping into the next, from **scores**, floats that rank elements within a tier (Ch 4). A typical tiering puts the central instructions and the output format at the top (they go in at all costs), explanations next, and context third. Pick one convention for whether importance accounts for length, and apply it everywhere. Dependencies come in three kinds:

- **Requirement** — one element needs another ("Richard is the protagonist of *The Beach*" before "He grew up in England").
- **Elastic** — a snippet has several versions (full → trimmed → minimal, e.g. a chapter with more and more paragraphs replaced by "..."); ask "what's the biggest version that fits?", not "does it fit?".
- **Mutually exclusive** — two snippets cover the same thing (a document and its summary, or overlapping passages); include at most one, with the shorter as the fallback.

Start with the **minimal prompt crafter**: order the elements and keep as many from the end as fit. It needs no scoring, and it works because models are trained to handle document suffixes, so it suits chat and apps that build on a main text. As the app grows, move to a greedy engine. **Additive** greedy starts empty and adds the highest-value element whose requirements are met and that fits. It copes when far more elements exist than fit, but breaks down with cyclical requirements or high-value elements that need low-value ones. **Subtractive** greedy starts with everything and removes the least valuable, pruning anything whose requirements are gone. It suits a manageable number of elements with few incompatibilities, and handles elastic snippets more easily (book, Ch 6).

An additive sketch:

```python
def assemble(snippets, budget):
    chosen, used, covered = [], 0, set()
    for s in sorted(snippets, key=lambda s: -s.priority):
        if s.group in covered:            # mutually exclusive with one already chosen
            continue
        if not s.requires <= covered:     # a requirement isn't in yet
            continue
        for version in s.versions:        # elastic: largest first
            if used + version.tokens <= budget:
                chosen.append((s.position, version.text))
                used += version.tokens
                covered.add(s.group)
                break
    return "".join(text for _, text in sorted(chosen))   # restore document order
```

Score by priority, but emit in document order. Retrieval, scoring and packing are covered in depth in [02-context](../../02-context-engineering/notes/02-context-anatomy.md).

---

## Agent system prompts: procedures, not rule piles

A long agent system prompt is an operating manual for a capable new hire. Li's Tau-Bench ablation (Experiment 2-4: airline and retail support) shows which properties of that manual matter:

| Change (all else fixed) | Effect |
|---|---|
| Tone swapped (neutral → bombastic → emoji-casual) | Little change in completion |
| **Same rules, flattened from an ordered procedure into an unordered list** | **Success fell more than 30%**; "verify identity before refund" was skipped |
| Tool descriptions removed (signatures kept) | Tool-call errors up 45% |

**Write an SOP, not a rule pile.** Numbered stages (validate → classify → preprocess → execute → verify), each with its exception branches. The model can then tell which stage it is in and what applies there, instead of searching hundreds of rules for one that fits. When an agent underperforms, **ablate before rewriting**: switch off one component at a time and see what moves.

**Make business rules executable.** "Choose the billing type that fits the task" behaves differently on every run. Is a clothing return "savings"? Is a cancellation? Product owners have to settle each edge as a decision rule: commission only when an existing bill is negotiated down; *never* on refunds or cancellations; success-probability bands map to billing models; "savings" are computed only from the current bill, never from an avoided future increase. In mature teams, **product managers own these rules**. Engineers encode them faithfully and don't invent business logic. Give the model a clear framework and let it spend its reasoning on the parts that need judgment.

**Few-shot placement.** Use 2–3 boundary-covering examples when rules can't capture the target (style, report format, tone). Skip them when the task is easy to state. Put them either in the system prompt or as synthetic first-turn messages, and keep them **byte-stable**. Per-request "most relevant" examples break the cache ([02-context](../../02-context-engineering/notes/02-context-anatomy.md#patterns-that-break-the-cache-or-the-model)).

Lab: [2-4 prompt-engineering](https://github.com/bojieli/ai-agent-book/tree/main/chapter2/prompt-engineering) (Tau-Bench ablations; needs an API key).

---

## Prompt templates

Separate the fixed skeleton from variable slots:

```
You are a data analyst. Answer the question using only the dataset excerpt.
<question>{{USER_QUESTION}}</question>
<dataset>{{DATASET_EXCERPT}}</dataset>
```

A template is the unit you version, test and optimize — see [08-prompt-optimization](08-prompt-optimization.md).

---

## Next

[Core techniques](03-core-techniques.md): examples, reasoning and the named techniques that fill in this structure.
