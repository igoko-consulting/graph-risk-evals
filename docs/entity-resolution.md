# Entity resolution: the layer beneath the graph

[in review]

## Why it comes first

A fraud graph's nodes are meant to be entities: people, accounts, devices, businesses. Source systems record events, not entities, and their identifiers are partial, inconsistent and sometimes deliberately varied. A name is spelled three ways, a device is shared, a phone number is reused, an account is reopened under a new reference. Entity resolution decides which records refer to the same real-world entity, and every graph feature sits on top of that decision.

Degree, two-hop reach, PageRank and community membership all count nodes. They inherit the resolution layer's errors before any model sees them, and no amount of tuning downstream can recover a link that resolution never made or remove one it made wrongly.

## Over-merge against under-merge

- **Under-merge** splits one entity into several nodes. A mule network then looks like many unrelated, low-degree accounts, and the ring structure that graph features exist to find disappears. Organised fraud exploits this on purpose by varying identifiers.
- **Over-merge** joins different entities into one node. A shared attribute such as a family address, a corporate device pool or a payment processor's account turns unrelated customers into a single hub. Degree and centrality inflate, false positives rise, and an innocent customer inherits a neighbour's risk.
- **The costs are not symmetric.** Under-merge mostly costs recall, and it does so silently. Over-merge costs precision and investigator time, visibly, and can harm customers. In a regulated setting it is also an explainability problem: the evidence chain an investigator sees rests on a merge nobody can defend.

The merge threshold is therefore a product decision with a cost on each side, not a data-cleaning detail. It should be set from an explicit cost per error, on held-out data, and revisited when the population shifts. Like the alert budget here, it should be fixed before anyone sees the result.

## What a working layer needs

- **Two kinds of matching, each with a recorded confidence:** deterministic rules for exact identifiers, probabilistic matching for fuzzy ones.
- **Merges stored as versioned, reversible facts with lineage,** so any graph feature can be traced back to the records and the rule that joined them.
- **Evaluation that reports both errors:** a labelled set of known same-entity and different-entity pairs, scored for over-merge and under-merge separately rather than as one accuracy figure.
- **Temporal correctness:** a merge made today must not rewrite a historical feature value, for the same reason the leakage gate here forbids future edges.

## Why it is not demonstrated here

The nodes in this dataset are transactions, not entities, and their features are anonymised. There are no names, addresses, devices or account identifiers to resolve, so there is nothing to merge or split, and no ground truth for whether two transactions share an owner. Any entity resolution built on this data would be invented.

The planned Phase 5 extension adds wallet addresses, which are closer to entities. Address clustering on a public blockchain is a different problem from customer resolution in payments, though, and it is left as a module to build, not a claim to make.

## What it means for the results

Arm B's graph features were computed on a graph whose nodes needed no resolution. On payments data the same features would carry the resolution layer's error, in a direction set by its merge threshold. That is one more reason the results here do not transfer to payments directly.
