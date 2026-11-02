# Credit default lab

Predicts credit card default when defaulters are rare, and measures what each way of handling the imbalance costs. On a 3% default rate, over 20 seeds with the same splits for every method, it compares doing nothing, class weights, random undersampling, random oversampling, SMOTE and threshold moving by PR-AUC, ROC-AUC, Brier score and expected cost. It also shows the leak from resampling before cross-validation, how much data a rare event needs, how far resampling distorts probabilities and how to fix them, and what PSI sees under covariate shift, prior shift, concept shift and train/serve skew.

```bash
cd data-science/01-classical-ml/practice/credit-default-lab
uv run --python 3.12 --with scikit-learn --with imbalanced-learn --with pandas --with xlrd --with matplotlib --with scipy python credit_default_lab.py
```

It takes about four minutes on a 12-core laptop, including the download. It prints each table, keeps them as CSV files under `results/`, and writes four figures to [`data-science/sources/images/`](../../../sources/images/): `credit-lab-method-comparison.png`, `credit-lab-reliability.png`, `credit-lab-events.png` and `credit-lab-drift.png`. Expect a first line of `30,000 rows, default rate 0.221`, and a boosted model at about PR-AUC 0.142, ROC-AUC 0.760 and Brier 0.028 when nothing is done to the data. Delete `results/` to recompute; a second run reads the tables back in a few seconds.

The data is [Default of Credit Card Clients](https://doi.org/10.24432/C55S3H) (I-Cheng Yeh, UCI Machine Learning Repository, CC BY 4.0): 30,000 Taiwanese card customers in 2005 with a 22.1% default rate. The script fetches the file from UCI on the first run, checks it against a pinned sha256 and caches it in `data/`, which is ignored along with `results/`. To reach 3%, `make_rare()` keeps every good customer and a random subset of defaulters. That rate is our choice, not a fact about the file, and sex, marriage and age are never used as inputs.

The discussion and the tables of results are in [`notes/10-imbalance-errors-and-drift.md`](../../notes/10-imbalance-errors-and-drift.md), whose code blocks import `credit_default_lab.py`.
