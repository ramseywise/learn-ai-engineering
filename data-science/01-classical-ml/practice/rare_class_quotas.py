# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas"]
# ///
"""The numbers in notes/11's section on sizing a benchmark for rare classes. Run with `uv run rare_class_quotas.py`, a few seconds.

Nothing is fitted. A made-up production mix of document classes and a made-up true accuracy per class, so the truth is known
and each design's error can be measured by drawing the benchmark many times.
"""
import numpy as np
import pandas as pd

pd.set_option("display.width", 160)
CLASSES = pd.DataFrame({"share": [.70, .20, .08, .015, .005], "accuracy": [.97, .92, .85, .70, .50]},
                       index=["invoice", "delivery note", "certificate", "drawing", "safety sheet"])
TRUTH = (CLASSES.share * CLASSES.accuracy).sum()
BUDGET, DRAWS = 1000, 20_000
rng = np.random.default_rng(0)


def draw(sizes):
    """One benchmark per row: accuracy measured in each class, nan where the class got no rows."""
    correct = rng.binomial(sizes.astype(int), CLASSES.accuracy.values, size=(DRAWS, len(CLASSES)))
    with np.errstate(invalid="ignore"):
        return correct, correct / sizes


designs = {"production mix": rng.multinomial(BUDGET, CLASSES.share.values, size=DRAWS),
           "equal quota": np.full((DRAWS, len(CLASSES)), BUDGET // len(CLASSES))}
print(f"true production accuracy {TRUTH:.3f}, benchmark of {BUDGET} labelled rows, {DRAWS:,} draws\n")
rows = []
for name, sizes in designs.items():
    correct, per_class = draw(sizes)
    raw = correct.sum(1) / sizes.sum(1)
    weighted = np.nansum(per_class * CLASSES.share.values, axis=1) / np.sum(~np.isnan(per_class) * CLASSES.share.values, axis=1)
    rows.append(dict(design=name, estimate="unweighted", mean=raw.mean(), sd=raw.std(), bias=raw.mean() - TRUTH))
    rows.append(dict(design=name, estimate="reweighted to production", mean=weighted.mean(), sd=weighted.std(), bias=weighted.mean() - TRUTH))
    table = pd.DataFrame({"rows": sizes.mean(0), "sd_of_accuracy": np.nanstd(per_class, axis=0), "no_rows_at_all": (sizes == 0).mean(0)}, index=CLASSES.index)
    print(f"--- {name}, per class\n{table.round(3).to_string()}\n")
print("--- headline accuracy\n" + pd.DataFrame(rows).round(4).to_string(index=False))

print("\n--- rows needed for a 95% interval of +/- the margin, at the true accuracy: 1.96^2 p(1-p) / margin^2")
need = pd.DataFrame({m: np.ceil(1.96**2 * CLASSES.accuracy * (1 - CLASSES.accuracy) / m**2) for m in (.10, .05, .03)}).astype(int)
need.columns = ["+/-10 points", "+/-5 points", "+/-3 points"]
print(need.to_string())

print("\n--- the production budget a random sample needs to hold 100 safety sheets, and the rule of three for zero errors")
print(f"100 / 0.005 = {100 / .005:,.0f} rows. Zero errors in n rows: 95% upper bound on the error rate about 3/n, so 3/100 = 3%")
