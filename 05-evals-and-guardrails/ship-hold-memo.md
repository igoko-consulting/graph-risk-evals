# Ship or hold: the Phase 4 gate

[in review]

**Decision: hold the gate until the author's review is done.** The results are published and reproduce; the write-up is not final. The form follows the ship-hold memo in the AI Evals course (`igoko-consulting/ai-evals`, 06-culture), under the rules in [gate-policy.md](gate-policy.md).

**What is already shipped, and why.** Every result was written through Gate 1 and Gate 2. The last clean-clone rerun reproduced every non-timing figure within the stated tolerance (commit `8970cd1`). Every fact in the evidence chains was rechecked in SQL, and none disagreed.

**Why the gate stays open.**
- Text marked `[in review]` has not yet been edited by the author.
- The evidence-chain review sample is not scored, and the blind second score waits on it.

**Also open, not blocking the gate.** The Kaggle route has never run, so the mirror's files are not yet confirmed against the publisher's copy (`04-the-data/NOTES.md`).

**What would change the decision.** Both blocking items closed, then a clean-clone check that leaves the tree unchanged, ships the gate. A failed reproduction on that check, or a scored sample that contradicts a published claim, keeps it held and is recorded in `change_log.md`.
