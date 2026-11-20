import os
import time

import duckdb
import ladybug
import numpy as np

import arm_d
import graph_store
from features import BUDGETS, arm_a, arm_b, budget_labels, load_frame, stage_one_scores
from leakage_gate import BASE_GRAPH, STAGING, STRUCTURAL_CACHE
from paths import COLUMNAR_STORE, RESULTS, ROOT, RUNS
from protocol import require, require_k_first
from results_io import leakage_gate_status, write_result
from tuning import SEEDS, TRIALS, fit_predict, search, tune


def summary(seed, config, trials, final_seconds, extra=None):
    return {
        "seed": seed,
        "best_config": config,
        "best_validation_average_precision": max(t["validation_average_precision"] for t in trials),
        "trials": len(trials),
        "tuning_fit_seconds": round(sum(t["fit_seconds"] for t in trials), 2),
        "final_fit_seconds": round(final_seconds, 2),
        "trial_validation_average_precision": [round(t["validation_average_precision"], 5) for t in trials],
        **(extra or {}),
    }


def main() -> None:
    require_k_first()
    dropped = set(leakage_gate_status(ROOT, RESULTS)["dropped_features"])
    with duckdb.connect(str(COLUMNAR_STORE), read_only=True) as con:
        frame = load_frame(con)
        graph = arm_d.build_graph(frame, *arm_d.load_edges(con))
    cache = np.load(STRUCTURAL_CACHE)
    require(np.array_equal(cache["node_ids"], frame.node_ids), "the structural feature cache covers different nodes")
    structural = {name: cache[name] for name in graph_store.STRUCTURAL}
    db = ladybug.Database(str(BASE_GRAPH))
    conn = ladybug.Connection(db)

    validation = frame.mask("validation") & frame.labelled
    everything = np.ones(len(frame.labels), dtype=bool)
    X_a, _ = arm_a(frame)
    log = {}
    RUNS.mkdir(parents=True, exist_ok=True)
    for fraction in BUDGETS[:-1]:
        name = f"{int(round(fraction * 100)):03d}"
        scores = {arm: np.zeros((len(SEEDS), len(frame.labels))) for arm in "ABD"}
        log[name] = {arm: [] for arm in "ABD"}
        for i, seed in enumerate(SEEDS):
            labels = budget_labels(frame, fraction, seed)
            budget_frame = frame.with_labels(labels)
            train = budget_frame.mask("training") & budget_frame.labelled
            started = time.perf_counter()

            config_a, trials_a = tune(X_a, labels, train, validation, seed)
            t = time.perf_counter()
            scores["A"][i] = fit_predict(config_a, seed, X_a, labels, train, everything)
            log[name]["A"].append(summary(seed, config_a, trials_a, time.perf_counter() - t,
                                          {"training_labels": int(train.sum())}))

            t = time.perf_counter()
            stage_one = stage_one_scores(budget_frame, lambda tr, sc: fit_predict(config_a, seed, X_a, labels, tr, sc))
            stage_one_seconds = time.perf_counter() - t
            aggregates = graph_store.score_aggregates(conn, frame.node_ids, stage_one, STAGING)
            X_b, _ = arm_b(frame, structural, aggregates, dropped)
            config_b, trials_b = tune(X_b, labels, train, validation, seed)
            t = time.perf_counter()
            scores["B"][i] = fit_predict(config_b, seed, X_b, labels, train, everything)
            log[name]["B"].append(summary(seed, config_b, trials_b, time.perf_counter() - t,
                                          {"stage_one_fit_seconds": round(stage_one_seconds, 2)}))

            config_d, trials_d = search(arm_d.sample_configs(seed),
                                        lambda c: arm_d.fit_predict(c, seed, graph, labels, train, validation),
                                        labels, validation)
            t = time.perf_counter()
            scores["D"][i] = arm_d.fit_predict(config_d, seed, graph, labels, train, everything)
            log[name]["D"].append(summary(seed, config_d, trials_d, time.perf_counter() - t))
            print(f"budget {name}%, seed {seed}: A, B and D tuned in {time.perf_counter() - started:.0f}s")
        np.savez(RUNS / f"scores-budget-{name}.npz", node_ids=frame.node_ids, **scores)

    write_result("label-budget-tuning", {
        "budgets_percent": [int(round(f * 100)) for f in BUDGETS],
        "note": "The 100 percent budget is the main run: results/arm-a-tuning.json, arm-b-tuning.json, arm-d-tuning.json.",
        "sampling": "One class-stratified permutation of training labels per seed; budgets nest. Validation labels kept in full.",
        "trials_per_seed": TRIALS,
        "seeds": list(SEEDS),
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
        "per_budget": log,
    }, uses_model_features=True)
    print("label-budget tuning written to results/")


if __name__ == "__main__":
    main()
