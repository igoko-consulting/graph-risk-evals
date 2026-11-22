# OKRs and outcome roadmap

[in review]

Objectives and key results for this lab, in the form the Product Leadership course uses (`igoko-consulting/product-leadership`, 01-strategy for OKRs, 02-roadmap for the outcome roadmap). **They were written after the build**, on 2026-11-22, from the author's stated objective and readers (owner input) and the PRD's goals. They record what was aimed at, scored against the record. They were not a plan set in advance.

## Where it plays, and the one hard no

- **Objective:** learning (owner input, 2026-11-22).
- **Readers, in order** (owner input, 2026-11-22): the author first, for learning; then product management practitioners from senior product manager to VP, for craft depth and leadership decision-making; then engineers, for trust and collaboration. Each objective below serves one of them, in that order.
- **The one hard no:** not a fraud detection product and not a claim about payments. No deployment, no serving layer, no production-readiness claim (PRD v2, Non-goals).

## Objective 1: the author learns how graph methods behave by building them

| Key result | Status | Evidence |
|---|---|---|
| Arm B's features run as traversal queries in an embedded graph store | Met | `graph/queries/` |
| A graph neural network arm trained and evaluated under the same tuning contract as the others | Met | Arm D, `00-build/arm_d.py`; README, Results |
| Traversal and aggregation workloads compared in a graph store and a columnar store | Met | [`docs/engine-comparison.md`](../docs/engine-comparison.md) |
| A working version of Phases 1 to 4 within the two-day sprint | Met for the pipeline and results; later notes and checks followed | [business-case.md](business-case.md), section 5 |

## Objective 2: a product leader can make the graph decision from this lab

| Key result | Status | Evidence |
|---|---|---|
| The README leads with the answer and the decision row that applies, both generated from `results/` | Met; in review until the author edits it | README, The answer and The decision matrix |
| Each material decision gives its reasoning, cost and alternatives | Met; in review | README, Key decisions; PRD v2, requirement 21 |
| Limitations separated into demonstrated, suggested and cannot be established | Met | README, Limitations |
| Cost expressed per true positive, **modelled**, with analyst time as the dominant term | Met | [`03-the-margin/NOTES.md`](../03-the-margin/NOTES.md); `results/cost-per-true-positive.json` |
| Production decisions mapped to the same ladder, by industry, never by company | In review | [`07-decision-log/decision-log.md`](../07-decision-log/decision-log.md) |

## Objective 3: an engineer can trust and build on the method

| Key result | Status | Evidence |
|---|---|---|
| The pre-registration committed and tagged before any result, and enforced in code | Met | Tag `prereg-v1`; Gate 1 |
| Leakage tests pass for every published result | Met | Gate 2; `results/leakage-tests.json` |
| Every number in the write-up generated from `results/` | Met after the audit fixes | `change_log.md`, 2026-11-20 audit fixes |
| One command on a clean clone reproduces every non-timing figure | Met | Commit `8970cd1` |
| The evidence-chain sample scored by the author, with a blind second score beside it | Open | [`05-evals-and-guardrails/judge-calibration.md`](../05-evals-and-guardrails/judge-calibration.md) |

**What these key results miss.** They are binary milestones, not measured outcomes. Whether a practitioner or an engineer actually got what Objectives 2 and 3 promise is untested beyond one cold-reader review (`change_log.md`, 2026-11-20). Measured targets would need reader evidence the repository does not have, and red line 5 rules out typing targets that `results/` cannot produce.

## Outcome roadmap

Each phase is listed by the outcome it was meant to move, not the work it contained (PRD v2, Roadmap).

| Phase | Outcome | Status |
|---|---|---|
| 1, Foundations | A result can be trusted to have been pre-registered, on data that matches the PRD | Done |
| 2, The ladder | Whether graph features add anything to a tuned local-feature model | Done |
| 3, The expensive rung and the economics | Whether a graph neural network adds more, and at what **modelled** cost per true positive | Done |
| 4, The argument | A reader arriving cold can follow the answer and its limits | Built; gate held ([ship-hold-memo.md](../05-evals-and-guardrails/ship-hold-memo.md)) |
| 5, Extension | Whether the findings hold on an actor-level graph | Not started |
