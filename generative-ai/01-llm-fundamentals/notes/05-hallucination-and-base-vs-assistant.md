---
origin: synthesis
sources:
  - "Huyen, AI Engineering (O'Reilly, 2025), ch. 1–2"
  - https://arxiv.org/abs/2201.08239
  - https://arxiv.org/abs/2304.00612
  - https://arxiv.org/abs/2301.06627
  - https://arxiv.org/abs/2009.11462
  - https://arxiv.org/abs/2004.09456
  - https://arxiv.org/abs/2108.07258
confidence: high
cleaned: 2026-11-01
---

# 5 — Hallucination and base versus assistant

@@HOOK@@

---

## Same input, different output

Huyen calls the probabilistic nature of a model the root of its two most reported problems (*AI Engineering*, ch. 2):

- **Inconsistency.** Sampling makes outputs vary by design. Fixing the temperature, top-p, top-k and seed reduces this but does not remove it: hosted models run on different machines, which do not execute the same arithmetic in exactly the same way, and on an API you do not choose the machine. Cache answers that must stay the same.
- **Hallucination.** Huyen reports two hypotheses for *why*, neither settled. In the first (Ortega et al., 2021, DeepMind), a model cannot tell the text it was given from the text it generated, so an early wrong token gets treated as fact and built on; Zhang et al. (2023) call this snowballing, with an example where a model, having started from a wrong assumption, claims that 9,677 is divisible by 13 although it answers correctly when asked directly. In the second (Leo Gao, then John Schulman in an April 2023 talk, both at OpenAI), supervised fine-tuning teaches a model to imitate labelers' answers that use knowledge the model does not have, which trains it to make things up. The first blames self-supervision, the second supervision, so they can both be true. Schulman said RLHF reduced hallucination at OpenAI; the InstructGPT paper measured the opposite, with RLHF plus SFT hallucinating more than SFT alone on its closed-domain tasks, even though labelers preferred the RLHF model overall. The practical upshot is the same either way: answer from provided context, ask for concise answers (fewer tokens, fewer chances to invent), and check claims.

---

## What a base model is not

A pretrained model continues text. Huyen calls it a "completion machine" (*AI Engineering*, ch. 1). Its training is *self-supervised*: the label for each position is the next token of the text, so the sentence "I love street food." yields six training examples, from (BOS → "I") to ("I love street food." → EOS), with no human labelling. That is why pretraining scales to trillions of tokens, and why the model learns what text looks like rather than what is true. Ask it a question and it may produce more questions. The assistant behaviour (answering, refusing, following a system prompt, calling tools) comes from post-training: supervised fine-tuning on demonstrations and then preference optimization. That pipeline is [chapters 06–09](06-pretraining-data-and-objectives.md) and, in depth, [05-RL](../../05-RL/README.md).

Scale does not supply that behaviour. In Google's LaMDA, crowdworkers rated the pretrained model's dialogue responses safe 84.8% of the time at 2B and 88% at 137B. Fine-tuning on annotated dialogue, less than 0.001% of the pretraining data, raised the 137B model to 95.2% and its groundedness from 57.9% to 73.2% ([arXiv:2201.08239](https://arxiv.org/abs/2201.08239) (Thoppilan et al., 2022, preprint)). Bowman's survey puts it this way: instruction following "isn't inherent to the model, but rather is grafted onto it using highly imperfect tools". So a model can fail a request and then succeed once it is reworded, and one failed prompt is not evidence that the capability is missing ([arXiv:2304.00612](https://arxiv.org/abs/2304.00612) (Bowman, Critical AI 2024)).

A base model also reproduces what is in its training text, including the parts nobody wanted. Scored with Google's Perspective API, 4.3% of OpenAI's WebText (GPT-2's training corpus) was toxic, and GPT-2 had trained on at least 40K documents from the quarantined subreddit /r/The_Donald. GPT-1, GPT-2, GPT-3 and CTRL all reached an expected maximum toxicity above 0.5 within 100 generations from an empty prompt. Starting from non-toxic web prompts, GPT-3 produced at least one toxic continuation in 25 samples half the time (0.50). For GPT-2 that rate was 0.48. Further pretraining on non-toxic text cut it to 0.23, PPLM steering to 0.17 and a banned-word filter only to 0.43, and the authors conclude that "no current method is failsafe" ([arXiv:2009.11462](https://arxiv.org/abs/2009.11462) (Gehman et al., Findings of EMNLP 2020)). Those scores come from a classifier that has known biases of its own, against African American English and mentions of identity groups. A better language model is not less biased. On StereoSet's 16,995 crowd-written test items, models' language-modelling scores and stereotype scores correlated at Spearman 0.87. GPT-2 large picked the stereotyped completion over the anti-stereotyped one 60.0% of the time, where 50% is unbiased, and the strongest model, an ensemble, 62.3% ([arXiv:2004.09456](https://arxiv.org/abs/2004.09456) (Nadeem et al., ACL 2021)). Bommasani et al., who coined the term *foundation model*, call the structural version of this **homogenization**. Almost every system is adapted from one of a few base models, so "any flaws in the model are blindly inherited by all adapted models", and the base model becomes a single point of failure ([arXiv:2108.07258](https://arxiv.org/abs/2108.07258) (Bommasani et al., 2021 ⚑)). Post-training and the checks applied downstream have to catch what pretraining put in.

Fluent text is also not evidence of thought. Mahowald et al. separate *formal* linguistic competence (grammar and the rules of a language) from *functional* competence (reasoning, world knowledge, tracking a situation, social inference), which in humans run on different brain networks. Next-token prediction delivers the first reliably. A BabyLM model trained on at most 100M words, about what a child hears, scored 86% on BLiMP's grammatical-versus-ungrammatical sentence pairs against a human baseline of 89%. The second stays patchy and usually comes from fine-tuning or added tools. It is a position paper, and its evidence is drawn from other studies ([arXiv:2301.06627](https://arxiv.org/abs/2301.06627) (Mahowald et al., Trends in Cognitive Sciences 2024)).

@@END@@
