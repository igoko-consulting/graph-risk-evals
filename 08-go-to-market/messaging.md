# Messaging pillars

[in review]

**An applied exercise.** The structure follows the messaging pillars in the Go-to-market course (`igoko-consulting/roamly-gtm-strategy`, 04-messaging): the shift in what readers ask, then pillars per audience, each with a proof point from this repository. Written on 2026-11-22.

## From and to

- **From:** "which model scores best on this dataset?"
- **To:** "when does a graph pay for itself, at an alert budget a team could staff, and how would I know before investing?"

## Audience 1: product management practitioners, senior product manager to VP

| Pillar | Proof point |
|---|---|
| The answer leads, with its limits beside it | The README opens with a generated answer and the decision row that applies; limitations are split into demonstrated, suggested and cannot be established |
| The decision turns on alert quality, not compute | **Modelled** cost per true positive, with analyst time as the dominant term (`03-the-margin/NOTES.md`, `results/cost-per-true-positive.json`) |
| A null result would have been published too | The pre-registration's kill criteria, committed before any result (`01-the-bet/pre-registration.md`) |
| Production decisions sit on the same ladder | The decision log, by industry, never by company (`07-decision-log/decision-log.md`, in review) |

## Audience 2: engineers

| Pillar | Proof point |
|---|---|
| The answer was committed before the result | Pre-registration tagged `prereg-v1` and hash-checked before every write (Gate 1) |
| No leakage passed silently | Gate 2's future-edge, label-shuffle and own-label tests, run at the current commit, on the same data |
| Every number traces to a run | Generated blocks and value spans from `results/`, each result carrying its commit and data checksums |
| It reproduces from one command | `make all` on a clean clone reproduced every non-timing figure (commit `8970cd1`) |

## Words to avoid

"Novel", "first", "proves", "fraud detection system", and any payments claim without its caveat. See [positioning.md](positioning.md), What it must never say.
