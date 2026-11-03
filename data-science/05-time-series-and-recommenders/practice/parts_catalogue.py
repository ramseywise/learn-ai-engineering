"""A generated parts catalogue with known ground truth, for pair matching and benchmark design.

Nothing here comes from a real company or catalogue. Parts, codes and descriptions are drawn from a seeded generator, so
the true relation between any two records is known exactly. The difficulties are ones we chose to put in.

The world has three levels. A record is one line in one plant's system. A part is one manufacturer's product, and several
records can describe it. A spec is what a part must meet: family, dimensions and critical attributes. Two parts with the
same spec are interchangeable. Two parts that differ only in a critical attribute look alike and are not.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from sklearn.feature_extraction.text import TfidfVectorizer

# dimensions and critical attributes per family. Each value lists its ways of being written; the first is canonical.
FAMILIES = {
    "bolt": {
        "names": ["hex bolt", "hexagon screw", "hex cap screw", "bolt hex"],
        "dims": {"d": [6, 8, 10, 12, 16], "l": [20, 30, 40, 50, 60, 80]},
        "render": lambda v: f"M{v['d']}x{v['l']}",
        "critical": {"grade": {"8.8": ["8.8", "cl 8.8"], "10.9": ["10.9", "cl 10.9"],
                               "a2": ["a2-70", "stainless a2", "1.4301"], "a4": ["a4-80", "stainless a4", "1.4401"]}},
    },
    "bearing": {
        "names": ["ball bearing", "deep groove bearing", "bearing dgbb", "radial ball brg"],
        "dims": {"d": [20, 25, 30, 35, 40], "l": [205, 206, 207, 208]},
        "render": lambda v: f"{v['l']} bore {v['d']}",
        "critical": {"seal": {"open": ["open", "unsealed"], "2rs": ["2rs", "rubber sealed"], "zz": ["zz", "metal shield"]},
                     "clear": {"c3": ["c3", "clearance c3"], "cn": ["cn", "normal clearance"]}},
    },
    "oring": {
        "names": ["o-ring", "o ring", "oring seal", "toric seal"],
        "dims": {"d": [10, 16, 25, 40, 63], "l": [2, 3, 4, 5]},
        "render": lambda v: f"{v['d']}x{v['l']}",
        "critical": {"mat": {"nbr": ["nbr", "nitrile"], "fkm": ["fkm", "viton"], "epdm": ["epdm", "ethylene propylene"]}},
    },
    "valve": {
        "names": ["gate valve", "valve gate", "wedge gate valve", "isolation valve"],
        "dims": {"d": [25, 50, 80, 100], "l": [150, 200, 250]},
        "render": lambda v: f"DN{v['d']} L{v['l']}",
        "critical": {"pn": {"pn16": ["pn16", "pn 16"], "pn40": ["pn40", "pn 40"]},
                     "body": {"gg25": ["gg25", "cast iron"], "1.4408": ["1.4408", "stainless body"]}},
    },
}
VENDORS = ["Arvol", "Benta", "Corsk", "Dovra", "Elmig", "Fenro", "Garst", "Holvik"]
PLANTS = ["north", "south", "east", "west"]
NOISE = ["pack 10", "pack 100", "new", "spare", "stock", "maint", "urgent", "alt", "ref only"]
# Spellings an extractor knows. Some in FAMILIES are left out on purpose, so extraction misses them.
UNKNOWN_TO_EXTRACTOR = {"1.4301", "1.4401", "metal shield", "ethylene propylene", "stainless body"}


def make_catalogue(seed=0, n_specs=500, missing=.15, typo=.05):
    """Return records and parts. Each record's `part` and `spec` are the ground truth."""
    rng = np.random.default_rng(seed)
    specs, seen = [], set()
    names = list(FAMILIES)
    while len(specs) < n_specs:
        base = dict(family=names[rng.integers(len(names))])
        fam = FAMILIES[base["family"]]
        base.update({k: int(rng.choice(v)) for k, v in fam["dims"].items()})
        base.update({k: str(rng.choice(list(v))) for k, v in fam["critical"].items()})
        specs.append(base)
        # A sibling: same family and dimensions, one critical attribute different. Most specs have one.
        if rng.random() < .7:
            attr = str(rng.choice(list(fam["critical"])))
            other = [x for x in fam["critical"][attr] if x != base[attr]]
            specs.append({**base, attr: str(rng.choice(other))})
    unique = []
    for s in specs:
        key = tuple(sorted(s.items()))
        if key not in seen:
            seen.add(key)
            unique.append(s)
    parts = []
    for spec_id, s in enumerate(unique):
        for _ in range(1 + rng.poisson(.7)):  # one spec, one or more makers: equivalents
            parts.append({**s, "spec": spec_id, "part": len(parts), "vendor": str(rng.choice(VENDORS)),
                          "code": f"{rng.integers(10, 99)}{chr(65 + rng.integers(26))}{rng.integers(1000, 9999)}"})
    parts = pd.DataFrame(parts)
    records = []
    for p in parts.to_dict("records"):
        for _ in range(1 + rng.poisson(1.2)):  # one part, several plants' records: duplicates
            records.append({"record": len(records), "part": p["part"], "spec": p["spec"], "family": p["family"],
                            "plant": str(rng.choice(PLANTS)), "text": _render(p, rng, missing, typo)})
    return pd.DataFrame(records), parts


def _render(p, rng, missing, typo):
    fam = FAMILIES[p["family"]]
    bits = [str(rng.choice(fam["names"])), fam["render"](p)]
    for attr, values in fam["critical"].items():
        if rng.random() > missing:
            bits.append(str(rng.choice(values[p[attr]])))
    if rng.random() < .7:
        bits.append(p["vendor"])
    if rng.random() < .5:
        bits.append(p["code"])
    if rng.random() < .3:
        bits.append(str(rng.choice(NOISE)))
    order = [bits[0], *rng.permutation(bits[1:]).tolist()]
    text = " ".join(order)
    if rng.random() < .5:
        text = text.upper()
    if rng.random() < typo and len(text) > 6:
        i = rng.integers(1, len(text) - 2)
        text = text[:i] + text[i + 1] + text[i] + text[i + 2:]
    return text


def extract(text, family):
    """Critical attributes a rule-based extractor can read. An attribute it can't read comes back as None."""
    low = text.lower()
    out = {}
    for attr, values in FAMILIES[family]["critical"].items():
        hits = {canon for canon, spellings in values.items()
                for s in spellings if s not in UNKNOWN_TO_EXTRACTOR and re.search(rf"(?<![\w.-]){re.escape(s)}(?![\w-])", low)}
        out[attr] = hits.pop() if len(hits) == 1 else None
    return out


def candidates(records, k=10):
    """Blocking: each record's k nearest records by character n-gram TF-IDF. Returns left, right indices, left < right."""
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True, lowercase=True)
    X = vec.fit_transform(records.text)
    sim = (X @ X.T).tocsr()
    pairs = set()
    for i in range(X.shape[0]):
        row = sim.getrow(i)
        top = row.indices[np.argsort(-row.data)[:k + 1]]
        pairs.update((min(i, int(j)), max(i, int(j))) for j in top if j != i)
    return np.array(sorted(pairs))


def relation(records, left, right):
    """The true relation of each pair: same part, equivalent, similar, or different."""
    lf, rf = records.iloc[left], records.iloc[right]
    same_part = lf.part.values == rf.part.values
    same_spec = lf.spec.values == rf.spec.values
    out = np.full(len(left), "different", dtype=object)
    return out, same_part, same_spec


def label_pairs(records, parts, pairs):
    """A frame of candidate pairs with their relation. 'similar' means same family and dimensions, different spec."""
    info = parts.drop_duplicates("spec").set_index("spec")
    lf, rf = records.iloc[pairs[:, 0]], records.iloc[pairs[:, 1]]
    a, b = info.loc[lf.spec.values], info.loc[rf.spec.values]
    same_shape = (a.family.values == b.family.values) & (a.d.values == b.d.values) & (a.l.values == b.l.values)
    rel = np.where(lf.part.values == rf.part.values, "same_part",
                   np.where(lf.spec.values == rf.spec.values, "equivalent",
                            np.where(same_shape, "similar", "different")))
    return pd.DataFrame({"left": pairs[:, 0], "right": pairs[:, 1], "relation": rel,
                         "left_part": lf.part.values, "right_part": rf.part.values})


def components(n, left, right):
    """Connected components over n nodes: what transitive closure of a set of match decisions produces."""
    graph = coo_matrix((np.ones(len(left)), (left, right)), shape=(n, n))
    return connected_components(graph, directed=False)[1]


def pair_scores(truth, pred):
    """Precision, recall and F1 for boolean arrays."""
    tp = np.sum(truth & pred)
    precision = tp / max(pred.sum(), 1)
    recall = tp / max(truth.sum(), 1)
    return precision, recall, 2 * precision * recall / max(precision + recall, 1e-12)
