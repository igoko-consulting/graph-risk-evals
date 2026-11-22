# Go-to-market strategy

[in review]

**An applied exercise, not a launch.** The lab is free and public, sells nothing, and has no launch plan. This page asks who should read the findings and how they would find them, in the structure of the Go-to-market course (`igoko-consulting/roamly-gtm-strategy`, 01-gtm-strategy). Written on 2026-11-22 from the record and the author's answers given that day (owner input). Channels, sequence and metrics are proposed, not done.

## 1. Goal

Learning (owner input, 2026-11-22). The findings reach the readers who can use them, in a form that keeps the method's honesty intact. Reach is not a goal in itself.

## 2. Readers

In order (owner input, 2026-11-22):

1. **The author.** It is a learning project first.
2. **Product management practitioners, senior product manager to VP.** For craft depth and leadership decision-making: when a graph earns its cost in fraud and AML detection, and how to decide that with evidence before investing.
3. **Engineers.** For trust and collaboration: the method is open to check, from the pre-registration to the leakage gates to the generated numbers.

**Not for:** anyone looking for a fraud detection product (a PRD non-goal), or a payments team expecting payments results. The dataset is a Bitcoin transaction graph with anonymised features and no account-level links.

## 3. Motion

The repository is the product, and readers arrive through links to it. No paid or pushed distribution fits a free learning lab.

## 4. The assumption this page pushes back on

**That a public lab should say who it is for in order to be found.** PRD v1 did that, in a user journey written for a hiring manager. The cross-model review called it out (a public lab that names its hiring audience reads as marketing, `PROMPTS.md`), and PRD v2 removed it because it reframes every honesty commitment as positioning (`prds/prd-v2.md`, Critical user journeys). So this exercise positions the findings, never the author. The readers above are named for what they would do with the findings, not for what they could do for the author.

## 5. One-pager

| | |
|---|---|
| **Problem** | Published comparisons on this dataset often keep the neighbour aggregates in the baseline and report model scores without pricing the alerts, so a product leader cannot see what the graph adds or what it costs (`prds/prd-v2.md`, Prior results and what this adds) |
| **Goal** | The findings are read and checked by the readers above, in order |
| **Audience** | Practitioners first (section 2), then engineers |
| **Value proposition** | A pre-registered, reproducible test of where graph stops paying for itself, with limits stated beside each claim ([positioning.md](positioning.md)) |
| **Motion** | The repository itself; readers arrive through links |
| **Channels (proposed)** | Practitioners: a short written summary that leads with the decision matrix and its limits and links to the README; a practitioner talk, if one fits. Engineers: the README's Running it section, and issues on the method. No promotion has been done |
| **Sequence (proposed)** | Nothing is promoted while text is marked `[in review]`. After the author signs off Phase 4 ([ship-hold-memo](../05-evals-and-guardrails/ship-hold-memo.md)): the final README, then the practitioner summary, then an invitation to check the method |
| **Metric (proposed)** | Practitioners: a cold reader can state the answer, the decision row that applies and one limitation after the README's five-minute path. One cold-reader review has tested this (`change_log.md`, 2026-11-20). Engineers: a clean-clone reproduction, or an issue on the method, from someone other than the author. Author: Objective 1 in [`02-the-decision/okrs.md`](../02-the-decision/okrs.md) |

## Pricing

Not applicable: the lab is free, sells nothing, and the dataset's licence (CC BY-NC-ND 4.0) is non-commercial.
