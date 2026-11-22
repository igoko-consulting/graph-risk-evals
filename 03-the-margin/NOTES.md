# 03-the-margin: cost model, assumptions, sensitivity

**Every cost figure in this repository is modelled, not measured.** The figures themselves live in `results/cost-per-true-positive.json` and the README; this note holds only the assumptions and the formula, so they can be challenged without hunting through code.

## Formula

For each arm and each test period:

> cost per true positive = (alerts reviewed × analyst cost per alert + compute cost) ÷ true positives in the top k

- **Alerts reviewed:** k per time step (`results/k.json`) times the steps in the period. The queue is a fixed budget, so every arm reviews the same number of alerts. Arms differ only in how many of those alerts are true positives.
- **True positives:** illicit transactions among each step's top k labelled transactions, pooled over the period.
- **Compute cost:** recorded fit time for the arm, tuning included, times the threads used, at a cloud CPU price. For Arm B it includes Arm A's tuning, because Arm B's stage one is Arm A's tuned model, and the graph-store build of its structural features.

## Assumptions, fixed before Arm D ran

| Assumption | Value | Basis |
|---|---|---|
| Analyst cost per alert | <!-- value:analyst-cost -->€25<!-- end value -->, sensitivity <!-- value:analyst-cost-low -->€12.50<!-- end value --> to <!-- value:analyst-cost-high -->€37.50<!-- end value --> | <!-- value:analyst-cost-basis -->Author assumption: about 20 minutes of first-line review at about €75 an hour fully loaded. Not sourced.<!-- end value --> |
| Compute price | <!-- value:compute-price -->€0.05<!-- end value --> per vCPU-hour | Order of magnitude for on-demand general-purpose cloud CPU. Its exact value does not matter; see the compute share in the results |

## What the model leaves out

- **Second-line review, escalation and filing.** True positives cost more downstream than false positives. Leaving this out understates the cost of every arm by the same per-true-positive amount, so it does not change their ranking.
- **Losses prevented.** Not estimable from this dataset, which carries no transaction values.
- **Engineering and operating cost of the graph store and the GNN.** Recorded below, outside the model: lab build time estimated from the repository's history, beside the author's modelled production estimate.
- **Serving compute.** Not included. Scoring is a single forward pass per model, against hundreds of fits in tuning.

## Build days per arm

[in review]

<!-- generated:build-days by 00-build/render_readme.py from results/; do not edit by hand -->
| Arm | Lab build time, minutes (estimated from git) | Production estimate, engineer-days (modelled) | Basis |
|---|---|---|---|
| A | About 15, at most 117 | 20 to 40 | Engineer-days for a first production version: feature pipeline from existing data, tuned boosted model, batch scoring, monitoring and model governance. Unsourced range suggested by the coding assistant. |
| B | About 44, at most 180 | 40 to 80 | Added to A: link features or a graph store, kept fresh and computed point-in-time so they cannot leak, and operational on-call. Unsourced range suggested by the coding assistant. |
| D | About 3, at most 73 | 60 to 120 | Added to A: a GNN training pipeline, scoring new nodes as they arrive, explanations for investigators and model risk review. Unsourced range suggested by the coding assistant. |

**How lab time is estimated.** Commits made within two minutes of each other form one batch, because the work was committed in batches. A batch's work time is the gap since the previous commit, capped at an hour because longer gaps hold pipeline runs or breaks, and it is split between arms by their share of the code lines the batch changed. The upper bound gives each arm the whole capped window of every batch that touched its files. Arm A owns the shared tabular pipeline, which B and D reuse, so B and D are counted for what they add; Gate 2 counts under B, whose graph features it exists to test. History up to commit `df2e649`.

**What it does not show.** The repository was built with an AI coding assistant in a two-day sprint, so lab time is far below what a team would need and says little about production cost. Neither column is an input to cost per true positive.

Source: `results/build-days.json`.
<!-- end generated:build-days -->

The author's production estimates live in `03-the-margin/build-days.csv`. After editing it, run `make build-days`.
