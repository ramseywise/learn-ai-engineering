# 04 — LLMs from scratch

> Build the whole stack of a language model by hand, from the chain rule to GPT-2, so that nothing underneath stays magic. Deck: [`slides/llms-from-scratch.pptx`](slides/llms-from-scratch.pptx) (source [`slides/deck.yaml`](slides/deck.yaml)). Practice: [`practice/`](practice/). References: [`references.md`](references.md).

## What it is

Three chapters built on Karpathy's [*Neural Networks: Zero to Hero*](https://karpathy.ai/zero-to-hero.html): micrograd (a backpropagation engine in about 100 lines), makemore (character-level language models, from counted bigrams to a WaveNet-style tree) and nanoGPT (a transformer on Tiny Shakespeare, then GPT-2 124M with OpenAI's weights loaded in). Watch the lectures and code along in the notebooks. The chapters are what you come back to, with every CPU-sized experiment rerun and its output shown.

## Why it matters

Most of what breaks in training has a one-line explanation once you have built the thing: a first loss of 27 where 3.30 belongs, tanh units saturated at 70%, an accumulation loop whose gradients are four times too large, a BatchNorm over the wrong dimension that raises no error. People who have written the stack can read those failures. There is also a floor to reach before the [generative AI](../../generative-ai/README.md) material makes sense, as tokenisation, attention and pre-training all assume this one.

## The story

A network is one big expression, and backpropagation is the chain rule walked through it in reverse, which micrograd writes in about 100 lines and checks against PyTorch. Language modelling then starts at its smallest: given 32,033 names, predict the following character, and beat the 3.30 of uniform guessing. Counting pairs gets to 2.45. An MLP over three characters gets to 2.17, and looking inside it shows a bad init, saturated units and the case for BatchNorm, which bring it to 2.10. A tree over eight characters gets to 2.00, and there it hits a limit, as which characters matter is fixed by their position. Attention lets each token choose from the data what to look at, and residual connections and LayerNorm make a stack of it trainable. The same code at full size is GPT-2. Load OpenAI's weights into it and every logit agrees with the reference, which leaves only the question of how to train one, and then what to do with it.

## Reading order

| # | Note | Question it answers |
|---|---|---|
| 01 | [micrograd](notes/01-micrograd.md) | What does `loss.backward()` actually do, and why does it beat nudging each parameter? |
| 02 | [makemore](notes/02-makemore.md) | What is a language model at its smallest, and how do you keep a deep one trainable? |
| 03 | [nanoGPT](notes/03-nanogpt.md) | What is attention, what does each piece of a transformer buy, and how is GPT-2 trained? |

Then continue with [LLM fundamentals](../../generative-ai/01-llm-fundamentals/README.md) in generative AI, which starts from tokenisation and treats LLMs as systems.

## Rules of thumb

- Check the first loss against `-log(1/vocab)` before you train anything.
- Compare gradients against a numerical or autograd reference when you write one by hand.
- Plot saturation, gradient scale and the update-to-data ratio by layer, because a loss curve cannot explain a failure.
- Check tensor shapes after every layer. The bugs that matter here raise no error.
- `loss / grad_accum_steps`, every time.
- Prove an architecture by loading known weights and comparing logits before you pay to train it.
- A low loss on one dataset does not compare with a low loss on another. Use a held-out benchmark, and still ask about leakage.

## Practice

The chapters' code blocks run in order from this folder:

```bash
uv run --python 3.12 --with torch --with scikit-learn python practice/run_note.py notes/01-micrograd.md                    # about 1 minute
uv run --python 3.12 --with torch python practice/run_note.py notes/02-makemore.md                                           # about 15 minutes on CPU
uv run --python 3.12 --with torch --with transformers --with tiktoken python practice/run_note.py notes/03-nanogpt.md        # about 6 minutes on CPU, downloads GPT-2
```

[`practice/nn-zero-to-hero/`](practice/nn-zero-to-hero/) is the vendored lecture code, MIT licensed. See its [README](practice/nn-zero-to-hero/README.md).

| Folder | What is there | What it needs |
|---|---|---|
| [`micrograd/`](practice/nn-zero-to-hero/micrograd/) | Lecture notebooks | Offline; `graphviz` and `torch` for some cells |
| [`makemore/`](practice/nn-zero-to-hero/makemore/) | Five notebooks, `names.txt` | Offline, CPU |
| [`nanogpt/bigram.py`](practice/nn-zero-to-hero/nanogpt/bigram.py), [`gpt.py`](practice/nn-zero-to-hero/nanogpt/gpt.py) | Bigram and full character-level transformer, `input.txt` | Offline; `bigram.py` on CPU, `gpt.py` on a GPU at default size |
| [`nanogpt/build-nanogpt/`](practice/nn-zero-to-hero/nanogpt/build-nanogpt/) | GPT-2 reproduction | GPUs and FineWeb-Edu for training; [`play.ipynb`](practice/nn-zero-to-hero/nanogpt/build-nanogpt/play.ipynb) only needs the weights |
