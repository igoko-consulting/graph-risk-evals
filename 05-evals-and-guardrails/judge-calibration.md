# Judge calibration

[in review]

Before a model's judgement counts for anything, compare it with a person's. The structure follows judge calibration in the AI Evals course (`igoko-consulting/ai-evals`, 03-eval-suites).

## Where a model judges in this repository

- **The evidence-chain review.** The author scores a seeded sample of Arm B's evidence chains on three questions: is the reason true, sufficient, and actionable by an investigator. A language model scores the same chains as a second scorer.
- **The PRD review.** Two models reviewed PRD v1 independently ([`docs/prd-review.md`](../docs/prd-review.md), [`PROMPTS.md`](../PROMPTS.md)). Their findings were checked against the dataset documentation and the originating paper before any action, so they acted as reviewers whose points were verified, not as judges whose scores counted.

## Protocol for the evidence-chain review

1. The author scores first, in `data/store/runs/evidence-chain-review.csv`, and runs `make review`.
2. `make review` also writes a blind sheet holding only the chain text. The model scores that sheet with the same rubric and never sees the author's answers.
3. The next `make review` saves the model's scores to `evidence-chain-scores-model.csv` and records, for each question, how often the two scorers gave the same answer, in `results/evidence-chain-review.json`.
4. The author's scores are the result. The model's are reported beside them and decide nothing. Agreement shows how far a model could stand in for the author on this task, on this sample.

## Status

Awaiting scores. Neither scorer has scored the sample yet, so there is no agreement to report. When there is, the README's evidence-chain paragraph reports it from `results/`.
