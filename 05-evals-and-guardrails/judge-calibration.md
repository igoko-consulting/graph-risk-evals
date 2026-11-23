# Judge calibration

[in review]

Before a model's judgement counts for anything, compare it with a person's on the same items. The structure follows judge calibration in the AI Evals course (`igoko-consulting/ai-evals`, 03-eval-suites). Written on 2026-11-22. **Status: protocol written, awaiting scores.**

## Where a model judges in this repository

- **The evidence-chain review.** The author scores a seeded sample of Arm B's evidence chains on three questions, from the PRD's rubric: is the reason true, sufficient, and actionable by an investigator. A language model scores the same chains blind, as a second scorer (`00-build/evidence_review.py`).
- **The PRD review.** Two models reviewed PRD v1 independently ([`docs/prd-review.md`](../docs/prd-review.md), [`PROMPTS.md`](../PROMPTS.md)). Their findings were checked against the dataset documentation and the originating paper before any action, so they acted as reviewers whose points were verified, not as judges whose scores counted. Nothing to calibrate there.

## Protocol for the evidence-chain review

1. **The author scores first**, in `data/store/runs/evidence-chain-review.csv`, then runs `make review`. Scoring first means the model's answers cannot anchor the author's.
2. **`make review` writes a blind sheet** holding only the chain text. The model scores that sheet with the same rubric and never sees the author's answers.
3. **The next `make review` saves the model's scores** to `evidence-chain-scores-model.csv` and records, for each question, how many chains both scored and how many got the same answer, in `results/evidence-chain-review.json`.
4. **The author's scores are the result.** The model's are reported beside them and decide nothing. Agreement shows how far a model could stand in for the author on this task, on this sample.

## What will be measured, and what it will not show

- **Raw agreement per question.** The code counts same answers; it does not correct for chance. If most chains get "yes" from both scorers, raw agreement will look high even if the model answers without reading. A chance-corrected measure (Cohen's kappa, as the course uses) would need a change to `evidence_review.py`, which this page does not make.
- **No bar is set yet.** The course sets an agreement bar before the judge's scores are read. Here the model's scores decide nothing, so a bar matters only if a model is ever to score a larger sample in the author's place. If so, the author sets it before reading the model's answers.
- **One person, one sample, one arm.** The sample is drawn from Arm B's pre-shift queue. Agreement on it says nothing about post-shift chains, other arms, or another investigator.

## Status

**Awaiting scores.** Neither scorer has scored the sample, so there is no agreement to report and none is implied here. `results/evidence-chain-review.json` was generated before the blind scorer existed and still describes the author as the only scorer; the next `make review` rewrites it. When scores exist, the README's evidence-chain paragraph reports them from `results/`.
