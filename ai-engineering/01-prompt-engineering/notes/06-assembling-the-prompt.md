---
origin: book
source: "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly) — Ch 6: Assembling the Prompt"
confidence: high
cleaned: 2026-07-29
---

# Ch 6 — Assembling the Prompt

## Anatomy of a well-constructed prompt

A prompt is built from elements drawn from dynamic context + static instructions (Ch 5).
No hard rule on element count or size — projects range from three lengthy elements to
hundreds of one-liners. Common skeleton, front to back:

1. **Introduction** — frames the document type up front ("This is about recommending a
   book", PDF p. 2) so the model interprets everything downstream through that lens. The
   model has a fixed "thought budget" per token (PDF p. 2) and can't pause to re-derive
   context, so setting focus early improves output. Applies recursively: subsections with
   a distinct focus benefit from their own mini-introduction.
2. **Context (the "long parade", PDF p. 2)** — the bulk of the prompt elements.
3. **Refocus** — restate the actual question after a long context dump.
4. **Transition** — the final nudge from "problem poser" to "problem solver."

Optional trailing newline convention: not required, but ending every prompt element with
`\n` simplifies string-concat code and token-length bookkeeping. Skip it if elements don't
fit the format naturally.

## The Valley of Meh

Two competing attention effects govern how much weight the model gives different parts of
the prompt:

- **In-context learning bias** — the closer information sits to the end of the prompt, the
  more it influences the completion.
- **Lost middle phenomenon** — models recall the beginning and end of a prompt well, but
  underweight content buried in the middle.

Together these produce the **Valley of Meh** (PDF p. 3): a region in the early-to-mid prompt where
context is used less effectively than context placed at the start or the second half. It
gets worse as prompts grow, and there's no full fix — mitigate by (a) placing your highest-
value context outside the valley (start or end) and (b) keeping the prompt as concise as
possible so the valley itself is smaller.

## Refocus, transition, and the sandwich technique

For long prompts, **refocus** = restating the main question after all context has been
laid out, so the model's attention returns to the task. Most engineers pair this with the
**sandwich technique**: state the ask once at the start (introduction) and again at the
end (refocus), bracketing the context in between. The refocus can be as short as half a
line or can carry real clarifications (e.g., desired output format) if the ask is nuanced.

**Transition** is the final beat that flips the model from absorbing context to producing
an answer — as simple as a trailing question mark in a chat interface (RLHF has trained
chat models to answer the last question asked, even implicitly). Completion models need
more explicit signals. The most reliable transition technique: switch from writing *as the
asker* to writing the *beginning of the model's answer yourself*, forcing the model to
continue from there rather than restate the question. Compared across missing / naive /
refined transitions on a completion model (`text-davinci-002`), the refined version (write
the transition as the opening of the assistant's answer, ending mid-sentence with an open
quote) reliably produced a real answer instead of a clarifying question or nothing at all.
Refocus and transition are often merged: write a sentence that both restates the problem
and starts the answer.

## What kind of document?

Little Red Riding Hood principle (Ch 4): match the document format to what's common in
training data, so the completion format is predictable. Four archetypes, each fixing a
weakness of the previous:

### The advice conversation

Two-party dialogue: one party asks for help, the other (the model) provides it. Default
mode for chat models (ChatML was built around it) but works for completion models too.
Advantages: natural to write, supports multiround interactions (inject app logic between
turns), integrates well with tool calls and real-world processes. On a chat model you get
RLHF compliance benefits; on a completion model you can dodge unwanted RLHF side effects
(stylistic tics, content policing).

**Inception trick** (completion models): write the *beginning* of the assistant's answer
yourself so the model treats it as its own output and continues from there — improves
compliance and removes uncertainty about whether the response opens with throat-clearing
or gets straight to the point. Extends further: you can write entire assistant turns
yourself across a multiturn conversation, and the model will treat prior turns as things
it actually said.

> Tip: writing a prompt from the assistant's perspective frames context as if the
> assistant is answering its own question — ensures the completion starts with the answer
> rather than another clarifying question.

Four ways to format the same dialogue transcript, each suited to different needs:

| Format | Strength | Weakness |
|---|---|---|
| Freeform text | Natural quoted dialogue | Hard to assemble programmatically |
| Script format (`Me: ... / Husband: ...`) | Easy to assemble | Weak for long/formatted elements (e.g. indented code) |
| Markerless (line breaks only, no speaker tags) | Good for formatted/long pasted text | Model can lose track of who's speaking / where a turn ends |
| Structured (XML-style tags, e.g. `<me>...</me>`) | Explicit speaker + turn boundaries | More verbose |

### The analytic report

Leverages the enormous training-data volume of business/science/legal-adjacent report
writing (skip legal defense specifically). Natural fit: intro → analysis/discussion →
conclusion → optional recap, with your gathered content dropped into the discussion or
background sections.

- Use a **Scope** section to declare boundaries up front ("This report focuses solely on
  novels, excluding self-help books", PDF p. 10) rather than negotiating exclusions dialogue-style —
  models respect stated boundaries more reliably in report form than mid-conversation.
- Reports read as objective analysis, which lowers the model's simulated-social-interaction
  overhead — but you must explicitly transition from analysis mode to decision mode before
  the conclusion, or you get a meandering, hard-to-parse response.
- This format pairs naturally with chain-of-thought prompting (Ch 8).

**Recommended default format: Markdown**, for report-style prompts specifically. Reasons:
ubiquitous in training data, minimal syntax so models parse/produce it reliably, headings
give you a rearrangeable/omittable section hierarchy, indentation is mostly free-form
(use triple-backtick fences for code), renders directly for end users, and links are
easy to parse back out programmatically.

**Table of contents as a control lever.** Put a ToC at the top of a Markdown report — it
orients the model the way it orients a human reader, and doubles as a completion-control
tool:
- **Scratchpad sections** (`# Ideas` / `# Analysis` before `# Conclusion`) give the model
  room for chain-of-thought-style reasoning ahead of the answer you actually care about.
- **End markers** (`# Appendix`, `# Further Reading` after the conclusion) signal where
  the real content ends — set the marker string as a stop sequence to cut generation
  short and save compute once the task is done.

### The structured document

Formal spec (XML, YAML, JSON) instead of prose — lets you make strong assumptions about
completion shape, which makes parsing (including complex/nested output) much easier.

**Case study — Anthropic's Artifacts prompt** (abridged, extracted by @elder_plinius):
uses XML to delineate roles. `artifacts_info` plays the system-message role and explains
Artifacts; it embeds an `<examples>` block of `<example>` entries, each with a
`<user_query>` and `<assistant_response>`. Inside `assistant_response`, the model first
emits an `<antThinking>` block (private reasoning on whether this query warrants an
Artifact) and, if so, an `<antArtifact identifier="..." type="..." language="..."
title="...">` block holding the actual content. Because the structure is fixed, the app
can reliably strip `antThinking` from what the user sees and route `antArtifact` content
into the Artifact pane by its declared title/type.

**XML vs. YAML vs. JSON:**
- **XML** — opening/closing tags, optional attributes; fine for short elements, and
  indentation doesn't matter even for multiline content. Five escape sequences to watch:
  `&quot;` `&apos;` `&lt;` `&gt;` `&amp;`. Supports `<!-- comments -->` as editorial hints
  to the model.
- **YAML** — hierarchy via indentation, which is fussy to get right but ideal when you
  need exact control over formatted/code content. `fieldname: |` opens a multiline block
  that preserves indentation as-is (no escaping needed); the block ends at the first line
  indented less than the field's own "zero" level. `|2` variant fixes the zero-indentation
  explicitly (previous line's indent + 2) rather than inferring it from the first content
  line.
- **JSON** — historically discouraged (escape-heavy, less readable) but now a reasonably
  good choice for OpenAI models specifically, since OpenAI has invested heavily in
  reliable JSON generation to support its tools/function-calling API.

## Formatting snippets into the document

How you embed a piece of retrieved data (e.g. a weather API result) depends on the
document type:

- **Conversation transcript** — phrase it as a Q&A turn:
  `Assistant: It's going to be {{ weather["description"] }} with a temperature of {{ weather["temperature"] }} degrees.`
- **Analytic report** — state it as natural-language prose under its own heading:
  `#### Weather Forecast\n{{ weather["description"] }} with a temperature of {{ weather["temperature"] }} degrees`
- **Structured document** — just serialize the object directly:
  `<weather><description>sunny</description><temperature>75</temperature></weather>`

**Asides** work across all formats: an explicitly marked side remark (`// <consider this
snippet from ../skill.go> ... // </end snippet>`) gives the model a strong hint about
where context came from without forcing it to use that context in any particular way —
used effectively in GitHub Copilot to pull in comparison code from other files.

**Snippet quality checklist:**
- **Modularity** — snippets should be insertable/removable like list items or tree leaves;
  favor document shapes (conversation-as-list, report-as-tree) that support this.
- **Naturalness** — format data so it reads as an organic part of the document (a code
  comment inside code, a natural sentence inside prose) rather than dumped verbatim.
- **Brevity** — fewer tokens for the same information content is strictly better.
- **Inertness** — a snippet's own token count shouldn't change when adjacent snippets
  change.

**Inertness detail — tokenization isn't additive.** Concatenating two strings doesn't
concatenate their token arrays: `"be"+"am"` → tokens `[be, am]` (2 tokens) individually,
but the merged string `"beam"` tokenizes to 1 token (`[beam]`); conversely `"cat"+"tail"`
(1+1=2 tokens standalone) becomes `"cattail"` → 3 tokens (`[c, att, ail]`) once merged.
Practical mitigations: separate prompt elements with whitespace to prevent unintended
merges; prefer snippets that start with a space rather than end with one (GPT tokenizers
have space-prefixed tokens but not space-suffixed ones); never start or end a snippet with
a newline (GPT tokenizers collapse multiple newlines together) — easiest to enforce by
banning leading newlines specifically.

**Few-shot example formatting** — two options:
1. Declare examples explicitly as examples: `In the following, when I encounter a
   question like "..." I will give an answer like "..."` (PDF p. 19).
2. Fold them into the document as if they were genuinely solved prior turns — harder to
   engineer correctly but produces a smoother prompt and lets the model "believe" it
   already succeeded at this style of task, reinforcing it going forward. Especially
   effective in ChatML-style transcripts.

## Elastic snippets

Problem: sometimes one piece of source content (e.g., two relevant passages from a novel)
can be represented at multiple levels of surrounding context, and you don't know in
advance how much context budget you'll have. Three fixed options — no context around each
snippet, some context around each, or one merged snippet with linking context — trade off
size against completeness, but a fixed choice wastes budget when more (or less) space is
available.

Two general strategies for handling variable context budget:

1. **Elastic prompt elements** — maintain versions of a snippet ranging from full (entire
   chapter) through progressively trimmed (paragraphs replaced by "...") down to a minimal
   two-quotes-plus-ellipsis version. At assembly time, don't ask "does this snippet fit?" —
   ask "what's the largest version of this snippet that fits?"
2. **Multiple independent prompt elements** — generate several candidate snippets (bare
   passage, passage+some context, passage+more context) and mark them mutually exclusive/
   incompatible at assembly time, since they overlap and only one should be included. This
   requires an assembly method that supports declaring elements as incompatible with each
   other (the subject of the next section of the book).

## Key takeaways

- Prompt anatomy is introduction → context → refocus → transition; the introduction sets
  the model's interpretive frame early because it has a fixed per-token "thought budget."
- The Valley of Meh (in-context recency bias + lost-middle effect) means early-to-mid
  content is underweighted — put your best material at the very start or very end, and
  keep prompts as short as possible to shrink the valley.
- Match document type to genre-appropriate training data: advice conversation (dialogue,
  four transcript formats trading off assembly ease vs. structure clarity), analytic
  report (Markdown, ToC as both orientation and stop-sequence control), or structured
  document (XML/YAML/JSON) when you need parseable output — Anthropic's Artifacts prompt
  is a concrete XML example with `antThinking`/`antArtifact` blocks.
- The inception trick — writing the start of the model's own answer — is the most
  reliable way to force compliance and skip throat-clearing, on both completion and chat
  models.
- Snippets should be modular, natural, brief, and inert; remember tokenization isn't
  additive across concatenated strings, so pad/order snippets carefully to avoid
  unintended token-count drift.
- When context volume is variable, use elastic snippets (largest version that fits) or
  mutually-exclusive candidate elements rather than committing to one fixed granularity.
