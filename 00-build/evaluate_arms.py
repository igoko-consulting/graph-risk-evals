import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_curve

from paths import RUNS
from protocol import PERIODS, require_k_first
from results_io import write_result

RESAMPLES = 1000
BOOTSTRAP_SEED = 20261119
TEST_PERIODS = ("pre_shift_test", "post_shift_test")
QUEUE_SIZES = tuple(range(10, 501, 10))


def tp_at(scores: np.ndarray, positives: np.ndarray, k: int) -> int:
    return int(positives[np.argsort(-scores, kind="stable")[:k]].sum())


def ap(positives: np.ndarray, scores: np.ndarray):
    return float(average_precision_score(positives, scores)) if 0 < positives.sum() < len(positives) else None


def step_index(steps, labelled, period):
    first, last = PERIODS[period]
    return {s: np.flatnonzero((steps == s) & labelled) for s in range(first, last + 1)}


def period_metrics(scores, positives, index: dict, k: int) -> dict:
    per_step, tp_total, illicit_total = [], 0, 0
    for step, idx in index.items():
        tp, illicit = tp_at(scores[idx], positives[idx], k), int(positives[idx].sum())
        tp_total, illicit_total = tp_total + tp, illicit_total + illicit
        per_step.append({
            "time_step": step, "labelled": len(idx), "illicit": illicit, "true_positives_at_k": tp,
            "precision_at_k": tp / k, "recall_at_k": tp / illicit if illicit else None,
            "average_precision": ap(positives[idx], scores[idx]),
        })
    pooled = np.concatenate(list(index.values()))
    step_aps = [s["average_precision"] for s in per_step if s["average_precision"] is not None]
    ceiling = sum(min(s["illicit"], k) for s in per_step) / (k * len(index))
    return {
        "precision_at_k_pooled": tp_total / (k * len(index)),
        "precision_at_k_ceiling": ceiling,
        "recall_at_k_pooled": tp_total / illicit_total if illicit_total else None,
        "average_precision_pooled": ap(positives[pooled], scores[pooled]),
        "average_precision_mean_per_step": float(np.mean(step_aps)) if step_aps else None,
        "steps_without_average_precision": [s["time_step"] for s in per_step if s["average_precision"] is None],
        "per_step": per_step,
    }


def queue_curve(scores, positives, index: dict) -> list:
    out = []
    illicit = sum(int(positives[i].sum()) for i in index.values())
    for q in QUEUE_SIZES:
        tp = sum(tp_at(scores[i], positives[i], q) for i in index.values())
        out.append({"queue_per_step": q, "precision": tp / (q * len(index)), "recall": tp / illicit if illicit else None})
    return out


def pr_curve(scores, positives, index: dict, points: int = 200) -> dict:
    pooled = np.concatenate(list(index.values()))
    precision, recall, _ = precision_recall_curve(positives[pooled], scores[pooled])
    keep = np.unique(np.linspace(0, len(precision) - 1, points).astype(int))
    return {"precision": np.round(precision[keep], 5).tolist(), "recall": np.round(recall[keep], 5).tolist()}


def unlabelled_share(scores, steps, labelled, period: str, k: int) -> float:
    first, last = PERIODS[period]
    shares = []
    for s in range(first, last + 1):
        idx = np.flatnonzero(steps == s)
        top = idx[np.argsort(-scores[idx], kind="stable")[:k]]
        shares.append(float((~labelled[top]).mean()))
    return float(np.mean(shares))


def interval(values) -> dict:
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    return {"low": float(np.percentile(v, 2.5)), "high": float(np.percentile(v, 97.5)), "resamples": int(len(v))}


def bootstrap(arms: dict, positives, indexes: dict, k: int) -> dict:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = {p: {a: {"p_at_k": [], "ap_pooled": [], "ap_mean": []} for a in arms} for p in indexes}
    for _ in range(RESAMPLES):
        for period, index in indexes.items():
            sampled = {s: rng.choice(idx, size=len(idx), replace=True) for s, idx in index.items()}
            pooled = np.concatenate(list(sampled.values()))
            for name, scores in arms.items():
                tp = sum(tp_at(scores[i], positives[i], k) for i in sampled.values())
                step_aps = [ap(positives[i], scores[i]) for i in sampled.values()]
                step_aps = [a for a in step_aps if a is not None]
                d = draws[period][name]
                d["p_at_k"].append(tp / (k * len(sampled)))
                pooled_ap = ap(positives[pooled], scores[pooled])
                d["ap_pooled"].append(np.nan if pooled_ap is None else pooled_ap)
                d["ap_mean"].append(np.mean(step_aps) if step_aps else np.nan)
    out = {}
    for period, by_arm in draws.items():
        a, b = by_arm["A"], by_arm["B"]
        out[period] = {
            "A": {m: interval(v) for m, v in a.items()},
            "B": {m: interval(v) for m, v in b.items()},
            "B_minus_A": {m: interval(np.array(b[m]) - np.array(a[m])) for m in a},
        }
    return out


def verdict(ci: dict) -> str:
    if ci["low"] > 0:
        return "B higher, outside the noise band"
    if ci["high"] < 0:
        return "A higher, outside the noise band"
    return "within the noise band"


def main() -> None:
    k = require_k_first()["data"]["k"]
    run = np.load(RUNS / "scores.npz")
    steps, labels = run["steps"], run["labels"]
    labelled, positives = labels != -1, labels == 1
    arms = {"A": run["A"].mean(axis=0), "B": run["B"].mean(axis=0)}
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
        name: [{p: {key: v for key, v in period_metrics(run[name][i], positives, indexes[p], k).items() if key != "per_step"}
                for p in TEST_PERIODS} for i in range(run[name].shape[0])]
        for name in arms
    }
    ci = bootstrap(arms, positives, indexes, k)

    h3 = {}
    for name in arms:
        pre = metrics[name]["pre_shift_test"]["average_precision_mean_per_step"]
        post = metrics[name]["post_shift_test"]["average_precision_mean_per_step"]
        h3[name] = {"pre_shift_mean": pre, "post_shift_mean": post, "relative_fall": (pre - post) / pre}

    kill_ci = ci["pre_shift_test"]["B_minus_A"]["p_at_k"]
    kill_fires = not kill_ci["low"] > 0
    comparisons = {
        p: {m: {"difference": metrics["B"][p][key] - metrics["A"][p][key], "interval_95": ci[p]["B_minus_A"][m],
                "verdict": verdict(ci[p]["B_minus_A"][m])}
            for m, key in (("p_at_k", "precision_at_k_pooled"), ("ap_pooled", "average_precision_pooled"),
                           ("ap_mean", "average_precision_mean_per_step"))}
        for p in TEST_PERIODS
    }
    write_result("evaluation-arms-a-b", {
        "k": k,
        "scores": "Each node's score is the mean of its five seed scores. Metrics on labelled nodes only.",
        "bootstrap": {"resamples": RESAMPLES, "seed": BOOTSTRAP_SEED, "stratified_by": "time step", "paired": True},
        "metrics": metrics,
        "per_seed": per_seed,
        "intervals": ci,
        "comparisons_b_minus_a": comparisons,
        "h3_relative_fall_in_average_precision": h3,
        "kill_criterion": {
            "rule": "Arm D is built only if the 95% interval on B minus A, precision at k pooled over steps 35 to 42, lies wholly above zero.",
            "interval": kill_ci,
            "fires": kill_fires,
            "decision": "Do not build Arm D. Continue Phase 3 without it." if kill_fires else "Build Arm D in Phase 3.",
        },
    }, uses_model_features=True)
    print(f"pre-shift precision at {k}: A {metrics['A']['pre_shift_test']['precision_at_k_pooled']:.3f}, "
          f"B {metrics['B']['pre_shift_test']['precision_at_k_pooled']:.3f}; "
          f"B - A 95% CI [{kill_ci['low']:.3f}, {kill_ci['high']:.3f}]; kill criterion {'FIRES' if kill_fires else 'does not fire'}")


if __name__ == "__main__":
    main()
