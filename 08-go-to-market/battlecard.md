# Battlecard: this lab against the published comparisons

[in review]

**An applied exercise.** The structure follows the battlecard in the Go-to-market course (`igoko-consulting/roamly-gtm-strategy`, 02-competitive-intel). The "competitors" are the published comparisons a practitioner would otherwise read. Written on 2026-11-22.

**Source and date.** Every claim about prior work comes from [`prds/prd-v2.md`](../prds/prd-v2.md), Prior results and what this adds (v2.5, 2026-11-20), which cites the dataset's own paper (Weber et al., 2019). The papers were not re-read for this exercise.

## Know the landscape

- **The dataset's own paper.** A random forest on the full feature set beat a graph convolutional network on illicit F1, and every model degraded sharply after the regime shift.
- **Later public work** examined temporal against random splits and leakage-free inductive protocols.

## The battlefield

| | Published comparisons, as PRD v2 describes them | This lab |
|---|---|---|
| Baseline | Frequently the full feature set, which already holds neighbour aggregates | Local features only, so the graph's lift is isolated |
| Operating point | An unconstrained threshold | A fixed alert budget, committed before any result |
| Economics | Model performance alone | Cost per true positive, **modelled**, dominated by analyst time |
| Scarce labels | Not well covered | A label-budget curve |
| Tuning | Not described in PRD v2 | Equal for every arm, to a protocol written before any run |
| Novelty | The dataset's paper reported the comparison first | Claims none for the headline comparison: a stricter replication |

## Where this lab is weaker

- **One dataset, anonymised.** The findings do not transfer to payments without account-level data this dataset lacks (README, Limitations).
- **A short time box.** Adversarial behaviour, other model families and a second dataset are untested (README, What a longer project would test).
- **Slower to run.** The full protocol takes hours on a laptop, against the specification's target (README, What kind of project this is).

## Why a reader picks it

- **For a product leader:** it answers the investment question at an operating point a team could staff, with the cost **modelled** and labelled so.
- **For an engineer:** every claim traces to a gate, a test or a file in `results/`, and one command reproduces it.

## The bet

Practitioners will trust a smaller claim made under pre-registration and leakage gates over a larger claim made without them. Nothing in this repository has tested that bet yet.
