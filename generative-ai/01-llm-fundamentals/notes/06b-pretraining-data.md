---
origin: synthesis  # split from 06-pretraining-data-and-objectives.md (2026-11-08): the data section moved here to keep 06 under the word limit
sources:
  - https://arxiv.org/abs/1911.02116
  - https://arxiv.org/abs/1803.02324
  - https://arxiv.org/abs/2306.09212
  - https://arxiv.org/abs/1506.06724
  - https://arxiv.org/abs/1910.10683
  - https://arxiv.org/abs/1911.00359
  - https://arxiv.org/abs/2201.11990
  - https://arxiv.org/abs/2302.03169
  - https://arxiv.org/abs/2303.17564
  - https://arxiv.org/abs/2305.06161
  - https://arxiv.org/abs/2305.10266
  - https://arxiv.org/abs/2305.10429
  - https://arxiv.org/abs/2306.11644
  - https://arxiv.org/abs/2309.05463
  - https://arxiv.org/abs/2311.07989
  - https://arxiv.org/abs/2401.00812
  - https://arxiv.org/abs/2401.02412
  - https://arxiv.org/abs/2401.16380
  - https://arxiv.org/abs/2404.14219
  - https://arxiv.org/abs/2411.04905
  - https://arxiv.org/abs/2411.12580
  - https://arxiv.org/abs/2412.15115
  - https://arxiv.org/abs/2504.04022
  - https://arxiv.org/abs/2601.21343
  - https://arxiv.org/abs/2601.21571
  - https://doi.org/10.18653/v1/2021.naacl-main.41
  - "Huyen, AI Engineering (O'Reilly, 2025), ch. 2"
  - https://arxiv.org/abs/1805.00932
  - https://doi.org/10.18653/v1/d18-1206
  - https://arxiv.org/abs/1910.14599
  - https://arxiv.org/abs/1805.12471
  - https://arxiv.org/abs/1505.00468
  - https://arxiv.org/abs/2305.08322
confidence: high
cleaned: 2026-11-08
---

# 6b — Pretraining data: what goes in

> A pretrained model is its data. Filtering, mixture and repetition move benchmark scores as much as architecture does, so the first question about any model is what it read.

[Chapter 6](06-pretraining-data-and-objectives.md) covered the objective and the training loop. This note covers the input: where pretraining text comes from, how it is filtered, how the mixture shapes what the model can do, and where the supply runs out.

---

## What the data is

```mermaid
flowchart LR
    A[Common Crawl snapshot] --> B[Line and page rules]
    B --> C[Paragraph dedup]
    C --> D[Language ID]
    D --> E[Quality score]
    E --> F[Mixture weights]
    F --> G[Training stream]
```

Most pretraining text starts as Common Crawl, a scrape of billions of web pages, usually filtered into something like Google's C4. Filtering is crude: GPT-2's WebText kept only pages linked from Reddit posts with at least three upvotes (*AI Engineering*, ch. 2). C4 itself was one month of Common Crawl (April 2019). T5's authors kept only lines that end in terminal punctuation and dropped pages with fewer than three sentences, a word from a bad-word list or a curly bracket. They deduplicated repeated three-sentence spans and kept pages that langdetect scored at least 0.99 English, which left about 750GB ([arXiv:1910.10683](https://arxiv.org/abs/1910.10683) (Raffel et al., JMLR 2020)). With their 220M baseline trained on 34B tokens, the 6.1TB unfiltered version scored worst on every task (GLUE 81.46 against 83.28). Small in-domain sets won on matching tasks: Wikipedia plus books raised exact match on the fiction-heavy MultiRC from 25.78 to 50.93. Repetition hurt only at extremes. Cycling a small subset 1,024 times cut GLUE to 79.55, while 64 repeats barely moved it. CCNet, from Facebook the same year, filtered by resemblance instead of rules. It removed duplicate paragraphs, which made up 70% of the text in a monthly snapshot, and only then ran fastText language identification, so boilerplate no longer pulled pages in small languages into English. It then scored each page by its perplexity under a 5-gram model trained on that language's Wikipedia and split each language into thirds. On one shard of the February 2019 snapshot, 42% of characters survived deduplication against that shard alone and 28% against 100 shards. A BERT-Base trained on the lowest-perplexity third beat the same model trained on Wikipedia by 3.3 XNLI points averaged over English, Russian, Chinese and Urdu (75.9 against 72.6), at the same step count but with more data in most languages. Urdu's 7-point gain came from 2.2GB against Wikipedia's 106MB, so quantity and quality are mixed, and each score is one run. The filter rewards text that reads like Wikipedia: the authors note that valid blog comments and jargon-heavy forums land in the worst-scoring third ([arXiv:1911.00359](https://arxiv.org/abs/1911.00359) (Wenzek et al., LREC 2020)). Books entered through BookCorpus, which was gathered for a different job: training sentence embeddings to align novels with their film adaptations.

It holds 11,038 free books by unpublished authors, each over 20,000 words, about 985M words in all, and Romance is the largest genre at 2,865 books ([arXiv:1506.06724](https://arxiv.org/abs/1506.06724) (Zhu et al., ICCV 2015)). The paper says nothing about licensing, consent or duplicates, yet the corpus went on to train GPT-1 and BERT. The mix decides what the model is good at. English is 45.88% of Common Crawl and Russian, second, about 6%, which shows up later as worse quality and higher token cost in other languages ([chapter 01](01-tokens-and-embeddings.md)). mT5 rebuilt C4 for 101 languages from all 71 monthly Common Crawl scrapes, replacing the English punctuation rule with a line-length filter. It sampled each language in proportion to its size raised to the power 0.3, which boosts the low-resource ones ([doi:10.18653/v1/2021.naacl-main.41](https://doi.org/10.18653/v1/2021.naacl-main.41) (Xue et al., NAACL 2021)). On zero-shot XNLI with mT5-Large, raising the exponent to 0.7 helped Russian (81.5 to 82.8) and hurt Swahili (75.4 to 70.6), and dropping the line-length filter cost 2 points.

Sharing capacity across 101 languages cost the small models: mT5-Small trailed English-only T5-Small on SQuAD (84.7 against 87.2 F1), and the gap had almost closed at XXL (95.6 against 96.2). Newer reports filter with a model instead. Qwen2.5 used Qwen2-Instruct as the quality filter, downsampled e-commerce, social media and entertainment, upsampled science and technology, and grew the corpus from 7T to 18T tokens ([arXiv:2412.15115](https://arxiv.org/abs/2412.15115) (Qwen Team, 2024-12)). An earlier Phi model, phi-1.5, leaned on synthetic data even harder. It carried phi-1's synthetic Python "textbooks" ([arXiv:2306.11644](https://arxiv.org/abs/2306.11644) (Gunasekar et al., 2023-06, preprint)) over to common-sense text. The 1.3B model trained on 150B tokens drawn from a 30B-token set. About 20B of that set was synthetic "textbook" text generated from 20K seed topics, and the only real data was 6B tokens of filtered code. It used about 1.5K A100-hours of training compute. It matched Llama2-7B on common sense (WinoGrande 0.734 vs 0.691) and trailed it on knowledge (MMLU 0.376 vs 0.453) ([arXiv:2309.05463](https://arxiv.org/abs/2309.05463) (Li et al., 2023-09, preprint)).

The generation recipe is described only as "intricate iterations", and there is no contamination analysis. Phi-3 pushed filtering hardest, keeping heavily filtered web data plus synthetic text in what Microsoft calls a "data optimal regime" ([arXiv:2404.14219](https://arxiv.org/abs/2404.14219) (Abdin et al., 2024-04)). **phi-3-mini (3.8B, 3.3T tokens) scored 68.8% on MMLU 5-shot, close to Mixtral 8x7B's 70.5%, but 64.0 on TriviaQA against Mixtral's 82.2.** Filtering kept reasoning and gave up stored facts. Both results come from Microsoft's internal eval pipeline, and the data was not released. Filtering can also remove a capability on purpose. With medicine as a proxy forget domain, dropping or loss-masking only the medical *tokens* hit medicine as hard as dropping whole documents and cost less on neighbouring biology. **At 1.8B parameters, matching an unfiltered model's medical loss would take about 7000× the compute.** It held up 10× better than an unlearning baseline against adversarial fine-tuning, and the filtered models still learned to refuse medical questions ([arXiv:2601.21571](https://arxiv.org/abs/2601.21571) (Rathi & Radford, 2026-01, preprint)). The evidence is that single proxy domain, at up to 1.8B parameters.

Most mixtures are still set by hand. Megatron-Turing NLG (530B) kept the Common Crawl pages a fastText classifier scored as most like OpenWebText2, Wikipedia and Books3, about 20% of the extracted text, and removed near-duplicates with MinHash at a Jaccard similarity of 0.8. Only 53% and 34% of the documents in its two newest Common Crawl snapshots came from URLs unseen in earlier ones. Its weights then ran OpenWebText2 3.6 times and Wikipedia 3.2 times while seeing 0.2 of arXiv and GitHub and half of each crawl ([arXiv:2201.11990](https://arxiv.org/abs/2201.11990) (Smith et al., 2022, preprint)). The paper reports none of these choices against an alternative. BloombergGPT's rule was simpler: its curated finance corpus, FinPile, must not fall below half of training, so the 363B tokens it had capped the corpus at 709B, again with no alternative mix tested ([chapter 15](15-pretraining-runs-cost-and-scale.md#worked-example-price-a-pretraining-run-before-you-plan-one); [arXiv:2303.17564](https://arxiv.org/abs/2303.17564) (Wu et al., 2023, preprint)). The mixture weights can be learned rather than hand-set. DoReMi trains a 280M proxy model with Group DRO, which upweights whichever domain the proxy is furthest behind a reference model on, and reuses its domain weights for an 8B model. On the Pile, the weights moved Pile-CC from 11% to 61% of the mix and cut arXiv from 10.5% to 0.4%. The 8B model gained 6.5 points of average one-shot exact match on five generative QA tasks, reached the baseline's accuracy in 2.6× fewer steps, and improved perplexity on all 22 domains. The tuning cost 8% of the 8B run's compute ([arXiv:2305.10429](https://arxiv.org/abs/2305.10429) (Xie et al., NeurIPS 2023)). A 1B proxy did worse than the 280M one, and the authors cannot explain why the weights transfer across scales. DSIR selects documents instead of domains. It resamples raw data so its hashed n-gram distribution matches a target such as Wikipedia and books, and it processed 100M Pile documents in 4.5 hours on one CPU node. A BERT-base trained from scratch on the selection scored 82.30 on GLUE against 80.25 for random data ([arXiv:2302.03169](https://arxiv.org/abs/2302.03169) (Xie et al., NeurIPS 2023)). That is masked-LM evidence only, and n-grams are a surface signal. Code is in nearly every mix on the belief that it teaches reasoning.

A survey of that belief cites GSM8K chain-of-thought scores rising from 12.4 for text-davinci-001 to 46.9 for code-trained text-davinci-002 ([arXiv:2401.00812](https://arxiv.org/abs/2401.00812) (Yang et al., 2024-01, preprint)). Those are different models, and the survey concedes that explicit causal evidence is still missing. Ruis et al. looked at the data side. They ranked 5M pretraining documents (2.5B tokens) of Cohere's Command R 7B and 35B by influence on 40 simple maths queries. Answers to factual questions turned up in the top 500 documents for 55% of queries at 7B. Answers to reasoning questions almost never did. The influential documents instead showed the procedure, often as code or formulas, and StackExchange appeared about 10× more often than its share of the data ([arXiv:2411.12580](https://arxiv.org/abs/2411.12580) (Ruis et al., ICLR 2025)). The sample is 2.5B tokens out of trillions, influence is computed only through MLP weights, and code was over-represented for control queries that need no reasoning. Capabilities also come from data nobody labelled. 1.4% of PaLM's training instances were bilingual, holding over 30M translation pairs across 44 languages. Removing the translation pairs, about 0.5% of examples, cost a 1B model 7.4 BLEU on zero-shot translation into English from high-resource languages, but only 2–3 BLEU at 8B ([arXiv:2305.10266](https://arxiv.org/abs/2305.10266) (Briakou et al., ACL 2023)). That evidence covers PaLM's data and English-paired translation only.

Reflection is another behaviour nobody labelled. Essential AI took OLMo-2 7B, 13B and 32B stage-1 pre-training checkpoints (40 in all) and gave them six tasks (BBH, CRUXEval input and output, GSM8K, GSM8K-Platinum, TriviaQA) in which a chain of thought carried an injected error, then appended "Wait,". **231 of 240 dataset-checkpoint pairs showed at least one instance of situational reflection (explicit or implicit recovery), the 7B model did so after only 198B tokens, and accuracy on the adversarial sets tracked log pre-training compute at an average Pearson r of 0.76**, all before any RL, which contests DeepSeek-R1's claim that reflection emerges from RL ([arXiv:2504.04022](https://arxiv.org/abs/2504.04022) (Essential AI, 2025-04, preprint)). Self-correction of a model's own wrong answers was rarer, 154 of 240 pairs, and those sets keep only questions every checkpoint of that size failed. The reflection classifier (DeepSeek-V3, checked on 3 of the 6 datasets) had precision 0.95–1.00 but recall 0.61–0.76, so the counts understate it. The correlation mixes model size with token count, the errors are synthetic, no RL model is compared, and the paper does not say which pre-training data produces reflection.

Adding scarce data after the fact has its own risk, forgetting. CALM keeps a PaLM 2-S anchor frozen, joins it by cross-attention at every fourth layer to a frozen PaLM 2-XXS model further pre-trained on low-resource languages or on code, and trains only the joining layers on 5–7% of the data. On multilingual GSM8K, further pre-training the anchor itself on the low-resource data took its high-resource-language average from 28.0 to 25.6, while the composed model reached 31.8 (25 low-resource languages: 25.0 against 22.5 for the anchor and 22.6 for the further pre-trained anchor). On code, the further pre-trained anchor lost Python code-to-text (chrF1 30.4 to 18.9) where the composed model held 30.5, yet it still beat the composed model on HumanEval (24.3 against 22.5) and MBPP (43.0 against 32.2) ([arXiv:2401.02412](https://arxiv.org/abs/2401.02412) (Bansal et al., 2024-01, preprint)). The models are closed PaLM 2 variants, no variance is reported (HumanEval is zero-shot, MBPP and code-to-text 3-shot), the low-resource GSM8K set is machine-translated, and forgetting is the authors' reading, not a measured mechanism.


Code corpora show what a documented pipeline involves. BigCode's StarCoder started from The Stack v1.2, 6.4TB of permissively licensed GitHub code in 384 languages, with an opt-out form; 44 people had opted out when the data was processed ([arXiv:2305.06161](https://arxiv.org/abs/2305.06161) (Li et al., TMLR 2023)). It kept 86 languages, near-deduplicated with MinHash, and removed files matching HumanEval, MBPP, APPS, GSM8K or DS-1000. To redact personal data, 1,399 crowd workers labelled 22,950 entities in 12,000 files, which trained an encoder to find secrets. It detected keys at 70.4 F1, against 6.7 for a regex baseline. StarCoderBase (15.5B) trained on 1T tokens, and StarCoder added 35B Python tokens on top. The paper also shows HumanEval misleading. CodeGen-16B-Mono came close to StarCoderBase on HumanEval (29.3 vs 30.4 pass@1) but scored half as much on DS-1000's data-science tasks (11.7 vs 23.8).

The authors concede the opt-out works per repository, so copies of the same code in other repositories stay in the data, and that the model can still emit personal data. OpenCoder released its whole pipeline and its 960B-token corpus with ablations at 1.5B ([arXiv:2411.04905](https://arxiv.org/abs/2411.04905) (Huang et al., 2024, preprint)). About 75% of GitHub files were exact duplicates. On 485M Python files, deduplicating per file kept 32.7B tokens and deduplicating per repository kept 99.5B, yet the file-level corpus trained the better model on HumanEval and MBPP. Keeping only repositories with at least 5 GitHub stars, as SantaCoder had also tested, lowered training loss but made the model worse, which the authors put down to lost diversity. Dropping the algorithmic and synthetic data from the final annealing stage also hurt. These comparisons are shown only as training curves, one run per setting.

A survey of code language models puts the same pipeline in a table. Its Table 2 lists code corpora from CodeSearchNet (20 GB) and the code part of the Pile (95 GB) up to The Stack (3,136 GB) and The Stack v2 (32 TB). General mixes carry code too: LaMDA 12.5% and PaLM 5%, at 14.0 and 26.2 pass@1 on HumanEval. PaLM-Coder, PaLM plus 7.8B extra code tokens, reached 36.0 at the same 540B size ([arXiv:2311.07989](https://arxiv.org/abs/2311.07989) (Zhang et al., 2023-11, preprint, v7 2024-06)). The scores are 0-shot HumanEval pass@1 taken from cited papers (LaMDA, PaLM and PaLM-Coder from Chowdhery et al.), so they were not run under one harness, and the survey itself calls the benefit of fill-in-the-middle training "controversial".

Two limits are closing in, according to Huyen (*AI Engineering*, ch. 2). **Data:** models consume public text faster than people write it (Villalobos et al., 2022), and sites are shutting crawlers out; Longpre et al. (2024) found 45% of C4 restricted by terms of service or robots.txt after 2023–24. Training on model-generated text is one answer, but *Building AI Agents* (ch. 3) warns of *model collapse*: studies in which models trained on synthetic data lost performance or forgot skills they had learned. Rephrasing real pages is safer than generating new ones. WRAP had Mistral-7B rewrite C4 in Wikipedia and Q&A styles and trained on the rewrites mixed with the originals. A 1.3B model reached the same zero-shot accuracy about 3x faster, and Pile perplexity fell by about half. Training on the rewrites alone hurt perplexity on messy real text ([arXiv:2401.16380](https://arxiv.org/abs/2401.16380) (Maini et al., ACL 2024)). Meta's self-improving pretraining goes a step past rewriting: a post-trained model rewrites each 128-token suffix and judges K policy rollouts against it, and the policy trains by online DPO on the best candidate against the worst. **In continued pretraining of a 1.4B Llama-2-style model for 2,000 steps with 16 rollouts, factuality evals rose from 42.3 to 57.6 and safety from 76.9 to 91.1 against the original checkpoint, and the generation-quality win rate reached 86.3%** ([arXiv:2601.21343](https://arxiv.org/abs/2601.21343) (Tan et al., 2026-01, preprint)). The win rate is judged by the same GPT-OSS-120B that trained the policy, each objective is a separately trained single run, judge tokens are not costed, and standard evals move only from 47.6 to 50.8 in the quality run (49.1 in the safety run), so read it as evidence that the judge's preferences transfer, not that pretraining got cheaper. Its ablation sharpens the collapse warning: SFT on one unjudged rollout fell to a quality win rate of 2.0, while training on the rewrites alone held safety at 86.5 with almost no quality gain. **Electricity:** data centres used an estimated 1–2% of world electricity at the time of writing, projected to reach 4–20% by 2030.

The same data questions arise outside text. Mahajan et al. pretrained ResNeXt-101 on up to 3.5B Instagram images labelled by their own hashtags, with no cleaning. Noise cost little: replacing 25% of the hashtags lost about 2 points of ImageNet-1k accuracy (linear classifier, 32x16d, 1B images, 17k hashtags). Resampling the Zipf-distributed tags uniformly or by square root beat natural sampling by 5 to 6 points (32x4d). Matching the label set to the target mattered as much as volume: the 1.5k ImageNet-aligned hashtags did best on ImageNet-1k, while 17k hashtags won by about 7 points on ImageNet-9k. The 32x16d network reached 84.2% on ImageNet-1k, 4.6 points above the same network trained on ImageNet alone, and 32x48d reached 85.4%. The run took about 22 days on 336 GPUs, the data cannot be replicated, and only ResNeXt was tried ([arXiv:1805.00932](https://arxiv.org/abs/1805.00932) (Mahajan et al., ECCV 2018)).

Multilingual pretraining shows the same data questions at the language level. XLM-R is a 550M masked-language encoder (250K SentencePiece vocabulary, 1.5M updates at batch 8,192) trained on CC-100, 2.5 TB of filtered CommonCrawl in 100 languages. Fine-tuned on English NLI and tested on 15 languages, it averaged 80.9 on XNLI against 66.3 for multilingual BERT, a 14.6-point gap (five seeds; the models also differ in data and size, so the gap is not all from the corpus). Two ablations at BERT-Base scale explain the design. Adding languages at fixed capacity dilutes each one, the *curse of multilinguality*: overall XNLI accuracy fell from 71.8 with 7 languages to 67.7 with 100 on Wikipedia, and more capacity eased it. Cleaned CommonCrawl beat Wikipedia most on low-resource languages (+7 points for Swahili and +4.8 for Urdu with translate-train-all, seven-language model). Sampling languages with exponent 0.3 balanced high- and low-resource languages best. The price of covering 100 languages is small: GLUE dev average 91.8 against 92.8 for English-only RoBERTa ([arXiv:1911.02116](https://arxiv.org/abs/1911.02116) (Conneau et al., ACL 2020)).

![Bar chart of XNLI accuracy for low-resource, high-resource and all languages as the number of pretraining languages grows from 7 to 100: high-resource accuracy falls from about 80 to 75, and low-resource accuracy peaks near 65 at 15 languages before dropping to about 58](../sources/images/conneau-xlmr-fig2.png)
*Image Source: Conneau et al., [Unsupervised Cross-lingual Representation Learning at Scale](https://arxiv.org/abs/1911.02116) (2020), Fig. 2*

### Evaluation sets are data too

How a test set is built decides what it measures, and the choices show in the scores. Narayan et al. built XSum from the one-sentence introduction of 226,711 BBC articles, so 36% of the summary unigrams are not in the article (CNN 17%, DailyMail 17%, NYT 23%). The lead sentence scores ROUGE-2 of 1.61 there against 11.13 on CNN, and a best-single-sentence oracle 29.79 ROUGE-1 against 50.38. ROUGE also misled: in a question-answering study the oracle's summaries answered 15.7% of questions, a topic-aware ConvS2S's 46.05% and the reference's 97.23% ([doi:10.18653/v1/d18-1206](https://doi.org/10.18653/v1/d18-1206) (Narayan et al., EMNLP 2018); one outlet, pre-pretraining baselines). Nie et al. built ANLI in three rounds in which annotators wrote hypotheses until a model in the loop erred. The model's error rate on verified examples fell from 18.33% in round 1 to 8.07% in round 2, RoBERTa trained on SNLI, MNLI, FEVER-NLI and ANLI scored 53.7% on the ANLI test (73.8, 48.9 and 44.4 by round), and a hypothesis-only RoBERTa still reached 41.5% on round 3 ([arXiv:1910.14599](https://arxiv.org/abs/1910.14599) (Nie et al., ACL 2020)). Warstadt et al. labelled 10,657 sentences from linguistics papers as acceptable or not, 70.5% acceptable, so CoLA is scored by Matthews correlation rather than accuracy. The best LSTM-era baseline reached 0.341 in-domain against 0.644 for human annotators, and the majority of five experts agreed with the labels on only 87% of sentences ([arXiv:1805.12471](https://arxiv.org/abs/1805.12471) (Warstadt et al., TACL 2019)). VQA has 0.76M questions on 0.25M images with 10 human answers each, scored min(humans giving the answer / 3, 1). A question-only LSTM got 48.76% (test-dev), against 58.16% for the best model with the image and 83.30% for humans (both test-standard), so language priors carry much of the score ([arXiv:1505.00468](https://arxiv.org/abs/1505.00468) (Antol et al., ICCV 2015)). C-Eval has 13,948 multiple-choice questions over 52 subjects in Chinese, 12,342 of them in the test split used for the scores. GPT-4 scored 66.4% zero-shot answer-only (25.0% is chance) and 53.3% on its eight hard maths and science subjects, and chain of thought did not lift the average (GPT-4 68.7 answer-only against 68.3 with it, five-shot). It is one run per model with no contamination measure ([arXiv:2305.08322](https://arxiv.org/abs/2305.08322) (Huang et al., NeurIPS 2023)).

A benchmark's data can also be gamed by its labelling habits. Gururangan et al. trained a fastText classifier on the hypothesis alone, with no premise, and it scored 67.0% on SNLI (majority class 34.3%) and 53.9% on MNLI-matched. Crowd workers left traces: the median neutral hypothesis is 9 tokens against 60% of entailment hypotheses at 7 or fewer, and "no" appears in 7.6% of MNLI contradictions. A DIIN model fell from 86.5 to 72.7 on SNLI and from 77.0 to 64.1 on MNLI-matched when scored only on the hard subset the hypothesis-only model got wrong. Filtering such examples is a partial remedy, not a clean one ([arXiv:1803.02324](https://arxiv.org/abs/1803.02324) (Gururangan et al., NAACL 2018); English NLI sets, 2018-era models).

The same care applies to a benchmark built in another language. CMMLU has 11.5K multiple-choice questions over 67 subjects, many with China-specific content. GPT-4 scored 70.95% five-shot and most open models stayed under 60%. The open Baichuan2-13B base model (61.92) beat ChatGPT (55.51), and LLaMA2-70B scored 53.21. Scoring method moved results: free generation scored 54.44 against 59.89 for next-token scoring in one comparison, with 6.44% of answers missed by the regex. ChatGPT and GPT-4 were scored by free generation, so they are not strictly comparable with the open models. 74 questions overlap C-Eval ([arXiv:2306.09212](https://arxiv.org/abs/2306.09212) (Li et al., ACL Findings 2024)).

### A toy filter

The sketch applies a T5-style line rule and a CCNet-style paragraph hash to four invented pages. It shows the mechanism only. The counts say nothing about real crawls.

```python
import hashlib, re

pages = [
    "Home\nAbout us\nContact\nWe test every recipe twice. The bread rose well. It tasted good.",
    "Click here to subscribe\nCookie notice\nAll rights reserved",
    "Home\nAbout us\nContact\nShip the model on Friday. Rollbacks are cheap. Monitor the error rate.",
    "{ \"error\": 404 } Lorem ipsum. Lorem ipsum. Lorem ipsum.",
]

def t5_lines(page):
    # keep lines ending in terminal punctuation, as T5's C4 filter does
    return [l for l in page.split("\n") if l.strip().endswith((".", "!", "?", '"'))]

def keep(page):
    kept = t5_lines(page)
    n_sent = sum(len(re.findall(r"[.!?]", l)) for l in kept)
    return n_sent >= 3 and "{" not in page, kept

survivors = []
for p in pages:
    ok, kept = keep(p)
    if ok:
        survivors.append(" ".join(kept))
print("pages kept:", len(survivors), "of", len(pages))

# paragraph-level dedup by hash of normalised text, as CCNet does
seen, dup, total = set(), 0, 0
for p in pages:
    for para in p.split("\n"):
        total += 1
        h = hashlib.md5(re.sub(r"\W+", " ", para.lower()).encode()).hexdigest()
        dup += h in seen
        seen.add(h)
print(f"duplicate paragraphs: {dup} of {total}")
```

```text
pages kept: 2 of 4
duplicate paragraphs: 3 of 12
```

Menus repeat across pages, so the hash catches them even though each page looks fine alone.


---

## Pitfalls

- **Treating more tokens as better tokens.** In the T5 ablations the unfiltered 6.1TB crawl scored worst on every task; a smaller filtered set beat it.
- **Filtering on a single quality score.** Rule-based filters, perplexity filters and classifier filters keep different pages. Check what a filter drops before trusting it.
- **Ignoring the language and code mix.** A mixture sets what the model is good at. Adding code or a second language shifts every other score, and it is hard to undo after the run.
- **Training on your own model's output without limits.** Repeated rounds of synthetic data drift toward the model's own mode and lose the tails.
- **Forgetting that evaluation sets are on the web.** Crawled text can contain benchmark questions, so a high score may reflect memory rather than skill.

---

## Try it

1. Take a folder of text files and apply the T5 line rules: keep lines ending in terminal punctuation, drop pages under three sentences. How much of the text survives?
2. Count the share of near-duplicate paragraphs with a hash of normalised text. What fraction is boilerplate?

<details>
<summary>Answers</summary>

1. The share depends on the source. Menus, headers and footers do not end in terminal punctuation, so they go first.
2. Boilerplate (navigation, cookie notices, licence text) usually dominates the duplicates. CCNet found duplicate paragraphs made up 70% of a monthly Common Crawl snapshot.

</details>

---

## Interview checklist

| Question | Answer |
|---|---|
| Where does pretraining text come from? | Mostly filtered Common Crawl, plus books, code, Wikipedia and increasingly synthetic text |
| Why filter instead of using everything? | In T5's ablation the unfiltered crawl scored worst on every task (GLUE 81.46 against 83.28 for the filtered set) |
| What does repetition do? | A few repeats barely matter. Cycling a small subset 1,024 times hurt GLUE in T5's ablation (79.55) |
| What happens when the data supply runs out? | Teams repeat data, mix in synthetic text and code, or rewrite web text. Models trained on their own output lose the tails (model collapse) |

---

## Next

[15 — The pretraining run: batch, cost and scale](15-pretraining-runs-cost-and-scale.md) prices the loop at real scale and answers the question about the tickets.
