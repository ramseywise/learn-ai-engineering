# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["torch", "torchvision", "pillow", "matplotlib"]
# ///
"""Measured grid for notes/04b: training from scratch vs a frozen pretrained backbone vs fine-tuning it all.

Run from this folder:
    uv run vision_transfer.py            # 3 seeds, about 13 minutes on an idle M4 Pro (MPS)
    uv run vision_transfer.py --seeds 1  # one seed, about 5; longer if the GPU is shared

Generates 6 classes of shapes (500 train / 100 test images per class, 64x64) into data/shapes/, then trains
each arm on 1%, 10% and 100% of the training images and scores it on the
full 600-image test set. Budgets are matched on wall-clock time, not steps: the scratch CNN gets 2,000
steps (it is still at chance after 500 on the full set), the ResNet-18 arms 500, about half a minute each. The first run downloads the ResNet-18 ImageNet weights (about 45 MB) to the torch cache.
Two extra rows at 10% isolate one choice each: BatchNorm left in train mode inside a frozen backbone,
and rotation/flip augmentation for the scratch model. Writes dl-vision-transfer.png.
"""
# %%
import argparse
import statistics
import time
from pathlib import Path

import torch
from torchvision.transforms import v2

import chartstyle as cs
import matplotlib.pyplot as plt
from vision_project.data import ShapesDataset, fraction, loaders, make_shapes
from vision_project.engine import device, fit
from vision_project.model import SmallCNN, count_trainable, pretrained_resnet18

FRACTIONS = [0.01, 0.10, 1.00]
IMAGENET = dict(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

plain = v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True)])
# The weights' own preset (ResNet18_Weights.IMAGENET1K_V1.transforms()) resizes to 256 and crops 224.
# We resize 64 -> 112 instead: same normalisation, a quarter of the pixels, so the grid runs in minutes.
pretrained = v2.Compose([v2.ToImage(), v2.Resize(112, antialias=True),
                         v2.ToDtype(torch.float32, scale=True), v2.Normalize(**IMAGENET)])
# Shapes keep their label under any rotation or flip, so these are safe augmentations here.
augmented = v2.Compose([v2.ToImage(), v2.RandomHorizontalFlip(), v2.RandomVerticalFlip(),
                        v2.RandomRotation(180), v2.ToDtype(torch.float32, scale=True)])

ARMS = {  # name: (build model, train transform, test transform, learning rate, optimiser steps)
    "scratch": (lambda: SmallCNN(6), plain, plain, 1e-3, 2000),
    "frozen": (lambda: pretrained_resnet18(6, freeze=True), pretrained, pretrained, 1e-3, 500),
    "fine-tune": (lambda: pretrained_resnet18(6, freeze=False), pretrained, pretrained, 3e-4, 500),
}
EXTRAS = {  # run at 10% only
    "frozen, BN in train mode": (lambda: pretrained_resnet18(6, freeze=True, bn_eval=False), pretrained, pretrained,
                                 1e-3, 500),
    "scratch + augmentation": (lambda: SmallCNN(6), augmented, plain, 1e-3, 2000),
}


def run(arm, share, seed, root, dev):
    build, train_tf, test_tf, lr, steps = arm
    torch.manual_seed(seed)
    model = build()
    train_set = fraction(ShapesDataset(root, "train", train_tf), share, seed)
    train_loader, test_loader = loaders(train_set, ShapesDataset(root, "test", test_tf), seed=seed)
    return fit(model, train_loader, test_loader, steps, lr, dev), len(train_set), count_trainable(model)


# %%
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=3)
    args = parser.parse_args()
    root = make_shapes(Path(__file__).parent / "data" / "shapes")
    dev = device()
    print(f"device {dev}, seeds 0..{args.seeds - 1}")

    results = {}
    jobs = [(name, arm, share) for name, arm in ARMS.items() for share in FRACTIONS]
    jobs += [(name, arm, 0.10) for name, arm in EXTRAS.items()]
    for name, arm, share in jobs:
        start = time.time()
        runs = [run(arm, share, seed, root, dev) for seed in range(args.seeds)]
        accs = [acc for acc, _, _ in runs]
        results[name, share] = accs
        _, n_train, n_trainable = runs[0]
        print(f"{name:26s} {share:>5.0%} steps={arm[4]} n={n_train:5d} trainable={n_trainable:>10,d} "
              f"acc mean {statistics.mean(accs):.3f} min {min(accs):.3f} max {max(accs):.3f} "
              f"({time.time() - start:.0f} s)", flush=True)

    cs.apply()
    fig, ax = plt.subplots()
    for (name, colour) in zip(ARMS, cs.CATEGORICAL):
        accs = [results[name, s] for s in FRACTIONS]
        means = [statistics.mean(a) for a in accs]
        low = [m - min(a) for m, a in zip(means, accs)]
        high = [max(a) - m for m, a in zip(means, accs)]
        ax.errorbar([s * 100 for s in FRACTIONS], means, yerr=[low, high], color=colour, marker="o", ms=6,
                    capsize=3, label=name)
    ax.axhline(1 / 6, color="grey", ls=":", lw=1)
    ax.text(1.6, 1 / 6 + 0.03, "chance (1 in 6)", color="grey", fontsize=9)
    ax.set_xscale("log")
    ax.set_xticks([1, 10, 100], ["1%\n(30 images)", "10%\n(300)", "100%\n(3,000)"])
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Share of the training set")
    ax.set_ylabel("Test accuracy (600 images)")
    ax.set_title("Scratch draws level with frozen features only at 3,000 images")
    ax.legend(loc="lower right")
    cs.save(fig, "dl-vision-transfer.png")
