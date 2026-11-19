# 00-build: pipeline, loaders, features, arms, evaluation

## Running it

`make all` on a clean clone. It needs either [uv](https://docs.astral.sh/uv/), which fetches the pinned Python itself, or Python 3.13 on the path as `python3.13`.

| Target | What it does |
|---|---|
| `make all` | Tests, then fetch and load, then every pipeline stage in order |
| `make data` | Fetch, verify checksums, load the columnar store, check the schema contract |
| `make test` | Unit tests: pre-registration gate and feature-group contract |
| `make clean` | Remove derived stores and caches; keeps the downloaded data |
| `make distclean` | Also remove downloaded data and the virtual environment |
| `make lock` | Re-pin `requirements.txt` from `requirements.in` with nothing newer than `EXCLUDE_NEWER` |

## Stage order, and why it is fixed

1. `fetch_data.py`: fetch, verify SHA-256, load `data/store/elliptic.duckdb`, validate the contract.
2. `compute_k.py`: k from steps 1 to 34 only. Every later stage that reads test steps calls `protocol.require_k_first()`, so k is always computed before any test step is read.
3. `class_balance.py`: labels per time step.
4. `day_one_checks.py`: counts against the PRD, feature split, cross-step edges. Writes the generated block in `04-the-data/NOTES.md` from `results/`.
5. `build_graph_store.py`: per-step graphs in LadybugDB, in-degree via `graph/queries/in-degree.cypher`, checked node by node against the columnar store.
6. `render_charts.py`: static SVG charts from `results/` only.

## The two gates

- **Gate 1, pre-registration.** `prereg_gate.py` hashes `01-the-bet/pre-registration.md` and compares it with the file in the commit tagged `prereg-v1`, which must be an annotated tag. Every write to `results/` goes through `results_io.write_result`, which runs the gate first. Tests in `tests/test_prereg_gate.py` prove it refuses an edited file, a whitespace change, a missing or lightweight tag and a deleted file, and that nothing is written when it refuses. A GitHub zip download has no tags, so the gate fails there by design.
- **Gate 2, leakage.** Not built yet; there are no model features to test. `write_result(..., uses_model_features=True)` refuses until it exists.

## Friction and findings

- **Kùzu to LadybugDB.** Kùzu is archived. LadybugDB 0.19.0 onwards links Homebrew's OpenSSL on macOS and fails to load without it, so 0.18.3 is pinned. Surfacing this on day one rather than in Phase 2 is the point of the thin slice.
- **Gradient-boosted trees on a stock Mac.** LightGBM and XGBoost need Homebrew's `libomp`. scikit-learn's histogram gradient boosting does not, so Arms A and B use it.
- **Layout.** Pipeline code lives here as scripts with snake_case names, because Python cannot import a hyphenated module. `PYTHONPATH` is set by the Makefile and `pytest.ini`. Artefacts keep kebab-case names.
- **One graph database, not 49.** Each per-step graph is the set of nodes sharing a `time_step` property; queries take the step as a parameter. With no cross-step edges this is equivalent to separate graphs and far simpler to load.
- **Deterministic chart output.** Charts use matplotlib's bundled font, text drawn as paths and a fixed SVG hash salt, so a rerun on any machine produces the same bytes and diffs only show real changes.
