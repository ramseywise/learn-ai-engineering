---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 5: Extracting domain-specific knowledge from unstructured data"
confidence: high
cleaned: 2026-07-29
---

# Ch 5 — Extracting Domain-Specific Knowledge from Unstructured Data

## Overview

Prior chapters covered KGs built from structured data (tables, knowledge bases). This
chapter addresses unstructured data — emails, chats, laws, research papers, news,
social media — as a source of business knowledge. Turning unstructured data into
knowledge requires data ingestion/processing, NLP techniques, data enrichment, ML
processing, and data modeling. Two conceptual challenges structure this work:

- **Knowledge representation** — how information is modeled so computers (and humans)
  can access it autonomously. A well-designed KG represents an ordered, connected
  version of information that would otherwise be isolated, distributed, and
  disorganized.
- **Knowledge learning** — using frameworks and technologies (NLP, LLMs) to mine
  insights from unstructured documents.

## The Archives Challenge

The chapter's running example is the **Rockefeller Archive Center (RAC)**, a repository
and research center covering philanthropy and the research sectors influenced by
American foundations. It holds records of 40+ philanthropic foundations, research
institutions, and cultural organizations, including the Rockefeller Foundation and Ford
Foundation.

**The Rockefeller Foundation**: founded 1913 by John D. Rockefeller, his son, and
advisor Frederick Taylor Gates — one of the earliest major US philanthropic
institutions. Rockefeller, at his peak, controlled 90% of US oil production and was the
wealthiest American of all time. He worried his heirs might "dissipate their
inheritances or become intoxicated with power" — a verbatim quote from the source — so
Gates pushed "permanent corporate philanthropies for the good of Mankind." Rockefeller
and Andrew Carnegie together defined the modern model of targeted philanthropy.

The Foundation's project-selection process relied on **program officers** who developed
deep domain networks and searched for recommendations. They recorded meetings, calls,
and dinners in diaries — often hastily typed, full of shorthand, abbreviations, and
domain-specific nomenclature. These diaries are a rich but messy knowledge source. If
mined properly, they could answer questions such as:

- Are there patterns that typically precede the funding of an idea?
- Do granted projects tend to follow recommendations from influential scientists or
  previous grantees?
- How many internal discussions take place before a grant is awarded?
- Are there trends in funding subdisciplines? Do they change over time?

The chapter's goal: build a high-quality domain-specific knowledge extraction system
that turns diary text into structured entities and relations, to be assembled into a KG
in the next chapter.

### The extraction pipeline (mental model)

```
Unstructured data sources → Digitization → Named entity recognition → Relation extraction
```

- **Digitization**: OCR, table extraction, image extraction/classification, object
  detection, etc.
- **Custom knowledge extraction** (NER + RE): trained traditional NER/RE models, or
  LLMs (e.g., OpenAI's GPT) used prompt-based or fine-tuned.

## Key Concepts of Knowledge Extraction

Transforming text into structured KGs centers on two fundamental processes: identifying
**entities** within text, and extracting the **relationships** that connect them. These
are the structural backbone of any KG.

### Recognizing named entities

**Named entity recognition (NER)** is an ML classification system trained to identify
mentions of named entities in raw text and assign them to predefined categories. It is
the first step from text to KG.

Business use cases for NER:

- Discovering insights by connecting documents from various sources (e.g., linking
  people mentioned in financial documents with business-registry data)
- Improving information management and data governance
- Laying the basis for a data compliance system
- Improving search capabilities
- Relating causes with effects (e.g., weather conditions and flight delays)

Generic open-source NLP libraries ship with categories like `Person`, `Location`,
`Organization` out of the box — but these are rarely sufficient for a domain-specific
task. In the RAC diary example (program officer Warren Weaver's entry), identifying
mentions of people and organizations matters, but so does identifying **conversation
topics**. The chapter introduces a `Topic` entity with three subtypes: research
`discipline`, `technology`, and `disease`.

Example diary excerpt (Warren Weaver, Oct 21, 1932) tags: `Person` (C. G. Rossby, R.,
Vilhelm Bjerknes, K. T. Compton), `Organization` (M.I.T.), and `Topic`/discipline
("aerological research," "meteorological research," "polar air masses," "temperate air
masses"). A simple dictionary-based NER system cannot identify these domain-specific
topics — this requires a **custom entity-extraction system**, built either by training a
custom NER model or by using LLMs.

### Extracting relations

**Relation extraction (RE)** is the second step: identifying semantic relations between
entity pairs within text. Example: *"Jane Austen, Victorian era writer, is currently
employed by Google."* This mentions a `PERSON` ("Jane Austen") and an `ORGANIZATION`
("Google") that are closely related — one employs the other. Capturing this relatedness
is what makes a true KG.

> **NOTE** (verbatim): "There are many ways to model this kind of relationship, such as
> `Jane Austen — WORKS_FOR -> Google` and `EMPLOYS: Jane Austen <- EMPLOYS - Google`. The
> important thing is to be consistent across documents."

## Building KGs with Large Language Models

Traditional NLP requires building task-specific training datasets, selecting model
architectures, and tuning hyperparameters — improving training-data quality is, in the
author's words, "to put it mildly, arduous."

In late 2022, OpenAI's GPT-3.5 series (including ChatGPT) demonstrated that a **large
language model** — built on the Transformer architecture — could draft letters,
summarize articles, answer questions, translate, generate code, and more from a natural
language prompt. The key concept enabling this is **transfer learning**: reusing
linguistic patterns learned on a generic task (e.g., predicting masked tokens) for
another task (e.g., RE), which drastically reduces the labeled-data volume needed.

What makes LLMs exceptional: model complexity (parameter count) and training-corpus
size/quality. Larger models need fewer data samples to reach the same test-set loss.
Historically, ML followed a **model-centric** approach — focus on architecture and
hyperparameters. A **data-centric** paradigm has since gained traction, focusing on data
engineering to improve training-data quality and quantity. Today's LLMs are powerful
enough that tasks can be formulated purely in natural language (**prompt engineering**)
with no model engineering required.

### Limitations to keep in mind

- **Hallucinations**: the tendency of a model to fabricate "facts" or false reasoning
  when there's no justification in the training data (e.g., inventing a cost figure for
  NASA's SLS rocket if it doesn't know the real one). OpenAI is working on this, but it
  remains an open issue.
- The author's stance: despite their achievements, LLMs shouldn't be called "AI" — true
  artificial intelligence is still a long way off. The recommended use is narrower:
  employ LLMs to build cleaner, more comprehensive KGs by extracting high-quality named
  entities, relations, and properties.

### Using LLMs: two roles in KG generation

```
Unstructured data → Data exploration → Prompt engineering → [iterate] → KG generation
                                              │
                                              ↓
                                        Preannotation → Human annotation → Fine-tune LLM
                                                              ↑
                                                    Human supervision: correct
                                                    outputs, add missing entities/relations
```

1. **Data exploration** — understand the domain and its challenges before writing
   prompts. Example: in the diary text, interviewee *C. G. Rossby* is introduced by full
   name once, then referred to only as "R." The extraction system must resolve these
   informal reference styles.
2. **Prompt engineering** — iteratively describe the task as precisely as possible to
   limit ambiguity and prevent the model from being "too inventive." Typically takes
   several iterations; small wording changes can meaningfully change output quality.
3. **Branch point** — if prompt-based output quality is sufficient, proceed directly to
   KG generation. If the task proves too complex for pure prompting, prepare a small
   training dataset (prompts + expected outputs), optionally **preannotated** using the
   already-engineered prompt, have humans correct/complete the annotations, then
   **fine-tune** the LLM via the provider's API (e.g., OpenAI's). If results still aren't
   good enough, add more training data and repeat. Fine-tuning costs more time and
   money but yields a model specialized to the domain with more stable, accurate output.

### Prompt engineering examples (walkthrough)

**Prompt version 1** — generic entity/relation extraction (Listing 5.1) asks GPT to
identify entities and output relations as `[ENTITY 1, ENTITY 1 TYPE, RELATION, ENTITY 2,
ENTITY 2 TYPE]`, directed (order matters), with one worked example provided (J.R. Smith /
Mary Hodge / cyclotron research).

```python
prompt_segments = dict()

prompt_segments['task'] =  # General task formulation
"""You are an expert on constructing Knowledge
Graphs from texts using named entity recognition and relation extraction.
Given a prompt, identify as many entities and relations among them as
possible and output a list of relations in the format [ENTITY 1, ENTITY
TYPE, RELATION, ENTITY 2, ENTITY 2 TYPE].
The relations are directed, so the order matters."""

prompt_segments['example'] = "J.R.Smith (Prof. Phys.) is employed by MIT
and mentioned another scientist, Mary Hodge, who works on cyclotron
research."  # An example: especially useful for complex tasks such as RE

prompt_segments['example_output'] =  # States the expected output
"""["J. R. Smith", "person", "has
title", "Professor of Physics", "title"]
["J. R. Smith", "person", "works for", "MIT", "organization"]
["J. R. Smith", "person", "talked about", "Mary", "person"]
["Mary", "person", "works on", "cyclotron", "occupation"]"""
```

This prompt is sent via the OpenAI chat-completions API, seeded as `system` (task),
`user` (example), `assistant` (example output), then `user` (the real query):

```python
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from listing_2 import prompt_segments

_ = load_dotenv()  # Loads the OpenAI API key from the .env file

OPENAI_MODEL = "gpt-4o-mini"

def openai_query(client, prompt_segments: dict,  # Function to run the stateless ChatGPT API query
  query: str):
    messages = [
        {"role": "system", "content": prompt_segments['task']},
        {"role": "user", "content": prompt_segments['example']},
        {"role": "assistant", "content": prompt_segments['example_output']},
        {"role": "user", "content": query}
    ]

    t_start = time.time()
    response = client.chat.completions.create(model=OPENAI_MODEL,
      messages=messages, temperature=0., max_tokens=2000)  # Specifies the model, temperature, and other parameters
    print(response.choices[0].message.content)
    print(f"\nTime: {round(time.time() - t_start, 1)} sec\n")

    return response.choices[0].message.content

if __name__ == "__main__":
  client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
  text = """..."""  # Text to process (Johns Hopkins Chemistry Dept. diary excerpt)
  openai_query(client, prompt_segments, text)
```

Run against a Johns Hopkins University Chemistry Department diary excerpt (D. H.
Andrews, J. B. Mayer), GPT-4o mini returns relations like:

```
["D.H. Andrews", "person", "has title", "Prof. Chem.", "title"]
["D.H. Andrews", "person", "specializes in", "thermodynamics", "field"]
["D.H. Andrews", "person", "is measuring", "specific heats of organic compounds", "research"]
["D.H. Andrews", "person", "is interested in", "mechanical models of various atoms", "research"]
["D.H. Andrews", "person", "demonstrates", "theory of the Raman spectra", "theory"]
["J.B. Mayer", "person", "has title", "Assoc. in Chem.", "title"]
["J.B. Mayer", "person", "is a former student of", "G. N. Lewis", "person"]
["J.B. Mayer", "person", "works with", "Max Born", "person"]
["J.B. Mayer", "person", "works at", "Gottingen", "location"]
["J.B. Mayer", "person", "specializes in", "energetics of crystal lattices", "field"]
```

Notable strengths: full names are recovered even where the diary only says "Mayer" or
"he" — the LLM performs **coreference resolution implicitly**, via its understanding of
document-wide context, unlike traditional RE pipelines that need a separate
coreference-resolution model. Titles are also expanded correctly ("Prof. Chem." →
"Professor of Chemistry," "Assoc. in Chem." → "Associate in Chemistry") — something no
traditional NER model could do.

**Problems surfaced by version 1**:

- **Relation-type fragmentation**: `specializes in`, `is measuring`, `is interested in`,
  `demonstrates` all represent the same underlying concept but are output as four
  distinct relation types from one short paragraph. At scale (thousands of pages), a
  Cypher query for "who works on research of organic compounds?" would need to
  enumerate every semantically-equivalent relation type — impractical.
  Node labels have the same issue: four research topics get three different labels
  (`field`, `research`, `theory`) when a human would likely use a single label like
  `topic` or `occupation`.
- **Prediction instability**: running the identical prompt/config on the same text
  twice does not guarantee the same output. On a second run, "theory of Raman spectra"
  and "straight calorimetric method" were dropped, even though the model still caught
  that Andrews described Mayer's personality (`["D.H. Andrews", "person", "describes",
  "J.B. Mayer", "person"]`) without capturing *what* was said. This demonstrates the
  instability risk of generic "identify all entities and relations" prompts for
  downstream KG tasks.

**Prompt version 2** (Listing 5.4) fixes normalization by explicitly listing entity
classes and relation classes of interest in the prompt, with explanations for
underperforming relation types, plus two guidance notes: how people are abbreviated
after first mention, and how organization/department names are abbreviated.

> **TIP** (verbatim): "Instead of using these simple lists, we could state the full,
> authoritative KG schema here, but this approach leaves the door open for output that
> includes entities and relations we haven't thought of."

```python
prompt_segments['task'] = """
...  # The same task description as in listing 5.1

Entities of interest: person, location, organization, date, occupation
(a.k.a. person's work, specialization, research discipline, interests,
occupation, technology).  # List of the most important entity classes

Top relations of interest: "works for", "works with",  # List of the most important relation classes
"student of" (link students with their teachers/advisors), "talked about"
(a person talking about another person), "talked with" (a person talking
with another person), "works on" (assignment of persons to
their occupation, work, specialization, research discipline, interests etc.).

Note that persons are often first referenced by their full name, and
then mentioned only by their surname or initials, for example: "A. N.
Richards" becomes "Richards", "ANR", or just "R.".

Note that organizations (universities, their departments) are often
shortened, for example: "University of California" is written as "U. of
Cal." or just "U. Cal.", "Department of Physics" is written as "Dept.
..." etc."""
```

This normalizes output — e.g. `works on` replaces the fragmented set for topics — though
`measures` and `specializes in` still leak through, and "Raman spectra" (vs. "theory of
Raman spectra") is inconsistent across runs, and the "straight calorimetric method"
relation is still missing.

**Prompt version 3** (Listing 5.6) expands the worked example to cover more relation
types the model struggled with — adds another `occupation` mention for the `works on`
relation and an example of `student of`:

```python
prompt_segments['example'] = "J.R.Smith, Prof. Phys. is employed by MIT
and mentioned another colleague Mary Hodge, who studies along with her
master's student John Smith radioisotopes produced by cyclotron."

prompt_segments['example_output'] = """["J. R. Smith", "person", "has
title", "Professor of Physics", "title"]
["J. R. Smith", "person", "works for", "MIT", "organization"]
["J. R. Smith", "person", "talked about", "Mary Hodge", "person"]
["Mary Hodge", "person", "works for", "MIT", "organization"]
["John Smith", "person", "student of", "Mary Hodge", "person"]
["Mary Hodge", "person", "works on", "radioisotopes", "occupation"]
["Mary Hodge", "person", "works on", "cyclotron", "occupation"]"""
```

Result: full stability in entity/relation class assignment, and correct capture of all
target relations — including organization names normalized to their long form ("Johns
Hopkins University Chemistry Department") and `works on` consistently used for
`calorimetric method`. The author calls this a "Eureka!" moment.

> **NOTE** (verbatim, paraphrase-safe summary): in the real RAC project, a few more
> iterations followed, and the output format was switched to JSON so each entity and
> relation could carry properties — enabling extraction of richer knowledge such as the
> sentiment of each `TALKED_ABOUT` relation (stored as a property) and business titles
> (an attribute of the `WORK_FOR` relation). The final prompt used for the chapter's KG
> lives in the book's code repository. Prompts were designed for ChatGPT models and
> tested on GPT-4o mini; readers should adapt them to whatever model is current, since
> the fundamentals — not model specifics — are the transferable lesson.

### Prompt engineering guidelines

- **Task description and domain-specific guidance** — a well-explained task is critical
  for output quality and stability. Experiment with formulations; add dataset-specific
  guidance (e.g., how people are abbreviated).
- **Naming of entity and relation classes** — list the entity/relation classes you care
  about in the prompt; this normalizes output. Terminology choice matters a lot: the
  chapter's own `Topic` label was renamed to `Occupation` after the team found `Topic`
  too generic — the rename alone produced much more comprehensive, stable results with
  an otherwise-identical prompt.
- **Complex and representative examples** — for complex tasks like RE, include a
  condensed but representative worked example covering complex linguistic
  formulations and all key relation types the model struggles with.
- **LLM configuration** — experiment with different LLMs and parameters, especially
  **temperature**. Higher temperature → more varied/creative output and more
  hallucination risk; lower temperature → more deterministic output. Guidance:
  creative tasks (text generation) favor higher temperature; code generation favors
  low temperature (~0.2); fact-focused tasks like entity/relation extraction should use
  **temperature 0**.
- **Testing prediction stability** — LLMs are generative and can produce different
  results on repeated runs of the same prompt against the same text. Mitigate with
  careful (non-ambiguous) prompt engineering and low temperature. If using a non-zero
  temperature, test stability by running the same prompt on the same test set multiple
  times and measuring overlap.
- **Unit-testing the prompt** — treat prompt iteration like code development: maintain a
  test list of (text snippet, expected output) pairs; periodically run the full list in
  bulk, calculate success rate, and inspect failures — this preserves prior gains as the
  prompt evolves.
- **Eyeballing a mini-KG** — at each **prompt milestone** (a point where accumulated
  prompt improvements feel like meaningful progress toward the task), deploy the prompt
  on a small document sample (a few dozen pages), build a mini-KG, and visually inspect
  it — seeing/touching a small graph surfaces improvement opportunities that reading raw
  output can miss.
- **Evaluation** — once satisfied, run a proper quantitative evaluation: process a few
  dozen pages, have a QA manager mark predictions correct/incorrect/missing, then
  compute per-class **precision, recall, and F1** for entities and relations. A QA
  manager can spot systemic failures invisible in a handful of examples. Alternative:
  use an LLM as judge instead of a human (imperfect, but so is human performance).
  Evaluation gives confidence before spending time/money on full-dataset KG production,
  and provides a baseline for monitoring future model drift.
- **Initial explorative KG** — when you don't yet know what's in the data or what the KG
  schema should be, use a quick generic entity/RE prompt (extract everything, short
  example format) to produce an unnormalized "explorative" mini-KG from a data sample,
  then navigate it for inspiration before starting real prompt engineering.
- **Be ambitious** — don't assume a task is too hard for the LLM; try it. LLMs can
  handle typos, deduce that "Prof. Chem." means Professor of Chemistry, and recognize
  "Stanford" as an organization from context. Provide full, clean entity names in
  prompt examples to get cleaner output from the start and reduce post-processing
  (entity cleansing/resolution).
- **Don't overthink** — prompt engineering here is essentially **zero-shot learning**
  (task description only) or **one-shot learning** (one example). These techniques have
  limits: complex reasoning tasks will always have imperfections because one-shot
  learning can't prepare a model for every edge case in a full dataset. Advice: do a
  couple of quick iterations, verify via mini-KG eyeballing, and move on. Once prompt
  engineering stops yielding satisfactory results, invest remaining project time in
  fine-tuning rather than never-ending prompt tweaking.

## KG Building: Traditional NLP or LLMs?

| Approach | Advantages | Disadvantages |
|---|---|---|
| **Traditional NLP** | Prediction speed (small models, fast even on CPU); infrastructure simplicity/cost (no GPUs needed); low prediction costs; easier/cheaper security for on-premises/isolated deployments | Requires in-house data science expertise; complex pipeline (NER, RE, coreference resolution, entity resolution/disambiguation must be chained); high data-annotation cost/complexity (multiple high-quality training datasets per domain, with no guaranteed outcome, especially for RE) |
| **LLMs** | Lower initial domain-customization cost (transfer learning + prompt engineering); shallow learning curve (no expert data scientists required); all-in-one NLP (one pass replaces a multi-step pipeline); generative nature yields cleaner, more accurate KGs out of the box; simpler post-processing (less cleansing/normalization/entity resolution) | Slower prediction speed even on GPUs; higher infrastructure complexity (GPUs required for both training and prediction); fine-tuning costs (OpenAI charges 10x more for running predictions with a custom model; on-prem still requires managing model versions); can be more expensive than traditional NLP for very large datasets, despite lower initial investment; higher security/on-premises deployment costs, especially without cloud access |

> **NOTE** (verbatim): "These days, many closed source as well as open source LLMs are
> made available through hyperscalers such as Amazon Web Services, Azure, and Google
> Cloud Platform, which alleviates some of the pain points we just mentioned."

The author's answer to "does traditional NLP have a place in the modern world of AI?" is
**"Absolutely!"** — substantial space remains for NLP given security requirements, cost
at scale, and streaming/low-latency scenarios. Where LLMs can't be used in production,
consider using them instead to accelerate traditional-NLP data annotation via
prompt-based preannotation.

## Takeaways

- KG construction from unstructured text requires two custom ML steps — **named entity
  recognition** and **relation extraction** — chained together, plus (for traditional
  NLP) coreference resolution and entity disambiguation.
- Generic NER categories (Person, Location, Organization) are rarely sufficient for a
  domain; domain-specific entity types (e.g., `Topic`/`Occupation` subtypes like
  research discipline, technology, disease) must be defined and iteratively refined.
- LLMs can perform NER + RE out of the box via prompt engineering, implicitly handling
  coreference resolution and title/name expansion that traditional pipelines need
  separate models for — but raw "extract everything" prompts produce fragmented,
  unstable relation and entity-class labels.
- Effective prompts explicitly enumerate target entity/relation classes, give
  domain-specific naming-convention guidance (abbreviations for people and
  organizations), and include representative worked examples — terminology choice for
  class names materially affects output quality.
- Use temperature 0 for fact-extraction tasks; test prediction stability by re-running
  identical prompts on identical text; unit-test prompts against a growing example set;
  eyeball mini-KGs at milestones; run formal precision/recall/F1 evaluation before
  scaling to a full dataset.
- If prompt engineering plateaus, fine-tune the LLM on a small human-corrected,
  prompt-preannotated dataset rather than continuing to over-iterate on prompts.
- Traditional NLP and LLMs are complementary, not mutually exclusive: choose based on
  dataset size, security/on-premises constraints, latency needs, and available
  expertise — they can coexist, or one can bootstrap training data for the other.
