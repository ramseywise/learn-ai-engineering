---
origin: book
source: "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly) — Ch 5: Prompt Content"
confidence: high
cleaned: 2026-07-29
---

# Ch 5 — Prompt Content

## Static vs. dynamic content

Two kinds of prompt content:

- **Static content**: hardcoded, defines/clarifies the general task, unchanged across users. E.g., "Which book do you think I should read next? *I mean for fun, not what kind of textbook.*"
- **Dynamic content**: pulled from variable sources, conveys context about the specific user/instance. E.g., "*The last book I read was 'Moby Dick,' btw.*"

The line is blurry and depends on how you built the app: a hardcoded rule ("don't recommend self-help books") is static/clarification; the same rule inferred from a user's message history is dynamic/context. Classify by origin (app logic vs. variable source), not by content.

## Static content: clarifying the question

Clarification matters more than expected because programmatic LLM calls don't get the live back-and-forth repair that human conversation or ChatGPT-style chat gets — misunderstandings go straight to failure. Clarification also produces **consistency**: the model handles all inputs the same way, which is a prerequisite for optimization and user trust.

Two forms of clarification:

**Explicit** — state the rule directly: `Use markdown`, `Don't use hyperlinks`, `Don't refer to dates after your knowledge cutoff of 2024-03-03`. Production systems can carry long lists of dos/don'ts (see the leaked Bing/Sydney prompt: identity rules, output-format rules, safety rules, all stated as flat imperative bullets).

Rules of thumb for writing explicit instructions:
- State positives, not negatives ("Thou shalt preserve life" > "Thou shalt not kill").
- Bolster commands with a reason — models follow rationale better than bare commands.
- Avoid absolutes — leave room for judgment ("kill only rarely...and make sure it's really appropriate").

RLHF-tuned chat models are better at following explicit instructions than base models, and the system message is the right channel for explicit instruction (models are specifically trained to prioritize it) — but no model is perfectly compliant.

**Implicit** — demonstrate rather than state, via few-shot examples (next section).

## Few-shot prompting

Adding Q/A-style examples to a prompt. Works because LLMs are strong pattern-continuers — showing examples teaches format, style, persona, *and* is often easier than writing exhaustive explicit rules, especially when the rule is hard to articulate precisely ("I know it when I see it" categories).

A prompt with no examples = **zero-shot**. Structure: `Introduction → [Question/Answer pairs] → Main question`.

Concrete example (predicting a book rating from review text): a few-shot prompt built from `(review title): (rating)` pairs teaches the model, implicitly, that ratings are integers 1–5, the text format (colon, newline), and even the *distribution* of ratings (skewed toward 4s/5s) — a lot of implicit structure that would be tedious and error-prone to spell out as explicit rules.

**Tip**: few-shot doesn't need to clarify the whole question — it's often used just to nail down output format cheaply.

**Warning**: only use few-shot when something about the task is genuinely non-obvious to the model. It lengthens the prompt and introduces the three drawbacks below — don't reach for it by default.

### Drawback 1 — scales poorly with context

If each example must carry the same rich context as the real question (e.g., full JSON user profiles), the prompt blows up: `For ${PersonA.name}, we know: ${JSON.stringify(PersonA)}, so we recommend ${BookForPersonA}` repeated per example, plus the real user. Risk is twofold: context-window overflow, and — even within budget — the model's attention has to disambiguate many long, structurally-similar blocks (echoes the multi-token "minibrain" attention mechanics from Ch. 3/4), which can confuse rather than help. Shortening examples avoids blowup but risks nudging the model away from the deeper reasoning the full-length context would have supported. Exception: if few-shot is scoped to teach *only* the output format, small stripped-down examples still transfer that one lesson fine.

### Drawback 2 — biases the model toward the examples (anchoring)

Anchoring: initial/example information unduly skews the judgment that follows. Demonstrated with a "guess the era of a name" task — same examples, different anchor years, wildly different completions (Figure 5-4, text-davinci-003).

Mitigations:
- Can't fully avoid anchoring, but cover a representative range of examples so you don't transmit an artificially narrow expectation.
- Match the **true distribution** of outcomes in your examples, not a naively "balanced" one. E.g., in the book-rating task, if ratings in reality skew heavily toward 5s, an evenly-spread example set (one of each 1–5) actively misleads the model into treating the categories as equally likely.
- Deliberately include edge cases as examples — an edge case the model never sees leads to unpredictable handling; but don't over-represent them relative to typical cases.

### Drawback 3 — spurious patterns

LLMs extrapolate from whatever pattern is present, even accidental ones. Example: examples ordered by ascending vs. descending numeric value each cause a *completely different*, pattern-following (not content-following) prediction (Figure 5-6). With only 3 examples, there's a 17% chance they land in accidental ascending order by pure luck (and same for descending) — patterns emerge from luck more often than intuition suggests, and even partial/mostly-held patterns still bias completions.

Default ordering trap: writing examples "happy path first, then edge/error cases" teaches the model "straightforward first, errors later" as a *sequence* pattern — so when the real question breaks that sequence, the model wrongly predicts "no solution" regardless of actual content (Figure 5-7, math word-problems example). Advanced fix: chain-of-thought (Ch. 8). Practical fix: shuffle examples, evaluate which subset/order improves results; frameworks like **DSPy** automate example selection/ordering against a target metric.

## Dynamic content

Dynamic content is the user- and instance-specific background the model needs — usually where most prompt-engineering time actually goes (ideation + retrieval plumbing). Two properties static clarification doesn't have to deal with:

**Latency / urgency.** Classify your application's trigger:

| Trigger | Urgency | Implication |
|---|---|---|
| Non-user trigger / fire-and-forget (e.g., email summarizer) | Low | Gather context at leisure |
| On-demand (e.g., book recommender) | Medium | Bounded wait tolerance; multi-pass LLM chains risky |
| Live/streaming response to user actions (e.g., autocomplete) | High | Every ms counts; complex retrieval likely infeasible |

Related: **preparability** — can a piece of context be computed/cached in advance because it changes rarely? If latency is tight, precompute everything precomputable; for extremely latency-critical apps it can even be worth speculatively preparing context you might not end up needing.

**Comparability.** Gather more context than you'll use, then triage (full triage method = Ch. 6). To triage, you need to compare context items:
- Is one item more useful than another?
- Does one depend on another?
- Does one invalidate another?

Practical shorthand: score each candidate item's usefulness (e.g., "their last book was X, and they loved it" → high score; "five years ago they read Y, no stated opinion" → medium). Static items get scored too since they compete for the same prompt budget — usually score high since clarity of the problem statement takes priority over context volume.

### Finding dynamic context

Two complementary methods:
1. **Mind-mapping the question** — put the question in the center, vary individual words/aspects outward, generate follow-up questions recursively ("What have I read last?" → "How did I like that?"). Tells you what you'd *want*; feasibility (API access, permissions) gets checked after.
2. **Inventory what's obtainable, then filter for relevance** — sort candidate sources along useful axes:
   - **Proximity** (near-to-app → far): current app/system state → saved app data (user profile) → info the app could start recording → public APIs (weather) → user-permissioned private data (purchase history, emails). Farther = harder to get, and needs to be more valuable to justify the cost.
   - **Stability** (slow-changing → ephemeral): stable profile info → slowly-changing history (purchases) → ephemeral state (current time, live interaction). Less stable = harder to precompute/cache, so latency mitigation gets harder too.

Recommended workflow: combine both — mind-map for ideas, inventory for feasibility, implement obvious/cheap sources first, add exotic ones as the app matures.

## Retrieval-Augmented Generation (RAG)

LLMs can't access anything outside training data unaided — asking about recent events or walled-off info yields refusal or hallucination. **RAG** (from the 2020 "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" paper): retrieve relevant content at request time, splice it into the prompt.

**Chekhov's gun fallacy**: models tend to treat *any* included context as necessarily relevant/important (mirroring a human writing/reading convention baked into training data) — so irrelevant retrieved snippets don't just fail to help, they actively mislead completions or crowd out better content. The only real mitigation is precision in retrieval, not just recall.

### Retrieval = search problem

Search string (e.g., a book summary) against a corpus of snippets, scored by relevance/similarity.

**Lexical retrieval** — mechanistic word-overlap matching (pre-LLM-era IR technique, still what powers most everyday search).
- Preprocessing: strip **stop words**, apply **stemming** (walking/walks/walked → walk).
- Basic scoring: **Jaccard similarity** = overlapping words / total unique words across snippet + query (0–1).
- Better scoring: **TF-IDF** / **BM25** — weight rarer words higher than common ones (fixes Jaccard treating "go" and "backpacking" as equally significant matches), at the cost of needing precomputed corpus-wide word-frequency stats.
- Strengths: cheap, no indexing/setup overhead, fast on small corpora, fully debuggable (a miss is explainable — mismatched tokens — and fixable via synonym lists, field-weighting, etc.). Weaknesses: defeated by typos, synonyms, language differences, paraphrase (shared words required even when meaning is shared or vice versa).

**Neural retrieval** — embed text into vectors via an **embedding model** (same Transformer lineage as LLMs but trained via **contrastive pretraining** to place semantically-similar text near each other in vector space, distance measured by **euclidean distance** or **cosine similarity**). Embedding models are much smaller/cheaper than LLMs, making large-corpus indexing practical.

Indexing pipeline (offline): split docs into snippets → embed each → store (snippet, vector) pairs in a vector datastore. Query pipeline (online): embed the query string → nearest-neighbor search → return matching snippets.

**Snippetizing** — cutting docs into search-ready chunks. Three sizing constraints: (1) under the embedding model's token limit (e.g., 8,191 tokens for 2024 OpenAI embedding models), (2) ideally one topic per chunk — mixed-topic chunks land at a confused midpoint in vector space, (3) sized appropriately for eventual prompt placement. Two cutting strategies: fixed **window/stride** (e.g., 256-word window, 128-word stride, with overlap to avoid splitting ideas mid-boundary — tunable trade-off vs. storage cost) or **natural boundaries** (paragraphs, sections — avoids mid-sentence cuts). For code, consider *augmenting* a snippet with context it wouldn't naturally include (e.g., reattach a method to its class definition) so the embedding captures full meaning.

**Vector storage**: libraries like **FAISS** for self-hosted fast nearest-neighbor search; managed options like **Pinecone.io** to avoid ops overhead.

**Neural vs. lexical trade-off**: lexical is mature, cheap, debuggable, and tunable by field-weighting; neural matches on *meaning* rather than tokens (survives paraphrase, cross-language, even cross-modality if jointly embedded) but is an opaque failure mode — a bad match gives you no lever to pull except retraining/reindexing. Don't assume neural is strictly better; pick per use case.

### Minimal RAG example (book-rating predictor)

Pipeline: embed each of the user's past reviews and index in FAISS → embed a candidate book's summary as the query → retrieve `k` nearest past reviews → splice into a prompt template (static intro + retrieved reviews + static question) → send to the LLM for a 1–5 rating prediction. Core retrieval call:

```python
def retrieve_reviews(index, query, reviews, k=2):
    query_vector = get_embedding(query)
    query_vector = np.array(query_vector).reshape(1, -1)
    distances, indices = index.search(query_vector, k)
    return [reviews[i] for i in indices[0]]
```

The retrieved snippets get concatenated into the prompt alongside static framing ("Here is a book I might want to read... Here are relevant reviews from the past... On a scale of 1–5..."), and the model's final numeric answer is grounded in that retrieved context rather than the base model's generic knowledge.

## Summarization

Complementary to retrieval: retrieval zooms in on relevant fragments; **summarization** zooms out, compressing large volumes into a synopsis. Simple case: append `Terselv summarize all of the above` to text and let the LLM compress it. Breaks down once the source text exceeds the context window — which is exactly the situation summarization is meant to solve, so naive single-pass summarization is self-defeating for large corpora.

**Hierarchical summarization**: divide-and-conquer. Split the corpus into semantic units no larger than the context window (e.g., book chapters), summarize each independently, then summarize the summaries — recursively, as many levels as needed (chapters → books → whole Bible, for a 1,189-chapter example). Cost scales with total original token count regardless of hierarchy depth, as long as each summary is meaningfully smaller (rule of thumb: ~1/10) than its source. Prefer splitting along natural corpus boundaries (chapters, files, directories); if forced to split unnaturally, avoid unbalanced groupings.

**Rumor problem**: each additional summarization layer is another chance for the model to subtly misrepresent the input, and errors compound down the hierarchy (more levels = more chances for drift) — like a game of telephone. Manageable in practice as long as summaries aren't so terse that each layer is meaningfully lossy.

**General vs. specific summaries**: summarization is lossy compression, and what gets discarded depends on what the summary is *for*. A generic summary of a vacation post keeps the highlights but may drop an offhand detail ("this book made the flight bearable") that's exactly what a downstream book-recommender needs. Fix: summarize with the end task already in mind (specific summarization) rather than generically. Trade-off: specific summaries are cheap to reuse only while the downstream question stays fixed — change the question and you must resummarize from scratch; general summaries are reusable across applications/questions since only the summarization artifact needs to be shared, not even the same LLM.

## Key takeaways

- Prompt content splits into **static** (task definition/clarification, same for everyone) and **dynamic** (per-user, per-instance context) — and clarifying the static task is a bigger lever on reliability than most people expect, because programmatic LLM calls get no conversational repair.
- **Few-shot** examples are an easy, implicit way to teach format/style/rules, but carry three real costs: they scale badly with per-example context size, they anchor the model to whatever range/distribution the examples imply, and they risk teaching spurious structural patterns (ordering, position) instead of content. Use only when the task is genuinely non-obvious.
- Dynamic content gathering should account for **latency/urgency** (how much time you actually have) and **preparability** (what can be precomputed), and should aim to over-gather then triage by usefulness/dependency/invalidation.
- **RAG** = retrieval (search problem: lexical word-overlap methods like Jaccard/BM25 vs. neural embedding-based nearest-neighbor search) + injection into the prompt; beware **Chekhov's gun fallacy** — models over-trust any included context regardless of actual relevance, so retrieval precision matters more than volume.
- **Hierarchical summarization** handles corpora larger than the context window at a cost proportional to total token count, but each level risks compounding misrepresentation (rumor problem); always summarize **toward the downstream question**, not generically, unless reuse across questions is the priority.
