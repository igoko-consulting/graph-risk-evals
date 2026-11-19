import numpy as np

from evaluate_arms import (BOOTSTRAP_SEED, RESAMPLES, TEST_PERIODS, ap, interval, period_metrics, pr_curve,
                           queue_curve, step_index, tp_at, unlabelled_share, verdict)
from paths import RUNS
from protocol import require_k_first
from results_io import read_result, write_result

ANALYST_COST = {"central": 25.0, "low": 12.5, "high": 37.5}
EURO_PER_VCPU_HOUR = 0.05
H2_MARGIN = 0.05
H1_THRESHOLD = 0.5
ARMS = ("A", "B", "D")


def draws(arms: dict, positives, indexes: dict, k: int, stats=("p_at_k", "ap_pooled", "ap_mean")) -> dict:
    """Same generator, seed and draw order as evaluate_arms.bootstrap, so resamples match Phase 2 exactly."""
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    out = {p: {a: {s: np.empty(RESAMPLES) for s in stats} for a in arms} for p in indexes}
    for r in range(RESAMPLES):
        for period, index in indexes.items():
            sampled = {s: rng.choice(idx, size=len(idx), replace=True) for s, idx in index.items()}
            pooled = np.concatenate(list(sampled.values())) if "ap_pooled" in stats else None
            for name, scores in arms.items():
                d = out[period][name]
                if "p_at_k" in stats:
                    d["p_at_k"][r] = sum(tp_at(scores[i], positives[i], k) for i in sampled.values()) / (k * len(sampled))
                if "ap_pooled" in stats:
                    v = ap(positives[pooled], scores[pooled])
                    d["ap_pooled"][r] = np.nan if v is None else v
                if "ap_mean" in stats:
                    aps = [ap(positives[i], scores[i]) for i in sampled.values()]
                    aps = [a for a in aps if a is not None]
                    d["ap_mean"][r] = np.mean(aps) if aps else np.nan
    return out


def named_verdict(ci: dict, hi: str, lo: str) -> str:
    return verdict(ci).replace("B higher", f"{hi} higher").replace("A higher", f"{lo} higher")


def comparison(point_a: float, point_b: float, draws_a, draws_b, hi: str, lo: str) -> dict:
    ci = interval(np.asarray(draws_b) - np.asarray(draws_a))
    return {"difference": point_b - point_a, "interval_95": ci, "verdict": named_verdict(ci, hi, lo)}


def h1(metrics: dict, d: dict) -> dict:
    def ratio(a, b, dd):
        best = max(b, dd)
        return (b - a) / (best - a) if best > a else np.nan
    m = {arm: metrics[arm]["pre_shift_test"]["average_precision_pooled"] for arm in ARMS}
    point = ratio(m["A"], m["B"], m["D"])
    pre = d["pre_shift_test"]
    per = np.array([ratio(pre["A"]["ap_pooled"][r], pre["B"]["ap_pooled"][r], pre["D"]["ap_pooled"][r])
                    for r in range(RESAMPLES)])
    if np.isnan(point):
        outcome = "undefined: neither B nor D beats A"
        ci = None
    else:
        ci = interval(per)
        outcome = ("supported" if ci["low"] >= H1_THRESHOLD else
                   "rejected" if ci["high"] < H1_THRESHOLD else "not separable from the 0.5 threshold")
    return {"definition": "(B - A) / (max(B, D) - A), PR-AUC pooled over the pre-shift period", "point": point,
            "interval_95": ci, "resamples_undefined": int(np.isnan(per).sum()), "outcome": outcome}


def h2(comp_d_b: dict) -> dict:
    rejected = comp_d_b["difference"] >= H2_MARGIN and comp_d_b["interval_95"]["low"] > 0
    return {"definition": "Rejected only if D - B, precision at k pooled pre-shift, is at least 5 points and its 95% interval excludes zero",
            "difference": comp_d_b["difference"], "interval_95": comp_d_b["interval_95"],
            "outcome": "rejected: the GNN justifies its cost on this test" if rejected else "stands: the GNN does not clear the bar"}


def h3(metrics: dict, d: dict) -> dict:
    def fall(pre, post):
        return (pre - post) / pre
    falls = {arm: fall(metrics[arm]["pre_shift_test"]["average_precision_mean_per_step"],
                       metrics[arm]["post_shift_test"]["average_precision_mean_per_step"]) for arm in ARMS}
    draws_fall = {arm: fall(d["pre_shift_test"][arm]["ap_mean"], d["post_shift_test"][arm]["ap_mean"]) for arm in ARMS}
    pairs = {}
    for simple, complex_ in (("A", "B"), ("B", "D"), ("A", "D")):
        ci = interval(draws_fall[complex_] - draws_fall[simple])
        pairs[f"{complex_} minus {simple}"] = {"difference": falls[complex_] - falls[simple], "interval_95": ci}
    if all(p["interval_95"]["low"] > 0 for p in pairs.values()):
        outcome = "supported"
    elif any(p["interval_95"]["high"] < 0 for p in pairs.values()):
        outcome = "contradicted: a more complex arm degrades less than a simpler one, outside the noise band"
    else:
        outcome = "not separable"
    return {"definition": "Relative fall in mean per-step PR-AUC from pre-shift to post-shift; positive pair differences mean the more complex arm fell more",
            "relative_fall": falls, "pairs": pairs, "outcome": outcome}


def compute_seconds() -> dict:
    a = read_result("arm-a-tuning")["data"]
    b = read_result("arm-b-tuning")["data"]
    d = read_result("arm-d-tuning")["data"]
    gate = read_result("leakage-tests")["data"]
    threads = int(a["omp_num_threads"] or 1)
    seconds = {
        "A": a["fit_seconds_total"],
        "B": a["fit_seconds_total"] + b["stage_one_fit_seconds"] + b["fit_seconds_total"]
             + gate["pagerank"]["structural_features_seconds"],
        "D": d["fit_seconds_total"],
    }
    return {"seconds": seconds, "threads": threads,
            "note": "B includes Arm A's tuning, because its stage one is Arm A's tuned model, and the graph-store "
                    "structural feature build. Score aggregation time is not included."}


def cost_per_true_positive(metrics: dict, k: int) -> dict:
    compute = compute_seconds()
    out = {}
    for arm in ARMS:
        compute_eur = compute["seconds"][arm] * compute["threads"] / 3600 * EURO_PER_VCPU_HOUR
        out[arm] = {"compute_eur": compute_eur}
        for period in TEST_PERIODS:
            m = metrics[arm][period]
            steps = len(m["per_step"])
            alerts = k * steps
            tp = sum(s["true_positives_at_k"] for s in m["per_step"])
            analyst = {level: alerts * cost for level, cost in ANALYST_COST.items()}
            out[arm][period] = {
                "alerts": alerts, "true_positives": tp,
                "analyst_eur": analyst,
                "cost_per_true_positive_eur": {level: (analyst[level] + compute_eur) / tp if tp else None for level in ANALYST_COST},
                "compute_share_of_cost": compute_eur / (analyst["central"] + compute_eur),
            }
    return {
        "modelled": True,
        "assumptions": {
            "analyst_cost_per_alert_eur": ANALYST_COST,
            "basis": "Author assumption: about 20 minutes of first-line review at about €75 an hour fully loaded. Not sourced.",
            "compute_eur_per_vcpu_hour": EURO_PER_VCPU_HOUR,
            "compute": compute,
        },
        "formula": "(alerts x analyst cost per alert + compute cost) / true positives in the top k, pooled over the period",
        "by_arm": out,
    }


def main() -> None:
    k = require_k_first()["data"]["k"]
    run = np.load(RUNS / "scores.npz")
    run_d = np.load(RUNS / "scores-d.npz")
    assert np.array_equal(run["node_ids"], run_d["node_ids"])
    steps, labels = run["steps"], run["labels"]
    labelled, positives = labels != -1, labels == 1
    arms = {"A": run["A"].mean(axis=0), "B": run["B"].mean(axis=0), "D": run_d["D"].mean(axis=0)}
    seeds = {"A": run["A"], "B": run["B"], "D": run_d["D"]}
    indexes = {p: step_index(steps, labelled, p) for p in TEST_PERIODS}

    metrics = {
        name: {p: {**period_metrics(scores, positives, indexes[p], k),
                   "unlabelled_share_of_top_k_all_nodes": unlabelled_share(scores, steps, labelled, p, k),
                   "queue_curve": queue_curve(scores, positives, indexes[p]),
                   "pr_curve": pr_curve(scores, positives, indexes[p])}
               for p in TEST_PERIODS}
        for name, scores in arms.items()
    }
    per_seed = {
        name: [{p: {key: v for key, v in period_metrics(seeds[name][i], positives, indexes[p], k).items() if key != "per_step"}
                for p in TEST_PERIODS} for i in range(seeds[name].shape[0])]
        for name in arms
    }
    d = draws(arms, positives, indexes, k)
    keys = {"p_at_k": "precision_at_k_pooled", "ap_pooled": "average_precision_pooled",
            "ap_mean": "average_precision_mean_per_step"}
    intervals = {p: {arm: {s: interval(d[p][arm][s]) for s in keys} for arm in ARMS} for p in TEST_PERIODS}
    comparisons = {
        f"{hi} minus {lo}": {p: {s: comparison(metrics[lo][p][key], metrics[hi][p][key], d[p][lo][s], d[p][hi][s], hi, lo)
                                 for s, key in keys.items()} for p in TEST_PERIODS}
        for lo, hi in (("A", "B"), ("B", "D"), ("A", "D"))
    }
    write_result("evaluation-phase-3", {
        "k": k,
        "scores": "Each node's score is the mean of its five seed scores. Metrics on labelled nodes only.",
        "bootstrap": {"resamples": RESAMPLES, "seed": BOOTSTRAP_SEED, "stratified_by": "time step", "paired": True,
                      "note": "Same resamples as results/evaluation-arms-a-b.json"},
        "metrics": metrics,
        "per_seed": per_seed,
        "intervals": intervals,
        "comparisons": comparisons,
        "hypotheses": {
            "H1": h1(metrics, d),
            "H2": h2(comparisons["D minus B"]["pre_shift_test"]["p_at_k"]),
            "H3": h3(metrics, d),
        },
    }, uses_model_features=True)
    write_result("cost-per-true-positive", cost_per_true_positive(metrics, k), uses_model_features=True)
    hyp = read_result("evaluation-phase-3")["data"]["hypotheses"]
    print(f"pre-shift precision at {k}: " + ", ".join(f"{a} {metrics[a]['pre_shift_test']['precision_at_k_pooled']:.3f}" for a in ARMS))
    print(" | ".join(f"{h}: {v['outcome']}" for h, v in hyp.items()))


if __name__ == "__main__":
    main()
