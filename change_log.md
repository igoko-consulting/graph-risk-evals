# Change log

Dated decisions. Figures live in `results/`; this file points to them rather than repeating them.

## 2026-11-19, session 1

**Graph store: LadybugDB 0.18.3, not Kùzu.** Kùzu was archived in October 2025 and its final release, 0.11.3, has no macOS arm64 build for Python 3.14. LadybugDB is the maintained fork, MIT licensed, with the same Cypher dialect, so queries in `graph/queries/` stay portable. 0.19.0 onwards ship macOS builds that link Homebrew's OpenSSL, which fails on a Mac without Homebrew, so 0.18.3 is pinned as the newest self-contained release. Revisit when a later release drops that dependency.

**Python 3.13.18, managed by uv.** Pinned in `.python-version`. 3.13 has wheels for every library in the planned stack. All dependency versions were released on or before 2026-11-05, at least two weeks before pinning, enforced with `uv pip compile --exclude-newer` (`make lock`).

**Data fetched from the PyTorch Geometric mirror for now.** No Kaggle token was available. SHA-256 checksums of the three CSV files are pinned in `loaders/elliptic.py`. The loader prefers Kaggle when a token exists and holds both routes to the same checksums, so the first Kaggle fetch verifies the mirror against the publisher's copy. Until then that verification is outstanding.

**Licence handling.** The dataset is CC BY-NC-ND 4.0. Data is never committed, and `results/` holds aggregate figures only, never per-node features, scores or labels. Recorded in `04-the-data/NOTES.md`.

**Arm A uses 93 features.** The PRD says Arm A uses "the 94 local features only, with the time-step column excluded". The dataset paper counts the time step among the 94 local features, and the PRD's own Phase 5 section says "93 local". Arm A therefore uses the 93 local features that remain once the time step is excluded. This clarifies the wording; it does not change any hypothesis or the intent of red line 3. Confirmed by the author before the data was loaded.

**Cross-step edges: none.** Answered on day one from the data, see `results/day-one-checks.json`. Time steps are disjoint graphs, so the leakage analysis in the PRD stands as written.

**Leakage gate status.** The future-edge and label-shuffle tests do not exist yet because no model features exist yet. `00-build/results_io.py` refuses to write any result flagged as using model features until they do. Session 1 results use labels and graph structure only.

**Library finding for Phase 2.** LightGBM 4.7.0 and XGBoost 3.4.1 install on macOS but fail to load without Homebrew's `libomp`. scikit-learn 1.9.1's histogram gradient boosting, torch 2.15.0 and torch-geometric 2.8.1 all load and run on Python 3.13 CPU with no system dependencies. **Gradient-boosted trees: scikit-learn's `HistGradientBoostingClassifier`.** Chosen by the author on 2026-11-19, before any arm was built, because a clean clone must run on a stock Mac with no system libraries installed by hand. LightGBM is the more common choice in practice; using it would mean asking every reviewer to install Homebrew first. Pinned when Phase 2 first imports it.

### Errata to the pre-registration

The pre-registration is hashed and tagged, so it cannot be corrected in place. These are recorded here before any arm has run.

1. **Specification version.** It cites `prds/prd-v2.md` v2.3. The PRD was at v2.4 when the tag was made. v2.4 added requirement traceability to the architecture table and pointed the junction diagram at the pre-registration for thresholds. No hypothesis, definition, period or kill criterion differs between the two.
2. **Tuning parity names two arms.** The protocol commitments say "Arms A and D receive the same tuning search method...". The PRD tuning contract says the protocol is identical across arms. It applies to every arm, A, B and D, as confirmed by the author on 2026-11-19.

### Integer rule for k

**k is the mean rounded to the nearest whole number, halves rounded up.** The pre-registration defines k as a mean, which is not a whole number, and a top-k queue needs one. The rule was chosen by the author after the mean was known (`results/k.json`), with no arm built, no model score produced and no test-step result seen. Rounding to nearest is the plainest reading of sizing a queue from historical case volume. `00-build/compute_k.py` applies it and writes both the mean and the integer.

## 2026-11-19, protocol fixed before any arm runs

Agreed by the author before any model was trained. The pre-registration leaves these open or unspecified; they are fixed here so none can be chosen after seeing a result.

### Tuning contract, identical for every arm

- **Search:** random search, 40 trials per seed, over one search space shared by every gradient-boosted arm. A seed fixes the sequence of candidate configurations, so Arms A and B evaluate the same 40 candidates for a given seed.
- **Space** (`HistGradientBoostingClassifier`): learning rate log-uniform 0.01 to 0.3; iterations 50 to 500; leaf nodes 15 to 127; minimum leaf size 10 to 200; L2 log-uniform 0.0001 to 10; feature subsampling 0.5 to 1.0; class weighting none or balanced. No internal early stopping.
- **Objective:** average precision on labelled nodes in validation steps 30 to 34, pooled.
- **Training window:** labelled nodes in steps 1 to 29. Final models are not refitted on validation steps.
- **Seeds:** 5 per arm. Each seed reruns the whole search, so seed spread includes tuning variance.
- **Recorded per arm:** trial count and fit time.

### Metrics

- **Precision at k:** for each test step, the 102 highest-scoring labelled nodes. Pooled over a period as true positives divided by 102 times the number of steps.
- **PR-AUC:** average precision. For H1, pooled over labelled nodes in the pre-shift period. For H3, the mean of per-step values, as pre-registered.
- **Scores:** each node's score is the mean of its 5 seed scores. Per-seed metrics are also reported.
- **Bootstrap:** 1,000 resamples of labelled nodes, drawn with replacement within each time step, paired across arms. 95% intervals are the 2.5th and 97.5th percentiles.

### Kill criterion metric

Arm D is built only if the 95% interval on Arm B minus Arm A, for precision at k pooled over pre-shift steps 35 to 42, lies wholly above zero. Post-shift results are reported but do not decide. If the criterion fires, Phase 3 continues without Arm D: label-budget curve for A and B, cost per true positive and limitations.

### Arm B structural features, and what "available at that time" means

- **Time scope.** Every graph feature for a node counts only neighbours in the node's own time step. An edge touching a later step can never change an earlier node's features. The future-edge test checks this with an injected cross-step edge.
- **In-degree and out-degree:** directed, same-step neighbours.
- **PageRank within the time step:** damping 0.85, uniform teleport over the step's nodes, dangling mass spread uniformly over the step, iterated in Cypher for exactly 100 iterations. Revised before any arm ran: the first draft stopped once no value moved by more than 1e-10, but a global stopping rule lets a change in one step alter how many iterations every other step gets, which the future-edge test would rightly flag. The final largest change is recorded in `results/leakage-tests.json`.
- **Two-hop neighbourhood size:** distinct nodes reachable within two hops ignoring direction, excluding the node itself.

### Two-stage score aggregates

- **Stage 1** is Arm A's tuned model for the same seed.
- **Training steps** are scored out of fold, over five contiguous blocks: 1 to 6, 7 to 12, 13 to 18, 19 to 24, 25 to 29. Each block is scored by a model trained on the other four, so no node is scored by a model that saw its own step. Some of those models are trained on later training steps; this touches training features only, never an evaluation step.
- **Validation and test steps** are scored by a stage-1 model trained on steps 1 to 29.
- **Aggregates:** mean and maximum of in-neighbour and out-neighbour stage-1 scores, computed in the graph store.
- **Own-label test:** flip the labels of sampled training nodes, rebuild, and assert their aggregates do not change. If this or either pre-registered leakage test fails, the feature is dropped, not adjusted.

### Leakage gate

The future-edge, label-shuffle and own-label tests run on the full data in every build, before any arm is tuned, using a fixed reference stage-one model (scikit-learn defaults, seed 0). The properties under test, neighbour scoping and the out-of-fold design, do not depend on the stage-one configuration. A test whose perturbation has no visible effect anywhere is treated as invalid and halts the build. `results_io.write_result` refuses any feature-derived result unless the gate passed at the same commit on the same data.

### Own-label test corrected before any arm ran

The first development run of the gate flipped 200 training labels drawn from all five stage-one blocks at once, and the flipped nodes' score aggregates moved. The cause was the test, not a leak. A node flipped in block 1 changes the stage-one models that score blocks 2 to 5, so a node in block 3 saw its neighbours' scores move because of other nodes' labels. The out-of-fold design intends exactly that: each block is scored using every other block's labels. It is not a node's own label reaching its own features, which is what the agreed test is meant to check. The test now flips 40 nodes within one block at a time, all five blocks in turn, so the model scoring the flipped nodes' block is untouched by the flip. No arm had been tuned or evaluated, and no performance figure existed, when this was found and changed. The development run's output was discarded; the gate result in `results/` comes from the corrected test.

### Smoke run before the official run

To exercise every code path before the long run, the full pipeline was run once with 2 trials and 2 seeds instead of 40 and 5. It printed a test-period comparison, which is unavoidable when testing the evaluation code end to end. Its output was discarded, and nothing in the protocol, features or evaluation was changed after it. The only change made afterwards was the thread count below, which affects runtime and not results.

### Thread count

`make` sets `OMP_NUM_THREADS` to the machine's performance cores. With all 12 cores, scikit-learn's fits ran several times slower on this Mac because threads placed on efficiency cores held up every iteration. Predictions from the same configuration are identical at 6 and 12 threads. The setting is recorded in each arm's tuning result.

### Reporting addition

Precision at k is reported with its ceiling for each period: the best any ranking could achieve when a step has fewer illicit labels than alerts. Added before any arm ran, after the synthetic-score check showed that several test steps, most of them post-shift, have fewer than 102 illicit labels.

### Phase 3, fixed now

- **Cost per true positive (modelled):** analyst cost €25 per alert, range €12.50 to €37.50 (±50%). This is an author assumption, about 20 minutes of first-line review at about €75 an hour fully loaded, not a sourced figure. Compute at €0.05 per vCPU-hour.
- **Arm D input:** the 93 local features only, so any relational signal D finds is learned rather than inherited from the provided aggregates.
- **Runtime:** the full tuning protocol takes priority over the 30-minute target. Measured runtime is recorded as a finding.
- **Write-up:** interpretation is drafted by Claude and marked as a draft for the author to edit. Every number in it is generated from `results/`.

## 2026-11-19, Phase 2 result

**Gate passed.** The official run was a clean clone at the commit recorded in every result file. Every leakage test passed and no feature was dropped (`results/leakage-tests.json`). Both arms were tuned under the full contract (`results/arm-a-tuning.json`, `results/arm-b-tuning.json`).

**Kill criterion did not fire.** Arm B's precision at k, pooled over the pre-shift steps, is higher than Arm A's, and the 95% interval on the difference lies wholly above zero (`results/evaluation-arms-a-b.json`, `kill_criterion`). As pre-registered, Arm D is built in Phase 3.

**Draft interpretation, for the author to edit.** The generated paragraph under Results in the README states the finding with its figures. The gain from graph features is small but clear before the shift, and larger in absolute terms after it, where both arms are far below the ceiling the labels allow. H1 and H2 need Arm D and are assessed in Phase 3.

**Presentation changes after the run, results untouched.** The Phase 2 chart gained a "best possible" line showing where steps have fewer illicit labels than alerts, and its labels were moved so they fit. One drafted README sentence claimed the post-shift intervals were wide. They are not, for precision at k, so it now says that the few post-shift labels cap precision at k. No result file was regenerated for either change.

## 2026-11-19, Phase 3 protocol, fixed before Arm D or any label budget runs

Written after the Phase 2 results for Arms A and B were known, and before any Arm D model or reduced-budget model existed. Where a rule below covers A and B, it is stated so it cannot be chosen to flatter a result already seen.

### Arm D, two-layer GraphSAGE

- **Input:** the 93 local features, standardised with the mean and standard deviation of every node in training steps 1 to 29. No labels are used for scaling.
- **Graph:** same-step edges only, used in both directions, matching Arm B's in- and out-neighbour features. Edges are filtered to the same step in code, so an injected cross-step edge cannot reach a message.
- **Architecture, fixed:** SAGEConv with mean aggregation to a hidden layer, ReLU, dropout, SAGEConv to one output. Two layers.
- **Training, inductive:** full-batch on the subgraph of training steps only. Validation and test nodes and edges are never seen in training. Loss is binary cross-entropy on labelled training nodes, optimiser Adam, no early stopping.
- **Search, same method and trial count as A and B:** random search, 40 trials per seed, 5 seeds, objective average precision on validation steps 30 to 34. Space: hidden size 32, 64 or 128; learning rate log-uniform 0.001 to 0.03; dropout 0 to 0.5; weight decay log-uniform 0.000001 to 0.001; epochs 50 to 200; class weighting none or balanced. Arm D's search space necessarily differs from the gradient-boosted space; trial count and compute are recorded so the comparison of effort is visible.
- **Leakage:** the gate also trains a reference Arm D and checks that its scores for earlier steps do not move under the injected future edges, and that no score moves when evaluation labels are shuffled.

### Label-budget curve (H4)

- **Budgets:** 5, 10, 25, 50 and 100 percent of the labelled nodes in training steps 1 to 29. The 100 percent point is the main run.
- **Sampling:** for each seed, one permutation of the training labels, stratified by class. Each budget takes the first share of it, so smaller budgets are nested inside larger ones. Every arm at a given seed and budget uses the same labels. Labels left out are treated as unknown; the nodes and edges stay in the graph.
- **Validation labels are kept in full at every budget.** In practice scarce labels would also mean a smaller validation set. This makes the curve somewhat optimistic at small budgets, and it is listed as a limitation.
- **Full protocol at each budget:** 40 trials, 5 seeds, every arm, with Arm B's stage one retrained on the reduced labels.

### Decision rules

- **H1** uses PR-AUC pooled over the pre-shift period, from seed-averaged scores: (B − A) / (max(B, D) − A). Undefined if neither B nor D beats A. Supported if the 95% bootstrap interval on the ratio lies wholly at or above 0.5. Rejected if it lies wholly below. Otherwise not separable from the threshold.
- **H2** as pre-registered: rejected only if D − B in pre-shift precision at k is at least 5 points and its 95% interval excludes zero.
- **H3:** the relative fall in mean per-step PR-AUC from the pre-shift to the post-shift period, per arm. For each pair of arms, the difference in relative fall gets a bootstrap interval. Supported if every simpler arm falls less than every more complex arm, with every pairwise interval excluding zero. Contradicted if any more complex arm falls less than a simpler one, outside the noise band. Otherwise not separable. Phase 2 already showed Arm B falling less than Arm A, recorded in `results/evaluation-arms-a-b.json`. This rule was written knowing that.
- **H4:** supported if B − A in pre-shift precision at k is larger at 5 percent than at 100 percent, with the 95% interval on that difference of differences wholly above zero. Contradicted if wholly below. Otherwise not separable. The same comparison is reported for D − A.
- **Bootstrap:** one shared set of 1,000 resamples, stratified by time step, paired across every arm and budget, drawn in the same order as Phase 2, so the A and B intervals match those already published.

### Cost per true positive, modelled

- **Analyst cost:** alerts reviewed (k per step times the steps in the period) times €25, with the range €12.50 to €37.50.
- **Compute cost:** all recorded fit time for the arm, tuning included, times the threads used, at €0.05 per vCPU-hour. Shown separately so its scale is visible.
- **Cost per true positive:** analyst plus compute cost, divided by true positives in the top k, pooled over the period. Reported for both periods.
- **Build days per arm** are an author-time cost the code cannot measure. They are recorded in `03-the-margin/NOTES.md` by the author, not generated.

### Phase 3 smoke run, before the official run

The Phase 3 stages were run once in miniature: 2 trials, 2 seeds, Arm D capped at 20 epochs, one 5 percent budget. It printed test-period comparisons including Arm D, which is unavoidable when testing the evaluation end to end. Its numbers come from models far smaller than the protocol's and were discarded. Changes made afterwards were presentation only: README wording ("gnn" casing, the compute-share sentence, and a limitations line that asserted every arm collapses after the shift, which now states the measured falls instead) and chart label layout. No protocol rule, feature, model or evaluation step changed.

## 2026-11-19, Arm D search space kept as fixed

After the Phase 3 headline was seen, Arm D's chosen learning rate or epoch count sat near the top of its range in three of five seeds (`results/arm-d-tuning.json`). The search space is kept as pre-registered in the Phase 3 protocol above. Widening it after test results are known would let the result choose the protocol. No exploratory rerun is planned. The README lists "whether a different GNN would close the gap" under what this cannot establish.

## 2026-11-20, Phase 3 result

The clean-clone build at commit `ef453b5` completed without error: the gates, every arm, the evaluation and the label-budget curve. Numbers are in `results/` and the README; none are restated here.

- **H2 stands.** The pre-registered prediction held. Arm D ranked below both A and B on pre-shift precision at k, outside the noise band in both comparisons.
- **H1 is supported only by construction.** B beat D in every resample, which makes the pre-registered ratio exactly 1. The README says so beside the outcome.
- **H3 is not separable.** D fell more than B after the shift, outside the noise band; the other two pairs are within it.
- **H4 is not separable.** The point estimate moved against the prediction, within the noise band. Reported alongside, D fell further behind A as labels shrank, outside the noise band.
- **Phase 2 results reproduced.** Every Phase 2 result regenerated identically apart from timings. PageRank's leakage-test maxima differ only at floating-point noise, far below the test tolerance.

**Provenance flag on two files.** `label-budget-curve.json` and `label-budget-tuning.json` carry `uncommitted_changes: true`. The cause is `README.md`, which the pipeline's own render step rewrote earlier in the same run, before the label budgets ran. `git status` on the clone showed no other change outside the excluded output paths, so no code differed from `ef453b5`. `README.md` is now excluded from the check, as the other pipeline outputs already were. The next clean-clone run regenerates both files with the corrected check.

**Presentation changes made after the results were seen; outcomes untouched.**
- H1 is labelled "by construction", with the reason.
- H3 shows its three pair intervals.
- The stale Phase 2 paragraph is replaced by a Phase 3 finding.
- The cost column says its bracket is the analyst-cost range, not a confidence interval.
- H4 shows the per-budget differences, the sign convention and the D minus A comparison this protocol said would be reported alongside.
- The label-budget chart notes that overlapping bands do not settle a comparison.

No result file was regenerated for any of these.

**Runtime.** The full protocol took hours on the clean clone, not the 30-minute target, as already accepted above. The run's own log is not a result file, so the figure is not quoted. A `record_runtime.py` stage now writes the measured total to `results/pipeline-runtime.json` on every `make all`.

## 2026-11-20, Phase 4 build, fixed before its official run

The Phase 3 gate passed with the clean-clone run above. Phase 4 builds the deliverables that need no production experience: evidence chains, the engine comparison appendix and a draft entity resolution note. The governance note and the decision log wait for the author.

### Evidence chains

- **Queue:** Arm B's top k labelled transactions per test step, from seed-averaged scores, as evaluated.
- **Chain:** the queued transaction's in-degree, out-degree and two-hop size, then its same-step link to the neighbour with the highest Arm A stage-one score, then that neighbour's strongest link onwards. Ties go to the lower node id. Only structure and stage-one scores are used, both known at scoring time; no label is.
- **Built in the graph store** with `graph/queries/evidence-neighbours.cypher` and the structural features Arm B already uses.
- **Truth check in code:** every degree, two-hop size and link is recomputed in SQL from the columnar store, and the stage halts on any disagreement. Sufficiency and actionability need a human; a seeded sample of 30 is written for the author to score.
- **Published as aggregates only.** The dataset's licence (CC BY-NC-ND 4.0) and `04-the-data/NOTES.md` rule out per-transaction outputs in `results/`. Full chains stay in `data/store/runs/`, which is git-ignored.
- **Arm D:** recorded as unable to produce a chain, with the size of its two-hop receptive field. No post-hoc explainer is used.
- **Stage-one scores** are now saved per seed by `run_arms.py`. For test steps they equal Arm A's scores, because stage one's last model is Arm A's tuned configuration trained on every training step; saving them makes that explicit rather than assumed.

### Engine comparison

- **Workloads:** Arm B's four, as queries. Degree and two-hop size run one query per step, neighbour-score aggregation and PageRank (100 fixed iterations) run over the whole graph.
- **Same work:** Cypher from `graph/queries/`, SQL in `graph/sql/`, outputs checked equal to within 1e-9 before any timing is kept. Neighbour scores are seeded random numbers, so no model output is involved.
- **Same conditions:** both stores file-based, built from one Parquet export, same process, same thread count, rows fetched as Python tuples in both. A first run, then 3 repeats with engine order alternated; medians reported.

### Smoke runs before the official run

Both stages were run once on local data from an earlier build. The evidence-chain smoke run printed test-period aggregates. One drafted README sentence depends on one of them: it says the chain is context rather than the reason only when more than half of Arm B's queue is also queued by Arm A. The smoke numbers were discarded. No definition above changed after either smoke run.

## 2026-11-20, Phase 4 result

A clean clone at `edc58a2` ran `make all` to completion. Every result file records that commit with no uncommitted changes, and the evidence-chain result also passed the leakage-gate check. The figures live in `results/` and the README; none is restated here.

- **Evidence chains:** every fact in every chain matched the SQL recomputation. Most of Arm B's queue is also Arm A's queue, so the README says chains are context rather than the reason, as the rule fixed before the official run required.
- **Engine comparison:** all four workloads returned matching outputs in both engines before any timing was kept.
- **Earlier results reproduced.** Every Phase 2 and Phase 3 result regenerated identically apart from timings. Modelled cost per true positive moved only in its fourth decimal place or beyond, because it includes measured tuning time; the rounded figures are unchanged.
- **Runtime** is now a result: `results/pipeline-runtime.json`.
- **First attempt lost to the network.** The dataset mirror reset the connection during the download. The run was restarted from a fresh clone at the same commit, with no code change.

**Presentation change after the results were seen; outcomes untouched.** The engine table now names its workloads "Two-hop size" and "PageRank" rather than generating "Two hop" and "Pagerank" from code names, and prints an output difference of zero as 0. `README.md` and `docs/engine-comparison.md` were re-rendered from the copied results; no result file was regenerated.

## 2026-11-20, queue-size chart and the write-up

**Queue-size chart, deliverable 16.** Precision and recall at every queue size from 10 to 500 per step, for each arm, before and after the shift. It is drawn from the queue curve already in `results/evaluation-phase-3.json`, so no result was regenerated. The curve had been published, and seen, before the chart was designed.

- **No intervals.** The published curve has point estimates only, so the chart and its table say they do not compare arms; comparisons stay at k, on paired resamples. Bootstrap bands at every queue size were considered and not added, because they need a new evaluation stage and a full clean-clone rerun of several hours. Decided by the author.
- **Both periods shown.** Showing only the pre-shift period would have left out the collapse after the shift. Decided by the author.
- **Table sizes.** The round sizes in the README table, 50, 200 and 500 per step, were picked after the curve had been seen. They are for reading and decide nothing.

**Runtime line.** The README now reports the measured runtime from `results/pipeline-runtime.json`. It is rendered again after `record_runtime.py`, so the line reports the run that produced it rather than the one before.

**Write-up, PRD v2.5, requirement 21.** At the author's request the README is restructured for a reader arriving cold: what kind of project this is, the decision matrix, then the key decisions with their reasoning, cost and alternatives, then results and limitations. It states that this is a learning project run as a two-day discovery sprint, as the author described it, and adds the critical user journeys appendix that the PRD places in the README. Two limitations are added: what a longer project would test, and that the evidence-chain review is not yet scored. Only hand-written text changed; no generated number did.

## 2026-11-20, audit fixes: the leakage gate's remedy and figures typed by hand

An independent read-only audit of the red lines, made after every result was published, found two gaps. Both are fixed in code and text. No result file was regenerated and no outcome changes.

**Gate 2 dropped more than the pre-registration allows.** Any Arm B feature that moved under a leakage test was dropped, and the gate still passed. The pre-registration allows dropping only for the two-stage score aggregates, and red line 2 says no result is written while a leakage test fails. `leakage_gate.py` now drops only a score aggregate that moves. Any structural feature that moves, or any movement in Arm D's reference scores, fails the gate and halts the build. The README had said no result is written if any test fails, which overstated the old code; it now states the rule. The published gate, run under the old rule at `edc58a2`, moved no feature and dropped nothing, so it passes the new rule too.

**Figures typed by hand.** The README quoted the analyst-cost assumption, feature counts, trials, seeds, resamples, queue sizes and the runtime target in hand-written prose, and `03-the-margin/NOTES.md` repeated the cost assumptions. They now sit in value spans that `render_readme.py` fills from `results/`, so they cannot drift from the run. The renderer refuses to say the arms were tuned equally if their trial or seed counts differ. The leakage line under the README's limitations is now generated from `results/leakage-tests.json`. Figures with no source in `results/` were removed rather than typed: the unsourced payments-margin figure, the Phase 5 dataset size, which stays in the PRD, and the user-journey RICE scores, which are the author's estimates and also stay in the PRD. The README's status line now says what is generated. `03-the-margin/NOTES.md` joins the pipeline outputs that do not count as uncommitted code, now listed once in `paths.py`.

## 2026-11-20, audit follow-up: disclosures, citation and caveats

The audit's lower-severity findings. Wording, generated text and checks only; no result file was regenerated and no outcome changes.

**The evidence-chain sentence was written knowing the real share.** The Phase 4 entry on smoke runs says their numbers were discarded. They were, but the evidence-chain smoke run used scores from an earlier full build, which regenerate identically, so the share it printed was the share later published. The "more than half" condition on that README sentence was written knowing it would hold. The sentence describes the published share and decides nothing, but the earlier entry understated what was known when it was written.

**Prior work cited.** The README and the generated Phase 3 finding now cite the published comparison (Weber et al., 2019). The finding had said the comparison was cited in the pre-registration; the pre-registration describes it without a citation, and it cannot be edited without breaking its hash.

**k described correctly.** The README said k was the mean per training step, and the queue-size notes said k was fixed from training steps. It is computed over the training and validation steps, as `results/k.json` and the pre-registration say.

**Caveats beside the claims.** The README now states, next to each claim: the bootstrap holds each arm's scores fixed and treats transactions within a step as independent, so it leaves out seed-to-seed variation and may be too narrow; each arm's scores are the mean of its seeds' models, which a deployment would not run; cost per true positive counts labelled transactions only; the leakage tests use one reference model on every training label; and the Phase 2 kill criterion is reported, not enforced by the pipeline. The notes under the results gain the seed-by-seed range of B minus A. That range was added after every result was published and decides nothing.

**Settings typed into generated text.** Arm A's feature count, the resamples, the shift step, the H2 bar, the label budgets shown, the queue grid and the steps with known labels are now read from `results/` rather than typed in `render_readme.py`. The H1 evidence no longer types its threshold; it says a majority is needed, as the hypothesis states. The Phase 3 ranking sentence now says it ranks point estimates. No generated number changed.

**Checks that survive `python -O`.** Bare `assert` statements in `00-build/` are now `require()` calls, which Python does not strip, and the two module-level checks in `loaders/elliptic.py` now raise the loader's `ContractError`.

**PRD v2.5 was written in place.** It went into `prds/prd-v2.md` (f55b090) rather than a new file. Versions v2 to v2.4 were drafted before the repository existed and first committed together; v2.5 is the first change to the file after it was committed, and git keeps v2.4 at `0511c14`. Moving v2.5 to its own file would change which file `CLAUDE.md` names as the working specification, so it is left for the author to decide.

## 2026-11-20, Gate 2 tightened to the PRD's rule

The audit fix above let a score aggregate that moved under any of the three leakage tests be dropped. The PRD's Gate 2 row says a failure of either the future-edge or the label-shuffle test fails the build, and red line 2 says no result is written while either fails. The pre-registration's remedy, dropping rather than adjusting, covers the two-stage aggregation leak, which is what the own-label flip tests. At the author's request, `leakage_gate.py` now fails the gate if any feature moves under the future-edge or label-shuffle test, and drops a score aggregate only if it moves under the own-label flip alone. The published gate moved no feature under any test, so it passes this rule as well; no result was regenerated and no outcome changes.

## 2026-11-20, review of the audit follow-up

A line-by-line review of the follow-up above found four small faults. All are fixed; no result was regenerated and no published figure changes.

- **H1's rule restated.** The README said H1 needs "a majority". The rule is that the whole interval lies at or above half, so exactly half counts and a majority on the point estimate alone does not. The text now says so.
- **H1 and H2 bars built from their constants.** `evaluate_phase3.py` typed "0.5" and "5 points" into its outcome and definition text, apart from the constants its decisions use. The text is now built from those constants. It comes out word for word as published, so the results still match the code.
- **Queue table divider.** The divider row counted every table size, so the table would have broken if k ever equalled one of them. It now counts the columns shown. With k at 102 the table is unchanged.
- **Dropped-feature sentence.** It would have said a feature's "own training labels" were flipped. The labels belong to the transactions, and it now says so. It shows only if a feature is dropped, which has not happened.
- **Leakage-test limits restated.** The README said the tests use a reference model "trained on every training label". Training steps are scored out of fold, so the README now says the tests run one reference configuration at the full training-label budget. The same line had the own-label wording above, and now matches it.
