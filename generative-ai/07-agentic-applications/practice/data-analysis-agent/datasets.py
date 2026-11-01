"""Load the course's real datasets from the data-analytics pillar. Nothing is synthesised here.

Paths are relative to the repo root. If the data moves, point DATA_AGENT_ROOT at a folder with
the same layout, or fix DATASETS below: the agent fails with a clear error instead of guessing.
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(os.environ.get("DATA_AGENT_ROOT", Path(__file__).resolve().parents[4]))
PILLAR = "data-analytics/01-python-for-data-analysis/practice"
DATASETS = {
    "tips": f"{PILLAR}/data/tips.csv",
    "titanic": f"{PILLAR}/mckinney/datasets/titanic/train.csv",
}


def load(name: str) -> pd.DataFrame:
    path = REPO_ROOT / DATASETS[name]
    if not path.is_file():
        raise FileNotFoundError(
            f"Dataset {name!r} not found at {path}. It may have moved: update DATASETS in datasets.py "
            "or set DATA_AGENT_ROOT."
        )
    return pd.read_csv(path)
