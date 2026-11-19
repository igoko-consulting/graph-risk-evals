import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter

from paths import CHARTS
from protocol import PERIODS
from results_io import read_result

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e6e5e0"
LICIT = "#2a78d6"
ILLICIT = "#eb6834"
UNKNOWN = "#d6d5ce"

PERIOD_LABELS = {
    "training": "Training",
    "validation": "Validation",
    "pre_shift_test": "Test, pre-shift",
    "post_shift_test": "Test, post-shift",
}

# Bundled font and fixed hash salt so the SVG is byte-identical on every machine.
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "svg.fonttype": "path",
    "svg.hashsalt": "graph-risk-evals",
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT_SECONDARY,
    "xtick.color": TEXT_SECONDARY,
    "ytick.color": TEXT_SECONDARY,
    "font.size": 9,
})


def _frame(ax) -> None:
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    for first, last in list(PERIODS.values())[1:]:
        ax.axvline(first - 0.5, color=TEXT_SECONDARY, linewidth=0.8, linestyle=(0, (2, 2)))


def class_balance() -> None:
    rows = read_result("class-balance-by-time-step")["data"]["by_time_step"]
    steps = [r["time_step"] for r in rows]
    illicit = [r["illicit"] for r in rows]
    licit = [r["licit"] for r in rows]
    unknown = [r["unknown"] for r in rows]
    share = [r["illicit_share_of_labelled"] for r in rows]
    total = sum(r["nodes"] for r in rows)

    fig, (top, bottom) = plt.subplots(
        2, 1, figsize=(10, 6.4), sharex=True, gridspec_kw={"height_ratios": [3, 2], "hspace": 0.18}
    )
    fig.patch.set_facecolor(SURFACE)
    bar = {"width": 0.8, "edgecolor": SURFACE, "linewidth": 1}
    top.bar(steps, illicit, color=ILLICIT, label="Illicit", **bar)
    top.bar(steps, licit, bottom=illicit, color=LICIT, label="Licit", **bar)
    top.bar(steps, unknown, bottom=[a + b for a, b in zip(illicit, licit)], color=UNKNOWN, label="Unlabelled", **bar)
    _frame(top)
    top.set_ylabel("Transactions")
    top.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    fig.legend(loc="upper left", frameon=False, ncol=3, labelcolor=TEXT, bbox_to_anchor=(0.062, 0.93),
               handlelength=1.2, columnspacing=1.2)
    ymax = top.get_ylim()[1] * 1.12
    top.set_ylim(0, ymax)
    for name, (first, last) in PERIODS.items():
        top.text((first + last) / 2, ymax * 0.97, PERIOD_LABELS[name], ha="center", va="top",
                 color=TEXT_SECONDARY, fontsize=8)

    bottom.bar(steps, share, color=ILLICIT, **bar)
    _frame(bottom)
    bottom.set_ylabel("Illicit share of labelled")
    bottom.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    bottom.set_xlabel("Time step")
    bottom.set_xlim(0.4, max(steps) + 0.6)
    bottom.set_xticks([1, 5, 10, 15, 20, 25, 30, 35, 40, 43, 45, 49])

    fig.suptitle("Class balance by time step", x=0.07, y=0.985, ha="left", fontsize=13, color=TEXT, fontweight="bold")
    fig.text(0.07, 0.935, f"Elliptic Data Set: {total:,} Bitcoin transactions over {len(steps)} time steps. "
             "Share is over labelled transactions only.", ha="left", color=TEXT_SECONDARY, fontsize=9)
    fig.text(0.07, 0.015, "Shows labels only. It does not show model performance, unlabelled transactions are not licit, "
             "and this is cryptocurrency data, not payments data.\nSource: results/class-balance-by-time-step.json. "
             "Data licence CC BY-NC-ND 4.0.", ha="left", va="bottom", color=TEXT_SECONDARY, fontsize=7.5)
    fig.subplots_adjust(left=0.07, right=0.985, top=0.86, bottom=0.14)

    CHARTS.mkdir(parents=True, exist_ok=True)
    target = CHARTS / "class-balance-by-time-step.svg"
    fig.savefig(target, format="svg", facecolor=SURFACE, metadata={"Date": None})
    plt.close(fig)
    print(f"chart written to {target.relative_to(CHARTS.parents[1])}")


if __name__ == "__main__":
    class_balance()
