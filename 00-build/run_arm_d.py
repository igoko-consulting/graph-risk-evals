import os
import time

import duckdb
import numpy as np

import arm_d
from features import load_frame
from paths import COLUMNAR_STORE, RESULTS, ROOT, RUNS
from protocol import require_k_first
from results_io import leakage_gate_status, write_result
from tuning import SEEDS, TRIALS, search


def main() -> None:
    require_k_first()
    leakage_gate_status(ROOT, RESULTS)
    with duckdb.connect(str(COLUMNAR_STORE), read_only=True) as con:
        frame = load_frame(con)
        graph = arm_d.build_graph(frame, *arm_d.load_edges(con))
    y = frame.labels
    train = frame.mask("training") & frame.labelled
    validation = frame.mask("validation") & frame.labelled
    everything = np.ones(len(y), dtype=bool)
    scores = np.zeros((len(SEEDS), len(y)))
    log = []
    for i, seed in enumerate(SEEDS):
        started = time.perf_counter()
        config, trials = search(arm_d.sample_configs(seed),
                                lambda c: arm_d.fit_predict(c, seed, graph, y, train, validation), y, validation)
        final = time.perf_counter()
        scores[i] = arm_d.fit_predict(config, seed, graph, y, train, everything)
        log.append({
            "seed": seed, "best_config": config,
            "best_validation_average_precision": max(t["validation_average_precision"] for t in trials),
            "tuning_fit_seconds": round(sum(t["fit_seconds"] for t in trials), 2),
            "final_fit_seconds": round(time.perf_counter() - final, 2),
            "trials": trials,
        })
        print(f"seed {seed}: Arm D tuned in {final - started:.0f}s")
    RUNS.mkdir(parents=True, exist_ok=True)
    np.savez(RUNS / "scores-d.npz", node_ids=frame.node_ids, D=scores)
    write_result("arm-d-tuning", {
        "arm": "D",
        "architecture": "two-layer GraphSAGE, mean aggregation, same-step edges in both directions, inductive",
        "input_features": 93,
        "reads_graph_structure": True,
        "trials_per_seed": TRIALS,
        "seeds": list(SEEDS),
        "trials_total": sum(len(s["trials"]) for s in log),
        "fit_seconds_total": round(sum(s["tuning_fit_seconds"] + s["final_fit_seconds"] for s in log), 1),
        "cpu_count": os.cpu_count(),
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
        "per_seed": log,
    }, uses_model_features=True)
    print("arm D tuning written to results/")


if __name__ == "__main__":
    main()
