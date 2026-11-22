# Business case

[in review]

The case for building this lab, framed the way the Product Leadership course frames one: what it costs, what it returns, and when to stop (`igoko-consulting/product-leadership`, 05-business-case). This is a non-commercial learning project, so the case is made in time and learning, not revenue.

## The case

- **Objective.** Learning (author, 2026-11-22): working knowledge of graph stores, traversal queries and graph neural network evaluation, gained by answering one product question with evidence (README, scope).
- **The question.** When does a graph earn its cost in fraud and AML detection? Answered on a public Bitcoin transaction graph, which is not payments data.
- **Why this author, now.** The author had production experience in fraud and payments, graph databases and data platforms, but no graph machine learning ([`docs/prd-review-prompt.md`](../docs/prd-review-prompt.md)). The lab exists to close that gap honestly.
- **Investment.** A two-day discovery sprint of the author's time, and compute on a laptop CPU. Build time per arm, estimated from git history beside a modelled production estimate, is in [`03-the-margin/NOTES.md`](../03-the-margin/NOTES.md), from `results/build-days.json`.
- **Return.** A pre-registered answer either way: the pre-registration made a null result a publishable finding before anything ran. Beyond the answer, a method that carries to other work: hash-enforced pre-registration, leakage gates, and a write-up whose numbers are generated.

## Kill criteria

- **For the project (author, 2026-11-22):** stop at scope, once a working version demonstrates the learning, within the time frame. In this repository the time frame is the two-day sprint.
- **Pre-registered:** the three criteria in [`01-the-bet/pre-registration.md`](../01-the-bet/pre-registration.md): Arm B not beating Arm A outside the noise band; every arm within the noise band of the others; the thin slice not working at the end of the first session.

## What happened

- **No kill criterion fired.** The thin slice worked in the first session. Before the regime shift, Arm B beat Arm A outside the noise band, so Arm D was built, as the pre-registration allowed (README, Results).
- **The build fitted the sprint; the checking did not.** Phases 1 to 4 were built within the sprint. The independent audit, the clean-clone reruns and the write-up continued after it, and are recorded in `change_log.md`.
- **Reviewers.** Personal only: family and colleagues (author, 2026-11-22). There was no sponsor and no budget holder.
