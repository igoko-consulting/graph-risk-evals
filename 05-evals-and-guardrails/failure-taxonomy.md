# Failure taxonomy

[in review]

Every failure found in this repository so far, grouped by mode, with how it was found and what now catches it. The structure follows the failure discovery work in the AI Evals course (`igoko-consulting/ai-evals`, 02-failure-discovery): checks are written for failures that happened, not for ones imagined.

| Mode | What happened | Found by | Caught now by | Record |
|---|---|---|---|---|
| Contaminated baseline | PRD v1's Arm A used every node feature, including the one-hop neighbour aggregates, so it was never graph-free and H1 was wrong by construction | Cross-model review of PRD v1 | Arm A's feature list is asserted in code and checked by the feature contract test | `docs/prd-review.md`; `tests/test_feature_contract.py` |
| Label-derived leakage | A hop-distance-to-a-known-bad-actor feature could read labels from the very test step it scored | Cross-model review of PRD v1 | The feature was removed; Gate 2's label-shuffle and own-label tests | `docs/prd-review.md`; `00-build/leakage_gate.py` |
| Leakage through a global rule | PageRank's first stopping rule let a change in one time step alter how many iterations every other step got | Fixing the protocol, before any arm ran | A fixed iteration count; Gate 2's future-edge test | `change_log.md`, 2026-11-19 protocol entry |
| Unclaimed prior work | The headline comparison was already published, and PRD v1 did not say so | Cross-model review of PRD v1 | The PRD's prior-results section; the citation in the generated README text | `prds/prd-v2.md`; `change_log.md`, audit follow-up |
| Untestable predictions | PRD v1's hypotheses rested on "majority", "enough", "less" and "noise band" without definitions, so no result could falsify them | Both models in the cross-model review of PRD v1 | Numeric definitions in the pre-registration, locked by Gate 1 | `docs/prd-review.md`, where both models agreed |
| A gate weaker than its rule | Gate 2 dropped any feature that moved and still passed, which is more than the pre-registration allows | Independent audit, after publication | Gate 2 now fails on any movement under the future-edge or label-shuffle test | `change_log.md`, audit fixes and Gate 2 entries |
| Figures typed by hand | Assumptions, counts and settings were typed into prose, where they could drift from the run | Independent audit | Value spans and generated blocks filled from `results/`; the renderer refuses to claim equal tuning if the arms differ | `change_log.md`, audit fixes |
| Text claiming more than the code | The README said no result is written if any test fails; k was described as computed from the wrong steps; a smoke-run disclosure understated what was known | Independent audit and its review | Corrected text, and caveats placed beside each claim | `change_log.md`, audit follow-up and its review |
| Exact claims that do not reproduce | Values below the leakage tolerance differ between identical runs, so a claim of exactly zero movement would not survive a rerun | Overnight clean-clone rerun | The leakage sentence always states the tolerance | Commits `48b2fdf` and `8970cd1` |
| Checks removed by optimisation | Bare `assert` statements would vanish under `python -O` | Audit follow-up | `require()` calls, which Python does not strip | `change_log.md`, audit follow-up |

**What the pattern shows.** The most damaging failures (the contaminated baseline, label leakage, unclaimed prior work) were found by review before any code existed. The audit after publication found weaker gates and drifting text rather than wrong results: no audit finding changed a published result.

**What nothing catches yet** is listed in [coverage-matrix.md](coverage-matrix.md).
