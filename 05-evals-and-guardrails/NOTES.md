# 05-evals-and-guardrails: eval stack, red lines, review queue

## Evidence-chain review

The rubric, from the PRD: is the reason true, sufficient, and actionable by an investigator.

- **Score in the sheet.** `make all` writes `data/store/runs/evidence-chain-review.csv`, a seeded sample of 30 chains from Arm B's pre-shift queue. Answer `true`, `sufficient` and `actionable` with y or n, all three or none, and add a note where it helps.
- **Then run `make review`.** It saves the scores to [`evidence-chain-scores.csv`](evidence-chain-scores.csv) and recounts them into `results/evidence-chain-review.json`, which the README reads. Commit both.
- **Why the scores are kept apart from the chains.** The chains name transactions, and the dataset's licence rules out publishing per-transaction outputs. Each score is saved against a SHA-256 of the chain it judges, so a rerun refills the sheet. A chain that changes cannot inherit a score given to a different one: the run halts instead.
- **Notes are published.** A note holding what looks like a transaction ID is refused.
- **A blank sheet row keeps a saved score.** To withdraw one, edit the saved file.
- **A blind second scorer.** `make review` also writes `data/store/runs/evidence-chain-review-blind.csv`, which holds only the chain text. After the author has scored, a language model scores that sheet with the same rubric, without seeing the author's answers, and the next `make review` saves its scores to [`evidence-chain-scores-model.csv`](evidence-chain-scores-model.csv) and counts how often the two scorers agree. The author scores first, so the model's answers cannot anchor the author's.

## Gates and failures

Added on 2026-11-22 from the AI Evals course structure (see `change_log.md`), all `[in review]`:

- [failure-taxonomy.md](failure-taxonomy.md): every failure found so far, ranked, and what now catches it.
- [gate-policy.md](gate-policy.md): Gate 1, Gate 2 and the other checks, which are hard and which advisory.
- [coverage-matrix.md](coverage-matrix.md): what each check catches, what nothing catches, and the critical gap.
- [judge-calibration.md](judge-calibration.md): the protocol for the blind second scorer; awaiting scores.
- [ship-hold-memo.md](ship-hold-memo.md): the Phase 4 gate decision, recommended as a hold.
