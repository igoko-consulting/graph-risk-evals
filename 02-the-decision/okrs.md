# OKRs

[in review]

Objectives and key results for this lab, in the form the Product Leadership course uses (`igoko-consulting/product-leadership`, 01-strategy and 02-roadmap). **They were written after the build**, from the author's stated aims (author, 2026-11-22) and the PRD's goals, so they record what was aimed at and scored against the record. They were not a plan set in advance.

## Objective 1: learn how graph methods behave by building them

| Key result | Status | Evidence |
|---|---|---|
| Arm B's features run as traversal queries in an embedded graph store | Met | `graph/queries/` |
| A graph neural network arm trained and evaluated under the same tuning contract as the others | Met | Arm D, `00-build/arm_d.py`; README, Results |
| Traversal and aggregation workloads compared in a graph store and a columnar store | Met | [`docs/engine-comparison.md`](../docs/engine-comparison.md) |

## Objective 2: answer the product question with evidence that survives scrutiny

| Key result | Status | Evidence |
|---|---|---|
| The pre-registration committed and tagged before any result, and enforced in code | Met | Tag `prereg-v1`; Gate 1 |
| Leakage tests pass for every published result | Met | Gate 2; `results/leakage-tests.json` |
| Every number in the write-up generated from `results/` | Met after the audit fixes | `change_log.md`, audit fixes |
| The decision matrix row chosen by code, from rules written before Arm D ran | Met; its wording in review | README, decision matrix |

## Objective 3: be readable to the people it is for

In order (author, 2026-11-22): the author first; then product practitioners from senior PM to VP, for craft depth and leadership decision-making; then engineers, for trust and collaboration.

| Key result | Status | Evidence |
|---|---|---|
| The README leads with the answer and gives the reasoning for each material decision | Met; in review until the author edits it | README; PRD requirement 21 |
| Limitations separated into demonstrated, suggested and cannot be established | Met | README, Limitations |
| The evidence-chain review sample scored by the author | Open | [`05-evals-and-guardrails/judge-calibration.md`](../05-evals-and-guardrails/judge-calibration.md) |

## The outcome each phase moved

| Phase | Outcome |
|---|---|
| 1, Foundations | A result can be trusted to have been pre-registered, on data that matches the PRD |
| 2, The ladder | Whether graph features add anything to a tuned local-feature model |
| 3, The expensive rung | Whether a graph neural network adds more, and at what cost per true positive |
| 4, The argument | A reader arriving cold can follow the answer and its limits |
| 5, Extension (not started) | Whether the findings hold on an actor-level graph |
