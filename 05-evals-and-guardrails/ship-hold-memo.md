# Ship or hold: the Phase 4 gate

[in review]

> **Decision: HOLD**, until the author's review is done. Recommended on 2026-11-22; the decision is the author's.

The form follows the ship-hold memo in the AI Evals course (`igoko-consulting/ai-evals`, 06-culture), under the rules in [gate-policy.md](gate-policy.md). "Ship" here means the author signs off Phase 4 and the write-up loses its `[in review]` markers. The results are already public.

## The answer

Hold the Phase 4 sign-off until the author has edited every item marked `[in review]` and scored the evidence-chain sample, because the numbers are reproduced but the interpretation around them is not yet the author's, and the one human check on whether the evidence chains help an investigator has not happened.

## The arguments

1. **The numbers are ready; the words are not.** Every result passed Gate 1 and Gate 2, and the last clean-clone rerun reproduced every non-timing figure within the stated tolerance (commit `8970cd1`). The prose that interprets them is marked `[in review]`, and the README tells readers so.
2. **The evidence chains are checked for truth, not usefulness.** Every fact in them was recomputed in SQL and none disagreed. Whether a chain is sufficient and actionable needs a person, and the sample is unscored. The blind second score waits on it ([judge-calibration.md](judge-calibration.md)).
3. **Holding costs little.** This is a learning project with no user waiting on a release. The results are public and reproduce; what the hold delays is the claim that the write-up is final.

## Next step: decision needed

The author, in this order:
1. Edit or accept each `[in review]` item, including the pages added on 2026-11-22.
2. Score the evidence-chain sample and run `make review`; then the blind model score and a second `make review`.
3. Run a clean-clone check that leaves the tree unchanged.
4. Sign off Phase 4, or record in `change_log.md` why not.

## Evidence

| Check | Status | Source |
|---|---|---|
| Gate 1, pre-registration | Passed for every result | Provenance in each `results/*.json` |
| Gate 2, leakage | Passed; nothing dropped | `results/leakage-tests.json` |
| Clean-clone reproduction | Every non-timing figure reproduced within tolerance | Commit `8970cd1` |
| Evidence-chain facts | All recomputed in SQL; none disagreed | README, Evidence chains |
| Evidence-chain usefulness | Not yet scored | `results/evidence-chain-review.json` |
| Author's edit of the write-up | Open | Items marked `[in review]` |

**Also open, not blocking:** the Kaggle route has never run, so the mirror's files are not yet confirmed against the publisher's copy (`04-the-data/NOTES.md`). The pinned checksums mean a mismatch would fail loudly rather than silently.

## Risk if shipped now

A reader would take draft interpretation as the author's considered view, and the evidence chains would be presented as useful to an investigator on the strength of their facts alone. Neither changes a number; both would weaken the honesty the repository rests on.

## What would change the decision

Both blocking items closed and a clean-clone check that leaves the tree unchanged: ship. A failed reproduction, or a scored sample that contradicts a published claim, keeps it held and is recorded in `change_log.md`.
