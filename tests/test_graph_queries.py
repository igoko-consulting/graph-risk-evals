import duckdb
import numpy as np
import pytest

import graph_store

NODES = [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (10, 2), (11, 2), (12, 2)]
EDGES = [(1, 2), (2, 3), (3, 1), (4, 3), (2, 5), (10, 11), (11, 12), (12, 1)]


@pytest.fixture(scope="module")
def store(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("graph")
    con = duckdb.connect()
    con.execute("CREATE TABLE nodes(node_id BIGINT, time_step INTEGER)")
    con.execute("CREATE TABLE edges(src BIGINT, dst BIGINT)")
    con.executemany("INSERT INTO nodes VALUES (?, ?)", NODES)
    con.executemany("INSERT INTO edges VALUES (?, ?)", EDGES)
    db, conn = graph_store.build(tmp / "g.lbug", *graph_store.export(con, tmp / "staging"))
    node_ids = np.array([n for n, _ in NODES])
    features, meta = graph_store.structural_features(conn, node_ids, [1, 2])
    return db, conn, node_ids, features, tmp


def same_step_edges():
    step = dict(NODES)
    return [(s, d) for s, d in EDGES if step[s] == step[d]]


def reference_pagerank(damping=0.85, iterations=graph_store.PAGERANK_ITERATIONS):
    step = dict(NODES)
    edges = same_step_edges()
    out = {}
    for s in {t for _, t in NODES}:
        members = [n for n, t in NODES if t == s]
        idx = {n: i for i, n in enumerate(members)}
        n = len(members)
        outdeg = np.zeros(n)
        for a, b in edges:
            if step[a] == s:
                outdeg[idx[a]] += 1
        pr = np.full(n, 1 / n)
        for _ in range(iterations):
            nxt = np.zeros(n)
            for a, b in edges:
                if step[a] == s:
                    nxt[idx[b]] += pr[idx[a]] / outdeg[idx[a]]
            dangling = pr[outdeg == 0].sum()
            pr = (1 - damping) / n + damping * (nxt + dangling / n)
        out.update({m: pr[idx[m]] for m in members})
    return np.array([out[n] for n, _ in NODES])


def test_degrees_count_same_step_neighbours_only(store):
    _, _, _, f, _ = store
    assert f["in_degree"].tolist() == [1, 1, 2, 0, 1, 0, 1, 1]
    assert f["out_degree"].tolist() == [1, 2, 1, 1, 0, 1, 1, 0]


def test_two_hop_ignores_direction_and_other_steps(store):
    _, _, _, f, _ = store
    assert f["two_hop_size"].tolist() == [4, 4, 4, 3, 3, 2, 2, 2]


def test_pagerank_matches_power_iteration(store):
    _, _, _, f, _ = store
    np.testing.assert_allclose(f["pagerank"], reference_pagerank(), rtol=0, atol=1e-12)


def test_pagerank_sums_to_one_per_step(store):
    _, _, _, f, _ = store
    steps = np.array([t for _, t in NODES])
    for s in (1, 2):
        assert f["pagerank"][steps == s].sum() == pytest.approx(1.0, abs=1e-12)


def test_neighbour_scores_use_same_step_neighbours_only(store):
    _, conn, node_ids, _, tmp = store
    scores = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    agg = graph_store.score_aggregates(conn, node_ids, scores, tmp / "scores")
    assert agg["nbr_score_in_mean"][0] == pytest.approx(0.3)
    assert agg["nbr_score_in_max"][2] == pytest.approx(0.4)
    assert agg["nbr_score_out_mean"][1] == pytest.approx(0.4)
    assert np.isnan(agg["nbr_score_out_max"][7])
