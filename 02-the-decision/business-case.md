# Business case

[in review]

The case for building this lab, in the form the Product Leadership course uses (`igoko-consulting/product-leadership`, 05-business-case): the bet, its assumptions ranked, the expected return, and the kill criterion. This is a non-commercial learning project, so the case is made in time and learning, not revenue. Written on 2026-11-22, after Phase 4, from the record and the author's answers given that day (cited as owner input).

## 1. The bet

> Building one pre-registered experiment end to end teaches more about when graph methods earn their cost in fraud and AML detection than reading about them, and leaves a method that carries to other work.

- **Objective:** learning (owner input, 2026-11-22). Working knowledge of graph stores, traversal queries and graph neural network evaluation, gained by answering one product question with evidence (README, What kind of project this is).
- **Starting point:** production experience in fraud and payments, graph databases and data platforms, but no graph machine learning ([`docs/prd-review-prompt.md`](../docs/prd-review-prompt.md)).
- **The question:** when does a graph earn its cost? Answered on the Elliptic Bitcoin transaction graph, which is public and is not payments data.

## 2. The assumptions, ranked

| Rank | Assumption | Held? | Evidence |
|---|---|---|---|
| 1 | The question can be answered honestly on public data | Held, within limits: the dataset has anonymised features, no transaction values and no account-level links, so nothing transfers directly to payments | README, Limitations; `04-the-data/NOTES.md` |
| 2 | A two-day sprint is enough for a method that survives scrutiny | Held for the build; the checking ran past it (section 5) | git history; `change_log.md` |
| 3 | An embedded graph store can express Arm B's features as traversal queries | Held | `graph/queries/`; [`docs/engine-comparison.md`](../docs/engine-comparison.md) |
| 4 | A laptop CPU is enough | Held for correctness; the full protocol takes hours, not the specification's target | README, What kind of project this is; `results/pipeline-runtime.json` |

## 3. The expected return

- **Investment:** the author's time over the sprint and the review since, and compute on a laptop CPU. Build time per arm, read from git history, sits beside a **modelled** production estimate in [`03-the-margin/NOTES.md`](../03-the-margin/NOTES.md), from `results/build-days.json`. Neither is an input to cost per true positive.
- **Return, whichever way the result fell:** the pre-registration made a null result a publishable finding before anything ran (`01-the-bet/pre-registration.md`, Kill criteria).
- **Return beyond the answer:** a method that carries to other regulated detection problems: hash-enforced pre-registration, leakage gates, and a write-up whose numbers are generated. The dataset does not carry over; the method does (PRD v2, Goals, Transferability).
- **No financial return** is claimed or modelled.

## 4. The kill criterion

- **For the project (owner input, 2026-11-22):** scope, a working version demonstrating learning, within the time frame. The same criterion applies to every one of the author's projects. In this repository's record, the time frame is the two-day discovery sprint (README; PRD v2, requirement 21).
- **Pre-registered** ([`01-the-bet/pre-registration.md`](../01-the-bet/pre-registration.md), Kill criteria):
  1. If Arm B does not beat Arm A outside the noise band, publish that and do not build Arm D.
  2. If all arms fall within the noise band of each other, report the comparison as underpowered.
  3. If the thin slice is not working at the end of the first session, ship a method write-up.

## 5. What happened

- **No pre-registered kill criterion fired.** The thin slice worked in the first session. Arm B beat Arm A outside the noise band before the regime shift, so Arm D was built, as pre-registered (`change_log.md`, 2026-11-19 Phase 2 result).
- **The project criterion, read against the record.** Scope held: what the time box left out is listed in the README and deferred to Phase 5. The pipeline and every result of Phases 1 to 4, the independent audit and its fixes, and the cold-reader revision fell within the sprint, on 19 and 20 November (`change_log.md`). The later clean-clone reruns, the build-days record, the governance note, the decision log and the blind scorer followed on 21 and 22 November (git history). Whether that later work counts against the time frame is the author's call.
- **Reviewers:** personal only, family and colleagues, named here by role (owner input, 2026-11-22). There was no sponsor and no budget holder.
