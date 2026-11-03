"""Pretrained encoder, pairs from match labels, optional mined negatives: the training behind notes/05's two scripts.

Imported by 05_similarity_lab.py and 05_similarity_tryit.py, which declare the dependencies. Not run on its own.
"""
import warnings

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

from parts_catalogue import components

warnings.filterwarnings("ignore")
pd.set_option("display.width", 160)
DEVICE = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SEEDS = range(3)
STEPS, BATCH, LR, TEMPERATURE, K = 400, 32, 2e-5, .05, 10


def sibling_of(parts):
    """Spec pairs with the same family and dimensions: the look-alikes that are not safe to swap."""
    info = parts.drop_duplicates("spec")
    return {s: set(g.spec) - {s} for _, g in info.groupby(["family", "d", "l"]) for s in g.spec}


def evaluate(vectors, records, parts, seen_specs=None):
    """Each record queries all the others. Recall@K of interchangeable records, and look-alikes in the top K.

    With seen_specs, also splits both by whether the query's spec occurred in training.
    """
    sim = vectors @ vectors.T
    np.fill_diagonal(sim, -np.inf)
    top = np.argpartition(-sim, K, axis=1)[:, :K]
    spec = records.spec.values
    siblings = sibling_of(parts)
    recalls, unsafe, seen = [], [], []
    for i in range(len(records)):
        relevant = (spec == spec[i]).sum() - 1
        if relevant:
            recalls.append((spec[top[i]] == spec[i]).sum() / min(relevant, K))
            unsafe.append(np.isin(spec[top[i]], list(siblings[spec[i]])).mean())
            seen.append(seen_specs is not None and spec[i] in seen_specs)
    out = dict(recall=np.mean(recalls), unsafe_in_top=np.mean(unsafe))
    if seen_specs is not None:
        recalls, unsafe, seen = np.array(recalls), np.array(unsafe), np.array(seen)
        out |= dict(recall_seen=recalls[seen].mean(), recall_unseen=recalls[~seen].mean(), unsafe_seen=unsafe[seen].mean(), unsafe_unseen=unsafe[~seen].mean())
    return out


def labelled_pairs(records, n, rng):
    """n known interchangeable pairs, the only labels training sees. Closing them gives the groups we know about."""
    candidates = [(a, b) for idx in records.groupby("spec").indices.values() for i, a in enumerate(idx) for b in idx[i + 1:]]
    pick = rng.permutation(len(candidates))[:n]
    pairs = np.array(candidates)[pick]
    return pairs, components(len(records), pairs[:, 0], pairs[:, 1])


def encode(model, texts):
    return model.encode(list(texts), batch_size=256, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)


def forward(model, texts):
    features = {k: v.to(DEVICE) if torch.is_tensor(v) else v for k, v in model.preprocess(list(texts)).items()}
    return F.normalize(model(features)["sentence_embedding"], dim=1)


def mine(model, records, pairs, groups, band, oracle):
    """For each anchor, the records its current embedding ranks in `band`, leaving out what the labels say is a match."""
    anchors = np.unique(pairs[:, 0])
    vectors = encode(model, records.text)
    order = np.argsort(-(vectors[anchors] @ vectors.T), axis=1)
    spec, out, false_negatives, total = records.spec.values, {}, 0, 0
    for a, row in zip(anchors, order):
        row = row[groups[row] != groups[a]]
        hits = row[band[0]:band[1]]
        false_negatives += (spec[hits] == spec[a]).sum()
        total += len(hits)
        if oracle:  # only possible on generated data, where the truth is known
            hits = hits[spec[hits] != spec[a]]
        out[a] = hits
    return out, false_negatives / max(total, 1)


def train(records, pairs, groups, seed, band=None, in_batch=True, oracle=False, n_mined=4, temperature=TEMPERATURE):
    """Pretrained encoder, in-batch softmax. Optional mined negatives per anchor, refreshed halfway through training."""
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    model = SentenceTransformer(MODEL, device=DEVICE)
    optimiser = torch.optim.AdamW(model.parameters(), lr=LR)
    text = records.text.values
    mined, false_share = None, []
    model.train()
    for step in range(STEPS):
        if band and step in (0, STEPS // 2):
            model.eval()
            mined, share = mine(model, records, pairs, groups, band, oracle)
            false_share.append(share)
            model.train()
        # one pair per known group in a batch, so no known match is used as a negative
        chosen, seen = [], set()
        for i in rng.permutation(len(pairs)):
            g = groups[pairs[i, 0]]
            if g not in seen:
                seen.add(g)
                chosen.append(i)
            if len(chosen) == BATCH:
                break
        batch = pairs[chosen]
        left, right = forward(model, text[batch[:, 0]]), forward(model, text[batch[:, 1]])
        logits = left @ right.T  # each left's positive is on the diagonal, the rest of the batch are negatives
        if band:
            extra = [mined.get(a, np.array([], int)) for a in batch[:, 0]]
            extra = [rng.permutation(e)[:n_mined] for e in extra]
            need = max((len(e) for e in extra), default=0)
            if need:
                flat = np.concatenate([e for e in extra if len(e)])
                vectors = forward(model, text[flat])
                offsets = np.cumsum([0] + [len(e) for e in extra])
                columns = torch.full((len(batch), need), -1e4, device=DEVICE)
                for row in range(len(batch)):
                    n = len(extra[row])
                    if n:
                        columns[row, :n] = (left[row:row + 1] @ vectors[offsets[row]:offsets[row + 1]].T)[0]
                logits = torch.cat([logits, columns], dim=1)
        if not in_batch:  # positives and mined negatives only
            keep = torch.zeros_like(logits, dtype=torch.bool)
            keep[:, len(batch):] = True
            keep[torch.arange(len(batch)), torch.arange(len(batch))] = True
            logits = logits.masked_fill(~keep, -1e4)
        loss = F.cross_entropy(logits / temperature, torch.arange(len(batch), device=DEVICE))
        optimiser.zero_grad()
        loss.backward()
        optimiser.step()
    model.eval()
    return model, np.mean(false_share) if false_share else float("nan")
