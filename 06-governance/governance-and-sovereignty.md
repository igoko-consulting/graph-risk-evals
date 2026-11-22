# Governance and sovereignty

[in review]

The first half describes what this repository does with its data, and every line of it can be checked in the code. The second comes from the author's production work, not from the dataset, which has no geography, jurisdictions or account holders.

## Data handling in this repository

- **Public data, bound by its licence.** The Elliptic Data Set is published under CC BY-NC-ND 4.0. It is never committed: `data/` is git-ignored and `loaders/` fetches it. See [`04-the-data/NOTES.md`](../04-the-data/NOTES.md).
- **Aggregates only.** `results/` holds aggregate figures, never per-node features, scores or labels, because the licence does not allow redistribution.
- **Fixed inputs.** Both fetch routes must match the SHA-256 checksums pinned in `loaders/elliptic.py`.
- **Lineage as a file.** Every result records its commit, whether the working tree was clean, the pre-registration hash and each data file's checksum. In an enterprise this belongs in a data catalogue with lineage support. The repository names that boundary rather than building it.
- **References by hash.** The author's evidence-chain scores are stored against a SHA-256 of each chain, not the chain itself, so the scores live in git while the transactions stay out. The hash is a reference, not anonymisation, which is the distinction drawn below.

## Sovereignty and residency, from production

Drawn from work in green tech, telecoms, retail, travel, the creative industries, digital design-and-build agencies and finance. None of it comes from this dataset, which is a Bitcoin transaction graph rather than payments data, and none of it was tested here.

- **The tension.** The edges that carry most signal often cross borders: between countries, regions and continents, and between specific sites such as offices. In travel, the booker, the supplier and the payment often sit in different jurisdictions, so every booking is a cross-border link, and that link is where fraud patterns show. Residency rules constrain where those edges may be joined.
- **What could not move.** Customer data, finance records, behavioural records, telemetry, network usage, research and development data, employee data and general operational data.
- **What teams did instead.** Raw data stayed where it was. Only data that had been anonymised, obfuscated, hashed or rolled up to aggregates crossed a boundary, checked first so that no customer details remained in readable form. Hashing used one consistent key, held centrally, so records still joined across regions, and in practice the result was often treated as de-identified.
- **Why hashing is not anonymisation.** Under GDPR a hashed identifier is pseudonymised, not anonymised, so it is still personal data, and an unsalted hash of an email address or phone number can be reversed by lookup. A graph sharpens the tension: a key stable enough to join records across a border is stable enough to identify a person.
- **What it cost.** Mostly time and organisation, rarely signal. Analysis took longer, each cross-border question needed extra process, and the safeguards needed new teams and workloads to run them. Signal was lost only at the edges, when an investigation could not follow a link back to the raw record across a border. That cuts against the specification, which frames residency as a limit on joining signal.
- **Proving who could see what.** Who could was shown through role-based access levels with periodic access reviews, which proved who could not see data as well as who could. Who did was shown through processing and access logs, lineage and session replay, combined forensically to reconstruct what happened. The same logs surfaced key behaviours, fraud, errors, the limits of system boundaries, and breaches or attempted breaches, and fed system improvements.
- **What the logs missed.** Logging stopped at system boundaries, so extracts, business intelligence dashboards and exported reports went unrecorded and left blind spots in any reconstruction. The replays and access logs also held personal data themselves, so residency rules applied to the logs too, which made them harder to combine centrally.
- **Where lineage lived, and where it stopped.** Hosted locally or in the cloud, with access privileges and residency settings chosen to meet each regulation, in tools from in-house builds to commercial catalogues, cloud pipeline catalogues and business intelligence logs. They traced source tables and pipelines well, and derived data such as features, scores and extracts poorly. Where lineage was missing, a team could not show whether a dataset had crossed a border, so the safe assumption was that it had, and that assumption added review time.
- **Why fragmented rules constrain cross-border fintech.** Data residency laws, national sovereignty requirements and government cloud regimes such as FedRAMP each draw their own boundary, so a cross-border graph is only as joinable as the strictest rule on each of its edges.

## What this establishes

- **Demonstrated.** The repository publishes only aggregates and hashes, starts every run from fixed bytes, and records lineage for every result. Each is checkable in code.
- **Suggested.** Nothing in this note. The production patterns above are the author's experience, not findings.
- **Cannot be established here.** Anything about residency, access control or cross-border joins. The dataset has no geography or jurisdictions, and the repository has no access control to test because its data is public.
