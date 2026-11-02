---
origin: curated
sources:
  - ../sources/
confidence: high
cleaned: 2026-11-01
---
# 03-nlp references

★ = changed a claim in the notes. ⚑ = preprint only. Books shared across pillars are in the [subject references](../references.md). PDFs live in the shared [`../sources/`](../sources/). Notes: [01 text representation](notes/01-text-representation.md), [02 text classification](notes/02-text-classification.md), [03 topics and summarization](notes/03-topic-models-and-summarization.md), [04 embeddings](notes/04-embeddings-and-similarity.md), [05 semantics and NER](notes/05-semantic-analysis-and-ner.md), [06 sentiment](notes/06-sentiment-analysis.md), [07 LLM embeddings as features](notes/07-llm-embeddings-as-features.md).

## Books

| Book | Why read it | Local | Maps to |
|---|---|---|---|
| ★ Sarkar, *Text Analytics with Python*, 2nd ed. (Apress, 2019) | The practical spine of this pillar, chapter by chapter, with notebooks kept in [`practice/text-analytics-with-python/`](practice/text-analytics-with-python/). The notes follow the 2nd edition's chapter numbers, and its [companion repo](https://github.com/dipanjanS/text-analytics-with-python) has the saved outputs behind the numbers we quote from it | [PDF](../sources/sarkar-text-analytics-with-python-2e.pdf). Despite the file name this copy has the text of the 1st edition, which has seven chapters and different numbering, so use the repo's notebooks for the 2nd edition | ch. 1, 3, 4 to [01](notes/01-text-representation.md); 5 to [02](notes/02-text-classification.md); 6, 7 to [03](notes/03-topic-models-and-summarization.md); 4b, 7a to [04](notes/04-embeddings-and-similarity.md); 8 to [05](notes/05-semantic-analysis-and-ner.md); 9 to [06](notes/06-sentiment-analysis.md) |
| Bird, Klein and Loper, [*Natural Language Processing with Python*](https://www.nltk.org/book/) (free online) | The NLTK book: corpora, WordNet, tagging and chunking, slower and more linguistic than the notes | [PDF](../sources/bird-klein-loper-nlp-with-python.pdf) | [01](notes/01-text-representation.md), [05](notes/05-semantic-analysis-and-ner.md) |
| Müller and Guido, *Introduction to Machine Learning with Python*, ch. 7 "Working with Text Data" | The cleanest introduction to bag of words and TF-IDF in scikit-learn, with [our notebook copy](../01-classical-ml/practice/intro-to-ml-in-python/07-working-with-text-data.ipynb) | [PDF](../sources/mueller-guido-introduction-to-ml-with-python.pdf) | [01](notes/01-text-representation.md), [02](notes/02-text-classification.md) |
| Jurafsky and Martin, [*Speech and Language Processing*, 3rd ed. draft](https://web.stanford.edu/~jurafsky/slp3/) (free online) | The textbook for depth on what these notes treat practically: logistic regression, vector semantics, sequence labelling | web only | [02](notes/02-text-classification.md), [04](notes/04-embeddings-and-similarity.md), [05](notes/05-semantic-analysis-and-ner.md) |
| Alammar and Grootendorst, *Hands-On Large Language Models* (O'Reilly, 2024), ch. 4 "Text Classification", ch. 5 "Text Clustering and Topic Modeling", ch. 10 "Creating Text Embedding Models" | The closest book to our last chapter, with [public notebooks](https://github.com/HandsOnLLM/Hands-On-Large-Language-Models) for all three | web only | [07](notes/07-llm-embeddings-as-features.md) |
| Boykis, [*What are embeddings?*](https://github.com/veekaybee/what_are_embeddings) (free) | A short, careful history of the idea from one-hot to transformers | web only | [04](notes/04-embeddings-and-similarity.md), [07](notes/07-llm-embeddings-as-features.md) |

## Core papers

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| ★ Mikolov, Chen, Corrado and Dean, *Efficient Estimation of Word Representations in Vector Space* ([arXiv:1301.3781](https://arxiv.org/abs/1301.3781), 2013) ⚑ | Skip-gram and CBOW, and the analogy test | web only | [04](notes/04-embeddings-and-similarity.md) |
| Mikolov, Sutskever, Chen, Corrado and Dean, *Distributed Representations of Words and Phrases and their Compositionality* ([arXiv:1310.4546](https://arxiv.org/abs/1310.4546), NIPS 2013) | Negative sampling and subsampling, which made it practical | web only | [04](notes/04-embeddings-and-similarity.md) |
| Pennington, Socher and Manning, [*GloVe*](https://aclanthology.org/D14-1162/) (EMNLP 2014) | Global co-occurrence counts, and the source of the vectors used in note 04 | web only | [04](notes/04-embeddings-and-similarity.md) |
| Bojanowski, Grave, Joulin and Mikolov, *Enriching Word Vectors with Subword Information* ([TACL 2017](https://doi.org/10.1162/tacl_a_00051)) | FastText: vectors for words never seen | web only | [04](notes/04-embeddings-and-similarity.md) |
| ★ Arora, Li, Liang, Ma and Risteski, [*Linear Algebraic Structure of Word Senses*](https://aclanthology.org/Q18-1034/) (TACL 2018) | A polysemous word's vector is approximately a weighted sum of its senses | web only | [04](notes/04-embeddings-and-similarity.md) |
| ★ Bolukbasi, Chang, Zou, Saligrama and Kalai, *Man is to Computer Programmer as Woman is to Homemaker?* ([arXiv:1607.06520](https://arxiv.org/abs/1607.06520), NIPS 2016) | Corpus associations end up in the vectors | web only | [04](notes/04-embeddings-and-similarity.md), [07](notes/07-llm-embeddings-as-features.md) |
| Maas, Daly, Pham, Huang, Ng and Potts, [*Learning Word Vectors for Sentiment Analysis*](https://aclanthology.org/P11-1015/) (ACL 2011) | The 25k/25k IMDb dataset used in note 06 | web only | [06](notes/06-sentiment-analysis.md) |
| Ribeiro, Singh and Guestrin, *"Why Should I Trust You?"* ([arXiv:1602.04938](https://arxiv.org/abs/1602.04938), KDD 2016) | LIME | [PDF](../sources/ribeiro-2016-why-should-i-trust-you.pdf) | [06](notes/06-sentiment-analysis.md) |
| ★ Monroe, Colaresi and Quinn, [*Fightin' Words*](https://doi.org/10.1093/pan/mpn018) (*Political Analysis*, 2008) | Why raw log-odds rank rare words too highly, and the shrinkage that fixes it. Bibliographic record checked; paper not read in full | web only | [06](notes/06-sentiment-analysis.md) |
| ★ Reimers and Gurevych, *Sentence-BERT* ([arXiv:1908.10084](https://arxiv.org/abs/1908.10084), EMNLP 2019) | Train the pooled vector so that related sentences land close | [PDF](../sources/reimers-2019-sentence-bert.pdf) | [07](notes/07-llm-embeddings-as-features.md) |
| ★ Grootendorst, *BERTopic* ([arXiv:2203.05794](https://arxiv.org/abs/2203.05794), 2022) ⚑ | Embed, reduce, cluster, then name clusters with c-TF-IDF | [PDF](../sources/grootendorst-2022-bertopic.pdf) | [03](notes/03-topic-models-and-summarization.md), [07](notes/07-llm-embeddings-as-features.md) |
| McInnes, Healy and Melville, *UMAP* ([arXiv:1802.03426](https://arxiv.org/abs/1802.03426), 2018) ⚑ | The reduction step | [PDF](../sources/mcinnes-2018-umap.pdf) | [07](notes/07-llm-embeddings-as-features.md) |
| Campello, Moulavi and Sander, [*Density-Based Clustering Based on Hierarchical Density Estimates*](https://doi.org/10.1007/978-3-642-37456-2_14) (PAKDD 2013) | HDBSCAN. Bibliographic record checked; paper not read in full | web only | [07](notes/07-llm-embeddings-as-features.md) |
| Liu, Ting and Zhou, [*Isolation Forest*](https://doi.org/10.1109/ICDM.2008.17) (ICDM 2008) | Anomalies are isolated by few random splits. Bibliographic record checked; paper not read in full | web only | [07](notes/07-llm-embeddings-as-features.md) |
| Breunig, Kriegel, Ng and Sander, [*LOF*](https://doi.org/10.1145/335191.335388) (SIGMOD 2000) | Outlierness relative to local density. Bibliographic record checked; paper not read in full | web only | [07](notes/07-llm-embeddings-as-features.md) |
| ★ Muennighoff, Tazi, Magne and Reimers, *MTEB* ([arXiv:2210.07316](https://arxiv.org/abs/2210.07316), EACL 2023) | No embedding method dominates all tasks, so test on yours. [Live leaderboard](https://huggingface.co/spaces/mteb/leaderboard) | web only | [07](notes/07-llm-embeddings-as-features.md) |
| ★ Tunstall et al., *SetFit* ([arXiv:2209.11055](https://arxiv.org/abs/2209.11055), 2022) ⚑ | Fine-tune a sentence encoder on few labels with contrastive pairs | web only | [07](notes/07-llm-embeddings-as-features.md) |

## Courses and videos

| Course | Platform, cost | Why take it | Maps to |
|---|---|---|---|
| [CS224N: NLP with Deep Learning](https://web.stanford.edu/class/cs224n/), [Winter 2021 lectures](https://www.youtube.com/playlist?list=PLoROMvodv4rOSH4v6133s9LFPRHjEmbmJ) | Stanford on YouTube, free | Word vectors in the first lectures, then the neural side that notes 04 and 07 use | [04](notes/04-embeddings-and-similarity.md), [07](notes/07-llm-embeddings-as-features.md) |
| [Natural Language Processing in TensorFlow](https://www.coursera.org/learn/natural-language-processing-tensorflow) | DeepLearning.AI on Coursera, audit or paid | The course behind [`practice/intro-to-nlp/tensorFlow/`](practice/intro-to-nlp/tensorFlow/): tokenizer, embeddings, CNN and LSTM sentiment | [01](notes/01-text-representation.md), [06](notes/06-sentiment-analysis.md) |
| [Natural Language Processing Specialization](https://www.coursera.org/specializations/natural-language-processing) | DeepLearning.AI on Coursera, audit or paid | A slower route through classification, vector spaces and sequence models | [02](notes/02-text-classification.md), [04](notes/04-embeddings-and-similarity.md), [05](notes/05-semantic-analysis-and-ner.md) |
| [Hugging Face LLM course](https://huggingface.co/learn/llm-course) | Hugging Face, free | Tokenizers, pipelines and fine-tuning, the hands-on bridge from this pillar to the next | [07](notes/07-llm-embeddings-as-features.md) |
| [StatQuest: Machine Learning playlist](https://www.youtube.com/playlist?list=PLblh5JKOoLUICTaGLRoHQDuF_7q2GfuJF) | YouTube, free | Short refreshers on the classifiers and clustering methods used here | [02](notes/02-text-classification.md), [03](notes/03-topic-models-and-summarization.md) |
| [Thakur, *Approaching (Almost) Any NLP Problem on Kaggle*](https://www.kaggle.com/code/abhishek/approaching-almost-any-nlp-problem-on-kaggle) | Kaggle notebook, free ([our copy](practice/approaching-almost-any-nlp-problem-on-kaggle.ipynb)) | How a competitor stacks TF-IDF, SVD, SVM, boosting and neural nets | [02](notes/02-text-classification.md) |
| [Kaggle Learn](https://www.kaggle.com/learn) | Kaggle, free | Short exercises in pandas and ML to warm up on | [02](notes/02-text-classification.md) |
| [fast.ai Practical Deep Learning](https://course.fast.ai) | fast.ai, free | Its NLP lesson fine-tunes a transformer top-down, a different route to note 07's question | [07](notes/07-llm-embeddings-as-features.md) |
