"""Generated shapes on cluttered backgrounds, written to an image-folder tree, and the Dataset that reads it back.

The folder layout is the one most real image sets use: root/split/class/image.png.
"""
import math
import random
from pathlib import Path

import torch
from PIL import Image, ImageDraw, ImageFilter
from torch.utils.data import DataLoader, Dataset, Subset

CLASSES = ["circle", "cross", "ring", "square", "star", "triangle"]
SIZE = 64


def _polygon(cx, cy, r, sides, turn, star=False):
    points = []
    count = sides * 2 if star else sides
    for i in range(count):
        radius = r if not star or i % 2 == 0 else r * 0.45
        angle = turn + 2 * math.pi * i / count
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return points


def draw(label, rng):
    """One 64x64 RGB image of `label`, with colour, size, position, rotation and clutter all random."""
    background = tuple(rng.randint(0, 255) for _ in range(3))
    img = Image.new("RGB", (SIZE, SIZE), background)
    d = ImageDraw.Draw(img)
    for _ in range(rng.randint(2, 6)):  # clutter: lines that are not the shape
        d.line([tuple(rng.uniform(0, SIZE) for _ in range(2)) for _ in range(2)],
               fill=tuple(rng.randint(0, 255) for _ in range(3)), width=rng.randint(1, 3))
    colour = tuple(rng.randint(0, 255) for _ in range(3))
    r = rng.uniform(10, 22)
    cx, cy = rng.uniform(r, SIZE - r), rng.uniform(r, SIZE - r)
    turn = rng.uniform(0, 2 * math.pi)
    if label == "circle":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour)
    elif label == "ring":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=colour, width=max(2, int(r / 4)))
    elif label == "square":
        d.polygon(_polygon(cx, cy, r, 4, turn), fill=colour)
    elif label == "triangle":
        d.polygon(_polygon(cx, cy, r, 3, turn), fill=colour)
    elif label == "star":
        d.polygon(_polygon(cx, cy, r, 5, turn, star=True), fill=colour)
    elif label == "cross":
        w = r / 3
        for a in (turn, turn + math.pi / 2):
            dx, dy = math.cos(a), math.sin(a)
            px, py = -dy * w, dx * w
            d.polygon([(cx - dx * r + px, cy - dy * r + py), (cx + dx * r + px, cy + dy * r + py),
                       (cx + dx * r - px, cy + dy * r - py), (cx - dx * r - px, cy - dy * r - py)], fill=colour)
    return img.filter(ImageFilter.GaussianBlur(rng.uniform(0, 1.0)))


def make_shapes(root, train_per_class=500, test_per_class=100, seed=0):
    """Write root/{train,test}/<class>/<n>.png once. Returns root. A second call with the same arguments is a no-op."""
    root = Path(root)
    stamp = root / f".done-{train_per_class}-{test_per_class}-{seed}"
    if stamp.exists():
        return root
    rng = random.Random(seed)
    for split, n in (("train", train_per_class), ("test", test_per_class)):
        for label in CLASSES:
            folder = root / split / label
            folder.mkdir(parents=True, exist_ok=True)
            for i in range(n):
                draw(label, rng).save(folder / f"{i:04d}.png")
    stamp.touch()
    return root


class ShapesDataset(Dataset):
    """Reads root/split/<class>/*.png. Returns (image tensor, class index) after `transform`."""

    def __init__(self, root, split, transform=None):
        self.paths = sorted(Path(root, split).glob("*/*.png"))
        self.classes = sorted({p.parent.name for p in self.paths})
        self.class_to_idx = {c: i for i, c in enumerate(self.classes)}
        self.targets = [self.class_to_idx[p.parent.name] for p in self.paths]
        self.transform = transform

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, i):
        img = Image.open(self.paths[i]).convert("RGB")
        return (self.transform(img) if self.transform else img), self.targets[i]


def fraction(dataset, share, seed):
    """A class-balanced subset holding `share` of each class, at least one image per class."""
    g = torch.Generator().manual_seed(seed)
    keep = []
    targets = torch.tensor(dataset.targets)
    for c in range(len(dataset.classes)):
        idx = torch.nonzero(targets == c).flatten()
        n = max(1, round(share * len(idx)))
        keep += idx[torch.randperm(len(idx), generator=g)[:n]].tolist()
    return Subset(dataset, sorted(keep))


def loaders(train_set, test_set, batch_size=32, seed=0):
    g = torch.Generator().manual_seed(seed)
    return (DataLoader(train_set, batch_size=batch_size, shuffle=True, generator=g),
            DataLoader(test_set, batch_size=256))
