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
6. `leakage_gate.py`: Gate 2, before any arm is tuned. Computes every Arm B feature in the graph store, then recomputes it under a future edge, a test-label shuffle and an own-label flip.
7. `run_arms.py`: Arm A tuned per seed; its model becomes stage one for Arm B's score aggregates; Arm B tuned per seed. Per-node scores stay in `data/store/runs/` and are never published.
8. `evaluate_arms.py`: precision at k, PR-AUC, paired bootstrap, the kill-criterion verdict.
9. `run_arm_d.py`: two-layer GraphSAGE (`arm_d.py`) tuned per seed, trained on the training-step subgraph only.
10. `evaluate_phase3.py`: all three arms on the same bootstrap resamples as Phase 2; H1, H2, H3; modelled cost per true positive.
11. `render_charts.py` and `render_readme.py`: charts and README blocks from `results/` only. They run twice, so the headline is published before the label-budget curve finishes.
12. `run_label_budgets.py`: every arm re-tuned at 5, 10, 25 and 50 percent of training labels.
13. `evaluate_label_budgets.py`: the curve and H4, on the same resamples again.

## The two gates

- **Gate 1, pre-registration.** `prereg_gate.py` hashes `01-the-bet/pre-registration.md` and compares it with the file in the commit tagged `prereg-v1`, which must be an annotated tag. Every write to `results/` goes through `results_io.write_result`, which runs the gate first. Tests in `tests/test_prereg_gate.py` prove it refuses an edited file, a whitespace change, a missing or lightweight tag and a deleted file, and that nothing is written when it refuses. A GitHub zip download has no tags, so the gate fails there by design.
- **Gate 2, leakage.** `leakage_gate.py` writes `results/leakage-tests.json`. `write_result(..., uses_model_features=True)` refuses unless that file says the gate passed at the current commit on the current data. Any feature that moves under a perturbation is dropped from Arm B. A perturbation with no visible effect anywhere invalidates the test and halts the build.

## Friction and findings

- **Kùzu to LadybugDB.** Kùzu is archived. LadybugDB 0.19.0 onwards links Homebrew's OpenSSL on macOS and fails to load without it, so 0.18.3 is pinned. Surfacing this on day one rather than in Phase 2 is the point of the thin slice.
- **Gradient-boosted trees on a stock Mac.** LightGBM and XGBoost need Homebrew's `libomp`. scikit-learn's histogram gradient boosting does not, so Arms A and B use it.
- **Layout.** Pipeline code lives here as scripts with snake_case names, because Python cannot import a hyphenated module. `PYTHONPATH` is set by the Makefile and `pytest.ini`. Artefacts keep kebab-case names.
- **Every traversal is scoped to the node's own step.** Without the `time_step` filters, a single injected cross-step edge would change an earlier node's degree, PageRank, two-hop size and score aggregates. The two-hop query filters intermediate nodes too, using LadybugDB's recursive-pattern predicate; filtering only the endpoints would let a path run through a future node.
- **PageRank in Cypher is the slowest graph-store stage.** Four statements per iteration over every node, 100 fixed iterations, with no built-in algorithm used. Kept in the graph store as the PRD requires. Its cost against a library implementation is not measured here; that belongs to the engine comparison appendix in Phase 4. The gate's total time is in `results/leakage-tests.json`.
- **Two-hop size is the most expensive single query**, because it is a variable-length pattern.
- **CPU-only PyTorch without dependency confusion.** Listing PyTorch's CPU index as an extra index for every package made `certifi` resolve to an older copy hosted there. `uv pip sync --torch-backend cpu` consults that index for PyTorch packages only. The pip fallback in the Makefile uses `--extra-index-url`, which picks the newest match across indexes, so it is unaffected. The Linux route has not been run on a Linux machine.
- **Arm D is deterministic on CPU.** `torch.use_deterministic_algorithms(True)` costs nothing measurable here, and repeated fits give identical scores, so seed spread for D reflects tuning and initialisation only.
- **One graph database, not 49.** Each per-step graph is the set of nodes sharing a `time_step` property; queries take the step as a parameter. With no cross-step edges this is equivalent to separate graphs and far simpler to load.
- **Deterministic chart output.** Charts use matplotlib's bundled font, text drawn as paths and a fixed SVG hash salt, so a rerun on any machine produces the same bytes and diffs only show real changes.
