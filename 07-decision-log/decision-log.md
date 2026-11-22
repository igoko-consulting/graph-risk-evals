# Decision log

[in review]

Production decisions from the author's work, anonymised: industries are named, employers are not. Each is mapped to the rung of the [escalation ladder](../README.md#the-escalation-ladder) it concerns, and to where this repository tests the same question. They are experience, not findings. Nothing here was measured in this repository, and none of it comes from the dataset, which is a Bitcoin transaction graph rather than payments data.

| # | Rung | Industry | Decision | Tested here |
|---|---|---|---|---|
| 1 | 1, kept | Energy major | Rules stayed the system of record; machine learning only ordered the alerts | Context only |
| 2 | 1 beside 2 | Travel tech | Fraud rules kept beside a tabular model, each with its own job | Arm A |
| 3 | 3 | Travel tech | Relationship signals added as features, not through a graph database | Arm B |
| 4 | Beneath 3 | Travel tech | A real-time workload that was aggregation, not traversal, moved to a columnar store | Engine comparison |
| 5 | 4, deferred | Omnichannel retailer | Deterministic customer matching first; a probabilistic identity graph deferred | Entity resolution note |
| 6 | 4 | Unicorn SaaS | Workspaces resolved to organisations by rules before any graph clustering | The ladder rule |
| 7 | 5, declined | Big tech | A graph neural network declined in favour of a boosted model with graph features | Arm D |

---

### 1. Rules kept as the system of record for regulated monitoring

**Rung 1, kept. Energy major.**

- **Problem.** Regulated monitoring, such as trading surveillance or asset safety, raised more alerts than analysts could work.
- **Options.** Replace the thresholds with a model; keep the thresholds alone; keep the thresholds and use machine learning only to order the alerts.
- **Choice and why.** The last. Regulators and auditors expect a threshold that can be stated and defended. A model that decides which alerts exist is harder to defend than one that decides which come first.
- **Cost.** The rules still raise every alert, so false positives are reordered, not removed, and two systems need maintaining.
- **Outcome.** The alert set stayed explainable to a regulator, and analyst time went to the highest-ranked alerts first.
- **In this repo.** Rung 1 is context only, because the dataset carries no rules to compare against. Ordering rather than replacing is the idea behind measuring precision at a fixed alert budget.

### 2. Fraud rules kept beside a model

**Rung 1 beside rung 2. Travel tech.**

- **Problem.** Booking and payment fraud was handled by rules, and a tabular model was proposed to replace them.
- **Options.** Replace the rules with the model; keep rules only; run both, with distinct jobs.
- **Choice and why.** Both. Rules answer a new attack the same day and give an explainable reason for a decline. The model ranks cases, which rules do badly.
- **Cost.** Two systems to maintain, and rules that outlive the attack they were written for unless someone retires them.
- **Outcome.** Rules stayed the first line, and the model took over ranking.
- **In this repo.** Arm A is rung 2: a tuned tabular model on local features. Rules are not tested, so the repo cannot say what they would add.

### 3. Relationship signals as features, not a graph database

**Rung 3. Travel tech.**

- **Problem.** Accounts linked by a shared device, card or address were a strong fraud signal, and a graph database was proposed to use it.
- **Options.** A graph database queried at decision time; link counts computed as features in the existing feature store; nothing.
- **Choice and why.** Features. Most of the value sat in simple counts, such as how many accounts share a device or how many cards an address has used. Those are aggregates the existing feature store could compute at the latency the decision needed.
- **Cost.** Patterns beyond one hop, such as a ring of accounts linked only through intermediaries, are not captured by one-hop counts.
- **Outcome.** Relationship signal reached the model without new infrastructure.
- **In this repo.** Arm B is this decision. It adds graph-derived features to Arm A's model and measures what they add; the README reports the result with its interval.

### 4. A real-time workload that was aggregation, not traversal

**Beneath rung 3, the engine choice. Travel tech.**

- **Problem.** Real-time fraud and linking checks at booking time. A graph store was proposed because the data looked like a graph.
- **Options.** A graph store; a columnar store; the existing transactional database.
- **Choice and why.** A columnar store. The queries that mattered were counts over time windows, such as bookings per card, device or property in a recent window. That is aggregation, not traversal, and a columnar engine does it faster and more cheaply.
- **Cost.** Genuine multi-hop questions became offline jobs rather than real-time checks.
- **Outcome.** The checks ran at booking time on the store that suited their shape.
- **In this repo.** The [engine comparison appendix](../docs/engine-comparison.md) runs Arm B's workloads in an embedded graph store and an embedded columnar store. It shows how query shapes behave on one small static dataset, and nothing about production economics.

### 5. Single customer view: deterministic matching first

**Rung 4, deferred. Omnichannel retailer.**

- **Problem.** The same customer appeared in store, online and loyalty records under different identifiers.
- **Options.** Deterministic matching on shared identifiers such as loyalty ID and email; a probabilistic identity graph; a bought identity resolution product.
- **Choice and why.** Deterministic first, probabilistic deferred. Deterministic matches are explainable, reversible and cheap. A probabilistic graph's false merges join different people's records, which is a privacy failure as well as a data quality one.
- **Cost.** Under-merging: customers who never share an identifier across channels stay split, so the single view is incomplete.
- **Outcome.** A narrower single view, but one whose every match could be explained.
- **In this repo.** The [entity resolution note](../docs/entity-resolution.md) sets out the over-merge against under-merge trade-off. This dataset's nodes are already transactions, so resolution is not tested.

### 6. Workspaces resolved to organisations, rules before clustering

**Rung 4. Unicorn SaaS.**

- **Problem.** Product-led growth produced many free workspaces belonging to one organisation, and sales needed to see them as one account.
- **Options.** Email-domain rules; clustering on the collaboration graph of who shares with whom; a bought firmographic match.
- **Choice and why.** Domain rules first, with collaboration links to confirm or extend a match. Rules cover the common case and are easy to explain to a sales team. Clustering waited until the rules plateaued.
- **Cost.** Personal email domains and contractors break domain rules, so some organisations stay fragmented or are wrongly joined.
- **Outcome.** Sales worked from organisation-level accounts, with known gaps.
- **In this repo.** The ladder's own rule: climb a rung only once the one below has been measured and plateaued.

### 7. A graph neural network declined

**Rung 5, declined. Big tech.**

- **Problem.** A deep model, a graph neural network, was proposed for a problem already served by a boosted model.
- **Options.** Adopt the graph neural network; keep the boosted model; add graph features to the boosted model.
- **Choice and why.** The boosted model with graph features. It came close on quality, cost less to serve, met the latency budget, and its decisions could be explained feature by feature.
- **Cost.** Whatever the graph neural network would have found that hand-built features miss stays unmeasured.
- **Outcome.** The graph neural network was paused, not ruled out.
- **In this repo.** Arm D, a GraphSAGE model, against Arm B. On this dataset Arm D ranked below Arm B; the README gives the figures and their intervals. That says nothing about how much a stronger graph neural network might add.

---

## What the entries share

Each decision climbs only as far as the rung below justified, and most stop short of a graph database or a graph neural network. The reasons recur: explainability to a regulator, an analyst or a sales team; the cost of new infrastructure; and the finding that the valuable queries were aggregates.

- **Demonstrated.** Nothing in this log. None of it was measured here.
- **Suggested.** A pattern of practice that matches this repository's result on its dataset: graph-derived features earned their place, and the graph neural network did not.
- **Cannot be established here.** How common these decisions are. They are one author's experience, selected by that author.
