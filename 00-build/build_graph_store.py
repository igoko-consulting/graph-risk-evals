import platform
import shutil
import time

import duckdb
import ladybug

from paths import COLUMNAR_STORE, GRAPH_STORE, QUERIES, STORE
from results_io import write_result

SCHEMA = (
    "CREATE NODE TABLE Tx(node_id INT64, time_step INT64, PRIMARY KEY(node_id))",
    "CREATE REL TABLE PAYS(FROM Tx TO Tx)",
)


def _reset(path) -> None:
    for p in (path, path.with_name(path.name + ".wal")):
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()


def main() -> None:
    staging = STORE / "staging"
    staging.mkdir(parents=True, exist_ok=True)
    nodes_file, edges_file = staging / "nodes.parquet", staging / "edges.parquet"
    with duckdb.connect(str(COLUMNAR_STORE), read_only=True) as con:
        con.execute(f"COPY (SELECT node_id, time_step FROM nodes ORDER BY node_id) TO '{nodes_file}' (FORMAT parquet)")
        con.execute(f"COPY (SELECT src, dst FROM edges) TO '{edges_file}' (FORMAT parquet)")
        reference = dict(con.execute(
            "SELECT n.node_id, count(e.src) FROM nodes n LEFT JOIN edges e ON e.dst = n.node_id GROUP BY n.node_id"
        ).fetchall())
        steps = [r[0] for r in con.execute("SELECT DISTINCT time_step FROM nodes ORDER BY 1").fetchall()]
        n_edges = con.execute("SELECT count(*) FROM edges").fetchone()[0]

    _reset(GRAPH_STORE)
    started = time.perf_counter()
    db = ladybug.Database(str(GRAPH_STORE))
    conn = ladybug.Connection(db)
    for statement in SCHEMA:
        conn.execute(statement)
    conn.execute(f"COPY Tx FROM '{nodes_file}'")
    conn.execute(f"COPY PAYS FROM '{edges_file}'")
    load_seconds = time.perf_counter() - started

    query = (QUERIES / "in-degree.cypher").read_text()
    started = time.perf_counter()
    graph_in_degree = {}
    for step in steps:
        for node_id, in_degree in conn.execute(query, {"step": step}).get_all():
            graph_in_degree[node_id] = in_degree
    query_seconds = time.perf_counter() - started

    one = lambda cypher: conn.execute(cypher).get_next()[0]
    graph_nodes = one("MATCH (t:Tx) RETURN count(t)")
    graph_edges = one("MATCH ()-[p:PAYS]->() RETURN count(p)")
    graph_cross = one("MATCH (a:Tx)-[:PAYS]->(b:Tx) WHERE a.time_step <> b.time_step RETURN count(*)")
    disagreements = sum(1 for node_id, d in reference.items() if graph_in_degree.get(node_id) != d)
    shutil.rmtree(staging)

    assert graph_nodes == len(reference) and graph_edges == n_edges, "graph store counts differ from the columnar store"
    assert disagreements == 0, f"in-degree disagrees with the columnar store for {disagreements} nodes"
    path = write_result("graph-store-check", {
        "engine": f"LadybugDB {ladybug.__version__}",
        "store": "one database; node property time_step scopes each per-step graph",
        "query": "graph/queries/in-degree.cypher, run once per time step",
        "nodes": graph_nodes,
        "edges": graph_edges,
        "time_steps_queried": len(steps),
        "edges_crossing_time_steps": graph_cross,
        "nodes_where_in_degree_disagrees_with_columnar_store": disagreements,
        "timing_seconds": {"load": round(load_seconds, 3), "in_degree_all_steps": round(query_seconds, 3)},
        "timing_note": "Wall-clock on the machine that ran the build. Not a benchmark.",
        "machine": f"{platform.system()} {platform.machine()}",
    })
    print(f"graph store loaded ({graph_nodes} nodes, {graph_edges} edges); in-degree matches for every node; {path.name}")


if __name__ == "__main__":
    main()
