# Pre-registration

**Committed before any result exists. Tagged `prereg-v1`. Never edited.**

The pipeline hashes this file and refuses to write to `results/` if the hash does not match the tagged commit. If you are reading this in a repository where results exist, the tag and the hash are the evidence that this was written first.

**Date committed:** 2026-11-19
**Author:** Martin Cook
**Specification:** `prds/prd-v2.md` v2.3

---

## What is being tested

Whether explicitly representing relationships between entities adds measurable detection value beyond a properly tuned tabular model built on the same historical information, and whether any such gain justifies its cost.

---

## Definitions

Fixed here, before any result, and used unchanged throughout.

| Term | Definition |
|---|---|
| **Training period** | Time steps 1 to 29 |
| **Validation period** | Time steps 30 to 34. All thresholds and hyperparameters selected here |
| **Pre-shift test period** | Time steps 35 to 42 |
| **Post-shift test period** | Time steps 43 to 49 |
| **k** | The mean number of illicit labels per time step across steps 1 to 34, computed in code before any test step is read |
| **Primary metric** | Precision at k, computed on labelled nodes only |
| **Evidence unit** | 5 random seeds per arm, paired bootstrap of 1,000 resamples stratified by time step |
| **Noise band** | The 95% bootstrap confidence interval on a difference between arms includes zero |

**Evaluation population.** Metrics are computed on labelled nodes only. Unlabelled nodes are never treated as negatives. When ranking across all nodes, the unlabelled share of the top-k queue is reported separately.

---

## Arms

| Arm | Definition |
|---|---|
| **A** | Tuned gradient-boosted trees on the 94 local features only. Time-step column excluded. Never reads the graph store |
| **B** | Arm A plus the 72 provided one-hop aggregates, plus structural features computed as traversal queries: in-degree, out-degree, PageRank within time step, two-hop neighbourhood size, and two-stage neighbour aggregates of the model's own predicted scores |
| **D** | Two-layer GraphSAGE, inductive. Architecture family fixed here, in advance |

No label-derived features are used in any arm. Hop-distance-to-a-confirmed-bad-actor is excluded because time steps are disjoint, so such a feature could only draw on labels within the same test step.

---

## Hypotheses

**H1.** Graph-derived features capture the majority of available lift.

> Defined as (B − A) / (max(B, D) − A) ≥ 0.5, measured on PR-AUC over the pre-shift test period.
>
> If Arm A is the best-performing arm, H1 is undefined. That outcome is itself the finding and is reported as such.

**H2.** The graph neural network does not justify its cost.

> H2 is rejected only if **both** conditions hold: Arm D beats Arm B on precision at k by at least 5 percentage points, pooled over the pre-shift test period; **and** the 95% bootstrap confidence interval on that difference excludes zero.
>
> If H2 is rejected, the pre-registered prediction was wrong. That is reported plainly, with what changed it.

**H3.** Simpler arms degrade less after the regime shift.

> Measured as the relative fall in PR-AUC from the mean of the pre-shift period to the mean of the post-shift period, compared across arms.

**H4.** The advantage of graph-derived features over the local-feature baseline widens as labels become scarcer.

> Measured across the label-budget curve at 5, 10, 25, 50 and 100 percent of training labels, with the full protocol applied identically at each budget.

---

## What would change my mind

H2 is the load-bearing prediction. It is rejected on the two-part test above and on nothing else. A gain that is large but whose confidence interval includes zero does not reject it. A gain that is statistically clear but under 5 percentage points does not reject it.

I expect Arm A or Arm B to win. If Arm D wins on both conditions, I was wrong, and the repository says so in the README rather than in a footnote.

---

## Kill criteria

1. **If Arm B does not beat Arm A outside the noise band**, publish that finding and do not build Arm D.
2. **If all arms fall within the noise band of each other**, the finding is that the comparison is underpowered on this data. State what data or design would separate them. Do not reach for a subset where the difference looks larger.
3. **If the thin end-to-end slice is not working at the end of the first build session**, stop. The repository ships as a method write-up.

---

## Protocol commitments

- No threshold, hyperparameter or operating point is selected on test steps, for any arm, at any stage.
- Arms A and D receive the same tuning search method, the same number of trials, the same training and validation windows, the same primary optimisation metric, the same early-stopping rule and class weighting, and the same number of seeds. Any architecture search for Arm D counts against its trial budget.
- Equal trials is not equal compute. Both trial count and training compute are recorded and reported.
- Two leakage tests run every build: insert a future edge and assert no earlier feature value changes; shuffle test labels and assert no feature value changes.
- Every reported figure is produced by code and read from `results/`.

---

## Still open at the time of committing

Recorded here honestly. None of these may be resolved by looking at test-period results.

| Question | Constraint on how it may be answered |
|---|---|
| Analyst cost per alert, for the cost model | Fixed and justified before any cost figure is published. Sensitivity range published alongside. Labelled modelled, never measured |
| Whether time steps contain cross-step edges | Confirmed in the loader on day one. If they do, the leakage analysis is revised and the revision is recorded in `change_log.md` before any arm runs |
| Whether two-stage predicted-score aggregation itself leaks | Designed and tested before Arm B runs. If it leaks, the feature is dropped rather than adjusted after seeing its effect |

---

## Prior work

The headline comparison on this dataset has been published. A random forest on the full feature set outperformed a two-layer graph convolutional network on illicit F1, and performance degraded sharply after the regime shift. This lab does not claim novelty in that comparison. What it adds is set out in section 2 of the specification: a cleanly separated baseline, a fixed alert budget, cost per true positive, a label-budget curve, and an equal and documented tuning protocol.
