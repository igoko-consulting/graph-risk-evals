import os
import time

import duckdb
import ladybug
import numpy as np

import graph_store
from features import arm_a, arm_b, load_frame, stage_one_scores
from leakage_gate import BASE_GRAPH, STAGING, STRUCTURAL_CACHE
from paths import COLUMNAR_STORE, RESULTS, ROOT, RUNS
from protocol import require_k_first
from results_io import leakage_gate_status, write_result
from tuning import SEEDS, TRIALS, fit_predict, tune


def tuning_summary(name: str, feature_names: tuple, log: list, extra: dict) -> dict:
    return {
        "arm": name,
        "feature_count": len(feature_names),
        "features": list(feature_names),
        "trials_per_seed": TRIALS,
        "seeds": list(SEEDS),
        "trials_total": sum(len(s["trials"]) for s in log),
        "fit_seconds_total": round(sum(s["tuning_fit_seconds"] + s["final_fit_seconds"] for s in log), 1),
        "cpu_count": os.cpu_count(),
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
        "per_seed": log,
        **extra,
    }


def main() -> None:
    require_k_first()
    gate = leakage_gate_status(ROOT, RESULTS)
    dropped = set(gate["dropped_features"])
    with duckdb.connect(str(COLUMNAR_STORE), read_only=True) as con:
        frame = load_frame(con)
    cache = np.load(STRUCTURAL_CACHE)
    assert np.array_equal(cache["node_ids"], frame.node_ids)
    structural = {name: cache[name] for name in graph_store.STRUCTURAL}
    db = ladybug.Database(str(BASE_GRAPH))
    conn = ladybug.Connection(db)

    y = frame.labels
    train = frame.mask("training") & frame.labelled
    validation = frame.mask("validation") & frame.labelled
    everything = np.ones(len(y), dtype=bool)
    X_a, names_a = arm_a(frame)
    scores = {"A": np.zeros((len(SEEDS), len(y))), "B": np.zeros((len(SEEDS), len(y)))}
    logs = {"A": [], "B": []}
    stage_one_seconds = 0.0
    names_b = ()

    for i, seed in enumerate(SEEDS):
        started = time.perf_counter()
        config_a, trials_a = tune(X_a, y, train, validation, seed)
        final = time.perf_counter()
        scores["A"][i] = fit_predict(config_a, seed, X_a, y, train, everything)
        logs["A"].append({
            "seed": seed, "best_config": config_a,
            "best_validation_average_precision": max(t["validation_average_precision"] for t in trials_a),
            "tuning_fit_seconds": round(sum(t["fit_seconds"] for t in trials_a), 2),
            "final_fit_seconds": round(time.perf_counter() - final, 2),
            "trials": trials_a,
        })
        print(f"seed {seed}: Arm A tuned in {final - started:.0f}s")

        started = time.perf_counter()
        stage_one = stage_one_scores(frame, lambda tr, sc: fit_predict(config_a, seed, X_a, y, tr, sc))
        stage_one_seconds += time.perf_counter() - started
        aggregates = graph_store.score_aggregates(conn, frame.node_ids, stage_one, STAGING)
        X_b, names_b = arm_b(frame, structural, aggregates, dropped)

        started = time.perf_counter()
        config_b, trials_b = tune(X_b, y, train, validation, seed)
        final = time.perf_counter()
        scores["B"][i] = fit_predict(config_b, seed, X_b, y, train, everything)
        logs["B"].append({
            "seed": seed, "best_config": config_b,
            "best_validation_average_precision": max(t["validation_average_precision"] for t in trials_b),
            "tuning_fit_seconds": round(sum(t["fit_seconds"] for t in trials_b), 2),
            "final_fit_seconds": round(time.perf_counter() - final, 2),
            "trials": trials_b,
        })
        print(f"seed {seed}: Arm B tuned in {final - started:.0f}s")

    RUNS.mkdir(parents=True, exist_ok=True)
    np.savez(RUNS / "scores.npz", node_ids=frame.node_ids, steps=frame.steps, labels=frame.labels, **scores)
    write_result("arm-a-tuning", tuning_summary("A", names_a, logs["A"], {
        "reads_graph_store": False,
    }), uses_model_features=True)
    write_result("arm-b-tuning", tuning_summary("B", names_b, logs["B"], {
        "dropped_by_leakage_gate": sorted(dropped),
        "stage_one_fit_seconds": round(stage_one_seconds, 1),
        "stage_one_note": "Stage one is Arm A's tuned model for the same seed; its fit time is Arm B compute.",
    }), uses_model_features=True)
    print("arm tuning written to results/")


if __name__ == "__main__":
    main()
