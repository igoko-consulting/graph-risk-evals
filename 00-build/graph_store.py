import shutil
from pathlib import Path

import duckdb
import ladybug
import numpy as np

from paths import QUERIES

SCHEMA = (
    "CREATE NODE TABLE Tx(node_id INT64, time_step INT64, PRIMARY KEY(node_id))",
    "CREATE REL TABLE PAYS(FROM Tx TO Tx)",
)
WORKING_PROPERTIES = (
    "outdeg INT64 DEFAULT 0",
    "n_step INT64 DEFAULT 0",
    "pr DOUBLE DEFAULT 0.0",
    "pr_next DOUBLE DEFAULT 0.0",
    "dangling DOUBLE DEFAULT 0.0",
    "score DOUBLE DEFAULT 0.0",
)
DAMPING = 0.85
# Fixed rather than stopped on convergence: a global stopping rule would let a change in one
# step alter how many iterations every other step receives.
PAGERANK_ITERATIONS = 100
STRUCTURAL = ("in_degree", "out_degree", "pagerank", "two_hop_size")
SCORE_AGGREGATES = ("nbr_score_in_mean", "nbr_score_in_max", "nbr_score_out_mean", "nbr_score_out_max")


def statements(name: str) -> list[str]:
    text = (QUERIES / f"{name}.cypher").read_text()
    parts = [p.strip() for p in text.split(";")]
    return [p for p in parts if any(line.strip() and not line.strip().startswith("//") for line in p.splitlines())]


def query(name: str) -> str:
    (single,) = statements(name)
    return single


def reset(path: Path) -> None:
    for p in (path, path.with_name(path.name + ".wal")):
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()


def export(con: duckdb.DuckDBPyConnection, staging: Path, extra_edges: list[tuple[int, int]] = ()) -> tuple[Path, Path]:
    staging.mkdir(parents=True, exist_ok=True)
    nodes_file, edges_file = staging / "nodes.parquet", staging / "edges.parquet"
    con.execute(f"COPY (SELECT node_id, time_step FROM nodes ORDER BY node_id) TO '{nodes_file}' (FORMAT parquet)")
    extra = " UNION ALL ".join(f"SELECT {int(s)}::BIGINT, {int(d)}::BIGINT" for s, d in extra_edges)
    edges_sql = "SELECT src, dst FROM edges" + (f" UNION ALL {extra}" if extra else "")
    con.execute(f"COPY ({edges_sql}) TO '{edges_file}' (FORMAT parquet)")
    return nodes_file, edges_file


def build(path: Path, nodes_file: Path, edges_file: Path) -> tuple[ladybug.Database, ladybug.Connection]:
    reset(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = ladybug.Database(str(path))
    conn = ladybug.Connection(db)
    for statement in SCHEMA:
        conn.execute(statement)
    conn.execute(f"COPY Tx FROM '{nodes_file}'")
    conn.execute(f"COPY PAYS FROM '{edges_file}'")
    for prop in WORKING_PROPERTIES:
        conn.execute(f"ALTER TABLE Tx ADD {prop}")
    return db, conn


def per_step(conn, name: str, steps, node_ids: np.ndarray, default: float = 0.0) -> np.ndarray:
    out = np.full(len(node_ids), default, dtype=float)
    q = query(name)
    for step in steps:
        rows = conn.execute(q, {"step": int(step)}).get_all()
        if rows:
            ids, values = np.array([r[0] for r in rows]), np.array([r[1] for r in rows], dtype=float)
            out[np.searchsorted(node_ids, ids)] = values
    return out


def pagerank(conn, node_ids: np.ndarray) -> tuple[np.ndarray, float]:
    for statement in statements("pagerank-setup"):
        conn.execute(statement)
    iterate, delta_q, commit = statements("pagerank-iterate"), query("pagerank-delta"), query("pagerank-commit")
    delta = float("nan")
    for _ in range(PAGERANK_ITERATIONS):
        for statement in iterate:
            conn.execute(statement, {"damping": DAMPING} if "$damping" in statement else None)
        delta = conn.execute(delta_q).get_next()[0]
        conn.execute(commit)
    rows = conn.execute("MATCH (t:Tx) RETURN t.node_id, t.pr ORDER BY t.node_id").get_all()
    ids = np.array([r[0] for r in rows])
    assert np.array_equal(ids, node_ids), "graph store nodes differ from the columnar store"
    return np.array([r[1] for r in rows], dtype=float), float(delta)


def structural_features(conn, node_ids: np.ndarray, steps) -> tuple[dict, dict]:
    """Takes no labels and no scores, so no label can reach these values."""
    features = {
        "in_degree": per_step(conn, "in-degree", steps, node_ids),
        "out_degree": per_step(conn, "out-degree", steps, node_ids),
        "two_hop_size": per_step(conn, "two-hop-size", steps, node_ids),
    }
    features["pagerank"], final_delta = pagerank(conn, node_ids)
    return {name: features[name] for name in STRUCTURAL}, {"pagerank_final_max_change": final_delta}


def score_aggregates(conn, node_ids: np.ndarray, scores: np.ndarray, staging: Path) -> dict:
    staging.mkdir(parents=True, exist_ok=True)
    path = staging / "scores.csv"
    np.savetxt(path, np.column_stack([node_ids, scores]), delimiter=",", header="node_id,score",
               comments="", fmt=["%d", "%.17g"])
    conn.execute(f"LOAD WITH HEADERS (node_id INT64, score DOUBLE) FROM '{path}' (header=true) "
                 "MATCH (t:Tx {node_id: node_id}) SET t.score = score")
    rows = conn.execute(query("neighbour-scores")).get_all()
    ids = np.array([r[0] for r in rows])
    assert np.array_equal(ids, node_ids), "graph store nodes differ from the columnar store"
    values = np.array([[np.nan if v is None else v for v in r[1:]] for r in rows], dtype=float)
    return {name: values[:, i] for i, name in enumerate(SCORE_AGGREGATES)}
