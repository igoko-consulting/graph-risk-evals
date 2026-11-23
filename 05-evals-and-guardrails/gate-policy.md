# Gate policy

[in review]

What blocks a result, a phase or a publication in this repository, and who can override it. The structure follows the CI gate policy in the AI Evals course (`igoko-consulting/ai-evals`, 04-eval-gates). There is no continuous integration here (deferred in the PRD), so "hard" means the code halts the run, not that a pull request is blocked. Written on 2026-11-22 from the code in `00-build/` and the record.

## Gates and their last result

| Check | Method | Gate | Fails when | Last result |
|---|---|---|---|---|
| Unit tests | `make test`, which `make all` runs before anything else | Hard | Any test fails | Passed when this page was written |
| Gate 1, the pre-registration | `00-build/prereg_gate.py`: SHA-256 of `01-the-bet/pre-registration.md` against the same file in the commit tagged `prereg-v1`, run by `results_io.write_result` before every write to `results/` | Hard | The hashes differ; the tag is missing or not annotated; the file is missing | Every result file records the tag commit and the hash it matched |
| Gate 2, leakage | `00-build/leakage_gate.py` runs the future-edge, label-shuffle and own-label tests; `results_io.py` refuses any feature-derived result unless the gate passed at the current commit, on the same data | Hard | Any feature moves beyond the tolerance under the future-edge or label-shuffle test; Arm D's reference scores move; the shuffle changed no label, so tested nothing; the gate ran at another commit or on other data | Passed; nothing dropped (`results/leakage-tests.json`) |
| Own-label flip | Part of Gate 2 | Remedy, not a halt | A two-stage score aggregate moves under this test alone: it is dropped, as the pre-registration allows | Nothing dropped |
| No selection on test steps | k computed from training and validation steps before any test step is read; tuning on validation steps only (red line 4) | Hard by design | Not tested: see [coverage-matrix.md](coverage-matrix.md) | No breach recorded |
| No win inside the noise band | Generated wording in `render_readme.py` calls a difference only when its interval excludes zero (red line 6) | Hard for generated text; review for hand-written text | A hand-written sentence calls such a difference a win | None found by the audit |
| Equal tuning claimed | The renderer checks trial and seed counts before saying the arms were tuned equally | Hard for generated text | The counts differ | Counts equal (`change_log.md`, 2026-11-20 audit fixes) |
| Phase 2 kill criterion | `evaluate_arms.py` writes `kill_criterion` to `results/evaluation-arms-a-b.json` | Advisory: reported, not enforced by the pipeline | The interval on Arm B minus Arm A does not lie wholly above zero | Did not fire, so Arm D was built (`change_log.md`, 2026-11-19 Phase 2 result) |
| Reproduction | `make all` on a clean clone, at each phase gate and before a published update | Publication gate, run by hand | Any non-timing figure differs beyond the stated tolerance | Reproduced (commit `8970cd1`) |

## Which checks are hard, and why

- **Gate 1 and Gate 2 have no override path.** They are the repository's central claim: a result written after the hypotheses moved, or on leaky features, would be worthless however good it looked. The only way past Gate 1 is a new pre-registration, committed on its own and tagged; a tagged commit is never amended (`CLAUDE.md`, Commits).
- **Generated wording is hard because it cannot be argued with mid-build.** The rule is applied by code before anyone has seen the number.

## Which are advisory, and why that is safe

- **The Phase 2 kill criterion.** Building Arm D is a decision, and the criterion's outcome is written to `results/` before Arm D runs, so a reader can check it was honoured. What is missed: nothing stops a future session building Arm D after the criterion fires, other than the written rule.
- **Hand-written text.** Red lines 5 to 7 bind prose outside the generated blocks, and only review checks it. The audit found faults of exactly this kind, which is why this stays a known gap rather than a solved one.

## Who decides

- **The author** signs off each phase, removes `[in review]` markers and decides interpretation.
- **A build session** stops and asks when a red line blocks the work, the data differs from the PRD, a kill criterion fires, an open question blocks implementation, or an assumption would change a result (`CLAUDE.md`, When to stop and ask).
- **Changes to a rule** are recorded as dated entries in `change_log.md` with their reason, as when Gate 2 was tightened at the author's request on 2026-11-20.

The Phase 4 decision under this policy is in [ship-hold-memo.md](ship-hold-memo.md).
