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
    _save(fig, "class-balance-by-time-step.svg")


def _save(fig, name: str) -> None:
    CHARTS.mkdir(parents=True, exist_ok=True)
    target = CHARTS / name
    fig.savefig(target, format="svg", facecolor=SURFACE, metadata={"Date": None})
    plt.close(fig)
    print(f"chart written to {target.relative_to(CHARTS.parents[1])}")


ARM_A = "#2a78d6"
ARM_B = "#eb6834"


def precision_at_k_a_b() -> None:
    ev = read_result("evaluation-arms-a-b")["data"]
    k = ev["k"]
    fig, (top, bottom) = plt.subplots(
        2, 1, figsize=(10, 6.4), gridspec_kw={"height_ratios": [3, 1.6], "hspace": 0.45}
    )
    fig.patch.set_facecolor(SURFACE)
    for arm, colour, label in (("A", ARM_A, "Arm A, local features"), ("B", ARM_B, "Arm B, plus graph features")):
        rows = [r for p in ("pre_shift_test", "post_shift_test") for r in ev["metrics"][arm][p]["per_step"]]
        top.plot([r["time_step"] for r in rows], [r["precision_at_k"] for r in rows], color=colour, linewidth=2,
                 marker="o", markersize=5, markeredgecolor=SURFACE, markeredgewidth=1.5, label=label)
    rows = [r for p in ("pre_shift_test", "post_shift_test") for r in ev["metrics"]["A"][p]["per_step"]]
    top.step([r["time_step"] for r in rows], [min(r["illicit"], k) / k for r in rows], where="mid", color=TEXT_SECONDARY,
             linewidth=1, linestyle=(0, (3, 2)), label="Best possible: fewer illicit labels than alerts")
    _frame(top)
    top.set_ylabel(f"Precision at k = {k}")
    top.set_ylim(0, 1.14)
    top.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    top.set_xticks(range(35, 50))
    top.set_xlim(34.5, 49.5)
    top.set_xlabel("Test time step")
    top.text(38.5, 1.12, "Pre-shift", ha="center", va="top", color=TEXT_SECONDARY, fontsize=8)
    top.text(46, 1.12, "Post-shift", ha="center", va="top", color=TEXT_SECONDARY, fontsize=8)
    top.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    fig.legend(loc="upper left", frameon=False, ncol=3, labelcolor=TEXT, bbox_to_anchor=(0.062, 0.93),
               handlelength=1.6, columnspacing=1.6)

    periods = (("pre_shift_test", "Pre-shift, steps 35 to 42"), ("post_shift_test", "Post-shift, steps 43 to 49"))
    for y, (period, label) in enumerate(periods):
        c = ev["comparisons_b_minus_a"][period]["p_at_k"]
        lo, hi = c["interval_95"]["low"], c["interval_95"]["high"]
        bottom.plot([lo, hi], [y, y], color=TEXT_SECONDARY, linewidth=2, solid_capstyle="round")
        bottom.plot([c["difference"]], [y], marker="o", markersize=8, color=TEXT, markeredgecolor=SURFACE, markeredgewidth=2)
        bottom.text(lo, y - 0.38, f"{c['difference'] * 100:+.1f} pts ({lo * 100:+.1f} to {hi * 100:+.1f}), {c['verdict']}",
                    va="center", ha="left", color=TEXT_SECONDARY, fontsize=8)
    bottom.axvline(0, color=TEXT, linewidth=1)
    bottom.set_yticks([0, 1])
    bottom.set_yticklabels([p[1] for p in periods])
    bottom.set_ylim(-0.8, 1.5)
    bottom.invert_yaxis()
    bottom.set_facecolor(SURFACE)
    bottom.grid(axis="x", color=GRID, linewidth=0.8)
    for side in ("top", "right", "left"):
        bottom.spines[side].set_visible(False)
    bottom.tick_params(length=0)
    bottom.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v * 100:+.0f} pts" if v else "0"))
    bottom.set_xlabel("Arm B minus Arm A, precision at k pooled over the period, with 95% bootstrap interval")
    span = max(abs(v) for p, _ in periods for v in ev["comparisons_b_minus_a"][p]["p_at_k"]["interval_95"].values()
               if isinstance(v, float))
    bottom.set_xlim(-span * 1.0, span * 2.3)

    fig.suptitle("Precision at k by test step, Arms A and B", x=0.07, y=0.985, ha="left", fontsize=13, color=TEXT,
                 fontweight="bold")
    fig.text(0.07, 0.935, f"Top {k} labelled transactions per step, scores averaged over five seeds.", ha="left",
             color=TEXT_SECONDARY, fontsize=9)
    fig.text(0.07, 0.015, "Labelled transactions only; unlabelled is not licit. One dataset, one regime shift. "
             "Cryptocurrency data, not payments data.\nSource: results/evaluation-arms-a-b.json.",
             ha="left", va="bottom", color=TEXT_SECONDARY, fontsize=7.5)
    fig.subplots_adjust(left=0.2, right=0.985, top=0.86, bottom=0.14)
    _save(fig, "precision-at-k-arms-a-b.svg")


ARM_D = "#1baf7a"
ARMS = (("A", ARM_A, "Arm A, local features"), ("B", ARM_B, "Arm B, plus graph features"),
        ("D", ARM_D, "Arm D, GraphSAGE"))


def _diff_panel(ax, comparisons: list[tuple[str, dict]]) -> None:
    lows = [c["interval_95"]["low"] for _, c in comparisons]
    highs = [c["interval_95"]["high"] for _, c in comparisons]
    left, right = min(min(lows), 0.0), max(max(highs), 0.0)
    width = (right - left) or 0.01
    for y, (label, c) in enumerate(comparisons):
        lo, hi = c["interval_95"]["low"], c["interval_95"]["high"]
        ax.plot([lo, hi], [y, y], color=TEXT_SECONDARY, linewidth=2, solid_capstyle="round")
        ax.plot([c["difference"]], [y], marker="o", markersize=8, color=TEXT, markeredgecolor=SURFACE, markeredgewidth=2)
        ax.text(right + 0.06 * width, y, f"{c['difference'] * 100:+.1f} pts ({lo * 100:+.1f} to {hi * 100:+.1f}), {c['verdict']}",
                va="center", ha="left", color=TEXT_SECONDARY, fontsize=8)
    ax.axvline(0, color=TEXT, linewidth=1)
    ax.set_yticks(range(len(comparisons)))
    ax.set_yticklabels([label for label, _ in comparisons])
    ax.set_ylim(-0.6, len(comparisons) - 0.4)
    ax.invert_yaxis()
    ax.set_facecolor(SURFACE)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v * 100:+.0f} pts" if v else "0"))
    ax.set_xlim(left - 0.1 * width, right + 1.5 * width)


def precision_at_k_all_arms() -> None:
    ev = read_result("evaluation-phase-3")["data"]
    k = ev["k"]
    fig, (top, bottom) = plt.subplots(
        2, 1, figsize=(10, 7.2), gridspec_kw={"height_ratios": [3, 2], "hspace": 0.45}
    )
    fig.patch.set_facecolor(SURFACE)
    periods = ("pre_shift_test", "post_shift_test")
    for arm, colour, label in ARMS:
        rows = [r for p in periods for r in ev["metrics"][arm][p]["per_step"]]
        top.plot([r["time_step"] for r in rows], [r["precision_at_k"] for r in rows], color=colour, linewidth=2,
                 marker="o", markersize=5, markeredgecolor=SURFACE, markeredgewidth=1.5, label=label)
    rows = [r for p in periods for r in ev["metrics"]["A"][p]["per_step"]]
    top.step([r["time_step"] for r in rows], [min(r["illicit"], k) / k for r in rows], where="mid", color=TEXT_SECONDARY,
             linewidth=1, linestyle=(0, (3, 2)), label="Best possible")
    _frame(top)
    top.set_ylabel(f"Precision at k = {k}")
    top.set_ylim(0, 1.14)
    top.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    top.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    top.set_xticks(range(35, 50))
    top.set_xlim(34.5, 49.5)
    top.set_xlabel("Test time step")
    top.text(38.5, 1.12, "Pre-shift", ha="center", va="top", color=TEXT_SECONDARY, fontsize=8)
    top.text(46, 1.12, "Post-shift", ha="center", va="top", color=TEXT_SECONDARY, fontsize=8)
    fig.legend(loc="upper left", frameon=False, ncol=4, labelcolor=TEXT, bbox_to_anchor=(0.062, 0.935),
               handlelength=1.6, columnspacing=1.4)
    pre = "pre_shift_test"
    _diff_panel(bottom, [(f"{pair}, pre-shift", ev["comparisons"][pair][pre]["p_at_k"])
                         for pair in ("B minus A", "D minus B", "D minus A")])
    bottom.set_xlabel("Difference in precision at k pooled over steps 35 to 42, with 95% bootstrap interval")
    fig.suptitle("Precision at k by test step, all arms", x=0.07, y=0.985, ha="left", fontsize=13, color=TEXT,
                 fontweight="bold")
    fig.text(0.07, 0.945, f"Top {k} labelled transactions per step, scores averaged over five seeds. "
             "Dashed: the best any ranking could do.", ha="left", color=TEXT_SECONDARY, fontsize=8.5)
    fig.text(0.07, 0.012, "Labelled transactions only; unlabelled is not licit. One dataset, one regime shift. "
             "Cryptocurrency data, not payments data.\nSource: results/evaluation-phase-3.json.",
             ha="left", va="bottom", color=TEXT_SECONDARY, fontsize=7.5)
    fig.subplots_adjust(left=0.16, right=0.985, top=0.87, bottom=0.12)
    _save(fig, "precision-at-k-all-arms.svg")


def label_budget_curve() -> None:
    lb = read_result("label-budget-curve")["data"]
    k = lb["k"]
    budgets = lb["budgets_percent"]
    pre = "pre_shift_test"
    fig, ax = plt.subplots(figsize=(10, 5.6))
    fig.patch.set_facecolor(SURFACE)
    for arm, colour, label in ARMS:
        points = [lb["curve"][f"{b:03d}"][pre][arm] for b in budgets]
        y = [p["precision_at_k_pooled"] for p in points]
        ax.fill_between(budgets, [p["interval_95"]["low"] for p in points], [p["interval_95"]["high"] for p in points],
                        color=colour, alpha=0.15, linewidth=0)
        ax.plot(budgets, y, color=colour, linewidth=2, marker="o", markersize=6, markeredgecolor=SURFACE,
                markeredgewidth=1.5, label=label)
        ax.text(budgets[-1] * 1.06, y[-1], label.split(",")[0], va="center", ha="left", color=TEXT, fontsize=8.5)
    ax.set_xscale("log")
    ax.set_xticks(budgets)
    ax.set_xticklabels([f"{b}%" for b in budgets])
    ax.minorticks_off()
    ax.set_xlim(budgets[0] * 0.85, budgets[-1] * 1.45)
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel(f"Precision at k = {k}, pre-shift")
    ax.set_xlabel("Share of training labels used")
    fig.legend(loc="upper left", frameon=False, ncol=3, labelcolor=TEXT, bbox_to_anchor=(0.062, 0.915),
               handlelength=1.6, columnspacing=1.6)
    fig.suptitle("Label-budget curve: precision at k as training labels shrink", x=0.07, y=0.985, ha="left",
                 fontsize=13, color=TEXT, fontweight="bold")
    fig.text(0.07, 0.925, "Pooled over steps 35 to 42. Bands are 95% bootstrap intervals. Full protocol re-run at every budget.",
             ha="left", color=TEXT_SECONDARY, fontsize=8.5)
    fig.text(0.07, 0.015, "Overlapping bands do not settle a comparison: arms are compared on paired resamples (H4 in the README). "
             "Validation labels kept in full at every budget,\nso small budgets are somewhat optimistic. "
             "Cryptocurrency data, not payments data. Source: results/label-budget-curve.json.",
             ha="left", va="bottom", color=TEXT_SECONDARY, fontsize=7.5)
    fig.subplots_adjust(left=0.08, right=0.985, top=0.82, bottom=0.17)
    _save(fig, "label-budget-curve.svg")


if __name__ == "__main__":
    from paths import RESULTS

    class_balance()
    if (RESULTS / "evaluation-arms-a-b.json").is_file():
        precision_at_k_a_b()
    if (RESULTS / "evaluation-phase-3.json").is_file():
        precision_at_k_all_arms()
    if (RESULTS / "label-budget-curve.json").is_file():
        label_budget_curve()
