# 08-go-to-market: readers, positioning, messaging

[in review]

**An applied exercise.** This lab is free and public, sells nothing, and has no launch plan. The exercise asks who should read the findings and how they will find them, using the structure of the Go-to-market course (`igoko-consulting/roamly-gtm-strategy`). It positions the findings, not the author.

## Who it is for

In order (author, 2026-11-22):

1. **The author.** It is a learning project first.
2. **Product practitioners, senior PM to VP.** For craft depth and leadership decisions: when a graph earns its cost, and how to decide that with evidence before investing.
3. **Engineers in graph and ML systems.** For trust and collaboration: the method is open to check, from the pre-registration to the leakage gates to the generated numbers.

**Not for:** anyone looking for a fraud detection product (a non-goal in the PRD), or a payments team expecting payments results. The dataset is a Bitcoin transaction graph.

## Positioning

For product leaders deciding whether to invest in graph methods for fraud or AML detection, this lab is a pre-registered, reproducible test of where graph stops paying for itself. Unlike most published comparisons, its baseline leaves out the neighbour aggregates, so the lift from graph information is isolated, and it reports cost per true positive at a fixed alert budget rather than model scores alone.

## Battlecard: against the published comparisons

| | Published comparisons, as the PRD summarises them | This lab |
|---|---|---|
| Baseline | Often the full feature set, which already holds neighbour aggregates | Local features only |
| Operating point | Often an unconstrained threshold | A fixed alert budget, committed in advance |
| Economics | Model performance alone | Cost per true positive, modelled and dominated by analyst time |
| Scarce labels | Not well covered | A label-budget curve |

This lab also tunes every arm equally, to a protocol written before any run, and claims no novelty for the headline comparison, which the dataset's own paper made first. Source: [`prds/prd-v2.md`](../prds/prd-v2.md), Prior results and what this adds.

## Messaging pillars

| Pillar | Proof point |
|---|---|
| The answer was committed before the result | Pre-registration tagged `prereg-v1` and hash-checked before every write (Gate 1) |
| No leakage passed silently | Gate 2's future-edge, label-shuffle and own-label tests, run at the current commit |
| Every number traces to a run | Generated blocks and value spans from `results/`, each result carrying its commit and data checksums |
| The limits sit beside the claims | Demonstrated, suggested and cannot be established, in the README |

## Channels

The README is the front door, linked from the author's GitHub profile. No promotion plan exists.

## Pricing

Not applicable. The lab is free, and the dataset's licence (CC BY-NC-ND 4.0) rules out commercial reuse of its outputs in any case.
