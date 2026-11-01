"""House style for this pillar's matplotlib charts. Chapter 2 walks through why each line is here."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

IMAGES = Path(__file__).resolve().parents[2] / "sources" / "images"

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
CATEGORICAL = [BLUE, ORANGE, AQUA, YELLOW]        # fixed order, validated, never cycled
CHANNEL_COLOUR = {"paid_social": BLUE, "organic": ORANGE, "email": AQUA, "referral": YELLOW}
INK, SECONDARY, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE, SURFACE = "#e1e0d9", "#c3c2b7", "#fcfcfb"
SEQUENTIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def apply():
    """Set the defaults once, so that no chart has to repeat them."""
    plt.rcParams.update({
        "figure.figsize": (8, 4.5), "figure.dpi": 150, "savefig.dpi": 150,
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "font.family": "sans-serif", "font.size": 10,
        "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
        "text.color": INK, "axes.labelcolor": SECONDARY, "axes.titlecolor": INK,
        "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "axes.edgecolor": BASELINE, "axes.grid": True, "axes.grid.axis": "y",
        "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": .7, "grid.linestyle": "-",
        "xtick.color": SECONDARY, "ytick.color": SECONDARY, "ytick.major.size": 0,
        "lines.linewidth": 2, "legend.frameon": False, "figure.constrained_layout.use": True,
        "axes.prop_cycle": plt.cycler(color=CATEGORICAL),
    })


def year_ticks(ax):
    """One x tick per January, labelled with the year, so date labels cannot collide."""
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


def save(fig, name):
    """Write a chart into the subject's shared image folder and report the file."""
    IMAGES.mkdir(parents=True, exist_ok=True)
    path = IMAGES / name
    fig.savefig(path)
    plt.close(fig)
    print(f"saved {path.name} ({path.stat().st_size // 1024} KB)")
