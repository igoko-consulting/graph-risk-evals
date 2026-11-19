# Change log

Dated decisions. Figures live in `results/`; this file points to them rather than repeating them.

## 2026-11-19, session 1

**Graph store: LadybugDB 0.18.3, not Kùzu.** Kùzu was archived in October 2025 and its final release, 0.11.3, has no macOS arm64 build for Python 3.14. LadybugDB is the maintained fork, MIT licensed, with the same Cypher dialect, so queries in `graph/queries/` stay portable. 0.19.0 onwards ship macOS builds that link Homebrew's OpenSSL, which fails on a Mac without Homebrew, so 0.18.3 is pinned as the newest self-contained release. Revisit when a later release drops that dependency.

**Python 3.13.18, managed by uv.** Pinned in `.python-version`. 3.13 has wheels for every library in the planned stack. All dependency versions were released on or before 2026-11-05, at least two weeks before pinning, enforced with `uv pip compile --exclude-newer` (`make lock`).

**Data fetched from the PyTorch Geometric mirror for now.** No Kaggle token was available. SHA-256 checksums of the three CSV files are pinned in `loaders/elliptic.py`. The loader prefers Kaggle when a token exists and holds both routes to the same checksums, so the first Kaggle fetch verifies the mirror against the publisher's copy. Until then that verification is outstanding.

**Licence handling.** The dataset is CC BY-NC-ND 4.0. Data is never committed, and `results/` holds aggregate figures only, never per-node features, scores or labels. Recorded in `04-the-data/NOTES.md`.

**Arm A uses 93 features.** The PRD says Arm A uses "the 94 local features only, with the time-step column excluded". The dataset paper counts the time step among the 94 local features, and the PRD's own Phase 5 section says "93 local". Arm A therefore uses the 93 local features that remain once the time step is excluded. This clarifies the wording; it does not change any hypothesis or the intent of red line 3. Confirmed by the author before the data was loaded.

**Cross-step edges: none.** Answered on day one from the data, see `results/day-one-checks.json`. Time steps are disjoint graphs, so the leakage analysis in the PRD stands as written.

**Leakage gate status.** The future-edge and label-shuffle tests do not exist yet because no model features exist yet. `00-build/results_io.py` refuses to write any result flagged as using model features until they do. Session 1 results use labels and graph structure only.

**Library finding for Phase 2.** LightGBM 4.7.0 and XGBoost 3.4.1 install on macOS but fail to load without Homebrew's `libomp`. scikit-learn 1.9.1's histogram gradient boosting, torch 2.15.0 and torch-geometric 2.8.1 all load and run on Python 3.13 CPU with no system dependencies. The gradient-boosted tree library is chosen in Phase 2; a clean clone on a stock Mac is the constraint.

### Errata to the pre-registration

The pre-registration is hashed and tagged, so it cannot be corrected in place. These are recorded here before any arm has run.

1. **Specification version.** It cites `prds/prd-v2.md` v2.3. The PRD was at v2.4 when the tag was made. v2.4 added requirement traceability to the architecture table and pointed the junction diagram at the pre-registration for thresholds. No hypothesis, definition, period or kill criterion differs between the two.
2. **Tuning parity names two arms.** The protocol commitments say "Arms A and D receive the same tuning search method...". The PRD tuning contract says the protocol is identical across arms. It is read as applying to every arm, A, B and D.

### Open before Phase 2

- **Integer rule for k.** The pre-registration defines k as a mean, which is not a whole number (`results/k.json`). A top-k queue needs a whole number. The rounding rule must be fixed and recorded here before any arm is evaluated, without reference to test-step data.
- **Analyst cost per alert.** Still open, as the pre-registration records.
- **Two-stage predicted-score aggregation.** Leakage design and test still to be written before Arm B runs.
