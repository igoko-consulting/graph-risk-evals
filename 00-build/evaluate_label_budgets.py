import numpy as np

from evaluate_arms import TEST_PERIODS, interval, period_metrics, step_index
from evaluate_phase3 import draws, named_verdict
from features import BUDGETS
from paths import RUNS
from protocol import require, require_k_first
from results_io import write_result

ARMS = ("A", "B", "D")


def label(fraction: float) -> str:
    return f"{int(round(fraction * 100)):03d}"


def load_scores() -> tuple[dict, np.ndarray, np.ndarray]:
    main = np.load(RUNS / "scores.npz")
    main_d = np.load(RUNS / "scores-d.npz")
    scores = {}
    for fraction in BUDGETS:
        if fraction == 1.0:
            run = {"A": main["A"], "B": main["B"], "D": main_d["D"]}
        else:
            budget = np.load(RUNS / f"scores-budget-{label(fraction)}.npz")
            require(np.array_equal(budget["node_ids"], main["node_ids"]), "label-budget scores cover different nodes from the main run")
            run = {arm: budget[arm] for arm in ARMS}
        for arm in ARMS:
            scores[(label(fraction), arm)] = run[arm].mean(axis=0)
    return scores, main["steps"], main["labels"]


def main() -> None:
    k = require_k_first()["data"]["k"]
    scores, steps, labels = load_scores()
    labelled, positives = labels != -1, labels == 1
    indexes = {p: step_index(steps, labelled, p) for p in TEST_PERIODS}
    keyed = {f"{b}/{a}": s for (b, a), s in scores.items()}
    d = draws(keyed, positives, indexes, k, stats=("p_at_k",))

    curve = {}
    for fraction in BUDGETS:
        b = label(fraction)
        curve[b] = {}
        for period in TEST_PERIODS:
            curve[b][period] = {}
            for arm in ARMS:
                m = period_metrics(scores[(b, arm)], positives, indexes[period], k)
                curve[b][period][arm] = {"precision_at_k_pooled": m["precision_at_k_pooled"],
                                         "interval_95": interval(d[period][f"{b}/{arm}"]["p_at_k"])}
            for hi in ("B", "D"):
                diff = d[period][f"{b}/{hi}"]["p_at_k"] - d[period][f"{b}/A"]["p_at_k"]
                ci = interval(diff)
                curve[b][period][f"{hi} minus A"] = {
                    "difference": curve[b][period][hi]["precision_at_k_pooled"] - curve[b][period]["A"]["precision_at_k_pooled"],
                    "interval_95": ci, "verdict": named_verdict(ci, hi, "A")}

    smallest, full = label(BUDGETS[0]), label(BUDGETS[-1])
    h4 = {}
    for hi in ("B", "D"):
        pre = "pre_shift_test"
        gap = lambda b: d[pre][f"{b}/{hi}"]["p_at_k"] - d[pre][f"{b}/A"]["p_at_k"]
        ci = interval(gap(smallest) - gap(full))
        point = curve[smallest][pre][f"{hi} minus A"]["difference"] - curve[full][pre][f"{hi} minus A"]["difference"]
        outcome = ("supported" if ci["low"] > 0 else "contradicted" if ci["high"] < 0 else "not separable")
        h4[f"{hi} minus A"] = {"widening": point, "interval_95": ci, "outcome": outcome}
    write_result("label-budget-curve", {
        "k": k,
        "budgets_percent": [int(round(f * 100)) for f in BUDGETS],
        "metric": "Precision at k pooled over the period, from seed-averaged scores, on labelled nodes",
        "bootstrap": "Same resamples as results/evaluation-phase-3.json",
        "curve": curve,
        "H4": {
            "definition": f"(B - A at {int(BUDGETS[0] * 100)}%) - (B - A at 100%), pre-shift precision at k. Supported if the 95% interval lies wholly above zero.",
            "B minus A": h4["B minus A"],
            "D minus A, reported alongside": h4["D minus A"],
            "outcome": h4["B minus A"]["outcome"],
        },
    }, uses_model_features=True)
    print(f"H4: {h4['B minus A']['outcome']} (widening {h4['B minus A']['widening']:+.3f})")


if __name__ == "__main__":
    main()
