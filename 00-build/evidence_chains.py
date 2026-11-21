"""Structural evidence chains for every transaction Arm B queues in a test step.

A chain is built only from the graph store, through graph/queries/, from what is known at scoring
time: structure and Arm A's stage-one scores. Every fact in every chain is then recomputed from the
columnar store, and the stage halts if any disagrees. Full chains stay in data/store/runs/, because
the dataset's licence rules out publishing per-transaction outputs; results/ gets aggregates only.
"""
import json

import duckdb
import ladybug
import numpy as np

import graph_store
from evaluate_arms import TEST_PERIODS
from evidence_review import write_sheet
from leakage_gate import BASE_GRAPH, STAGING, STRUCTURAL_CACHE
from paths import COLUMNAR_STORE, RUNS
from protocol import PERIODS, period_of, require, require_k_first
from results_io import write_result

REVIEW_SAMPLE = 30
REVIEW_SEED = 20261120


def top_k(scores: np.ndarray, idx: np.ndarray, k: int) -> np.ndarray:
    return idx[np.argsort(-scores[idx], kind="stable")[:k]]


def neighbours(conn, ids) -> dict[int, list[tuple[int, str, float]]]:
    out: dict[int, list[tuple[int, str, float]]] = {}
    if len(ids):
        for node, nbr, direction, score in conn.execute(graph_store.query("evidence-neighbours"),
                                                        {"ids": [int(i) for i in ids]}).get_all():
            out.setdefault(node, []).append((nbr, direction, score))
    return out


def strongest(links, exclude=None):
    """Highest stage-one score; ties go to the lower node id so the choice is deterministic."""
    links = [x for x in links if x[0] != exclude]
    return min(links, key=lambda x: (-x[2], x[0])) if links else None


def columnar_truth(con, flagged_ids: list[int]) -> dict:
    """Same-step neighbours and two-hop sets recomputed in SQL, independently of the graph store."""
    con.execute("CREATE OR REPLACE TEMP TABLE flagged AS SELECT unnest(?::BIGINT[]) AS node_id", [flagged_ids])
    same_step = """
        SELECT e.src, e.dst FROM edges e
        JOIN nodes a ON a.node_id = e.src JOIN nodes b ON b.node_id = e.dst
        WHERE a.time_step = b.time_step
    """
    con.execute(f"CREATE OR REPLACE TEMP TABLE same_step AS {same_step}")
    links = con.execute("""
        SELECT f.node_id, s.src, 'in' FROM flagged f JOIN same_step s ON s.dst = f.node_id
        UNION ALL
        SELECT f.node_id, s.dst, 'out' FROM flagged f JOIN same_step s ON s.src = f.node_id
    """).fetchall()
    two_hop = con.execute("""
        WITH u AS (SELECT src AS a, dst AS b FROM same_step UNION ALL SELECT dst, src FROM same_step),
        reach AS (
            SELECT u.a, u.b AS x FROM u JOIN flagged f ON f.node_id = u.a
            UNION
            SELECT u1.a, u2.b FROM u u1 JOIN flagged f ON f.node_id = u1.a JOIN u u2 ON u2.a = u1.b
        )
        SELECT a, count(DISTINCT x) FROM reach WHERE x <> a GROUP BY a
    """).fetchall()
    truth: dict = {"links": {}, "two_hop": {a: n for a, n in two_hop}}
    for node, nbr, direction in links:
        truth["links"].setdefault(node, set()).add((nbr, direction))
    return truth


def adjacent_same_step(con, pairs: list[tuple[int, int, str]]) -> set[tuple[int, int, str]]:
    if not pairs:
        return set()
    con.execute("CREATE OR REPLACE TEMP TABLE hop2 AS SELECT * FROM (SELECT unnest(?::BIGINT[]) AS a, "
                "unnest(?::BIGINT[]) AS b, unnest(?::VARCHAR[]) AS direction)",
                [[p[0] for p in pairs], [p[1] for p in pairs], [p[2] for p in pairs]])
    rows = con.execute("""
        SELECT h.a, h.b, h.direction FROM hop2 h
        JOIN same_step s ON (h.direction = 'out' AND s.src = h.a AND s.dst = h.b)
                         OR (h.direction = 'in' AND s.src = h.b AND s.dst = h.a)
    """).fetchall()
    return {(a, b, d) for a, b, d in rows}


def sentence(c: dict, k: int) -> str:
    def link(h, frm):
        verb = "receives from" if h["direction"] == "in" else "pays"
        queued = f"in the top {k} of its step by Arm A's model" if h["in_stage_one_top_k"] else \
                 f"ranked {h['stage_one_rank']} in its step by Arm A's model"
        return f"{frm} {verb} {h['neighbour']}, {queued} (score {h['stage_one_score']:.2f})"
    parts = [f"Transaction {c['node_id']}, step {c['step']}, ranked {c['rank_b']} of {k} by Arm B.",
             f"It has {c['in_degree']} incoming and {c['out_degree']} outgoing same-step links, "
             f"and {c['two_hop_size']} transactions within two hops."]
    if c["hop1"]:
        parts.append(f"Strongest link: it {link(c['hop1'], '').strip()}.")
        if c["hop2"]:
            parts.append(f"Next: {link(c['hop2'], str(c['hop1']['neighbour']))}.")
    else:
        parts.append("It has no same-step links, so there is no chain to show.")
    return " ".join(parts)


def main() -> None:
    k = require_k_first()["data"]["k"]
    run = np.load(RUNS / "scores.npz")
    run_d = np.load(RUNS / "scores-d.npz")
    node_ids, steps, labels = run["node_ids"], run["steps"], run["labels"]
    require(np.array_equal(run_d["node_ids"], node_ids), "Arm D's scores cover different nodes from Arms A and B")
    b, a, d, s1 = (x.mean(axis=0) for x in (run["B"], run["A"], run_d["D"], run["stage_one"]))
    cache = np.load(STRUCTURAL_CACHE)
    require(np.array_equal(cache["node_ids"], node_ids), "the structural feature cache covers different nodes")
    labelled = labels != -1
    position = {int(n): i for i, n in enumerate(node_ids)}

    stage_one_rank = np.zeros(len(node_ids), dtype=int)
    for step in np.unique(steps):
        idx = np.flatnonzero(steps == step)
        stage_one_rank[idx[np.argsort(-s1[idx], kind="stable")]] = np.arange(1, len(idx) + 1)

    flagged, flagged_a, flagged_d, rank_b = [], set(), [], {}
    for period in TEST_PERIODS:
        first, last = PERIODS[period]
        for step in range(first, last + 1):
            idx = np.flatnonzero((steps == step) & labelled)
            queue = top_k(b, idx, k)
            flagged.extend(queue)
            rank_b.update({int(i): r + 1 for r, i in enumerate(queue)})
            flagged_a.update(int(i) for i in top_k(a, idx, k))
            flagged_d.extend(top_k(d, idx, k))
    flagged = np.array(flagged)
    flagged_ids = [int(node_ids[i]) for i in flagged]

    db = ladybug.Database(str(BASE_GRAPH))
    conn = ladybug.Connection(db)
    graph_store.load_scores(conn, node_ids, s1, STAGING / "evidence")
    hop1_links = neighbours(conn, flagged_ids)
    hop1 = {n: strongest(hop1_links.get(n, [])) for n in flagged_ids}
    hop2_links = neighbours(conn, sorted({h[0] for h in hop1.values() if h}))

    def describe(link) -> dict:
        i = position[link[0]]
        return {"neighbour": link[0], "direction": link[1], "stage_one_score": float(link[2]),
                "stage_one_rank": int(stage_one_rank[i]), "in_stage_one_top_k": bool(stage_one_rank[i] <= k)}

    chains = []
    for i, node in zip(flagged, flagged_ids):
        h1 = hop1[node]
        h2 = strongest(hop2_links.get(h1[0], []), exclude=node) if h1 else None
        chains.append({
            "node_id": node, "step": int(steps[i]), "period": period_of(int(steps[i])), "rank_b": rank_b[int(i)],
            "label": int(labels[i]), "also_queued_by_a": int(i) in flagged_a,
            "in_degree": int(cache["in_degree"][i]), "out_degree": int(cache["out_degree"][i]),
            "two_hop_size": int(cache["two_hop_size"][i]),
            "hop1": describe(h1) if h1 else None, "hop2": describe(h2) if h2 else None,
        })

    with duckdb.connect(str(COLUMNAR_STORE), read_only=True) as con:
        truth = columnar_truth(con, flagged_ids)
        hop2_true = adjacent_same_step(con, [(c["hop1"]["neighbour"], c["hop2"]["neighbour"], c["hop2"]["direction"])
                                             for c in chains if c["hop2"]])
        known_label_links = con.execute(
            "SELECT count(*) FROM edges e JOIN flagged f ON f.node_id IN (e.src, e.dst) "
            "JOIN nodes n ON n.node_id = CASE WHEN e.src = f.node_id THEN e.dst ELSE e.src END "
            "WHERE n.time_step <= ?", [PERIODS["validation"][1]]).fetchone()[0]
    checked = false = 0
    for c in chains:
        links = truth["links"].get(c["node_id"], set())
        facts = [
            c["in_degree"] == sum(1 for _, dr in links if dr == "in"),
            c["out_degree"] == sum(1 for _, dr in links if dr == "out"),
            c["two_hop_size"] == truth["two_hop"].get(c["node_id"], 0),
            (c["hop1"] is None) == (not links),
        ]
        if c["hop1"]:
            facts.append((c["hop1"]["neighbour"], c["hop1"]["direction"]) in links)
        if c["hop2"]:
            facts.append((c["hop1"]["neighbour"], c["hop2"]["neighbour"], c["hop2"]["direction"]) in hop2_true)
        checked += len(facts)
        false += facts.count(False)
    if false:
        raise SystemExit(f"{false} of {checked} evidence-chain facts disagree with the columnar store")

    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "evidence-chains.json").write_text(json.dumps(chains, indent=1))
    rng = np.random.default_rng(REVIEW_SEED)
    pre = [c for c in chains if c["period"] == "pre_shift_test"]
    sample = [pre[j] for j in sorted(rng.choice(len(pre), size=min(REVIEW_SAMPLE, len(pre)), replace=False))]
    write_sheet([(c["node_id"], sentence(c, k)) for c in sample])

    def share(rows, test) -> float | None:
        return sum(1 for r in rows if test(r)) / len(rows) if rows else None

    def summary(rows) -> dict:
        return {
            "flagged": len(rows),
            "with_chain": share(rows, lambda c: c["hop1"] is not None),
            "with_two_hop_chain": share(rows, lambda c: c["hop2"] is not None),
            "strongest_link_in_stage_one_top_k": share(rows, lambda c: c["hop1"] and c["hop1"]["in_stage_one_top_k"]),
            "also_queued_by_arm_a": share(rows, lambda c: c["also_queued_by_a"]),
            "median_two_hop_size": float(np.median([c["two_hop_size"] for c in rows])) if rows else None,
        }

    by_period = {}
    for period in TEST_PERIODS:
        rows = [c for c in chains if c["period"] == period]
        by_period[period] = {
            "all_flagged": summary(rows),
            "flagged_illicit": summary([c for c in rows if c["label"] == 1]),
            "flagged_licit": summary([c for c in rows if c["label"] == 0]),
        }
    d_two_hop = cache["two_hop_size"][np.array(flagged_d)]
    write_result("evidence-chains", {
        "k": k,
        "queue": "Arm B's top k labelled transactions per test step, from seed-averaged scores, as evaluated.",
        "chain": "Degree and two-hop size of the flagged transaction, then its same-step link to the neighbour with "
                 "the highest Arm A stage-one score, then that neighbour's strongest link onwards. Built with "
                 "graph/queries/ only, from information available at scoring time.",
        "truth_check": {"facts_checked": checked, "facts_false": false,
                        "method": "Every degree, two-hop size and link recomputed in SQL from the columnar store"},
        "links_to_a_known_label": {
            "count": int(known_label_links),
            "counted": "Edges in either direction between a flagged transaction and any transaction in steps 1 to 34",
            "why": "Edges never cross time steps, and test-step labels are not known at scoring time, so no chain "
                   "can cite a counterparty whose label was known.",
        },
        "by_period": by_period,
        "arm_d": {
            "flagged": len(flagged_d),
            "receptive_field_median_transactions": float(np.median(d_two_hop)),
            "receptive_field_empty_share": float(np.mean(d_two_hop == 0)),
            "why_no_chain": "A two-layer GraphSAGE score depends on every transaction within two hops through learned "
                            "weights. The traversal can list those transactions but not say which of them moved the "
                            "score. A post-hoc explainer would add an approximation that is not a fact about the graph.",
        },
        "review": {"sample": len(sample), "seed": REVIEW_SEED, "file": "data/store/runs/evidence-chain-review.csv",
                   "rubric": "Is the reason true, sufficient, and actionable by an investigator. Scored by the author."},
    }, uses_model_features=True)
    pre_all = by_period["pre_shift_test"]["all_flagged"]
    print(f"evidence chains: {checked} facts checked, none false; pre-shift chain coverage {pre_all['with_chain']:.1%}")


if __name__ == "__main__":
    main()
