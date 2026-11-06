"""The two model families the chapter compares: a small CNN trained from scratch, and a pretrained ResNet-18."""
import torch.nn as nn
from torchvision.models import ResNet18_Weights, resnet18


class SmallCNN(nn.Module):
    """Two conv blocks and a linear head, in the shape of chapter 04's CNN, for 3x64x64 input."""

    def __init__(self, n_classes, width=32):
        super().__init__()

        def block(c_in, c_out):
            return nn.Sequential(
                nn.Conv2d(c_in, c_out, 3, padding=1), nn.BatchNorm2d(c_out), nn.ReLU(),
                nn.Conv2d(c_out, c_out, 3, padding=1), nn.BatchNorm2d(c_out), nn.ReLU(),
                nn.MaxPool2d(2))

        self.features = nn.Sequential(block(3, width), block(width, 2 * width), block(2 * width, 4 * width))
        self.head = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(4 * width, n_classes))

    def forward(self, x):
        return self.head(self.features(x))


def pretrained_resnet18(n_classes, freeze, bn_eval=True):
    """ImageNet ResNet-18 with its 1000-way `fc` replaced by an `n_classes` head.

    freeze=True trains the new head only (feature extraction); freeze=False trains every layer (fine-tuning).
    bn_eval=True keeps a frozen backbone's BatchNorm layers in eval mode during training, so their running
    statistics stay the ImageNet ones. requires_grad=False stops the weights moving, not the running statistics.
    """
    model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
    if freeze:
        for p in model.parameters():
            p.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, n_classes)  # new layer: requires_grad is True
    if freeze and bn_eval:
        return FrozenBackbone(model)
    return model


class FrozenBackbone(nn.Module):
    """Wraps a frozen model so .train() only switches the head; every other layer stays in eval mode."""

    def __init__(self, model, head="fc"):
        super().__init__()
        self.model = model
        self.head = head

    def train(self, mode=True):
        super().train(mode)
        self.model.eval()
        getattr(self.model, self.head).train(mode)
        return self

    def forward(self, x):
        return self.model(x)


def count_trainable(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
