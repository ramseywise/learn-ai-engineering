# Deck spec — `slides/deck.yaml`

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
    notes: speaker notes for the divider
    slides: [...]
```

Use `agenda: false, divider: false` for a closing part (rules of thumb, where next). It gets
no number and no divider.

## Every slide

| Key | Meaning |
|---|---|
| `layout` | one of the layouts below (required) |
| `title` | title-bar text (required). Keep it under ~60 characters |
| `kicker` | small line at the right of the breadcrumb strip |
| `lead` | one sentence under the breadcrumb, before the body |
| `takeaway` | tinted strip at the bottom: the one line to remember |
| `source` | note path, shown in the footer and appended to the speaker notes |
| `notes` | speaker notes: what to say, context left off the slide |

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
image: ../sources/images/cot.png    # relative to the YAML; .png/.jpg/.svg (SVG is rasterised)
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

## Writing rules

- **One idea per slide.** The title states the claim or the topic. The takeaway states what to do about it.
- **The slides support the talk; they are not the notes.** Put numbers, names and short phrases on the slide. Put the explanation, caveats and citations in `notes`.
- **Keep the evidence.** If the note has a number (an ablation, a benchmark delta), put it on the slide in bold. Numbers are what people remember from a lecture.
- **Pick the layout from the content's shape.** Contrasts get `compare`. Choosing between options gets `table`. A pipeline or loop gets `flow`. A ladder or ordered list gets `steps`. A thesis gets `statement`. Avoid putting everything in `bullets`.
- **Bullets have at most 6 items and 2 lines each.** If the builder shrinks text below about 14pt, cut words.
- **Attribute.** Every content slide gets `source:` pointing to its note. Name the paper and year in the kicker when the slide is about one result.
