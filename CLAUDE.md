# CLAUDE.md — working rules for graph-risk-evals

These rules bind every session. They are not suggestions and they are not negotiable mid-build. If a rule blocks the work, stop and say so rather than working around it.

---

## The spec

**`prds/prd-v2.md` is the working specification.** Implement from it.

**`prds/prd-v1.md` is historical and must not be implemented.** It contains three errors that were found in review and corrected in v2. If v1 and v2 disagree, v2 is right. Do not attempt to reconcile them.

`docs/prd-review.md` records what changed and why. Read it if a decision in v2 looks arbitrary.

---

## Red lines

Violating any of these invalidates the repository's central claim. Each one is enforced in code, not by good intentions.

1. **No result is written to `results/` unless the pre-registration hash matches the `prereg-v1` tag.** The gate runs before any write. If it fails, the run halts.
2. **No result is written while either leakage test fails.** Future-edge test and label-shuffle test, both green, every run.
3. **Arm A uses the 94 local features only.** The time-step column is excluded. This is asserted in code, not stated in a comment. Arm A never reads from the graph store.
4. **No threshold, hyperparameter or operating point is ever selected on test steps.** Validation steps only, for every arm, at every stage.
5. **Every number in the README, the site and any document comes from `results/`.** Nothing is hand-entered. Nothing is written by a model.
6. **No win is declared on a difference whose bootstrap confidence interval includes zero.**
7. **Modelled figures are labelled modelled**, every time they appear. Never presented as measured.
8. **Datasets are never committed.** `data/` is git-ignored. A loader fetches them.

---

## Commits

- **No co-authorship or generated-by attribution lines in commit messages.** Plain messages only.
- Imperative mood, one line, body only when the reasoning is not obvious from the diff.
- Commit the pre-registration on its own, then tag it. Never amend a tagged commit.

---

## Build order

Follow the phases in the PRD. Do not start a phase before the previous one's gate has passed.

**Session 1 is the thin end-to-end slice and nothing else.** Loader working, cross-step edge question answered, one metric computed, one chart rendered, every version pinned. Resist building anything further until that runs on a clean clone.

If the slice is not working by the end of session 1, the kill criterion fires: stop, and the repository ships as a method write-up.

---

## Technical constraints

- **Static.** No server, no API keys, no network calls at view time. The site reads JSON from `results/`.
- **Laptop CPU.** No GPU. The full pipeline runs in under 30 minutes on a clean clone.
- **One command.** `make all` or equivalent runs load, build, arms, evaluation and export.
- **Pinned versions.** Exact versions in `requirements.txt` from the first commit. No ranges, no bare names.
- **Arm B features are traversal queries in the embedded graph store**, committed under `graph/queries/`. Do not compute them in a Python graph library. If a query is materially slower or more awkward than the library equivalent, record it as a finding in `NOTES.md` rather than switching.

---

## Honesty rules

These exist because the repository's value is its method, not its result.

- **Report the result that occurred.** If the pre-registered prediction fails, say so plainly and say what changed your mind.
- **A null result is a finding.** Do not reframe it, bury it, or look for a cut of the data where it looks better.
- **State limitations beside the claim**, not only in a limitations section. Every chart carries what it does not establish.
- **Separate demonstrated, suggested and cannot be established.** Three categories, used consistently.
- **Do not generalise beyond the dataset.** This is a cryptocurrency transaction graph. It is not payments data. Say so wherever a payments reader might assume otherwise.
- **Prior work is cited.** The headline comparison has been published before. Section 2 of the PRD states what this adds.

---

## Safety and privacy

- **Public data only.** No employer data, no client data, no confidential material, in any file.
- **The decision log names industries, never companies.** Omnichannel retailer, travel tech, big tech, unicorn SaaS, energy major.
- **No locations, no internal project names, no vendor names tied to an employer.**
- Entries describe a decision and its reasoning. If a line reads as internals rather than as learning, cut it.
- The test: would this sit comfortably on a conference slide.

---

## Documentation conventions

Carried from the existing portfolio so the repositories read as one system.

- **README is the dashboard**, human-facing: how to read the repo, the decision matrix, deliverables table, limitations, repo tree.
- **`CLAUDE.md` is agent-facing.** These rules. Not duplicated in the README.
- **`NOTES.md` per module** for reasoning, friction and takeaways.
- **`PROMPTS.md`** logs prompts and model replies verbatim.
- **PRDs are versioned, never overwritten.**
- **`change_log.md`** is a dated decision log.
- Kebab-case file names that describe the artefact.
- Counts come from code, never from a model-written summary.

---

## When to stop and ask

- A red line blocks the work.
- The data does not match what the PRD describes.
- A kill criterion has fired.
- An open question in the PRD needs answering before implementation can continue.
- You are about to make an assumption that would change a result.

Say what you found, what it blocks, and what the options are. Do not proceed on a guess.
