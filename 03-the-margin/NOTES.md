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
- **Engineering and operating cost of the graph store and the GNN.** Build days per arm are a real cost the code cannot measure; the author records them below.
- **Serving compute.** Not included. Scoring is a single forward pass per model, against hundreds of fits in tuning.

## Build days per arm

_To be recorded by the author._

| Arm | Build days | Note |
|---|---|---|
| A | | |
| B | | |
| D | | |
