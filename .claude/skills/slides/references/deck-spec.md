# Deck spec — `slides/deck.yaml` and `slides/lectures/*.yaml`

`scripts/slides/build_deck.py` renders one YAML file into a 16:9 `.pptx` in the course's
house style (navy title bar with an orange edge, breadcrumb strip, white cards with
coloured stripes, tinted takeaway strip). The style comes from
`05-graph-engineering/sources/langgraph_extended.pptx`. The worked example is
`ai-engineering/01-prompt-engineering/slides/deck.yaml`.

## Top level

```yaml
deck:
  title: Prompt Engineering                    # title slide, left panel
  subtitle: Writing the document the model completes
  tagline: |-                                  # small text under the orange rule
    Tokens · Anatomy · Techniques
  byline: optional
  reference: "Notes: ai-engineering/01-prompt-engineering"   # bottom of the title slide
  output: prompt-engineering.pptx              # relative to the YAML; default <pillar>.pptx
  notes: speaker notes for the title slide

parts:
  - title: Foundations                          # "Part 1 · Foundations" in every breadcrumb
    summary: How models read prompts · Prompt anatomy   # shown on the title slide and the divider
    divider: true                               # navy section slide before the part (default true)
    agenda: true                                # numbered + listed on the title slide (default true)
    overview: true                              # this part opens the deck; exempt from the beat check (default false)
    notes: speaker notes for the divider
    slides: [...]
```

Use `agenda: false, divider: false` for a closing part (rules of thumb, where next). It gets
no number and no divider.

An `overview: true` part is still an agenda part: it gets a number, a divider and a line on the title slide.

## Every slide

| Key | Meaning |
|---|---|
| `layout` | one of the layouts below (required) |
| `title` | title-bar text (required). Keep it under ~60 characters |
| `kicker` | small line at the right of the breadcrumb strip |
| `lead` | one sentence under the breadcrumb, before the body |
| `takeaway` | tinted strip at the bottom: the one line to remember, and the flashcard answer. Required on every content slide except `statement` |
| `recall` | optional flashcard question when the title is not one. Not drawn on the slide |
| `source` | note path, shown in the footer and appended to the speaker notes |
| `notes` | speaker notes: what to say, context left off the slide |
| `level` | `core` (default), `practice` or `deep`: the audience this slide is for. See Levels below. Any other value stops the build |
| `beat` | `problem`, `fundamentals`, `practice`, `pitfalls` or `wrap`: what this slide does in its part. See The story. Any other value stops the build |

**Inline markup.** In any text, `**bold**` and `` `code` `` are supported, and nothing else.

**YAML traps.**
- Quote any string that starts with `*`, `[`, `{`, `"`, `` ` ``, `-` or `#`.
- Quote any string that contains `: `.
- Quote table cells that contain a comma. An unquoted comma inside `[a, b, c]` splits the cell. The builder stops with an error naming the row.
- Quote values that contain `?` inside a flow mapping or sequence (`{label: Exists?}`, `[a, Pass?]`). Otherwise PyYAML fails to parse them.
- Quote `Yes`, `No`, `On`, `Off`, `True` and `False`. Unquoted, they become booleans and render as "True" or "False".
- A bullet such as `- Lead term: explanation` is a mapping, not a string, and renders as an empty bullet. Quote it.

**Images.** `.png`, `.jpg` and `.svg` work. Check the real format with `file`, because downloaded "`.png`" files are often WebP, which fails. Convert them with `sips -s format png in.png --out out.png`.

**Image size.** Images are embedded at about 220 dpi of their displayed size, never larger, and as JPEG when that is smaller. Plan on 60–150 KB per image slide. The whole `.pptx` must stay under 1000 KB, which is the pre-commit limit, so a deck has room for about 6–10 image slides. Give each one a reason to be there.

## Levels

One `deck.yaml` holds the whole lecture, and a build can draw a shorter talk from it. Each level adds to the one before.

| Level | Meaning |
|---|---|
| `core` | tells the idea to any audience. A slide with no `level` is `core` |
| `practice` | adds how it is done |
| `deep` | adds the code and math |

```bash
make slides PILLAR=<pillar> LEVEL=core      # writes slides/<topic>-core.pptx next to the full deck
```

A filtered build keeps the title slide, every part's divider, the closing parts whole (`agenda: false`, whatever their
slides' levels) and every slide at or below the requested level. A part left with no slides is dropped, from the title
slide's agenda too, and the remaining parts renumber. `PDF=1` writes `<topic>-<level>.pdf`.

Filtered files are gitignored and never overwrite the full deck, and `make deck-check` does not look at them. The story
rules and coverage are checked against the full deck, so a filtered build reports the same story warnings as a full one.

## Layouts

### `bullets`
```yaml
bullets:
  - plain string
  - text: "**Lead** item"
    sub: [sub-bullet, sub-bullet]
aside:            # optional right-hand card (title/body/bullets/accent) …
  title: The one idea
  body: …
# … or a bare code block on the right: aside: {code: "…", lang: python} with no title
```

### `compare`: two cards side by side
```yaml
emphasis: right          # right (default) | left | none: which card gets the navy band
left:  {title: …, bullets: [...], body: …, code: …, tag: "footer line", accent: "D4621A"}
right: {title: …, bullets: [...], tag: …}
```

### `cards`: 2–4 in a row, or 5–6 laid out in rows of 3
```yaml
cards:
  - {title: …, body: …}          # or bullets: [...], code: …
  - {title: "So…", accent: "0EA5C9", body: …}   # accent recolours the stripe
```

### `table`
```yaml
header: [Rule, Weak, Strong]
widths: [2.2, 3.2, 5]      # relative column widths
rows:
  - [cell, "cell, with comma", "**bold** cell"]
highlight: [1]             # 0-based row indices to tint
bold_first: true           # bold the first column (default true)
```
Up to about 8 rows of short cells fits. For more, split the table across two slides.
The table layout ignores `bullets`: put any takeaway in the title or on its own slide.

### `flow`: left-to-right boxes with arrows
```yaml
steps:
  - Plain label
  - {label: Model, sub: proposes a call, accent: "1E3A5F"}
loop: repeat until done      # optional green return arrow under the boxes
end_accent: true             # last box orange (default true)
bullets: [...]               # or caption: one line
```
3–5 steps fit. Keep each label to 1–3 words and put the detail in `sub`.

### `steps`: numbered rows
```yaml
axis: weaker → stronger guarantee   # optional vertical arrow label at the left
steps:
  - {title: Ask for it, text: "…"}
  - {title: …, text: …, n: "★", accent: "D4621A"}
```
Fits 4–6 steps. Use it for ladders, criteria, and ordered procedures.

### `code`
```yaml
lang: python        # chip text on the code block
code: |-
  …
bullets: [...]      # optional: code on the left, bullets on the right
```
Keep code under about 16 lines and 60 columns when it has side bullets. Without bullets it can be about 90 columns wide.

### `statement`: one big sentence
```yaml
statement: An LLM is a document-completion engine.
attribution: smaller line under it
```

### `image`
```yaml
image: ../sources/images/wei-chain-of-thought-fig1.png   # relative to the YAML; .png/.jpg/.svg (SVG is rasterised)
caption: Standard vs. CoT prompting (Wei et al., 2022)
bullets: [...]                      # optional: image left, bullets right
```

## Palette (for `accent`)

| Hex | Use |
|---|---|
| `1E3A5F` | navy: default, structure |
| `D4621A` | orange: emphasis, the answer, the warning |
| `0EA5C9` | teal: the "so what" card |
| `0F7490` | dark teal: alternative or secondary |
| `5B21B6` | purple: the occasional third category |
| `94A3B8` / `CBD5E1` | greys: de-emphasised steps |

## The story

A deck is the lecture a teacher would give over the notes, not the notes compressed. The builder
warns on each rule it can check, so `STRICT=1` fails until they hold.
It also warns on a content slide with no `recall` whose title is not a question, and on a list question
in `recall` answered by a one-line takeaway.

Each build stamps the sha256 of `deck.yaml` into the pptx. `make deck-check`, part of `make test`, fails when a
stamped deck no longer matches its yaml, and reports decks with no stamp without failing them.

- **Spine.** Every part runs problem, what breaks, principle, technique, evidence, what you do on
  Monday. The first slide of a part is a `statement` or `image` that poses the problem. The last
  one's `takeaway` closes the part.
- **Beats.** A part runs fundamentals, then practice, then pitfalls, and `beat` on each slide says which it is
  (`problem` and `wrap` mark the slides around them). The deck opens with an overview part (`overview: true`) that says
  which problems exist, which model families answer them, and where this pillar sits in the course. These checks apply
  only to a deck where at least one slide sets `beat`: the builder warns when an agenda part has no slide for one of
  `fundamentals`, `practice` or `pitfalls` (it checks that they are there, not their order; an overview part is exempt),
  and when the first agenda part is not marked `overview: true`.
- **Layout mix.** No layout above 25% of the deck. No three consecutive slides with one layout.
  Each part has at least one `code` block or worked example and one `image` or `flow`. An `overview: true` part owes no code.
- **Flashcard pairs.** `title` (or `recall`) is the prompt and `takeaway` is the answer. Librarian
  imports one card per slide and attaches it to the lesson named in `source:`, so write a takeaway
  that stands alone. `source:` must name the note file, as in `notes/03-estimation.md`.
- **Coverage.** Every note in the pillar has at least one slide with `source:` pointing at it.
- **Size.** 30 to 45 content slides for a pillar of 10 or more notes, 15 to 30 for a smaller pillar,
  15 to 25 for a programming module. `deep` slides don't count towards these limits, because the talk is the deck without them.

Closing parts (`agenda: false`) are exempt from takeaway and part-mix checks.

## Lecture series

A pillar can be taught as a series of full lectures instead of one deck: an overview, then one lecture per note. Each
lecture is its own file, `<pillar>/slides/lectures/NN-slug.yaml`, and builds to `NN-slug.pptx` beside it. `NN-slug` is
the note's stem, because note numbers are stable ids. Reading order comes from the README's syllabus. The worked example
is `data-science/01-classical-ml/slides/lectures/`. Everything above applies, apart from the differences below.

```yaml
lecture:
  covers: [data-science/01-classical-ml/notes/01-statistical-foundations.md]   # repo-relative
  requires: [data-science/01-classical-ml/README.md]
  next: [data-science/01-classical-ml/notes/02-supervised-learning.md]
  related: [data-analytics/02-probability-and-statistics/notes/04-estimation.md]
  omits:                       # note headings left out on purpose
    - Reading map
  overview: true               # only on the opening lecture, which covers the README
```

**Graph.** Lectures are the nodes, and `requires`, `next` and `related` are the edges. Edges point at notes, because a
note exists before its lecture does. In `DECKS.md`, a target with no lecture yet is labelled "<note title>, notes only". A
generated slide shows the note title, plus the subject if it is elsewhere. Both start
naming the lecture the day one is written. `make deck-graph-check`, part of `make test`, fails on an edge or `covers`
path that does not exist, a note two lectures claim, and a cycle in `requires`. `make deck-graph` regenerates `DECKS.md`,
the curriculum-wide map.

**Generated slides.** "Where this lecture sits" follows the title slide, and "Where this leads" closes the lecture. Both
come from the `lecture:` block, so don't write them in the YAML. The story rules don't judge them.

**`section`.** Each slide names the exact `##` heading it teaches. The builder warns when a heading has no slide and no
line in `omits`, when a section or an omit isn't in the note, and when sections run against the note's order. Practice,
Try it, Interview checklist, Next, References and Further reading aren't owed slides.

**Size.** A lecture owes one content slide per 150 words of its note, at least 20 and at most 60. An overview owes at
least 15. `deep` slides count here, because a lecture is the whole note.

**Story.** The spine is checked once per lecture, not per part: open on a `statement` or `image`, include an `image` or
`flow`, include code, and include the `fundamentals`, `practice` and `pitfalls` beats. An overview owes no code and no
beats. Layout mix and flashcard rules are unchanged.

```bash
make slides PILLAR=<pillar> LECTURE=01-statistical-foundations STRICT=1 PREVIEW=1
```

`LEVEL=` works as it does for a single deck. Previews are in `slides/lectures/.preview/<stem>/`. A YAML image path has
one more `../` than in `deck.yaml`: `../../../sources/images/...` from a pillar in `data-science/`.

## Writing rules

- **One idea per slide.** The title states the claim or the topic. The takeaway states what to do about it.
- **The slides support the talk; they are not the notes.** Put numbers, names and short phrases on the slide. Put the explanation, caveats and citations in `notes`.
- **Keep the evidence.** If the note has a number (an ablation, a benchmark delta), put it on the slide in bold. Numbers are what people remember from a lecture.
- **Pick the layout from the content's shape.** Contrasts get `compare`. Choosing between options gets `table`. A pipeline or loop gets `flow`. A ladder or ordered list gets `steps`. A thesis gets `statement`. Avoid putting everything in `bullets`.
- **Bullets have at most 6 items and 2 lines each.** If the builder shrinks text below about 14pt, cut words.
- **Attribute.** Every content slide gets `source:` pointing to its note. Name the paper and year in the kicker when the slide is about one result.
