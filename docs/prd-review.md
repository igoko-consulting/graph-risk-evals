# PRD review, cross-model

Two independent reviews of `prds/prd-v1.md`, each asked to act as a sceptical CPTO and then as a staff engineer in graph and ML systems. Fresh chat, identical prompt, identical attachment, no follow-up argument. Prompt and both replies verbatim in `PROMPTS.md`.

**Model A:** GPT-6. **Model B:** Claude Opus 5.5.

Both returned the same final verdict: ship with changes, not as specified.

---

## Invalidating errors

Found by Model B only. All three verified against the dataset documentation and the originating paper before action.

| # | Finding | Why it invalidated v1 | Action |
|---|---|---|---|
| 1 | Arm A was not graph-free. Of 166 node features, 94 are local and 72 are one-hop neighbour aggregates built as a manual proxy for one round of message passing | The baseline already contained graph information, so H1 was wrong by construction | Arm A reduced to the 94 local features, time-step column excluded. Asserted in code |
| 2 | The headline comparison is already published. The originating paper reported a random forest beating a two-layer GCN on illicit F1, with collapse after the step-43 regime shift | v1 read as a first encounter with the dataset | New section: prior results and what this adds. Reframed as a stricter replication |
| 3 | Label-derived graph features leak. Time steps are disjoint, so hop-distance-to-a-confirmed-bad-actor at test time can only use labels from that same test step | Arm B's score would be inflated and the comparison void | Label-distance features removed. Replaced with two-stage neighbour aggregates of the model's own predicted scores. Second leakage test added: shuffle test labels, assert no feature changes |

---

## Where both models agreed

Acted on without further debate.

| Issue | Both said | Action |
|---|---|---|
| Pre-registration not falsifiable | "Majority", "enough", "less" and "noise band" are undefined | All four defined numerically. Noise band defined as a bootstrap CI including zero |
| Operating point unresolved | k cannot remain open when results are generated | k = mean illicit labels per step across training steps, computed before any test step is read. Full PR curve also published |
| Equal tuning is not a budget | Equal trials does not mean equal optimisation | Tuning contract specified: search method, trial count, validation window, metric, early stopping, class weighting, seeds. Trials and compute both recorded |
| Cost model weak | Compute per scored entity cannot separate the arms | Replaced with cost per true positive, dominated by analyst cost per alert, with sensitivity range. Build days logged per arm |
| Scope is not five days | Eight P0 requirements plus a front end plus a governance pack | Cuts and demotions below. P0 reduced to the experiment and its integrity checks |
| Statistical evidence undefined | Single seed, few illicit labels per step | 5 seeds, paired bootstrap, CIs on every reported difference |
| Unlabelled population ambiguous | 77% unlabelled, and unlabelled is not legitimate | Metrics on labelled nodes only, stated. Unlabelled share of top-k reported separately |

---

## Where the models disagreed

| Question | Model A | Model B | Decision and why |
|---|---|---|---|
| Operating point | Top 1% of scored entities | Mean illicit labels per step from training steps | **B.** Computed from data before test, and mirrors how operations teams size queues from historical case volume. A's 1% is defensible but arbitrary |
| Explainability coverage | Keep 100% coverage as P0 | Arm B only. SHAP over anonymised features explains nothing | **B.** Arm D's inability to produce a meaningful evidence chain is recorded as a finding about the method, which is more useful than a weak explanation |
| Governance pack | Retain, but do not make it a workstream | Cut to one page, keep sovereignty, drop the autonomy split | **B, and they converge.** One page plus the sovereignty note. The autonomy split is production theatre on a static experiment |
| CUJ and RICE table | Not raised | Cut. Process theatre with one scorer | **Split.** Table retained, moved to an appendix, with single-scorer status stated. The hiring-manager story deleted: naming recruiters as the audience reframes every honesty commitment as positioning |

---

## Cuts, part-cuts and demotions

Reviewers proposed four full cuts. One was taken in full, one part-cut, one demoted, one deferred.

| Item | Reviewers | Decision | Reasoning |
|---|---|---|---|
| Language-model explanation summaries | Both: cut | **Cut** | Adds a model dependency and a second evaluation problem, faithfulness, which is not this repo's question. A deterministic structural reason is clearer and unattackable |
| Database engine benchmark | Both: cut | **Part-cut** | The production decision it reproduces is genuinely useful, so it stays in the decision log as lived experience. The benchmark becomes a two-hour P2 appendix with confounds listed. At 234,000 edges it would largely time start-up and caching |
| Interactive threshold explorer | Both: cut, replace with static charts | **Demoted to P2** | The cost identified was about sequence, not the artefact. A polished demo beside incomplete methodology signals presentation over evidence. The same explorer after the method is solid signals the opposite |
| Unsupervised arm, Arm C | Both: cut or defer | **Deferred to P2** | On small disjoint per-step graphs scored against incomplete labels the result is noisy and hard to interpret, and it does not serve the central question |
| Golden set and labelling protocol | B: cut as theatre | **Cut** | The dataset is static and nobody confirms anything. The label-budget curve answers the real scarcity question instead |

---

## Additions taken from the reviews

| Addition | Source | Why |
|---|---|---|
| Label-budget curve at 5, 10, 25, 50, 100 percent of training labels | B | Tests the PRD's own claim about label scarcity. Not well covered in the published comparisons. Half a day once the pipeline is parameterised |
| Cost per true positive, analyst time dominant | Both, B sharper | Rescues the economics goal, which compute-per-entity could not support |
| Prior results and what this adds | B | Removes the first-encounter impression and reframes the work as a stricter replication |
| Decision matrix as README centrepiece | A | Turns a model comparison into a product artefact: finding, decision, evidence |
| Demonstrated, suggested, cannot be established | A | Separates the three honestly, rather than one undifferentiated limitations paragraph |
| Pre-registration hash enforced by the pipeline | B | Converts a promise into a mechanism. Roughly twenty lines |
| Second leakage test: shuffle test labels | B | Catches label-derived features, which the original future-edge test would not |

---

## Rejected or softened

| Suggestion | Source | Position |
|---|---|---|
| Remove the CUJ and RICE table entirely | B | Softened. It is the author's long-standing PRD format and the document is also a writing sample. Moved to an appendix with single-scorer status stated |
| Remove the take-rate framing from H2 | B | Accepted in the hypothesis, retained in Context as commercial motivation rather than as a tested quantity. The data carries no transaction value, so it cannot be tested here |
| Keep the full governance pack | A | Softened to one page plus the sovereignty note |

---

## What both said not to touch

Preserved unchanged: the escalation ladder as the organising argument; the commitment to publish a null result; equal tuning as a principle; the time-aware split; the leakage check as a build-failing test; "if B does not beat A, do not build D"; the thin slice first with versions pinned; the static, no-server, laptop-CPU constraint; the explicit non-goals; the separation of production experience from experimental evidence; and the data sovereignty note, which both identified as the most differentiated content in the document.

---

## Process note

The review cost roughly one hour against a five-day build. It caught three errors that would have made the experiment unpublishable, and it removed about a day and a half of work that did not serve the central question.

Where the models disagreed, the disagreement is recorded rather than resolved silently. Model B's technical pass was materially stronger, which is consistent with it holding specific knowledge of this dataset. That is worth noting as a property of the review, not as a general ranking.
