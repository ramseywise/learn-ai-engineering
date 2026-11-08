---
origin: synthesis
sources:
  - ../references.md
  - ../practice/05_similarity_lab.py (generated catalogue)
  - ../practice/05_similarity_tryit.py
  - ../practice/similarity_train.py
  - https://arxiv.org/abs/2003.08505
  - https://arxiv.org/abs/1503.03832
  - https://arxiv.org/abs/2004.11362
  - https://arxiv.org/abs/2006.11632
  - https://arxiv.org/abs/2004.04906
  - https://arxiv.org/abs/2007.00808
  - https://arxiv.org/abs/2112.07577
  - https://arxiv.org/abs/2301.09521
  - https://arxiv.org/abs/2202.02098
  - https://arxiv.org/abs/2010.08240
  - https://arxiv.org/abs/2212.06121
  - https://arxiv.org/abs/2304.12329
  - https://www.databricks.com/blog/improving-retrieval-and-rag-embedding-model-finetuning
  - https://sbert.net/docs/sentence_transformer/loss_overview.html
  - https://sbert.net/docs/package_reference/util/hard_negatives.html
  - https://sbert.net/docs/package_reference/sentence_transformer/losses.html
  - https://sbert.net/docs/package_reference/sentence_transformer/sampler.html
  - https://weaviate.io/blog/fine-tune-embedding-model
confidence: medium
cleaned: 2026-11-03
---

# Learning a similarity function

A pretrained sentence encoder, asked to find other records of the same part in a catalogue of short part descriptions, found 13.4% of them. Character n-grams with no training found 45.6%. The same encoder, after about half a minute of training on 1,000 known matches, found 90.8%. Then the obvious next step, feeding it harder negatives, left recall where it was and changed something else.

This chapter runs that experiment. It asks when to tune an embedding model for your domain, how many pairs you need, how to build them from match labels, and what hard-negative mining really buys.

**In plain words.** A pretrained encoder learned what "similar" means from someone else's text. Tuning teaches it what similar means for you, by showing it pairs you know match, and letting everything else in the batch stand in as non-matches. Mining means searching for the non-matches the model currently likes best, and training on those. It's like a new clerk who has only read novels. Show them a thousand pairs of invoice lines that are the same part and they get far better. Then drill them on the pairs they keep confusing, and they stop confusing those, though they don't find any more of the real matches.

We don't derive the losses here. [Triplet loss and NT-Xent](../../02-deep-learning/notes/04-convolutional-networks.md#embeddings-face-verification) are in DS 02/04, and in-batch [softmax](../../02-deep-learning/notes/01-neural-networks-fundamentals.md#the-forward-pass) with its logQ correction is in [two-tower retrieval](03-two-tower-and-evaluation.md#training-in-batch-softmax-and-its-bias). This chapter uses in-batch softmax with no logQ term, since records here aren't drawn by popularity. The catalogue and the idea of a look-alike come from [the last chapter](04-entity-matching-and-learning-to-rank.md#similar-is-not-interchangeable).

## The experiment

Each record is one short description, and records of one spec are safe to swap. Here is one spec, then a look-alike, which has the same family and dimensions and a different spec:

```text
hex cap screw Garst a4-80 85Q4872 M14x50
HEX BOLT REF ONLY 1.4401 40A9059 M14X50
HEX BOLT A4-80 M14X50 17F9721
hex bolt 17F9721 M14x50 1.4401
HEXAGON SCREW ALT 39W8215 DOVRA M14X50     <- look-alike
```

The setup, from [`practice/05_similarity_lab.py`](../practice/05_similarity_lab.py), which takes 15 to 25 minutes on an Apple M4 Pro GPU:

- **Model.** `all-MiniLM-L6-v2`, a small pretrained sentence encoder, about 90 MB. Each training run is 400 steps, batch 32, learning rate 2e-5, temperature 0.05, about 35 seconds.
- **Data.** Generated catalogues of about 1,700 records. Training and test catalogues are different generations. They share no code, but about two thirds of the test specs also occur in training under another code, and they share the families and the shape of the text. Recurring specs barely help: at 1,000 pairs, recall is 0.911 on seen specs and 0.902 on unseen, with standard deviations of 0.011 and 0.015. Shared families are the generous part, and we test that below.
- **Recall@10.** Each test record queries all the others. Recall is the share of its true matches in its top 10, with the denominator capped at 10.
- **Look-alikes in the top 10.** The share of those ten slots holding a look-alike. A median spec has only three records, so most of the ten slots can't hold a match and something else fills them.
- **Reported.** Means over three seeds, with standard deviations in the lab's output.

## Frozen against tuned

```text
                                 pairs   recall  look-alikes in top 10
TF-IDF characters, no training       0    0.456    0.089
frozen pretrained                    0    0.134    0.030
tuned, in-batch                    100    0.799    0.371
                                   300    0.881    0.476
                                  1000    0.908    0.494
                                  3000    0.912    0.501
```

Frozen is the worst row, below a bag of character n-grams. MiniLM was built on English sentences, and these records are mostly codes, grades and dimensions. Don't take 13.4% to 90.8% as what tuning does in general. It's the size of the gap on this text, where the frozen model has the least to work with.

Look at the last column too. Tuning took look-alikes in the top 10 from 0.030 to 0.494. Our reading is that a model learning codes and dimensions pulls same-shaped records together, the unsafe ones included, and fills the slots a frozen model left to noise. We return to this under mining.

Other people's gains run from nothing to large:

- A [Databricks measurement](https://www.databricks.com/blog/improving-retrieval-and-rag-embedding-model-finetuning) (vendor blog, February 2025), with 6,000 to 14,220 pairs per set, moved `gte-large-en-v1.5` recall@10 from 0.293 to 0.552 on FinanceBench, 0.821 to 0.873 on ManufactQA, and 0.849 to 0.884 on DocsQA. A different model, `e5-mistral`, stayed at 0.899 on DocsQA. An untuned `text-embedding-3-large` scored 0.95 there, so a better frozen model can beat a tuned one. Some of those test sets are as small as 139 queries.
- [Zeakis et al.](https://arxiv.org/abs/2304.12329) (PVLDB 2023) compared 12 language models across 17 entity-resolution benchmarks. On supervised pair classification, not retrieval, tuning only the last layer on five of those datasets, they report that "SentenceBERT models also benefit from fine-tuning, but to a lesser extent" than BERT-style models do.

So measure frozen first, against a character baseline, on your own text. A frozen score below the baseline, as here, is a strong sign the encoder is missing what your text carries. A frozen score above it doesn't settle the question. Only a tuned run does, and a few hundred pairs make that cheap to try.

## Building pairs from match labels

A match label is a pair of records. Training needs a batch of pairs where the other items really are non-matches. Two steps get there:

1. Close the labelled pairs into groups, as in [splitting pairs](04-entity-matching-and-learning-to-rank.md#splitting-pairs-without-leaking-the-answer). If A matches B and B matches C, A and C are a known match even though nobody labelled them.
2. Build each batch with at most one pair per known group, so no known match is used as a negative.

```python
chosen, seen = [], set()                  # illustrative: from similarity_train.py
for i in rng.permutation(len(pairs)):
    g = groups[pairs[i, 0]]
    if g not in seen:
        seen.add(g)
        chosen.append(i)
    if len(chosen) == BATCH:
        break
batch = pairs[chosen]
left, right = forward(model, text[batch[:, 0]]), forward(model, text[batch[:, 1]])
logits = left @ right.T                   # each left's positive is on the diagonal, the rest of the batch are negatives
loss = F.cross_entropy(logits / temperature, torch.arange(len(batch)))
```

The second step only removes matches you know about. An unlabelled match in the batch is still treated as a negative, which is called a **false negative**. Labels are always partial, so you can reduce this but can't remove it.

Split straight after closing the labels, before you build any batch. In [the last chapter](04-entity-matching-and-learning-to-rank.md#splitting-pairs-without-leaking-the-answer), holding out parts while their look-alikes stayed in training overstated a similarity model by 0.131. Here the test catalogue is a new generation with no code in common, which you can't do with real data, and it doesn't hold specs out. With real data, hold out whole specs.

## How many pairs

Our curve climbs fast and flattens. From 100 to 300 pairs recall gains 0.082, from 300 to 1,000 it gains 0.027, and from 1,000 to 3,000 it gains 0.004, which is well inside the seed noise of about 0.01. The training catalogues hold about 3,400 pairs a label could cover, so 1,000 is about 30% of them.

That curve is from generated data, and you shouldn't carry its numbers to your own. We looked for a controlled curve of labelled pairs against retrieval quality on text and didn't find one. A figure you'll see quoted, from a vendor blog, is ["1,000 to 5,000" samples](https://weaviate.io/blog/fine-tune-embedding-model) for narrow domains. It cites no study. The nearest real evidence is in entity matching, where the task is classifying pairs rather than retrieving, and it has the same shape:

- [Peeters and Bizer](https://arxiv.org/abs/2202.02098) (WWW 2022 companion, a four-page poster) trained a supervised contrastive encoder for product matching. Against the best baseline on WDC Computers, the F1 lead was 8.84 points at about 3,000 pairs and 0.84 at about 68,000. The contrastive encoder gained most where labels are scarce, because the baselines catch up.
- [WDC Products](https://arxiv.org/abs/2301.09521) (Peeters, Der and Bizer, EDBT 2024) grew training from 2,500 to 19,835 pairs at 80% corner cases, its hard look-alikes. On products seen in training, its contrastive matcher R-SupCon went from an F1 of 77.48 to 82.15, far above the cross-encoder Ditto at small size, 58.33. The next section shows the catch.
- [Augmented SBERT](https://arxiv.org/abs/2010.08240) (Thakur et al., NAACL 2021) found a plain bi-encoder, which embeds each text on its own as our tuned model does, trailing a [cross-encoder](../../../generative-ai/02-rag-retrieval/notes/05b-query-parsing-conversational-retrieval-and-reranking.md#reranking) at 1,400 to 10,000 samples, 72.07 against 77.74 in Spearman on Spanish-STS and 74.66 against 81.23 in F1 on Quora, each the best of five seeds on the dev set. Using the cross-encoder to label extra pairs closed most of that, to 76.24 and 79.31, taking the best sampling strategy for each dataset.

Measure your own curve by training on 100, 300 and 1,000 pairs. It costs minutes on a laptop, and when the last step gains less than your seed noise, more labels of the same kind won't pay. Labels of a new kind may, as the next section shows.

## A family it never saw

Every test so far had families the model trained on. Now remove one family from training entirely, and score only that family in a new catalogue. This is 1,000 pairs, in-batch, one seed per family:

```text
recall@10                       bearing   bolt  oring    mean
TF-IDF characters, no training    0.317  0.539  0.498   0.451
frozen pretrained                 0.093  0.138  0.139   0.124
trained on all families           0.861  0.947  0.944   0.917
trained without this family       0.578  0.782  0.784   0.715
```

Recall falls by 0.20 on average, and the tuned model still beats TF-IDF on every family. The generator is kind here. All its families share the same code format and vendor names, and their dimensions are all short digit strings, so some of what the model learned carries across. Expect a real new product line, with a new vocabulary, to fall further. That's a guess we can't test on this data.

Real data shows a harder version of this. In WDC Products, R-SupCon led on seen products and collapsed on unseen ones, with an F1 of 82.15 against 53.31 at the large size. Ditto held 67.94 on unseen and the cross-encoder RoBERTa held 69.75. Those two read the pair together, and both scored well above R-SupCon on unseen products. A score on a held-out family belongs next to your headline number.

## Mining hard negatives

In-batch negatives are whatever else landed in the batch, and most are easy. Mining adds the ones the model currently likes. For each anchor, the left record of a training pair, rank all the training records with the current encoder, drop what the labels call a match, and take a band of ranks. We add four per anchor to the in-batch set, and we rebuild the list once, halfway through training. All arms use 1,000 pairs:

```text
                                     recall  look-alikes  mined matches
                                             in top 10    before removal
in-batch                              0.908     0.494       -
+ hardest (rank 1-10)                 0.906     0.363     0.047
+ hardest, false negatives removed    0.893     0.304     0.048
+ rank 11-100                         0.908     0.502     0.002
hardest only, no in-batch             0.852     0.250     0.047
```

Recall's standard deviation over the three seeds is about 0.01 for each arm. Read it row by row.

**Mining did not raise recall, and it did cut look-alikes.** Adding the hardest ranks left recall at 0.906 and took look-alikes in the top 10 from 0.494 to 0.363. That held on every seed: 0.498 to 0.377, 0.499 to 0.349, 0.485 to 0.363. The hard negatives in a catalogue are the look-alikes, so training against them pushes those away. If your only metric is recall@10, mining looks useless here. It's working on a metric you may not have been measuring.

**Rank 11 to 100 did nothing.** Those records are already easy for this model. [Facebook's search team](https://arxiv.org/abs/2006.11632) (Huang et al., KDD 2020) found the opposite band best, with rank 101 to 500 giving the best recall on their much larger corpus, and reported that "using the hardest examples is not the best strategy." A rank band depends on the corpus, so test one and don't copy it.

**Hard negatives alone cost recall, and did not collapse.** Removing in-batch negatives lost 0.056 recall and gave the lowest look-alike share. [FaceNet](https://arxiv.org/abs/1503.03832) (Schroff et al., CVPR 2015) warns that the hardest negatives can lead to "a collapsed model (i.e. f(x) = 0)", and we didn't see that. We started from a pretrained encoder with a small learning rate, which may be why, though we didn't test that. Facebook's finding fits ours: models trained on hard negatives alone did not beat random negatives. Their fix was to ration them. Mining online, at most two hard per positive worked best. Mining offline over the whole result pool, recall kept rising with the easy-to-hard ratio until it saturated at 100 to 1. They also measured a warning about what you call a negative. Using impressions nobody clicked, which are hard by construction, gave an "absolute 55% regression in recall" for people search.

**Removing false negatives did not help recall.** About 4.7% of the mined hardest records were true matches the labels missed, a share counted before any removal, which is why the removal arm shows it too. On generated data we can remove exactly those, and recall stayed within noise of the plain arm, at 0.893 against 0.906. Look-alikes did move, from 0.363 to 0.304, with standard deviations of 0.014 and 0.029, and we didn't test why. At this rate false negatives don't hold recall back. At a higher rate they can: [GPL](https://arxiv.org/abs/2112.07577) (Wang et al., NAACL 2022), a way to tune an encoder with no labels, lost 2.5 nDCG@10 points using hard negatives with generated queries, and blames false negatives, "a common issue for hard negative mining." Before you build a mining pipeline, read a sample of what it mines and count the true matches.

Other studies did see retrieval gains, on other tasks. [DPR](https://arxiv.org/abs/2004.04906) (Karpukhin et al., EMNLP 2020) added one BM25 negative to in-batch training and raised top-5 accuracy on the Natural Questions dev set, at batch 32, from 52.1 to 65.0. It found that "adding a single BM25 negative passage improves the result substantially while adding two does not help further." [ANCE](https://arxiv.org/abs/2007.00808) (Xiong et al., ICLR 2021) samples one negative uniformly from the current model's top 200, refreshes the index every 10,000 batches using as much GPU again, and, warmed up on BM25 negatives, reached an MRR@10 of 0.330 on MS MARCO against 0.279 and 0.280 for in-batch training with the same warm-up. It has no frozen baseline and doesn't address false negatives. We don't know why those two gained and our recall didn't. They measure earlier ranks on passages, and our recall had already flattened, but neither explanation is tested here.

## Which loss

Less than the papers suggest. [Musgrave et al.](https://arxiv.org/abs/2003.08505) (ECCV 2020) reran 13 losses plus one loss-and-miner pairing under one fair protocol, on three vision datasets with an ImageNet-pretrained encoder. On CUB, a bird-species set, mean average precision at R (where R is how many true matches the query has), on concatenated 512-dimensional embeddings, went from 14.21 for the pretrained model to 26.53 for the 2006 contrastive loss and 23.69 for triplet, with the best of all at 26.70. On SOP, an online-products set, those three were 23.44, 44.39 and 43.37, with the best at 47.41. Training was the big step, and the choice of loss the small one. They conclude that "state of the art loss functions perform marginally better than, and sometimes on par with, classic methods." That's vision, and applying it to text is our inference.

[Supervised contrastive learning](https://arxiv.org/abs/2004.11362) (Khosla et al., NeurIPS 2020) is often quoted beside these. Its evidence is closed-set image classification, 78.7% against 78.2% on ImageNet, so it doesn't speak to retrieval over parts it has never seen.

Start with in-batch softmax, the [`MultipleNegativesRankingLoss`](https://sbert.net/docs/sentence_transformer/loss_overview.html) of `sentence-transformers`, and spend your time on the labels and the split.

## What tuning doesn't replace

**The attribute check.** After tuning, about half the top 10 are look-alikes, and after mining more than a third still are. Tuning is what lets a candidate list contain the right records. It doesn't make them safe to swap. The score proposes and [extracted attributes decide](04-entity-matching-and-learning-to-rank.md#similar-is-not-interchangeable), with unread ones going to a person.

**The reranker, until you've compared them.** GPL's averages over six sets from BeIR, a public retrieval benchmark, show how far tuning without labels got: 45.2 nDCG@10 frozen, 51.5 with GPL, 52.9 with TSDAE, another label-free method, added, 54.7 for BM25 with a cross-encoder on top, and 55.1 for TSDAE plus GPL with the cross-encoder. That's tuning without labels, and we didn't test labelled tuning against a reranker. Their words: "TSDAE and GPL can narrow but not fully close the performance gap." [Rosa et al.](https://arxiv.org/abs/2212.06121) (preprint) argue that "when training and test data are similar, cross-encoders and bi-encoders have similar effectiveness", and that the gap opens when they differ. That matches the held-out family above. We looked for a clean condition under which a reranker becomes unnecessary and didn't find one. The Databricks post says tuned embeddings did "as well as or better than reranking in many cases", from a vendor and with no conditions attached. So run your own comparison.

## With the library

The lab writes its own loop so that you can see how the batch is built. In practice, [`sentence-transformers`](https://sbert.net/docs/sentence_transformer/loss_overview.html) 6 gives you the same loss with a [no-duplicates sampler](https://sbert.net/docs/package_reference/sentence_transformer/sampler.html). [`mine_hard_negatives`](https://sbert.net/docs/package_reference/util/hard_negatives.html) has a `range_min` to skip the top ranks that may be true matches, and margins to keep negatives below the positive. One default can catch you out. [`BatchSemiHardTripletLoss`](https://sbert.net/docs/package_reference/sentence_transformer/losses.html) uses Euclidean distance with a margin of 5, against 0.2 in FaceNet on normalised vectors.

## All four stages together

A real system chains everything in this subject: read attributes with rules, retrieve candidates, score pairs, then decide what merges without a person. [`practice/06_parts_capstone_lab.py`](../practice/06_parts_capstone_lab.py) does that on generated catalogues, with retrieval by character TF-IDF rather than a tuned encoder. It trains on one catalogue, sets thresholds on a second and reports on a third, each generated from its own seed. "Interchangeable" means same spec. The prices are assumptions: a wrong merge costs 200 euros, a review 3 and a missed pair 5.

Each new catalogue has about 1,766 records and 3,784 true interchangeable pairs. The thresholds come from a search over 40 quantile points. Means of 5 seeds:

| Arm | True pairs offered | Merged | Wrong merges | Wrong after closure | Reviews | Still unfound | Euros per record |
|---|---:|---:|---:|---:|---:|---:|---:|
| Full pipeline, k=10 | 0.505 | 546 | 0.4 | 0.6 | 1,187 | 2,255 | 8.44 |
| No stop on stated conflict | 0.505 | 564 | 0.4 | 0.6 | 1,170 | 2,255 | 8.41 |
| Rules hidden from model and gate | 0.505 | 492 | 0.2 | 0.2 | 239 | 3,107 | 9.22 |
| No review band | 0.505 | 668 | 8.4 | 17.2 | 22 | 3,102 | 9.77 |
| Thresholds set on 200 specs, not 800 | 0.505 | 599 | 5.4 | 11.6 | 1,256 | 2,195 | 8.95 |
| Retrieve k=3 | 0.329 | 516 | 0.4 | 0.4 | 646 | 2,717 | 8.82 |
| Retrieve k=30 | 0.681 | 542 | 0.8 | 1.2 | 1,494 | 2,015 | 8.32 |

Four things stand out. At this search setting, each arm's cost difference from the full pipeline went the same way in all 5 seeds unless noted:

- **Retrieval sets the ceiling.** At k=10, half the true pairs never reach the model, and no pair scorer can recover them. Most still-unfound pairs are of this kind. Tripling k raised that share to 0.681, for 2.8 times the candidates, and the extra pairs mostly went to review at these prices. The saving is small and not safe to memorise. Across three tuning draws and three search settings, k=30 was cheaper in 7 of 9 comparisons, by 0.11 to 0.38 euros per record. In the other 2, it cost about 0.32 more, because a finer search picked a threshold that let through about 7 wrong merges. Closure is the one exception to the ceiling, since a missing pair can come back through a chain of offered ones. If every true pair offered were confirmed and joined into groups, that would reach 0.563 of all true pairs at k=3, 0.825 at k=10 and 0.947 at k=30. In the full pipeline, merges plus confirmed reviews reach 0.670, with 4 wrong pairs implied. The table's "still unfound" doesn't credit any of this.
- **Set thresholds on a catalogue of production size.** The table's 5.4 wrong merges depends on which small catalogue you draw and how finely you search. Over three draws and searches of 40, 80 and 200 points for the merge threshold, 200 specs gave 1.2 to 6.6 wrong merges and 800 gave 0 to 2.4, so even the 0.4 in the table isn't a stable figure. The ranges overlap, and 200 specs cost more in 7 of the 9 matched settings, by up to 0.51 euros per record, and a hair less in the other 2. At 40 points, the merge threshold's standard deviation across seeds was 0.005 to 0.015, against 0.002 to 0.004. So a small catalogue gives a noisier threshold. Don't trust a wrong-merge count from a single search.
- **Closure multiplies mistakes.** With no review band, 8.4 wrong pairs became 17.2 once merges were joined into groups. One wrong link can join two whole groups.
- **A stop on stated conflicts caught nothing here.** The model seeing the conflict isn't the reason. With rules hidden from it, 19.2 pairs per catalogue with a stated clash still scored above the merge threshold, and none was wrong. Every one was a true pair whose records disagree, so an attribute was mistyped or misread. The stop sends those to a person, and in the full pipeline that's 17.2 pairs. Reading the attributes mattered a lot, though: hiding them cost 0.78 euros per record. So rules earned their place as model inputs, at least on these generated catalogues.

The review band's value depends on the price of a miss. At 20 euros per missed pair, reviews rose from 1,187 to 2,087, and merges stayed at 546. Replacing `candidates` with the encoder you tuned above is the obvious next experiment, and we haven't run it.

## Pitfalls

- **Skipping the frozen baseline.** Without a frozen score and a character score on the same test set, a tuned number says nothing. Here frozen was 0.134 and characters were 0.456.
- **Testing on the families you trained on, and stopping.** That gave 0.917 where a held-out family gave 0.715.
- **Using only recall to judge mining.** Recall stayed at about 0.91 while look-alikes fell from 0.494 to 0.363. Measure what the negatives were meant to fix.
- **Mining without reading what you mined.** Nothing errors when mined negatives are true matches, so read a sample and count. Ours were 4.7%, and that won't hold on every dataset.
- **Training on hard negatives alone.** It cost 0.056 recall here. Keep in-batch negatives in the mix.
- **Copying a rank band.** The symptom is a mining arm that changes nothing, as rank 11 to 100 did here, while rank 101 to 500 was best at Facebook. Try one on your corpus.
- **Letting known matches be negatives.** Nothing errors, and the loss quietly pushes true matches apart. Close the labels into groups, and allow one pair per group in a batch. We didn't measure the cost of skipping this.
- **Quoting a rule of thumb for pair counts.** The figure we traced, 1,000 to 5,000, cites no study. Train at three sizes and read the curve.

## Try it

Numbers come from [`practice/05_similarity_tryit.py`](../practice/05_similarity_tryit.py), about four minutes on an Apple M4 Pro GPU.

1. **What does the temperature do?** Before running it, guess how recall changes at temperatures 0.05, 0.2 and 1.0, with everything else fixed.

<details><summary>Answer</summary>

```text
1000 pairs, in-batch, mean and standard deviation over three seeds, new catalogue
            recall        unsafe_in_top
              mean    std          mean    std
temperature
0.05         0.913  0.010         0.483  0.021
0.20         0.848  0.008         0.542  0.014
1.00         0.776  0.010         0.506  0.022
```

Recall falls by 0.137 from the coldest to the warmest. A low temperature makes the loss focus on the negatives closest to the anchor, so in-batch softmax is already doing a soft kind of mining. The 0.05 row differs from the chapter's 0.908 and 0.494 because this script draws a different sample of pairs, about the size of the seed noise.

</details>

2. **A colleague reports that mining "did nothing" because recall@10 stayed flat.** What do you ask them to measure?

<details><summary>Answer</summary>

What the negatives were meant to fix. Here that's look-alikes in the top 10, which fell from 0.494 to 0.363 with recall flat. Their task might call for a different number, such as confusions between two named classes, or precision at a fixed recall. If none of those move either, then mining isn't earning its pipeline.

</details>

3. **Your labels cover about 30% of the true matches, and batches hold 32 pairs from a catalogue of 1,700 records.** Does the one-pair-per-group rule stop false negatives? Which false negatives are more dangerous, in-batch or mined?

<details><summary>Answer</summary>

It doesn't stop them. It removes only known matches, and an unlabelled match can still land in the batch. In-batch ones are rare, since a batch is a random 32 of many groups. Mined ones are more dangerous, because mining searches for records the model ranks highly, which is where true matches sit. In our lab the hardest band held 4.7% true matches against 0.2% for rank 11 to 100.

</details>

## Interview checklist

| Question | Short answer |
|---|---|
| When should you tune an embedding model? | When a small tuned run beats the frozen model by more than your seed noise on your text. Measure frozen and a character baseline first. Ours scored 0.134 and 0.456, and tuning reached 0.908. Published gains run from none to large. |
| How do you build training pairs from match labels? | Close the labels into groups, split by whole specs, and allow one pair per known group in a batch, so no known match is used as a negative. |
| How many labelled pairs do you need? | Measure it: train at three sizes. Ours flattened by 1,000 pairs on generated data, and the rule of thumb we traced cites no study. Contrastive gains shrink as labels grow, 8.84 F1 points at 3,000 pairs to 0.84 at 68,000 on WDC Computers. |
| What is a false negative in training? | A true match treated as a non-match because the labels missed it. Mining finds them more than random sampling does: 4.7% of our hardest band against 0.2% of rank 11 to 100. |
| What did hard-negative mining buy? | Not recall, which stayed near 0.91. It cut look-alikes in the top 10 from 0.494 to 0.363, on every seed. Measure what the negatives were meant to fix. |
| Why not train on the hardest negatives only? | It cost us 0.056 recall, Facebook's hard-only models didn't beat random negatives, and FaceNet warns of collapse, though we didn't see it. Mix them with easy ones. |
| Which metric-learning loss should you pick? | Start with in-batch softmax. Under a fair protocol on vision data, newer losses barely beat 2006 contrastive, and most of the gain came from training at all. |
| Does a tuned encoder generalise to a new product family? | Less well. Ours fell from 0.917 to 0.715 on a held-out family. In WDC Products, R-SupCon fell to an F1 of 53.31 on unseen products while cross-encoders held near 68 to 70. |
| Does tuning remove the need for a reranker or attribute check? | No for the attribute check, since half the top 10 are still look-alikes. Don't assume so for the reranker: tuning without labels narrowed the gap but didn't close it in GPL, and we didn't test labelled tuning against one. Run the comparison on your data. |

## Next

You can now tell when an encoder is worth tuning and how to measure what mining does. The tuned encoder proposes candidates, and [AE 08/03](../../../ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag.md) uses the same retrieval step across text and images. The next step in the course is language modelling proper: carry on with [the LLM fundamentals pillar in generative AI](../../../generative-ai/01-llm-fundamentals/README.md). [DE 06/06](../../../data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring.md) puts matching in its place among the other jobs of one invoice system.
