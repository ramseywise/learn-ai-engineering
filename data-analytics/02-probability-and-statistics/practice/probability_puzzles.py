# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy"]
# ///
"""Interview probability puzzles: closed form against simulation.

Each puzzle states its answer exactly, then checks it with a Monte Carlo run.
The habit to build: say the closed form first, then know how you would verify it
in ten lines if the interviewer doubts it.

Run from this folder with: uv run probability_puzzles.py
"""
from math import comb, exp, factorial

import numpy as np

rng = np.random.default_rng(7)
N = 200_000  # simulated repetitions per puzzle
ROWS: list[tuple[str, float, float]] = []


def record(name: str, exact: float, simulated: float) -> None:
    ROWS.append((name, exact, simulated))


# %% Bayes: a positive test for a rare condition
# Prevalence 1%, sensitivity 95%, false positive rate 5%. P(condition | positive)?
prev, sens, fpr = 0.01, 0.95, 0.05
exact = prev * sens / (prev * sens + (1 - prev) * fpr)
sick = rng.random(N) < prev
positive = np.where(sick, rng.random(N) < sens, rng.random(N) < fpr)
record("P(condition | positive test)", exact, sick[positive].mean())

# %% Bayes again: a fraud flag
# 0.1% of transactions are fraud. The model flags 99% of fraud and 1% of legitimate ones.
prev, sens, fpr = 0.001, 0.99, 0.01
exact = prev * sens / (prev * sens + (1 - prev) * fpr)
M = 2_000_000  # rare event, so more draws
fraud = rng.random(M) < prev
flag = np.where(fraud, rng.random(M) < sens, rng.random(M) < fpr)
record("P(fraud | flagged)", exact, fraud[flag].mean())

# %% Complement rule: at least one six in four rolls
exact = 1 - (5 / 6) ** 4
rolls = rng.integers(1, 7, size=(N, 4))
record("P(at least one six in 4 rolls)", exact, (rolls == 6).any(axis=1).mean())

# %% Birthday problem: 23 people, any shared birthday
exact = 1 - np.prod([(365 - i) / 365 for i in range(23)])
days = rng.integers(0, 365, size=(N, 23))
days.sort(axis=1)
record("P(shared birthday, 23 people)", exact, (np.diff(days, axis=1) == 0).any(axis=1).mean())

# %% Conditioning: two children, at least one is a boy
kids = rng.integers(0, 2, size=(N, 2))  # 1 = boy
at_least_one = kids.sum(axis=1) >= 1
record("P(two boys | at least one boy)", 1 / 3, (kids.sum(axis=1) == 2)[at_least_one].mean())
older_boy = kids[:, 0] == 1
record("P(two boys | older is a boy)", 1 / 2, (kids.sum(axis=1) == 2)[older_boy].mean())

# %% Monty Hall: win rate when you always switch
car = rng.integers(0, 3, size=N)
pick = rng.integers(0, 3, size=N)
record("P(win | switch), Monty Hall", 2 / 3, (car != pick).mean())  # switching wins when the first pick was wrong

# %% Expected flips until the first head, and until two heads in a row
# E[first head] = 1/p = 2. For HH: E = 1 + E1/2 + E/2 and E1 = 1 + E/2, so E = 6.
def flips_until_hh(r: np.random.Generator) -> int:
    run = n = 0
    while run < 2:
        n += 1
        run = run + 1 if r.random() < 0.5 else 0
    return n


record("E[flips to first head]", 2.0, rng.geometric(0.5, size=N).mean())
record("E[flips to HH]", 6.0, np.mean([flips_until_hh(rng) for _ in range(40_000)]))

# %% Coupon collector: rolls until every face of a die has appeared
exact = 6 * sum(1 / k for k in range(1, 7))  # 14.7
def rolls_until_all(r: np.random.Generator) -> int:
    seen, n = set(), 0
    while len(seen) < 6:
        seen.add(int(r.integers(1, 7)))
        n += 1
    return n


record("E[rolls to see all six faces]", exact, np.mean([rolls_until_all(rng) for _ in range(40_000)]))

# %% Optional reroll: roll a die for its face value, with one optional reroll
# Reroll when the first roll is below the reroll's expectation of 3.5, so on 1, 2 or 3.
first, second = rng.integers(1, 7, size=N), rng.integers(1, 7, size=N)
record("E[payout with one optional reroll]", 0.5 * 5 + 0.5 * 3.5, np.where(first <= 3, second, first).mean())

# %% Binomial: 10 fair flips
record("P(exactly 5 heads in 10)", comb(10, 5) / 2**10, (rng.binomial(10, 0.5, size=N) == 5).mean())
record("P(8 or more heads in 10)", sum(comb(10, k) for k in (8, 9, 10)) / 2**10, (rng.binomial(10, 0.5, size=N) >= 8).mean())

# %% Poisson: tickets arrive at 3 an hour
record("P(no tickets in 20 minutes)", exp(-1), (rng.poisson(1.0, size=N) == 0).mean())
exact = 1 - sum(exp(-3) * 3**k / factorial(k) for k in (0, 1))
record("P(2 or more tickets in an hour)", exact, (rng.poisson(3.0, size=N) >= 2).mean())

# %% Cards: two aces from the top of a shuffled deck
deck = np.array([1] * 4 + [0] * 48)
draws = rng.permuted(np.tile(deck, (N, 1)), axis=1)[:, :2]
record("P(two aces in two draws)", 4 / 52 * 3 / 51, (draws.sum(axis=1) == 2).mean())

# %% Uniforms: a stick broken at a uniform point, and the larger of two uniforms
u = rng.random(N)
record("E[longer piece of a broken stick]", 0.75, np.maximum(u, 1 - u).mean())
record("E[max of two Uniform(0,1)]", 2 / 3, np.maximum(rng.random(N), rng.random(N)).mean())

# %% von Neumann: a fair bit from a coin with P(heads) = 0.7
# Flip twice. HT -> 1, TH -> 0, otherwise flip again. Both orders have probability p(1-p).
p = 0.7
a, b = rng.random(N) < p, rng.random(N) < p
keep = a != b
record("P(output 1) from a 0.7 coin", 0.5, a[keep].mean())
record("E[flips per fair bit], p=0.7", 1 / (p * (1 - p)), 2 / keep.mean())

# %% report
print(f"{'puzzle':<38}{'exact':>10}{'simulated':>12}{'gap':>9}")
worst = 0.0
for name, exact, sim in ROWS:
    gap = abs(sim - exact) / max(abs(exact), 1e-12)
    worst = max(worst, gap)
    print(f"{name:<38}{exact:>10.4f}{sim:>12.4f}{gap:>8.1%}")
assert worst < 0.05, f"a simulation is more than 5% from its closed form ({worst:.1%})"
print(f"\nAll {len(ROWS)} simulations within 5% of the closed form.")

# %% Try it
# 1. Expected flips until HT (not HH). Guess first: is it more or fewer than 6? Then simulate.
# 2. Three dice: P(the sum is 10). Count the outcomes by hand, then check.
# 3. Change the prevalence in the first puzzle to 10%. What happens to the posterior, and why?
# 4. Two people agree to meet between 12:00 and 13:00 and each waits 15 minutes. P(they meet)?
