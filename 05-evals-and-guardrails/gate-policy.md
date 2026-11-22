# Gate policy

[in review]

What blocks a result, a phase or a publication in this repository, and who can override it. The structure follows the eval gates in the AI Evals course (`igoko-consulting/ai-evals`, 04-eval-gates).

## Gates in code: nobody overrides them

- **Gate 1, the pre-registration.** Before any write to `results/`, `00-build/prereg_gate.py` hashes `01-the-bet/pre-registration.md` and compares it with the commit tagged `prereg-v1`. A mismatch halts the run. The only way past it is a new pre-registration, committed on its own and tagged; a tagged commit is never amended (CLAUDE.md, Commits).
- **Gate 2, leakage.** A result built from model feature values is written only if the leakage gate passed at the current commit, on the same data (`00-build/results_io.py`). The gate fails if any feature moves under the future-edge or label-shuffle test by more than the tolerance recorded in `results/leakage-tests.json`. A two-stage score aggregate that moves under the own-label flip alone is dropped, which is the remedy the pre-registration allows.
- **No selection on test steps.** Thresholds, hyperparameters and k come from training and validation steps only (red line 4), and k is computed before any test step is read.

## Rules applied when writing: the author enforces them

- **No win inside the noise band.** A difference whose bootstrap interval includes zero is reported as not separable (red line 6). The generated text applies the rule, and no hand-written text may call such a difference a win.
- **Kill criteria.** From the pre-registration: if Arm B does not beat Arm A outside the noise band, publish that and do not build Arm D; if every arm falls within the noise band of the others, report the comparison as underpowered; if the thin slice is not working at the end of the first session, ship a method write-up. The Phase 2 criterion is reported, not enforced by the pipeline.
- **Phase gates.** No phase starts before the previous one's gate passes (CLAUDE.md, Build order), and each gate includes a run from a clean clone.
- **Publication.** An update to published results needs every non-timing figure to reproduce on a clean clone. When the overnight rerun moved two values below the tolerance, publication waited until the wording no longer depended on them (commits `48b2fdf` and `8970cd1`).

## Who decides

- **The author** signs off each phase, removes `[in review]` markers and decides interpretation.
- **A build session** stops and asks when a red line blocks the work, the data differs from the PRD, a kill criterion fires, an open question blocks implementation, or an assumption would change a result (CLAUDE.md, When to stop and ask).
- **Overrides** of the writing rules are recorded as dated entries in `change_log.md` with their reason. The code gates have no override path.

The Phase 4 decision under this policy is in [ship-hold-memo.md](ship-hold-memo.md).
