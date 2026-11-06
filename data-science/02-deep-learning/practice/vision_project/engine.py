"""train_step and test_step: chapter 01's loop, cut into the two functions every experiment reuses."""
import itertools

import torch


def device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def train_step(model, batch, loss_fn, optimiser, dev):
    model.train()
    x, y = (t.to(dev) for t in batch)
    loss = loss_fn(model(x), y)
    optimiser.zero_grad()
    loss.backward()
    optimiser.step()
    return loss.item()


@torch.no_grad()
def test_step(model, loader, dev):
    model.eval()
    correct = total = 0
    for x, y in loader:
        x, y = x.to(dev), y.to(dev)
        correct += (model(x).argmax(1) == y).sum().item()
        total += len(y)
    return correct / total


def fit(model, train_loader, test_loader, steps, lr, dev, weight_decay=0.0):
    """Train for a fixed number of optimiser steps, cycling the loader, so every data fraction gets the same budget."""
    model.to(dev)
    params = [p for p in model.parameters() if p.requires_grad]
    optimiser = torch.optim.AdamW(params, lr=lr, weight_decay=weight_decay)
    loss_fn = torch.nn.CrossEntropyLoss()
    batches = itertools.chain.from_iterable(itertools.repeat(train_loader))
    for _, batch in zip(range(steps), batches):
        train_step(model, batch, loss_fn, optimiser, dev)
    return test_step(model, test_loader, dev)
