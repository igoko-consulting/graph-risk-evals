# Prompts and model replies

Prompts given to models during this project, with the replies verbatim.

## PRD review, cross-model

Two independent reviews of `prds/prd-v1.md`, run before the repository existed. Each was a fresh chat with the prompt below and `prds/prd-v1.md` attached, and no follow-up. What was acted on, and why, is in [`docs/prd-review.md`](docs/prd-review.md).

- **Model A:** GPT-6.
- **Model B:** Claude Opus 5.5.

The prompt is copied from [`docs/prd-review-prompt.md`](docs/prd-review-prompt.md). The replies are as copied from each chat, unedited. Copying dropped the chat apps' headings and table formatting, so some lines run together when this page is rendered; the raw file keeps every line.

### The prompt

You are reviewing a PRD for a public, personal engineering lab. I want it challenged, not improved politely.

**Assume the premise is sound.** The author is a senior product leader with production experience in fraud and payments, graph databases and data platforms, but no graph machine learning. The repo exists to close that gap honestly and to test when graph methods stop paying for themselves. Do not spend the review questioning whether the project should exist.

**Hard constraints. A recommendation that breaks one of these is not useful.**

- One person, roughly five days of focused work, alongside a job search.
- Public repository, public data only, no employer data.
- Static: no server, no hosting cost, no API keys at view time.
- Runs on a laptop CPU.
- The deliverable is an argument with evidence, not a product.

**Do two separate passes in one reply.**

**Pass 1: as a sceptical CPTO.** You are deciding whether this is worth the author's week, and whether it would change your view of them as a candidate for a principal product role in regulated fintech.

**Pass 2: as a staff engineer who runs graph and ML systems in production.** You are deciding whether the method is sound and whether the results would survive your scrutiny.

**For each pass, give me exactly this:**

1. **The five most serious problems, ranked.** For each: what is wrong, what it would cost if unaddressed, and the smallest change that fixes it. Not a list of everything that could be better.
2. **What you would cut.** Name at least two things in the PRD that should be removed or deferred, and say what the author gains by cutting them. You must name something; "nothing" is not an acceptable answer.
3. **The one claim most likely to be attacked**, and how you would attack it.
4. **What would make you reject this outright** as evidence of the author's judgement.
5. **What is already good enough and should not be touched.** Be specific, because the author will otherwise over-revise.

**Rules for your answer.**

- Rank by consequence, not by how easy the issue is to spot.
- Do not suggest anything that needs more than half a day unless it replaces something already in scope.
- Do not propose additional datasets, frameworks, infrastructure or features unless you are cutting something to pay for them.
- If the pre-registration, the kill criteria or the equal-tuning requirement are weak, say so first. They carry the repo's credibility.
- Be concrete about numbers. If an operating point, a threshold or a cost assumption is arbitrary, say what it should be instead and why.
- If you think the honest answer is that the result will be uninteresting, say that plainly and say what would make it interesting.

End with a single line: **ship as specified, ship with the changes above, or do not ship.**

---

### Model A reply: GPT-6

PRD Review: graph-risk-evals

Document reviewed: PRD v1, 19 November 2026
Review basis: The attached PRD, assessed against the stated five-day constraint and the intended purpose of a public engineering lab.

My overall assessment: the premise is strong, the product judgement is visible, but the PRD currently describes a substantially larger experiment than the author can credibly execute in five days. More importantly, several methodological decisions that determine whether the results are trustworthy remain unresolved.

There is a potentially excellent portfolio piece here. It could demonstrate something more valuable than familiarity with graph ML: the judgement to know when an expensive technical capability is warranted, when it isn’t, and how to establish that with evidence.

But the current PRD risks demonstrating the opposite: an experienced product leader who understands the commercial question but has not yet sufficiently constrained the experiment needed to answer it.

⸻

PASS 1 — Sceptical CPTO

My perspective: I’m considering whether to invest a week of this person’s time and whether the finished work would materially strengthen my assessment of them for a Principal Product Manager or equivalent senior product leadership position in regulated fintech.

1. The five most serious problems, ranked

1. The pre-registration isn’t sufficiently falsifiable

What is wrong

The document makes a good commitment to pre-registration, but the hypotheses are not yet sufficiently precise to prevent interpretation after seeing the results.

H1:

Graph-derived features added to a tuned gradient-boosted baseline will capture the majority of the available detection lift.

What constitutes the majority?

H2:

A graph neural network will not beat that arm by enough to justify its modelled cost per decision at a sub-one-percent take rate.

What constitutes enough?

The document then introduces a five-percentage-point precision improvement as the threshold for rejecting H2.

That’s an enormous improvement in a fraud detection context, and there is no rationale for selecting it.

More importantly, the five-point threshold is not necessarily aligned with the commercial value of the improvement.

H3 predicts that simpler models degrade less after a regime shift. There is no numerical definition of less.

The kill criteria also need tightening. “Within the noise band” is not operationally defined.

What it costs if unaddressed

This is the central credibility problem.

A technically competent reviewer can reasonably conclude that the author has designed hypotheses that are easy to reinterpret after observing the results.

That undermines the entire proposition of an honest public experiment.

It also weakens the strongest potential hiring signal: intellectual honesty.

Smallest change

Spend two hours resolving the pre-registration.

Define:

* H1: What percentage of the incremental lift does Arm B capture relative to Arm D?
* H2: What minimum improvement would justify the additional complexity?
* H3: What numerical difference constitutes materially lower degradation?
* Statistical uncertainty: What constitutes evidence of a meaningful difference?
* Kill criteria: What exact conditions prevent an arm from proceeding?

I would replace the arbitrary five-percentage-point threshold with a commercially interpretable minimum detectable improvement.

For example, define the improvement in terms of additional confirmed illicit entities detected within the same fixed review capacity.

If the experiment cannot support that level of precision, explicitly acknowledge it.

My verdict: Do not generate the first result until this is resolved.

⸻

2. Five days is not credible against the current scope

What is wrong

The PRD describes several distinct projects:

1. A reproducible graph ML experiment.
2. A comparative database benchmarking exercise.
3. An explainability and evidence-chain evaluation.
4. A static interactive front end.
5. A governance and regulatory documentation package.
6. A production decision log.
7. A cost-modelling exercise.

Each is reasonable independently.

Together, they are not a five-day project for someone learning graph ML.

The particularly concerning part is that the requirements classify many of these as P0.

The static front end is P1, but the query-shape comparison and evidence-chain requirements are P0.

Even the five-day estimate doesn’t appear explicitly in the PRD as a delivery constraint.

What it costs if unaddressed

The likely outcome is a collection of partially implemented experiments, weak documentation and a polished front end.

That would be worse than a smaller, completed experiment.

For a Principal PM candidate, I care about the ability to make difficult prioritisation decisions, not the ability to accumulate impressive-sounding deliverables.

Smallest change

Make the first release answer one question:

When does adding graph-derived information justify its additional operational and economic cost in financial crime detection?

Keep:

* Tuned tabular baseline.
* Graph-derived features.
* GNN comparison.
* Time-aware evaluation.
* Leakage checks.
* Modelled economics.
* A clear written conclusion.

Defer:

* Database engine benchmark.
* Interactive threshold explorer.
* Language-model-generated explanations.
* Governance documentation beyond a concise limitations and data-handling note.

The five-day constraint should be explicit in the PRD.

If an experiment takes longer than half a day and doesn’t directly strengthen the central argument, it doesn’t belong in v1.

⸻

3. The economics are not yet decision-grade

What is wrong

The PRD correctly recognises that detection lift without economics is insufficient.

However, the cost-per-decision metric is currently too weak to support the intended commercial argument.

The PRD proposes:

Modelled compute and storage per scored entity.

It also requires a sensitivity range of at least ±50%.

That is not enough.

The cost of a fraud detection decision isn’t simply infrastructure divided by the number of entities scored.

There are at least four relevant components:

* Compute and storage.
* Data preparation and graph maintenance.
* Model development and operational maintenance.
* Human investigation generated by false positives.

The last one is particularly important.

If the GNN generates more useful detections but also increases the review queue, the economics may be negative.

Conversely, if graph features improve precision at a fixed review capacity, they might create substantial value without significantly increasing infrastructure costs.

What it costs if unaddressed

The project risks producing a technically interesting comparison with an economically meaningless conclusion.

A CPTO or fraud director will ask:

“How does this change the economics of operating the detection function?”

The current PRD doesn’t adequately answer that.

Smallest change

Replace the headline metric with:

Incremental value per 1,000 reviewed decisions.

Use a transparent model with three components:

1. Additional illicit entities detected.
2. False-positive investigations avoided or introduced.
3. Incremental infrastructure and operating costs.

Make the assumptions explicit.

Do not pretend to know the actual economics of a production fraud operation from a public dataset.

Show sensitivity at low, central and high assumptions.

Importantly, distinguish measured model performance from modelled commercial value.

⸻

4. The project risks positioning the author as a graph ML enthusiast rather than a product leader

What is wrong

The PRD spends considerable space on technologies and architecture.

It has an escalation ladder, four experiment arms, a query-shape benchmark, a static front end and governance documentation.

But the actual decision rule is still underdeveloped.

The strongest statement in the PRD is:

The decision facing a product leader is not whether graphs can find rings. They can. It is whether the lift justifies the cost per decision, the label requirements and the loss of explainability.

That’s the project.

Yet the requirements don’t fully operationalise that decision.

For example, what would cause a product leader to choose:

* Tabular ML?
* Graph-derived features?
* A full graph ML architecture?

The answer should be a set of decision boundaries, not simply a ranking of four models.

What it costs if unaddressed

The project might demonstrate technical curiosity without demonstrating principal-level judgement.

For the role I’m hiring for, technical fluency is useful.

The ability to allocate investment between competing technical approaches is much more valuable.

Smallest change

Add one final decision matrix.

Finding	Product decision
Tabular performs comparably to graph features	Don’t introduce graph complexity
Graph features materially improve detection economics	Invest in graph-derived features
GNN provides additional material value	Investigate whether the additional operational burden is justified
All methods perform similarly	Don’t invest further based on this dataset

Include the evidence supporting each decision.

Make this the centrepiece of the README.

⸻

5. The dataset creates a significant credibility and transferability problem

What is wrong

The PRD is unusually honest about the dataset limitations.

That’s good.

But there is a risk that the central argument becomes:

“Graph methods work on a cryptocurrency transaction dataset.”

That isn’t necessarily interesting to a regulated payments business.

The author wants to demonstrate judgement in financial crime detection, particularly in payments and AML.

The dataset does not represent the full complexity of payment fraud.

The anonymised node features also make it difficult to establish whether the model has learned meaningful fraud behaviour or dataset-specific patterns.

What it costs if unaddressed

The work could be dismissed as an academic exercise with limited commercial relevance.

The risk is especially high if the conclusions are written as general statements about regulated fintech.

Smallest change

Don’t add another dataset to v1.

Instead, strengthen the limitations section.

Explicitly separate:

* What the experiment demonstrates.
* What it suggests.
* What it cannot establish.

In particular, distinguish cryptocurrency transaction-network detection from card fraud, account takeover, mule detection in payment systems and AML investigations.

The honest limitation is more impressive than pretending the dataset represents all these domains.

⸻

2. What I would cut

Three things.

A. The graph database versus columnar database benchmark.

This is an interesting architectural question, but it is a separate experiment.

It doesn’t directly answer whether graph-derived information improves fraud detection economics.

You risk spending valuable time benchmarking two database technologies without producing evidence that changes the main product decision.

Cut it from v1.

B. The language-model-generated explanation summaries.

The PRD proposes precomputed language-model summaries alongside evidence chains.

This introduces another model, another potential failure mode and another evaluation requirement.

It also creates unnecessary questions about how summaries are generated and validated.

The structured evidence chain is sufficient for the central argument.

Defer language-model summaries.

C. The interactive threshold explorer.

The threshold explorer is attractive, but static charts showing precision, recall and review volume across operating points would answer the same question.

The interactive interface adds implementation work without strengthening the underlying evidence.

Cut it.

What the author gains: time to make the experiment itself more rigorous.

⸻

3. The one claim most likely to be attacked

Organised fraud lives in the relationships between accounts, not in individual transactions, so per-transaction monitoring misses it by design.

This is too categorical.

It suggests that transaction-level monitoring is fundamentally incapable of identifying organised fraud.

That isn’t true.

Transaction-level models can incorporate historical aggregates, behavioural signals and other derived features that capture network effects indirectly.

Indeed, Arm A versus Arm B is intended to test precisely how much additional value graph-derived features provide.

I’d challenge the opening premise:

“If a properly engineered tabular model already captures most of the available relational signal, what exactly are we claiming graph technology adds?”

The project becomes more interesting if it acknowledges that graph representations are not automatically superior to appropriately engineered tabular features.

I’d reframe the claim as:

Organised fraud can be difficult to detect through transaction-level signals alone because relevant evidence may be distributed across connected accounts. This experiment tests whether explicitly representing those relationships adds measurable value beyond a properly tuned tabular baseline.

That’s considerably more defensible.

⸻

4. What would make me reject this outright as evidence of the author’s judgement

Three things would be disqualifying.

1. Changing the pre-registration after seeing results. Particularly if the operating point, success thresholds or hypotheses are adjusted to produce a more interesting conclusion.
2. Presenting modelled economics as measured economics. Or implying that a modelled cost per decision represents actual production operating costs.
3. Publishing a technically impressive result without acknowledging that the dataset cannot support the claimed generalisation.

There is another potential warning sign: publishing a polished interactive demonstration while the experimental methodology remains incomplete.

That would suggest the author optimises for presentation over evidence.

⸻

5. What is already good enough and should not be touched

There is quite a lot worth preserving.

The central question.

“When does a graph earn its cost?” is excellent.

It is commercially meaningful, technically interesting and appropriately constrained.

Keep it.

The commitment to publish a null result.

This is one of the strongest elements of the PRD. Don’t dilute it.

The equal-tuning principle.

The insistence that the baseline must receive comparable tuning attention is exactly right.

Don’t compromise it to save time.

The separation of production experience from experimental evidence.

The decision log and explicit statement that this is not production experience are important.

Preserve that distinction.

The static architecture.

Public data, no server, no hosting cost, no API keys at view time and laptop execution are excellent constraints.

They make the work independently verifiable.

The explicit exclusions.

No GraphRAG, no real-time claims, no production-readiness claims and no unnecessary regulatory mapping.

This is good product discipline.

The data sovereignty discussion.

This is arguably the most differentiated commercial insight in the PRD.

The tension between relational signal crossing jurisdictional boundaries and the restrictions on where data can be joined is genuinely relevant to cross-border payments.

Keep it, but don’t turn it into another major implementation workstream.

The escalation ladder.

The principle of only climbing to a more expensive method after establishing that the previous one has plateaued is exactly the right product philosophy.

Keep the organising principle.

⸻

PASS 2 — Staff Engineer, Graph and ML Systems

My perspective: I run graph and ML systems in production. I don’t care whether the README looks impressive. I care whether the experiment is technically valid, reproducible and capable of surviving scrutiny from someone who understands graph learning.

My overall assessment: the experimental design has the right instincts, but the current PRD leaves several methodological gaps that could invalidate the results.

1. The five most serious problems, ranked

1. Temporal leakage is substantially more complicated than the PRD suggests

What is wrong

The PRD says:

Training uses only time steps before the split point. An automated test fails the run if any feature draws on later data.

Good intention.

But temporal graph leakage isn’t just a matter of ensuring training rows have earlier timestamps.

Consider:

* A node exists before the training cutoff.
* It receives additional edges afterwards.
* Its degree, centrality or community membership changes.
* A graph feature is calculated using the complete graph.
* That feature is then used to score an earlier transaction.

You have leakage even though the transaction timestamp is correct.

This is particularly important for:

* Shared-attribute degree.
* Beneficiary fan-in.
* Cluster size.
* Community membership.
* Distance to confirmed bad actors.

The hop-distance feature has another issue: confirmed bad-actor labels may arrive after the transaction being scored.

Using those labels retrospectively introduces information that wasn’t available at decision time.

What it costs if unaddressed

The graph-feature arm could look substantially better than it really is.

A competent graph ML reviewer will immediately question whether graph features were constructed using information available at the time of scoring.

If the answer isn’t clear, the entire comparison becomes suspect.

Smallest change

Define a strict feature-availability contract.

For each evaluation time step:

* Construct the graph using only edges available at that time.
* Calculate features from that historical graph.
* Use only labels available by that time.
* Never allow future edges or future confirmations to influence historical features.

Add one automated test that inserts a future edge and verifies that earlier feature values do not change.

This is more valuable than several additional evaluation features.

⸻

2. Equal tuning budgets do not automatically produce a fair comparison

What is wrong

The PRD states:

Arm A is tuned with the same budget and the same search method as Arm D.

This sounds fair but isn’t necessarily fair.

A gradient-boosted tree and a GNN have fundamentally different hyperparameter spaces.

They have different sensitivities to:

* Learning rate.
* Model capacity.
* Regularisation.
* Training duration.
* Sampling.
* Neighbourhood depth.
* Embedding dimensions.
* Random initialisation.

Equal numbers of trials do not guarantee comparable optimisation.

The more fundamental issue is that the PRD hasn’t specified the tuning protocol.

Are you using the same validation period?

Are you optimising precision at k?

Are you selecting a single model or averaging multiple random seeds?

Are you allowing graph-specific preprocessing to be tuned?

What it costs if unaddressed

You could incorrectly conclude that the GNN adds little value when the actual issue is insufficient tuning.

Or incorrectly conclude that it adds value because it received more effective optimisation.

Both outcomes undermine the experiment.

Smallest change

Define a tuning contract before implementation.

I’d specify:

* Same historical training data.
* Same temporal validation window.
* Same primary optimisation metric.
* Same number of tuning trials.
* Same number of final evaluation runs.
* Fixed random seeds.
* Identical held-out test periods.

One important qualification: equal tuning effort is not the same as equal compute.

Record both tuning trials and training compute.

For a five-day project, use a modest, explicitly bounded search rather than attempting exhaustive optimisation.

⸻

3. The operating point is still unresolved, and that invalidates the headline comparison

What is wrong

The PRD explicitly identifies this as an open question:

What is the right review-queue size k for precision at k?

This should not remain open when the first result is generated.

Precision at k is a business decision disguised as an evaluation metric.

If k is 100, the result might look different from k = 1,000.

And the economically appropriate review capacity depends on the business being modelled.

The PRD also introduces a sub-one-percent take rate in H2 without clearly defining its relationship to the dataset’s prevalence.

These are different quantities:

* Dataset label prevalence.
* Model detection rate.
* Review-queue capacity.
* Operational alert or investigation rate.

They must not be conflated.

What it costs if unaddressed

The headline conclusion can change simply by changing k.

That makes the result easy to attack.

Smallest change

Choose one primary operating point before evaluation.

For this experiment, I’d use:

Top 1% of scored entities per evaluation period.

Why?

It creates a clear, fixed-capacity comparison without pretending to know the actual capacity of a production fraud team.

Report precision at that operating point as the primary metric.

Also report:

* Recall at the same operating point.
* PR-AUC as a secondary diagnostic.
* Number of confirmed illicit entities detected.
* Number of false positives.

Be explicit that the 1% is an experimental constraint, not an industry benchmark.

Do not change it after seeing the results.

⸻

4. The cost model risks becoming fabricated precision

What is wrong

The PRD requires modelled cost per scored entity, with sensitivity of ±50%.

The problem is that the underlying assumptions aren’t specified.

For example:

* What hardware is assumed?
* Is graph construction included?
* Is feature computation included?
* Are embeddings regenerated for each scoring period?
* Is storage amortised?
* Is training included or only inference?
* What happens when the graph grows?

A model that requires an expensive initial graph build but cheap repeated inference behaves differently from one requiring repeated neighbourhood aggregation.

The ±50% range is arbitrary.

It doesn’t necessarily capture the actual uncertainty.

What it costs if unaddressed

The cost comparison could look rigorous while being little more than an invented spreadsheet.

This would undermine the commercial conclusion.

Smallest change

Replace the single cost-per-decision number with three explicitly separated measurements:

Cost category	Measurement
Training	Compute time and estimated compute cost
Feature generation	Compute time and estimated compute cost per evaluation period
Inference	Compute time and estimated cost per scored entity

Record actual laptop execution time and memory usage.

Then apply a transparent illustrative unit-cost assumption.

Show how the conclusion changes under different assumptions.

Don’t claim to have measured production infrastructure economics.

⸻

5. The graph methodology is insufficiently specified

What is wrong

The PRD describes Arm D as:

Inductive GNN node classification.

But that isn’t a sufficiently precise method specification.

There are important distinctions:

* What constitutes a node?
* What constitutes an edge?
* Are edges directed?
* Are edge attributes used?
* Are graph features aggregated over one or multiple hops?
* How are previously unseen nodes handled?
* How are nodes with no historical neighbours handled?
* Are labels attached to nodes or transactions?
* How does the model distinguish a new account from a previously observed one?

The open question about heterogeneous graphs is particularly important.

If the underlying dataset contains only a single node type and a particular representation of transactions, the model may be testing a relatively narrow graph-learning problem.

That is fine.

But the PRD needs to say exactly what it is testing.

What it costs if unaddressed

The experiment risks producing a result that is technically difficult to reproduce or interpret.

It also becomes difficult to distinguish a limitation of GNNs from a limitation of the chosen architecture or graph representation.

Smallest change

Specify one GNN architecture and one graph representation.

Document:

* Node definition.
* Edge definition.
* Directionality.
* Temporal construction.
* Features.
* Label availability.
* Treatment of unseen nodes.

Do not introduce heterogeneous graph support unless the primary dataset genuinely requires it.

For v1, one well-defined architecture is more valuable than architectural breadth.

⸻

2. What I would cut

A. Community detection as an additional experiment

The unsupervised arm is intellectually attractive.

But it introduces a different evaluation problem.

How do you define a discovered ring?

How do you match communities to known illicit entities?

How do you account for the fact that the labels are incomplete?

How do you distinguish a large legitimate cluster from an organised illicit network?

That’s a separate experiment.

Defer it.

The supervised comparison already answers the central question.

B. The graph database versus columnar database benchmark

I’d remove this entirely from v1.

The proposed workloads are too narrow to establish a meaningful general comparison between graph and columnar engines.

A multi-hop traversal and a high-cardinality aggregation are not enough to establish that one engine is generally preferable.

There are additional questions around:

* Data loading.
* Indexing.
* Query optimisation.
* Materialisation.
* Hardware configuration.
* Cache state.
* Query planning.
* Storage layout.

The benchmark could easily consume half a day or more while generating evidence of limited value.

C. Language-model explanation summaries

Remove them.

The structured evidence chain is the important part.

An LLM-generated explanation introduces a second evaluation problem: whether the natural-language explanation faithfully represents the underlying evidence.

That is not the question this repository needs to answer.

A deterministic explanation is sufficient:

“Account A shares three historical counterparties with previously confirmed illicit accounts.”

No language model required.

⸻

3. The one claim most likely to be attacked

The assumption that graph-derived features represent information that a properly tuned tabular model cannot already capture.

This is the critical methodological question.

Consider a graph with three accounts sharing a beneficiary.

A tabular model might already capture:

* Number of shared beneficiaries.
* Beneficiary fan-in.
* Transaction frequency.
* Account age.
* Historical activity patterns.

Adding graph-derived features may simply provide another representation of information already available in the underlying data.

That’s not necessarily bad.

But it changes what the experiment demonstrates.

The important question becomes:

Does explicitly constructing graph relationships produce meaningful incremental detection value beyond a well-engineered tabular representation of the same historical information?

I’d attack this by examining the feature definitions.

Specifically:

1. Are the graph-derived features genuinely relational?
2. Are equivalent aggregate features already present in Arm A?
3. Are graph features computed using exactly the same historical information?
4. Does Arm B improve performance on genuinely unseen future periods?

If the graph arm wins, I’d want to know whether it wins because of graph structure or because it simply received better feature engineering.

This is the most important comparison in the entire project.

⸻

4. What would make me reject this outright as evidence of the author’s judgement

Four things.

1. Any temporal leakage.

Not just obvious future labels.

Future graph edges, future degree calculations, future community membership or future confirmation information.

If any of these influence historical predictions, the results are invalid.

2. An improperly tuned baseline.

If the tabular baseline receives less attention than the graph model, the central comparison is compromised.

3. An evaluation that treats unlabelled entities as legitimate.

The dataset contains approximately 77% unlabelled entities.

Unlabelled does not mean legitimate.

Treating them as negative examples would create a serious evaluation problem.

The PRD acknowledges label bias, but the evaluation protocol needs to address this explicitly.

At minimum, report metrics against the observed labelled population and acknowledge the limitations of that population.

4. Claims about production graph infrastructure based on this benchmark.

A small static dataset running on an embedded graph engine cannot establish the production economics of a distributed graph platform.

The PRD currently acknowledges this limitation.

I would expect the final implementation to preserve that discipline.

⸻

5. What is already good enough and should not be touched

The escalation ladder.

Rules → tabular → graph-derived features → graph algorithms → GNN.

This is a sensible progression.

It communicates the principle of increasing complexity only when justified.

The distinction between graph features and graph neural networks.

This is important.

Many discussions collapse these into one category.

The PRD correctly separates them.

The time-aware evaluation requirement.

Keep it.

It’s essential for financial crime detection, where historical relationships and delayed labels matter.

The explicit label distribution.

The 2% illicit, 21% licit and 77% unlabelled distribution is important context.

Don’t simplify it into a conventional binary classification problem without explaining what happens to the unlabelled population.

The commitment to automated leakage checks.

Keep this as P0.

I’d actually consider it the most important technical acceptance criterion in the entire PRD.

The laptop CPU constraint.

Excellent.

It prevents infrastructure from becoming a substitute for methodological quality.

The distinction between evidence generation and production decision-making.

The autonomy split is sensible context.

Just don’t spend implementation time building a production-style approval architecture for a static experiment.

The explicit limitations around real-time performance.

Keep these statements.

They prevent the benchmark from being misinterpreted.

The structured evidence chain.

This is worth keeping.

A fraud detection result without an explanation of why an entity was flagged is incomplete from an operational perspective.

But deterministic evidence is enough.

⸻

Combined assessment

The two perspectives converge on something important.

The PRD has the right strategic question, but it currently has too many ways to demonstrate that question and too few sufficiently defined rules for establishing whether the answer is true.

I’d make the following decisions before committing the first experiment.

Area	Decision	Priority
Pre-registration	Define measurable hypotheses and kill criteria	Critical
Temporal evaluation	Define historical feature availability and prevent graph leakage	Critical
Operating point	Fix top 1% before running results	Critical
Baseline	Specify equal tuning protocol	Critical
Unlabelled data	Define evaluation treatment explicitly	Critical
Economics	Separate measured compute from modelled business costs	High
GNN	Specify one architecture and representation	High
Database benchmark	Remove from v1	Cut
Community detection	Defer	Cut
LLM explanations	Remove from v1	Cut
Interactive explorer	Replace with static charts	Cut
Governance	Retain concise limitations and sovereignty discussion	Keep

The uncomfortable question: what if the result is uninteresting?

That is a real possibility.

The dataset may show that a tuned tabular model already captures most of the available signal.

Graph-derived features may add little.

The GNN may perform similarly or worse.

And the cost comparison may not support additional graph complexity.

That is not a failed project.

In fact, it could be the strongest possible outcome for the intended positioning.

But only if the experiment is rigorous enough to support the conclusion.

A Principal Product Manager who can demonstrate that an expensive technology doesn’t earn its cost is more valuable than one who can demonstrate that they successfully implemented it.

The interesting result isn’t necessarily that graph ML wins.

It’s establishing where the incremental value of relational information begins, where it plateaus, and what evidence justifies moving to a more expensive architecture.

That’s a much better hiring story.

⸻

Final verdict

Ship with the changes above.

Not the current scope.

I’d spend the first half-day resolving the pre-registration, evaluation protocol, operating point and feature-availability rules.

Then build the smallest reproducible experiment:

1. Tuned tabular baseline.
2. Graph-derived feature augmentation.
3. GNN comparison, conditional on the earlier results.
4. Leakage-tested temporal evaluation.
5. Transparent cost analysis.
6. Static charts and a clear product decision.

Everything else is secondary.

The project should demonstrate that the author knows when not to build a graph ML system, not simply that they know how to build one.

---

### Model B reply: Claude Opus 5.5

Review: graph-risk-evals PRD, Draft v1
First: the three credibility pillars are weak in the details
The intent behind the pre-registration, the kill criteria and equal tuning is right. As written, though, none of them can be enforced.

* Two open questions block the pre-registration. The size of the review queue (k) and the cost model are both still marked Open. Yet H2 and the "what would change my mind" test depend on them. A pre-registration that leaves its own operating point undecided doesn't bind anything. Settle both before committing it.
* H1: "majority of the available lift" isn't defined. Define it as (B − A) / (max(B, D) − A) ≥ 0.5, using PR-AUC on the pre-shift test steps. If A comes out best, H1 is undefined and that is itself the finding.
* H2: "3 consecutive steps above 5pp" is a coin flip, not a test. Each test step holds roughly 90 illicit labels before the shift, and far fewer after it. Five points at a single step is a handful of entities. Replace it with this: pool steps 35–42, run 5 seeds, and use a paired bootstrap (1,000 resamples, stratified by step). H2 is rejected only if the GNN's gain is at least 5pp and its 95% confidence interval excludes zero.
* H3: "degrades less" is trivially true for a weak model unless you measure the drop relatively. Define it as the relative fall in PR-AUC, comparing the mean of steps 43–49 with the mean of steps 35–42.
* "Noise band" in the kill criteria has no definition. Define it as: the paired bootstrap 95% confidence interval on the difference includes zero.
* Equal tuning doesn't say what is equal. Specify all of this:
   * same search method (Optuna TPE) and the same number of trials (40) for each arm;
   * the same validation window: train on steps 1–29, validate on 30–34;
   * the same early-stopping rule, class weighting and threshold rule;
   * the GNN architecture family fixed in advance (2-layer GraphSAGE), with any architecture search counted against its budget.
Say plainly that equal trials does not mean equal compute.
* "Never edited" relies on trust. Tag the commit `prereg-v1`. Then have the pipeline hash the pre-registration file and refuse to write `results/` if the hash doesn't match the tag. That's about 20 lines of code.

Pass 1: sceptical CPTO
1. Five most serious problems
1. The headline result is already published, and the PRD doesn't say so.

* What's wrong: Weber et al. (2019), the paper that released this dataset, found that a random forest on all features beat a GCN (illicit F1 roughly 0.79 against 0.63). They also found that every model collapses after the dark-market shutdown at time step 43. H1 to H3 largely restate that paper.
* Cost: A reviewer who knows the dataset reads this as a first encounter with it. That is exactly the impression the repo exists to avoid.
* Fix: Add one paragraph headed "Prior results and what this adds". Frame the work as a stricter replication: equal tuning, a fixed alert budget, and cost per true positive.

2. The cost model measures the wrong cost.

* What's wrong: Scoring around 200,000 nodes on a CPU costs fractions of a cent, whichever arm you use. Cost per decision therefore can't tell the arms apart, and the cost condition in H2 will always pass. The costs that actually differ between arms are analyst time per alert and engineering effort.
* Cost: The economics goal, the thing that sets this apart from academic work, becomes decoration.
* Fix: Use a unit model:
cost per true positive = (k × analyst cost per alert + compute) / true positives
Assume €20 per alert, with a ±50% range. Show compute as the rounding error it is. Log the build days spent on each arm as a second cost. Neither costs you anything to add.

3. The payments framing promises things the data can't deliver.

* What's wrong: In this dataset the nodes are Bitcoin transactions and the features are anonymised. There are no accounts, devices, addresses or opening dates. Three of the rung-3 features can't be computed: shared-attribute degree, beneficiary fan-in and cluster formation speed.
* Cost: A principal-level reader spots the overreach in the context section, and doubts the rest.
* Fix: Rewrite the rung-3 list to what can actually be computed:
   * in-degree and out-degree;
   * PageRank within each time step;
   * size of the node's two-hop neighbourhood;
   * aggregates of neighbours' predicted scores.
Label the payments examples as "what this would be on payments data".

4. The scope doesn't fit five days.

* What's wrong: 8 P0 requirements, 5 P1s, a front end and a governance pack is closer to three weeks of work.
* Cost: It ships half-built, and that damages the honesty claim more than a smaller scope would.
* Fix: v1 is Arms A, B and D, the evaluation, the leakage test, the cost model and charts in the README. Everything else is P2.

5. The self-referential framing weakens the honesty claim.

* What's wrong: CUJ 11 ("As a hiring manager…"), the Transferability goal and the RICE table on a solo five-day lab.
* Cost: A public lab that names its hiring audience reads as marketing. RICE scores for 12 stories with one scorer read as process theatre.
* Fix: Delete CUJ 11. Move the CUJ table to an appendix or remove it. Keep the decision log, framed as "practitioner notes".

2. What I would cut

* The query-shape test. It doesn't touch H1, H2 or H3. At 234,000 edges everything fits in memory, so you'd mostly be timing engine start-up. Gain: about a day, and one fewer attackable claim.
* The front end and threshold explorer. Replace them with a precomputed threshold table and a chart in the README. Gain: about a day.
* The golden set and labelling protocol. The dataset is static and no human confirms anything, so these are theatre. Gain: half a day, and less to defend.
* The governance pack, cut to one page. Keep the data sovereignty note; it's the original part. Drop the HIPAA/FedRAMP line and the autonomy split. Gain: half a day.

Spend the time you get back on a label-budget curve. Train each arm on 5%, 10%, 25%, 50% and 100% of the training labels. This tests the TL;DR's own claim that labels "arrive late and rarely". It's the one result here that isn't already published, and it's half a day of work once the pipeline is parameterised.
3. The claim most likely to be attacked
"A detection capability has to pay for itself in basis points," tested in H2 against a sub-one-percent take rate.
The attack: the data has no transaction value, no fee and no loss amount. Both sides of the margin are invented, so the conclusion is just the assumptions. Remove the take rate from H2. If you keep it at all, show it as an illustration using a stated hypothetical transaction value.
4. What would make me reject it outright

* Git history shows the pre-registration committed after any result on the test steps.
* Bitcoin results are presented as evidence about payments mule networks.
* A null result is reframed rather than published.
* Modelled costs are shown with false precision, or without the "modelled" label.

5. Good enough, don't touch

* The TL;DR.
* The decision framing: "not whether graphs can find rings… whether the lift justifies the cost".
* The non-goals list.
* The publish-whatever-the-result stance.
* The escalation ladder as the organising argument.
* The red lines.
* The build-vs-buy and real-time statements.
* The data sovereignty note.

Pass 2: staff engineer, graph and ML in production
1. Five most serious problems
1. Arm A is not graph-free.

* What's wrong: Of the dataset's 166 features, the last 72 are aggregates over each node's one-hop neighbours. Arm A, described as "node features only", already contains graph information.
* Cost: A against B no longer isolates the lift from graph features. H1 is wrong by construction.
* Fix: Arm A uses the 93 local features only, and excludes the time-step column. Arm B adds the 72 provided aggregates plus your own structural features.

2. Label leakage within a time step.

* What's wrong: Each time step is a separate graph, with no edges between steps. "Hop distance to a confirmed bad actor" at test time can only use labels from that same test step. Your leakage test checks for future time steps, not for label-derived features.
* Cost: Arm B's score is inflated and the whole comparison is void.
* Fix: Drop label-distance features. Replace them with neighbour aggregates of the model's own predicted scores, in two stages. Add a test that shuffles the test labels and asserts that every feature stays the same.

3. No defined unit of statistical evidence.

* What's wrong: One seed, per-step metrics, and late test steps with very few illicit labels.
* Cost: Differences of 1 to 3 points will be read as wins.
* Fix: Use the 5-seed paired bootstrap from the top section. Make steps 35–42 the headline and report steps 43–49 separately.

4. The evaluation population and k are undefined.

* What's wrong: 77% of nodes are unlabelled. If you rank every node, precision at k counts unlabelled nodes, and it isn't clear whether they're hits or misses.
* Cost: The headline metric is ambiguous, and different readers will compute different numbers.
* Fix: Compute metrics on labelled nodes only, and say so. Also report the share of the top-k queue that is unlabelled when you rank all nodes. Set k to the mean number of illicit labels per step in steps 1–34. It's computed in code before the test steps are touched, and it mirrors how operations teams size queues from historical case volume. Publish the full precision-recall curve too, so k isn't load-bearing. Choose the threshold on validation steps, never on test steps.

5. An open question that can be closed now.

* What's wrong: "Does the GNN need a heterogeneous graph?" The dataset has one node type, and a heterogeneous GNN would mean inventing node types.
* Fix: Answer it: no. Name the remaining design choice instead: a GNN applied to each disjoint step graph has to be inductive. State GraphSAGE and move on.

2. What I would cut

* Arm C (unsupervised). Community detection on small disjoint graphs per step, scored against biased labels, will be noisy and hard to read. Gain: most of a day, and one fewer weak result.
* The language-model summaries and their faithfulness check. Even generated offline, this adds a model dependency and a second evaluation problem. Gain: half a day.
* 100% explainability coverage for Arm D. SHAP values over anonymised features ("feature 37") explain nothing. Produce evidence chains for Arm B from graph structure, and record Arm D's lack of one as a limitation. Gain: you avoid GNNExplainer work and the arguments that come with it.

3. The claim most likely to be attacked
H1: graph features capture most of the lift.
The attack: "Your baseline already has neighbour aggregates, and your graph features read test labels. Show me A on the 93 local features only, B without label-derived features, five seeds and the confidence intervals." As specified, the PRD fails all of that.
4. What would make me reject it outright

* A random rather than time-aware split.
* Arm A including neighbour aggregates while being called node-only.
* Thresholds or hyperparameters chosen on test steps.
* Single-seed point estimates with wins declared on gaps under 3 points.

5. Good enough, don't touch

* The time-aware split as a red line.
* The leakage check as a test that fails the build (widen its scope, keep it).
* Equal tuning as a principle.
* "If B doesn't beat A, don't build D."
* A thin slice first, with versions pinned.
* Evidence chains from graph structure rather than anonymised features (risk 2's mitigation is right).
* The embedded graph store trade-off.
* The 30-minute CPU budget, which is realistic at this size.

The honest answer on interest: as specified, the result will probably be uninteresting. B will match or beat D, and everything will collapse after step 43, which is already published. Three additions make it worth a principal reader's time:

* the label-budget curve;
* cost per true positive;
* an Arm A built cleanly enough to isolate graph lift properly for the first time.

Ship with the changes above.

---

## Build prompts

The prompts that started the build sessions are in [`docs/claude-code-prompt-session0.md`](docs/claude-code-prompt-session0.md) and [`docs/claude-code-prompt.md`](docs/claude-code-prompt.md). Session transcripts are not published: they are long and hold material outside this project.
