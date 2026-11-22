# Coverage matrix

[in review]

Which failure modes each check catches, which nothing catches yet, and what the checks cost to run. The structure follows the coverage matrix in the AI Evals course (`igoko-consulting/ai-evals`, 05-scale). The modes come from [failure-taxonomy.md](failure-taxonomy.md) and from the risks the README names as untested. Written on 2026-11-22 from the code and the record.

## Coverage

| Failure mode | Caught by | Coverage | Gap |
|---|---|---|---|
| Contaminated baseline | Arm A's feature list asserted in code; `tests/test_feature_contract.py` | Covered | None known |
| A changed pre-registration | Gate 1; `tests/test_prereg_gate.py` | Covered | None known |
| Temporal leakage | Gate 2's future-edge test, every build | Partial | The tests run one reference configuration at the full training-label budget (README caveat). Gate 2's decision rule has no unit test of its own; it is exercised only by full runs |
| Label-derived leakage | Gate 2's label-shuffle and own-label tests | Partial | As above |
| Selection on test steps | The protocol code; k computed before any test step is read | Gap | No test fails if a later change reads a test step during tuning |
| Noise read as a win | Bootstrap intervals; generated wording that applies red line 6 | Partial | The intervals leave out seed-to-seed variation and may be too narrow (README caveat); hand-written text relies on review |
| Results that do not reproduce | Clean-clone reruns; pinned versions; data checked against pinned checksums | Partial | Run on one machine type; the Kaggle route has never run, so the mirror is not yet confirmed against the publisher's copy (`04-the-data/NOTES.md`) |
| Figures typed by hand | Value spans and generated blocks filled from `results/` | Partial | Hand-written prose outside generated blocks relies on review |
| Wrong facts in an evidence chain | Every fact rechecked in SQL against the columnar store | Covered | None known |
| Chains that would not help an investigator | The author's review sample; the blind second scorer ([judge-calibration.md](judge-calibration.md)) | Gap until scored | Not yet scored; one human scorer |
| Claims beyond the dataset | The honesty rules in `CLAUDE.md`; caveats beside each claim; a cold-reader review | Partial | No automated check |
| Adversarial behaviour, cold start, camouflage | Nothing | Gap | Deferred to Phase 5 |
| Findings that do not hold on another dataset | Nothing | Gap | Deferred to Phase 5 |
| A change merged without the checks | `make test` and clean-clone checks, run by hand | Partial | No continuous integration; deferred in the PRD |

## What runs today, and what it costs

- **Every `make all`:** the unit tests first, then Gate 1 before each write and Gate 2 before each feature-derived write. The tests and the gates are small beside the rest of the run.
- **At each phase gate and before a published update:** a clean-clone run of `make all`. This is almost the whole cost, because it tunes every arm at every label budget. Its duration is in `results/pipeline-runtime.json` and the README.
- **By hand:** review of hand-written text, and the author's evidence-chain scores.

## Accepted gaps

- **Adversarial behaviour and a second dataset.** Deferred to Phase 5. The dataset is static, so adversarial tests would need a design of their own, and a second dataset is the Phase 5 extension. The README states both beside the claims they limit.
- **No continuous integration.** Deferred in the PRD. A solo lab with every run started by hand loses little from it today; the cost is that a check skipped by hand would go unnoticed.

## Critical gap

- **Red line 4 has no failing test.** Red lines 1 to 3, which protect the experiment, are enforced in code, with tests. Red line 4 protects it just as much. "No threshold, hyperparameter or operating point is ever selected on test steps" holds by design, and the audit found no breach, but a later change that read a test step during tuning would pass every check. A test that runs tuning with test-step labels hidden, and fails if they are read, would close it. Proposed, not built: building it is a code change outside this page.
