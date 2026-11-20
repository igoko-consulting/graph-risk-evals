import platform
import shutil
import time

import duckdb
import ladybug
import numpy as np

import graph_store
from paths import COLUMNAR_STORE, GRAPH_STORE, STORE
from protocol import require
from results_io import write_result


def main() -> None:
    staging = STORE / "staging" / "check"
    with duckdb.connect(str(COLUMNAR_STORE), read_only=True) as con:
        files = graph_store.export(con, staging)
        reference = dict(con.execute(
            "SELECT n.node_id, count(e.src) FROM nodes n LEFT JOIN edges e ON e.dst = n.node_id GROUP BY n.node_id"
        ).fetchall())
        node_ids = np.array(sorted(reference))
        steps = [r[0] for r in con.execute("SELECT DISTINCT time_step FROM nodes ORDER BY 1").fetchall()]
        n_edges = con.execute("SELECT count(*) FROM edges").fetchone()[0]

    started = time.perf_counter()
    db, conn = graph_store.build(GRAPH_STORE, *files)
    load_seconds = time.perf_counter() - started

    started = time.perf_counter()
    in_degree = graph_store.per_step(conn, "in-degree", steps, node_ids)
    query_seconds = time.perf_counter() - started

    one = lambda cypher: conn.execute(cypher).get_next()[0]
    graph_nodes = one("MATCH (t:Tx) RETURN count(t)")
    graph_edges = one("MATCH ()-[p:PAYS]->() RETURN count(p)")
    graph_cross = one("MATCH (a:Tx)-[:PAYS]->(b:Tx) WHERE a.time_step <> b.time_step RETURN count(*)")
    disagreements = int(sum(in_degree[i] != reference[n] for i, n in enumerate(node_ids)))
    shutil.rmtree(staging)

    require(graph_nodes == len(reference) and graph_edges == n_edges, "graph store counts differ from the columnar store")
    require(disagreements == 0, f"in-degree disagrees with the columnar store for {disagreements} nodes")
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
