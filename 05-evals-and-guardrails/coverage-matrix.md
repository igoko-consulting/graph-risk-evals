# Coverage matrix

[in review]

Which failure modes each check catches, and which nothing catches yet. The structure follows the coverage matrix in the AI Evals course (`igoko-consulting/ai-evals`, 05-scale). The modes come from [failure-taxonomy.md](failure-taxonomy.md) and from the risks the README names as untested.

| Failure mode | Caught by | Gap |
|---|---|---|
| Contaminated baseline | Arm A's feature list asserted in code; `tests/test_feature_contract.py` | None known |
| Temporal leakage | Gate 2's future-edge test | The tests use one reference model trained on every training label (README caveat) |
| Label-derived leakage | Gate 2's label-shuffle and own-label tests | As above |
| A changed pre-registration | Gate 1 | None known |
| Selection on test steps | The protocol code, and k computed before test steps are read | No test fails if a later change reads a test step during tuning |
| Noise read as a win | Bootstrap intervals; generated wording that applies red line 6 | The intervals leave out seed-to-seed variation and may be too narrow (README caveat) |
| Results that do not reproduce | Clean-clone reruns; pinned versions; data checked against pinned checksums | Runs on one machine type; the Kaggle route is untested |
| Figures typed by hand | Value spans and generated blocks filled from `results/` | Hand-written prose outside generated blocks relies on review |
| Wrong facts in an evidence chain | Every fact rechecked in SQL against the columnar store | None known |
| Chains that would not help an investigator | The author's review sample; the blind second scorer ([judge-calibration.md](judge-calibration.md)) | Not yet scored; one human scorer |
| Claims beyond the dataset | The honesty rules in CLAUDE.md; caveats beside each claim; a cold-reader review | No automated check |
| Adversarial behaviour, cold start, camouflage | Nothing | Deferred to Phase 5 |
| Findings that do not hold on another dataset | Nothing | Deferred to Phase 5 |
| A change merged without the checks | `make test` and clean-clone checks, run by hand | No continuous integration; deferred in the PRD |

**What the checks cost.** Almost all of it is the clean-clone run, which tunes every arm at every label budget; its duration is in `results/pipeline-runtime.json` and the README. The unit tests and the leakage gate are small beside it.
