"""Gate 2. Runs before any arm is tuned, on the full data, with a fixed reference stage-one model.

The properties tested are structural (neighbour scoping and the out-of-fold design), so they hold for
any stage-one configuration, including the tuned ones used later.
"""
import time

import duckdb
import numpy as np

import graph_store
from features import ILLICIT, LICIT, STAGE_ONE_BLOCKS, Frame, load_frame, stage_one_scores
from paths import COLUMNAR_STORE, STORE
from tuning import REFERENCE_CONFIG, fit_predict
from results_io import write_result

TOLERANCE = 1e-12
FLIPS_PER_BLOCK = 40
BASE_GRAPH = STORE / "features-base.lbug"
FUTURE_GRAPH = STORE / "features-future-edge.lbug"
STRUCTURAL_CACHE = STORE / "structural-features.npz"
STAGING = STORE / "staging"


def feature_values(frame: Frame, conn, structural: dict) -> tuple[dict, np.ndarray]:
    scores = stage_one_scores(
        frame, lambda train, score: fit_predict(REFERENCE_CONFIG, 0, frame.local, frame.labels, train, score)
    )
    return {**structural, **graph_store.score_aggregates(conn, frame.node_ids, scores, STAGING)}, scores


def max_diff(a: np.ndarray, b: np.ndarray, where: np.ndarray) -> float:
    x, y = a[where], b[where]
    both_nan = np.isnan(x) & np.isnan(y)
    if (np.isnan(x) != np.isnan(y)).any():
        return float("inf")
    return float(np.max(np.abs(x[~both_nan] - y[~both_nan]), initial=0.0))


def pick_future_edges(con, frame: Frame) -> list[tuple[int, int]]:
    last, early = int(frame.steps.max()), 10
    late = frame.node_ids[frame.steps == last]
    old = frame.node_ids[frame.steps == early]
    existing = {tuple(r) for r in con.execute(
        "SELECT src, dst FROM edges WHERE src IN (SELECT node_id FROM nodes WHERE time_step = ?)", [last]).fetchall()}
    a, b = next((int(x), int(y)) for x in late[:50] for y in late[:50] if x != y and (x, y) not in existing)
    return [(a, b), (int(late[-1]), int(old[0])), (int(old[-1]), int(late[-2]))]


def main() -> None:
    started = time.perf_counter()
    with duckdb.connect(str(COLUMNAR_STORE), read_only=True) as con:
        frame = load_frame(con)
        future_edges = pick_future_edges(con, frame)
        base_files = graph_store.export(con, STAGING / "base")
        future_files = graph_store.export(con, STAGING / "future", future_edges)
    steps = np.unique(frame.steps)

    base_db, base = graph_store.build(BASE_GRAPH, *base_files)
    structural, structural_meta = graph_store.structural_features(base, frame.node_ids, steps)
    np.savez(STRUCTURAL_CACHE, node_ids=frame.node_ids, **structural)
    values, base_scores = feature_values(frame, base, structural)
    names = list(values)
    results = {name: {} for name in names}

    future_db, future = graph_store.build(FUTURE_GRAPH, *future_files)
    future_structural, _ = graph_store.structural_features(future, frame.node_ids, steps)
    future_values, _ = feature_values(frame, future, future_structural)
    earlier = frame.steps < frame.steps.max()
    latest = ~earlier
    effect = {n: max_diff(values[n], future_values[n], latest) for n in names}
    for n in names:
        results[n]["future_edge_max_change_earlier_steps"] = max_diff(values[n], future_values[n], earlier)
    future_effect_visible = max(effect.values()) > TOLERANCE
    del future, future_db
    graph_store.reset(FUTURE_GRAPH)

    rng = np.random.default_rng(20261119)
    evaluation = frame.steps > 29
    shuffled = frame.labels.copy()
    shuffled[evaluation] = rng.permutation(shuffled[evaluation])
    assert (shuffled != frame.labels).any()
    shuffled_values, _ = feature_values(frame.with_labels(shuffled), base, structural)
    everywhere = np.ones(len(frame.node_ids), dtype=bool)
    for n in names:
        results[n]["label_shuffle_max_change"] = max_diff(values[n], shuffled_values[n], everywhere)

    # Flips are made one block at a time. Flipping nodes in several blocks at once moves a node's
    # aggregates through other nodes' labels, which the out-of-fold design allows by intent.
    training_labelled = frame.mask("training") & frame.labelled
    own_change = {n: 0.0 for n in graph_store.SCORE_AGGREGATES}
    flip_effect_visible, nodes_flipped = True, 0
    for first, last in STAGE_ONE_BLOCKS:
        in_block = np.flatnonzero(training_labelled & (frame.steps >= first) & (frame.steps <= last))
        flipped_idx = rng.choice(in_block, size=FLIPS_PER_BLOCK, replace=False)
        flipped = frame.labels.copy()
        flipped[flipped_idx] = np.where(flipped[flipped_idx] == ILLICIT, LICIT, ILLICIT)
        flipped_values, flipped_scores = feature_values(frame.with_labels(flipped), base, structural)
        own = np.zeros(len(frame.node_ids), dtype=bool)
        own[flipped_idx] = True
        flip_effect_visible &= float(np.max(np.abs(flipped_scores - base_scores))) > TOLERANCE
        nodes_flipped += len(flipped_idx)
        for n in own_change:
            own_change[n] = max(own_change[n], max_diff(values[n], flipped_values[n], own))
    for n, change in own_change.items():
        results[n]["own_label_flip_max_change"] = change

    for n, r in results.items():
        r["passed"] = all(v <= TOLERANCE for v in r.values())
    tests_valid = future_effect_visible and flip_effect_visible
    dropped = sorted(n for n, r in results.items() if not r["passed"])
    write_result("leakage-tests", {
        "description": "Gate 2. Every Arm B feature is recomputed under three perturbations and compared with its "
                       "unperturbed value. A feature that moves is dropped, not adjusted.",
        "tests": {
            "future_edge": {
                "what": "Inject edges dated to the last time step, including two that cross back to step 10. "
                        "No feature of any node in an earlier step may change.",
                "injected_edges": future_edges,
                "effect_visible_in_last_step": future_effect_visible,
            },
            "label_shuffle": {
                "what": "Permute every label in steps 30 to 49. No feature of any node may change.",
            },
            "own_label_flip": {
                "what": f"In each stage-one block in turn, flip the labels of {FLIPS_PER_BLOCK} sampled training nodes. "
                        "Their own neighbour-score aggregates may not change.",
                "nodes_flipped": nodes_flipped,
                "effect_visible_elsewhere": flip_effect_visible,
            },
        },
        "stage_one_model": {"config": REFERENCE_CONFIG, "seed": 0, "note": "fixed reference model; the gate runs before any arm is tuned"},
        "tolerance": TOLERANCE,
        "per_feature": results,
        "tests_valid": tests_valid,
        "dropped_features": dropped,
        "gate_passed": tests_valid,
        "pagerank": {"damping": graph_store.DAMPING, "iterations": graph_store.PAGERANK_ITERATIONS, **structural_meta},
        "seconds": round(time.perf_counter() - started, 1),
    })
    print(f"leakage gate: {'passed' if tests_valid else 'INVALID'}; dropped features: {dropped or 'none'}")
    if not tests_valid:
        raise SystemExit("leakage tests had no visible effect, so they test nothing; halting")


if __name__ == "__main__":
    main()
