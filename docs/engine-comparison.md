# Engine comparison appendix

_Draft for the author to edit. Timeboxed to half a day, as the specification requires._

## What it asks

How do Arm B's four graph workloads behave as queries in an embedded graph store (LadybugDB, Cypher) and in an embedded columnar store (DuckDB, SQL), on this dataset?

Both reviews of the specification recommended cutting this appendix, because at this size it largely times start-up, caching and query planning rather than anything architectural. It was kept on purpose: working knowledge of how traversal and aggregation workloads behave on different engines is a stated objective of this lab. That reasoning is recorded in `prds/prd-v2.md`. It is not a headline result and nothing in the README's decision matrix depends on it.

## Method

- **Same work in both engines.** The Cypher queries are the ones Arm B uses, in `graph/queries/`. The SQL equivalents are in `graph/sql/`, written once and not tuned. Each workload's outputs must agree across engines before its timings are kept; the run halts if they do not.
- **Same conditions.** Both stores are file-based and built from the same Parquet export, in the same process, with the same thread count. Rows come back as Python tuples in both, and fetch time is included.
- **First run reported separately.** Then repeats, with the engine order alternated between repeats, and the median kept.
- **No model output.** The neighbour-score workload uses seeded random scores, so this stage needs no trained arm and no leakage gate.

`00-build/engine_comparison.py` runs it as part of `make all`.

## Results

<!-- generated:engine-comparison by 00-build/render_readme.py from results/; do not edit by hand -->
| Workload | What it does | LadybugDB, median (first run) | DuckDB, median (first run) | LadybugDB time ÷ DuckDB time | Largest output difference |
|---|---|---|---|---|---|
| Degree | Aggregation: in- and out-degree, same-step neighbours only, one query per step for each | 4.97s (5.05s) | 0.45s (0.51s) | 11.0 | 0 |
| Two-hop size | Traversal: distinct transactions within two hops, ignoring direction, one query per step | 11.44s (11.59s) | 0.45s (0.48s) | 25.6 | 0 |
| Neighbour scores | Aggregation over a join: mean and maximum neighbour score, both directions, whole graph | 0.56s (0.54s) | 0.24s (0.24s) | 2.3 | 5e-16 |
| PageRank | Iterative: PageRank within each step, 100 fixed iterations, whole graph | 129.25s (129.66s) | 3.18s (3.19s) | 40.7 | 6e-17 |

**What it showed.** On every workload here the columnar store was faster, by 2.3 to 40.7 times, with the widest gaps on PageRank and two-hop size.

203,769 transactions, 234,355 edges, 49 time steps. LadybugDB (graph store, Cypher) 0.18.3; DuckDB (columnar store, SQL) 2.0.0. 6 threads in both, 3 repeats after a first run, engine order alternated between repeats. Both file-based and on the same disk, loaded from the same Parquet export; default settings. Rows fetched as Python tuples in both engines; fetch time is included. Machine: Apple M3 Pro, 6 performance cores, 36 GB, macOS-27.0.1-arm64-arm-64bit-Mach-O, Python 3.13.18.

**Confounds.**

- The graph is small, so start-up, query planning and Python-side fetching are a large share of each time.
- Repeats run in the same process after a first run, so caches are warm; first runs are reported separately.
- Each query was written once, in the plainest form for its language, and was not tuned for either engine.
- PageRank in the graph store writes node properties with four statements per iteration; in SQL each iteration replaces one table. The shapes differ because the languages do.
- Per-step workloads issue one query per step in both engines, as Arm B does.

**What this does not establish.** Anything about production economics, concurrency, ingest, larger graphs or other engines. It records how these query shapes behaved on one small static graph, on one laptop.

Source: `results/engine-comparison.json`.
<!-- end generated:engine-comparison -->
