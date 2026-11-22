# Governance and sovereignty

_Draft for the author to edit._

One page, as the specification sets. The first half describes what this repository does with its data, and every line in it can be checked in the code. The second half comes from the author's production work, not from the dataset, which has no geography, no jurisdictions and no account holders.

## Data handling in this repository

- **Public data, bound by its licence.** The Elliptic Data Set is published under CC BY-NC-ND 4.0. It is never committed: `data/` is git-ignored and `loaders/` fetches it. See [`04-the-data/NOTES.md`](../04-the-data/NOTES.md).
- **Aggregates only.** `results/` holds aggregate figures, never per-node features, scores or labels, because the licence does not allow redistribution.
- **Fixed inputs.** Both fetch routes must match the SHA-256 checksums pinned in `loaders/elliptic.py`, so every run starts from identical bytes.
- **Lineage as a file.** Every result records the commit that produced it, whether the working tree was clean, the pre-registration hash and the checksum of each data file. In an enterprise this belongs in a data catalogue with lineage support. The repository names that boundary rather than building it.
- **References by hash.** The author's evidence-chain scores are stored against a SHA-256 of each chain, not the chain itself, so the scores live in git while the transactions stay out. It is a small instance of the pattern described below.

## Sovereignty and residency, from production

Drawn from work in green tech, telecoms, retail, travel, the creative industries, digital design-and-build agencies and finance. None of it comes from this dataset, which is a Bitcoin transaction graph rather than payments data, and none of it was tested here.

- **The tension.** The edges that carry most signal often cross borders: between countries, regions and continents, and between specific sites such as offices. Residency rules constrain where those edges may be joined.
- **What could not move.** Customer data, finance records, behavioural records, telemetry, network usage, research and development data, employee data and general operational data.
- **What teams did instead.** Raw data stayed where it was. Only data that had been anonymised, obfuscated, hashed or rolled up to aggregates crossed a boundary, and it was checked first so that no customer details or identifiers remained.
- **What it cost.** Analysis took longer. Each cross-border question needed extra process, and the safeguards often needed new teams and workloads to run them.
- **Proving who could see what.** Logs covered processing, access, access levels and lineage, so a team could show who had access to what and, as important, who did not. Session replay, and the ability to combine logs forensically, let a team reconstruct what happened. The same logs surfaced key behaviours, fraud, errors, the limits of system boundaries, and breaches or attempted breaches, and fed system improvements.
- **Where lineage lived.** Hosted locally or in the cloud, with access privileges and residency settings chosen to meet each regulation. Tools ranged from in-house builds to commercial data catalogues, the catalogues built into cloud pipeline services, and the logs of business intelligence tools.
- **Why fragmented rules constrain cross-border fintech.** Data residency laws, national sovereignty requirements and government cloud regimes such as FedRAMP each draw their own boundary, so a cross-border graph is only as joinable as the strictest rule on each of its edges.

## What this establishes

- **Demonstrated.** The repository publishes only aggregates and hashes, starts every run from fixed bytes, and records lineage for every result. Each is checkable in code.
- **Suggested.** Nothing in this note. The production patterns above are the author's experience, not findings.
- **Cannot be established here.** Anything about residency, access control or cross-border joins. The dataset has no geography or jurisdictions, and the repository has no access control to test because its data is public.
