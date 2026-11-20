"""Engine comparison appendix: Arm B's four graph workloads, timed in the graph store and the columnar store.

Both engines run in this process, on file-based stores built from the same exported files, with the
same thread count, and return rows as Python tuples. Outputs must agree before any timing is kept.
The neighbour-score workload uses synthetic scores, so no model output is involved.
"""
import os
import platform
import statistics
import subprocess
import time

import duckdb
import ladybug
import numpy as np

import graph_store
from paths import COLUMNAR_STORE, ROOT, STORE
from results_io import write_result

SQL = ROOT / "graph" / "sql"
LADYBUG_PATH = STORE / "engine-comparison.lbug"
DUCKDB_PATH = STORE / "engine-comparison.duckdb"
STAGING = STORE / "staging" / "engine-comparison"
REPEATS = 3
SCORE_SEED = 20261119
TOLERANCE = 1e-9


def sql(name: str) -> str:
    return (SQL / f"{name}.sql").read_text()


def aligned(rows, node_ids: np.ndarray, columns: int, default=0.0) -> np.ndarray:
    out = np.full((len(node_ids), columns), default, dtype=float)
    if rows:
        ids = np.array([r[0] for r in rows])
        out[np.searchsorted(node_ids, ids)] = [[np.nan if v is None else v for v in r[1:]] for r in rows]
    return out


class Ladybug:
    name = "LadybugDB (graph store, Cypher)"

    def __init__(self, conn, node_ids, steps):
        self.conn, self.node_ids, self.steps = conn, node_ids, steps

    def per_step(self, query_name: str) -> np.ndarray:
        q = graph_store.query(query_name)
        rows = [r for s in self.steps for r in self.conn.execute(q, {"step": int(s)}).get_all()]
        return aligned(rows, self.node_ids, 1)

    def degree(self):
        return np.hstack([self.per_step("in-degree"), self.per_step("out-degree")])

    def two_hop(self):
        return self.per_step("two-hop-size")

    def neighbour_scores(self):
        return aligned(self.conn.execute(graph_store.query("neighbour-scores")).get_all(), self.node_ids, 4)

    def pagerank(self):
        for statement in graph_store.statements("pagerank-setup"):
            self.conn.execute(statement)
        iterate = graph_store.statements("pagerank-iterate") + [graph_store.query("pagerank-commit")]
        for _ in range(graph_store.PAGERANK_ITERATIONS):
            for statement in iterate:
                self.conn.execute(statement, {"damping": graph_store.DAMPING} if "$damping" in statement else None)
        return aligned(self.conn.execute("MATCH (t:Tx) RETURN t.node_id, t.pr").get_all(), self.node_ids, 1)


class DuckDB:
    name = "DuckDB (columnar store, SQL)"

    def __init__(self, con, node_ids, steps):
        self.con, self.node_ids, self.steps = con, node_ids, steps

    def per_step(self, name: str) -> np.ndarray:
        q = sql(name)
        rows = [r for s in self.steps for r in self.con.execute(q, {"step": int(s)}).fetchall()]
        return aligned(rows, self.node_ids, 1)

    def degree(self):
        return np.hstack([self.per_step("in-degree"), self.per_step("out-degree")])

    def two_hop(self):
        return self.per_step("two-hop-size")

    def neighbour_scores(self):
        return aligned(self.con.execute(sql("neighbour-scores")).fetchall(), self.node_ids, 4)

    def pagerank(self):
        self.con.execute(sql("pagerank-setup"))
        iterate = sql("pagerank-iterate")
        for _ in range(graph_store.PAGERANK_ITERATIONS):
            self.con.execute(iterate, {"damping": graph_store.DAMPING})
        return aligned(self.con.execute("SELECT node_id, pr FROM pr").fetchall(), self.node_ids, 1)


WORKLOADS = {
    "degree": "Aggregation: in- and out-degree, same-step neighbours only, one query per step for each",
    "two_hop": "Traversal: distinct transactions within two hops, ignoring direction, one query per step",
    "neighbour_scores": "Aggregation over a join: mean and maximum neighbour score, both directions, whole graph",
    "pagerank": "Iterative: PageRank within each step, 100 fixed iterations, whole graph",
}


def timed(fn):
    started = time.perf_counter()
    out = fn()
    return out, time.perf_counter() - started


def max_difference(a: np.ndarray, b: np.ndarray) -> float:
    if not np.array_equal(np.isnan(a), np.isnan(b)):
        return float("inf")
    both = ~np.isnan(a)
    return float(np.max(np.abs(a[both] - b[both]))) if both.any() else 0.0


def sysctl(name: str) -> str | None:
    out = subprocess.run(["sysctl", "-n", name], capture_output=True, text=True)
    return out.stdout.strip() or None


def main() -> None:
    threads = int(os.environ.get("OMP_NUM_THREADS") or os.cpu_count())
    with duckdb.connect(str(COLUMNAR_STORE), read_only=True) as con:
        nodes_file, edges_file = graph_store.export(con, STAGING)
        node_ids, steps = (np.array(x) for x in zip(*con.execute(
            "SELECT node_id, time_step FROM nodes ORDER BY node_id").fetchall()))
    scores = np.random.default_rng(SCORE_SEED).random(len(node_ids))

    db, conn = graph_store.build(LADYBUG_PATH, nodes_file, edges_file)
    conn = ladybug.Connection(db, num_threads=threads)
    graph_store.load_scores(conn, node_ids, scores, STAGING)
    lbug_version = conn.execute("CALL db_version() RETURN *").get_all()[0][0]

    graph_store.reset(DUCKDB_PATH)
    duck = duckdb.connect(str(DUCKDB_PATH))
    duck.execute(f"SET threads = {threads}")
    duck.execute(f"CREATE TABLE nodes AS SELECT * FROM '{nodes_file}'")
    duck.execute(f"CREATE TABLE edges AS SELECT * FROM '{edges_file}'")
    duck.execute("CREATE TABLE scores AS SELECT unnest(?::BIGINT[]) AS node_id, unnest(?::DOUBLE[]) AS score",
                 [node_ids.tolist(), scores.tolist()])

    unique_steps = np.unique(steps)
    engines = {"ladybug": Ladybug(conn, node_ids, unique_steps), "duckdb": DuckDB(duck, node_ids, unique_steps)}
    out = {}
    for workload, description in WORKLOADS.items():
        first, results = {}, {}
        for key, engine in engines.items():
            results[key], first[key] = timed(getattr(engine, workload))
        diff = max_difference(results["ladybug"], results["duckdb"])
        if not diff <= TOLERANCE:
            raise SystemExit(f"{workload}: engines disagree by {diff}; timings would compare different work")
        repeats = {key: [] for key in engines}
        for r in range(REPEATS):
            order = list(engines) if r % 2 == 0 else list(reversed(engines))
            for key in order:
                repeats[key].append(timed(getattr(engines[key], workload))[1])
        out[workload] = {
            "description": description,
            "max_difference_between_engines": diff,
            "seconds": {key: {"first_run": round(first[key], 3),
                              "median_of_repeats": round(statistics.median(repeats[key]), 3),
                              "repeats": [round(x, 3) for x in repeats[key]]} for key in engines},
            "ratio_ladybug_to_duckdb": statistics.median(repeats["ladybug"]) / statistics.median(repeats["duckdb"]),
        }
        print(f"{workload}: LadybugDB {out[workload]['seconds']['ladybug']['median_of_repeats']}s, "
              f"DuckDB {out[workload]['seconds']['duckdb']['median_of_repeats']}s")
    edges = int(duck.execute("SELECT count(*) FROM edges").fetchone()[0])
    duck.close()

    write_result("engine-comparison", {
        "workloads": out,
        "graph": {"nodes": int(len(node_ids)), "edges": edges, "time_steps": int(len(unique_steps))},
        "configuration": {
            "engines": {"ladybug": {"name": Ladybug.name, "version": lbug_version},
                        "duckdb": {"name": DuckDB.name, "version": duckdb.__version__}},
            "threads": threads,
            "repeats": REPEATS,
            "storage": "Both file-based and on the same disk, loaded from the same Parquet export; default settings",
            "result_format": "Rows fetched as Python tuples in both engines; fetch time is included",
            "queries": "graph/queries/*.cypher and graph/sql/*.sql",
        },
        "machine": {
            "cpu": sysctl("machdep.cpu.brand_string") or platform.processor(),
            "performance_cores": sysctl("hw.perflevel0.physicalcpu"),
            "memory_bytes": sysctl("hw.memsize"),
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "confounds": [
            "The graph is small, so start-up, query planning and Python-side fetching are a large share of each time.",
            "Repeats run in the same process after a first run, so caches are warm; first runs are reported separately.",
            "Each query was written once, in the plainest form for its language, and was not tuned for either engine.",
            "PageRank in the graph store writes node properties with four statements per iteration; in SQL each "
            "iteration replaces one table. The shapes differ because the languages do.",
            "Per-step workloads issue one query per step in both engines, as Arm B does.",
        ],
        "does_not_establish": "Anything about production economics, concurrency, ingest, larger graphs or other "
                              "engines. It records how these query shapes behaved on one small static graph, on "
                              "one laptop.",
    })


if __name__ == "__main__":
    main()
