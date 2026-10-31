---
origin: vendored snapshot: Text Analytics with Python (kept as practice)
sources:
  - ../practice/Text Analytics with Python/Ch08 - Semantic Analysis/
  - ../sources/sarkar-text-analytics-with-python-2e.pdf
  - ../sources/bird-klein-loper-nlp-with-python.pdf
  - https://wordnet.princeton.edu/
  - https://spacy.io/usage/linguistic-features#named-entities
  - https://sklearn-crfsuite.readthedocs.io/
confidence: high
cleaned: 2026-10-31
---
# 12 — Semantic Analysis and Named Entity Recognition

> Meaning from structure rather than vectors: a lexical database of senses and relations (WordNet), sequence labelling that finds people, places and organisations in text (NER, with spaCy, Stanford tools, or your own CRF), and the formal logic that early systems used to represent what a sentence asserts. NER and relation extraction are the front end of every knowledge graph.

---

## WordNet (Sarkar ch. 8a)

WordNet groups English words into **synsets** (sets of synonyms sharing one sense) and links synsets by semantic relations. "Bank" has 18 noun and verb synsets: the river bank, the financial institution, a bank of switches, to bank a plane...

```python
from nltk.corpus import wordnet as wn
for s in wn.synsets("fruit"):
    print(s.name(), s.pos(), s.definition())
# fruit.n.01  n  the ripened reproductive body of a seed plant
# yield.n.03  n  an amount of a product
# fruit.v.01  v  cause to bear fruit
```

| Relation | Meaning | Example | Method |
|---|---|---|---|
| Synonym / antonym | Same / opposite sense | large ↔ big; large ↔ small | `lemma.antonyms()` |
| Hypernym / hyponym | Is-a (more general / more specific) | tree → woody plant; tree → oak | `hypernyms()`, `hyponyms()`, `hypernym_paths()` |
| Holonym / meronym | Part-of / has-part (member, part, substance) | forest has-member tree; tree has-part trunk; tree has-substance heartwood | `member_holonyms()`, `part_meronyms()`, `substance_meronyms()` |
| Entailment | Verb A implies verb B | walk entails step; eat entails chew | `entailments()` |
| Homonyms / homographs | Same spelling, different sense | bank (river) / bank (money) | multiple synsets |

### Similarity and disambiguation

```python
tree, lion, tiger, cat, dog = (wn.synset(x) for x in
    ["tree.n.01", "lion.n.01", "tiger.n.02", "cat.n.01", "dog.n.01"])
lion.lowest_common_hypernyms(tiger)    # [Synset('big_cat.n.01')]
lion.path_similarity(tiger)            # 0.33 ; lion vs tree: 0.07
# path_similarity = 1 / (1 + shortest is-a path length); also wup_similarity, lch_similarity

from nltk.wsd import lesk
lesk(word_tokenize("Lead is a very soft, malleable metal"), "lead", "n")   # Synset('lead.n.02'): the metal
lesk(word_tokenize("John is the actor who plays the lead"), "lead", "n")    # a leading role
```

**Lesk** picks the sense whose dictionary definition overlaps most with the context words. It is a weak baseline; contextual embeddings ([14](14-neural-text-models.md)) disambiguate implicitly and much better. WordNet's lasting uses are lemmatisation ([08](08-text-representation.md)), query expansion with synonyms and hypernyms, and as a hand-built taxonomy, an early knowledge graph.

---

## Named entity recognition (Sarkar ch. 8b)

Label spans of text with entity types: PERSON, ORG, GPE (geo-political entity), LOC, DATE, MONEY, etc. It is **sequence labelling**: one tag per token, usually in the **BIO** scheme.

| Token | Barack | Obama | visited | New | York | in | May |
|---|---|---|---|---|---|---|---|
| Tag | B-per | I-per | O | B-geo | I-geo | O | B-tim |

### spaCy

```python
import spacy
from spacy import displacy
nlp = spacy.load("en_core_web_sm")           # notebook: spacy.load('en') (spaCy 2 shortcut)
doc = nlp(text)
[(ent.text, ent.label_) for ent in doc.ents]
# [('Three', 'CARDINAL'), ('Facebook', 'ORG'), ('UK', 'GPE'), ('Zuckerberg', 'PERSON'), ('London', 'GPE'), ...]
displacy.render(doc, style="ent", jupyter=True)
```

![spaCy NER output with entities highlighted in a news paragraph](../sources/images/sarkar-spacy-ner.png)
*Image source: Sarkar, Text Analytics with Python (2nd ed.), companion repo `Ch08/spacy_ner.png`*

The notebook's text is a news paragraph about parliaments asking Mark Zuckerberg to testify. spaCy gets most entities right, mislabels a few (an organisation tagged as a person, a nationality as GPE). Counting `ent.label_` over a corpus gives a quick profile of what a collection is about.

### Stanford NER and CoreNLP

The same text through Stanford's CRF-based tagger (`nltk.tag.StanfordNERTagger`, 3-class: PERSON, ORGANIZATION, LOCATION) and through the CoreNLP server (more types, plus SUTime for dates). Both need Java and downloaded model files; the notebook's hard-coded `E:/stanford/...` paths will not exist on your machine. Today, `stanza` (Stanford's Python library) replaces both.

| Tool | Model | Types | Notes |
|---|---|---|---|
| spaCy `en_core_web_sm/md/lg/trf` | CNN or transformer | 18 (OntoNotes) | Fast, Python-native; `trf` most accurate |
| Stanford NER / CoreNLP | CRF | 3, 4, 7 or 12 | Java service |
| stanza | BiLSTM-CRF | 18 | Python; many languages |
| Hugging Face token classification | Fine-tuned BERT-style | Any | `pipeline("ner")` ([14](14-neural-text-models.md#transformers-pipelines)) |
| LLM extraction | Prompted | Any, defined in the prompt | Flexible schema; check precision |

---

## Building your own NER tagger (Sarkar ch. 8c)

When the entity types are your own (product codes, drug names, contract clauses), train a tagger. Sarkar uses the Kaggle GMB corpus (`ner_dataset.csv.gz`, ~48k sentences, 17 BIO tags: geo, org, per, gpe, tim, art, eve, nat) and a **conditional random field**.

A CRF is a linear model over the whole tag sequence: it scores features of each token *and* transitions between adjacent tags, so it learns that I-per can't follow B-geo. Features are hand-crafted per token:

```python
def word2features(sent, i):
    word, pos = sent[i][0], sent[i][1]
    f = {"bias": 1.0, "word.lower()": word.lower(),
         "word[-3:]": word[-3:], "word[-2:]": word[-2:],           # suffixes: -ton, -ist, -ing
         "word.isupper()": word.isupper(), "word.istitle()": word.istitle(),
         "word.isdigit()": word.isdigit(), "postag": pos, "postag[:2]": pos[:2]}
    if i > 0:
        w1, p1 = sent[i-1][0], sent[i-1][1]
        f.update({"-1:word.lower()": w1.lower(), "-1:word.istitle()": w1.istitle(), "-1:postag": p1})
    else:
        f["BOS"] = True
    if i < len(sent) - 1:
        w1, p1 = sent[i+1][0], sent[i+1][1]
        f.update({"+1:word.lower()": w1.lower(), "+1:word.istitle()": w1.istitle(), "+1:postag": p1})
    else:
        f["EOS"] = True
    return f

import sklearn_crfsuite
from sklearn_crfsuite import metrics
crf = sklearn_crfsuite.CRF(algorithm="lbfgs", c1=0.1, c2=0.1,      # L1 and L2 penalties
                           max_iterations=100, all_possible_transitions=True)
crf.fit(X_train, y_train)                                          # X: list of lists of feature dicts
labels = [l for l in crf.classes_ if l != "O"]                     # don't let 'O' inflate the score
print(metrics.flat_classification_report(y_test, crf.predict(X_test), labels=labels))
```

The trained model scores well on frequent types (geo, tim, per, gpe: F1 ~0.8–0.9) and poorly on rare ones (art, eve, nat: few training examples). Inspecting `crf.transition_features_` shows the learned grammar: `B-per → I-per` strongly positive, `O → I-per` strongly negative.

The notebook ends with an end-to-end pipeline: sentence-tokenise a new document, POS-tag it, build features, predict tags, and merge B/I runs into entity spans, compared with spaCy's output on the same text.

| Approach | Data needed | Strength |
|---|---|---|
| Rules / gazetteers (spaCy `EntityRuler`, regex) | None | Precise on closed lists (product codes) |
| CRF on hand features | Thousands of labelled sentences | Interpretable, fast, small |
| BiLSTM-CRF | More | Learns features |
| Fine-tuned transformer | Hundreds to thousands | Best accuracy |
| LLM prompting | Zero to few examples | New types instantly; slower, costlier |

**Evaluate NER at the entity level** (exact span and type match, as `seqeval` does), not token level: token accuracy is dominated by `O`.

---

## Semantic representations (Sarkar ch. 8d)

Before statistical NLP, meaning was represented in logic. NLTK can evaluate and prove statements:

```python
import nltk
read_expr = nltk.sem.Expression.fromstring

# Propositional logic: evaluate truth of compound statements under a valuation
# First-order logic: quantifiers and predicates, then theorem proving
prover = nltk.ResolutionProver()           # Prover9 is an external binary; the resolution prover is built in
rule  = read_expr("all x. all y. (jumps_over(x, y) -> -jumps_over(y, x))")
event = read_expr("jumps_over(fox, dog)")
goal  = read_expr("jumps_over(dog, fox)")
prover.prove(goal, [rule, event])          # False: the rule rules it out
```

Sarkar also builds a small first-order model (a domain of entities and a valuation of predicates) and evaluates quantified expressions against it. The practical descendants are triples (subject, predicate, object), knowledge graphs, and constrained output schemas. LLMs now do the extraction step; the graph and query languages took over the representation.

---

## Where this goes next

NER and relation extraction populate knowledge graphs; WordNet-style taxonomies become ontologies. Building knowledge graphs from text with LLMs, including entity resolution, is in [`../../ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms.md`](../../ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms.md).

---

## Practice

| Notebook | Covers | Runs |
|---|---|---|
| [`Ch08a - Exploring WordNet`](../practice/Text%20Analytics%20with%20Python/Ch08%20-%20Semantic%20Analysis/Ch08a%20-%20Exploring%20WordNet.ipynb) | Synsets, relations, similarity, Lesk | Runs offline after `nltk.download("wordnet")` |
| `Ch08b - Named Entity Recognition` | spaCy, Stanford NER, CoreNLP | spaCy part: needs `en_core_web_sm` (notebook uses the spaCy 2 `'en'` shortcut). Stanford parts: needs service (Java, Stanford NER jars, CoreNLP server; hard-coded Windows paths) |
| `Ch08c - Building NER Taggers` | CRF tagger on GMB, end-to-end pipeline | Runs offline; `sklearn-crfsuite`; `ner_dataset.csv.gz` included; `sklearn.externals.joblib` fixed to `joblib` |
| `Ch08d - Analyzing Semantic Representations` | Propositional and first-order logic in NLTK | Runs offline (resolution prover); Prover9 cells need the external binary |

---

→ Next: [13-sentiment-analysis.md](13-sentiment-analysis.md) — lexicons, supervised models and deep models for opinion, plus what drives it.
