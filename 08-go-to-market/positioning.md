# Positioning

[in review]

**An applied exercise.** The structure follows the positioning framework in the Go-to-market course (`igoko-consulting/roamly-gtm-strategy`, 03-positioning): six components, then one statement. It positions the findings, not the author ([gtm-strategy.md](gtm-strategy.md), section 4). Written on 2026-11-22.

## Framework

| Component | Question | This lab |
|---|---|---|
| For | Who, specifically? | Product leaders, senior product manager to VP, deciding whether graph methods are worth building for fraud or AML detection (owner input, 2026-11-22) |
| Who need | What problem? | To know what a graph adds over a well-tuned model without it, and what the extra alerts cost, before committing a team |
| We offer | What is it? | A pre-registered, reproducible experiment on a public Bitcoin transaction graph, from local features to graph features to a graph neural network, with a decision matrix generated from its results |
| Because of | The outcome | A decision made on evidence whose hypotheses, leakage tests and numbers can all be checked |
| Despite | The honest shortcoming | One dataset with anonymised features and no account-level links: it is not payments data, and nothing transfers to payments directly |
| Better than | Why this, for this reader | Published comparisons that keep neighbour aggregates in the baseline and report model scores without a cost ([battlecard.md](battlecard.md)) |

## Statement

> For product leaders deciding whether to invest in graph methods for fraud or AML detection, this lab is a pre-registered, reproducible test of where graph stops paying for itself. Unlike comparisons that keep the neighbour aggregates in the baseline, it isolates what the graph adds, and it reports **modelled** cost per true positive at a fixed alert budget rather than model scores alone. It is one Bitcoin transaction graph, not payments data, and it says so beside every claim.

**Category:** a decision lab and a stricter replication, not a detection product and not a benchmark.

## What it must never say

- **"Novel" or "first"** about the headline comparison. The dataset's own paper made it (PRD v2, Prior results).
- **Anything about payments** without the caveat beside it (`CLAUDE.md`, Honesty rules).
- **Anything about the author's availability or career.** That would turn the honesty commitments into positioning, which is why PRD v2 removed the hiring-manager journey.
- **A measured cost.** Every cost figure is modelled (red line 7).
