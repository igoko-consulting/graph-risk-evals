# 05-evals-and-guardrails: eval stack, red lines, review queue

## Evidence-chain review

The rubric, from the PRD: is the reason true, sufficient, and actionable by an investigator.

- **Score in the sheet.** `make all` writes `data/store/runs/evidence-chain-review.csv`, a seeded sample of 30 chains from Arm B's pre-shift queue. Answer `true`, `sufficient` and `actionable` with y or n, all three or none, and add a note where it helps.
- **Then run `make review`.** It saves the scores to [`evidence-chain-scores.csv`](evidence-chain-scores.csv) and recounts them into `results/evidence-chain-review.json`, which the README reads. Commit both.
- **Why the scores are kept apart from the chains.** The chains name transactions, and the dataset's licence rules out publishing per-transaction outputs. Each score is saved against a SHA-256 of the chain it judges, so a rerun refills the sheet. A chain that changes cannot inherit a score given to a different one: the run halts instead.
- **Notes are published.** A note holding what looks like a transaction ID is refused.
- **A blank sheet row keeps a saved score.** To withdraw one, edit the saved file.
