# Generative AI: general resources

Links that belong to no single pillar. They were kept from the retired `resources.md` (2026-10-31). Each pillar's own courses, books and papers are in its `references.md`.

## Python and ML toolchain

These are the libraries the notebooks assume. Install per project with `uv`/`pip` from
each project's `pyproject.toml`. Don't install them all at once.

| Area | Libraries |
|---|---|
| Data | [NumPy](https://numpy.org/doc/), [pandas](https://pandas.pydata.org/docs/), [SciPy](https://docs.scipy.org/doc/scipy/), [Matplotlib](https://matplotlib.org/stable/), [seaborn](https://seaborn.pydata.org/) |
| Classical ML | [scikit-learn](https://scikit-learn.org/stable/), [XGBoost](https://xgboost.readthedocs.io/), [LightGBM](https://lightgbm.readthedocs.io/), [CatBoost](https://catboost.ai/docs/) |
| Deep learning | [PyTorch](https://pytorch.org/docs/), [TensorFlow](https://www.tensorflow.org/learn) / [Keras](https://keras.io/) |
| Vision | [OpenCV](https://docs.opencv.org/), [scikit-image](https://scikit-image.org/docs/stable/), [Pillow](https://pillow.readthedocs.io/) |

## Foundations (math, Python, classical ML)

- [MIT 18.06 Linear Algebra](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/): Strang's lectures.
- [CS50's Introduction to Programming with Python](https://www.edx.org/learn/python/harvard-university-cs50-s-introduction-to-programming-with-python); practice on [HackerRank Python](https://www.hackerrank.com/domains/python) (see [`programming/`](../programming/README.md)).
- [Machine Learning Specialization (Andrew Ng)](https://www.coursera.org/specializations/machine-learning-introduction): the course behind [`data-science/`](../data-science/README.md)'s Ng notebooks.
- [CS50's Introduction to AI](https://cs50.harvard.edu/ai/) and [AIMA](https://aima.cs.berkeley.edu/), for classical AI: search, reasoning, planning.
- [Designing Machine Learning Systems](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/) (Huyen) and [Made With ML](https://madewithml.com/): production ML.

## Prompting → [ai-engineering/01-prompt](../ai-engineering/01-prompt-engineering/README.md)

- [Anthropic prompt engineering docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) · [OpenAI Cookbook](https://cookbook.openai.com/)

## Staying current

- Papers: the [AI Papers of the Week](../ai-engineering/02-context-engineering/references.md) flow (`/papers` skill) · [Distill](https://distill.pub/) (archive)
- Newsletters: [TLDR AI](https://tldr.tech/ai) · [The Rundown AI](https://www.therundown.ai/)
