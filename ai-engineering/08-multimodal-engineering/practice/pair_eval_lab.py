# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Score four fake vision models under four test designs for notes/07, and see which shortcut each design exposes.

Run from this folder (a second or two, standard library only, downloads no data, calls no model):
    uv run pair_eval_lab.py

The fixture is a generated set of invoice questions, with no images. The "models" are small functions with a known
behaviour, so we know the right verdict before scoring: one reads the invoice with a stated accuracy and three take a
shortcut. Scorers, pairing, rotation and the bootstrap are real code you can point at real predictions. The numbers
describe these made-up models, not any real one.
"""
# %%
import random

SEED, N_PAIRS, N_BOOT = 7, 150, 2000
CURRENCIES = ["EUR", "USD", "GBP", "DKK"]


# %% Fixture: pairs of invoices that differ in one field, so an image-blind answer can be right on only one
def make_pairs(rng, n):
    pairs = []
    for i in range(n):
        common, rare = rng.sample(CURRENCIES, 2)
        pairs.append({"id": i, "question": "Which currency is the total in?", "a": common, "b": rare,
                      "prior": "EUR" if "EUR" in (common, rare) else common})
    return pairs


# %% Models. Each gets the image's true value, the options as shown, and answers with an option index
def reader(rng, truth, options, prior):
    """Reads the image, and misreads with a stated probability."""
    return options.index(truth) if rng.random() < 0.88 else rng.randrange(len(options))


def prior_guesser(rng, truth, options, prior):
    """Ignores the image and always gives the commonest currency."""
    return options.index(prior) if prior in options else 0


def first_option(rng, truth, options, prior):
    """Ignores the image and picks option A."""
    return 0


def half_reader(rng, truth, options, prior):
    """Reads half the time and takes the prior otherwise, as a model that leans on context might."""
    return options.index(truth) if rng.random() < 0.5 else prior_guesser(rng, truth, options, prior)


def yes_model(rng, present, plausible):
    return rng.random() < (0.92 if present else (0.6 if plausible else 0.1))


def careful_yes_model(rng, present, plausible):
    return rng.random() < (0.88 if present else 0.05)


MODELS = {"reads at 88%": (reader, careful_yes_model), "always the prior": (prior_guesser, yes_model),
          "always option A": (first_option, yes_model), "half reads, half prior": (half_reader, yes_model)}


# %% Test designs, each returning one 0 or 1 per unit, so the same bootstrap serves them all
def options_for(rng, pair):
    others = [c for c in CURRENCIES if c not in (pair["a"], pair["b"])]
    return rng.sample([pair["a"], pair["b"], *others], 4)


def per_image(rng, model, pairs):
    """The usual score: one image from each pair, chosen at random, and one answer."""
    out = []
    for p in pairs:
        truth = p["a"] if rng.random() < 0.5 else p["b"]
        opts = options_for(rng, p)
        out.append(int(opts[model(rng, truth, opts, p["prior"])] == truth))
    return out


def paired(rng, model, pairs):
    """Both images in a pair must be right. A model that ignores the image can't pass where the answers differ."""
    out = []
    for p in pairs:
        opts = options_for(rng, p)
        out.append(int(all(opts[model(rng, t, opts, p["prior"])] == t for t in (p["a"], p["b"]))))
    return out


def circular(rng, model, pairs):
    """CircularEval: rotate the options through every position, and all rotations must be right."""
    out = []
    for p in pairs:
        truth, opts = rng.choice((p["a"], p["b"])), options_for(rng, p)
        rotations = [opts[s:] + opts[:s] for s in range(len(opts))]
        out.append(int(all(r[model(rng, truth, r, p["prior"])] == truth for r in rotations)))
    return out


def absent_field(rng, yes_fn, n):
    """Balanced 'is this field on the invoice?' with plausible absent fields. Returns per-unit correctness and yes-ratio."""
    correct, yes = [], 0
    for i in range(n):
        present = i % 2 == 0
        said_yes = yes_fn(rng, present, True)
        yes += said_yes
        correct.append(int(said_yes == present))
    return correct, yes / n


def bootstrap(rng, xs):
    means = sorted(sum(rng.choices(xs, k=len(xs))) / len(xs) for _ in range(N_BOOT))
    return sum(xs) / len(xs), means[int(0.025 * N_BOOT)], means[int(0.975 * N_BOOT)]


def fmt(stat):
    return f"{stat[0]:.2f} [{stat[1]:.2f}, {stat[2]:.2f}]"


# %% Report
rng = random.Random(SEED)
pairs = make_pairs(rng, N_PAIRS)
print(f"{N_PAIRS} generated invoice pairs, 95% bootstrap intervals over {N_BOOT} resamples, seed {SEED}\n")
print(f"{'model':24}{'per image':>20}{'paired':>20}{'circular':>20}{'absent field':>20}{'yes-ratio':>11}")
for name, (fn, yes_fn) in MODELS.items():
    plain = bootstrap(rng, per_image(rng, fn, pairs))
    pair = bootstrap(rng, paired(rng, fn, pairs))
    circ = bootstrap(rng, circular(rng, fn, pairs))
    absent, yes = absent_field(rng, yes_fn, 2 * N_PAIRS)
    print(f"{name:24}{fmt(plain):>20}{fmt(pair):>20}{fmt(circ):>20}{fmt(bootstrap(rng, absent)):>20}{yes:11.2f}")
