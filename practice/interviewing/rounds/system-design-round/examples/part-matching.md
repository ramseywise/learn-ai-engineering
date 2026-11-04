---
units:
  - data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank.md
  - data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function.md
  - data-science/01-classical-ml/notes/13-automate-review-or-reject.md
  - ai-engineering/08-multimodal-engineering/notes/02-document-understanding.md
---

# Example: Finding Interchangeable Industrial Parts

## Prompt

"Industrial companies each keep their own parts catalogue, full of duplicates and of parts from different makers that would do the same job. Records are messy text, and many parts also have a scanned datasheet or an engineering drawing. Design a system that finds which parts are interchangeable."

**What the interviewer is checking**: whether you turn "find matches" into a decision with prices, and whether you separate looking similar from being safe to swap. A candidate who draws only an embedding index and a threshold has answered a search question, and this one is about what happens when a match is wrong.

## Step 1: Clarify & scope (3 min)

**Questions I'd ask**:

- What happens to a match: a suggestion to a buyer, a merged master record, or an automatic substitution on a purchase order?
- What does a wrong swap cost compared with a missed one? A seal in the wrong material can stop a plant, while a missed match costs a duplicate stock line.
- Who can confirm a match, how many can they look at per week, and do their answers come back as labels?
- Do we have any confirmed matches today, and from how many customers?
- Do matches stay inside one customer's catalogue, or cross customers?
- May one customer's data train a model that serves another? Can it leave their network?
- Roughly how many records per customer, and how many new ones per day?
- What share of records has a datasheet or drawing, and is it a scan, a PDF with text, or a CAD file?

**Assumptions after clarify**:

- Output is a merge into a master record, with an audit trail. Merges can be undone, but purchase orders placed in between can't.
- A wrong merge costs far more than a review, which costs about the same as a miss. We'll get real prices from the customer and treat them as inputs.
- A small team of engineers reviews matches, and their decisions are stored as labels.
- Matches stay inside each customer's catalogue. Customers share one model, with per-customer thresholds, and raw records stay separated by customer.
- Batch first. A nightly run is enough for a catalogue that changes slowly, plus a synchronous check when someone creates a part.

## Step 2: Requirements (2 min)

**Functional**: read attributes from records and documents, propose candidate pairs, score them, and route each to merge, review or leave. Merges are explainable and reversible. Every decision is logged with the model version and the attributes it relied on.

**Non-functional**: a precision floor on automatic merges, set by the prices. Recall is measured on a fixed random sample of records with all their matches labelled, so it includes pairs the retrieval step missed. A review queue no larger than the team can clear. Candidate generation that scales with records, not with pairs of records.

**Say out loud**: "I won't quote an accuracy target until I have prices. The thresholds come from what a wrong merge costs compared with a review."

## Step 3: Design (15 min)

### Pipeline

```text
Records + documents
  → Normalise text, part codes and units
  → Read attributes: rules on text; document model for scans and drawings
      each attribute carries a value, a source and "unread" as a real state
  → Retrieve candidates per record: lexical first, top k; add a tuned encoder
      to the union once it beats lexical on recall at the same k
  → Score pairs: gradient boosting on similarity and attribute-agreement features
  → Calibrate per customer, with partial pooling
  → Route by cost: merge / review / leave
      a stated critical-attribute clash can't auto-merge
  → Merge into groups (transitive closure), with a guard on group size
  → Reviewer decisions → labels → retrain, re-tune thresholds, re-run
```

### Key trade-offs narrated

**Retrieval sets the ceiling, so tune it first**: no pair scorer can recover what retrieval drops. Closure can, but only through a chain of offered pairs, and it brings wrong links with it. In [the course's capstone](../../../../../data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function.md#all-four-stages-together), on generated catalogues of about 1,766 records with character TF-IDF retrieval at k=10, only 0.505 of true pairs were ever offered to the model. Going to k=30 raised that to 0.681 for 2.8 times the candidates. Merges plus confirmed reviews at k=10 closed to 0.670 of true pairs, with 4 wrong pairs implied. Measure recall of retrieval on its own, because a pair score computed only on retrieved pairs can't show this loss. See [blocking](../../../../../data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank.md#blocking-cut-the-candidates-and-accept-what-that-costs).

**Label "interchangeable", not "looks alike"**: the training target is a choice you make. An o-ring in NBR and one in FKM read almost the same and can't be swapped. Tuning an encoder helps the right record reach the list, but [about half the top 10 were still look-alikes after tuning](../../../../../data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function.md#what-tuning-doesnt-replace) in that chapter's setup. So the encoder proposes and attributes decide.

**Attributes as features, and also as a hard stop?** In the capstone, hiding attributes from the model cost 0.78 euros per record, at assumed prices of 200 for a wrong merge, 3 for a review and 5 for a miss. A hard stop on stated conflicts caught no wrong merges. Every clashing pair above the merge threshold was a true pair, with a mistyped or misread attribute, even when the model couldn't see attributes. I'd keep the stop anyway for [a different reason](../../../../../data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank.md#similar-is-not-interchangeable): it's explainable to an auditor and it can't drift. Say that you're choosing it for those reasons and not for the error rate.

**Three routes, thresholds from prices**: [price each route](../../../../../data-science/01-classical-ml/notes/13-automate-review-or-reject.md#price-each-route-and-the-thresholds-follow), and the thresholds follow. A two-way decision forces every uncertain pair into either a merge or a miss. In the capstone, removing the review band raised wrong merges from 0.4 to 8.4 per catalogue. Thresholds from the price formula need calibrated scores. A search on labelled data needs only the order, and the capstone searched without calibrating. That search needs a catalogue of production size, because a small one gives a noisier threshold: across three tuning draws and three search settings, a quarter-size catalogue gave 1.2 to 6.6 wrong merges, against 0 to 2.4 at full size. The ranges overlap, so don't trust a wrong-merge count from a single search.

**Closure amplifies mistakes**: one wrong link can join two whole groups. In the capstone's no-review arm, 8.4 wrong pairs became 17.2 after closure. So score groups as well as pairs, flag groups that grow past a limit, and check that an unmerge restores the old groups. See [closing predictions](../../../../../data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank.md#splitting-pairs-without-leaking-the-answer).

**Which document model**: I'm assuming datasheets from many makers, which is a long tail of formats at modest batch volume, so [the route table](../../../../../ai-engineering/08-multimodal-engineering/notes/02-document-understanding.md#choosing-a-route) points to a vision-language model with a schema and strong validation. Check it on your own pages, and validate each value against the attribute's type and unit. If one customer's scans turn out to have one or two known layouts, an OCR pipeline is the better start. [Fine-tune](../../../../../ai-engineering/08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model.md) only after you've shown the errors come from the model and not from the resolution. Drawings need their own test: [small dimensions, tolerances and symbols fail differently](../../../../../ai-engineering/08-multimodal-engineering/notes/02-document-understanding.md#drawings-and-3d-parts) from ordinary pages, and a dropped tolerance isn't a typo. [What serving costs](../../../../../ai-engineering/07-inference-engineering/notes/08b-serving-encoders-and-vision-models.md) favours a batch run here.

**Customers differ**: one shared score can mean different risks at different customers. Thresholds per customer overfit when a customer has few labels, so use [partial pooling](../../../../../data-science/01-classical-ml/notes/13-automate-review-or-reject.md#when-customers-differ). Splits need the same care: [keep a spec out of both train and test](../../../../../data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank.md#splitting-pairs-without-leaking-the-answer), or the score measures memory.

### Sidecars

- **Bootstrap labels**: exact part-code matches and a first reviewed sample. Also label a fixed random sample of records, and for each one find all its matches by checking its whole family-and-dimension block. Reviewer labels only cover what the model already found, and random pairs are too rarely matches to label directly: about 1 in 400 in the capstone.
- **Eval set**: [frequencies as in production for the headline, rare costly cases in separate slices](../../../../../generative-ai/08-eval/notes/03-eval-datasets.md#coverage-and-balance).
- **Model gate**: a new model [replays held-out decisions](../../../../../data-engineering/06-ml-platform/notes/02-experiment-tracking-and-model-registry.md) and runs in [shadow](../../../../../data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring.md#shadow-and-canary) before it can merge anything.

## Step 4: Shortcomings (3 min)

- **Wrong attributes pass the rule.** If a record states the wrong material, a rule agrees with it. In [the generator behind these numbers](../../../../../data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank.md#similar-is-not-interchangeable), a 2% mistype rate produced about 23 unsafe accepts per catalogue from the rule alone. Sample the merge pile for audit, not only the review pile.
- **Selection bias in labels.** Reviewers see what the model sent them, so its misses never get labelled unless you sample outside the queue.
- **The evidence here is generated.** Every capstone number comes from a catalogue generator with mistype and missing rates we chose. They show what to measure, not what a real catalogue will give.
- **Thin 3D evidence.** I'd treat retrieval from CAD geometry as a later experiment, because the course found few part-to-part retrieval scores with their setup stated.

## Step 5: Close with measurement (2 min)

**Metrics**:

- Retrieval: recall of true pairs at k, on the fixed sample of records.
- Pairs: precision of automatic merges from the audit sample, and recall.
- Groups: wrong pairs after closure, and the largest group's size.
- Reviewers: queue size and age, and how often they disagree with the model.
- Money: euros per record at the agreed prices, the number that decides between arms.
- Per customer: all of the above, since a good average can hide one bad customer.

**Future improvements**:

- Add a tuned encoder to the union, compared on recall at the same k. The capstone didn't run this.
- Matching across customers, if contracts allow it.
- Prices that vary by part class, so critical parts get stricter thresholds.
- Active learning for the review queue, once a random sample protects the eval.
- CAD geometry as another retrieval channel.

---

**Study refs**: [Entity matching](../../../../../data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank.md); [Learning a similarity function](../../../../../data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function.md); [Automate, review or reject](../../../../../data-science/01-classical-ml/notes/13-automate-review-or-reject.md); [Document understanding](../../../../../ai-engineering/08-multimodal-engineering/notes/02-document-understanding.md). Run the capstone with `uv run 06_parts_capstone_lab.py` from `data-science/05-time-series-and-recommenders/practice/`.
