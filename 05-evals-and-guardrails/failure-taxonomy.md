# Failure taxonomy

[in review]

Every failure found in this repository so far, grouped by mode, ranked, and traced to what now catches it. The structure follows the failure taxonomy canvas in the AI Evals course (`igoko-consulting/ai-evals`, 02-failure-discovery): checks are written for failures that happened, not for ones imagined. Written on 2026-11-22 from the record, after Phase 4.

**Severity** here has three levels, because each failure happened once and frequency does not separate them:
- **Invalidating:** left in place, the result would mean nothing.
- **Weakening:** the result stands, but a guarantee was weaker than the text claimed.
- **Presentation:** result and guarantee stand; the text misled or buried something.

## Top three, prioritised

| Rank | Failure | Severity | Found by | Why it ranks here |
|---|---|---|---|---|
| 1 | Contaminated baseline | Invalidating | One of two model reviewers of PRD v1 | It would have made H1 wrong by construction and every graph-against-baseline comparison meaningless |
| 2 | Label-derived leakage | Invalidating | The same reviewer | It would have inflated Arm B's score and voided the comparison |
| 3 | A gate weaker than its rule | Weakening | Independent audit, after publication | The only failure that reached shipped code: Gate 2 claimed more than it enforced |

## #1 risk: impact statement

> This failure matters because a baseline that already holds one round of neighbour aggregation hides most of what a graph adds, which would have led a reader to a conclusion about graph methods that the experiment never tested.

## Every failure found so far

| Mode | What happened | Severity | Found by | Caught now by | Record |
|---|---|---|---|---|---|
| Contaminated baseline | PRD v1's Arm A used every node feature, including the one-hop neighbour aggregates, so it was never graph-free | Invalidating | Cross-model review of PRD v1 | Arm A's feature list asserted in code; the feature contract tests | [`docs/prd-review.md`](../docs/prd-review.md); `tests/test_feature_contract.py` |
| Label-derived leakage | A hop-distance-to-a-known-bad-actor feature could read labels from the very test step it scored | Invalidating | Cross-model review of PRD v1 | The feature was removed; Gate 2's label-shuffle and own-label tests | `docs/prd-review.md`; `00-build/leakage_gate.py` |
| Unclaimed prior work | The headline comparison was already published, and PRD v1 did not say so | Invalidating, for the claim of contribution | Cross-model review of PRD v1 | The PRD's prior-results section; the citation in the generated README text | [`prds/prd-v2.md`](../prds/prd-v2.md); `change_log.md`, 2026-11-20 audit follow-up |
| Untestable predictions | PRD v1's hypotheses rested on "majority", "enough", "less" and "noise band" without definitions, so no result could falsify them | Invalidating, for the pre-registration | Both models in the cross-model review of PRD v1 | Numeric definitions in the pre-registration, locked by Gate 1 | `docs/prd-review.md`, where both models agreed |
| Leakage through a global rule | PageRank's first stopping rule let a change in one time step alter how many iterations every other step got | Weakening | Fixing the protocol, before any arm ran | A fixed iteration count; Gate 2's future-edge test | `change_log.md`, 2026-11-19 protocol entry |
| A gate weaker than its rule | Gate 2 dropped any feature that moved and still passed, which is more than the pre-registration allows | Weakening | Independent audit, after publication | Gate 2 now fails on any movement under the future-edge or label-shuffle test | `change_log.md`, 2026-11-20 audit fixes and Gate 2 entries |
| Checks removed by optimisation | Bare `assert` statements would vanish under `python -O` | Weakening | Audit follow-up | `require()` calls, which Python does not strip | `change_log.md`, 2026-11-20 audit follow-up |
| Figures typed by hand | Assumptions, counts and settings were typed into prose, where they could drift from the run | Presentation | Independent audit | Value spans and generated blocks filled from `results/`; the renderer refuses to claim equal tuning if the arms differ | `change_log.md`, 2026-11-20 audit fixes |
| Text claiming more than the code | The README said no result is written if any test fails; k was described as computed from the wrong steps; a smoke-run disclosure understated what was known | Presentation | Independent audit and its review | Corrected text, and caveats placed beside each claim | `change_log.md`, 2026-11-20 audit follow-up and its review |
| Exact claims that do not reproduce | Values below the leakage tolerance differ between identical runs, so a claim of exactly zero movement would not survive a rerun | Presentation | Overnight clean-clone rerun | The leakage sentence always states the tolerance | Commits `48b2fdf` and `8970cd1` |
| Answer too late for a cold reader | The answer first appeared in the decision matrix, well down the page | Presentation | Cold-reader review | A generated answer block under the title, read from the same rules as the decision matrix | `change_log.md`, 2026-11-20 cold-reader entry |
| A versioning rule bent | PRD v2.5 was written into `prds/prd-v2.md` rather than a new file, against "PRDs are versioned, never overwritten" | Presentation | Audit follow-up | Nothing yet: left for the author to decide | `change_log.md`, 2026-11-20 audit follow-up |

## Defending the prioritisation

- **Why the two leakage-class failures lead.** Both would have produced a confident, wrong answer. Neither would have been visible in the results, only in the design.
- **Why the weak gate outranks unclaimed prior work.** Missing prior work damaged the claim of novelty, not the measurement, and was fixed in the PRD before any code. The weak gate was in shipped code and the README overstated it. The published run happened to pass the stricter rule, so no result changed, but that was luck rather than design.
- **Why untestable predictions do not make the top three.** Both reviewers found them, so the review was not a single point of failure for that one, and Gate 1 now locks the definitions.
- **What is missed.** The three errors the PRD review classed as invalidating all came from one of the two model reviewers, so the review step itself is a single point of failure. No cross-model review of PRD v2 is recorded.

## What the pattern shows

- **Review before code caught the worst failures.** The contaminated baseline, label leakage, unclaimed prior work and untestable predictions were found before any code existed.
- **The audit after publication found weaker guarantees and drifting text, not wrong results.** No audit finding changed a published result (`change_log.md`, 2026-11-20 entries).

What nothing catches yet is in [coverage-matrix.md](coverage-matrix.md).
