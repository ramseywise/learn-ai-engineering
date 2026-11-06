# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["torch", "torchvision", "pillow"]
# ///
"""A Vision Transformer written from Eq. 1-4 of Dosovitskiy et al. (arXiv:2010.11929), for notes/05b and 04b.

Run from this folder:
    uv run vit_from_paper.py

1. Builds ViT-B/16 from the equations with Table 1's sizes and checks its parameter count against torchvision's.
2. Trains a small ViT from scratch on the generated shapes (data/shapes/, made by vision_project.data).
3. Trains only a new linear head on torchvision's ImageNet ViT-B/16. The first run downloads its weights
   (about 330 MB) to the torch cache.
About 5 minutes on an M4 Pro (MPS).
"""
# %%
import time
from pathlib import Path

import torch
import torch.nn as nn
from torchvision.models import ViT_B_16_Weights, vit_b_16
from torchvision.transforms import v2

from vision_project.data import ShapesDataset, loaders, make_shapes
from vision_project.engine import device, fit
from vision_project.model import FrozenBackbone, count_trainable


class Block(nn.Module):
    """Eq. 2 and 3: pre-norm multi-head self-attention, then a two-layer GELU MLP, each with a residual."""

    def __init__(self, dim, heads, mlp_dim):
        super().__init__()
        self.ln1 = nn.LayerNorm(dim, eps=1e-6)
        self.attn = nn.MultiheadAttention(dim, heads, batch_first=True)
        self.ln2 = nn.LayerNorm(dim, eps=1e-6)
        self.mlp = nn.Sequential(nn.Linear(dim, mlp_dim), nn.GELU(), nn.Linear(mlp_dim, dim))

    def forward(self, z):
        h = self.ln1(z)
        z = z + self.attn(h, h, h, need_weights=False)[0]  # z'_l = MSA(LN(z_{l-1})) + z_{l-1}
        return z + self.mlp(self.ln2(z))                   # z_l  = MLP(LN(z'_l)) + z'_l


class ViT(nn.Module):
    def __init__(self, image=224, patch=16, channels=3, dim=768, depth=12, heads=12, mlp_dim=3072, n_classes=1000):
        super().__init__()
        n_patches = (image // patch) ** 2
        # Eq. 1, E in R^{(P^2 C) x D}: a conv whose kernel and stride are the patch size is that same linear map,
        # applied to every non-overlapping P x P patch.
        self.embed = nn.Conv2d(channels, dim, kernel_size=patch, stride=patch)
        self.cls = nn.Parameter(torch.zeros(1, 1, dim))                 # x_class
        self.pos = nn.Parameter(torch.randn(1, n_patches + 1, dim) * .02)  # E_pos in R^{(N+1) x D}
        self.blocks = nn.Sequential(*[Block(dim, heads, mlp_dim) for _ in range(depth)])
        self.ln = nn.LayerNorm(dim, eps=1e-6)
        self.head = nn.Linear(dim, n_classes)

    def forward(self, x):                                   # x: [B, C, H, W]
        z = self.embed(x).flatten(2).transpose(1, 2)        # [B, N, D]
        z = torch.cat([self.cls.expand(len(z), -1, -1), z], dim=1) + self.pos  # [B, N+1, D]
        z = self.blocks(z)
        return self.head(self.ln(z[:, 0]))                  # Eq. 4: y = LN(z_L^0), then the head


# %%
if __name__ == "__main__":
    # 1. Table 1, ViT-Base: 12 layers, D 768, MLP 3072, 12 heads, "86M" parameters.
    ours = count_trainable(ViT())
    theirs = ViT_B_16_Weights.IMAGENET1K_V1.meta["num_params"]
    print(f"ViT-B/16 from the equations: {ours:,} parameters; torchvision's: {theirs:,}; equal: {ours == theirs}")

    root = make_shapes(Path(__file__).parent / "data" / "shapes")
    dev = device()
    plain = v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True)])
    preset = ViT_B_16_Weights.IMAGENET1K_V1.transforms()  # resize 256, crop 224, ImageNet mean and std
    train_full = ShapesDataset(root, "train", plain)

    # 2. From scratch: a small ViT on 64x64 images, patch 8 gives 64 patches + 1 class token.
    torch.manual_seed(0)
    small = ViT(image=64, patch=8, dim=128, depth=6, heads=4, mlp_dim=256, n_classes=6)
    train_loader, test_loader = loaders(train_full, ShapesDataset(root, "test", plain))
    start = time.time()
    acc = fit(small, train_loader, test_loader, steps=2000, lr=3e-4, dev=dev, weight_decay=0.05)
    print(f"small ViT from scratch: {count_trainable(small):,} parameters, 3,000 images, 2,000 steps, "
          f"test accuracy {acc:.3f} ({time.time() - start:.0f} s)")

    # 3. Pretrained, frozen: the paper fine-tunes by replacing the head with a zero-initialised D x K layer.
    torch.manual_seed(0)
    pre = vit_b_16(weights=ViT_B_16_Weights.IMAGENET1K_V1)
    for p in pre.parameters():
        p.requires_grad = False
    pre.heads = nn.Linear(768, 6)
    nn.init.zeros_(pre.heads.weight)
    nn.init.zeros_(pre.heads.bias)
    frozen = FrozenBackbone(pre, head="heads")  # only the new head switches to train mode
    train_loader, test_loader = loaders(ShapesDataset(root, "train", preset), ShapesDataset(root, "test", preset))
    start = time.time()
    acc = fit(frozen, train_loader, test_loader, steps=500, lr=1e-3, dev=dev)
    print(f"ImageNet ViT-B/16, frozen, new head: {count_trainable(frozen):,} trainable parameters, 3,000 images, "
          f"500 steps, test accuracy {acc:.3f} ({time.time() - start:.0f} s)")
