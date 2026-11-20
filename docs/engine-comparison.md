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
_Populated when the engine-comparison stage runs._
<!-- end generated:engine-comparison -->
